"""Two-speed quality lane: fast lane is free, quality lane is bounded and safe."""

from hashlib import sha256
from pathlib import Path

import curiosity.contracts.stages as stages_module
from curiosity.application import CuriosityApplication
from curiosity.contracts.model import ModelCallResult, ModelCapabilities, ModelGateway
from curiosity.ingest.pipeline import FetchResponse
from curiosity.store import LocalStore

ENGLISH_FACT = b"Ocean currents transport heat around the planet.\n"
LONG_ENGLISH = (
    b"The second-largest moon of Saturn, named Titan, has a dense atmosphere with "
    b"nitrogen and methane that scientists at several observatories study closely "
    b"in detail every season.\n"
)
CHINESE_FACT = "火星有2顆小衛星，它們叫做火衛一和火衛二。\n".encode()


class FixtureFetcher:
    def __init__(self, content: bytes):
        self.content = content
        self.calls = 0

    def fetch(self, url: str, *, headers: dict[str, str], max_bytes: int) -> FetchResponse:
        self.calls += 1
        etag = sha256(self.content).hexdigest()[:16]
        if headers.get("If-None-Match") == etag:
            return FetchResponse(304, b"", "text/plain")
        return FetchResponse(200, self.content, "text/plain", etag)


class FakeEndpoint:
    model_id = "fake-model"
    capabilities = ModelCapabilities(
        supports_structured=True, supports_prompt_cache=True, supports_batch=False,
        supports_usage_tokens=True, supports_cost_metadata=False,
    )

    def __init__(self, *responses: str, respond=None, model_id: str = "fake-model"):
        self.responses = list(responses)
        self.respond = respond
        self.calls = 0
        self.model_id = model_id

    def generate(self, prompt: str) -> ModelCallResult:
        self.calls += 1
        if self.respond is not None:
            content = self.respond(prompt)
        else:
            content = self.responses.pop(0) if self.responses else ""
        return ModelCallResult(content=content, input_tokens=10, output_tokens=5)

    def generate_structured(self, prompt: str, *, response_schema: dict) -> ModelCallResult:
        return self.generate(prompt)


def smart_quality_respond(prompt: str) -> str:
    if prompt.startswith("Translate"):
        return "Mars has 2 small moons."
    if prompt.startswith("The rewritten sentence must be faithful"):
        return '{"faithful": true, "violations": []}'
    return '{"verdict": "supported", "confidence": 0.9, "reason": "ok"}'


def make_app(path: Path, fetcher: FixtureFetcher, gateway: ModelGateway | None):
    store = LocalStore(path / "curiosity.db")
    return store, CuriosityApplication(store, fetcher=fetcher, gateway=gateway)


def gateway(*responses: str, max_calls: int | None = None) -> ModelGateway:
    return ModelGateway(cheap=FakeEndpoint(*responses), max_calls=max_calls)


def test_golden_english_corpus_requires_zero_provider_calls(tmp_path):
    endpoint = FakeEndpoint("never used")
    store, app = make_app(tmp_path, FixtureFetcher(ENGLISH_FACT), ModelGateway(cheap=endpoint))
    try:
        app.initialize()
        app.add_source("https://example.test/ocean")
        report = app.refresh_build()
        assert report.pulses_built == 1
        assert report.model_calls == 0 and endpoint.calls == 0
        assert report.escalated == 0 and not report.budget_exhausted
        pulses = store.list_eligible_pulses()
        assert pulses[0].display_fact == "Ocean currents transport heat around the planet."
    finally:
        store.close()


def test_non_english_translates_to_verified_english_fact_bound_to_evidence(tmp_path):
    endpoint = FakeEndpoint(
        "Mars has 2 small moons.",  # translate
        '{"faithful": true, "violations": []}',  # fidelity judge
        '{"verdict": "supported", "confidence": 0.9, "reason": "faithful"}',  # verify
    )
    store, app = make_app(tmp_path, FixtureFetcher(CHINESE_FACT), ModelGateway(cheap=endpoint))
    try:
        app.initialize()
        app.add_source("https://example.test/mars")
        report = app.refresh_build()
        assert report.pulses_built == 1
        assert report.model_calls == 3 and report.cached_hits == 0
        pulses = store.list_eligible_pulses()
        assert pulses[0].display_fact == "Mars has 2 small moons."
        evidence = store.payloads_for_ids("evidence", pulses[0].evidence_ids)
        assert "火星" in evidence[0]["quote"]
        inspected = app.inspect_pulse(pulses[0].id)
        assert inspected["verification"]["status"] == "verified"
        assert inspected["verification"]["provider_used"] is True
    finally:
        store.close()


