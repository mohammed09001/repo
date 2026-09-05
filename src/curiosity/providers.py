"""Optional provider adapters and the config-driven registry.

Core knowledge contracts never import this module. The CLI builds a neutral
:class:`ModelGateway` here and hands it to the application.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field

import httpx

from curiosity.config.settings import AppConfig, provider_readiness
from curiosity.contracts.model import (
    ModelCallResult,
    ModelCapabilities,
    ModelFailure,
    ModelGateway,
)


class ProviderError(ModelFailure):
    pass


@dataclass(frozen=True)
class OpenAICompatibleEndpoint:
    """Small OpenAI-compatible chat boundary with no SDK dependency."""

    api_key: str
    model_id: str
    base_url: str = "https://api.openai.com/v1"
    timeout_seconds: float = 20.0
    capabilities: ModelCapabilities = field(
        default_factory=lambda: ModelCapabilities(
            supports_structured=True,
            supports_prompt_cache=True,
            supports_batch=False,
            supports_usage_tokens=True,
            supports_cost_metadata=False,
        )
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "_client", None)

    def _client_for(self) -> httpx.Client:
        client = getattr(self, "_client", None)
        if client is None:
            client = httpx.Client(
                timeout=httpx.Timeout(
                    self.timeout_seconds,
                    connect=self.timeout_seconds,
                    read=self.timeout_seconds,
                    write=self.timeout_seconds,
                    pool=self.timeout_seconds,
                ),
                max_redirects=5,
            )
            object.__setattr__(self, "_client", client)
        return client

    def close(self) -> None:
        client = getattr(self, "_client", None)
        if client is not None:
            client.close()
            object.__setattr__(self, "_client", None)

    def generate(self, prompt: str) -> ModelCallResult:
        return self._chat(prompt, structured=None)

    def generate_structured(self, prompt: str, *, response_schema: dict) -> ModelCallResult:
        return self._chat(prompt, structured=response_schema)

    def _chat(self, prompt: str, *, structured: dict | None) -> ModelCallResult:
        body: dict[str, object] = {
            "model": self.model_id,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
        }
        if structured is not None:
            body["response_format"] = {
                "type": "json_schema",
                "json_schema": {"name": "result", "strict": True, "schema": structured},
            }
        started = time.monotonic()
        try:
            response = self._client_for().post(
                f"{self.base_url.rstrip('/')}/chat/completions",
                json=body,
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
        except httpx.HTTPError as exc:
            raise ProviderError("provider request failed") from exc
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ProviderError(f"provider returned HTTP {response.status_code}") from exc
        try:
            payload = response.json()
            content = payload["choices"][0]["message"]["content"]
            usage = payload.get("usage") or {}
            details = usage.get("prompt_tokens_details") or {}
            return ModelCallResult(
                content=str(content),
                input_tokens=int(usage.get("prompt_tokens", 0) or 0),
                output_tokens=int(usage.get("completion_tokens", 0) or 0),
                cached_tokens=int(details.get("cached_tokens", 0) or 0),
                latency_ms=(time.monotonic() - started) * 1000,
            )
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ProviderError("provider response was incomplete") from exc


def build_gateway(config: AppConfig) -> ModelGateway | None:
    """Construct a real provider gateway through the same path the CLI uses.

    Returns None whenever no usable endpoint can be built, preserving
    deterministic offline operation.
    """
    ready, _ = provider_readiness(config)
    if not ready:
        return None
    cheap = OpenAICompatibleEndpoint(
        api_key=config.provider_api_key,
        model_id=config.provider_cheap_model or config.provider_model,
        base_url=config.provider_base_url or "https://api.openai.com/v1",
    )
    strong = None
    if config.provider_strong_model:
        strong = OpenAICompatibleEndpoint(
            api_key=config.provider_api_key,
            model_id=config.provider_strong_model,
            base_url=config.provider_base_url or "https://api.openai.com/v1",
        )
    return ModelGateway(
        cheap=cheap,
        strong=strong,
        prices=config.provider_prices,
        max_calls=config.provider_max_calls,
        max_cost=config.provider_max_cost,
        cache_enabled=config.provider_cache,
    )