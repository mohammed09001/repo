"""Feed intelligence: real signals, exposure cooldown, continuous refill."""

from datetime import UTC, datetime

from curiosity.application import CuriosityApplication
from curiosity.contracts.models import (
    CardType,
    Chunk,
    CuriosityCard,
    CuriosityPulse,
    Evidence,
    EvidenceSupport,
    KnowledgeAtom,
    ProvenanceClass,
    SourceDocument,
    SourceRecord,
    SourceType,
    TrustClass,
    deterministic_id,
)
from curiosity.ranking.engine import (
    freshness_from_age,
    novelty_from_distance,
    quality_class,
    source_quality_class,
)
from curiosity.runtime import TerminalPlayback
from curiosity.store import LocalStore

NOW = datetime(2026, 9, 3, tzinfo=UTC)


def seed_pulse(
    store: LocalStore,
    *,
    display_fact: str,
    source_label: str,
    topic: str = "general",
    verified_at: datetime = NOW,
    provider_used: bool = False,
    reason_codes: tuple[str, ...] = ("direct_textual_support",),
) -> str:
    source_id = deterministic_id("source", source_label)
    document_id = deterministic_id("document", source_label)
    chunk_id = deterministic_id("chunk", source_label)
    atom_id = deterministic_id("atom", source_label)
    card_id = deterministic_id("card", source_label)
    evidence_id = deterministic_id("evidence", source_label)
    store.put_source(
        SourceRecord(
            id=source_id,
            source_type=SourceType.NOTE,
            canonical_locator=f"local://{source_label}",
            title=source_label,
            trust=TrustClass.REMOTE_UNTRUSTED,
            provenance=ProvenanceClass.USER_AUTHORED,
            retrieved_at=NOW,
        )
    )
    store.put_document(
        SourceDocument(
            id=document_id,
            source_id=source_id,
            content_sha256="a" * 64,
            raw_text=display_fact,
            captured_at=NOW,
            provenance=ProvenanceClass.SOURCE,
        )
    )
    store.put_chunk(
        Chunk(
            id=chunk_id,
            document_id=document_id,
            ordinal=0,
            text=display_fact,
            char_start=0,
            char_end=len(display_fact),
            provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
        )
    )
    store.put_atom(
        KnowledgeAtom(
            id=atom_id,
            statement=display_fact,
            claim_status="supported",
            evidence_ids=(evidence_id,),
            provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
            created_at=NOW,
        )
    )
    store.put_evidence(
        Evidence(
            id=evidence_id,
            source_id=source_id,
            document_id=document_id,
            chunk_id=chunk_id,
            quote=display_fact,
            support=EvidenceSupport.DIRECT,
            provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
        )
    )
    store.put_card(
        CuriosityCard(
            id=card_id,
            card_type=CardType.QUESTION,
            prompt=display_fact,
            atom_ids=(atom_id,),
            evidence_ids=(evidence_id,),
            provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
            created_at=NOW,
        )
    )
    pulse = CuriosityPulse(
        id=deterministic_id("pulse", source_label),
        card_id=card_id,
        atom_id=atom_id,
        display_fact=display_fact,
        topics=(topic,),
        source_id=source_id,
        document_id=document_id,
        evidence_ids=(evidence_id,),
        verified_at=verified_at,
        provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
    )
    store.put_pulse(
        pulse,
        verification={
            "status": "verified",
            "reason_codes": list(reason_codes),
            "risk_flags": [],
            "provider_used": provider_used,
        },
        stage_key="seed-stage",
    )
    store.put_stage_key(
        source_id=source_id,
        document_id=document_id,
        parser_version="plain-1",
        document_key="",
        stage_key="seed-stage",
    )
    return pulse.id


def app_with(store: LocalStore) -> CuriosityApplication:
    app = CuriosityApplication(store)
    app.initialize()
    return app


def test_signal_functions_are_explainable():
    assert quality_class({"status": "verified", "reason_codes": ["direct_textual_support"], "risk_flags": []}) == (1.0, "direct_support")
    assert quality_class({"status": "verified", "reason_codes": [], "risk_flags": [], "provider_used": True}) == (0.8, "model_verified")
    assert source_quality_class("remote_untrusted")[0] == 0.5
    assert source_quality_class("curated")[0] == 1.0
    assert freshness_from_age(0) == 1.0
    assert 0.0 < freshness_from_age(3600 * 24 * 90) < 0.5
    assert novelty_from_distance(None) == 1.0
    assert novelty_from_distance(10) == 0.0
    assert novelty_from_distance(30) == 1.0


