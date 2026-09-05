"""Provider-neutral model boundary. Core quality code depends only on these
shapes; provider-specific SDKs and payloads never cross into domain records."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class ModelCallResult:
    """One bounded model response with best-effort usage accounting.

    ``cached_tokens`` reflects provider-reported prompt-cache savings when the
    provider exposes them; absence is encoded as 0, never as a failure.
    """

    content: str
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    latency_ms: float = 0.0


class ModelFailure(RuntimeError):
    """Neutral provider failure. Core code catches this, never provider SDK types."""


@dataclass(frozen=True)
class ModelCapabilities:
    supports_structured: bool = True
    supports_prompt_cache: bool = False
    supports_batch: bool = False
    supports_usage_tokens: bool = True
    supports_cost_metadata: bool = False


class ModelEndpoint(Protocol):
    """The minimal gateway a provider adapter must satisfy."""

    model_id: str
    capabilities: ModelCapabilities

    def generate(self, prompt: str) -> ModelCallResult: ...

    def generate_structured(self, prompt: str, *, response_schema: dict) -> ModelCallResult: ...


@dataclass(frozen=True)
class ModelGateway:
    """Provider-neutral bundle wired by the CLI; core consumes only this shape.

    ``prices`` holds explicit per-million-token input/output prices in user
    config only; an empty map means cost is unknown, never zero.
    """

    cheap: ModelEndpoint
    strong: ModelEndpoint | None = None
    prices: dict[str, float] = field(default_factory=dict)
    max_calls: int | None = None
    max_cost: float | None = None
    cache_enabled: bool = True

    def cost_for(self, input_tokens: int, output_tokens: int) -> float | None:
        if not self.prices:
            return None
        per_input = self.prices.get("input", 0.0)
        per_output = self.prices.get("output", 0.0)
        return (input_tokens / 1_000_000 * per_input) + (output_tokens / 1_000_000 * per_output)

    def close(self) -> None:
        close = getattr(self.cheap, "close", None)
        if close is not None:
            close()
        if self.strong is not None:
            close = getattr(self.strong, "close", None)
            if close is not None:
                close()