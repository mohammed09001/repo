import sqlite3
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from time import perf_counter

import pytest

import curiosity.store.sqlite as sqlite_module
from curiosity.contracts.models import (
    CardType,
    Chunk,
    CuriosityCard,
    CuriosityPulse,
    Exposure,
    KnowledgeAtom,
    PlaybackSession,
    Profile,
    ProvenanceClass,
    SessionStatus,
    SourceDocument,
    SourceRecord,
    SourceType,
    TrustClass,
    deterministic_id,
)
from curiosity.store import LocalStore, StoreError
from curiosity.store.migrations import CURRENT_SCHEMA_VERSION, Migration

NOW = datetime(2026, 9, 3, tzinfo=UTC)


def records():
    source_id = deterministic_id("source", "store-fixture")
    document_id = deterministic_id("document", "store-fixture")
    card_id = deterministic_id("card", "store-fixture")
    profile_id = deterministic_id("profile", "store-fixture")
    source = SourceRecord(
        id=source_id,
        source_type=SourceType.NOTE,
        canonical_locator="local://store-fixture",
        title="Store fixture",
        trust=TrustClass.LOCAL,
        provenance=ProvenanceClass.USER_AUTHORED,
        retrieved_at=NOW,
    )
    document = SourceDocument(
        id=document_id,
        source_id=source_id,
        content_sha256=sha256(b"durable searchable text").hexdigest(),
        raw_text="durable searchable text",
        captured_at=NOW,
        provenance=ProvenanceClass.USER_AUTHORED,
    )
    chunk = Chunk(
        id=deterministic_id("chunk", "store-fixture"),
        document_id=document_id,
        ordinal=0,
        text="durable searchable text",
        char_start=0,
        char_end=23,
        provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
    )
    card = CuriosityCard(
        id=card_id,
        card_type=CardType.QUESTION,
        prompt="What is durable?",
        atom_ids=(deterministic_id("atom", "store-fixture"),),
        provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
        created_at=NOW,
    )
    profile = Profile(
        id=profile_id, display_name="Ada", created_at=NOW, provenance=ProvenanceClass.USER_AUTHORED
    )
    return source, document, chunk, card, profile


def test_fresh_migrations_and_fts_lifecycle(tmp_path: Path):
    with LocalStore(tmp_path / "store.db") as store:
        source, document, chunk, _, _ = records()
        assert store.schema_version == CURRENT_SCHEMA_VERSION
        assert store.put_source(source)
        assert store.put_document(document) == document.id
        assert store.put_chunk(chunk)
        assert [item.id for item in store.search_documents("searchable")] == [document.id]
        assert [item.id for item in store.search_chunks("durable")] == [chunk.id]
        store.connection.execute("DELETE FROM documents WHERE id = ?", (document.id,))
        assert store.search_documents("searchable") == []
        assert store.search_chunks("durable") == []