def drain(app, limit=20) -> None:
    shown = 0
    while shown < limit:
        pulse = app.current_playback_pulse()
        if pulse is None:
            break
        app.acknowledge_playback_pulse(pulse)
        shown += 1


def test_profile_weights_change_queue_order(tmp_path):
    current = [NOW]

    def now():
        return current[0]

    with LocalStore(tmp_path / "c.db") as store:
        app = CuriosityApplication(store, now=now)
        app.initialize()
        seed_pulse(store, display_fact="Coral reefs support marine biodiversity.", source_label="coral", topic="science")
        seed_pulse(store, display_fact="Baroque art emphasizes dramatic light and shadow.", source_label="baroque", topic="art")
        app.configure_profile(weights={"science": 3.0, "art": 1.0})
        first = app.prepare_playback(size=2)
        assert first[0].topics[0] == "science"
        drain(app)
        current[0] = NOW.replace(hour=NOW.hour + 8)  # let the cooldown lapse
        app.configure_profile(weights={"art": 3.0, "science": 1.0})
        second = app.prepare_playback(size=2)
        assert second[0].topics[0] == "art"


def test_excluded_topic_never_appears(tmp_path):
    with LocalStore(tmp_path / "c.db") as store:
        app = app_with(store)
        seed_pulse(store, display_fact="Coral reefs support marine biodiversity.", source_label="coral", topic="science")
        seed_pulse(store, display_fact="Baroque art emphasizes dramatic light and shadow.", source_label="baroque", topic="art")
        app.configure_profile(weights={"science": 3.0, "art": 1.0}, excluded_topics=("art",))
        queued = app.prepare_playback(size=2)
        assert [pulse.topics[0] for pulse in queued] == ["science"]


def test_recently_shown_fact_is_demoted_and_recovers_after_cooldown(tmp_path):
    current = [NOW]

    def now():
        return current[0]

    with LocalStore(tmp_path / "c.db") as store:
        app = CuriosityApplication(store, now=now)
        app.initialize()
        seed_pulse(store, display_fact="Coral reefs support marine biodiversity.", source_label="coral", topic="science")
        seed_pulse(store, display_fact="Baroque art emphasizes dramatic light and shadow.", source_label="baroque", topic="art")
        app.configure_profile(weights={"science": 3.0, "art": 1.0})
        first = app.prepare_playback(size=1)
        coral_card = first[0].card_id
        pulse = app.current_playback_pulse()
        assert pulse is not None
        app.acknowledge_playback_pulse(pulse)
        # The just-shown science fact is now in the hard repeat window (age ~0).
        second = app.prepare_playback(size=1)
        assert second[0].card_id != coral_card
        pool = app._build_ranked_pool(app.initialize())
        assert not any(candidate.id == deterministic_id("pulse", "coral") for candidate in pool[0])
        # Advance the clock past the wall-clock hard window; the fact recovers.
        current[0] = NOW.replace(hour=NOW.hour + 8)
        pool = app._build_ranked_pool(app.initialize())
        assert any(candidate.id == deterministic_id("pulse", "coral") for candidate in pool[0])


def test_continuous_refill_plays_beyond_old_six_item_limit(tmp_path):
    from curiosity.contracts.model import ModelCallResult, ModelCapabilities, ModelGateway

    class SpyEndpoint:
        model_id = "spy"
        capabilities = ModelCapabilities()

        def __init__(self):
            self.calls = 0

        def generate(self, prompt):
            self.calls += 1
            return ModelCallResult(content="unused")

        def generate_structured(self, prompt, *, response_schema):
            return self.generate(prompt)

    spy = SpyEndpoint()
    with LocalStore(tmp_path / "c.db") as store:
        app = CuriosityApplication(store, gateway=ModelGateway(cheap=spy))
        app.initialize()
        for number in range(14):
            seed_pulse(
                store,
                display_fact=f"Observation number {number} confirms a repeatable result.",
                source_label=f"fact{number}",
                topic="general",
            )
        shown = 0
        first_batch = app.prepare_playback(size=6)
        assert len(first_batch) == 6
        while True:
            pulse = app.current_playback_pulse()
            if pulse is None:
                if not app.refill_playback():
                    break
                continue
            app.acknowledge_playback_pulse(pulse)
            shown += 1
            app.refill_playback()
        assert shown >= 12  # crosses multiple refill cycles
        assert spy.calls == 0  # zero provider work across every display/refill cycle


