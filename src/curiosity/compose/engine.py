from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime

from curiosity.contracts.models import CardType, CuriosityCard, ProvenanceClass, deterministic_id
from curiosity.knowledge.engine import KnowledgeCandidate
from curiosity.verify.engine import VerificationResult, VerificationStatus


class CompositionError(ValueError):
    pass


@dataclass(frozen=True)
class CardPacket:
    card: CuriosityCard
    hook: str
    body: str
    atom_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    relationship: str | None = None


_CLICKBAIT = re.compile(r"\b(secret|shocking|you won't believe|urgent|always|never|best)\b", re.I)


def compose_card(
    candidate: KnowledgeCandidate,
    verification: VerificationResult,
    *,
    card_type: CardType = CardType.QUESTION,
) -> CardPacket:
    if verification.status is not VerificationStatus.VERIFIED or not verification.playable:
        raise CompositionError("only verified, policy-safe candidates may be composed")
    body = candidate.atom.statement.strip()
    if not body.endswith("."):
        body += "."
    words = body.rstrip(".").split()
    if (
        len(body) > 240
        or len(words) < 3
        or len(words) > 40
        or body.count(".") != 1
        or _CLICKBAIT.search(body)
    ):
        raise CompositionError("fact violates concise educational-fact grammar")
    evidence_ids = tuple(evidence.id for evidence in candidate.evidence)
    card = CuriosityCard(
        id=deterministic_id("card", candidate.atom.id, card_type, "deterministic-v1"),
        card_type=card_type,
        prompt=body,
        atom_ids=(candidate.atom.id,),
        evidence_ids=evidence_ids,
        provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
        created_at=datetime.now(UTC),
    )
    return CardPacket(card, body, body, card.atom_ids, evidence_ids)


def compose_sequence(
    items: list[tuple[KnowledgeCandidate, VerificationResult]],
    *,
    relationship: str,
    maximum: int = 6,
) -> tuple[CardPacket, ...]:
    if relationship not in {
        "same_concept",
        "prerequisite",
        "mechanism",
        "contrast",
        "chronology",
        "connection",
    }:
        raise CompositionError("relationship must be explicit")
    if not 2 <= len(items) <= maximum:
        raise CompositionError("sequence must contain 2..maximum cards")
    packets = [compose_card(candidate, result) for candidate, result in items]
    return tuple(
        CardPacket(
            packet.card,
            packet.hook,
            packet.body,
            packet.atom_ids,
            packet.evidence_ids,
            relationship,
        )
        for packet in packets
    )
