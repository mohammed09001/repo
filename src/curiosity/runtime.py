"""Safe local terminal playback primitives."""

from __future__ import annotations

import os
import re
import sys
import textwrap
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol


class PlaybackSource(Protocol):
    """The small local boundary used by the terminal loop."""

    def current_playback_pulse(self): ...

    def acknowledge_playback_pulse(self, pulse) -> bool: ...

    def refill_playback(self) -> bool: ...


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


def enable_vt() -> bool:
    """Enable ANSI/VT processing on a Windows console; a no-op elsewhere.

    Returns True when cursor control sequences are usable on the attached
    output, False when they are not (e.g. a captured or non-console stream),
    in which case callers must fall back to newline records.
    """
    if os.name != "nt":
        return True
    try:
        import ctypes
        import msvcrt

        kernel32 = ctypes.windll.kernel32
        handle = msvcrt.get_osfhandle(sys.stdout.fileno())
        mode = ctypes.c_uint32()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        return True
    except (AttributeError, OSError, ValueError):
        return False


class TtySurface:
    """A minimal single-region terminal surface for one-fact-at-a-time display.

    Only the currently displayed fact is visible: each update returns to the
    start of the owned region, clears it, and writes the new text. The first
    render claims the line the cursor already occupies, so unrelated terminal
    history is never cleared. ``close`` restores a clean final line so the next
    shell prompt is placed below the final fact. Resize is handled by tracking
    the exact number of lines the wrapped render occupies.
    """

    def __init__(self, write: Callable[[str], None]) -> None:
        self.write = write
        self.owned = 0

    def show(self, text: str) -> None:
        text = safe_text(text)
        lines = text.count("\n") + 1
        if self.owned:
            self.write("\r")
            for _ in range(self.owned - 1):
                self.write("\x1b[2K\x1b[1A")
            self.write("\x1b[2K")
        self.write(text)
        self.owned = lines

    def close(self) -> None:
        if self.owned:
            self.write("\r\n")
            self.owned = 0


@dataclass
class TerminalPlayback:
    """A testable, non-TUI timed terminal loop over a precomputed local queue.

    ``surface`` switches the renderer to single-region replacement for an
    interactive TTY; without it the loop emits newline records, which is the
    safe redirected/non-TTY path. ``should_continue`` (ambient mode) stops the
    loop at the next fact boundary while the ambient controller is quiet, and
    ``should_refill`` gates the local-only queue refill behind the controller.
    """

    source: PlaybackSource
    sleeper: Callable[[float], None]
    write: Callable[[str], None]
    interval_seconds: float = 10
    width: int = 80
    surface: TtySurface | None = None
    should_continue: Callable[[], bool] | None = None
    should_refill: Callable[[], bool] | None = None

    def __post_init__(self) -> None:
        if self.interval_seconds <= 0:
            raise ValueError("interval must be positive")

    def run(self, *, once: bool = False) -> int:
        shown = 0
        try:
            while True:
                if self.should_continue is not None and not self.should_continue():
                    return shown
                pulse = self.source.current_playback_pulse()
                if pulse is None:
                    return shown
                # Render first, then acknowledge in one database transaction. This
                # gives at-least-once display on a process crash, never skipped facts.
                text = render_fact(pulse.display_fact, width=self.width)
                if self.surface is not None:
                    self.surface.show(text)
                else:
                    self.write(text)
                if not self.source.acknowledge_playback_pulse(pulse):
                    return shown
                shown += 1
                if once:
                    return shown
                # Local-only refill happens outside the render critical section so
                # the reservoir stays above its low watermark; never network/parse/model.
                refill = getattr(self.source, "refill_playback", None)
                if refill is not None and (self.should_refill is None or self.should_refill()):
                    refill()
                self.sleeper(self.interval_seconds)
        finally:
            if self.surface is not None:
                self.surface.close()
