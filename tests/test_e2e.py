"""Authoritative offline product qualification over real internal engines."""

from datetime import UTC, datetime

from curiosity.application import CuriosityApplication
from curiosity.ingest.pipeline import FetchResponse
from curiosity.runtime import TerminalPlayback
from curiosity.store import LocalStore


class OfflineWebFixture:
    """A transport fixture: no network access is possible in this test."""

    def __init__(self) -> None:
        self.calls = 0

    def fetch(self, url: str, *, headers: dict[str, str], max_bytes: int) -> FetchResponse:
        self.calls += 1
        assert url == "https://example.test/knowledge"
        assert max_bytes == 2_000_000
        return FetchResponse(
            200,
            b"<html><nav>ignore</nav><article><p>"
            b"Version control stores snapshots of file states.</p></article>"
            b"<script>ignore()</script></html>",
            "text/html",
            etag="fixture-v1",
        )


def test_offline_personal_terminal_e2e(tmp_path):
    """source -> ingest -> extract -> verify -> compose -> rank -> queue -> play."""
    database = tmp_path / "data" / "curiosity.db"
    fixture = OfflineWebFixture()
    def now() -> datetime:
        return datetime(2026, 9, 4, tzinfo=UTC)

    with LocalStore(database) as store:
        app = CuriosityApplication(store, fetcher=fixture, now=now)
        app.initialize(display_name="Ada")
        app.configure_profile(weights={"general": 3.0})
        app.add_source("https://example.test/knowledge", title="Fixture title")
        assert app.refresh_build().pulses_built == 1
        assert fixture.calls == 1
        queued = app.prepare_playback(size=3)
        assert len(queued) == 1
        pulse_id = queued[0].id

    # Reopen proves the queue and provenance are durable, rather than fixtures
    # directly inserting a final pulse.
    with LocalStore(database) as reopened:
        app = CuriosityApplication(reopened, fetcher=fixture, now=now)
        output, sleeps = [], []
        assert TerminalPlayback(app, sleeps.append, output.append).run() == 1
        assert sleeps == [10]
        assert output == ["Version control stores snapshots of file states."]
        assert "source" not in output[0].lower()
        assert "topic" not in output[0].lower()
        inspected = app.inspect_pulse(pulse_id)
        assert inspected is not None
        assert inspected["source"].canonical_locator == "https://example.test/knowledge"
        assert inspected["verification"]["status"] == "verified"
        assert "Version control stores snapshots" in inspected["evidence"][0]["quote"]
        assert app.stats()["facts_shown"] == 1
