"""Real OpenAI-compatible endpoint end-to-end against a local mock server.

Proves the configured provider object built by the CLI path actually performs
bounded, ledgered, cached quality work and persists a verified English fact.
"""

import json
import threading
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from curiosity.application import CuriosityApplication
from curiosity.contracts.model import ModelGateway
from curiosity.ingest.pipeline import FetchResponse
from curiosity.providers import OpenAICompatibleEndpoint
from curiosity.store import LocalStore

CHINESE_FACT = "火星有2顆小衛星，它們叫做火衛一和火衛二。\n".encode()


class FixtureFetcher:
    def fetch(self, url: str, *, headers: dict[str, str], max_bytes: int) -> FetchResponse:
        etag = sha256(CHINESE_FACT).hexdigest()[:16]
        if headers.get("If-None-Match") == etag:
            return FetchResponse(304, b"", "text/plain")
        return FetchResponse(200, CHINESE_FACT, "text/plain", etag)


class _MockHandler(BaseHTTPRequestHandler):
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


def test_real_endpoint_quality_lane_end_to_end(tmp_path):
    server = ThreadingHTTPServer(("127.0.0.1", 0), _MockHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base_url = f"http://127.0.0.1:{server.server_port}/v1"
        gateway = ModelGateway(
            cheap=OpenAICompatibleEndpoint(
                api_key="sk-mock", model_id="mock-mini", base_url=base_url, timeout_seconds=5.0
            ),
            prices={"input": 1.0, "output": 2.0},
            max_calls=10,
        )
        with LocalStore(tmp_path / "curiosity.db") as store:
            app = CuriosityApplication(store, fetcher=FixtureFetcher(), gateway=gateway)
            app.initialize()
            app.add_source("https://example.test/mars")
            report = app.refresh_build()
            assert report.pulses_built == 1
            assert report.model_calls == 3  # translate + fidelity + verify
            assert report.cached_hits == 0
            assert not report.budget_exhausted
            pulses = store.list_eligible_pulses()
            assert pulses[0].display_fact == "Mars has 2 small moons."
            rows = store.model_usage_summary(report.run_id)
            totals = {row["task_type"]: row for row in rows}
            assert totals["translate"]["input_tokens"] == 120
            assert totals["translate"]["cached_tokens"] == 40
            cost = gateway.cost_for(
                int(totals["translate"]["input_tokens"]),
                int(totals["translate"]["output_tokens"]),
            )
            assert cost is not None and cost > 0
            # A second unchanged quality build reuses the local model cache.
            report2 = app.refresh_build()
            assert report2.skipped == 1  # incremental stage key skip
    finally:
        server.shutdown()
        server.server_close()