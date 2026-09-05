"""Typed SQLite repositories with explicit transactions and durable job leases."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from curiosity.contracts.identity import source_identity_key
from curiosity.contracts.models import (
    Chunk,
    CuriosityCard,
    CuriosityPulse,
    Evidence,
    Exposure,
    HarnessEvent,
    KnowledgeAtom,
    PlaybackSession,
    Profile,
    ProvenanceClass,
    SourceDocument,
    SourceRecord,
    deterministic_id,
)

from .migrations import MIGRATIONS


class StoreError(RuntimeError):
    """A diagnostic local-store failure; callers must not silently discard it."""


@dataclass(frozen=True)
class ClaimedJob:
    id: str
    idempotency_key: str
    stage: str
    attempts: int
    input_budget: int
    output_budget: int


@dataclass(frozen=True)
class StoreDiagnostic:
    schema_version: int
    integrity_check: str
    foreign_key_violations: tuple[tuple[Any, ...], ...]
    invalid_payload_rows: tuple[tuple[str, str], ...]
    recoverable_running_jobs: int


def _timestamp(value: datetime | None = None) -> str:
    return (value or datetime.now(UTC)).astimezone(UTC).isoformat()


class LocalStore:
    """The one local SQLite database for canonical content and mutable work state."""

    def __init__(self, path: Path | str, *, busy_timeout_ms: int = 5_000):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path, isolation_level=None)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.execute(f"PRAGMA busy_timeout = {int(busy_timeout_ms)}")
        # WAL is appropriate for a single-machine store with occasional concurrent readers/workers.
        self.connection.execute("PRAGMA journal_mode = WAL")
        self._usage_seq = 0
        self.migrate()

    def close(self) -> None:
        # SQLite-recommended cheap maintenance; guarded for capability safety.
        try:
            self.connection.execute("PRAGMA optimize")
        except sqlite3.Error:
            pass
        self.connection.close()

    def __enter__(self) -> LocalStore:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    @contextmanager
    def transaction(self, *, immediate: bool = False) -> Iterator[sqlite3.Connection]:
        self.connection.execute("BEGIN IMMEDIATE" if immediate else "BEGIN")
        try:
            yield self.connection
        except Exception:
            self.connection.rollback()
            raise
        else:
            self.connection.commit()

    def migrate(self) -> None:
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations (version INTEGER PRIMARY KEY, name TEXT NOT NULL, applied_at TEXT NOT NULL)"
        )
        applied = {
            row[0] for row in self.connection.execute("SELECT version FROM schema_migrations")
        }
        for migration in MIGRATIONS:
            if migration.version in applied:
                continue
            try:
                if migration.foreign_keys_off:
                    # PRAGMA foreign_keys cannot be toggled inside a transaction,
                    # but the rebuild statements themselves run atomically below.
                    self.connection.execute("PRAGMA foreign_keys=OFF")
                    with self.transaction(immediate=True) as connection:
                        for statement in migration.statements:
                            connection.execute(statement)
                        connection.execute(
                            "INSERT INTO schema_migrations(version, name, applied_at) VALUES (?, ?, ?)",
                            (migration.version, migration.name, _timestamp()),
                        )
                    self.connection.execute("PRAGMA foreign_keys=ON")
                else:
                    with self.transaction(immediate=True) as connection:
                        for statement in migration.statements:
                            connection.execute(statement)
                        connection.execute(
                            "INSERT INTO schema_migrations(version, name, applied_at) VALUES (?, ?, ?)",
                            (migration.version, migration.name, _timestamp()),
                        )
            except sqlite3.Error as error:
                raise StoreError(
                    f"migration {migration.version} ({migration.name}) failed: {error}"
                ) from error
            if migration.version == 7:
                self._backfill_v7()
            if migration.version == 9:
                self._backfill_v9()
        self.connection.execute("PRAGMA foreign_keys=ON")

    def _backfill_v7(self) -> None:
        """Give pre-existing pulses a real stage key and mark current documents."""
        from curiosity.contracts.stages import stage_key

        with self.transaction(immediate=True) as connection:
            for row in connection.execute(
                "SELECT id, document_id FROM pulses WHERE stage_key = ''"
            ):
                connection.execute(
                    "UPDATE pulses SET stage_key=? WHERE id=?",
                    (stage_key(row["document_id"]), row["id"]),
                )
            current = connection.execute(
                """SELECT source_id, document_id FROM (
                     SELECT source_id, document_id, verified_at,
                            ROW_NUMBER() OVER (
                                PARTITION BY source_id ORDER BY verified_at DESC, id DESC
                            ) AS rn
                     FROM pulses
                   ) WHERE rn = 1"""
            ).fetchall()
            for row in current:
                connection.execute(
                    """INSERT INTO stage_keys(source_id, document_id, parser_version, document_key, stage_key, built_at)
                       VALUES (?, ?, '', '', ?, ?)
                       ON CONFLICT(source_id) DO UPDATE SET document_id=excluded.document_id,
                       parser_version='', document_key='', stage_key=excluded.stage_key, built_at=excluded.built_at""",
                    (row["source_id"], row["document_id"], stage_key(row["document_id"]), _timestamp()),
                )

    def _backfill_v9(self) -> None:
        """Fingerprint existing pulses and seed the Near-Duplicate Firewall index."""
        from curiosity.knowledge.engine import fact_fingerprint

        with self.transaction(immediate=True) as connection:
            for row in connection.execute(
                "SELECT id, card_id, source_id, payload_json FROM pulses"
            ):
                display = str(json.loads(row["payload_json"]).get("display_fact", ""))
                fingerprint = fact_fingerprint(display)
                connection.execute(
                    "UPDATE pulses SET fact_fingerprint=? WHERE id=?",
                    (fingerprint, row["id"]),
                )
                connection.execute(
                    """INSERT OR IGNORE INTO fact_index(pulse_id, card_id, source_id, fingerprint, fact_text, created_at)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (row["id"], row["card_id"], row["source_id"], fingerprint, display, _timestamp()),
                )

    @property
    def schema_version(self) -> int:
        row = self.connection.execute(
            "SELECT COALESCE(MAX(version), 0) FROM schema_migrations"
        ).fetchone()
        return int(row[0])

    def _insert(self, table: str, values: dict[str, Any]) -> bool:
        columns = ", ".join(values)
        placeholders = ", ".join("?" for _ in values)
        with self.transaction(immediate=True) as connection:
            result = connection.execute(
                f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) ON CONFLICT(id) DO NOTHING",
                tuple(values.values()),
            )
        return result.rowcount == 1

    def put_source(self, source: SourceRecord) -> bool:
        return self._insert(
            "sources",
            {
                "id": source.id,
                "source_type": source.source_type,
                "canonical_locator": source.canonical_locator,
                "title": source.title,
                "trust": source.trust,
                "provenance": source.provenance,
                "retrieved_at": _timestamp(source.retrieved_at),
                "identity_key": source_identity_key(source),
                "metadata_json": json.dumps(source.metadata, sort_keys=True),
                "payload_json": source.model_dump_json(),
            },
        )

    def source_conflicts(self, *, locator: str, identity_key: str) -> bool:
        """True when a registered source already proves the same work."""
        row = self.connection.execute(
            """SELECT 1 FROM sources
               WHERE canonical_locator = ? OR (identity_key = ? AND identity_key IS NOT NULL)
               LIMIT 1""",
            (locator, identity_key),
        ).fetchone()
        return row is not None

    def put_document(self, document: SourceDocument) -> str:
        existing = self.connection.execute(
            "SELECT id FROM documents WHERE id=?", (document.id,)
        ).fetchone()
        if existing:
            return str(existing["id"])
        self._insert(
            "documents",
            {
                "id": document.id,
                "source_id": document.source_id,
                "content_sha256": document.content_sha256,
                "raw_text": document.raw_text,
                "captured_at": _timestamp(document.captured_at),
                "provenance": document.provenance,
                "payload_json": document.model_dump_json(),
            },
        )
        return document.id

    def put_chunk(self, chunk: Chunk) -> bool:
        return self._insert(
            "chunks",
            {
                "id": chunk.id,
                "document_id": chunk.document_id,
                "ordinal": chunk.ordinal,
                "text": chunk.text,
                "char_start": chunk.char_start,
                "char_end": chunk.char_end,
                "provenance": chunk.provenance,
                "payload_json": chunk.model_dump_json(),
            },
        )

    def put_evidence(self, evidence: Evidence) -> bool:
        return self._insert(
            "evidence",
            {
                "id": evidence.id,
                "source_id": evidence.source_id,
                "document_id": evidence.document_id,
                "chunk_id": evidence.chunk_id,
                "quote": evidence.quote,
                "support": evidence.support,
                "provenance": evidence.provenance,
                "payload_json": evidence.model_dump_json(),
            },
        )

    def put_atom(self, atom: KnowledgeAtom) -> bool:
        return self._insert(
            "atoms",
            {
                "id": atom.id,
                "statement": atom.statement,
                "claim_status": atom.claim_status,
                "provenance": atom.provenance,
                "created_at": _timestamp(atom.created_at),
                "payload_json": atom.model_dump_json(),
            },
        )

    def put_card(self, card: CuriosityCard) -> bool:
        return self._insert(
            "cards",
            {
                "id": card.id,
                "card_type": card.card_type,
                "prompt": card.prompt,
                "provenance": card.provenance,
                "created_at": _timestamp(card.created_at),
                "payload_json": card.model_dump_json(),
            },
        )

    def put_pulse(
        self,
        pulse: CuriosityPulse,
        *,
        verification: dict[str, Any],
        stage_key: str = "",
    ) -> bool:
        from curiosity.knowledge.engine import fact_fingerprint

        fingerprint = fact_fingerprint(pulse.display_fact)
        with self.transaction(immediate=True) as connection:
            result = connection.execute(
                """INSERT INTO pulses (id, card_id, atom_id, display_fact, source_id, document_id,
                   verified_at, verification_json, stage_key, fact_fingerprint, payload_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(id) DO NOTHING""",
                (
                    pulse.id,
                    pulse.card_id,
                    pulse.atom_id,
                    pulse.display_fact,
                    pulse.source_id,
                    pulse.document_id,
                    _timestamp(pulse.verified_at),
                    json.dumps(verification, sort_keys=True),
                    stage_key,
                    fingerprint,
                    pulse.model_dump_json(),
                ),
            )
            inserted = result.rowcount == 1
            connection.execute(
                """INSERT INTO fact_index(pulse_id, card_id, source_id, fingerprint, fact_text, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT(pulse_id) DO UPDATE SET source_id=excluded.source_id,
                   fingerprint=excluded.fingerprint, fact_text=excluded.fact_text""",
                (pulse.id, pulse.card_id, pulse.source_id, fingerprint, pulse.display_fact, _timestamp()),
            )
        return inserted

    def put_profile(self, profile: Profile) -> bool:
        values = {
            "id": profile.id,
            "display_name": profile.display_name,
            "created_at": _timestamp(profile.created_at),
            "provenance": profile.provenance,
            "payload_json": profile.model_dump_json(),
        }
        with self.transaction(immediate=True) as connection:
            result = connection.execute(
                """INSERT INTO profiles (id, display_name, created_at, provenance, payload_json)
                   VALUES (:id, :display_name, :created_at, :provenance, :payload_json)
                   ON CONFLICT(id) DO UPDATE SET display_name=excluded.display_name,
                   payload_json=excluded.payload_json""",
                values,
            )
        return result.rowcount == 1

    def get_profile(self, profile_id: str) -> Profile | None:
        row = self.connection.execute(
            "SELECT payload_json FROM profiles WHERE id=?", (profile_id,)
        ).fetchone()
        return Profile.model_validate_json(row["payload_json"]) if row else None

    def get_source(self, source_id: str) -> SourceRecord | None:
        row = self.connection.execute(
            "SELECT payload_json FROM sources WHERE id=?", (source_id,)
        ).fetchone()
        return SourceRecord.model_validate_json(row["payload_json"]) if row else None

    def list_sources(self) -> list[SourceRecord]:
        rows = self.connection.execute(
            "SELECT payload_json FROM sources ORDER BY canonical_locator"
        )
        return [SourceRecord.model_validate_json(row["payload_json"]) for row in rows]

    def remove_source(self, source_id: str) -> bool:
        with self.transaction(immediate=True) as connection:
            result = connection.execute("DELETE FROM sources WHERE id=?", (source_id,))
        return result.rowcount == 1

    def list_pulses(self) -> list[CuriosityPulse]:
        rows = self.connection.execute("SELECT payload_json FROM pulses ORDER BY verified_at, id")
        return [CuriosityPulse.model_validate_json(row["payload_json"]) for row in rows]

    def list_eligible_pulses(self) -> list[CuriosityPulse]:
        """Only pulses whose document and stage fingerprint match the current build.

        Superseded pulses stay readable for inspect but are never ranked here.
        """
        return [pulse for pulse, _ in self.list_eligible_with_fingerprint()]

    def list_eligible_with_fingerprint(self) -> list[tuple[CuriosityPulse, str]]:
        """Eligible pulses paired with their claim fingerprint for the firewall
        and exposure cooldown."""
        rows = self.connection.execute(
            """SELECT p.payload_json, p.fact_fingerprint FROM pulses p
               JOIN stage_keys s ON s.source_id = p.source_id
               WHERE p.document_id = s.document_id AND p.stage_key = s.stage_key
               ORDER BY p.verified_at, p.id"""
        )
        return [
            (CuriosityPulse.model_validate_json(row["payload_json"]), str(row["fact_fingerprint"]))
            for row in rows
        ]

    def get_pulse(self, pulse_id: str) -> CuriosityPulse | None:
        row = self.connection.execute(
            "SELECT payload_json FROM pulses WHERE id=?", (pulse_id,)
        ).fetchone()
        return CuriosityPulse.model_validate_json(row["payload_json"]) if row else None

    def get_pulse_verification(self, pulse_id: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            "SELECT verification_json FROM pulses WHERE id=?", (pulse_id,)
        ).fetchone()
        return json.loads(row["verification_json"]) if row else None

    def payloads_for_ids(self, table: str, ids: tuple[str, ...]) -> list[dict[str, Any]]:
        """Read lineage owned by a pulse; table names are deliberately closed."""
        if table not in {"atoms", "cards", "evidence"} or not ids:
            return []
        marks = ", ".join("?" for _ in ids)
        rows = self.connection.execute(
            f"SELECT payload_json FROM {table} WHERE id IN ({marks})", ids
        )
        return [json.loads(row["payload_json"]) for row in rows]

    def next_session_pulse(self, profile_id: str) -> CuriosityPulse | None:
        """Advance a durable local queue; no ranking, parsing, or network work occurs here."""
        with self.transaction(immediate=True) as connection:
            session = connection.execute(
                """SELECT id, position FROM sessions WHERE profile_id=? AND status IN ('created', 'active')
                   ORDER BY started_at DESC LIMIT 1""",
                (profile_id,),
            ).fetchone()
            if session is None:
                return None
            row = connection.execute(
                """SELECT p.payload_json FROM session_cards sc JOIN pulses p ON p.card_id=sc.card_id
                   WHERE sc.session_id=? AND sc.ordinal >= ? ORDER BY sc.ordinal LIMIT 1""",
                (session["id"], session["position"]),
            ).fetchone()
            if row is None:
                connection.execute(
                    "UPDATE sessions SET status='completed' WHERE id=?", (session["id"],)
                )
                return None
            connection.execute(
                "UPDATE sessions SET position=position+1, status='active' WHERE id=?",
                (session["id"],),
            )
        return CuriosityPulse.model_validate_json(row["payload_json"])

    def current_session_pulse(self, profile_id: str) -> CuriosityPulse | None:
        """Return the queued item without changing durable state.

        The terminal renderer calls this before writing.  A crash after the write
        but before acknowledgement may repeat one fact, which is preferable to
        silently losing an exposure. Queued items whose pulse was invalidated
        (removed source or superseded build) are skipped by advancing position.
        """
        with self.transaction(immediate=True) as connection:
            session = connection.execute(
                """SELECT id, position FROM sessions WHERE profile_id=? AND status IN ('created', 'active')
                   ORDER BY started_at DESC LIMIT 1""",
                (profile_id,),
            ).fetchone()
            if session is None:
                return None
            while True:
                row = connection.execute(
                    """SELECT sc.ordinal, p.payload_json FROM session_cards sc
                       LEFT JOIN pulses p ON p.card_id=sc.card_id
                       WHERE sc.session_id=? AND sc.ordinal=?""",
                    (session["id"], session["position"]),
                ).fetchone()
                if row is None or row["payload_json"] is None:
                    # Invalidated item: skip it and continue; mark done when past the end.
                    next_ordinal = connection.execute(
                        "SELECT 1 FROM session_cards WHERE session_id=? AND ordinal>=? LIMIT 1",
                        (session["id"], int(session["position"]) + 1),
                    ).fetchone()
                    if next_ordinal is None:
                        connection.execute(
                            "UPDATE sessions SET status='completed' WHERE id=?",
                            (session["id"],),
                        )
                        return None
                    connection.execute(
                        "UPDATE sessions SET position=?, status='active' WHERE id=?",
                        (int(session["position"]) + 1, session["id"]),
                    )
                    session = dict(session)
                    session["position"] = int(session["position"]) + 1
                    continue
                return CuriosityPulse.model_validate_json(row["payload_json"])
        return None

    def record_displayed_pulse(self, profile_id: str, pulse: CuriosityPulse, *, at: datetime) -> bool:
        """Atomically acknowledge one rendered fact and its durable exposure."""
        with self.transaction(immediate=True) as connection:
            session = connection.execute(
                """SELECT id, position FROM sessions WHERE profile_id=? AND status IN ('created', 'active')
                   ORDER BY started_at DESC LIMIT 1""",
                (profile_id,),
            ).fetchone()
            if session is None:
                return False
            expected = connection.execute(
                "SELECT card_id FROM session_cards WHERE session_id=? AND ordinal=?",
                (session["id"], session["position"]),
            ).fetchone()
            if expected is None or expected["card_id"] != pulse.card_id:
                return False
            exposure = Exposure(
                id=deterministic_id("exposure", session["id"], str(session["position"])),
                profile_id=profile_id,
                card_id=pulse.card_id,
                exposed_at=at,
                outcome="shown",
                provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
            )
            connection.execute(
                """INSERT INTO exposures(id, profile_id, card_id, exposed_at, outcome, provenance, payload_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT(id) DO NOTHING""",
                (exposure.id, exposure.profile_id, exposure.card_id, _timestamp(at), exposure.outcome,
                 exposure.provenance, exposure.model_dump_json()),
            )
            position = int(session["position"]) + 1
            remaining = connection.execute(
                "SELECT 1 FROM session_cards WHERE session_id=? AND ordinal>=? LIMIT 1",
                (session["id"], position),
            ).fetchone()
            connection.execute(
                "UPDATE sessions SET position=?, status=? WHERE id=?",
                (position, "active" if remaining else "completed", session["id"]),
            )
        return True

    def put_exposure(self, exposure: Exposure) -> bool:
        return self._insert(
            "exposures",
            {
                "id": exposure.id,
                "profile_id": exposure.profile_id,
                "card_id": exposure.card_id,
                "exposed_at": _timestamp(exposure.exposed_at),
                "outcome": exposure.outcome,
                "provenance": exposure.provenance,
                "payload_json": exposure.model_dump_json(),
            },
        )

    def recent_exposures(
        self, profile_id: str, *, since: str | None = None, limit: int = 5000
    ) -> list[dict[str, Any]]:
        """Bounded, most-recent-first exposure history for one profile, optionally
        restricted to exposures at or after an ISO timestamp (the cooldown window)."""
        if since:
            rows = self.connection.execute(
                """SELECT e.card_id, p.fact_fingerprint AS fingerprint, p.source_id, e.exposed_at,
                   json_extract(p.payload_json, '$.topics[0]') AS topic,
                   fi.fact_text
                   FROM exposures e
                   JOIN pulses p ON p.card_id = e.card_id
                   LEFT JOIN fact_index fi ON fi.pulse_id = p.id
                   WHERE e.profile_id=? AND e.exposed_at >= ?
                   ORDER BY e.exposed_at DESC LIMIT ?""",
                (profile_id, since, limit),
            )
        else:
            rows = self.connection.execute(
                """SELECT e.card_id, p.fact_fingerprint AS fingerprint, p.source_id, e.exposed_at,
                   json_extract(p.payload_json, '$.topics[0]') AS topic,
                   fi.fact_text
                   FROM exposures e
                   JOIN pulses p ON p.card_id = e.card_id
                   LEFT JOIN fact_index fi ON fi.pulse_id = p.id
                   WHERE e.profile_id=? ORDER BY e.exposed_at DESC LIMIT ?""",
                (profile_id, limit),
            )
        return [dict(row) for row in rows]

    def fact_exists(
        self,
        fingerprint: str,
        *,
        exclude_pulse_id: str | None = None,
        exclude_source_id: str | None = None,
    ) -> bool:
        """Stage 1 firewall: an exact normalized fact already exists."""
        if exclude_pulse_id and exclude_source_id:
            row = self.connection.execute(
                "SELECT 1 FROM fact_index WHERE fingerprint=? AND pulse_id<>? AND source_id<>? LIMIT 1",
                (fingerprint, exclude_pulse_id, exclude_source_id),
            ).fetchone()
        elif exclude_pulse_id:
            row = self.connection.execute(
                "SELECT 1 FROM fact_index WHERE fingerprint=? AND pulse_id<>? LIMIT 1",
                (fingerprint, exclude_pulse_id),
            ).fetchone()
        elif exclude_source_id:
            row = self.connection.execute(
                "SELECT 1 FROM fact_index WHERE fingerprint=? AND source_id<>? LIMIT 1",
                (fingerprint, exclude_source_id),
            ).fetchone()
        else:
            row = self.connection.execute(
                "SELECT 1 FROM fact_index WHERE fingerprint=? LIMIT 1", (fingerprint,)
            ).fetchone()
        return row is not None

    def shortlist_fact_rows(
        self, terms: str, *, limit: int = 20, exclude_source_id: str | None = None
    ) -> list[tuple[str, str]]:
        """Stage 2 firewall: FTS5 shortlist of candidate facts sharing significant terms."""
        if not terms:
            return []
        try:
            if exclude_source_id:
                rows = self.connection.execute(
                    """SELECT fi.pulse_id, fi.fact_text
                       FROM fact_index_fts f JOIN fact_index fi ON fi.rowid = f.rowid
                       WHERE fact_index_fts MATCH ? AND fi.source_id<>?
                       ORDER BY bm25(fact_index_fts) LIMIT ?""",
                    (terms, exclude_source_id, limit),
                ).fetchall()
            else:
                rows = self.connection.execute(
                    """SELECT fi.pulse_id, fi.fact_text
                       FROM fact_index_fts f JOIN fact_index fi ON fi.rowid = f.rowid
                       WHERE fact_index_fts MATCH ?
                       ORDER BY bm25(fact_index_fts) LIMIT ?""",
                    (terms, limit),
                ).fetchall()
        except sqlite3.OperationalError:
            return []
        return [(str(row["pulse_id"]), str(row["fact_text"])) for row in rows]

    def remaining_playback_count(self, profile_id: str) -> int:
        row = self.connection.execute(
            """SELECT COUNT(*) AS remaining FROM session_cards sc
               JOIN (SELECT id, position FROM sessions
                     WHERE profile_id=? AND status IN ('created', 'active')
                     ORDER BY started_at DESC LIMIT 1) s ON s.id = sc.session_id
               WHERE sc.ordinal >= s.position""",
            (profile_id,),
        ).fetchone()
        return int(row["remaining"]) if row else 0

    def queued_card_ids(self, profile_id: str) -> frozenset[str]:
        rows = self.connection.execute(
            """SELECT sc.card_id FROM session_cards sc
               JOIN sessions s ON s.id = sc.session_id
               WHERE s.profile_id=? AND s.status IN ('created', 'active')""",
            (profile_id,),
        )
        return frozenset(str(row["card_id"]) for row in rows)

    def active_session_id(self, profile_id: str) -> str | None:
        row = self.connection.execute(
            """SELECT id FROM sessions WHERE profile_id=? AND status IN ('created', 'active')
               ORDER BY started_at DESC LIMIT 1""",
            (profile_id,),
        ).fetchone()
        return str(row["id"]) if row else None

    def append_session_cards(
        self, session_id: str, cards: Sequence[tuple[str, str, str]]
    ) -> None:
        """Extend a durable session with more queued items for continuous playback."""
        with self.transaction(immediate=True) as connection:
            start = connection.execute(
                "SELECT COALESCE(MAX(ordinal), -1) FROM session_cards WHERE session_id=?",
                (session_id,),
            ).fetchone()[0]
            connection.executemany(
                """INSERT INTO session_cards(session_id, card_id, ordinal, reason, fingerprint)
                   VALUES (?, ?, ?, ?, ?) ON CONFLICT(session_id, card_id) DO NOTHING""",
                (
                    (session_id, card_id, int(start) + 1 + index, reason, fingerprint)
                    for index, (card_id, reason, fingerprint) in enumerate(cards)
                ),
            )

    def put_harness_event(self, event: HarnessEvent) -> bool:
        return self._insert(
            "harness_events",
            {
                "id": event.id,
                "adapter": str(event.details.get("adapter", "unknown")),
                "event_type": event.event_type,
                "occurred_at": _timestamp(event.occurred_at),
                "payload_json": event.model_dump_json(),
            },
        )

    def get_ambient_state(self) -> tuple[str, str] | None:
        row = self.connection.execute(
            "SELECT state, updated_at FROM ambient_state WHERE id=1"
        ).fetchone()
        return (str(row["state"]), str(row["updated_at"])) if row else None

    def put_ambient_state(self, state: str, *, at: datetime) -> None:
        with self.transaction(immediate=True) as connection:
            connection.execute(
                """INSERT INTO ambient_state(id, state, updated_at) VALUES (1, ?, ?)
                   ON CONFLICT(id) DO UPDATE SET state=excluded.state,
                   updated_at=excluded.updated_at""",
                (state, _timestamp(at)),
            )

    def start_run_summary(self, run_id: str, *, at: datetime) -> None:
        with self.transaction(immediate=True) as connection:
            connection.execute(
                """INSERT INTO run_summaries(run_id, started_at, status) VALUES (?, ?, 'running')
                   ON CONFLICT(run_id) DO NOTHING""",
                (run_id, _timestamp(at)),
            )

    def finish_run_summary(
        self,
        run_id: str,
        *,
        status: str,
        counters: dict[str, int | float],
        at: datetime,
        detail: str = "",
    ) -> None:
        columns = {
            "sources",
            "fetched",
            "reused",
            "reparsed",
            "skipped",
            "candidates",
            "verified",
            "pulses_built",
            "rejected",
            "duplicates_suppressed",
            "model_calls",
            "cached_hits",
            "model_failures",
            "budget_exhausted",
            "http_fetches",
            "http_cache_hits",
            "bytes_downloaded",
            "retries",
            "failures",
            "elapsed_ms",
            "ingest_elapsed_ms",
            "parser_elapsed_ms",
        }
        known = {key: counters[key] for key in columns if key in counters}
        sets = ", ".join(f"{key}=?" for key in known)
        values = [known[key] for key in known]
        with self.transaction(immediate=True) as connection:
            connection.execute(
                f"UPDATE run_summaries SET status=?, finished_at=?, detail=?, {sets} WHERE run_id=?",
                (status, _timestamp(at), detail, *values, run_id),
            )

    def get_last_run_summary(self) -> dict[str, Any] | None:
        row = self.connection.execute(
            "SELECT * FROM run_summaries ORDER BY started_at DESC, run_id DESC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None

    def list_run_summaries(self, *, limit: int = 20) -> list[dict[str, Any]]:
        rows = self.connection.execute(
            "SELECT * FROM run_summaries ORDER BY started_at DESC LIMIT ?", (int(limit),)
        )
        return [dict(row) for row in rows]

    def put_session(
        self,
        session: PlaybackSession,
        *,
        generation: int = 0,
        reasons: Sequence[str] | None = None,
        fingerprints: Sequence[str] | None = None,
    ) -> bool:
        inserted = self._insert(
            "sessions",
            {
                "id": session.id,
                "profile_id": session.profile_id,
                "status": session.status,
                "started_at": _timestamp(session.started_at),
                "ended_at": _timestamp(session.ended_at) if session.ended_at else None,
                "provenance": session.provenance,
                "payload_json": session.model_dump_json(),
            },
        )
        if inserted:
            with self.transaction(immediate=True) as connection:
                connection.execute(
                    "UPDATE sessions SET generation=? WHERE id=?", (generation, session.id)
                )
                reasons = reasons or ("",) * len(session.card_ids)
                fingerprints = fingerprints or ("",) * len(session.card_ids)
                connection.executemany(
                    "INSERT INTO session_cards(session_id, card_id, ordinal, reason, fingerprint) VALUES (?, ?, ?, ?, ?)",
                    (
                        (session.id, card_id, ordinal, reason, fingerprint)
                        for ordinal, (card_id, reason, fingerprint) in enumerate(
                            zip(session.card_ids, reasons, fingerprints, strict=True)
                        )
                    ),
                )
        return inserted

    def search_documents(self, query: str, *, limit: int = 20) -> list[SourceDocument]:
        rows = self.connection.execute(
            """SELECT d.payload_json FROM documents_fts f
               JOIN documents d ON d.rowid = f.rowid WHERE documents_fts MATCH ? LIMIT ?""",
            (query, limit),
        )
        return [SourceDocument.model_validate_json(row["payload_json"]) for row in rows]

    def search_chunks(self, query: str, *, limit: int = 20) -> list[Chunk]:
        rows = self.connection.execute(
            """SELECT c.payload_json FROM chunks_fts f
               JOIN chunks c ON c.rowid = f.rowid WHERE chunks_fts MATCH ? LIMIT ?""",
            (query, limit),
        )
        return [Chunk.model_validate_json(row["payload_json"]) for row in rows]

    def put_cache(
        self,
        *,
        cache_key: str,
        content_sha256: str,
        fetched_at: datetime,
        parser_version: str,
        etag: str | None = None,
        last_modified: str | None = None,
        metadata: dict[str, str] | None = None,
        document_id: str | None = None,
        raw_bytes: bytes | None = None,
    ) -> None:
        with self.transaction(immediate=True) as connection:
            connection.execute(
                """INSERT INTO caches(cache_key, content_sha256, etag, last_modified, fetched_at, parser_version, metadata_json, document_id, raw_bytes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(cache_key) DO UPDATE SET content_sha256=excluded.content_sha256, etag=excluded.etag,
                   last_modified=excluded.last_modified, fetched_at=excluded.fetched_at, parser_version=excluded.parser_version,
                   metadata_json=excluded.metadata_json, document_id=excluded.document_id, raw_bytes=excluded.raw_bytes""",
                (
                    cache_key,
                    content_sha256,
                    etag,
                    last_modified,
                    _timestamp(fetched_at),
                    parser_version,
                    json.dumps(metadata or {}, sort_keys=True),
                    document_id,
                    raw_bytes,
                ),
            )

    def get_cache(self, cache_key: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            """SELECT content_sha256, etag, last_modified, fetched_at, parser_version, metadata_json, document_id, raw_bytes
               FROM caches WHERE cache_key = ?""",
            (cache_key,),
        ).fetchone()
        if row is None:
            return None
        return {
            "content_sha256": str(row["content_sha256"]),
            "etag": row["etag"],
            "last_modified": row["last_modified"],
            "fetched_at": str(row["fetched_at"]),
            "parser_version": str(row["parser_version"]),
            "metadata": json.loads(row["metadata_json"]),
            "document_id": row["document_id"],
            "raw_bytes": row["raw_bytes"],
        }

    def get_stage_key(self, source_id: str) -> dict[str, str] | None:
        row = self.connection.execute(
            """SELECT document_id, parser_version, document_key, stage_key, built_at
               FROM stage_keys WHERE source_id = ?""",
            (source_id,),
        ).fetchone()
        return dict(row) if row else None

    def put_stage_key(
        self,
        *,
        source_id: str,
        document_id: str,
        parser_version: str,
        document_key: str,
        stage_key: str,
    ) -> None:
        with self.transaction(immediate=True) as connection:
            connection.execute(
                """INSERT INTO stage_keys(source_id, document_id, parser_version, document_key, stage_key, built_at)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT(source_id) DO UPDATE SET document_id=excluded.document_id,
                   parser_version=excluded.parser_version, document_key=excluded.document_key,
                   stage_key=excluded.stage_key, built_at=excluded.built_at""",
                (
                    source_id,
                    document_id,
                    parser_version,
                    document_key,
                    stage_key,
                    _timestamp(),
                ),
            )

    def get_adapter_state(self, adapter_name: str) -> dict[str, Any]:
        row = self.connection.execute(
            "SELECT state_json FROM adapter_state WHERE adapter_name=?", (adapter_name,)
        ).fetchone()
        return json.loads(row["state_json"]) if row else {}

    def set_adapter_state(self, adapter_name: str, state: dict[str, Any]) -> None:
        with self.transaction(immediate=True) as connection:
            connection.execute(
                """INSERT INTO adapter_state(adapter_name, state_json, updated_at) VALUES (?, ?, ?)
                   ON CONFLICT(adapter_name) DO UPDATE SET state_json=excluded.state_json,
                   updated_at=excluded.updated_at""",
                (adapter_name, json.dumps(state, sort_keys=True), _timestamp()),
            )

    def put_discovery_candidate(self, *, provider: str, record: SourceRecord) -> bool:
        return self._insert(
            "discovery_candidates",
            {
                "id": record.id,
                "provider": provider,
                "canonical_locator": record.canonical_locator,
                "identity_key": source_identity_key(record),
                "source_type": record.source_type,
                "title": record.title,
                "metadata_json": json.dumps(record.metadata, sort_keys=True),
                "payload_json": record.model_dump_json(),
                "discovered_at": _timestamp(),
            },
        )

    def candidate_conflicts(self, *, locator: str, identity_key: str) -> bool:
        """True when a pending candidate already proves the same work."""
        row = self.connection.execute(
            """SELECT 1 FROM discovery_candidates
               WHERE canonical_locator = ? OR identity_key = ? LIMIT 1""",
            (locator, identity_key),
        ).fetchone()
        return row is not None

    def list_discovery_candidates(self) -> list[dict[str, Any]]:
        rows = self.connection.execute(
            """SELECT id, provider, canonical_locator, identity_key, source_type, title, payload_json, discovered_at
               FROM discovery_candidates ORDER BY discovered_at, id"""
        )
        return [dict(row) for row in rows]

    def get_discovery_candidate(self, candidate_id: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            """SELECT id, provider, canonical_locator, identity_key, source_type, title, payload_json, discovered_at
               FROM discovery_candidates WHERE id = ?""",
            (candidate_id,),
        ).fetchone()
        return dict(row) if row else None

    def remove_discovery_candidate(self, candidate_id: str) -> bool:
        with self.transaction(immediate=True) as connection:
            result = connection.execute(
                "DELETE FROM discovery_candidates WHERE id=?", (candidate_id,)
            )
        return result.rowcount == 1

    def record_model_usage(
        self,
        *,
        run_id: str,
        task_type: str,
        model_id: str,
        tier: str,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int,
        latency_ms: float,
        cache_hit: bool,
        failed: bool,
        escalation_reason: str | None,
        source_id: str | None,
        document_id: str | None,
    ) -> None:
        self._usage_seq += 1
        usage_id = deterministic_id("usage", run_id, str(self._usage_seq))
        with self.transaction(immediate=True) as connection:
            connection.execute(
                """INSERT INTO model_usage(id, run_id, occurred_at, task_type, model_id, tier,
                   input_tokens, output_tokens, cached_tokens, latency_ms, cache_hit, failed,
                   escalation_reason, source_id, document_id, metadata_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '{}')""",
                (
                    usage_id,
                    run_id,
                    _timestamp(),
                    task_type,
                    model_id,
                    tier,
                    int(input_tokens),
                    int(output_tokens),
                    int(cached_tokens),
                    float(latency_ms),
                    int(cache_hit),
                    int(failed),
                    escalation_reason,
                    source_id,
                    document_id,
                ),
            )

    def model_usage_summary(self, run_id: str) -> list[dict[str, Any]]:
        rows = self.connection.execute(
            """SELECT task_type, model_id, tier,
               COUNT(*) AS calls,
               SUM(cache_hit) AS cache_hits,
               SUM(failed) AS failures,
               SUM(input_tokens) AS input_tokens,
               SUM(output_tokens) AS output_tokens,
               SUM(cached_tokens) AS cached_tokens,
               SUM(latency_ms) AS latency_ms
               FROM model_usage WHERE run_id=? GROUP BY task_type, model_id, tier
               ORDER BY task_type, model_id, tier""",
            (run_id,),
        )
        return [dict(row) for row in rows]

    def get_model_cache(self, cache_key: str) -> dict[str, object] | None:
        row = self.connection.execute(
            """SELECT task_type, model_id, contract_version, result_json, cached_tokens
               FROM model_cache WHERE cache_key=?""",
            (cache_key,),
        ).fetchone()
        return dict(row) if row else None

    def put_model_cache(
        self,
        *,
        cache_key: str,
        task_type: str,
        model_id: str,
        contract_version: str,
        result_json: str,
        cached_tokens: int,
    ) -> None:
        with self.transaction(immediate=True) as connection:
            connection.execute(
                """INSERT INTO model_cache(cache_key, task_type, model_id, contract_version,
                   result_json, cached_tokens, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(cache_key) DO UPDATE SET result_json=excluded.result_json,
                   cached_tokens=excluded.cached_tokens, created_at=excluded.created_at""",
                (
                    cache_key,
                    task_type,
                    model_id,
                    contract_version,
                    result_json,
                    int(cached_tokens),
                    _timestamp(),
                ),
            )

    def record_build_event(
        self,
        *,
        run_id: str,
        source_id: str | None,
        document_id: str | None,
        candidate_id: str,
        escalation_reason: str | None,
        outcome: str,
        detail: str,
    ) -> None:
        self._usage_seq += 1
        event_id = deterministic_id("event", run_id, str(self._usage_seq))
        with self.transaction(immediate=True) as connection:
            connection.execute(
                """INSERT INTO build_events(id, run_id, occurred_at, source_id, document_id,
                   candidate_id, escalation_reason, outcome, detail)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    event_id,
                    run_id,
                    _timestamp(),
                    source_id,
                    document_id,
                    candidate_id,
                    escalation_reason,
                    outcome,
                    detail,
                ),
            )

    def create_job(
        self, *, job_id: str, idempotency_key: str, stage: str, now: datetime | None = None
    ) -> str:
        timestamp = _timestamp(now)
        with self.transaction(immediate=True) as connection:
            connection.execute(
                """INSERT INTO jobs(id, idempotency_key, stage, status, next_attempt_at, created_at, updated_at)
                   VALUES (?, ?, ?, 'pending', ?, ?, ?) ON CONFLICT(idempotency_key) DO NOTHING""",
                (job_id, idempotency_key, stage, timestamp, timestamp, timestamp),
            )
            row = connection.execute(
                "SELECT id FROM jobs WHERE idempotency_key = ?", (idempotency_key,)
            ).fetchone()
        return str(row["id"])

    def claim_job(
        self, *, worker_id: str, lease_seconds: int = 60, now: datetime | None = None
    ) -> ClaimedJob | None:
        current = now or datetime.now(UTC)
        now_text, expiry = (
            _timestamp(current),
            _timestamp(current + timedelta(seconds=lease_seconds)),
        )
        with self.transaction(immediate=True) as connection:
            row = connection.execute(
                """SELECT * FROM jobs WHERE status = 'pending' AND next_attempt_at <= ?
                   ORDER BY created_at, id LIMIT 1""",
                (now_text,),
            ).fetchone()
            if row is None:
                return None
            updated = connection.execute(
                """UPDATE jobs SET status='running', attempts=attempts+1, lease_owner=?, lease_expires_at=?, updated_at=?
                   WHERE id=? AND status='pending'""",
                (worker_id, expiry, now_text, row["id"]),
            )
            if updated.rowcount != 1:
                return None
            return ClaimedJob(
                row["id"],
                row["idempotency_key"],
                row["stage"],
                row["attempts"] + 1,
                row["input_budget"],
                row["output_budget"],
            )

    def claim_job_by_id(
        self, *, job_id: str, worker_id: str, lease_seconds: int = 3600, now: datetime | None = None
    ) -> bool:
        """Claim one specific job by id (used by the refresh run owner).

        Unlike ``claim_job`` this never claims another stage's pending work, so
        an interrupted refresh can be resumed without disturbing other jobs.
        """
        current = now or datetime.now(UTC)
        now_text, expiry = (
            _timestamp(current),
            _timestamp(current + timedelta(seconds=lease_seconds)),
        )
        with self.transaction(immediate=True) as connection:
            updated = connection.execute(
                """UPDATE jobs SET status='running', attempts=attempts+1, lease_owner=?, lease_expires_at=?, updated_at=?
                   WHERE id=? AND status='pending'""",
                (worker_id, expiry, now_text, job_id),
            )
        return updated.rowcount == 1

    def complete_job(
        self,
        *,
        job_id: str,
        worker_id: str,
        input_budget: int = 0,
        output_budget: int = 0,
        now: datetime | None = None,
    ) -> bool:
        with self.transaction(immediate=True) as connection:
            result = connection.execute(
                """UPDATE jobs SET status='succeeded', lease_owner=NULL, lease_expires_at=NULL,
                   input_budget=input_budget + ?, output_budget=output_budget + ?, updated_at=?
                   WHERE id=? AND status='running' AND lease_owner=?""",
                (input_budget, output_budget, _timestamp(now), job_id, worker_id),
            )
        return result.rowcount == 1

    def fail_job(
        self, *, job_id: str, worker_id: str, error_class: str, detail: str, retry_at: datetime
    ) -> bool:
        with self.transaction(immediate=True) as connection:
            result = connection.execute(
                """UPDATE jobs SET status='pending', lease_owner=NULL, lease_expires_at=NULL, error_class=?, error_detail=?,
                   next_attempt_at=?, updated_at=? WHERE id=? AND status='running' AND lease_owner=?""",
                (error_class, detail, _timestamp(retry_at), _timestamp(), job_id, worker_id),
            )
        return result.rowcount == 1

    def recover_abandoned_jobs(self, *, now: datetime | None = None) -> int:
        timestamp = _timestamp(now)
        with self.transaction(immediate=True) as connection:
            result = connection.execute(
                """UPDATE jobs SET status='pending', lease_owner=NULL, lease_expires_at=NULL, updated_at=?
                   WHERE status='running' AND lease_expires_at <= ?""",
                (timestamp, timestamp),
            )
        return result.rowcount

    def diagnostics(self, *, now: datetime | None = None) -> StoreDiagnostic:
        invalid: list[tuple[str, str]] = []
        for table in (
            "sources",
            "documents",
            "chunks",
            "evidence",
            "atoms",
            "cards",
            "pulses",
            "profiles",
            "exposures",
            "sessions",
        ):
            for row in self.connection.execute(f"SELECT id, payload_json FROM {table}"):
                try:
                    json.loads(row["payload_json"])
                except json.JSONDecodeError:
                    invalid.append((table, str(row["id"])))
        foreign_keys = tuple(
            tuple(row) for row in self.connection.execute("PRAGMA foreign_key_check")
        )
        recoverable = self.connection.execute(
            "SELECT COUNT(*) FROM jobs WHERE status='running' AND lease_expires_at <= ?",
            (_timestamp(now),),
        ).fetchone()[0]
        integrity = self.connection.execute("PRAGMA integrity_check").fetchone()[0]
        return StoreDiagnostic(
            self.schema_version, str(integrity), foreign_keys, tuple(invalid), int(recoverable)
        )


class SimilarityIndex:
    """Optional vector capability. SQLite FTS remains usable without an implementation."""

    def search(self, text: str, *, limit: int) -> Sequence[str]:
        raise NotImplementedError("Similarity indexing is optional and not configured")
