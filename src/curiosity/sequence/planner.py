from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class QueueItem:
    card_id: str
    topic: str
    score: float
    verified: bool
    reason: str
    sequence_id: str | None = None
    text: str = ""
    fingerprint: str = ""


def plan_queue(
    items: list[QueueItem],
    *,
    size: int = 6,
    seed: int = 0,
    max_topic_streak: int = 2,
    diversity_lambda: float = 0.0,
    unexpected_share: float = 0.0,
    unexpected_topics: frozenset[str] = frozenset(),
    similarity: Callable[[QueueItem, QueueItem], float] | None = None,
) -> tuple[QueueItem, ...]:
    """Greedy MMR-like local planning with transparent bounded rules.

    Relevance is `score`; redundancy is the max similarity to already-selected
    items discounted by ``diversity_lambda``. Unverified items never enter;
    a configured share of slots can be reserved for unexpected (low-weight)
    topics; consecutive same-topic runs are capped. Deterministic given seed.
    """
    rng = random.Random(seed)
    eligible = [item for item in items if item.verified]
    remaining = sorted(eligible, key=lambda item: (-item.score, rng.random(), item.card_id))
    result: list[QueueItem] = []
    unexpected_reserved = max(0, int(round(size * unexpected_share)))
    unexpected_used = 0

    def effective(item: QueueItem) -> float:
        redundancy = 0.0
        if similarity is not None and result:
            redundancy = max(similarity(item, previous) for previous in result)
        return item.score - diversity_lambda * redundancy

    while remaining and len(result) < size:
        if len(result) >= max_topic_streak:
            blocked_topic = result[-1].topic
            alternatives = [item for item in remaining if item.topic != blocked_topic]
            # The streak cap is a diversity preference: it only bites when the
            # corpus actually offers another topic. A single-topic feed must
            # not starve.
            candidates = alternatives if alternatives else remaining
        else:
            candidates = remaining
        if not candidates:
            break
        chosen = max(candidates, key=lambda item: (effective(item), rng.random(), item.card_id))
        if unexpected_reserved and chosen.topic in unexpected_topics:
            if unexpected_used >= unexpected_reserved:
                mainstream = [item for item in candidates if item.topic not in unexpected_topics]
                if mainstream:
                    chosen = max(
                        mainstream, key=lambda item: (effective(item), rng.random(), item.card_id)
                    )
            else:
                unexpected_pool = [item for item in candidates if item.topic in unexpected_topics]
                if unexpected_pool:
                    chosen = max(
                        unexpected_pool, key=lambda item: (effective(item), rng.random(), item.card_id)
                    )
        reason = _pick_reason(chosen, result, unexpected_topics, similarity)
        result.append(replace(chosen, reason=reason))
        remaining.remove(chosen)
        if chosen.topic in unexpected_topics:
            unexpected_used += 1
    return tuple(result)


def _pick_reason(
    chosen: QueueItem,
    result: list[QueueItem],
    unexpected_topics: frozenset[str],
    similarity: Callable[[QueueItem, QueueItem], float] | None,
) -> str:
    if chosen.topic in unexpected_topics:
        return "unexpected_discovery"
    if result and similarity is not None:
        related = max(similarity(chosen, previous) for previous in result)
        if related >= 0.5:
            return "continuity_related"
        return "diversity_balanced"
    return "relevance"