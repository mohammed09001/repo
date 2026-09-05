from __future__ import annotations

import math
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
    quality: float = 1.0
    novelty: float = 1.0
    curiosity: float = 0.5
    freshness: float = 1.0
    source_quality: float = 0.5
    usefulness: float = 0.5
    signal_reasons: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Ranked:
    candidate: Candidate
    score: float
    reasons: dict[str, float]


def quality_class(verification: dict[str, object]) -> tuple[float, str]:
    """Quality signal from stored verification state; never invented."""
    if verification.get("status") != "verified":
        return 0.0, "not_verified"
    if verification.get("risk_flags"):
        return 0.4, "risk_flagged"
    reasons = set(verification.get("reason_codes", ()))
    if "direct_textual_support" in reasons:
        return 1.0, "direct_support"
    if verification.get("provider_used"):
        return 0.8, "model_verified"
    return 0.9, "verified_deterministic"


def source_quality_class(trust: str) -> tuple[float, str]:
    if trust in {"user", "local", "curated"}:
        return 1.0, "trusted_source"
    return 0.5, "remote_untrusted"


def freshness_from_age(age_seconds: float, *, half_life_days: float = 90.0) -> float:
    """Evergreen-friendly recency signal; mostly neutral for old facts."""
    return math.exp(-max(0.0, age_seconds) / 3600 / 24 / half_life_days)


def novelty_from_distance(
    distance: int | None, *, hard_window: int = 10, cooldown: int = 30
) -> float:
    """Deterministic exposure-distance cooldown: a fact seen within
    ``hard_window`` exposures is suppressed upstream; just past it novelty is
    low and recovers to 1.0."""
    if distance is None or distance < 0:
        return 1.0
    span = max(1, cooldown - hard_window)
    return max(0.0, min(1.0, (distance - hard_window) / span))


def novelty_from_age(
    age_seconds: float, *, hard_hours: float = 6.0, cooldown_hours: float = 72.0
) -> float:
    """Deterministic wall-clock cooldown so a continuous session never
    tight-loops through a small corpus regardless of exposure distance."""
    age_hours = max(0.0, age_seconds) / 3600.0
    span = max(1.0, cooldown_hours - hard_hours)
    return max(0.0, min(1.0, (age_hours - hard_hours) / span))


def rank(
    candidates: list[Candidate],
    profile: ProfilePreferences,
    *,
    recent_ids: frozenset[str] = frozenset(),
    recent_topics: tuple[str, ...] = (),
    recent_sources: frozenset[str] = frozenset(),
) -> list[Ranked]:
    weights = profile.normalized_weights()
    ranked = []
    for item in candidates:
        if not item.verified or item.topic in profile.excluded_topics:
            continue
        interest = weights.get(item.topic, profile.unexpected_discovery_weight)
        repetition = 1.0 if item.id in recent_ids else 0.0
        topic_streak = (
            1.0
            if recent_topics[-profile.max_consecutive_topic :].count(item.topic)
            >= profile.max_consecutive_topic
            else 0.0
        )
        source_penalty = 0.1 if item.source_id in recent_sources else 0.0
        reasons = {
            "interest": interest,
            "quality": item.quality,
            "source_quality": item.source_quality,
            "usefulness": item.usefulness,
            "freshness": item.freshness,
            "novelty": item.novelty,
            "curiosity": item.curiosity,
            "repetition_penalty": -repetition,
            "topic_streak_penalty": -topic_streak,
            "source_diversity_penalty": -source_penalty,
        }
        ranked.append(Ranked(item, sum(reasons.values()), reasons))
    return sorted(ranked, key=lambda value: (-value.score, value.candidate.id))