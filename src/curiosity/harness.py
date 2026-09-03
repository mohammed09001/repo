"""Optional, minimized harness lifecycle normalization."""

from datetime import UTC, datetime

from curiosity.contracts.models import HarnessEvent, JobStatus, ProvenanceClass, deterministic_id

SUPPORTED = {"session_start", "working", "idle", "turn_complete", "session_end"}


def normalize(adapter: str, event_type: str, *, at: datetime | None = None) -> HarnessEvent | None:
    if event_type not in SUPPORTED:
        return None
    moment = (at or datetime.now(UTC)).astimezone(UTC)
    return HarnessEvent(
        id=deterministic_id("event", adapter, event_type, moment.isoformat()),
        job_status=JobStatus.RUNNING if event_type == "working" else JobStatus.SUCCEEDED,
        event_type=event_type,
        occurred_at=moment,
        details={"adapter": adapter},
        provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
    )


CAPABILITIES = {
    "manual": {"start": False, "busy": False, "idle": False, "complete": False},
    "codex_notify": {"start": False, "busy": False, "idle": False, "complete": True},
}
