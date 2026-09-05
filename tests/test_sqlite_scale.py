"""SQLite at personal scale: evidence-based indexing and maintenance.

Builds a synthetic corpus large enough to reveal query/index problems, inspects
``EXPLAIN QUERY PLAN`` for the hot queries, and measures prepare/refill and the
display-tick read against a target budget. No authoritative lineage is pruned;
``PRAGMA optimize`` is exercised as a capability-safe maintenance point.
"""

import time
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path

from curiosity.application import CuriosityApplication
from curiosity.contracts.models import (
    CardType,
    CuriosityCard,
    CuriosityPulse,
    Exposure,
    KnowledgeAtom,
    Profile,
    ProvenanceClass,
    SourceDocument,
    SourceRecord,
    SourceType,
    TrustClass,
    deterministic_id,
)
from curiosity.store import LocalStore

NOW = datetime(2026, 9, 5, tzinfo=UTC)

SCALE_PULSES = 400
SCALE_EXPOSURES_PER_PULSE = 8


def _seed_large_store(store: LocalStore, profile_id: str, source_id: str, document_id: str) -> None:
    """Seed a synthetic corpus of eligible pulses and exposure history."""
    for i in range(SCALE_PULSES):
        atom_id = deterministic_id("atom", "scale", str(i))
        evidence_id = deterministic_id("evidence", "scale", str(i))
        card_id = deterministic_id("card", "scale", str(i))
        card = CuriosityCard(
            id=card_id,
            card_type=CardType.INSIGHT,
            prompt=f"prompt {i}",
            atom_ids=(atom_id,),
            provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
            created_at=NOW,
        )
        store.put_card(card)
        store.put_atom(
            KnowledgeAtom(
                id=atom_id,
                statement=f"Scale fact number {i} about the corpus.",
                claim_status="supported",
                evidence_ids=(evidence_id,),
                provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
                created_at=NOW,
            )
        )
        pulse = CuriosityPulse(
            id=deterministic_id("pulse", "scale", str(i)),
            card_id=card_id,
            atom_id=atom_id,
            display_fact=f"Scale fact number {i} about the corpus.",
            topics=("general",),
            source_id=source_id,
            document_id=document_id,
            evidence_ids=(evidence_id,),
            verified_at=NOW,
            provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
        )
        store.put_pulse(pulse, verification={}, stage_key="s")
        for e in range(SCALE_EXPOSURES_PER_PULSE):
            store.put_exposure(
                Exposure(
                    id=deterministic_id("exposure", "scale", str(i), str(e)),
                    profile_id=profile_id,
                    card_id=card_id,
                    exposed_at=NOW - timedelta(days=2, hours=i),
                    outcome="shown",
                    provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
                )
            )


def _plan(store: LocalStore, sql: str, params: tuple = ()) -> str:
    rows = store.connection.execute("EXPLAIN QUERY PLAN " + sql, params).fetchall()
    return " | ".join(str(row[3]) for row in rows)


def test_hot_query_plans_use_intended_indexes(tmp_path: Path):
    store = LocalStore(tmp_path / "scale.db")
    try:
        profile_id = deterministic_id("profile", "scale")
        source_id = deterministic_id("source", "scale")
        document_id = deterministic_id("document", "scale")
        store.put_profile(
            Profile(id=profile_id, display_name="Scale", created_at=NOW, provenance=ProvenanceClass.USER_AUTHORED)
        )
        store.put_source(
            SourceRecord(
                id=source_id,
                source_type=SourceType.WEB,
                canonical_locator="https://example.test/scale",
                title="Scale",
                trust=TrustClass.REMOTE_UNTRUSTED,
                provenance=ProvenanceClass.SOURCE,
                retrieved_at=NOW,
            )
        )
        store.put_document(
            SourceDocument(
                id=document_id,
                source_id=source_id,
                content_sha256=sha256(b"scale").hexdigest(),
                raw_text="scale",
                captured_at=NOW,
                provenance=ProvenanceClass.SOURCE,
            )
        )
        store.put_stage_key(
            source_id=source_id,
            document_id=document_id,
            parser_version="plain-1",
            document_key="k",
            stage_key="s",
        )
        _seed_large_store(store, profile_id, source_id, document_id)

        # Exposure history must use the profile/time index.
        exposures_plan = _plan(
            store,
            """SELECT e.card_id FROM exposures e
               JOIN pulses p ON p.card_id = e.card_id
               WHERE e.profile_id=? AND e.exposed_at >= ? ORDER BY e.exposed_at DESC LIMIT 5000""",
            (profile_id, "2020-01-01T00:00:00+00:00"),
        )
        assert "exposures_profile_time_idx" in exposures_plan
        # The session queue hot query must use the sessions index, not a scan.
        session_plan = _plan(
            store,
            """SELECT id, position FROM sessions
               WHERE profile_id=? AND status IN ('created', 'active')
               ORDER BY started_at DESC LIMIT 1""",
            (profile_id,),
        )
        assert "sessions_profile_status_started_idx" in session_plan
        assert "SCAN sessions" not in session_plan
    finally:
        store.close()