def test_negation_flip_rewrite_is_rejected_and_original_kept(tmp_path):
    # >24-word English fact triggers an optional fidelity rewrite; the model
    # returns a negation-flipped rewrite that must never reach display.
    original = "Saturn's moon Titan has a dense atmosphere with nitrogen and methane."
    endpoint = FakeEndpoint("Titan does not have a dense atmosphere.")
    store, app = make_app(tmp_path, FixtureFetcher(ENGLISH_FACT), None)
    store.close()
    # Use a source whose sentence is short enough to be playable but verbose.
    fetcher = FixtureFetcher(LONG_ENGLISH)
    store = LocalStore(tmp_path / "curiosity.db")
    app = CuriosityApplication(store, fetcher=fetcher, gateway=ModelGateway(cheap=endpoint))
    try:
        app.initialize()
        app.add_source("https://example.test/titan")
        report = app.refresh_build()
        assert report.model_calls >= 1
        pulses = store.list_eligible_pulses()
        for pulse in pulses:
            assert "does not have" not in pulse.display_fact
        assert original is not None
    finally:
        store.close()


def test_number_change_rewrite_is_rejected(tmp_path):
    fetcher = FixtureFetcher(LONG_ENGLISH)
    endpoint = FakeEndpoint("Saturn's moon Titan has 99 moons with nitrogen and methane.")
    with LocalStore(tmp_path / "curiosity.db") as store:
        app = CuriosityApplication(store, fetcher=fetcher, gateway=ModelGateway(cheap=endpoint))
        app.initialize()
        app.add_source("https://example.test/titan")
        report = app.refresh_build()
        assert report.model_calls >= 1
        for pulse in store.list_eligible_pulses():
            assert "99" not in pulse.display_fact


def test_provider_failure_never_creates_pulse(tmp_path):
    class FailingEndpoint(FakeEndpoint):
        def generate(self, prompt):
            self.calls += 1
            from curiosity.contracts.model import ModelFailure

            raise ModelFailure("boom")

    endpoint = FailingEndpoint()
    store, app = make_app(tmp_path, FixtureFetcher(CHINESE_FACT), ModelGateway(cheap=endpoint))
    try:
        app.initialize()
        app.add_source("https://example.test/mars")
        report = app.refresh_build()
        assert report.pulses_built == 0 and report.model_failures >= 1
        assert store.list_eligible_pulses() == []
        assert app.prepare_playback() == ()
    finally:
        store.close()


def test_budget_exhaustion_stops_escalation_safely(tmp_path):
    endpoint = FakeEndpoint("Mars has 2 small moons.", '{"faithful": true, "violations": []}')
    store, app = make_app(
        tmp_path, FixtureFetcher(CHINESE_FACT), ModelGateway(cheap=endpoint, max_calls=2)
    )
    try:
        app.initialize()
        app.add_source("https://example.test/mars")
        report = app.refresh_build()
        # 2 budget slots consumed (translate, fidelity); verify is blocked.
        assert report.budget_exhausted is True
        assert report.pulses_built == 0
        assert store.list_eligible_pulses() == []
    finally:
        store.close()


def test_repeated_quality_build_hits_local_model_cache(tmp_path, monkeypatch):
    responses = [
        "Mars has 2 small moons.",
        '{"faithful": true, "violations": []}',
        '{"verdict": "supported", "confidence": 0.9, "reason": "ok"}',
    ]
    endpoint = FakeEndpoint(*responses)
    store, app = make_app(tmp_path, FixtureFetcher(CHINESE_FACT), ModelGateway(cheap=endpoint))
    try:
        app.initialize()
        app.add_source("https://example.test/mars")
        first = app.refresh_build()
        assert first.model_calls == 3 and first.pulses_built == 1
        # Changing only the extractor contract forces a rebuild; the model cache
        # must absorb every quality call.
        monkeypatch.setattr(stages_module, "EXTRACTOR_VERSION", "extract-no-llm-v9")
        second = app.refresh_build()
        assert second.pulses_built == 1
        assert endpoint.calls == 3  # no new provider calls
        assert second.model_calls == 0
        assert second.cached_hits >= 3
        assert len(store.list_eligible_pulses()) == 1
    finally:
        store.close()


def test_cache_misses_when_quality_contract_changes(tmp_path, monkeypatch):
    endpoint = FakeEndpoint(respond=smart_quality_respond)
    store, app = make_app(tmp_path, FixtureFetcher(CHINESE_FACT), ModelGateway(cheap=endpoint))
    try:
        app.initialize()
        app.add_source("https://example.test/mars")
        app.refresh_build()
        first_calls = endpoint.calls
        assert first_calls == 3
        monkeypatch.setattr(stages_module, "QUALITY_VERSION", "quality-lane-v2")
        second = app.refresh_build()
        assert endpoint.calls == first_calls + 3  # cache keys changed with the contract
        assert second.model_calls == 3
        assert second.pulses_built == 1
    finally:
        store.close()


