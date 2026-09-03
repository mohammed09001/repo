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
    Exposure,
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


def test_upgrade_from_v1_preserves_source_data(tmp_path: Path):
    path = tmp_path / "upgrade.db"
    with LocalStore(path) as seeded:
        source, _, _, _, _ = records()
        seeded.put_source(source)
        seeded.connection.execute("DELETE FROM schema_migrations WHERE version = 2")
        seeded.connection.execute("DROP TRIGGER documents_ai")
        seeded.connection.execute("DROP TRIGGER documents_ad")
        seeded.connection.execute("DROP TRIGGER chunks_ai")
        seeded.connection.execute("DROP TRIGGER chunks_ad")
        seeded.connection.execute("DROP TABLE session_cards")
        seeded.connection.execute("DROP TABLE sessions")
        seeded.connection.execute("DROP TABLE exposures")
        seeded.connection.execute("DROP TABLE profiles")
        seeded.connection.execute("DROP TABLE cards")
        seeded.connection.execute("DROP TABLE atoms")
        seeded.connection.execute("DROP TABLE evidence")
        seeded.connection.execute("DROP TABLE chunks_fts")
        seeded.connection.execute("DROP TABLE documents_fts")
        seeded.connection.execute("DROP TABLE chunks")
        seeded.connection.execute("DROP TABLE jobs")
        seeded.connection.execute("DROP TABLE caches")
        seeded.connection.execute("DROP TABLE adapter_state")
    with LocalStore(path) as upgraded:
        assert upgraded.schema_version == CURRENT_SCHEMA_VERSION
        assert (
            upgraded.connection.execute("SELECT title FROM sources").fetchone()[0]
            == "Store fixture"
        )


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
        duplicate = document.model_copy(update={"id": deterministic_id("document", "duplicate")})
        assert store.put_document(duplicate) == document.id
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
        start = perf_counter()
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
        assert perf_counter() - start < 1.0
        diagnostic = store.diagnostics(now=NOW)
        assert diagnostic.integrity_check == "ok"
        assert diagnostic.foreign_key_violations == ()
        store.connection.execute(
            "UPDATE documents SET payload_json = '{' WHERE id = ?", (document.id,)
        )
        assert ("documents", document.id) in store.diagnostics().invalid_payload_rows
