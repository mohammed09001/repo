from datetime import UTC, datetime

from curiosity.application import CuriosityApplication
from curiosity.ingest.pipeline import FetchResponse
from curiosity.store import LocalStore


class FixtureFetcher:
    def fetch(self, url: str, *, headers: dict[str, str], max_bytes: int) -> FetchResponse:
        return FetchResponse(
            200,
            b"A deterministic fixture demonstrates durable local orchestration.",
            "text/plain",
        )


def test_offline_refresh_is_idempotent_and_pulses_survive_reopen(tmp_path):
    path = tmp_path / "curiosity.db"

    def now() -> datetime:
        return datetime(2026, 9, 3, tzinfo=UTC)

    with LocalStore(path) as store:
        app = CuriosityApplication(store, fetcher=FixtureFetcher(), now=now)
        profile = app.initialize()
        source = app.add_source("https://example.test/fact")
        assert app.refresh_build() == 1
        assert app.refresh_build() == 0
        pulses = app.prepare_playback()
        assert [pulse.display_fact for pulse in pulses] == [
            "A deterministic fixture demonstrates durable local orchestration."
        ]
        inspected = app.inspect_pulse(pulses[0].id)
        assert inspected is not None and inspected["source"].id == source.id
        current = app.current_playback_pulse()
        assert current is not None and current.id == pulses[0].id
        assert app.acknowledge_playback_pulse(current)
        assert app.stats()["facts_shown"] == 1
        restarted = app.prepare_playback()
        assert restarted
        assert app.current_playback_pulse() is not None
        assert app.inspect_pulse(restarted[0].id)["verification"]["status"] == "verified"
        assert store.get_profile(profile.id) == profile
    with LocalStore(path) as reopened:
        assert len(reopened.list_pulses()) == 1
        assert CuriosityApplication(reopened, now=now).current_playback_pulse() is not None