def test_tiny_corpus_reaches_exhaustion_without_spin(tmp_path):
    with LocalStore(tmp_path / "c.db") as store:
        app = app_with(store)
        seed_pulse(store, display_fact="Coral reefs support marine biodiversity.", source_label="coral")
        assert app.prepare_playback(size=6)
        shown = 0
        while True:
            pulse = app.current_playback_pulse()
            if pulse is None:
                assert not app.refill_playback()
                break
            app.acknowledge_playback_pulse(pulse)
            shown += 1
            assert shown <= 1  # one fact shown, then clean finish, never a tight loop
            if not app.refill_playback():
                break
        assert shown == 1


def test_invalidated_queued_item_is_skipped(tmp_path):
    with LocalStore(tmp_path / "c.db") as store:
        app = app_with(store)
        seed_pulse(store, display_fact="Coral reefs support marine biodiversity.", source_label="coral")
        seed_pulse(store, display_fact="Baroque art emphasizes dramatic light and shadow.", source_label="baroque")
        queued = app.prepare_playback(size=2)
        assert len(queued) == 2
        # Remove one source: its queued pulse is invalidated.
        victim_source = next(
            s for s in app.list_sources() if s.canonical_locator == "local://coral"
        )
        assert app.remove_source(victim_source.id)
        pulse = app.current_playback_pulse()
        assert pulse is not None
        assert "coral" not in pulse.display_fact  # the invalidated item was skipped
        assert app.acknowledge_playback_pulse(pulse)


def test_semantic_stats_reflect_semantic_policy(tmp_path):
    from curiosity.contracts.models import Exposure

    with LocalStore(tmp_path / "c.db") as store:
        app = app_with(store)
        card_a = store.get_pulse(seed_pulse(store, display_fact="Coral reefs support marine biodiversity.", source_label="coral")).card_id
        card_b = store.get_pulse(seed_pulse(store, display_fact="Coral reefs support marine biodiversity.", source_label="coral2")).card_id
        for number, card_id in enumerate((card_a, card_b)):
            store.put_exposure(
                Exposure(
                    id=deterministic_id("exposure", "semantic", str(number)),
                    profile_id=app.default_profile_id(),
                    card_id=card_id,
                    exposed_at=NOW,
                    outcome="shown",
                    provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
                )
            )
        stats = app.stats()
        assert stats["facts_shown"] == 2
        assert stats["distinct_facts_shown"] == 2  # distinct by card
        assert stats["semantic_facts_shown"] == 1  # one idea, shown twice
        assert stats["semantic_repetitions"] == 1


def test_restart_resumes_correct_next_item(tmp_path):
    db = tmp_path / "c.db"
    with LocalStore(db) as store:
        app = app_with(store)
        for number in range(4):
            seed_pulse(
                store,
                display_fact=f"Observation number {number} confirms a repeatable result.",
                source_label=f"fact{number}",
            )
        app.prepare_playback(size=4)
        first = app.current_playback_pulse()
        assert first is not None
        app.acknowledge_playback_pulse(first)
    with LocalStore(db) as store:
        app = app_with(store)
        # Resumes at the item after the acknowledged one, not the first.
        resumed = app.current_playback_pulse()
        assert resumed is not None and resumed.id != first.id


def test_large_corpus_refill_is_bounded_not_pairwise(tmp_path):
    with LocalStore(tmp_path / "c.db") as store:
        app = app_with(store)
        for number in range(200):
            seed_pulse(
                store,
                display_fact=f"Observation number {number} confirms a repeatable result.",
                source_label=f"fact{number}",
                topic="general",
            )
        # A refill must complete promptly on a 200-fact corpus; the firewall uses
        # a bounded FTS shortlist and MMR compares only against selected items.
        first = app.prepare_playback(size=6)
        assert len(first) == 6
        shown = 0
        while True:
            pulse = app.current_playback_pulse()
            if pulse is None:
                if not app.refill_playback():
                    break
                continue
            app.acknowledge_playback_pulse(pulse)
            shown += 1
            app.refill_playback()
        assert shown == 200  # every fact shown exactly once before exhaustion


def test_terminal_playback_uses_refill_and_stays_local(tmp_path):
    with LocalStore(tmp_path / "c.db") as store:
        app = app_with(store)
        for number in range(10):
            seed_pulse(
                store,
                display_fact=f"Observation number {number} confirms a repeatable result.",
                source_label=f"fact{number}",
            )
        app.prepare_playback(size=6)
        output, sleeps = [], []
        shown = TerminalPlayback(app, sleeps.append, output.append, interval_seconds=1).run(once=False)
        assert shown == 10
        assert len(output) == 10 and all("\n" not in line or len(line) < 200 for line in output)