"""Small deterministic resource guards shared by local engines."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Budget:
    max_requests: int = 20
    max_bytes: int = 2_000_000
    requests: int = 0
    bytes: int = 0

    def consume(self, *, byte_count: int = 0) -> None:
        if self.requests + 1 > self.max_requests or self.bytes + byte_count > self.max_bytes:
            raise RuntimeError("local budget exhausted")
        self.requests += 1
        self.bytes += byte_count

    def summary(self) -> dict[str, int]:
        return {"requests": self.requests, "bytes": self.bytes}


def retry_delay(attempt: int, *, base_seconds: float = 0.25, jitter: float = 0.0) -> float:
    if attempt < 0:
        raise ValueError("attempt must be non-negative")
    return base_seconds * (2**attempt) + jitter


TRANSIENT_HTTP_STATUSES = frozenset({408, 425, 429, 500, 502, 503, 504})


def classify_http_status(status: int) -> str:
    """Per-stage retry classification: ``transient`` or ``permanent``.

    Connection/timeout and 5xx/429/408/425 errors may be retried with capped
    attempts; other 4xx responses are permanent and must not spin.
    """
    if status in TRANSIENT_HTTP_STATUSES:
        return "transient"
    return "permanent"


def classify_exception(error: BaseException) -> str:
    """Classify a transport/parser exception as ``transient`` or ``permanent``.

    Network-layer and timeout errors are transient; a marked transient flag on
    the error wins; anything else is permanent.
    """
    transient = getattr(error, "transient", None)
    if isinstance(transient, bool):
        return "transient" if transient else "permanent"
    import httpx

    if isinstance(error, (httpx.TransportError, httpx.TimeoutException, httpx.ConnectError)):
        return "transient"
    return "permanent"


def bounded_retry(
    operation: Any,
    *,
    attempts: int = 3,
    base_seconds: float = 0.25,
    is_transient: Any = None,
    on_retry: Any = None,
) -> Any:
    """Run ``operation()`` with a capped exponential-backoff retry.

    ``is_transient(error)`` decides whether a failure may be retried; a ``None``
    classifier retries only errors carrying a truthy ``transient`` attribute or
    HTTPX transport/timeout errors. ``on_retry(attempt)`` is invoked before each
    backoff so callers can count retries. After the final attempt the last
    error is re-raised unchanged.
    """
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    last_error: BaseException | None = None
    for attempt in range(attempts):
        try:
            return operation()
        except BaseException as error:  # noqa: BLE001 - classified and capped
            last_error = error
            classifier = is_transient(error) if is_transient is not None else classify_exception(error)
            if classifier != "transient" or attempt >= attempts - 1:
                raise
            if on_retry is not None:
                on_retry(attempt)
            import time

            time.sleep(retry_delay(attempt, base_seconds=base_seconds))
    assert last_error is not None
    raise last_error
