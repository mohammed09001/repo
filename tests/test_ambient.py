"""Ambient runtime controller: state transitions, debounce, restart, isolation."""

from datetime import UTC, datetime, timedelta

from curiosity.ambient import (
    STALE_AFTER_SECONDS,
    AmbientController,
    AmbientPosture,
    AmbientState,
    ambient_state_for_event,
    posture_for_state,
)
from curiosity.application import CuriosityApplication
from curiosity.harness import normalize
from curiosity.store import LocalStore


def _now() -> datetime:
    return datetime(2026, 9, 5, 12, 0, tzinfo=UTC)


def _event(event_type: str, *, adapter: str = "opencode", at: datetime | None = None):
    return normalize(adapter, event_type, at=at or _now())


def test_state_transition_table_is_deterministic():
    assert ambient_state_for_event("session_start") == AmbientState.ACTIVE_WORK
    assert ambient_state_for_event("working") == AmbientState.ACTIVE_WORK
    assert ambient_state_for_event("idle") == AmbientState.WAITING_OR_IDLE
    assert ambient_state_for_event("turn_complete") == AmbientState.TURN_COMPLETE
    assert ambient_state_for_event("session_end") == AmbientState.QUIET
    assert ambient_state_for_event("not_a_real_event") is None
    assert posture_for_state(AmbientState.ACTIVE_WORK) == AmbientPosture.ACTIVE
    assert posture_for_state(AmbientState.UNKNOWN) == AmbientPosture.QUIET
    assert posture_for_state(AmbientState.WAITING_OR_IDLE) == AmbientPosture.QUIET
    assert posture_for_state(AmbientState.TURN_COMPLETE) == AmbientPosture.QUIET
    assert posture_for_state(AmbientState.QUIET) == AmbientPosture.QUIET


def test_full_lifecycle_sequence_drives_posture(tmp_path):
    with LocalStore(tmp_path / "ambient.db") as store:
        controller = AmbientController(store, now=_now)
        assert controller.current_state() == AmbientState.UNKNOWN
        assert not controller.playback_active()
        assert controller.ingest(_event("session_start")).changed
        assert controller.playback_active()
        assert controller.refill_allowed()
        assert controller.ingest(_event("working")).changed is False  # same derived state
        assert controller.ingest(_event("idle")).changed
        assert controller.current_state() == AmbientState.WAITING_OR_IDLE
        assert not controller.playback_active()
        assert not controller.refill_allowed()
        assert controller.ingest(_event("turn_complete")).changed
        assert controller.current_state() == AmbientState.TURN_COMPLETE
        assert not controller.playback_active()


def test_unsupported_events_never_guess(tmp_path):
    from curiosity.contracts.models import (
        HarnessEvent,
        JobStatus,
        ProvenanceClass,
        deterministic_id,
    )

    with LocalStore(tmp_path / "ambient.db") as store:
        controller = AmbientController(store, now=_now)
        unknown = HarnessEvent(
            id=deterministic_id("event", "mystery", "fixture"),
            job_status=JobStatus.SUCCEEDED,
            event_type="mystery",
            occurred_at=_now(),
            details={"adapter": "opencode"},
            provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
        )
        signal = controller.ingest(unknown)
        assert signal.state == AmbientState.UNKNOWN
        assert not signal.changed
        assert controller.current_state() == AmbientState.UNKNOWN


def test_repeated_events_are_idempotent_and_debounced(tmp_path):
    with LocalStore(tmp_path / "ambient.db") as store:
        controller = AmbientController(store, now=_now)
        first = controller.ingest(_event("working"))
        assert first.changed
        assert store.get_ambient_state() == ("active_work", _now().isoformat())
        repeated = controller.ingest(_event("working"))
        assert not repeated.changed
        assert repeated.state == AmbientState.ACTIVE_WORK
        # The persisted timestamp is not rewritten by a redundant event.
        assert store.get_ambient_state() == ("active_work", _now().isoformat())
        assert store.connection.execute("SELECT COUNT(*) FROM ambient_state").fetchone()[0] == 1


def test_stale_state_restarts_as_unknown(tmp_path):
    with LocalStore(tmp_path / "ambient.db") as store:
        controller = AmbientController(store, now=_now)
        controller.ingest(_event("working"))
        assert controller.playback_active()
        stale = AmbientController(store, now=lambda: _now() + timedelta(seconds=STALE_AFTER_SECONDS + 1))
        assert stale.current_state() == AmbientState.UNKNOWN
        assert not stale.playback_active()


def test_fresh_state_survives_restart(tmp_path):
    with LocalStore(tmp_path / "ambient.db") as store:
        AmbientController(store, now=_now).ingest(_event("working"))
    with LocalStore(tmp_path / "ambient.db") as reopened:
        assert AmbientController(reopened, now=_now).playback_active()


