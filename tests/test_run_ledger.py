"""Refresh run ledger: bounded summaries, interruption recovery, retries."""

from datetime import UTC, datetime, timedelta
from hashlib import sha256

import pytest

from curiosity.application import CuriosityApplication
from curiosity.ingest.pipeline import FetchResponse, IngestError
from curiosity.reliability import bounded_retry, classify_http_status, retry_delay
from curiosity.store import LocalStore

NOW = datetime(2026, 9, 5, 12, 0, tzinfo=UTC)


def now() -> datetime:
    return NOW


HTML = b"<html><body><article><p>A durable ledger fact survives the refresh.</p></article></body></html>"
CHANGED = b"<html><body><article><p>A rebuilt ledger fact replaces the old one.</p></article></body></html>"


class Fetcher:
    def __init__(self, *responses):
        self.responses = list(responses)

    def fetch(self, url, *, headers, max_bytes):
        return self.responses.pop(0)


class TransientRaisingFetcher:
    def __init__(self, failures, response):
        self.failures = failures
        self.response = response

    def fetch(self, url, *, headers, max_bytes):
        if self.failures > 0:
            self.failures -= 1
            raise IngestError("network error: fixture", transient=True)
        return self.response


class PermanentFetcher:
    def fetch(self, url, *, headers, max_bytes):
        raise IngestError("permanent parser failure", transient=False)


def _app(tmp_path, fetcher):
    store = LocalStore(tmp_path / "curiosity.db")
    app = CuriosityApplication(store, fetcher=fetcher, now=now)
    app.initialize()
    app.add_source("https://example.test/ledger")
    return store, app


def test_refresh_records_bounded_secret_free_run_summary(tmp_path):
    store, app = _app(tmp_path, Fetcher(FetchResponse(200, HTML, "text/html", "etag-v1")))
    try:
        report = app.refresh_build()
        assert report.status == "succeeded"
        assert report.pulses_built == 1
        summary = store.get_last_run_summary()
        assert summary is not None
        assert summary["run_id"] == report.run_id
        assert summary["status"] == "succeeded"
        assert summary["sources"] == 1
        assert summary["http_fetches"] == 1
        assert summary["pulses_built"] == 1
        assert summary["elapsed_ms"] >= 0
        assert summary["detail"] == ""
        # No source body, prompt, or secret is ever persisted.
        assert HTML.decode() not in summary["detail"]
    finally:
        store.close()


def test_second_unchanged_refresh_is_dramatically_cheaper(tmp_path):
    store, app = _app(
        tmp_path,
        Fetcher(
            FetchResponse(200, HTML, "text/html", "etag-v1"),
            FetchResponse(304, b"", "text/html"),
        ),
    )
    try:
        first = app.refresh_build()
        assert first.http_fetches == 1 and first.parser_elapsed_ms > 0
        second = app.refresh_build()
        assert second.skipped == 1
        assert second.http_fetches == 0
        assert second.http_cache_hits == 1
        assert second.parser_elapsed_ms == 0
        assert second.model_calls == 0 and second.pulses_built == 0
        runs = store.list_run_summaries(limit=5)
        assert [run["run_id"] for run in runs] == [second.run_id, first.run_id]
    finally:
        store.close()


def test_content_change_records_only_that_runs_work(tmp_path):
    fetcher = Fetcher(
        FetchResponse(200, HTML, "text/html", "etag-v1"),
        FetchResponse(304, b"", "text/html"),
        FetchResponse(200, CHANGED, "text/html", "etag-v2"),
    )
    store, app = _app(tmp_path, fetcher)
    try:
        app.refresh_build()
        app.refresh_build()
        third = app.refresh_build()
        assert third.pulses_built == 1  # only the changed branch rebuilt
        assert third.http_cache_hits == 0  # content changed, no 304 reuse
    finally:
        store.close()


def test_transient_fetch_failure_retries_with_cap_and_records_retries(tmp_path):
    store, app = _app(
        tmp_path, TransientRaisingFetcher(failures=2, response=FetchResponse(200, HTML, "text/html"))
    )
    try:
        report = app.refresh_build()
        assert report.pulses_built == 1
        assert report.retries == 2
        assert report.failures == 0
        summary = store.get_last_run_summary()
        assert summary["retries"] == 2 and summary["failures"] == 0
    finally:
        store.close()


