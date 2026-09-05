"""Canonical product use cases; CLI handlers only adapt arguments to this facade."""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from typing import Any

import httpx

from curiosity.ambient import AmbientController, AmbientSignal
from curiosity.compose.engine import CompositionError, compose_card
from curiosity.contracts import stages
from curiosity.contracts.identity import source_identity_key
from curiosity.contracts.model import ModelGateway
from curiosity.contracts.models import (
    CuriosityPulse,
    HarnessEvent,
    PlaybackSession,
    Profile,
    ProvenanceClass,
    SessionStatus,
    SourceRecord,
    SourceType,
    TrustClass,
    deterministic_id,
)
from curiosity.contracts.stages import derived_contract, stage_key
from curiosity.dedupe.engine import lexical_similarity, suppressed_pool_ids
from curiosity.ingest.pipeline import Fetcher, HttpxFetcher, IngestionPipeline
from curiosity.knowledge.engine import extract_no_llm
from curiosity.quality.engine import (
    QualityBudget,
    classify_candidate,
    run_quality,
)
from curiosity.ranking.engine import (
    Candidate,
    ProfilePreferences,
    freshness_from_age,
    novelty_from_age,
    novelty_from_distance,
    quality_class,
    rank,
    source_quality_class,
)
from curiosity.sequence.planner import QueueItem, plan_queue
from curiosity.sources.adapters import (
    GitHubAdapter,
    SemanticScholarAdapter,
    WebAdapter,
    YouTubeAdapter,
    canonicalize_url,
)
from curiosity.sources.http import (
    DiscoveryBudget,
    DiscoveryError,
    HttpClient,
    PostTransport,
    Transport,
)
from curiosity.store import LocalStore
from curiosity.verify.engine import VerificationStatus, verify_candidate


class ApplicationError(RuntimeError):
    pass


@dataclass(frozen=True)
class DiscoveryCredentials:
    """Config-owned discovery secrets; never read ad-hoc from the environment here."""

    github_token: str | None = None
    semantic_scholar_api_key: str | None = None
    youtube_api_key: str | None = None


@dataclass(frozen=True)
class DiscoveryCounters:
    provider: str
    requests: int
    bytes: int
    retries: int
    elapsed_ms: int
    results: int
    deduped: int
    candidates: int
    registered: int
    rate_limited: int
    failed: int


@dataclass(frozen=True)
class DiscoveryResult:
    records: tuple[SourceRecord, ...]
    counters: DiscoveryCounters
    error: str = ""


@dataclass
class BuildReport:
    sources: int = 0
    fetched: int = 0
    reused: int = 0
    reparsed: int = 0
    skipped: int = 0
    candidates: int = 0
    verified: int = 0
    pulses_built: int = 0
    escalated: int = 0
    rejected: int = 0
    model_calls: int = 0
    cached_hits: int = 0
    model_failures: int = 0
    budget_exhausted: bool = False
    run_id: str = ""
    duplicates_suppressed: int = 0
    http_fetches: int = 0
    http_cache_hits: int = 0
    bytes_downloaded: int = 0
    retries: int = 0
    failures: int = 0
    parser_elapsed_ms: float = 0.0
    ingest_elapsed_ms: int = 0
    elapsed_ms: int = 0
    status: str = "succeeded"

    def ledger(self) -> dict[str, int | float]:
        """Bounded, secret-free counters persisted in the refresh run ledger."""
        return {
            "sources": self.sources,
            "fetched": self.fetched,
            "reused": self.reused,
            "reparsed": self.reparsed,
            "skipped": self.skipped,
            "candidates": self.candidates,
            "verified": self.verified,
            "pulses_built": self.pulses_built,
            "rejected": self.rejected,
            "duplicates_suppressed": self.duplicates_suppressed,
            "model_calls": self.model_calls,
            "cached_hits": self.cached_hits,
            "model_failures": self.model_failures,
            "budget_exhausted": int(self.budget_exhausted),
            "http_fetches": self.http_fetches,
            "http_cache_hits": self.http_cache_hits,
            "bytes_downloaded": self.bytes_downloaded,
            "retries": self.retries,
            "failures": self.failures,
            "parser_elapsed_ms": self.parser_elapsed_ms,
            "ingest_elapsed_ms": self.ingest_elapsed_ms,
            "elapsed_ms": self.elapsed_ms,
        }


