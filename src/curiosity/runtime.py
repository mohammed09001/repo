"""Safe local terminal playback primitives."""

from __future__ import annotations

import re
import textwrap
from dataclasses import dataclass


def safe_text(value: str) -> str:
    return re.sub(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]", "", value)


@dataclass
class Playback:
    cards: tuple[tuple[str, str, str], ...]
    interval_seconds: int = 10
    position: int = 0
    paused: bool = False
    stopped: bool = False

    def __post_init__(self) -> None:
        if not 3 <= self.interval_seconds <= 3600:
            raise ValueError("interval must be 3..3600 seconds")

    def next(self) -> tuple[str, str, str] | None:
        if self.stopped or self.paused or self.position >= len(self.cards):
            return None
        card = self.cards[self.position]
        self.position += 1
        return card

    def pause(self) -> None:
        self.paused = True

    def resume(self) -> None:
        self.paused = False

    def stop(self) -> None:
        self.stopped = True


def render(card: tuple[str, str, str], *, width: int = 80) -> str:
    hook, body, source = (safe_text(part) for part in card)
    return "\n".join(
        [
            textwrap.fill(hook, width=width),
            textwrap.fill(body, width=width),
            f"Source: {textwrap.shorten(source, width=width)}",
        ]
    )
