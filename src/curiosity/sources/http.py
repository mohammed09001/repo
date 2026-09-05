"""Shared bounded HTTP behavior; adapters receive transport rather than owning clients.

One long-lived pooled HTTPX client is used per discovery/refresh run. Tests
inject scripted transports so the suite never touches the network.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime
from typing import Protocol

import httpx

_REDIRECT_LIMIT = 10
_POOL_CONNECTIONS = 5


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


def _bounded_body(response: httpx.Response, *, max_bytes: int) -> bytes:
    total = 0
    parts: list[bytes] = []
    for chunk in response.iter_bytes():
        total += len(chunk)
        if total > max_bytes:
            raise DiscoveryError("response exceeds configured size bound", transient=False)
        parts.append(chunk)
    return b"".join(parts)


def httpx_transport(
    client: httpx.Client, *, max_response_bytes: int
) -> Transport:
    def transport(url: str, headers: Mapping[str, str], timeout: float) -> HttpResponse:
        response = client.get(
            url,
            headers=dict(headers),
            timeout=timeout,
            follow_redirects=True,
        )
        return HttpResponse(
            response.status_code,
            dict(response.headers.items()),
            _bounded_body(response, max_bytes=max_response_bytes),
        )

    return transport


def httpx_post_transport(
    client: httpx.Client, *, max_response_bytes: int
) -> PostTransport:
    def transport(
        url: str, headers: Mapping[str, str], body: bytes, timeout: float
    ) -> HttpResponse:
        response = client.post(
            url,
            headers=dict(headers),
            content=body,
            timeout=timeout,
            follow_redirects=True,
        )
        return HttpResponse(
            response.status_code,
            dict(response.headers.items()),
            _bounded_body(response, max_bytes=max_response_bytes),
        )

    return transport


class HttpClient:
    """One request policy: user agent, bounds, retries, rate errors, and cancellation."""

    def __init__(
        self,
        *,
        transport: Transport | None = None,
        post_transport: PostTransport | None = None,
        budget: DiscoveryBudget | None = None,
        timeout_seconds: float = 10.0,
        max_response_bytes: int = 1_000_000,
        retries: int = 1,
        retry_backoff_seconds: float = 0.25,
        sleeper: Callable[[float], None] = time.sleep,
    ):
        self.transport = transport
        self.post_transport = post_transport
        self.budget = budget or DiscoveryBudget()
        self.timeout_seconds, self.max_response_bytes, self.retries, self.sleeper = (
            timeout_seconds,
            max_response_bytes,
            retries,
            sleeper,
        )
        self.retry_backoff_seconds = retry_backoff_seconds
        self._client: httpx.Client | None = None
        self.bytes_received = 0
        self.retries_performed = 0

    def _note(self, response: HttpResponse) -> None:
        self.bytes_received += len(response.body)

    def _resolve_transport(self) -> None:
        if self.transport is None:
            self._client = httpx.Client(
                timeout=httpx.Timeout(
                    self.timeout_seconds,
                    connect=self.timeout_seconds,
                    read=self.timeout_seconds,
                    write=self.timeout_seconds,
                    pool=self.timeout_seconds,
                ),
                limits=httpx.Limits(
                    max_connections=_POOL_CONNECTIONS,
                    max_keepalive_connections=_POOL_CONNECTIONS,
                ),
                max_redirects=_REDIRECT_LIMIT,
            )
            self.transport = httpx_transport(self._client, max_response_bytes=self.max_response_bytes)
        if self.post_transport is None:
            client = self._client or httpx.Client()
            if self._client is None:
                self._client = client
            self.post_transport = httpx_post_transport(
                client, max_response_bytes=self.max_response_bytes
            )

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def get_bytes(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        cancelled: Callable[[], bool] | None = None,
        accept: str = "application/xml,text/xml,text/plain",
    ) -> tuple[bytes, Mapping[str, str]]:
        """Bounded raw GET for non-JSON resources such as RSS/Atom feeds."""
        self._resolve_transport()
        request_headers = {
            "User-Agent": "curiosity-engine/1.0 metadata-discovery",
            "Accept": accept,
        }
        request_headers.update(headers or {})
        for attempt in range(self.retries + 1):
            if cancelled and cancelled():
                raise Cancelled()
            self.budget.consume()
            response = self.transport(url, request_headers, self.timeout_seconds)
            self._note(response)
            if len(response.body) > self.max_response_bytes:
                raise DiscoveryError("response exceeds configured size bound", transient=False)
            if response.status == 429 or (
                response.status == 403 and _retry_after(response.headers)
            ):
                raise DiscoveryError(
                    "rate limited",
                    transient=True,
                    retry_after=_retry_after(response.headers),
                )
            if 500 <= response.status <= 599:
                error = DiscoveryError(f"server error ({response.status})", transient=True)
            elif response.status >= 400:
                raise DiscoveryError(f"permanent HTTP error ({response.status})", transient=False)
            else:
                return response.body, response.headers
            self.retries_performed += 1
            if attempt == self.retries:
                raise error
            self.sleeper(self.retry_backoff_seconds * (2**attempt))
        raise AssertionError("unreachable")

    def get_json(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        cancelled: Callable[[], bool] | None = None,
    ) -> tuple[dict | list, Mapping[str, str]]:
        self._resolve_transport()
        request_headers = {
            "User-Agent": "curiosity-engine/1.0 metadata-discovery",
            "Accept": "application/json",
        }
        request_headers.update(headers or {})
        for attempt in range(self.retries + 1):
            if cancelled and cancelled():
                raise Cancelled()
            self.budget.consume()
            response = self.transport(url, request_headers, self.timeout_seconds)
            self._note(response)
            if len(response.body) > self.max_response_bytes:
                raise DiscoveryError("response exceeds configured size bound", transient=False)
            if response.status == 429 or (
                response.status == 403 and _retry_after(response.headers)
            ):
                # Rate limits must not be retried aggressively; honor Retry-After
                # durably and let the caller exit boundedly.
                raise DiscoveryError(
                    f"rate limited ({response.status})",
                    transient=True,
                    retry_after=_retry_after(response.headers),
                )
            if 500 <= response.status <= 599:
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
            self.retries_performed += 1
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
        self._resolve_transport()
        request_headers = {
            "User-Agent": "curiosity-engine/1.0 metadata-discovery",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        request_headers.update(headers or {})
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.budget.consume()
        response = self.post_transport(url, request_headers, body, self.timeout_seconds)
        self._note(response)
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