def test_controller_never_touches_knowledge_content(tmp_path):
    from curiosity.ingest.pipeline import FetchResponse

    class FixtureFetcher:
        def fetch(self, url, *, headers, max_bytes):
            return FetchResponse(200, b"A deterministic fact for isolation.", "text/plain")

    with LocalStore(tmp_path / "ambient.db") as store:
        app = CuriosityApplication(store, fetcher=FixtureFetcher(), now=_now)
        app.add_source("https://example.test/isolation")
        assert app.refresh_build().pulses_built == 1
        before = store.list_pulses()[0].model_dump()
        before_source = store.list_sources()[0].model_dump()
        before_verification = store.get_pulse_verification(before["id"])
        before_stats = app.stats()
        # A full noisy lifecycle never changes knowledge truth.
        for event_type in ("session_start", "working", "working", "idle", "turn_complete", "session_end"):
            app.record_harness_event(_event(event_type))
        after = store.list_pulses()[0].model_dump()
        assert after == before
        assert store.list_sources()[0].model_dump() == before_source
        assert store.get_pulse_verification(before["id"]) == before_verification
        assert app.stats() == before_stats
        # The controller only wrote the single ambient_state row plus events.
        assert store.get_ambient_state() is not None


def test_record_harness_event_returns_signal_and_drives_application_state(tmp_path):
    with LocalStore(tmp_path / "ambient.db") as store:
        app = CuriosityApplication(store, now=_now)
        signal = app.record_harness_event(_event("working"))
        assert signal.changed
        assert app.ambient_state()["posture"] == "active"
        assert app.ambient_playback_active()
        assert app.ambient_refill_allowed()
        app.record_harness_event(_event("idle"))
        assert app.ambient_state()["state"] == "waiting_or_idle"
        assert not app.ambient_playback_active()
        assert not app.ambient_refill_allowed()


class _FactFetcher:
    def fetch(self, url, *, headers, max_bytes):
        from curiosity.ingest.pipeline import FetchResponse

        body = b"Ambient integration fact one." if "one" in url else b"Ambient integration fact two."
        return FetchResponse(200, body, "text/plain")


def _build_two_facts(tmp_path):
    database = tmp_path / "data" / "curiosity.db"
    store = LocalStore(database)
    app = CuriosityApplication(store, fetcher=_FactFetcher(), now=_now)
    app.add_source("https://example.test/one")
    app.add_source("https://example.test/two")
    assert app.refresh_build().pulses_built == 2
    app.prepare_playback(size=6)
    return store, app


def test_ambient_playback_stops_at_fact_boundary_when_controller_quiets(tmp_path):
    from curiosity.runtime import TerminalPlayback, TtySurface

    store, app = _build_two_facts(tmp_path)
    try:
        app.record_harness_event(_event("working"))
        output, sleeps = [], []
        surface = TtySurface(output.append)

        def sleeper(seconds):
            sleeps.append(seconds)
            if len(sleeps) == 1:
                # The controller quiets during the first fact's dwell.
                app.record_harness_event(_event("idle"))

        shown = TerminalPlayback(
            app,
            sleeper,
            output.append,
            surface=surface,
            should_continue=app.ambient_playback_active,
            should_refill=app.ambient_refill_allowed,
        ).run()
        assert shown == 1
        assert sleeps == [10]
        # The current fact finished its full dwell before the quiet boundary and
        # the durable session is coherent for the next invocation.
        assert store.remaining_playback_count(app.initialize().id) == 1
        assert app.current_playback_pulse() is not None
        assert not app.ambient_playback_active()
    finally:
        store.close()


def test_ambient_quiet_at_start_plays_nothing_but_manual_play_bypasses_controller(tmp_path):
    from curiosity.runtime import TerminalPlayback

    store, app = _build_two_facts(tmp_path)
    try:
        # No harness event: posture is quiet, so ambient mode shows nothing.
        assert not app.ambient_playback_active()
        output, sleeps = [], []
        assert (
            TerminalPlayback(
                app, sleeps.append, output.append, should_continue=app.ambient_playback_active
            ).run()
            == 0
        )
        # Manual standalone play ignores the ambient controller entirely.
        output, sleeps = [], []
        assert TerminalPlayback(app, sleeps.append, output.append).run() == 2
        assert sleeps == [10, 10]
    finally:
        store.close()


def test_opencode_busy_idle_payload_drives_controller_states(tmp_path):
    from curiosity.harness import opencode_event

    with LocalStore(tmp_path / "ambient.db") as store:
        app = CuriosityApplication(store, now=_now)
        assert not app.ambient_playback_active()
        app.record_harness_event(opencode_event({"type": "session.status", "properties": {"status": "busy"}}))
        assert app.ambient_state() == {"state": "active_work", "posture": "active"}
        app.record_harness_event(opencode_event({"type": "session.status", "properties": {"status": "idle"}}))
        assert app.ambient_state() == {"state": "waiting_or_idle", "posture": "quiet"}
        # Repeated idle events do not duplicate work: the persisted row is stable.
        app.record_harness_event(opencode_event({"type": "session.idle"}))
        assert store.connection.execute("SELECT COUNT(*) FROM ambient_state").fetchone()[0] == 1
        assert store.connection.execute("SELECT state FROM ambient_state").fetchone()[0] == "waiting_or_idle"
        # A session error is terminal/quiet.
        app.record_harness_event(opencode_event({"type": "session.error"}))
        assert app.ambient_state()["posture"] == "quiet"