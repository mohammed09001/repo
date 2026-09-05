"""Source-grounded candidate extraction; derived claims are never source truth."""

from .engine import KnowledgeCandidate, extract_no_llm, is_english, make_candidate

__all__ = ["KnowledgeCandidate", "extract_no_llm", "is_english", "make_candidate"]