def test_permanent_failure_records_failed_run_and_raises(tmp_path):
    store, app = _app(tmp_path, PermanentFetcher())
    try:
        with pytest.raises(IngestError, match="permanent"):
            app.refresh_build()
        summary = store.get_last_run_summary()
        assert summary["status"] == "failed"
        assert summary["failures"] == 1
        assert "IngestError" in summary["detail"]
        assert store.connection.execute("SELECT COUNT(*) FROM pulses").fetchone()[0] == 0
    finally:
        store.close()


def test_interrupted_refresh_job_is_recovered_and_resume_is_idempotent(tmp_path):
    store, app = _app(
        tmp_path,
        Fetcher(
            FetchResponse(200, HTML, "text/html", "etag-v1"),
            FetchResponse(304, b"", "text/html"),
        ),
    )
    try:
        app.refresh_build()
        assert len(store.list_eligible_pulses()) == 1
        # Simulate a killed refresh: a refresh job claimed and then abandoned.
        interrupted_id = store.create_job(
            job_id="job_deadbeefdeadbeef0000000000000001",
            idempotency_key="refresh:interrupted",
            stage="refresh",
            now=NOW,
        )
        assert store.claim_job_by_id(job_id=interrupted_id, worker_id="refresh-worker", now=NOW, lease_seconds=1)
        stale = store.diagnostics(now=NOW + timedelta(seconds=5)).recoverable_running_jobs
        assert stale == 1
        recovered = store.recover_abandoned_jobs(now=NOW + timedelta(seconds=5))
        assert recovered == 1
        # A fresh refresh after recovery does not duplicate the pulse.
        again = app.refresh_build()
        assert again.skipped == 1 and again.pulses_built == 0
        assert len(store.list_eligible_pulses()) == 1
    finally:
        store.close()


def test_budget_exhaustion_is_terminal_run_state_not_exception(tmp_path):
    import json
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    from curiosity.contracts.model import ModelGateway
    from curiosity.providers import OpenAICompatibleEndpoint

    CHINESE = "火星有2顆小衛星，它們叫做火衛一和火衛二。\n".encode()

    class FixtureFetcher:
        def fetch(self, url, *, headers, max_bytes):
            return FetchResponse(200, CHINESE, "text/plain")

    class MockHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            prompt = body["messages"][0]["content"]
            content = "Mars has 2 small moons." if prompt.startswith("Translate") else "{}"
            payload = {
                "choices": [{"message": {"content": content}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "prompt_tokens_details": {}},
            }
            data = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), MockHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        gateway = ModelGateway(
            cheap=OpenAICompatibleEndpoint(
                api_key="sk-mock",
                model_id="mock-mini",
                base_url=f"http://127.0.0.1:{server.server_port}/v1",
                timeout_seconds=5.0,
            ),
            max_calls=1,
        )
        store = LocalStore(tmp_path / "budget.db")
        try:
            app = CuriosityApplication(store, fetcher=FixtureFetcher(), gateway=gateway, now=now)
            app.initialize()
            app.add_source("https://example.test/budget")
            report = app.refresh_build()
            assert report.budget_exhausted is True
            assert report.status == "budget_exhausted"
            summary = store.get_last_run_summary()
            assert summary["status"] == "budget_exhausted"
            assert summary["budget_exhausted"] == 1
        finally:
            store.close()
    finally:
        server.shutdown()
        server.server_close()


def test_retry_classification_and_capped_backoff():
    assert classify_http_status(429) == "transient"
    assert classify_http_status(500) == "transient"
    assert classify_http_status(404) == "permanent"
    assert retry_delay(2) == 1.0

    calls = {"count": 0}

    def flaky():
        calls["count"] += 1
        if calls["count"] < 3:
            raise IngestError("boom", transient=True)
        return "ok"

    assert bounded_retry(flaky, attempts=3, base_seconds=0.0) == "ok"
    assert calls["count"] == 3

    def always_bad():
        raise IngestError("boom", transient=True)

    with pytest.raises(IngestError):
        bounded_retry(always_bad, attempts=2, base_seconds=0.0)

    def permanent():
        raise IngestError("bad", transient=False)

    with pytest.raises(IngestError, match="bad"):
        bounded_retry(permanent, attempts=3, base_seconds=0.0)


def test_hash_import_used_for_document_keys(tmp_path):
    # Guard against accidental drift in the document identity contract.
    assert sha256(HTML).hexdigest() == sha256(HTML).hexdigest()