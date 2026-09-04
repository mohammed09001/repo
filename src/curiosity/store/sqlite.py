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
        self.migrate()

    def close(self) -> None:
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
                "metadata_json": json.dumps(source.metadata, sort_keys=True),
                "payload_json": source.model_dump_json(),
            },
        )

    def put_document(self, document: SourceDocument) -> str:
        existing = self.connection.execute(
            "SELECT id FROM documents WHERE content_sha256 = ?", (document.content_sha256,)
        ).fetchone()
        if existing:
            return str(existing["id"])
        try:
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
        except sqlite3.IntegrityError:
            existing = self.connection.execute(
                "SELECT id FROM documents WHERE content_sha256 = ?", (document.content_sha256,)
            ).fetchone()
            if existing:
                return str(existing["id"])
            raise
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

    def put_pulse(self, pulse: CuriosityPulse, *, verification: dict[str, Any]) -> bool:
        return self._insert(
            "pulses",
            {
                "id": pulse.id,
                "card_id": pulse.card_id,
                "atom_id": pulse.atom_id,
                "display_fact": pulse.display_fact,
                "source_id": pulse.source_id,
                "document_id": pulse.document_id,
                "verified_at": _timestamp(pulse.verified_at),
                "verification_json": json.dumps(verification, sort_keys=True),
                "payload_json": pulse.model_dump_json(),
            },
        )

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
        silently losing an exposure.
        """
        session = self.connection.execute(
            """SELECT id, position FROM sessions WHERE profile_id=? AND status IN ('created', 'active')
               ORDER BY started_at DESC LIMIT 1""",
            (profile_id,),
        ).fetchone()
        if session is None:
            return None
        row = self.connection.execute(
            """SELECT p.payload_json FROM session_cards sc JOIN pulses p ON p.card_id=sc.card_id
               WHERE sc.session_id=? AND sc.ordinal=?""",
            (session["id"], session["position"]),
        ).fetchone()
        return CuriosityPulse.model_validate_json(row["payload_json"]) if row else None

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

    def put_session(self, session: PlaybackSession) -> bool:
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
                connection.executemany(
                    "INSERT INTO session_cards(session_id, card_id, ordinal) VALUES (?, ?, ?)",
                    (
                        (session.id, card_id, ordinal)
                        for ordinal, card_id in enumerate(session.card_ids)
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
    ) -> None:
        with self.transaction(immediate=True) as connection:
            connection.execute(
                """INSERT INTO caches(cache_key, content_sha256, etag, last_modified, fetched_at, parser_version, metadata_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(cache_key) DO UPDATE SET content_sha256=excluded.content_sha256, etag=excluded.etag,
                   last_modified=excluded.last_modified, fetched_at=excluded.fetched_at, parser_version=excluded.parser_version,
                   metadata_json=excluded.metadata_json""",
                (
                    cache_key,
                    content_sha256,
                    etag,
                    last_modified,
                    _timestamp(fetched_at),
                    parser_version,
                    json.dumps(metadata or {}, sort_keys=True),
                ),
            )

    def get_cache(self, cache_key: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            """SELECT content_sha256, etag, last_modified, fetched_at, parser_version, metadata_json
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
        }

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