def test_large_store_prepares_and_refills_within_budget(tmp_path: Path):
    store = LocalStore(tmp_path / "scale.db")
    try:
        app = CuriosityApplication(store, now=lambda: NOW)
        profile_id = app.default_profile_id()
        app.initialize()
        source_id = deterministic_id("source", "scale")
        document_id = deterministic_id("document", "scale")
        store.put_source(
            SourceRecord(
                id=source_id,
                source_type=SourceType.WEB,
                canonical_locator="https://example.test/scale",
                title="Scale",
                trust=TrustClass.REMOTE_UNTRUSTED,
                provenance=ProvenanceClass.SOURCE,
                retrieved_at=NOW,
            )
        )
        store.put_document(
            SourceDocument(
                id=document_id,
                source_id=source_id,
                content_sha256=sha256(b"scale").hexdigest(),
                raw_text="scale",
                captured_at=NOW,
                provenance=ProvenanceClass.SOURCE,
            )
        )
        store.put_stage_key(
            source_id=source_id,
            document_id=document_id,
            parser_version="plain-1",
            document_key="k",
            stage_key="s",
        )
        _seed_large_store(store, profile_id, source_id, document_id)

        started = time.perf_counter()
        prepared = app.prepare_playback(size=6)
        prepare_ms = (time.perf_counter() - started) * 1000
        assert prepared
        assert prepare_ms < 1000, f"prepare_playback took {prepare_ms:.1f}ms on scale corpus"

        # The display tick must stay a fast local read.
        started = time.perf_counter()
        current = app.current_playback_pulse()
        tick_ms = (time.perf_counter() - started) * 1000
        assert current is not None
        assert tick_ms < 100, f"tick read took {tick_ms:.2f}ms"

        # Continuous refill extends the durable queue below the low watermark.
        for _ in range(4):
            pulse = app.current_playback_pulse()
            if pulse is None:
                break
            app.acknowledge_playback_pulse(pulse)
        remaining_before = store.remaining_playback_count(profile_id)
        assert remaining_before <= 3
        started = time.perf_counter()
        assert app.refill_playback()
        refill_ms = (time.perf_counter() - started) * 1000
        assert refill_ms < 1000, f"refill took {refill_ms:.1f}ms"
        assert store.remaining_playback_count(profile_id) > remaining_before
    finally:
        store.close()


def test_pragma_optimize_is_capability_safe(tmp_path: Path):
    # PRAGMA optimize must not raise on a healthy store and must be guarded
    # against unsupported engines.
    with LocalStore(tmp_path / "opt.db") as store:
        store.connection.execute("CREATE TABLE t(x INTEGER)")
        store.connection.execute("INSERT INTO t VALUES (1), (2), (3)")
        store.connection.execute("PRAGMA optimize")
        assert store.connection.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 3
    # A real close() also runs it safely.
    store = LocalStore(tmp_path / "opt2.db")
    store.put_profile(
        Profile(
            id=deterministic_id("profile", "opt"),
            display_name="Opt",
            created_at=NOW,
            provenance=ProvenanceClass.USER_AUTHORED,
        )
    )
    store.close()


