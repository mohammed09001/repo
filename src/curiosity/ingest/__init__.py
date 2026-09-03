"""Bounded fetch, parse, normalize, and deterministic chunking pipeline."""

from .pipeline import IngestionPipeline, chunk_text, normalize_text

__all__ = ["IngestionPipeline", "chunk_text", "normalize_text"]
