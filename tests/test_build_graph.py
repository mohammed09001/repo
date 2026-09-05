"""Incremental build graph: stage fingerprints skip and invalidate precisely."""

from hashlib import sha256
from pathlib import Path

import curiosity.contracts.stages as stages_module
import curiosity.ingest.pipeline as pipeline_module
from curiosity.application import CuriosityApplication
from curiosity.ingest.pipeline import FetchResponse
from curiosity.store import LocalStore

URL_A = "https://example.test/a"
URL_B = "https://example.test/b"
HTML_A = b"<html><body><article><p>Alpha determines durable local facts.</p></article></body></html>"
HTML_A_CHANGED = (
    b"<html><body><article><p>Alpha now bounds newer civic experiments.</p></article></body></html>"
)
HTML_B = b"<html><body><article><p>Beta governs useful reproducible knowledge.</p></article></body></html>"


class ChangeableFetcher:
    """Conditional-GET fixture whose content can change per URL."""

    def __init__(self) -> None:
        self.content: dict[str, bytes] = {}
        self.requests: dict[str, int] = {}

    def set(self, url: str, html: bytes) -> None:
        self.content[url] = html

    def fetch(self, url: str, *, headers: dict[str, str], max_bytes: int) -> FetchResponse:
        self.requests[url] = self.requests.get(url, 0) + 1
        html = self.content[url]
        etag = sha256(html).hexdigest()[:16]
        if headers.get("If-None-Match") == etag:
            return FetchResponse(304, b"", "text/html")
        return FetchResponse(200, html, "text/html", etag, "now")


def seeded(tmp_path: Path) -> tuple[LocalStore, CuriosityApplication, ChangeableFetcher]:
    fetcher = ChangeableFetcher()
    fetcher.set(URL_A, HTML_A)
    fetcher.set(URL_B, HTML_B)
    store = LocalStore(tmp_path / "curiosity.db")
    app = CuriosityApplication(store, fetcher=fetcher)
    app.initialize()
    return store, app, fetcher


def test_unchanged_refresh_skips_all_downstream_work(tmp_path):
    store, app, _ = seeded(tmp_path)
    try:
        app.add_source(URL_A)
        first = app.refresh_build()
        assert first.pulses_built == 1 and first.skipped == 0
        second = app.refresh_build()
        assert second.pulses_built == 0
        assert second.skipped == 1
        assert second.fetched == 0 and second.candidates == 0
        assert len(store.list_eligible_pulses()) == 1
    finally:
        store.close()


def test_content_change_invalidates_only_that_branch(tmp_path):
    store, app, fetcher = seeded(tmp_path)
    try:
        app.add_source(URL_A)
        app.add_source(URL_B)
        app.refresh_build()
        first_pulses = store.list_eligible_pulses()
        assert len(first_pulses) == 2
        source_a = next(source for source in app.list_sources() if source.canonical_locator == URL_A)

        fetcher.set(URL_A, HTML_A_CHANGED)
        report = app.refresh_build()
        assert report.skipped == 1  # B untouched
        assert report.pulses_built == 1  # A rebuilt

        second_pulses = store.list_eligible_pulses()
        old_a = [pulse for pulse in first_pulses if pulse.source_id == source_a.id][0]
        assert len(second_pulses) == 2
        assert all(pulse.id != old_a.id for pulse in second_pulses)
        # Historical pulse stays inspectable while no longer eligible.
        assert store.get_pulse(old_a.id) is not None
    finally:
        store.close()


def test_parser_version_change_reparses_and_supersedes_old_branch(tmp_path, monkeypatch):
    store, app, _ = seeded(tmp_path)
    try:
        app.add_source(URL_A)
        app.refresh_build()
        old_pulse = store.list_eligible_pulses()[0]
        old_document = store.get_pulse(old_pulse.id).document_id

        monkeypatch.setattr(pipeline_module, "HTML_PRECISION_VERSION", "trafilatura-3.0-test")
        report = app.refresh_build()
        assert report.reparsed == 1 and report.skipped == 0
        new_pulses = store.list_eligible_pulses()
        assert len(new_pulses) == 1
        assert new_pulses[0].id != old_pulse.id
        assert new_pulses[0].document_id != old_document
        assert store.get_pulse(old_pulse.id) is not None
        assert store.get_stage_key(new_pulses[0].source_id)["document_id"] != old_document
    finally:
        store.close()


def test_reopen_resumes_without_duplicate_rows(tmp_path):
    db = tmp_path / "curiosity.db"
    fetcher = ChangeableFetcher()
    fetcher.set(URL_A, HTML_A)
    with LocalStore(db) as store:
        app = CuriosityApplication(store, fetcher=fetcher)
        app.initialize()
        app.add_source(URL_A)
        assert app.refresh_build().pulses_built == 1
    with LocalStore(db) as store:
        app = CuriosityApplication(store, fetcher=fetcher)
        report = app.refresh_build()
        assert report.skipped == 1 and report.pulses_built == 0
        assert len(store.list_eligible_pulses()) == 1
        assert store.connection.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == 1
        assert store.connection.execute("SELECT COUNT(*) FROM stage_keys").fetchone()[0] == 1


def test_stage_contract_change_rebuilds_but_is_idempotent_after(tmp_path, monkeypatch):
    store, app, _ = seeded(tmp_path)
    try:
        app.add_source(URL_A)
        app.refresh_build()
        before = {pulse.id for pulse in store.list_eligible_pulses()}
        monkeypatch.setattr(stages_module, "EXTRACTOR_VERSION", "extract-no-llm-v2")
        report = app.refresh_build()
        assert report.pulses_built == 1 and report.skipped == 0
        after = {pulse.id for pulse in store.list_eligible_pulses()}
        assert before.isdisjoint(after)
        # The new contract is now the stored baseline; a third refresh skips.
        again = app.refresh_build()
        assert again.skipped == 1 and again.pulses_built == 0
    finally:
        store.close()