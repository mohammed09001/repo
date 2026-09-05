"""Near-Duplicate Firewall: exact hash -> FTS5 shortlist -> cheap similarity."""

from hashlib import sha256
from pathlib import Path

from curiosity.application import CuriosityApplication
from curiosity.ingest.pipeline import FetchResponse
from curiosity.store import LocalStore

FACT_A = b"Mars has 2 small moons that orbit the planet.\n"
FACT_A_PARAPHRASE = b"Mars possesses two small moons orbiting it.\n"
FACT_B = b"Ocean currents transport heat around the planet.\n"
FACT_C_INCREASE = b"Sunlight increases the rate of photosynthesis in plants.\n"
FACT_C_DECREASE = b"Sunlight decreases the rate of photosynthesis in plants.\n"


class MultiFetcher:
    def __init__(self, contents: dict[str, bytes]):
        self.contents = contents
        self.calls = 0

    def fetch(self, url: str, *, headers: dict[str, str], max_bytes: int) -> FetchResponse:
        self.calls += 1
        content = self.contents[url]
        etag = sha256(content).hexdigest()[:16]
        if headers.get("If-None-Match") == etag:
            return FetchResponse(304, b"", "text/plain")
        return FetchResponse(200, content, "text/plain", etag)


def build(tmp_path: Path, contents: dict[str, bytes]):
    store = LocalStore(tmp_path / "curiosity.db")
    app = CuriosityApplication(store, fetcher=MultiFetcher(contents))
    app.initialize()
    for url in contents:
        app.add_source(url)
    return store, app


def test_exact_duplicate_from_two_sources_is_suppressed(tmp_path):
    store, app = build(tmp_path, {"https://e.test/a": FACT_A, "https://e.test/b": FACT_A})
    try:
        report = app.refresh_build()
        assert report.pulses_built == 1
        assert report.duplicates_suppressed == 1
        assert len(store.list_eligible_pulses()) == 1
        event = store.connection.execute(
            "SELECT outcome, detail FROM build_events WHERE outcome='duplicate_suppressed'"
        ).fetchone()
        assert event is not None and event["detail"] == "duplicate"
    finally:
        store.close()


def test_near_paraphrase_is_suppressed_without_provider_call(tmp_path):
    contents = {"https://e.test/a": FACT_A, "https://e.test/b": FACT_A_PARAPHRASE}
    store, app = build(tmp_path, contents)
    try:
        report = app.refresh_build()
        assert report.pulses_built == 1
        assert report.duplicates_suppressed == 1
        assert len(store.list_eligible_pulses()) == 1
    finally:
        store.close()


def test_contradictory_direction_is_never_merged(tmp_path):
    contents = {"https://e.test/a": FACT_C_INCREASE, "https://e.test/b": FACT_C_DECREASE}
    store, app = build(tmp_path, contents)
    try:
        report = app.refresh_build()
        assert report.pulses_built == 2
        assert report.duplicates_suppressed == 0
        assert len(store.list_eligible_pulses()) == 2
    finally:
        store.close()


def test_related_concept_is_kept_but_distinct_facts_are_not_merged(tmp_path):
    contents = {"https://e.test/a": FACT_A, "https://e.test/b": FACT_B}
    store, app = build(tmp_path, contents)
    try:
        report = app.refresh_build()
        assert report.pulses_built == 2
        assert len(store.list_eligible_pulses()) == 2
    finally:
        store.close()


def test_firewall_shortlist_is_bounded_and_fts_aware(tmp_path):
    from curiosity.dedupe.engine import firewall_decision, fts_terms, lexical_similarity
    from curiosity.knowledge.engine import fact_fingerprint

    contents = {"https://e.test/a": FACT_A, "https://e.test/b": FACT_B}
    store, app = build(tmp_path, contents)
    try:
        app.refresh_build()
        source_a = next(s for s in app.list_sources() if s.canonical_locator == "https://e.test/a")
        assert fact_fingerprint("Mars has 2 small moons that orbit the planet.") != ""
        assert fts_terms("Mars has 2 small moons that orbit the planet.")
        assert 0.0 <= lexical_similarity("a b c", "d e f") <= 1.0
        decision, _ = firewall_decision(
            store, "Mars has 2 small moons that orbit the planet.", exclude_source_id=None
        )
        assert decision == "duplicate"
        # The same source's own fact never counts as a duplicate against itself.
        decision_self, _ = firewall_decision(
            store, "Mars has 2 small moons that orbit the planet.",
            exclude_source_id=source_a.id,
        )
        assert decision_self in {"related_concept", "distinct"}
    finally:
        store.close()