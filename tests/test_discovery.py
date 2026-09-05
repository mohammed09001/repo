"""Discovery control plane: CLI routing through the application boundary."""

import pytest

import curiosity.cli as cli_module
from curiosity.application import (
    ApplicationError,
    CuriosityApplication,
    DiscoveryCredentials,
)
from curiosity.contracts.models import SourceRecord
from curiosity.sources.http import DiscoveryError, HttpResponse
from curiosity.store import LocalStore

GITHUB_BODY = (
    b'{"items":[{"html_url":"https://github.com/acme/widget",'
    b'"full_name":"acme/widget","description":"demo"}]}'
)
PAPERS_BODY = (
    b'{"data":[{"paperId":"p1","title":"A paper without abstract",'
    b'"url":"https://example.org/p1","year":2026}]}'
)


class FixtureTransport:
    """A scripted transport used at the application discovery boundary."""

    def __init__(self, *responses: HttpResponse):
        self.responses = list(responses)
        self.calls: list[str] = []

    def __call__(self, url: str, headers: dict, timeout: float) -> HttpResponse:
        self.calls.append(url)
        if not self.responses:
            raise AssertionError("unexpected discovery request")
        return self.responses.pop(0)


def app_with(store: LocalStore, transport: FixtureTransport, **secrets: str | None) -> CuriosityApplication:
    return CuriosityApplication(
        store,
        discovery=DiscoveryCredentials(
            github_token=secrets.get("github_token", "token"),
            semantic_scholar_api_key=secrets.get("semantic_scholar_api_key", "key"),
            youtube_api_key=secrets.get("youtube_api_key", "key"),
        ),
        discovery_transport=transport,
    )


def install_cli_app(monkeypatch: pytest.MonkeyPatch, store_path, transport: FixtureTransport):
    def fake_app(args):
        store = LocalStore(store_path / "curiosity.db")
        return store, app_with(store, transport)

    monkeypatch.setattr(cli_module, "_app", fake_app)