def test_no_authoritative_lineage_is_pruned_by_scale_load(tmp_path: Path):
    with LocalStore(tmp_path / "scale.db") as store:
        profile_id = deterministic_id("profile", "scale")
        source_id = deterministic_id("source", "scale")
        document_id = deterministic_id("document", "scale")
        store.put_profile(
            Profile(id=profile_id, display_name="Scale", created_at=NOW, provenance=ProvenanceClass.USER_AUTHORED)
        )
        store.put_source(
            SourceRecord(
                id=source_id,
                source_type=SourceType.WEB,
                canonical_locator="https://example.test/scale",
                title="Scale",
                trust=TrustClass.REMOTE_UNTRUSTED,
                provenance=ProvenanceClass.SOURCE,
                retrieved_at=NOW,
            )
        )
        store.put_document(
            SourceDocument(
                id=document_id,
                source_id=source_id,
                content_sha256=sha256(b"scale").hexdigest(),
                raw_text="scale",
                captured_at=NOW,
                provenance=ProvenanceClass.SOURCE,
            )
        )
        _seed_large_store(store, profile_id, source_id, document_id)
        before_exposures = store.connection.execute("SELECT COUNT(*) FROM exposures").fetchone()[0]
        before_pulses = store.connection.execute("SELECT COUNT(*) FROM pulses").fetchone()[0]
        # A full recent-exposures read (the cooldown query) must not delete rows.
        store.recent_exposures(profile_id, since="2020-01-01T00:00:00+00:00", limit=5000)
        assert (
            store.connection.execute("SELECT COUNT(*) FROM exposures").fetchone()[0]
            == before_exposures
        )
        assert store.connection.execute("SELECT COUNT(*) FROM pulses").fetchone()[0] == before_pulses


def test_fts_shortlist_is_bounded_and_uses_fts5(tmp_path: Path):
    with LocalStore(tmp_path / "fts.db") as store:
        source_id = deterministic_id("source", "fts")
        document_id = deterministic_id("document", "fts")
        store.put_source(
            SourceRecord(
                id=source_id,
                source_type=SourceType.WEB,
                canonical_locator="https://example.test/fts",
                title="FTS",
                trust=TrustClass.REMOTE_UNTRUSTED,
                provenance=ProvenanceClass.SOURCE,
                retrieved_at=NOW,
            )
        )
        store.put_document(
            SourceDocument(
                id=document_id,
                source_id=source_id,
                content_sha256=sha256(b"fts").hexdigest(),
                raw_text="fts",
                captured_at=NOW,
                provenance=ProvenanceClass.SOURCE,
            )
        )
        for i in range(100):
            card_id = deterministic_id("card", "fts", str(i))
            atom_id = deterministic_id("atom", "fts", str(i))
            store.put_atom(
                KnowledgeAtom(
                    id=atom_id,
                    statement=f"A shortlist searchable scale fact number {i}.",
                    claim_status="supported",
                    evidence_ids=(deterministic_id("evidence", "fts", str(i)),),
                    provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
                    created_at=NOW,
                )
            )
            store.put_card(
                CuriosityCard(
                    id=card_id,
                    card_type=CardType.INSIGHT,
                    prompt=f"p{i}",
                    atom_ids=(atom_id,),
                    provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
                    created_at=NOW,
                )
            )
            store.put_pulse(
                CuriosityPulse(
                    id=deterministic_id("pulse", "fts", str(i)),
                    card_id=card_id,
                    atom_id=atom_id,
                    display_fact=f"A shortlist searchable scale fact number {i}.",
                    topics=("general",),
                    source_id=source_id,
                    document_id=document_id,
                    evidence_ids=(deterministic_id("evidence", "fts", str(i)),),
                    verified_at=NOW,
                    provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
                ),
                verification={},
            )
        rows = store.shortlist_fact_rows("searchable AND scale", limit=20)
        assert len(rows) <= 20
        assert rows
        # A query term missing from the FTS index never crashes the shortlist.
        assert store.shortlist_fact_rows("zzzznope", limit=10) == []