def test_upgrade_from_v1_preserves_source_data(tmp_path: Path, monkeypatch):
    path = tmp_path / "upgrade.db"
    with monkeypatch.context() as context:
        context.setattr(sqlite_module, "MIGRATIONS", sqlite_module.MIGRATIONS[:1])
        with LocalStore(path) as seeded:
            source, _, _, _, _ = records()
            seeded.connection.execute(
                """INSERT INTO sources(id, source_type, canonical_locator, title, trust, provenance,
                   retrieved_at, metadata_json, payload_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    source.id,
                    source.source_type,
                    source.canonical_locator,
                    source.title,
                    source.trust,
                    source.provenance,
                    NOW.isoformat(),
                    "{}",
                    source.model_dump_json(),
                ),
            )
            assert seeded.schema_version == 1
    with LocalStore(path) as upgraded:
        assert upgraded.schema_version == CURRENT_SCHEMA_VERSION
        assert (
            upgraded.connection.execute("SELECT title FROM sources").fetchone()[0]
            == "Store fixture"
        )
        restored = upgraded.get_source(source.id)
        assert restored is not None and restored.canonical_locator == source.canonical_locator


def test_upgrade_v6_to_v7_rebuilds_documents_and_backfills_stage_keys(
    tmp_path: Path, monkeypatch
):
    path = tmp_path / "upgrade-v6.db"
    with monkeypatch.context() as context:
        context.setattr(sqlite_module, "MIGRATIONS", sqlite_module.MIGRATIONS[:6])
        with LocalStore(path) as seeded:
            assert seeded.schema_version == 6
            source, document, chunk, card, profile = records()
            seeded.connection.execute(
                """INSERT INTO sources(id, source_type, canonical_locator, title, trust, provenance,
                   retrieved_at, metadata_json, payload_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    source.id,
                    source.source_type,
                    source.canonical_locator,
                    source.title,
                    source.trust,
                    source.provenance,
                    NOW.isoformat(),
                    "{}",
                    source.model_dump_json(),
                ),
            )
            seeded.put_document(document)
            seeded.put_chunk(chunk)
            seeded.put_card(card)
            seeded.put_profile(profile)
            atom_id = deterministic_id("atom", "v6-atom")
            seeded.put_atom(
                KnowledgeAtom(
                    id=atom_id,
                    statement="A v6 claim backed by evidence.",
                    claim_status="supported",
                    evidence_ids=(deterministic_id("evidence", "v6"),),
                    provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
                    created_at=NOW,
                )
            )
            pulse_id = deterministic_id("pulse", "v6-pulse")
            pulse = CuriosityPulse(
                id=pulse_id,
                card_id=card.id,
                atom_id=atom_id,
                display_fact="A v6 claim backed by evidence.",
                topics=("general",),
                source_id=source.id,
                document_id=document.id,
                evidence_ids=(deterministic_id("evidence", "v6"),),
                verified_at=NOW,
                provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
            )
            seeded.connection.execute(
                """INSERT INTO pulses(id, card_id, atom_id, display_fact, source_id, document_id,
                   verified_at, verification_json, payload_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, '{}', ?)""",
                (
                    pulse_id,
                    card.id,
                    atom_id,
                    pulse.display_fact,
                    source.id,
                    document.id,
                    NOW.isoformat(),
                    pulse.model_dump_json(),
                ),
            )
    with LocalStore(path) as upgraded:
        assert upgraded.schema_version == CURRENT_SCHEMA_VERSION
        assert [item.id for item in upgraded.search_documents("searchable")] == [document.id]
        pulse_row = upgraded.connection.execute(
            "SELECT stage_key FROM pulses WHERE id=?", (pulse_id,)
        ).fetchone()
        assert pulse_row is not None and pulse_row["stage_key"] != ""
        current = upgraded.get_stage_key(source.id)
        assert current is not None and current["document_id"] == document.id
        assert current["stage_key"] == pulse_row["stage_key"]
        assert [pulse.id for pulse in upgraded.list_eligible_pulses()] == [pulse_id]
        # The rebuilt documents table keeps working for new inserts.
        extra = document.model_copy(update={"id": deterministic_id("document", "after-upgrade")})
        upgraded.put_document(extra)
        assert [item.id for item in upgraded.search_documents("searchable")] == [
            document.id,
            extra.id,
        ]