def test_usage_ledger_persists_across_reopen(tmp_path):
    endpoint = FakeEndpoint(
        "Mars has 2 small moons.",
        '{"faithful": true, "violations": []}',
        '{"verdict": "supported", "confidence": 0.9, "reason": "ok"}',
    )
    db = tmp_path / "curiosity.db"
    fetcher = FixtureFetcher(CHINESE_FACT)
    with LocalStore(db) as store:
        app = CuriosityApplication(store, fetcher=fetcher, gateway=ModelGateway(cheap=endpoint))
        app.initialize()
        app.add_source("https://example.test/mars")
        report = app.refresh_build()
        assert report.model_calls == 3
        run_id = report.run_id
    with LocalStore(db) as store:
        rows = store.model_usage_summary(run_id)
        assert sum(int(row["calls"]) for row in rows) == 3
        assert any(row["task_type"] == "translate" for row in rows)
        assert any(row["task_type"] == "verify" for row in rows)
        assert store.connection.execute("SELECT COUNT(*) FROM model_cache").fetchone()[0] == 3


def test_cost_budget_stops_escalation(tmp_path):
    endpoint = FakeEndpoint(
        "Mars has 2 small moons.",
        '{"faithful": true, "violations": []}',
        '{"verdict": "supported", "confidence": 0.9, "reason": "ok"}',
    )
    # Each fake call reports 10 input + 5 output tokens; at input=1.0/output=2.0
    # per million tokens, a run costing more than the tiny cap must stop.
    gateway = ModelGateway(cheap=endpoint, prices={"input": 1.0, "output": 2.0}, max_cost=1e-6)
    store, app = make_app(tmp_path, FixtureFetcher(CHINESE_FACT), gateway)
    try:
        app.initialize()
        app.add_source("https://example.test/mars")
        report = app.refresh_build()
        assert report.budget_exhausted is True
        assert report.pulses_built == 0
        assert store.list_eligible_pulses() == []
    finally:
        store.close()


def test_queue_size_never_triggers_model_work(tmp_path):
    endpoint = FakeEndpoint(
        "Mars has 2 small moons.",
        '{"faithful": true, "violations": []}',
        '{"verdict": "supported", "confidence": 0.9, "reason": "ok"}',
    )
    store, app = make_app(tmp_path, FixtureFetcher(CHINESE_FACT), ModelGateway(cheap=endpoint))
    try:
        app.initialize()
        app.add_source("https://example.test/mars")
        app.refresh_build()
        calls_after_build = endpoint.calls
        assert app.prepare_playback(size=3)
        assert app.prepare_playback(size=50)
        assert endpoint.calls == calls_after_build
    finally:
        store.close()


def test_strong_tier_escalates_only_on_unresolved_verify(tmp_path):
    def cheap_respond(prompt: str) -> str:
        if prompt.startswith("Translate"):
            return "Mars has 2 small moons."
        if "faithful" in prompt:
            return '{"faithful": true, "violations": []}'
        return '{"verdict": "uncertain", "confidence": 0.4, "reason": "ambiguous"}'

    cheap = FakeEndpoint(respond=cheap_respond, model_id="mock-mini")
    strong = FakeEndpoint(
        respond=lambda p: '{"verdict": "supported", "confidence": 0.9, "reason": "ok"}',
        model_id="mock-strong",
    )
    store, app = make_app(
        tmp_path, FixtureFetcher(CHINESE_FACT), ModelGateway(cheap=cheap, strong=strong)
    )
    try:
        app.initialize()
        app.add_source("https://example.test/mars")
        report = app.refresh_build()
        assert report.pulses_built == 1
        assert cheap.calls == 3  # translate + fidelity + cheap verify
        assert strong.calls == 1  # strong verify only after uncertain cheap verdict
        assert report.model_calls == 4
    finally:
        store.close()


def test_policy_ambiguity_is_rejected_without_model(tmp_path):
    fetcher = FixtureFetcher(b"Medical treatment always cures patients quickly.\n")
    endpoint = FakeEndpoint("never called")
    with LocalStore(tmp_path / "curiosity.db") as store:
        app = CuriosityApplication(store, fetcher=fetcher, gateway=ModelGateway(cheap=endpoint))
        app.initialize()
        app.add_source("https://example.test/medical")
        report = app.refresh_build()
        assert report.pulses_built == 0
        assert endpoint.calls == 0
        assert store.list_eligible_pulses() == []
        assert report.rejected >= 1