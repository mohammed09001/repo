from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProfilePreferences:
    topic_weights: dict[str, float] = field(default_factory=lambda: {"general": 1.0})
    excluded_topics: frozenset[str] = frozenset()
    unexpected_discovery_weight: float = 0.1
    max_consecutive_topic: int = 2

    def normalized_weights(self) -> dict[str, float]:
        values = {
            key: max(0.0, value)
            for key, value in self.topic_weights.items()
            if key not in self.excluded_topics
        }
        total = sum(values.values())
        return {key: value / total for key, value in values.items()} if total else {"general": 1.0}


@dataclass(frozen=True)
class Candidate:
    id: str
    topic: str
    source_id: str
    verified: bool
    quality: float
    novelty: float
    curiosity: float
    freshness: float


@dataclass(frozen=True)
class Ranked:
    candidate: Candidate
    score: float
    reasons: dict[str, float]


def rank(
    candidates: list[Candidate],
    profile: ProfilePreferences,
    *,
    recent_ids: frozenset[str] = frozenset(),
    recent_topics: tuple[str, ...] = (),
) -> list[Ranked]:
    weights = profile.normalized_weights()
    ranked = []
    for item in candidates:
        if not item.verified or item.topic in profile.excluded_topics:
            continue
        interest = weights.get(item.topic, profile.unexpected_discovery_weight)
        repetition = (
            1.0
            if item.id in recent_ids
            or recent_topics[-profile.max_consecutive_topic :].count(item.topic)
            >= profile.max_consecutive_topic
            else 0.0
        )
        reasons = {
            "interest": interest,
            "quality": item.quality,
            "novelty": item.novelty,
            "curiosity": item.curiosity,
            "freshness": item.freshness,
            "repetition_penalty": -repetition,
        }
        ranked.append(Ranked(item, sum(reasons.values()), reasons))
    return sorted(ranked, key=lambda value: (-value.score, value.candidate.id))
