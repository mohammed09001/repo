"""Provider-neutral ambient runtime state machine.

Raw harness events are translated into a small derived runtime state that an
ambient playback loop may consult. The controller only ever influences whether
ambient playback is active or quiet and whether a local queue may be refilled;
it never touches source truth, verification, knowledge content, or ranking.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

from curiosity.contracts.models import HarnessEvent

# Persisted ambient state is only trustworthy while fresh. An agent session that
# stops emitting events for longer than this is treated as ended, never guessed.
STALE_AFTER_SECONDS = 600


class AmbientState(StrEnum):
    UNKNOWN = "unknown"
    ACTIVE_WORK = "active_work"
    WAITING_OR_IDLE = "waiting_or_idle"
    TURN_COMPLETE = "turn_complete"
    QUIET = "quiet"


class AmbientPosture(StrEnum):
    ACTIVE = "active"
    QUIET = "quiet"


# Raw adapter event type -> derived ambient state. Unknown event types return
# None so the controller never guesses from an unsupported signal.
_EVENT_STATE: dict[str, AmbientState] = {
    "session_start": AmbientState.ACTIVE_WORK,
    "working": AmbientState.ACTIVE_WORK,
    "idle": AmbientState.WAITING_OR_IDLE,
    "turn_complete": AmbientState.TURN_COMPLETE,
    "session_end": AmbientState.QUIET,
}

# Derived state -> playback posture. Only actual agent work keeps ambient
# playback active; completion/idle/end transitions quiet it. UNKNOWN is quiet:
# ambient playback never starts without evidence of an active coding session.
_STATE_POSTURE: dict[AmbientState, AmbientPosture] = {
    AmbientState.UNKNOWN: AmbientPosture.QUIET,
    AmbientState.ACTIVE_WORK: AmbientPosture.ACTIVE,
    AmbientState.WAITING_OR_IDLE: AmbientPosture.QUIET,
    AmbientState.TURN_COMPLETE: AmbientPosture.QUIET,
    AmbientState.QUIET: AmbientPosture.QUIET,
}


def ambient_state_for_event(event_type: str) -> AmbientState | None:
    """Return the derived state for a raw event type, or None when unsupported."""
    return _EVENT_STATE.get(event_type)


def posture_for_state(state: AmbientState) -> AmbientPosture:
    return _STATE_POSTURE[state]


@dataclass(frozen=True)
class AmbientSignal:
    """One derived transition outcome for a raw harness event."""

    state: AmbientState
    posture: AmbientPosture
    refill_allowed: bool
    changed: bool


class AmbientController:
    """Derives and persists the minimal local ambient runtime state.

    Repeated events that map to the current state are idempotent: they neither
    rewrite the persisted timestamp nor count as a transition, which debounces
    redundant lifecycle signals. State changes are always applied and stamped
    with their transition time. Restart restores the last state only while it
    is still fresh; stale or missing state resolves to UNKNOWN (quiet).
    """

    def __init__(self, store: Any, *, now: Callable[[], datetime] | None = None) -> None:
        self.store = store
        self.now = now or (lambda: datetime.now(UTC))

    def current_state(self) -> AmbientState:
        row = self.store.get_ambient_state()
        if row is None:
            return AmbientState.UNKNOWN
        state, updated_at = row
        try:
            updated = datetime.fromisoformat(str(updated_at))
        except ValueError:
            return AmbientState.UNKNOWN
        if self.now() - updated > timedelta(seconds=STALE_AFTER_SECONDS):
            return AmbientState.UNKNOWN
        try:
            return AmbientState(state)
        except ValueError:
            return AmbientState.UNKNOWN

    def ingest(self, event: HarnessEvent) -> AmbientSignal:
        current = self.current_state()
        posture = posture_for_state(current)
        signal = AmbientSignal(current, posture, posture == AmbientPosture.ACTIVE, False)
        target = ambient_state_for_event(event.event_type)
        if target is None or target == current:
            return signal
        self.store.put_ambient_state(target.value, at=self.now())
        posture = posture_for_state(target)
        return AmbientSignal(target, posture, posture == AmbientPosture.ACTIVE, True)

    def posture(self) -> AmbientPosture:
        return posture_for_state(self.current_state())

    def playback_active(self) -> bool:
        return self.posture() == AmbientPosture.ACTIVE

    def refill_allowed(self) -> bool:
        return self.playback_active()