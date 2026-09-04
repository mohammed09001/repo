"""Terminal adapters for the canonical application facade."""

from __future__ import annotations

import argparse
import sqlite3
import sys
import time
from pathlib import Path

from curiosity import __version__
from curiosity.application import ApplicationError, CuriosityApplication
from curiosity.config.settings import capability_state, load_config
from curiosity.harness import (
    CAPABILITIES,
    install_claude,
    install_opencode,
    normalize,
    uninstall_claude,
    uninstall_opencode,
)
from curiosity.ingest.pipeline import IngestError
from curiosity.runtime import TerminalPlayback
from curiosity.store import LocalStore


def _app(args: argparse.Namespace) -> tuple[LocalStore, CuriosityApplication]:
    config = load_config(cli={"data_path": args.data_path})
    store = LocalStore(config.data_path / "curiosity.db")
    return store, CuriosityApplication(store)


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
    print(
        f"curiosity {__version__}\npython {sys.version.split()[0]}\nconfig_path {config.config_path}\ndata_path {config.data_path}"
    )
    try:
        with sqlite3.connect(":memory:") as connection:
            connection.execute("CREATE VIRTUAL TABLE probe USING fts5(text)")
        fts = "available"
    except sqlite3.OperationalError:
        fts = "unavailable"
    print(f"sqlite {sqlite3.sqlite_version}; fts5 {fts}")
    for name, state in capability_state(config).items():
        print(f"capability.{name} {state}")
    if args.deep:
        with LocalStore(config.data_path / "curiosity.db") as store:
            diagnostic = store.diagnostics()
            queue_ready = store.connection.execute(
                "SELECT COUNT(*) FROM sessions WHERE status IN ('created', 'active')"
            ).fetchone()[0]
            print(f"schema_version {diagnostic.schema_version}")
            print(f"database_integrity {diagnostic.integrity_check}")
            print(f"foreign_key_violations {len(diagnostic.foreign_key_violations)}")
            print(f"invalid_payload_rows {len(diagnostic.invalid_payload_rows)}")
            print(f"recoverable_jobs {diagnostic.recoverable_running_jobs}")
            print(f"queue_ready_sessions {queue_ready}")
    return 0


def _init(args: argparse.Namespace) -> int:
    store, app = _app(args)
    try:
        print(f"initialized {app.initialize(display_name=args.name).id}")
    finally:
        store.close()
    return 0


def _profile(args: argparse.Namespace) -> int:
    store, app = _app(args)
    try:
        if args.profile_command == "set":
            weights = {}
            for item in args.interest:
                topic, sep, value = item.partition("=")
                if not sep:
                    raise ApplicationError("interest must use topic=weight")
                weights[topic] = float(value)
            profile = app.configure_profile(
                weights=weights or None,
                excluded_topics=tuple(args.exclude) if args.exclude else None,
                unexpected_discovery_weight=args.unexpected,
                max_consecutive_topic=args.max_consecutive,
            )
        elif args.profile_command == "reset":
            profile = app.configure_profile(
                weights={"general": 1.0},
                excluded_topics=(),
                unexpected_discovery_weight=0.1,
                max_consecutive_topic=2,
            )
        else:
            profile = app.initialize()
        print(
            f"profile {profile.id}\ninterests "
            + ", ".join(f"{k}={v:g}" for k, v in profile.topic_weights.items())
        )
    except (ApplicationError, ValueError) as error:
        print(f"profile failed: {error}", file=sys.stderr)
        return 2
    finally:
        store.close()
    return 0


def _source(args: argparse.Namespace) -> int:
    store, app = _app(args)
    try:
        if args.source_command == "add":
            print(f"added {app.add_source(args.url, title=args.title).id}")
        elif args.source_command == "list":
            for source in app.list_sources():
                print(f"{source.id} {source.canonical_locator}")
        elif app.remove_source(args.source_id):
            print(f"removed {args.source_id}")
        else:
            print("source not found", file=sys.stderr)
            return 2
    finally:
        store.close()
    return 0


