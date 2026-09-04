"""Shared bounded HTTP behavior; adapters receive transport rather than owning clients."""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener


class DiscoveryError(RuntimeError):
    def __init__(self, message: str, *, transient: bool, retry_after: datetime | None = None):
        super().__init__(message)
        self.transient = transient
        self.retry_after = retry_after


class BudgetExceeded(DiscoveryError):
    def __init__(self) -> None:
        super().__init__("discovery request budget exhausted", transient=False)


class Cancelled(DiscoveryError):
    def __init__(self) -> None:
        super().__init__("discovery cancelled", transient=False)


@dataclass(frozen=True)
class HttpResponse:
    status: int
    headers: Mapping[str, str]
    body: bytes


class Transport(Protocol):
    def __call__(self, url: str, headers: Mapping[str, str], timeout: float) -> HttpResponse: ...


class PostTransport(Protocol):
    def __call__(
        self, url: str, headers: Mapping[str, str], body: bytes, timeout: float
    ) -> HttpResponse: ...


@dataclass
class DiscoveryBudget:
    max_requests: int = 20
    used_requests: int = 0

    def consume(self) -> None:
        if self.used_requests >= self.max_requests:
            raise BudgetExceeded()
        self.used_requests += 1


def _retry_after(headers: Mapping[str, str]) -> datetime | None:
    value = headers.get("Retry-After") or headers.get("retry-after")
    if not value:
        return None
    try:
        return datetime.now(UTC) + timedelta(seconds=int(value))
    except ValueError:
        try:
            return parsedate_to_datetime(value).astimezone(UTC)
        except (TypeError, ValueError):
            return None


class _BoundedRedirects(HTTPRedirectHandler):
    def __init__(self, maximum: int) -> None:
        super().__init__()
        self.maximum, self.seen = maximum, 0

    def redirect_request(self, *args: object, **kwargs: object) -> Request | None:
        self.seen += 1
        if self.seen > self.maximum:
            return None
        return super().redirect_request(*args, **kwargs)


def urllib_transport(url: str, headers: Mapping[str, str], timeout: float) -> HttpResponse:
    request = Request(url, headers=dict(headers))
    try:
        opener = build_opener(_BoundedRedirects(3))
        with opener.open(request, timeout=timeout) as response:  # noqa: S310 - explicit adapter endpoints only
            return HttpResponse(response.status, dict(response.headers.items()), response.read())
    except HTTPError as error:
        return HttpResponse(error.code, dict(error.headers.items()), error.read())
    except URLError as error:
        raise DiscoveryError(f"network error: {error.reason}", transient=True) from error


def urllib_post_transport(
    url: str, headers: Mapping[str, str], body: bytes, timeout: float
) -> HttpResponse:
    request = Request(url, data=body, headers=dict(headers), method="POST")
    try:
        with build_opener(_BoundedRedirects(3)).open(request, timeout=timeout) as response:  # noqa: S310
            return HttpResponse(response.status, dict(response.headers.items()), response.read())
    except HTTPError as error:
        return HttpResponse(error.code, dict(error.headers.items()), error.read())
    except URLError as error:
        raise DiscoveryError(f"network error: {error.reason}", transient=True) from error


class HttpClient:
    """One request policy: user agent, bounds, retries, rate errors, and cancellation."""

    def __init__(
        self,
        *,
        transport: Transport = urllib_transport,
        post_transport: PostTransport = urllib_post_transport,
        budget: DiscoveryBudget | None = None,
        timeout_seconds: float = 10.0,
        max_response_bytes: int = 1_000_000,
        retries: int = 1,
        retry_backoff_seconds: float = 0.25,
        sleeper: Callable[[float], None] = time.sleep,
    ):
        self.transport, self.post_transport, self.budget = (
            transport,
            post_transport,
            budget or DiscoveryBudget(),
        )
        self.timeout_seconds, self.max_response_bytes, self.retries, self.sleeper = (
            timeout_seconds,
            max_response_bytes,
            retries,
            sleeper,
        )
        self.retry_backoff_seconds = retry_backoff_seconds

    def get_json(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        cancelled: Callable[[], bool] | None = None,
    ) -> tuple[dict | list, Mapping[str, str]]:
        request_headers = {
            "User-Agent": "curiosity-engine/0.1 metadata-discovery",
            "Accept": "application/json",
        }
        request_headers.update(headers or {})
        for attempt in range(self.retries + 1):
            if cancelled and cancelled():
                raise Cancelled()
            self.budget.consume()
            response = self.transport(url, request_headers, self.timeout_seconds)
            if len(response.body) > self.max_response_bytes:
                raise DiscoveryError("response exceeds configured size bound", transient=False)
            if response.status == 429 or (
                response.status == 403 and _retry_after(response.headers)
            ):
                error = DiscoveryError(
                    f"rate limited ({response.status})",
                    transient=True,
                    retry_after=_retry_after(response.headers),
                )
            elif 500 <= response.status <= 599:
                error = DiscoveryError(f"server error ({response.status})", transient=True)
            elif response.status >= 400:
                raise DiscoveryError(f"permanent HTTP error ({response.status})", transient=False)
            else:
                try:
                    payload = json.loads(response.body.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise DiscoveryError("malformed JSON response", transient=False) from exc
                if not isinstance(payload, (dict, list)):
                    raise DiscoveryError(
                        "JSON response must be an object or array", transient=False
                    )
                return payload, response.headers
            if attempt == self.retries:
                raise error
            self.sleeper(self.retry_backoff_seconds * (2**attempt))
        raise AssertionError("unreachable")

    def post_json(
        self,
        url: str,
        payload: dict[str, object] | list[str],
        *,
        headers: Mapping[str, str] | None = None,
    ) -> tuple[dict | list, Mapping[str, str]]:
        request_headers = {
            "User-Agent": "curiosity-engine/0.1 metadata-discovery",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        request_headers.update(headers or {})
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.budget.consume()
        response = self.post_transport(url, request_headers, body, self.timeout_seconds)
        if len(response.body) > self.max_response_bytes:
            raise DiscoveryError("response exceeds configured size bound", transient=False)
        if response.status == 429 or (response.status == 403 and _retry_after(response.headers)):
            raise DiscoveryError(
                "rate limited", transient=True, retry_after=_retry_after(response.headers)
            )
        if response.status >= 400:
            raise DiscoveryError(f"permanent HTTP error ({response.status})", transient=False)
        try:
            decoded = json.loads(response.body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise DiscoveryError("malformed JSON response", transient=False) from exc
        if not isinstance(decoded, (dict, list)):
            raise DiscoveryError("JSON response must be an object or array", transient=False)
        return decoded, response.headers