class CuriosityApplication:
    """The sole cross-domain coordinator for local first-use and daily-use flows."""

    def __init__(
        self,
        store: LocalStore,
        *,
        fetcher: Fetcher | None = None,
        gateway: ModelGateway | None = None,
        now: Callable[[], datetime] | None = None,
        discovery: DiscoveryCredentials | None = None,
        discovery_transport: Transport | None = None,
        discovery_post_transport: PostTransport | None = None,
    ) -> None:
        self.store = store
        self.fetcher = fetcher
        self.gateway = gateway
        self._run_seq = 0
        self.now = now or (lambda: datetime.now(UTC))
        self.discovery = discovery or DiscoveryCredentials()
        self.discovery_transport = discovery_transport
        self.discovery_post_transport = discovery_post_transport

    @staticmethod
    def default_profile_id() -> str:
        return deterministic_id("profile", "local-default-user")

    def initialize(self, *, display_name: str = "Local user") -> Profile:
        profile = self.store.get_profile(self.default_profile_id())
        if profile is not None:
            return profile
        profile = Profile(
            id=self.default_profile_id(),
            display_name=display_name,
            created_at=self.now(),
            provenance=ProvenanceClass.USER_AUTHORED,
        )
        self.store.put_profile(profile)
        return profile

    def configure_profile(
        self,
        *,
        weights: dict[str, float] | None = None,
        excluded_topics: tuple[str, ...] | None = None,
        unexpected_discovery_weight: float | None = None,
        max_consecutive_topic: int | None = None,
    ) -> Profile:
        current = self.initialize()
        profile = current.model_copy(
            update={
                "topic_weights": weights if weights is not None else current.topic_weights,
                "interests": tuple((weights or current.topic_weights).keys()),
                "excluded_topics": excluded_topics
                if excluded_topics is not None
                else current.excluded_topics,
                "unexpected_discovery_weight": unexpected_discovery_weight
                if unexpected_discovery_weight is not None
                else current.unexpected_discovery_weight,
                "max_consecutive_topic": max_consecutive_topic
                if max_consecutive_topic is not None
                else current.max_consecutive_topic,
            }
        )
        self.store.put_profile(profile)
        return profile

    def add_source(self, locator: str, *, title: str | None = None) -> SourceRecord:
        canonical = canonicalize_url(locator)
        source = SourceRecord(
            id=deterministic_id("source", canonical),
            source_type=SourceType.WEB,
            canonical_locator=canonical,
            title=title or canonical,
            trust=TrustClass.REMOTE_UNTRUSTED,
            provenance=ProvenanceClass.SOURCE,
            retrieved_at=self.now(),
        )
        self.store.put_source(source)
        return source

    def list_sources(self) -> list[SourceRecord]:
        return self.store.list_sources()

    def remove_source(self, source_id: str) -> bool:
        # Lineage rows protect sources by default; remove the entire derived branch deliberately.
        with self.store.transaction(immediate=True) as connection:
            pulse_rows = connection.execute(
                "SELECT id, card_id, atom_id FROM pulses WHERE source_id=?", (source_id,)
            ).fetchall()
            cards = [row["card_id"] for row in pulse_rows]
            atoms = [row["atom_id"] for row in pulse_rows]
            connection.execute("DELETE FROM pulses WHERE source_id=?", (source_id,))
            if cards:
                marks = ",".join("?" for _ in cards)
                connection.execute(f"DELETE FROM exposures WHERE card_id IN ({marks})", cards)
                connection.execute(f"DELETE FROM session_cards WHERE card_id IN ({marks})", cards)
                connection.execute(f"DELETE FROM cards WHERE id IN ({marks})", cards)
            if atoms:
                marks = ",".join("?" for _ in atoms)
                connection.execute(f"DELETE FROM atoms WHERE id IN ({marks})", atoms)
            connection.execute("DELETE FROM evidence WHERE source_id=?", (source_id,))
            result = connection.execute("DELETE FROM sources WHERE id=?", (source_id,))
        return result.rowcount == 1

    # --- Discovery control plane -------------------------------------------------

    def _check_rate_state(self, provider: str) -> None:
        state = self.store.get_adapter_state(provider)
        retry_after = state.get("retry_after")
        if not state.get("rate_limited") or not retry_after:
            return
        try:
            retry_at = datetime.fromisoformat(str(retry_after))
        except ValueError:
            return
        if retry_at > self.now():
            raise DiscoveryError(
                f"{provider} discovery is rate-limited until {retry_at.isoformat()}",
                transient=True,
                retry_after=retry_at,
            )

    def _record_rate_state(self, provider: str, error: DiscoveryError) -> None:
        state: dict[str, object] = {"rate_limited": True}
        if error.retry_after is not None:
            state["retry_after"] = error.retry_after.isoformat()
        self.store.set_adapter_state(provider, state)

    def _discover(
        self, provider: str, *, limit: int, build: Callable[[HttpClient], list[SourceRecord]]
    ) -> DiscoveryResult:
        self._check_rate_state(provider)
        budget = DiscoveryBudget(max_requests=limit + 2)
        started = time.monotonic()
        rate_limited = 0
        failed = 0
        last_error = ""
        bytes_received = 0
        retries_performed = 0
        records: list[SourceRecord] = []
        try:
            client = HttpClient(
                budget=budget,
                retries=1,
                transport=self.discovery_transport,
                post_transport=self.discovery_post_transport,
            )
            try:
                records = build(client)
            finally:
                bytes_received = client.bytes_received
                retries_performed = client.retries_performed
                client.close()
        except DiscoveryError as error:
            if error.transient:
                rate_limited = 1
                self._record_rate_state(provider, error)
            else:
                failed = 1
                last_error = str(error)
        elapsed_ms = int((time.monotonic() - started) * 1000)
        results = len(records)
        deduped = 0
        stored = 0
        for record in records:
            identity = source_identity_key(record)
            if self.store.source_conflicts(
                locator=record.canonical_locator, identity_key=identity
            ) or self.store.candidate_conflicts(locator=record.canonical_locator, identity_key=identity):
                deduped += 1
                continue
            if self.store.put_discovery_candidate(provider=provider, record=record):
                stored += 1
        return DiscoveryResult(
            tuple(records),
            DiscoveryCounters(
                provider=provider,
                requests=budget.used_requests,
                bytes=bytes_received,
                retries=retries_performed,
                elapsed_ms=elapsed_ms,
                results=results,
                deduped=deduped,
                candidates=stored,
                registered=0,
                rate_limited=rate_limited,
                failed=failed,
            ),
            error=last_error,
        )

    def discover_github(self, query: str, *, limit: int = 10) -> DiscoveryResult:
        return self._discover(
            "github",
            limit=limit,
            build=lambda client: GitHubAdapter(
                client, token=self.discovery.github_token
            ).search(query, limit=limit),
        )

    def discover_papers(self, query: str, *, limit: int = 10) -> DiscoveryResult:
        return self._discover(
            "papers",
            limit=limit,
            build=lambda client: SemanticScholarAdapter(
                client, api_key=self.discovery.semantic_scholar_api_key
            ).search(query, limit=limit),
        )

    def discover_feed(self, feed_url: str, *, limit: int = 10) -> DiscoveryResult:
        def build(client: HttpClient) -> list[SourceRecord]:
            try:
                canonical = canonicalize_url(feed_url)
            except ValueError as exc:
                raise DiscoveryError(str(exc), transient=False) from exc
            xml, _ = client.get_bytes(canonical)
            return WebAdapter().feed(xml, feed_url=canonical)
        return self._discover("feed", limit=limit, build=build)

    def discover_youtube(self, query: str, *, limit: int = 10) -> DiscoveryResult:
        return self._discover(
            "youtube",
            limit=limit,
            build=lambda client: YouTubeAdapter(
                client, api_key=self.discovery.youtube_api_key
            ).search(query, limit=limit),
        )

    def list_discovered(self) -> list[dict[str, Any]]:
        return self.store.list_discovery_candidates()

    def register_discovered(
        self, candidate_ids: tuple[str, ...] = (), *, all: bool = False
    ) -> int:
        if all:
            candidates = self.store.list_discovery_candidates()
        else:
            if not candidate_ids:
                raise ApplicationError("register requires candidate ids or --all")
            candidates = []
            for candidate_id in candidate_ids:
                row = self.store.get_discovery_candidate(candidate_id)
                if row is None:
                    raise ApplicationError(f"discovery candidate not found: {candidate_id}")
                candidates.append(row)
        registered = 0
        for row in candidates:
            record = SourceRecord.model_validate_json(row["payload_json"])
            identity = source_identity_key(record)
            if self.store.source_conflicts(
                locator=record.canonical_locator, identity_key=identity
            ):
                self.store.remove_discovery_candidate(row["id"])
                continue
            if self.store.put_source(record):
                registered += 1
            self.store.remove_discovery_candidate(row["id"])
        return registered

    def remove_discovered(self, candidate_id: str) -> bool:
        return self.store.remove_discovery_candidate(candidate_id)

    # --- Incremental refresh / build --------------------------------------------

    def refresh_build(self) -> BuildReport:
        """Two-speed build: deterministic fast lane, then bounded quality lane.

        A source whose fetch reuses the current document AND whose stage key is
        unchanged skips all downstream work. Candidates that the fast lane can
        prove directly never touch a model; only escalated candidates consume
        bounded, cached, ledgered provider calls.

        The whole run is durable: one bounded ``run_summaries`` row plus a
        leased ``jobs`` row. An interrupted refresh leaves a recoverable
        running job that the next run detects and resets, and every stage is
        idempotent (304 reuse + ``ON CONFLICT``), so resuming never duplicates
        documents or pulses. Budget exhaustion is a terminal run status, not an
        exception.
        """
        self._run_seq += 1
        run_id = deterministic_id("run", self.now().isoformat(), str(self._run_seq))
        report = BuildReport(run_id=run_id)
        started = time.monotonic()
        gateway = self.gateway
        model_id = gateway.cheap.model_id if gateway else None
        quality = gateway is not None
        contract = derived_contract(
            extractor=stages.EXTRACTOR_VERSION, model_id=model_id, quality=quality
        )
        budget = QualityBudget(
            max_calls=gateway.max_calls if gateway and gateway.max_calls else 10,
            max_cost=gateway.max_cost if gateway else None,
        )
        client: httpx.Client | None = None
        pipeline: IngestionPipeline | None = None
        try:
            self.store.recover_abandoned_jobs(now=self.now())
            self.store.start_run_summary(run_id, at=self.now())
            job_id = self.store.create_job(
                job_id=deterministic_id("job", "refresh", run_id),
                idempotency_key=f"refresh:{run_id}",
                stage="refresh",
                now=self.now(),
            )
            self.store.claim_job_by_id(job_id=job_id, worker_id="refresh-worker", now=self.now())
            ingest_started = time.monotonic()
            fetcher = self.fetcher
            if fetcher is None:
                # One pooled client for the whole refresh run, closed when done.
                client = httpx.Client(
                    timeout=10.0,
                    limits=httpx.Limits(max_connections=5, max_keepalive_connections=5),
                    max_redirects=10,
                )
                fetcher = HttpxFetcher(client)
            pipeline = IngestionPipeline(self.store, fetcher)
            for source in self.store.list_sources():
                report.sources += 1
                outcome = pipeline.ingest(source)
                expected = stage_key(
                    outcome.document.id, model_id=model_id, quality=gateway is not None
                )
                current = self.store.get_stage_key(source.id)
                if (
                    outcome.reused
                    and current is not None
                    and current["document_id"] == outcome.document.id
                    and current["stage_key"] == expected
                ):
                    report.skipped += 1
                    continue
                if outcome.reused:
                    report.reused += 1
                if outcome.reparsed:
                    report.reparsed += 1
                if not outcome.reused and not outcome.reparsed:
                    report.fetched += 1
                candidates = extract_no_llm(
                    outcome.document, outcome.chunks, contract=contract
                )
                report.candidates += len(candidates)
                for candidate in candidates:
                    verification = verify_candidate(
                        candidate, source, outcome.document, outcome.chunks
                    )
                    escalation = classify_candidate(candidate.atom.statement, verification)
                    if escalation is None:
                        self._persist_verified(
                            candidate, verification, source, outcome.document,
                            expected, report,
                        )
                        continue
                    report.escalated += 1
                    if gateway is None:
                        # No provider: deterministic reject, never a pulse.
                        self.store.record_build_event(
                            run_id=run_id,
                            source_id=source.id,
                            document_id=outcome.document.id,
                            candidate_id=candidate.atom.id,
                            escalation_reason=escalation.reason.value,
                            outcome="rejected",
                            detail="no_provider_offline",
                        )
                        report.rejected += 1
                        continue
                    quality = run_quality(
                        candidate,
                        source,
                        outcome.document,
                        outcome.chunks,
                        gateway,
                        budget,
                        self.store,
                        self.store,
                        run_id=run_id,
                        escalation=escalation,
                        source_id=source.id,
                        contract=contract,
                    )
                    if budget.exhausted:
                        report.budget_exhausted = True
                    self.store.record_build_event(
                        run_id=run_id,
                        source_id=source.id,
                        document_id=outcome.document.id,
                        candidate_id=candidate.atom.id,
                        escalation_reason=escalation.reason.value,
                        outcome="rejected" if quality.rejected else "rebuilt",
                        detail=quality.reason,
                    )
                    if quality.candidate is None or quality.verified is None:
                        report.rejected += 1
                        continue
                    self._persist_verified(
                        quality.candidate, quality.verified, source, outcome.document,
                        expected, report,
                    )
                document_key = sha256(
                    "\x1f".join([outcome.document.content_sha256, outcome.parser_version]).encode()
                ).hexdigest()
                self.store.put_stage_key(
                    source_id=source.id,
                    document_id=outcome.document.id,
                    parser_version=outcome.parser_version,
                    document_key=document_key,
                    stage_key=expected,
                )
            report.ingest_elapsed_ms = int((time.monotonic() - ingest_started) * 1000)
            self._fold_pipeline_counters(report, pipeline)
            for row in self.store.model_usage_summary(run_id):
                report.model_calls += int(row["calls"]) - int(row["cache_hits"]) - int(row["failures"])
                report.cached_hits += int(row["cache_hits"])
                report.model_failures += int(row["failures"])
            report.elapsed_ms = int((time.monotonic() - started) * 1000)
            report.status = "budget_exhausted" if report.budget_exhausted else "succeeded"
            self.store.finish_run_summary(
                run_id, status=report.status, counters=report.ledger(), at=self.now()
            )
            self.store.complete_job(job_id=job_id, worker_id="refresh-worker", now=self.now())
            return report
        except BaseException as error:  # noqa: BLE001 - recorded as a failed run
            self._fold_pipeline_counters(report, pipeline)
            report.elapsed_ms = int((time.monotonic() - started) * 1000)
            report.status = "failed"
            self.store.finish_run_summary(
                run_id,
                status="failed",
                counters=report.ledger(),
                at=self.now(),
                detail=f"{type(error).__name__}: {error}",
            )
            raise
        finally:
            if client is not None:
                client.close()
            if gateway is not None:
                gateway.close()

    @staticmethod
    def _fold_pipeline_counters(report: BuildReport, pipeline: IngestionPipeline | None) -> None:
        """Copy bounded HTTP/parser counters from the pipeline into the report.

        Called on both the success and failure paths so a failed run still
        records exactly what was attempted.
        """
        if pipeline is None:
            return
        report.http_fetches = int(pipeline.counters["http_fetches"])
        report.http_cache_hits = int(pipeline.counters["http_cache_hits"])
        report.bytes_downloaded = int(pipeline.counters["bytes_downloaded"])
        report.retries = int(pipeline.counters["retries"])
        report.failures = int(pipeline.counters["failures"])
        report.parser_elapsed_ms = float(pipeline.counters["parser_elapsed_ms"])

    def dry_run_refresh(self) -> dict[str, int]:
        """Truthful local-state work estimate without any network or provider call."""
        estimate = {"sources": 0, "would_skip": 0, "would_build": 0}
        for source in self.store.list_sources():
            estimate["sources"] += 1
            if self.store.get_stage_key(source.id) is None:
                estimate["would_build"] += 1
            else:
                estimate["would_skip"] += 1
        return estimate

    def _persist_verified(
        self,
        candidate,
        verification,
        source: SourceRecord,
        document,
        expected: str,
        report: BuildReport,
    ) -> None:
        """Compose and persist one verified projection (fast or quality lane).

        The Near-Duplicate Firewall runs here, after deterministic verification,
        so an exact or same-claim duplicate never becomes a new playable pulse.
        """
        self.store.put_atom(candidate.atom)
        for evidence in candidate.evidence:
            self.store.put_evidence(evidence)
        if (
            verification.status is not VerificationStatus.VERIFIED
            or not verification.playable
        ):
            return
        try:
            packet = compose_card(candidate, verification)
        except CompositionError:
            # Concise-fact grammar is a hard projection policy; a candidate
            # that violates it is not playable, not fatal.
            return
        from curiosity.dedupe.engine import firewall_decision

        tier, _sim = firewall_decision(
            self.store,
            packet.body,
            exclude_pulse_id=deterministic_id("pulse", packet.card.id),
            exclude_source_id=source.id,
        )
        if tier in {"duplicate", "same_wording", "same_claim"}:
            report.duplicates_suppressed += 1
            self.store.record_build_event(
                run_id=report.run_id,
                source_id=source.id,
                document_id=document.id,
                candidate_id=candidate.atom.id,
                escalation_reason=None,
                outcome="duplicate_suppressed",
                detail=tier,
            )
            return
        report.verified += 1
        self.store.put_card(packet.card)
        pulse = CuriosityPulse(
            id=deterministic_id("pulse", packet.card.id),
            card_id=packet.card.id,
            atom_id=candidate.atom.id,
            display_fact=packet.body,
            topics=candidate.topics or ("general",),
            source_id=source.id,
            document_id=document.id,
            evidence_ids=packet.evidence_ids,
            verified_at=self.now(),
            provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
        )
        if self.store.put_pulse(
            pulse,
            verification={
                "status": verification.status,
                "reason_codes": verification.reason_codes,
                "risk_flags": verification.risk_flags,
                "provider_used": verification.provider_used,
            },
            stage_key=expected,
        ):
            report.pulses_built += 1

    # --- Playback -----------------------------------------------------------------

    _HARD_REPEAT_WINDOW = 10
    _COOLDOWN = 30
    _LOW_WATERMARK = 3
    _HARD_HOURS = 6.0
    _COOLDOWN_HOURS = 72.0

    def _profile_preferences(self, profile: Profile) -> ProfilePreferences:
        return ProfilePreferences(
            topic_weights=profile.topic_weights,
            excluded_topics=frozenset(profile.excluded_topics),
            unexpected_discovery_weight=profile.unexpected_discovery_weight,
            max_consecutive_topic=profile.max_consecutive_topic,
        )

    def _build_ranked_pool(
        self,
        profile: Profile,
        *,
        exclude_card_ids: frozenset[str] = frozenset(),
    ) -> tuple[list[Candidate], dict[str, CuriosityPulse], frozenset[str], tuple[str, ...]]:
        """Build explainable ranking candidates from real stored state.

        Applies the Near-Duplicate Firewall against recently seen ideas before
        ranking so repeated/paraphrased facts never occupy attention.
        """
        now = self.now()
        now_seconds = now.timestamp()

        def item_age(item: dict[str, Any]) -> float:
            try:
                exposed_at = datetime.fromisoformat(str(item["exposed_at"]))
            except (TypeError, ValueError):
                return float("inf")
            return max(0.0, now_seconds - exposed_at.timestamp())

        # The hard repeat window is wall-clock: every idea seen within the last
        # few hours is suppressed, regardless of corpus size or how many other
        # facts were shown in between. The query is indexed and capped.
        hard_hours_seconds = self._HARD_HOURS * 3600
        since = (now - timedelta(seconds=hard_hours_seconds)).isoformat()
        recent = self.store.recent_exposures(profile.id, since=since, limit=5000)
        pool = self.store.list_eligible_with_fingerprint()
        pool_rows = [
            (pulse.id, fingerprint, pulse.display_fact) for pulse, fingerprint in pool
        ]
        suppressed = suppressed_pool_ids(self.store, recent, pool_rows)
        by_id = {pulse.id: pulse for pulse, _ in pool}
        recent_sources = frozenset(
            item["source_id"] for item in recent if item.get("source_id")
        )
        recent_topics = tuple(
            str(item["topic"]) for item in recent if item.get("topic")
        )
        recent_fingerprints = [
            str(item["fingerprint"]) for item in recent if item.get("fingerprint")
        ]
        hard_fingerprints = {
            str(item["fingerprint"]) for item in recent if item.get("fingerprint")
        }
        recent_exposed_at: dict[str, float] = {}
        for item in recent:
            fingerprint = str(item.get("fingerprint") or "")
            if not fingerprint:
                continue
            age = item_age(item)
            recent_exposed_at[fingerprint] = min(
                recent_exposed_at.get(fingerprint, age), age
            )
        candidates: list[Candidate] = []
        for pulse, fingerprint in pool:
            if (
                pulse.id in suppressed
                or fingerprint in hard_fingerprints
                or pulse.card_id in exclude_card_ids
            ):
                continue
            verification = self.store.get_pulse_verification(pulse.id) or {}
            quality, quality_reason = quality_class(verification)
            source = self.store.get_source(pulse.source_id)
            source_quality, source_reason = (
                source_quality_class(source.trust) if source else (0.5, "missing_source")
            )
            freshness = freshness_from_age((now - pulse.verified_at).total_seconds())
            if fingerprint in recent_fingerprints:
                distance = recent_fingerprints.index(fingerprint)
                distance_novelty = novelty_from_distance(
                    distance, hard_window=self._HARD_REPEAT_WINDOW, cooldown=self._COOLDOWN
                )
            else:
                distance_novelty = 1.0
            age_novelty = novelty_from_age(
                recent_exposed_at.get(fingerprint, float("inf")),
                hard_hours=self._HARD_HOURS,
                cooldown_hours=self._COOLDOWN_HOURS,
            )
            novelty = min(distance_novelty, age_novelty)
            novelty_reason = (
                "exposure_cooldown" if fingerprint in recent_fingerprints else "not_recently_seen"
            )
            topic = pulse.topics[0] if pulse.topics else "general"
            candidates.append(
                Candidate(
                    pulse.id,
                    topic,
                    pulse.source_id,
                    True,
                    quality=quality,
                    novelty=novelty,
                    curiosity=0.5,
                    freshness=freshness,
                    source_quality=source_quality,
                    usefulness=0.5,
                    signal_reasons={
                        "quality": quality_reason,
                        "source_quality": source_reason,
                        "freshness": "verified_recency",
                        "novelty": novelty_reason,
                        "curiosity": "no_evidence_neutral",
                        "usefulness": "no_evidence_neutral",
                    },
                )
            )
        return candidates, by_id, recent_sources, recent_topics

    def _plan_batch(
        self,
        profile: Profile,
        *,
        size: int,
        generation: int,
        exclude_card_ids: frozenset[str] = frozenset(),
    ) -> tuple[tuple[CuriosityPulse, ...], list[str], list[str]]:
        """Plan one bounded local batch: (pulses, per-item reasons, fingerprints)."""
        preferences = self._profile_preferences(profile)
        candidates, by_id, recent_sources, recent_topics = self._build_ranked_pool(
            profile, exclude_card_ids=exclude_card_ids
        )
        ranked = rank(
            candidates,
            preferences,
            recent_ids=frozenset(),
            recent_topics=recent_topics,
            recent_sources=recent_sources,
        )
        unexpected_topics = frozenset(
            topic
            for topic in {candidate.topic for candidate in candidates}
            if topic not in profile.topic_weights
        )
        unexpected_share = min(0.25, max(0.0, profile.unexpected_discovery_weight))
        base_seed = int(deterministic_id("feedseed", profile.id)[-8:], 16)

        def similarity(a: QueueItem, b: QueueItem) -> float:
            return lexical_similarity(a.text, b.text) if a.text and b.text else 0.0

        queue = plan_queue(
            [
                QueueItem(
                    item.candidate.id,
                    item.candidate.topic,
                    item.score,
                    True,
                    "ranked",
                    text=by_id[item.candidate.id].display_fact,
                )
                for item in ranked
            ],
            size=size,
            seed=base_seed + generation,
            max_topic_streak=preferences.max_consecutive_topic,
            diversity_lambda=0.6,
            unexpected_share=unexpected_share,
            unexpected_topics=unexpected_topics,
            similarity=similarity,
        )
        pulses = tuple(by_id[item.card_id] for item in queue)
        reasons = [item.reason for item in queue]
        fingerprints = [pulse.display_fact for pulse in pulses]
        return pulses, reasons, fingerprints

    def _activate_session(
        self,
        profile: Profile,
        *,
        generation: int,
        pulses: tuple[CuriosityPulse, ...],
        reasons: list[str],
        fingerprints: list[str],
    ) -> tuple[CuriosityPulse, ...]:
        if not pulses:
            return ()
        session_number = self.store.connection.execute(
            "SELECT COUNT(*) FROM sessions WHERE profile_id=?", (profile.id,)
        ).fetchone()[0]
        session = PlaybackSession(
            id=deterministic_id(
                "session", profile.id, str(session_number), *(pulse.card_id for pulse in pulses)
            ),
            profile_id=profile.id,
            status=SessionStatus.CREATED,
            card_ids=tuple(pulse.card_id for pulse in pulses),
            started_at=self.now(),
            provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
        )
        self.store.put_session(
            session,
            generation=generation,
            reasons=reasons,
            fingerprints=fingerprints,
        )
        return pulses

    def prepare_playback(self, *, size: int = 6) -> tuple[CuriosityPulse, ...]:
        profile = self.initialize()
        current = self.store.current_session_pulse(profile.id)
        if current is not None:
            # An interrupted run resumes the already-ranked durable session.
            return (current,)
        pulses, reasons, fingerprints = self._plan_batch(profile, size=size, generation=0)
        return self._activate_session(profile, generation=0, pulses=pulses, reasons=reasons, fingerprints=fingerprints)

    def refill_playback(self, *, size: int = 6) -> bool:
        """Local-only low/high-watermark refill. No network, parse, or model work.

        Called outside the render critical section. When the active reservoir
        drops to the low watermark it is extended with a new ranked batch that
        excludes items already queued or recently shown. Returns False only when
        the local corpus has nothing new to offer.
        """
        profile = self.initialize()
        remaining = self.store.remaining_playback_count(profile.id)
        session_id = self.store.active_session_id(profile.id)
        if session_id is not None and remaining > self._LOW_WATERMARK:
            return True
        if session_id is not None:
            generation = self.store.connection.execute(
                "SELECT generation FROM sessions WHERE id=?", (session_id,)
            ).fetchone()[0]
            excluded = self.store.queued_card_ids(profile.id)
            pulses, reasons, fingerprints = self._plan_batch(
                profile, size=size, generation=int(generation) + 1, exclude_card_ids=excluded
            )
            if not pulses:
                return False
            self.store.append_session_cards(
                session_id, list(zip((p.card_id for p in pulses), reasons, fingerprints, strict=True))
            )
            return True
        generation = self.store.connection.execute(
            "SELECT COALESCE(MAX(generation), 0) FROM sessions WHERE profile_id=?",
            (profile.id,),
        ).fetchone()[0]
        pulses, reasons, fingerprints = self._plan_batch(
            profile, size=size, generation=int(generation) + 1
        )
        selected = self._activate_session(
            profile, generation=int(generation) + 1, pulses=pulses, reasons=reasons, fingerprints=fingerprints
        )
        return bool(selected)

    def next_playback_pulse(self) -> CuriosityPulse | None:
        """Consume the precomputed durable queue without invoking ranking or source work."""
        return self.store.next_session_pulse(self.initialize().id)

    def current_playback_pulse(self) -> CuriosityPulse | None:
        """The playback tick reads only a local durable queue."""
        return self.store.current_session_pulse(self.initialize().id)

    def acknowledge_playback_pulse(self, pulse: CuriosityPulse) -> bool:
        return self.store.record_displayed_pulse(self.initialize().id, pulse, at=self.now())

    def record_harness_event(self, event: HarnessEvent) -> AmbientSignal:
        """Persist the raw event and derive the bounded ambient runtime state.

        Optional adapters end here: the derived state may influence whether an
        ambient playback loop stays active or quiets, and whether a local queue
        may refill. It never influences source truth, verification, knowledge
        content, or ranking.
        """
        self.store.put_harness_event(event)
        return AmbientController(self.store, now=self.now).ingest(event)

    def ambient_state(self) -> dict[str, str]:
        controller = AmbientController(self.store, now=self.now)
        return {
            "state": controller.current_state().value,
            "posture": controller.posture().value,
        }

    def ambient_playback_active(self) -> bool:
        return AmbientController(self.store, now=self.now).playback_active()

    def ambient_refill_allowed(self) -> bool:
        return AmbientController(self.store, now=self.now).refill_allowed()

    def inspect_pulse(self, pulse_id: str) -> dict[str, object] | None:
        pulse = self.store.get_pulse(pulse_id)
        if pulse is None:
            return None
        source = self.store.get_source(pulse.source_id)
        return {
            "pulse": pulse,
            "source": source,
            "atom": self.store.payloads_for_ids("atoms", (pulse.atom_id,)),
            "evidence": self.store.payloads_for_ids("evidence", pulse.evidence_ids),
            "card": self.store.payloads_for_ids("cards", (pulse.card_id,)),
            "verification": self.store.get_pulse_verification(pulse.id),
        }

    def stats(self) -> dict[str, int]:
        rows = self.store.connection.execute(
            "SELECT COUNT(*) AS shown, COUNT(DISTINCT card_id) AS distinct_facts FROM exposures"
        ).fetchone()
        semantic = self.store.connection.execute(
            """SELECT p.fact_fingerprint FROM exposures e
               JOIN pulses p ON p.card_id=e.card_id"""
        ).fetchall()
        semantic_distinct = len({row["fact_fingerprint"] for row in semantic})
        shown_cards = self.store.connection.execute(
            """SELECT p.payload_json FROM exposures e
               JOIN pulses p ON p.card_id=e.card_id"""
        )
        explored = {
            topic
            for row in shown_cards
            for topic in json.loads(row["payload_json"]).get("topics", [])
        }
        session_rows = self.store.connection.execute(
            "SELECT status, position FROM sessions"
        ).fetchall()
        return {
            "sources": len(self.store.list_sources()),
            "pulses": len(self.store.list_eligible_pulses()),
            "profiles": int(
                self.store.connection.execute("SELECT COUNT(*) FROM profiles").fetchone()[0]
            ),
            "facts_shown": int(rows["shown"]),
            "distinct_facts_shown": int(rows["distinct_facts"]),
            "semantic_facts_shown": semantic_distinct,
            "topics_explored": len(explored),
            "repetitions": int(rows["shown"] - rows["distinct_facts"]),
            "semantic_repetitions": int(rows["shown"] - semantic_distinct),
            "sessions_completed": sum(row["status"] == "completed" for row in session_rows),
            "session_items_acknowledged": sum(int(row["position"]) for row in session_rows),
        }