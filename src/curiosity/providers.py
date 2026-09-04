"""Optional provider adapters. Core knowledge contracts never import this module."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ProviderError(RuntimeError):
    pass


@dataclass(frozen=True)
class OpenAICompatibleStructuredProvider:
    """Small OpenAI-compatible JSON-schema boundary with no SDK dependency."""

    api_key: str
    model_id: str
    base_url: str = "https://api.openai.com/v1"
    timeout_seconds: float = 20.0

    def generate_structured(self, prompt: str) -> tuple[str, int, int, float]:
        schema = {
            "name": "knowledge_candidates",
            "strict": True,
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "statement": {"type": "string"},
                        "chunk_id": {"type": "string"},
                        "topics": {"type": "array", "items": {"type": "string"}},
                        "why_interesting": {"type": "string"},
                    },
                    "required": ["statement", "chunk_id", "topics", "why_interesting"],
                    "additionalProperties": False,
                },
            },
        }
        body = json.dumps(
            {
                "model": self.model_id,
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_schema", "json_schema": schema},
                "temperature": 0,
            }
        ).encode()
        request = Request(
            f"{self.base_url.rstrip('/')}/chat/completions",
            data=body,
            method="POST",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
        )
        started = time.monotonic()
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:  # noqa: S310
                payload = json.loads(response.read().decode())
        except (HTTPError, URLError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ProviderError("structured provider request failed") from exc
        try:
            content = payload["choices"][0]["message"]["content"]
            usage = payload.get("usage", {})
            return (
                str(content),
                int(usage.get("prompt_tokens", 0)),
                int(usage.get("completion_tokens", 0)),
                time.monotonic() - started,
            )
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise ProviderError("structured provider response was incomplete") from exc