def test_cli_discover_github_registers_selected_result(tmp_path, monkeypatch, capsys):
    transport = FixtureTransport(
        HttpResponse(200, {"X-RateLimit-Resource": "search", "ETag": "t"}, GITHUB_BODY)
    )
    install_cli_app(monkeypatch, tmp_path, transport)
    assert cli_module.main(["discover", "github", "widget", "--data-path", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "provider github" in out
    assert "requests 1" in out
    assert "results 1" in out
    assert "candidates 1" in out
    assert "candidate source_" in out

    with LocalStore(tmp_path / "curiosity.db") as store:
        assert store.list_sources() == []
        assert len(store.list_discovery_candidates()) == 1

    assert cli_module.main(["discover", "register", "--all", "--data-path", str(tmp_path)]) == 0
    assert "registered 1" in capsys.readouterr().out
    with LocalStore(tmp_path / "curiosity.db") as store:
        sources = store.list_sources()
        assert len(sources) == 1
        assert sources[0].canonical_locator == "https://github.com/acme/widget"


def test_cli_discover_papers_preserves_missing_abstract(tmp_path, monkeypatch, capsys):
    transport = FixtureTransport(HttpResponse(200, {}, PAPERS_BODY))
    install_cli_app(monkeypatch, tmp_path, transport)
    assert cli_module.main(["discover", "papers", "abstractless", "--data-path", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "provider papers" in out and "candidates 1" in out
    with LocalStore(tmp_path / "curiosity.db") as store:
        assert store.list_sources() == []
        row = store.list_discovery_candidates()[0]
        record = SourceRecord.model_validate_json(row["payload_json"])
        assert record.metadata["abstract_available"] == "false"
        assert record.metadata["paper_id"] == "p1"


def test_cli_discover_feed_reads_xml_without_auto_registration(tmp_path, monkeypatch, capsys):
    feed = b"<rss><channel><item><title>One</title><link>https://example.org/a</link></item></channel></rss>"
    transport = FixtureTransport(HttpResponse(200, {}, feed))
    install_cli_app(monkeypatch, tmp_path, transport)
    assert cli_module.main(
        ["discover", "feed", "https://example.org/feed.xml", "--data-path", str(tmp_path)]
    ) == 0
    out = capsys.readouterr().out
    assert "provider feed" in out and "candidates 1" in out
    with LocalStore(tmp_path / "curiosity.db") as store:
        assert store.list_sources() == []


def test_rate_limit_records_state_and_never_spins(tmp_path):
    transport = FixtureTransport(HttpResponse(429, {"Retry-After": "60"}, b"{}"))
    with LocalStore(tmp_path / "store.db") as store:
        app = app_with(store, transport)
        result = app.discover_github("widget")
        assert result.counters.rate_limited == 1 and result.counters.results == 0
        state = store.get_adapter_state("github")
        assert state["rate_limited"] is True and "retry_after" in state
        assert len(transport.calls) == 1
        with pytest.raises(DiscoveryError, match="rate-limited until"):
            app.discover_github("widget")
        assert len(transport.calls) == 1  # no spin; bounded exit on stored state


def test_cli_rate_limit_exits_boundedly(tmp_path, monkeypatch, capsys):
    transport = FixtureTransport(HttpResponse(429, {"Retry-After": "60"}, b"{}"))
    install_cli_app(monkeypatch, tmp_path, transport)
    assert cli_module.main(["discover", "github", "widget", "--data-path", str(tmp_path)]) == 2
    out, err = capsys.readouterr()
    assert "rate_limited 1" in out
    assert "rate limited" in err


def test_absent_key_and_unknown_provider_fail_truthfully(tmp_path, monkeypatch, capsys):
    with LocalStore(tmp_path / "store.db") as store:
        app = app_with(store, FixtureTransport(), youtube_api_key=None)
        result = app.discover_youtube("music")
        assert result.counters.failed == 1
        assert "no API key" in result.error
        with pytest.raises(ApplicationError, match="not found"):
            app.register_discovered(("source_000000000000000000000000",))

    transport = FixtureTransport(HttpResponse(200, {}, GITHUB_BODY))
    install_cli_app(monkeypatch, tmp_path, transport)
    with pytest.raises(SystemExit) as unknown:
        cli_module.main(["discover", "bogus", "query", "--data-path", str(tmp_path)])
    assert unknown.value.code == 2


def test_youtube_disabled_flag_is_truthful(tmp_path, monkeypatch, capsys):
    transport = FixtureTransport()
    install_cli_app(monkeypatch, tmp_path, transport)
    monkeypatch.delenv("CURIOSITY_FEATURE_YOUTUBE", raising=False)
    assert (
        cli_module.main(["discover", "youtube", "music", "--data-path", str(tmp_path)]) == 2
    )
    err = capsys.readouterr().err
    assert "disabled" in err and "youtube" in err.lower()


def test_discovery_dedupe_keeps_one_candidate_per_stable_identity(tmp_path):
    papers = HttpResponse(200, {}, PAPERS_BODY)
    feed_xml = (
        b"<rss><channel><item><title>Same paper</title>"
        b"<link>https://example.org/p1</link></item></channel></rss>"
    )
    transport = FixtureTransport(papers, HttpResponse(200, {}, feed_xml))
    with LocalStore(tmp_path / "store.db") as store:
        app = app_with(store, transport)
        first = app.discover_papers("same paper")
        assert first.counters.candidates == 1
        second = app.discover_feed("https://example.org/feed.xml")
        assert second.counters.candidates == 0 and second.counters.deduped == 1
        rows = store.list_discovery_candidates()
        assert len(rows) == 1
        assert rows[0]["provider"] == "papers"


def test_register_skips_existing_sources_and_reports_count(tmp_path):
    transport = FixtureTransport(
        HttpResponse(200, {}, GITHUB_BODY), HttpResponse(200, {}, GITHUB_BODY)
    )
    with LocalStore(tmp_path / "store.db") as store:
        app = app_with(store, transport)
        app.discover_github("widget")
        app.register_discovered(all=True)
        assert len(app.list_sources()) == 1
        # A second discovery is deduped against the registered source.
        second = app.discover_github("widget")
        assert second.counters.results == 1 and second.counters.deduped == 1


def test_discovery_never_leaks_into_normal_playback(tmp_path):
    transport = FixtureTransport(HttpResponse(200, {}, GITHUB_BODY))
    with LocalStore(tmp_path / "store.db") as store:
        app = app_with(store, transport)
        app.initialize()
        app.discover_github("widget")
        assert app.list_sources() == []
        assert app.prepare_playback() == ()