def test_upgrade_v7_to_v8_adds_model_economy_tables(tmp_path: Path, monkeypatch):
    path = tmp_path / "upgrade-v7.db"
    with monkeypatch.context() as context:
        context.setattr(sqlite_module, "MIGRATIONS", sqlite_module.MIGRATIONS[:7])
        with LocalStore(path) as seeded:
            assert seeded.schema_version == 7
    with LocalStore(path) as upgraded:
        assert upgraded.schema_version == CURRENT_SCHEMA_VERSION
        upgraded.record_model_usage(
            run_id="run_x",
            task_type="translate",
            model_id="m",
            tier="cheap",
            input_tokens=10,
            output_tokens=5,
            cached_tokens=0,
            latency_ms=1.0,
            cache_hit=False,
            failed=False,
            escalation_reason="non_english",
            source_id=None,
            document_id=None,
        )
        assert len(upgraded.model_usage_summary("run_x")) == 1
        upgraded.put_model_cache(
            cache_key="key",
            task_type="translate",
            model_id="m",
            contract_version="v1",
            result_json="{}",
            cached_tokens=0,
        )
        assert upgraded.get_model_cache("key")["result_json"] == "{}"
        upgraded.record_build_event(
            run_id="run_x", source_id=None, document_id=None, candidate_id="cand_x",
            escalation_reason="non_english", outcome="rejected", detail="offline",
        )
        assert upgraded.connection.execute(
            "SELECT COUNT(*) FROM build_events WHERE run_id='run_x'"
        ).fetchone()[0] == 1


