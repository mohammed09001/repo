from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from curiosity.contracts.models import Chunk, SourceDocument, SourceRecord
from curiosity.knowledge.engine import KnowledgeCandidate


class VerificationStatus(StrEnum):
    VERIFIED = "verified"
    UNCERTAIN = "uncertain"
    REJECTED = "rejected"


@dataclass(frozen=True)
class EvidenceBinding:
    atom_id: str
    evidence_id: str
    source_id: str
    document_id: str
    chunk_id: str
    excerpt: str


@dataclass(frozen=True)
class VerificationResult:
    status: VerificationStatus
    bindings: tuple[EvidenceBinding, ...]
    reason_codes: tuple[str, ...]
    risk_flags: tuple[str, ...]
    provider_used: bool = False

    @property
    def playable(self) -> bool:
        return self.status is VerificationStatus.VERIFIED and not self.risk_flags


class SupportVerifier(Protocol):
    def judge(self, claim: str, evidence: str) -> tuple[str, float, str]: ...


_HIGH_RISK = re.compile(
    r"\b(medical|diagnos|treat|legal|lawsuit|invest|financial|investment)\b", re.I
)
_SUPERLATIVE = re.compile(r"\b(always|never|best|worst|proves)\b", re.I)
_NUMBER = re.compile(r"\b\d+(?:\.\d+)?(?:%|\b)")


def _risks(statement: str) -> tuple[str, ...]:
    flags = []
    if _HIGH_RISK.search(statement):
        flags.append("high_risk_actionable_domain")
    if _SUPERLATIVE.search(statement):
        flags.append("unverifiable_superlative")
    return tuple(flags)


def verify_candidate(
    candidate: KnowledgeCandidate,
    source: SourceRecord,
    document: SourceDocument,
    chunks: list[Chunk],
    *,
    verifier: SupportVerifier | None = None,
    confidence_threshold: float = 0.8,
) -> VerificationResult:
    by_id = {chunk.id: chunk for chunk in chunks}
    bindings: list[EvidenceBinding] = []
    reasons: list[str] = []
    for evidence in candidate.evidence:
        chunk = by_id.get(evidence.chunk_id or "")
        if (
            not chunk
            or evidence.source_id != source.id
            or evidence.document_id != document.id
            or chunk.document_id != document.id
        ):
            return VerificationResult(
                VerificationStatus.REJECTED,
                (),
                ("orphaned_or_stale_evidence",),
                _risks(candidate.atom.statement),
            )
        bindings.append(
            EvidenceBinding(
                candidate.atom.id, evidence.id, source.id, document.id, chunk.id, chunk.text[:500]
            )
        )
    if not bindings:
        return VerificationResult(
            VerificationStatus.REJECTED, (), ("missing_evidence",), _risks(candidate.atom.statement)
        )
    evidence_text = " ".join(binding.excerpt for binding in bindings)
    claim_numbers = set(_NUMBER.findall(candidate.atom.statement))
    evidence_numbers = set(_NUMBER.findall(evidence_text))
    if claim_numbers and not claim_numbers.issubset(evidence_numbers):
        return VerificationResult(
            VerificationStatus.UNCERTAIN,
            tuple(bindings),
            ("unsupported_numeric_anchor",),
            _risks(candidate.atom.statement),
        )
    if candidate.atom.statement.casefold().rstrip(".") in evidence_text.casefold():
        status = VerificationStatus.VERIFIED
        reasons.append("direct_textual_support")
    elif verifier is None:
        status = VerificationStatus.UNCERTAIN
        reasons.append("deterministic_support_ambiguous")
    else:
        verdict, confidence, reason = verifier.judge(candidate.atom.statement, evidence_text)
        if verdict == "supported" and confidence >= confidence_threshold:
            status = VerificationStatus.VERIFIED
        elif verdict == "contradicted":
            status = VerificationStatus.REJECTED
        else:
            status = VerificationStatus.UNCERTAIN
        reasons.append(reason)
    return VerificationResult(
        status,
        tuple(bindings),
        tuple(reasons),
        _risks(candidate.atom.statement),
        verifier is not None,
    )
