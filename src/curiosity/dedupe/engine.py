"""Near-Duplicate Firewall.

`exact normalized fingerprint -> FTS5 shortlist -> cheap lexical similarity`.
No embedding/model work happens here; contradictory anchors never merge.
"""

from __future__ import annotations

import re
from typing import Protocol

from rapidfuzz import fuzz

from curiosity.knowledge.engine import fact_fingerprint
from curiosity.quality.fidelity import anchor_conflict

_STOPWORDS = frozenset(
    """
    a an and are as at be but by for from has have in is it its of on or that the
    to with was were will would can could should may might their there this they
    you your we our which who whom what when where how why not no into over under
    about after before between during without through against than then so such
    only own same each other another most more also just very because
    """.split()
)
_TOKEN = re.compile(r"[a-z0-9]+")


def significant_tokens(text: str) -> frozenset[str]:
    """Lowercase alphanumeric tokens minus stopwords, for FTS shortlist queries
    and cheap lexical similarity."""
    tokens = {token for token in _TOKEN.findall(text.casefold()) if token not in _STOPWORDS}
    return frozenset(tokens)


def fts_terms(text: str) -> str:
    """FTS5 SHOULD query over significant tokens. Near-duplicates share only a
    few tokens, so AND would miss them; OR + bm25 shortlists the most relevant
    candidates and the lexical stage filters precisely."""
    tokens = significant_tokens(text)
    if not tokens:
        return ""
    return " OR ".join(sorted(tokens)[:12])


def lexical_similarity(a: str, b: str) -> float:
    """Cheap deterministic similarity for one-sentence facts using RapidFuzz's
    token-set ratio, which is robust to word reordering in paraphrases."""
    return fuzz.token_set_ratio(a, b) / 100.0


def similarity_tier(similarity: float) -> str:
    if similarity >= 0.85:
        return "same_wording"
    if similarity >= 0.58:
        return "same_claim"
    if similarity >= 0.35:
        return "related_concept"
    return "distinct"


class FactIndex(Protocol):
    def fact_exists(
        self,
        fingerprint: str,
        *,
        exclude_pulse_id: str | None = None,
        exclude_source_id: str | None = None,
    ) -> bool: ...

    def shortlist_fact_rows(
        self, terms: str, *, limit: int = 20, exclude_source_id: str | None = None
    ) -> list[tuple[str, str]]: ...


def firewall_decision(
    index: FactIndex,
    text: str,
    *,
    exclude_pulse_id: str | None = None,
    exclude_source_id: str | None = None,
) -> tuple[str, float]:
    """Classify a fact against the corpus: duplicate / same_wording / same_claim /
    related_concept / distinct. Contradictory anchors never suppress, and a
    source's own superseded facts never count against it."""
    fingerprint = fact_fingerprint(text)
    if index.fact_exists(
        fingerprint, exclude_pulse_id=exclude_pulse_id, exclude_source_id=exclude_source_id
    ):
        return "duplicate", 1.0
    best_tier = "distinct"
    best_sim = 0.0
    terms = fts_terms(text)
    for _pulse_id, fact_text in index.shortlist_fact_rows(
        terms, limit=20, exclude_source_id=exclude_source_id
    ):
        if anchor_conflict(text, fact_text):
            continue
        sim = lexical_similarity(text, fact_text)
        tier = similarity_tier(sim)
        if tier != "distinct" and sim > best_sim:
            best_tier, best_sim = tier, sim
    return best_tier, best_sim


def suppressed_pool_ids(
    index: FactIndex,
    recent_exposures: list[dict[str, str]],
    pool_rows: list[tuple[str, str, str]],
) -> frozenset[str]:
    """Pulse ids to exclude from refill because the user effectively just saw
    the same idea (exact fingerprint or same-claim paraphrase)."""
    suppressed: set[str] = set()
    recent_fingerprints = {
        str(item["fingerprint"]) for item in recent_exposures if item.get("fingerprint")
    }
    for pulse_id, fingerprint, _text in pool_rows:
        if fingerprint and fingerprint in recent_fingerprints:
            suppressed.add(pulse_id)
    for item in recent_exposures:
        text = item.get("fact_text") or ""
        if not text:
            continue
        terms = fts_terms(text)
        for pulse_id, fact_text in index.shortlist_fact_rows(terms, limit=10):
            if pulse_id in suppressed:
                continue
            if anchor_conflict(text, fact_text):
                continue
            tier = similarity_tier(lexical_similarity(text, fact_text))
            if tier in {"same_wording", "same_claim"}:
                suppressed.add(pulse_id)
    return frozenset(suppressed)