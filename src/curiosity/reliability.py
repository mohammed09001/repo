"""Small deterministic resource guards shared by local engines."""

from dataclasses import dataclass


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
