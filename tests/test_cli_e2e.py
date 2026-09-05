"""Authoritative clean-install CLI E2E: the exact commands a new user runs.

Runs the real ``curiosity`` command handlers against a local mock HTTP server
(fixture transports, no secrets, no external network). Proves the full product
path at the CLI boundary, including real discovery, a real provider mode,
PDF success on the qualified path, restart coherence, fact-only output, and
the injected 10-second cadence.
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from curiosity.cli import main
from curiosity.store import LocalStore

FIXTURES = Path(__file__).parent / "fixtures"

ARTICLE_A = (
    b"<html><head><title>A</title></head><body><nav>menu</nav><article><p>"
    b"Deterministic CLI fixture explains orbital mechanics simply.</p>"
    b"</article></body></html>"
)
ARTICLE_B = (
    b"<html><head><title>B</title></head><body><article><p>"
    b"Another CLI fixture describes tectonic plate motion clearly.</p>"
    b"</article></body></html>"
)
CHINESE_ARTICLE = (
    "<html><head><title>C</title></head><body><article><p>"
    "火星有2顆小衛星，它們叫做火衛一和火衛二。"
    "</p></article></body></html>"
).encode()


class FixtureHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        routes = {
            "/article-a": (ARTICLE_A, "text/html", "a-v1"),
            "/article-b": (ARTICLE_B, "text/html", "b-v1"),
            "/zh": (CHINESE_ARTICLE, "text/html", "zh-v1"),
            "/paper": ((FIXTURES / "sample.pdf").read_bytes(), "application/pdf", "pdf-v1"),
            "/item-1": (ARTICLE_A, "text/html", "i1-v1"),
            "/item-2": (ARTICLE_B, "text/html", "i2-v1"),
        }
        if self.path == "/feed":
            base = f"http://127.0.0.1:{self.server.server_port}"
            body = (
                "<?xml version=\"1.0\" encoding=\"UTF-8\"?><rss version=\"2.0\">"
                "<channel><title>Fixture Feed</title>"
                f"<item><title>Feed one</title><link>{base}/item-1</link>"
                "<description>Feed item one is a discoverable source.</description></item>"
                f"<item><title>Feed two</title><link>{base}/item-2</link>"
                "<description>Feed item two is another discoverable source.</description></item>"
                "</channel></rss>"
            ).encode()
            routes = {"/feed": (body, "application/rss+xml", "feed-v1")}
        route = routes.get(self.path)
        if route is None:
            self.send_response(404)
            self.end_headers()
            return
        body, mime, etag = route
        if self.headers.get("If-None-Match") == etag:
            self.send_response(304)
            self.send_header("ETag", etag)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("ETag", etag)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class ProviderHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        prompt = body["messages"][0]["content"]
        if prompt.startswith("Translate"):
            content = "Mars has 2 small moons."
        elif "faithful" in prompt:
            content = json.dumps({"faithful": True, "violations": []})
        else:
            content = json.dumps({"verdict": "supported", "confidence": 0.9, "reason": "ok"})
        payload = {
            "choices": [{"message": {"content": content}}],
            "usage": {
                "prompt_tokens": 120,
                "completion_tokens": 12,
                "prompt_tokens_details": {"cached_tokens": 40},
            },
        }
        data = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


@pytest.fixture(scope="module")
def server():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield httpd
    finally:
        httpd.shutdown()
        httpd.server_close()


@pytest.fixture(scope="module")
def provider_server():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), ProviderHandler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield httpd
    finally:
        httpd.shutdown()
        httpd.server_close()


def _bootstrap(server, tmp_path, *, articles=("article-a",), capsys=None):
    data = tmp_path / "data"
    assert main(["init", "--data-path", str(data), "--name", "Ada"]) == 0
    assert main(["profile", "set", "--data-path", str(data), "--interest", "general=3"]) == 0
    base = f"http://127.0.0.1:{server.server_port}"
    for article in articles:
        assert main(["source", "add", "--data-path", str(data), f"{base}/{article}"]) == 0
    assert main(["refresh", "--data-path", str(data)]) == 0
    if capsys is not None:
        capsys.readouterr()
    return data


def test_clean_install_cli_flow_end_to_end(server, tmp_path, capsys):
    data = tmp_path / "data"
    assert main(["init", "--data-path", str(data), "--name", "Ada"]) == 0
    assert "initialized" in capsys.readouterr().out
    assert (
        main(["profile", "set", "--data-path", str(data), "--interest", "general=3"]) == 0
    )
    capsys.readouterr()
    base = f"http://127.0.0.1:{server.server_port}"
    assert main(["source", "add", "--data-path", str(data), f"{base}/article-a"]) == 0
    capsys.readouterr()
    assert main(["refresh", "--data-path", str(data)]) == 0
    refresh_out = capsys.readouterr().out
    assert "built 1 verified pulses" in refresh_out
    assert "run_status succeeded" in refresh_out

    assert main(["play", "--once", "--data-path", str(data)]) == 0
    play_out = capsys.readouterr().out
    assert "orbital mechanics" in play_out
    assert "source" not in play_out.lower()
    assert "topic" not in play_out.lower()

    assert main(["stats", "--data-path", str(data)]) == 0
    stats_out = capsys.readouterr().out
    assert "facts_shown 1" in stats_out

    with LocalStore(data / "curiosity.db") as store:
        pulse_id = store.list_eligible_pulses()[0].id
    assert main(["inspect", "--data-path", str(data), pulse_id]) == 0
    inspect_out = capsys.readouterr().out
    assert "orbital mechanics" in inspect_out
    assert "generated_at" in inspect_out

    config = tmp_path / "config.toml"
    config.write_text(f"data_path = {json.dumps(str(data))}\n")
    assert main(["doctor", "--deep", "--config", str(config)]) == 0
    doctor_out = capsys.readouterr().out
    assert "database_integrity ok" in doctor_out
    assert "last_run_status succeeded" in doctor_out
    assert "last_run_pulses_built 1" in doctor_out
    assert "API_KEY" not in doctor_out
    assert "token" not in doctor_out


def test_play_cadence_uses_injected_sleeper_and_is_fact_only(server, tmp_path, monkeypatch, capsys):
    data = _bootstrap(server, tmp_path, capsys=capsys)
    sleeps = []
    monkeypatch.setattr("curiosity.cli.time.sleep", lambda seconds: sleeps.append(seconds))
    assert main(["play", "--data-path", str(data)]) == 0
    assert sleeps == [10]
    play_out = capsys.readouterr().out
    assert "orbital mechanics" in play_out
    assert "source" not in play_out.lower()
    assert "topic" not in play_out.lower()
    assert "https://" not in play_out


def test_cli_restart_resumes_durable_queue(server, tmp_path, monkeypatch, capsys):
    data = _bootstrap(server, tmp_path, articles=("article-a", "article-b"), capsys=capsys)
    sleeps = []
    monkeypatch.setattr("curiosity.cli.time.sleep", lambda seconds: sleeps.append(seconds))
    assert main(["play", "--once", "--data-path", str(data)]) == 0
    first = capsys.readouterr().out
    # Reopen the real path: the second play resumes the same durable queue and
    # shows the remaining fact, never the already-acknowledged one.
    assert main(["play", "--once", "--data-path", str(data)]) == 0
    second = capsys.readouterr().out
    assert first != second
    assert first.strip() and second.strip()


def test_discover_is_real_feed_and_register(server, tmp_path, capsys):
    data = tmp_path / "data"
    assert main(["init", "--data-path", str(data)]) == 0
    base = f"http://127.0.0.1:{server.server_port}"
    assert main(["discover", "feed", "--data-path", str(data), f"{base}/feed"]) == 0
    discover_out = capsys.readouterr().out
    assert "provider feed" in discover_out
    assert "candidates 2" in discover_out
    assert main(["discover", "list", "--data-path", str(data)]) == 0
    listed = capsys.readouterr().out
    assert f"{base}/item-1" in listed
    assert main(["discover", "register", "--all", "--data-path", str(data)]) == 0
    assert "registered 2" in capsys.readouterr().out
    assert main(["source", "list", "--data-path", str(data)]) == 0
    sources = capsys.readouterr().out
    assert f"{base}/item-1" in sources


def test_provider_mode_is_real_through_config(provider_server, server, tmp_path, capsys, monkeypatch):
    data = tmp_path / "data"
    base = f"http://127.0.0.1:{server.server_port}"
    config = tmp_path / "config.toml"
    config.write_text(
        f"data_path = {json.dumps(str(data))}\n"
        "provider_api_key = \"sk-mock\"\n"
        "provider_cheap_model = \"mock-mini\"\n"
        f"provider_base_url = \"http://127.0.0.1:{provider_server.server_port}/v1\"\n"
        "provider_prices = { input = 1.0, output = 2.0 }\n"
    )
    monkeypatch.setenv("CURIOSITY_CONFIG", str(config))
    assert main(["init", "--data-path", str(data)]) == 0
    assert main(["source", "add", "--data-path", str(data), f"{base}/zh"]) == 0
    assert main(["refresh", "--data-path", str(data)]) == 0
    refresh_out = capsys.readouterr().out
    assert "model_calls 3" in refresh_out
    assert "built 1 verified pulses" in refresh_out
    assert main(["play", "--once", "--data-path", str(data)]) == 0
    assert "Mars has 2 small moons." in capsys.readouterr().out


def test_pdf_cli_e2e_succeeds(server, tmp_path, capsys):
    pytest.importorskip(
        "docling", reason="requires the optional curiosity-engine[pdf] extra"
    )
    data = _bootstrap(server, tmp_path, articles=("paper",), capsys=capsys)
    assert main(["play", "--once", "--data-path", str(data)]) == 0
    play_out = capsys.readouterr().out
    assert "periodic table organizes chemical elements" in play_out
    assert "source" not in play_out.lower()


def test_pdf_cli_absent_extra_fails_cleanly(server, tmp_path, monkeypatch, capsys):
    import builtins

    real_import = builtins.__import__

    def no_docling(name, *args, **kwargs):
        if name == "docling" or name.startswith("docling."):
            raise ImportError("no docling")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", no_docling)
    data = tmp_path / "data"
    base = f"http://127.0.0.1:{server.server_port}"
    assert main(["init", "--data-path", str(data)]) == 0
    assert main(["source", "add", "--data-path", str(data), f"{base}/paper"]) == 0
    assert main(["refresh", "--data-path", str(data)]) == 2
    assert "Docling requires the optional" in capsys.readouterr().err