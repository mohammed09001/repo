"""Append-only SQLite schema migrations owned by the local store."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    statements: tuple[str, ...]


MIGRATIONS = (
    Migration(
        1,
        "source_documents",
        (
            """
            CREATE TABLE sources (
                id TEXT PRIMARY KEY,
                source_type TEXT NOT NULL,
                canonical_locator TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                trust TEXT NOT NULL,
                provenance TEXT NOT NULL,
                retrieved_at TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE documents (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
                content_sha256 TEXT NOT NULL UNIQUE,
                raw_text TEXT NOT NULL,
                captured_at TEXT NOT NULL,
                provenance TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """,
            "CREATE INDEX documents_source_id_idx ON documents(source_id)",
        ),
    ),
    Migration(
        2,
        "knowledge_jobs_search",
        (
            """
            CREATE TABLE chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                ordinal INTEGER NOT NULL,
                text TEXT NOT NULL,
                char_start INTEGER NOT NULL,
                char_end INTEGER NOT NULL,
                provenance TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                UNIQUE(document_id, ordinal),
                CHECK(char_end > char_start)
            )
            """,
            """
            CREATE TABLE evidence (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL REFERENCES sources(id) ON DELETE RESTRICT,
                document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE RESTRICT,
                chunk_id TEXT REFERENCES chunks(id) ON DELETE RESTRICT,
                quote TEXT NOT NULL,
                support TEXT NOT NULL,
                provenance TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE atoms (
                id TEXT PRIMARY KEY,
                statement TEXT NOT NULL,
                claim_status TEXT NOT NULL,
                provenance TEXT NOT NULL,
                created_at TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE cards (
                id TEXT PRIMARY KEY,
                card_type TEXT NOT NULL,
                prompt TEXT NOT NULL,
                provenance TEXT NOT NULL,
                created_at TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE profiles (
                id TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                provenance TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE exposures (
                id TEXT PRIMARY KEY,
                profile_id TEXT NOT NULL REFERENCES profiles(id) ON DELETE RESTRICT,
                card_id TEXT NOT NULL REFERENCES cards(id) ON DELETE RESTRICT,
                exposed_at TEXT NOT NULL,
                outcome TEXT NOT NULL,
                provenance TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE sessions (
                id TEXT PRIMARY KEY,
                profile_id TEXT NOT NULL REFERENCES profiles(id) ON DELETE RESTRICT,
                status TEXT NOT NULL,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                provenance TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE session_cards (
                session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                card_id TEXT NOT NULL REFERENCES cards(id) ON DELETE RESTRICT,
                ordinal INTEGER NOT NULL,
                PRIMARY KEY(session_id, card_id),
                UNIQUE(session_id, ordinal)
            )
            """,
            """
            CREATE TABLE jobs (
                id TEXT PRIMARY KEY,
                idempotency_key TEXT NOT NULL UNIQUE,
                stage TEXT NOT NULL,
                status TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0 CHECK(attempts >= 0),
                next_attempt_at TEXT NOT NULL,
                lease_owner TEXT,
                lease_expires_at TEXT,
                error_class TEXT,
                error_detail TEXT,
                input_budget INTEGER NOT NULL DEFAULT 0 CHECK(input_budget >= 0),
                output_budget INTEGER NOT NULL DEFAULT 0 CHECK(output_budget >= 0),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """,
            "CREATE INDEX jobs_claim_idx ON jobs(status, next_attempt_at, lease_expires_at)",
            """
            CREATE TABLE caches (
                cache_key TEXT PRIMARY KEY,
                content_sha256 TEXT NOT NULL,
                etag TEXT,
                last_modified TEXT,
                fetched_at TEXT NOT NULL,
                parser_version TEXT NOT NULL,
                metadata_json TEXT NOT NULL
            )
            """,
            "CREATE INDEX caches_content_hash_idx ON caches(content_sha256)",
            """
            CREATE TABLE adapter_state (
                adapter_name TEXT PRIMARY KEY,
                state_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """,
            "CREATE VIRTUAL TABLE documents_fts USING fts5(raw_text, content='documents', content_rowid='rowid')",
            "CREATE VIRTUAL TABLE chunks_fts USING fts5(text, content='chunks', content_rowid='rowid')",
            """
            CREATE TRIGGER documents_ai AFTER INSERT ON documents BEGIN
                INSERT INTO documents_fts(rowid, raw_text) VALUES (new.rowid, new.raw_text);
            END
            """,
            """
            CREATE TRIGGER documents_ad AFTER DELETE ON documents BEGIN
                INSERT INTO documents_fts(documents_fts, rowid, raw_text)
                VALUES ('delete', old.rowid, old.raw_text);
            END
            """,
            """
            CREATE TRIGGER chunks_ai AFTER INSERT ON chunks BEGIN
                INSERT INTO chunks_fts(rowid, text) VALUES (new.rowid, new.text);
            END
            """,
            """
            CREATE TRIGGER chunks_ad AFTER DELETE ON chunks BEGIN
                INSERT INTO chunks_fts(chunks_fts, rowid, text) VALUES ('delete', old.rowid, old.text);
            END
            """,
        ),
    ),
)

CURRENT_SCHEMA_VERSION = MIGRATIONS[-1].version
