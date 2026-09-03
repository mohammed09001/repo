from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

from curiosity import __version__
from curiosity.config.settings import capability_state, load_config
from curiosity.contracts.models import (
    ProvenanceClass,
    SourceRecord,
    SourceType,
    TrustClass,
    deterministic_id,
)
from curiosity.ingest.pipeline import IngestError, IngestionPipeline, UrllibFetcher
from curiosity.sources.adapters import canonicalize_url
from curiosity.store import LocalStore


def _sqlite_fts5_status() -> str:
    try:
        with sqlite3.connect(":memory:") as connection:
            connection.execute("CREATE VIRTUAL TABLE probe USING fts5(text)")
        return "available"
    except sqlite3.OperationalError:
        return "unavailable"


def _doctor(args: argparse.Namespace) -> int:
    config = load_config(
        cli={
            "config_path": args.config,
            "data_path": args.data_path,
            "feature_youtube": args.youtube,
            "feature_embeddings": args.embeddings,
            "feature_sqlite_vec": args.sqlite_vec,
            "feature_harness": args.harness,
        }
    )
    config.data_path.mkdir(parents=True, exist_ok=True)
    print(f"curiosity {__version__}")
    print(f"python {sys.version.split()[0]}")
    print(f"config_path {config.config_path}")
    print(f"data_path {config.data_path}")
    print(f"sqlite {sqlite3.sqlite_version}; fts5 {_sqlite_fts5_status()}")
    for name, state in capability_state(config).items():
        print(f"capability.{name} {state}")
    return 0


def _ingest(args: argparse.Namespace) -> int:
    config = load_config(cli={"data_path": args.data_path})
    locator = canonicalize_url(args.url)
    source = SourceRecord(
        id=deterministic_id("source", locator),
        source_type=SourceType.WEB,
        canonical_locator=locator,
        title=locator,
        trust=TrustClass.REMOTE_UNTRUSTED,
        provenance=ProvenanceClass.SOURCE,
        retrieved_at=datetime.now(UTC),
    )
    try:
        with LocalStore(config.data_path / "curiosity.db") as store:
            document, chunks, reused = IngestionPipeline(
                store, UrllibFetcher(), max_bytes=args.max_bytes, chunk_ceiling=args.chunk_ceiling
            ).ingest(source)
    except IngestError as error:
        print(f"ingest failed: {error}", file=sys.stderr)
        return 2
    print(f"{'reused' if reused else 'ingested'} {document.id} ({len(chunks)} chunks)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="curiosity", description="Local-first Curiosity Engine")
    subparsers = parser.add_subparsers(dest="command")
    doctor = subparsers.add_parser("doctor", help="report local setup and optional capabilities")
    doctor.add_argument("--config", type=Path, help="path to a TOML configuration file")
    doctor.add_argument("--data-path", type=Path, help="directory for local data")
    for name, help_text in (
        ("youtube", "enable the optional YouTube adapter"),
        ("embeddings", "enable optional embeddings"),
        ("sqlite-vec", "enable optional sqlite-vec"),
        ("harness", "enable optional harness integrations"),
    ):
        doctor.add_argument(
            f"--{name}",
            action=argparse.BooleanOptionalAction,
            default=None,
            help=help_text,
        )
    doctor.set_defaults(handler=_doctor)
    ingest = subparsers.add_parser("ingest", help="fetch, normalize, and chunk one explicit URL")
    ingest.add_argument("url")
    ingest.add_argument("--data-path", type=Path, help="directory for local data")
    ingest.add_argument("--max-bytes", type=int, default=2_000_000)
    ingest.add_argument("--chunk-ceiling", type=int, default=1_200)
    ingest.set_defaults(handler=_ingest)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "handler"):
        parser.print_help()
        return 0
    return args.handler(args)
