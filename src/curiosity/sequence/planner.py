from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class QueueItem:
    card_id: str
    topic: str
    score: float
    verified: bool
    reason: str
    sequence_id: str | None = None


def plan_queue(
    items: list[QueueItem], *, size: int = 6, seed: int = 0, max_topic_streak: int = 2
) -> tuple[QueueItem, ...]:
    """Plan outside playback; unverified/stale items never enter the queue."""
    rng = random.Random(seed)
    eligible = [item for item in items if item.verified]
    ordered = sorted(eligible, key=lambda item: (-item.score, rng.random(), item.card_id))
    result: list[QueueItem] = []
    for item in ordered:
        if len(result) == size:
            break
        if len(result) >= max_topic_streak and all(
            previous.topic == item.topic for previous in result[-max_topic_streak:]
        ):
            continue
        result.append(item)
    return tuple(result)