def test_upgrade_v8_to_v9_adds_feed_intelligence(tmp_path: Path, monkeypatch):
    path = tmp_path / "upgrade-v8.db"
    with monkeypatch.context() as context:
        context.setattr(sqlite_module, "MIGRATIONS", sqlite_module.MIGRATIONS[:8])
        with LocalStore(path) as seeded:
            assert seeded.schema_version == 8
            source, document, chunk, card, profile = records()
            seeded.connection.execute(
                """INSERT INTO sources(id, source_type, canonical_locator, title, trust, provenance,
                   retrieved_at, identity_key, metadata_json, payload_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    source.id, source.source_type, source.canonical_locator, source.title,
                    source.trust, source.provenance, NOW.isoformat(), "url:local://x", "{}",
                    source.model_dump_json(),
                ),
            )
            seeded.put_document(document)
            seeded.put_chunk(chunk)
            seeded.put_card(card)
            seeded.put_profile(profile)
            atom_id = deterministic_id("atom", "store-fixture")
            seeded.put_atom(
                KnowledgeAtom(
                    id=atom_id,
                    statement="Mars has two small moons.",
                    claim_status="supported",
                    evidence_ids=(deterministic_id("evidence", "store-fixture"),),
                    provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
                    created_at=NOW,
                )
            )
            from curiosity.contracts.models import CuriosityPulse

            pulse = CuriosityPulse(
                id=deterministic_id("pulse", "v8"),
                card_id=card.id,
                atom_id=atom_id,
                display_fact="Mars has two small moons.",
                topics=("general",),
                source_id=source.id,
                document_id=document.id,
                evidence_ids=(deterministic_id("evidence", "v8"),),
                verified_at=NOW,
                provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
            )
            seeded.connection.execute(
                """INSERT INTO pulses(id, card_id, atom_id, display_fact, source_id, document_id,
                   verified_at, verification_json, stage_key, payload_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, '{}', '', ?)""",
                (
                    pulse.id, pulse.card_id, pulse.atom_id, pulse.display_fact,
                    pulse.source_id, pulse.document_id, NOW.isoformat(),
                    pulse.model_dump_json(),
                ),
            )
    with LocalStore(path) as upgraded:
        assert upgraded.schema_version == CURRENT_SCHEMA_VERSION
        assert upgraded.connection.execute(
            "SELECT fact_fingerprint FROM pulses WHERE id=?", (pulse.id,)
        ).fetchone()[0] != ""
        assert upgraded.connection.execute(
            "SELECT COUNT(*) FROM fact_index"
        ).fetchone()[0] == 1
        assert upgraded.connection.execute(
            "SELECT fingerprint FROM fact_index WHERE pulse_id=?", (pulse.id,)
        ).fetchone()[0] == upgraded.connection.execute(
            "SELECT fact_fingerprint FROM pulses WHERE id=?", (pulse.id,)
        ).fetchone()[0]
        assert upgraded.shortlist_fact_rows("mars AND moons")[0][0] == pulse.id


def test_upgrade_v9_to_v10_adds_ambient_runtime_state(tmp_path: Path, monkeypatch):
    path = tmp_path / "upgrade-v9.db"
    with monkeypatch.context() as context:
        context.setattr(sqlite_module, "MIGRATIONS", sqlite_module.MIGRATIONS[:9])
        with LocalStore(path) as seeded:
            assert seeded.schema_version == 9
    with LocalStore(path) as upgraded:
        assert upgraded.schema_version == CURRENT_SCHEMA_VERSION
        assert upgraded.get_ambient_state() is None
        upgraded.put_ambient_state("active_work", at=NOW)
        assert upgraded.get_ambient_state() == ("active_work", NOW.isoformat())
        upgraded.put_ambient_state("quiet", at=NOW + timedelta(seconds=1))
        assert upgraded.get_ambient_state() == ("quiet", (NOW + timedelta(seconds=1)).isoformat())
        assert upgraded.connection.execute("SELECT COUNT(*) FROM ambient_state").fetchone()[0] == 1


def test_upgrade_v10_to_v11_adds_refresh_run_ledger(tmp_path: Path, monkeypatch):
    path = tmp_path / "upgrade-v10.db"
    with monkeypatch.context() as context:
        context.setattr(sqlite_module, "MIGRATIONS", sqlite_module.MIGRATIONS[:10])
        with LocalStore(path) as seeded:
            assert seeded.schema_version == 10
    with LocalStore(path) as upgraded:
        assert upgraded.schema_version == CURRENT_SCHEMA_VERSION
        assert upgraded.get_last_run_summary() is None
        upgraded.start_run_summary("run_ledger", at=NOW)
        upgraded.finish_run_summary(
            "run_ledger",
            status="succeeded",
            counters={
                "sources": 1,
                "pulses_built": 2,
                "http_fetches": 1,
                "http_cache_hits": 0,
                "retries": 0,
                "failures": 0,
                "parser_elapsed_ms": 12.5,
                "elapsed_ms": 30,
                "model_calls": 0,
            },
            at=NOW + timedelta(seconds=1),
        )
        summary = upgraded.get_last_run_summary()
        assert summary is not None
        assert summary["status"] == "succeeded"
        assert summary["pulses_built"] == 2
        assert summary["parser_elapsed_ms"] == 12.5
        assert len(upgraded.list_run_summaries(limit=5)) == 1


def test_failed_migration_leaves_a_diagnosable_unapplied_version(tmp_path: Path, monkeypatch):
    path = tmp_path / "failed-migration.db"
    with LocalStore(path) as store:
        assert store.schema_version == CURRENT_SCHEMA_VERSION
    bad = Migration(CURRENT_SCHEMA_VERSION + 1, "bad_fixture", ("CREATE TABLE broken (",))
    monkeypatch.setattr(sqlite_module, "MIGRATIONS", (*sqlite_module.MIGRATIONS, bad))
    with pytest.raises(StoreError, match="bad_fixture"):
        LocalStore(path)
    with sqlite3.connect(path) as connection:
        versions = {row[0] for row in connection.execute("SELECT version FROM schema_migrations")}
    assert bad.version not in versions


def test_constraints_idempotency_cache_and_foreign_keys(tmp_path: Path):
    with LocalStore(tmp_path / "store.db") as store:
        source, document, _, _, _ = records()
        assert store.put_source(source)
        assert not store.put_source(source)
        assert store.put_document(document) == document.id
        # Deterministic id gives within-source idempotency; a distinct id is a
        # distinct document even when bytes match (branch-local invalidation).
        assert store.put_document(document) == document.id
        duplicate = document.model_copy(update={"id": deterministic_id("document", "duplicate")})
        assert store.put_document(duplicate) == duplicate.id
        assert store.connection.execute(
            "SELECT COUNT(*) FROM documents WHERE content_sha256=?",
            (document.content_sha256,),
        ).fetchone()[0] == 2
        with pytest.raises(sqlite3.IntegrityError):
            store.connection.execute(
                "INSERT INTO chunks(id, document_id, ordinal, text, char_start, char_end, provenance, payload_json) VALUES ('chunk_deadbeefdeadbeef', 'missing_deadbeefdeadbeef', 0, 'x', 0, 1, 'derived_deterministic', '{}')"
            )
        store.put_cache(
            cache_key="fetch:one",
            content_sha256=document.content_sha256,
            fetched_at=NOW,
            parser_version="1",
            etag="etag",
            last_modified="yesterday",
        )
        assert store.get_cache("fetch:one")["etag"] == "etag"


def test_leases_restart_and_separate_exposure_session_state(tmp_path: Path):
    with LocalStore(tmp_path / "store.db") as store:
        source, document, _, card, profile = records()
        store.put_source(source)
        store.put_document(document)
        store.put_card(card)
        store.put_profile(profile)
        exposure = Exposure(
            id=deterministic_id("exposure", "store-fixture"),
            profile_id=profile.id,
            card_id=card.id,
            exposed_at=NOW,
            outcome="shown",
            provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
        )
        session = PlaybackSession(
            id=deterministic_id("session", "store-fixture"),
            profile_id=profile.id,
            status=SessionStatus.ACTIVE,
            card_ids=(card.id,),
            started_at=NOW,
            provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
        )
        assert store.put_exposure(exposure)
        assert store.put_session(session)
        before = store.connection.execute(
            "SELECT payload_json FROM cards WHERE id=?", (card.id,)
        ).fetchone()[0]
        assert store.create_job(
            job_id=deterministic_id("job", "store-fixture"),
            idempotency_key="ingest:store-fixture",
            stage="ingest",
            now=NOW,
        )
        first = store.claim_job(worker_id="worker-a", lease_seconds=5, now=NOW)
        assert first is not None
        assert store.claim_job(worker_id="worker-b", now=NOW) is None
        assert store.recover_abandoned_jobs(now=NOW + timedelta(seconds=6)) == 1
        reclaimed = store.claim_job(worker_id="worker-b", now=NOW + timedelta(seconds=6))
        assert reclaimed is not None and reclaimed.id == first.id
        assert not store.complete_job(job_id=first.id, worker_id="worker-a")
        assert store.complete_job(job_id=first.id, worker_id="worker-b", input_budget=10)
        assert (
            store.connection.execute(
                "SELECT payload_json FROM cards WHERE id=?", (card.id,)
            ).fetchone()[0]
            == before
        )


def test_diagnostics_and_small_synthetic_fts_latency(tmp_path: Path):
    with LocalStore(tmp_path / "store.db") as store:
        source, document, _, _, _ = records()
        store.put_source(source)
        store.put_document(document)
        for number in range(100):
            store.connection.execute(
                "INSERT INTO documents(id, source_id, content_sha256, raw_text, captured_at, provenance, payload_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    deterministic_id("document", f"bulk-{number}"),
                    source.id,
                    sha256(str(number).encode()).hexdigest(),
                    f"synthetic retrieval token {number}",
                    NOW.isoformat(),
                    "user_authored",
                    document.model_dump_json(),
                ),
            )
        assert store.search_documents("retrieval")
        start = perf_counter()
        assert store.search_documents("retrieval")
        assert perf_counter() - start < 0.25
        diagnostic = store.diagnostics(now=NOW)
        assert diagnostic.integrity_check == "ok"
        assert diagnostic.foreign_key_violations == ()
        store.connection.execute(
            "UPDATE documents SET payload_json = '{' WHERE id = ?", (document.id,)
        )
        assert ("documents", document.id) in store.diagnostics().invalid_payload_rows
