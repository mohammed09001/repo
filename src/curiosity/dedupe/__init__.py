"""Cheap local near-duplicate suppression without embeddings."""

from curiosity.dedupe.engine import (
    firewall_decision,
    fts_terms,
    lexical_similarity,
    significant_tokens,
    similarity_tier,
    suppressed_pool_ids,
)

__all__ = [
    "firewall_decision",
    "fts_terms",
    "lexical_similarity",
    "significant_tokens",
    "similarity_tier",
    "suppressed_pool_ids",
]