def _refresh(args: argparse.Namespace) -> int:
    store, app = _app(args)
    try:
        if not app.list_sources():
            raise ApplicationError("no sources; run 'curiosity source add <url>' first")
        print(f"built {app.refresh_build()} verified pulses")
    except (ApplicationError, IngestError) as error:
        print(f"refresh failed: {error}", file=sys.stderr)
        return 2
    finally:
        store.close()
    return 0


def _ingest(args: argparse.Namespace) -> int:
    store, app = _app(args)
    try:
        app.add_source(args.url)
        print(f"built {app.refresh_build()} verified pulses")
    except IngestError as error:
        print(f"ingest failed: {error}", file=sys.stderr)
        return 2
    finally:
        store.close()
    return 0


def _play(args: argparse.Namespace) -> int:
    store, app = _app(args)
    try:
        pulses = app.prepare_playback(size=args.size)
        if not pulses:
            raise ApplicationError(
                "no playable facts; run 'curiosity refresh' after adding a source"
            )
        runtime = TerminalPlayback(
            app,
            sleeper=time.sleep,
            write=lambda text: print(text, flush=True),
            interval_seconds=args.interval,
        )
        runtime.run(once=args.once)
    except ApplicationError as error:
        print(f"play failed: {error}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        # The current rendered fact is already acknowledged; the next durable
        # position is coherent and will resume cleanly on the next invocation.
        return 130
    finally:
        store.close()
    return 0


def _inspect(args: argparse.Namespace) -> int:
    store, app = _app(args)
    try:
        item = app.inspect_pulse(args.pulse_id)
        if item is None:
            print("pulse not found", file=sys.stderr)
            return 2
        pulse, source = item["pulse"], item["source"]
        evidence = item["evidence"]
        verification = item["verification"] or {}
        print(
            f"fact {pulse.display_fact}\n"
            f"source {source.canonical_locator if source else 'missing'}\n"
            f"topic {', '.join(pulse.topics)}\n"
            f"verification {verification.get('status', 'unknown')}\n"
            f"verification_reasons {', '.join(verification.get('reason_codes', ())) or 'not recorded'}\n"
            f"evidence {' | '.join(str(row['quote']) for row in evidence) or 'missing'}\n"
            f"provenance {pulse.provenance}\n"
            f"generated_at {pulse.verified_at.isoformat()}"
        )
    finally:
        store.close()
    return 0


def _stats(args: argparse.Namespace) -> int:
    store, app = _app(args)
    try:
        for key, value in app.stats().items():
            print(f"{key} {value}")
    finally:
        store.close()
    return 0


def _discover(args: argparse.Namespace) -> int:
    print(
        "Discovery providers are optional; add an explicit URL with 'curiosity source add <url>'."
    )
    return 0


def _harness(args: argparse.Namespace) -> int:
    if args.harness_command in {"install", "uninstall", "status"}:
        try:
            if args.adapter == "claude":
                if args.harness_command == "install":
                    install_claude(args.path)
                elif args.harness_command == "uninstall":
                    print("removed" if uninstall_claude(args.path) else "not installed")
                else:
                    print("installed" if 'curiosity harness emit claude turn_complete' in args.path.read_text(encoding='utf-8') else "not installed")
            elif args.adapter == "opencode":
                if args.harness_command == "install":
                    install_opencode(args.path)
                elif args.harness_command == "uninstall":
                    print("removed" if uninstall_opencode(args.path) else "not installed")
                else:
                    print("installed" if args.path.exists() else "not installed")
            else:
                print("Codex supports completion notification only; no installer is provided.")
        except (OSError, ValueError) as error:
            print(f"harness {args.harness_command} failed: {error}", file=sys.stderr)
            return 2
        return 0
    store, app = _app(args)
    try:
        event = normalize(args.adapter, args.event_type)
        if event is None:
            print("unsupported harness event", file=sys.stderr)
            return 2
        app.record_harness_event(event)
    finally:
        store.close()
    return 0


def _data(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--data-path", type=Path)


def _nested_data(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--data-path", type=Path, default=argparse.SUPPRESS)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="curiosity", description="Local-first Curiosity Engine")
    commands = parser.add_subparsers(dest="command")
    doctor = commands.add_parser("doctor", help="report local setup")
    doctor.add_argument("--config", type=Path)
    _data(doctor)
    doctor.add_argument("--deep", action="store_true", help="check local database health")
    for name in ("youtube", "embeddings", "sqlite-vec", "harness"):
        doctor.add_argument(f"--{name}", action=argparse.BooleanOptionalAction, default=None)
    doctor.set_defaults(handler=_doctor)
    init = commands.add_parser("init", help="initialize local state")
    _data(init)
    init.add_argument("--name", default="Local user")
    init.set_defaults(handler=_init)
    profile = commands.add_parser("profile", help="show or set weighted interests")
    _data(profile)
    ps = profile.add_subparsers(dest="profile_command", required=True)
    show = ps.add_parser("show")
    _nested_data(show)
    show.set_defaults(handler=_profile)
    pset = ps.add_parser("set")
    _nested_data(pset)
    pset.add_argument("--interest", action="append", default=[])
    pset.add_argument("--exclude", action="append", default=[])
    pset.add_argument("--unexpected", type=float)
    pset.add_argument("--max-consecutive", type=int)
    pset.set_defaults(handler=_profile)
    reset = ps.add_parser("reset")
    _nested_data(reset)
    reset.set_defaults(handler=_profile)
    source = commands.add_parser("source", help="manage explicit sources")
    _data(source)
    ss = source.add_subparsers(dest="source_command", required=True)
    add = ss.add_parser("add")
    _nested_data(add)
    add.add_argument("url")
    add.add_argument("--title")
    add.set_defaults(handler=_source)
    listing = ss.add_parser("list")
    _nested_data(listing)
    listing.set_defaults(handler=_source)
    remove = ss.add_parser("remove")
    _nested_data(remove)
    remove.add_argument("source_id")
    remove.set_defaults(handler=_source)
    refresh = commands.add_parser("refresh", help="fetch sources and build verified facts")
    _data(refresh)
    refresh.set_defaults(handler=_refresh)
    ingest = commands.add_parser("ingest", help="add, fetch, and build one explicit URL")
    _data(ingest)
    ingest.add_argument("url")
    ingest.set_defaults(handler=_ingest)
    discover = commands.add_parser("discover", help="show discovery options")
    _data(discover)
    discover.set_defaults(handler=_discover)
    play = commands.add_parser("play", help="display precomputed facts")
    _data(play)
    play.add_argument("--interval", type=int, default=10)
    play.add_argument("--size", type=int, default=6)
    play.add_argument("--once", action="store_true")
    play.set_defaults(handler=_play)
    inspect = commands.add_parser("inspect", help="show pulse provenance")
    _data(inspect)
    inspect.add_argument("pulse_id")
    inspect.set_defaults(handler=_inspect)
    stats = commands.add_parser("stats", help="show local product counts")
    _data(stats)
    stats.set_defaults(handler=_stats)
    harness = commands.add_parser("harness", help="manage or receive minimized optional adapter events")
    _data(harness)
    hs = harness.add_subparsers(dest="harness_command", required=True)
    emit = hs.add_parser("emit")
    emit.add_argument("adapter", choices=list(CAPABILITIES))
    emit.add_argument("event_type")
    emit.set_defaults(handler=_harness)
    for operation in ("install", "uninstall", "status"):
        command = hs.add_parser(operation)
        command.add_argument("adapter", choices=["claude", "opencode", "codex_notify"])
        command.add_argument("--path", type=Path, required=True)
        command.set_defaults(handler=_harness)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "handler"):
        parser.print_help()
        return 0
    return args.handler(args)
