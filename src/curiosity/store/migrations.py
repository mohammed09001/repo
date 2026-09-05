"""Append-only SQLite schema migrations owned by the local store."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    statements: tuple[str, ...]
    foreign_keys_off: bool = False


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
    Migration(
        3,
        "playable_pulses",
        (
            """
            CREATE TABLE pulses (
                id TEXT PRIMARY KEY,
                card_id TEXT NOT NULL UNIQUE REFERENCES cards(id) ON DELETE RESTRICT,
                atom_id TEXT NOT NULL REFERENCES atoms(id) ON DELETE RESTRICT,
                display_fact TEXT NOT NULL,
                source_id TEXT NOT NULL REFERENCES sources(id) ON DELETE RESTRICT,
                document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE RESTRICT,
                verified_at TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """,
            "CREATE INDEX pulses_source_idx ON pulses(source_id, document_id)",
        ),
    ),
    Migration(
        4,
        "session_queue_position",
        ("ALTER TABLE sessions ADD COLUMN position INTEGER NOT NULL DEFAULT 0",),
    ),
    Migration(
        5,
        "harness_events",
        (
            """
            CREATE TABLE harness_events (
                id TEXT PRIMARY KEY,
                adapter TEXT NOT NULL,
                event_type TEXT NOT NULL,
                occurred_at TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """,
            "CREATE INDEX harness_events_adapter_time_idx ON harness_events(adapter, occurred_at)",
        ),
    ),
    Migration(
        6,
        "pulse_verification",
        ("ALTER TABLE pulses ADD COLUMN verification_json TEXT NOT NULL DEFAULT '{}'",),
    ),
    Migration(
        7,
        "incremental_build_graph",
        (
            # Rebuild documents without a unique raw-content hash so a changed
            # parser version can produce a distinct document for the same bytes.
            """
            CREATE TABLE documents_new (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
                content_sha256 TEXT NOT NULL,
                raw_text TEXT NOT NULL,
                captured_at TEXT NOT NULL,
                provenance TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """,
            """
            INSERT INTO documents_new (rowid, id, source_id, content_sha256, raw_text, captured_at, provenance, payload_json)
            SELECT rowid, id, source_id, content_sha256, raw_text, captured_at, provenance, payload_json FROM documents
            """,
            "DROP TABLE documents",
            "ALTER TABLE documents_new RENAME TO documents",
            "CREATE INDEX documents_source_id_idx ON documents(source_id)",
            "CREATE INDEX documents_content_sha_idx ON documents(content_sha256)",
            # The FTS index stores document rowids, which were preserved above.
            # Recreate the content sync triggers that DROP TABLE removed.
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
            # Stable identity for conservative cross-provider source dedupe.
            "ALTER TABLE sources ADD COLUMN identity_key TEXT",
            # Cache stores the exact document and raw bytes needed for a
            # parser-version-triggered re-parse on an unchanged 304 response.
            "ALTER TABLE caches ADD COLUMN document_id TEXT",
            "ALTER TABLE caches ADD COLUMN raw_bytes BLOB",
            # Untrusted pending discovery results; never part of the knowledge
            # pipeline until the user explicitly registers them as sources.
            """
            CREATE TABLE discovery_candidates (
                id TEXT PRIMARY KEY,
                provider TEXT NOT NULL,
                canonical_locator TEXT NOT NULL UNIQUE,
                identity_key TEXT NOT NULL,
                source_type TEXT NOT NULL,
                title TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                discovered_at TEXT NOT NULL
            )
            """,
            "CREATE INDEX discovery_candidates_provider_time_idx ON discovery_candidates(provider, discovered_at)",
            # Current eligibility projection per source. Pulses whose document or
            # stage key does not match this row are historical, not eligible.
            """
            CREATE TABLE stage_keys (
                source_id TEXT PRIMARY KEY REFERENCES sources(id) ON DELETE CASCADE,
                document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE RESTRICT,
                parser_version TEXT NOT NULL,
                document_key TEXT NOT NULL,
                stage_key TEXT NOT NULL,
                built_at TEXT NOT NULL
            )
            """,
            "ALTER TABLE pulses ADD COLUMN stage_key TEXT NOT NULL DEFAULT ''",
        ),
        foreign_keys_off=True,
    ),
    Migration(
        8,
        "model_economy",
        (
            # Model-work ledger: one row per model call or cache hit so a refresh
            # run can be audited without building a billing platform.
            """
            CREATE TABLE model_usage (
                id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                occurred_at TEXT NOT NULL,
                task_type TEXT NOT NULL,
                model_id TEXT NOT NULL,
                tier TEXT NOT NULL,
                input_tokens INTEGER NOT NULL DEFAULT 0,
                output_tokens INTEGER NOT NULL DEFAULT 0,
                cached_tokens INTEGER NOT NULL DEFAULT 0,
                latency_ms REAL NOT NULL DEFAULT 0,
                cache_hit INTEGER NOT NULL DEFAULT 0,
                failed INTEGER NOT NULL DEFAULT 0,
                escalation_reason TEXT,
                source_id TEXT,
                document_id TEXT,
                metadata_json TEXT NOT NULL
            )
            """,
            "CREATE INDEX model_usage_run_idx ON model_usage(run_id, occurred_at)",
            # Semantic-safe local model cache. Identity excludes raw full prompts
            # and any secret-bearing payload; only validated results are stored.
            """
            CREATE TABLE model_cache (
                cache_key TEXT PRIMARY KEY,
                task_type TEXT NOT NULL,
                model_id TEXT NOT NULL,
                contract_version TEXT NOT NULL,
                result_json TEXT NOT NULL,
                cached_tokens INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """,
            # Per-candidate quality-lane outcomes (escalated/rejected/rebuilt)
            # so refresh diagnostics are auditable without mixing them into
            # token-accounting rows.
            """
            CREATE TABLE build_events (
                id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                occurred_at TEXT NOT NULL,
                source_id TEXT,
                document_id TEXT,
                candidate_id TEXT NOT NULL,
                escalation_reason TEXT,
                outcome TEXT NOT NULL,
                detail TEXT NOT NULL
            )
            """,
            "CREATE INDEX build_events_run_idx ON build_events(run_id, occurred_at)",
        ),
    ),
    Migration(
        9,
        "feed_intelligence",
        (
            # Claim fingerprint of the displayed fact for exact/near-duplicate
            # suppression and exposure cooldown keyed by idea, not card identity.
            "ALTER TABLE pulses ADD COLUMN fact_fingerprint TEXT NOT NULL DEFAULT ''",
            # Durable per-item diagnostics for continuous sequencing.
            "ALTER TABLE sessions ADD COLUMN generation INTEGER NOT NULL DEFAULT 0",
            "ALTER TABLE session_cards ADD COLUMN reason TEXT NOT NULL DEFAULT ''",
            "ALTER TABLE session_cards ADD COLUMN fingerprint TEXT NOT NULL DEFAULT ''",
            # Projection table for the Near-Duplicate Firewall: one row per pulse
            # fact, indexed by exact fingerprint and by FTS5 for shortlisting.
            """
            CREATE TABLE fact_index (
                pulse_id TEXT PRIMARY KEY REFERENCES pulses(id) ON DELETE CASCADE,
                card_id TEXT NOT NULL,
                source_id TEXT NOT NULL,
                fingerprint TEXT NOT NULL,
                fact_text TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """,
            "CREATE INDEX fact_index_fingerprint_idx ON fact_index(fingerprint)",
            "CREATE INDEX exposures_profile_time_idx ON exposures(profile_id, exposed_at)",
            "CREATE VIRTUAL TABLE fact_index_fts USING fts5(fact_text, content='fact_index', content_rowid='rowid')",
            """
            CREATE TRIGGER fact_index_ai AFTER INSERT ON fact_index BEGIN
                INSERT INTO fact_index_fts(rowid, fact_text) VALUES (new.rowid, new.fact_text);
            END
            """,
            """
            CREATE TRIGGER fact_index_ad AFTER DELETE ON fact_index BEGIN
                INSERT INTO fact_index_fts(fact_index_fts, rowid, fact_text)
                VALUES ('delete', old.rowid, old.fact_text);
            END
            """,
        ),
    ),
    Migration(
        10,
        "ambient_runtime_state",
        (
            # One derived ambient runtime state row: only the state value and the
            # transition timestamp needed for restart freshness and debounce.
            """
            CREATE TABLE ambient_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                state TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """,
        ),
    ),
    Migration(
        11,
        "refresh_run_ledger",
        (
            # One bounded summary row per refresh/build run. Aggregates only;
            # source bodies, prompts, and secrets are never stored here.
            """
            CREATE TABLE run_summaries (
                run_id TEXT PRIMARY KEY,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                status TEXT NOT NULL,
                sources INTEGER NOT NULL DEFAULT 0,
                fetched INTEGER NOT NULL DEFAULT 0,
                reused INTEGER NOT NULL DEFAULT 0,
                reparsed INTEGER NOT NULL DEFAULT 0,
                skipped INTEGER NOT NULL DEFAULT 0,
                candidates INTEGER NOT NULL DEFAULT 0,
                verified INTEGER NOT NULL DEFAULT 0,
                pulses_built INTEGER NOT NULL DEFAULT 0,
                rejected INTEGER NOT NULL DEFAULT 0,
                duplicates_suppressed INTEGER NOT NULL DEFAULT 0,
                model_calls INTEGER NOT NULL DEFAULT 0,
                cached_hits INTEGER NOT NULL DEFAULT 0,
                model_failures INTEGER NOT NULL DEFAULT 0,
                budget_exhausted INTEGER NOT NULL DEFAULT 0,
                http_fetches INTEGER NOT NULL DEFAULT 0,
                http_cache_hits INTEGER NOT NULL DEFAULT 0,
                bytes_downloaded INTEGER NOT NULL DEFAULT 0,
                retries INTEGER NOT NULL DEFAULT 0,
                failures INTEGER NOT NULL DEFAULT 0,
                elapsed_ms INTEGER NOT NULL DEFAULT 0,
                ingest_elapsed_ms INTEGER NOT NULL DEFAULT 0,
                parser_elapsed_ms REAL NOT NULL DEFAULT 0,
                detail TEXT NOT NULL DEFAULT ''
            )
            """,
            "CREATE INDEX run_summaries_started_idx ON run_summaries(started_at)",
        ),
    ),
    Migration(
        12,
        "session_queue_indexes",
        (
            # Hot playback queries select the current session by profile and
            # status on every display tick; the query plan otherwise scans the
            # whole sessions table with a temp B-tree sort.
            """
            CREATE INDEX sessions_profile_status_started_idx
            ON sessions(profile_id, status, started_at)
            """,
        ),
    ),
)

CURRENT_SCHEMA_VERSION = MIGRATIONS[-1].version
