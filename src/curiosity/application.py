"""Canonical product use cases; CLI handlers only adapt arguments to this facade."""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, datetime

from curiosity.compose.engine import compose_card
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
from curiosity.ingest.pipeline import Fetcher, IngestionPipeline, UrllibFetcher
from curiosity.knowledge.engine import (
    ExtractionBudget,
    StructuredProvider,
    extract_no_llm,
    extract_structured,
)
from curiosity.ranking.engine import Candidate, ProfilePreferences, rank
from curiosity.sequence.planner import QueueItem, plan_queue
from curiosity.sources.adapters import SourceAdapter, WebAdapter
from curiosity.store import LocalStore
from curiosity.verify.engine import VerificationStatus, verify_candidate


class ApplicationError(RuntimeError):
    pass


class CuriosityApplication:
    """The sole cross-domain coordinator for local first-use and daily-use flows."""

    def __init__(
        self,
        store: LocalStore,
        *,
        fetcher: Fetcher | None = None,
        structured_provider: StructuredProvider | None = None,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self.store = store
        self.fetcher = fetcher or UrllibFetcher()
        self.structured_provider = structured_provider
        self.now = now or (lambda: datetime.now(UTC))

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
        from curiosity.sources.adapters import canonicalize_url

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

    def discover(
        self, adapter: SourceAdapter, query: str, *, limit: int = 10
    ) -> list[SourceRecord]:
        records = adapter.search(query, limit=limit)
        for record in records:
            self.store.put_source(record)
        return records

    def discover_feed(self, xml: bytes, *, feed_url: str) -> list[SourceRecord]:
        records = WebAdapter().feed(xml, feed_url=feed_url)
        for record in records:
            self.store.put_source(record)
        return records

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

    def refresh_build(self) -> int:
        """Fetch explicit sources and persist only safe verified playable projections."""
        built = 0
        for source in self.store.list_sources():
            document, chunks, _ = IngestionPipeline(self.store, self.fetcher).ingest(source)
            candidates = (
                extract_structured(document, chunks, self.structured_provider, ExtractionBudget())
                if self.structured_provider
                else extract_no_llm(document, chunks)
            )
            for candidate in candidates:
                verification = verify_candidate(candidate, source, document, chunks)
                self.store.put_atom(candidate.atom)
                for evidence in candidate.evidence:
                    self.store.put_evidence(evidence)
                if (
                    verification.status is not VerificationStatus.VERIFIED
                    or not verification.playable
                ):
                    continue
                packet = compose_card(candidate, verification)
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
                ):
                    built += 1
        return built

    def prepare_playback(self, *, size: int = 6) -> tuple[CuriosityPulse, ...]:
        profile = self.initialize()
        current = self.store.current_session_pulse(profile.id)
        if current is not None:
            # An interrupted run resumes the already-ranked durable session.
            return (current,)
        preferences = ProfilePreferences(
            topic_weights=profile.topic_weights,
            excluded_topics=frozenset(profile.excluded_topics),
            unexpected_discovery_weight=profile.unexpected_discovery_weight,
            max_consecutive_topic=profile.max_consecutive_topic,
        )
        pulses = self.store.list_pulses()
        by_id = {pulse.id: pulse for pulse in pulses}
        ranked = rank(
            [
                Candidate(
                    pulse.id,
                    pulse.topics[0] if pulse.topics else "general",
                    pulse.source_id,
                    True,
                    1.0,
                    1.0,
                    1.0,
                    1.0,
                )
                for pulse in pulses
            ],
            preferences,
        )
        queue = plan_queue(
            [
                QueueItem(item.candidate.id, item.candidate.topic, item.score, True, "ranked")
                for item in ranked
            ],
            size=size,
        )
        selected = tuple(by_id[item.card_id] for item in queue)
        if selected:
            session_number = self.store.connection.execute(
                "SELECT COUNT(*) FROM sessions WHERE profile_id=?", (profile.id,)
            ).fetchone()[0]
            session = PlaybackSession(
                id=deterministic_id(
                    "session", profile.id, str(session_number), *(pulse.card_id for pulse in selected)
                ),
                profile_id=profile.id,
                status=SessionStatus.CREATED,
                card_ids=tuple(pulse.card_id for pulse in selected),
                started_at=self.now(),
                provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
            )
            self.store.put_session(session)
        return selected

    def next_playback_pulse(self) -> CuriosityPulse | None:
        """Consume the precomputed durable queue without invoking ranking or source work."""
        return self.store.next_session_pulse(self.initialize().id)

    def current_playback_pulse(self) -> CuriosityPulse | None:
        """The playback tick reads only a local durable queue."""
        return self.store.current_session_pulse(self.initialize().id)

    def acknowledge_playback_pulse(self, pulse: CuriosityPulse) -> bool:
        return self.store.record_displayed_pulse(self.initialize().id, pulse, at=self.now())

    def record_harness_event(self, event: HarnessEvent) -> bool:
        """Optional adapters end here; they have no control over playback."""
        return self.store.put_harness_event(event)

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
            "pulses": len(self.store.list_pulses()),
            "profiles": int(
                self.store.connection.execute("SELECT COUNT(*) FROM profiles").fetchone()[0]
            ),
            "facts_shown": int(rows["shown"]),
            "distinct_facts_shown": int(rows["distinct_facts"]),
            "topics_explored": len(explored),
            "repetitions": int(rows["shown"] - rows["distinct_facts"]),
            "sessions_completed": sum(row["status"] == "completed" for row in session_rows),
            "session_items_acknowledged": sum(int(row["position"]) for row in session_rows),
        }
