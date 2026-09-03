"""Ports used by adapters; core code depends on these interfaces only."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from random import Random
from typing import Protocol


class ModelGeneration(Protocol):
    def generate(self, prompt: str) -> str: ...


class Embeddings(Protocol):
    def embed(self, texts: Sequence[str]) -> Sequence[Sequence[float]]: ...


class SourceAdapter(Protocol):
    def fetch(self, locator: str) -> str: ...


class Parser(Protocol):
    def parse(self, raw_text: str) -> str: ...


class Clock(Protocol):
    def now(self) -> datetime: ...


class RandomSeed(Protocol):
    def rng(self) -> Random: ...


class NoLLMProvider:
    """Deterministic offline fallback. It never calls a model or network."""

    def generate(self, prompt: str) -> str:
        cleaned = " ".join(prompt.split())
        if not cleaned:
            return ""
        sentence = cleaned.split(". ", 1)[0].rstrip(".")
        return f"Consider: {sentence}."
