"""Safe local terminal playback primitives."""

from __future__ import annotations

import re
import textwrap
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol


class PlaybackSource(Protocol):
    """The small local boundary used by the terminal loop."""

    def current_playback_pulse(self): ...

    def acknowledge_playback_pulse(self, pulse) -> bool: ...


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
    _, body, _ = (safe_text(part) for part in card)
    return textwrap.fill(body, width=width)


def render_fact(fact: str, *, width: int = 80) -> str:
    """Normal playback deliberately has no source, topic, or other metadata."""
    return textwrap.fill(safe_text(fact), width=width)


@dataclass
class TerminalPlayback:
    """A testable, non-TUI timed terminal loop over a precomputed local queue."""

    source: PlaybackSource
    sleeper: Callable[[float], None]
    write: Callable[[str], None]
    interval_seconds: float = 10
    width: int = 80

    def __post_init__(self) -> None:
        if self.interval_seconds <= 0:
            raise ValueError("interval must be positive")

    def run(self, *, once: bool = False) -> int:
        shown = 0
        while True:
            pulse = self.source.current_playback_pulse()
            if pulse is None:
                return shown
            # Render first, then acknowledge in one database transaction. This
            # gives at-least-once display on a process crash, never skipped facts.
            self.write(render_fact(pulse.display_fact, width=self.width))
            if not self.source.acknowledge_playback_pulse(pulse):
                return shown
            shown += 1
            if once:
                return shown
            self.sleeper(self.interval_seconds)
