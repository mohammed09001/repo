from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256

from curiosity.contracts import stages
from curiosity.contracts.models import (
    Chunk,
    ClaimStatus,
    Evidence,
    EvidenceSupport,
    KnowledgeAtom,
    ProvenanceClass,
    SourceDocument,
    deterministic_id,
)


class KnowledgeError(RuntimeError):
    pass


@dataclass(frozen=True)
class KnowledgeCandidate:
    atom: KnowledgeAtom
    evidence: tuple[Evidence, ...]
    status: str = "candidate"
    topics: tuple[str, ...] = ()
    difficulty: str = "unknown"
    difficulty_uncertain: bool = True
    why_interesting: str = "source-grounded candidate"
    normalized_hash: str = ""

    @property
    def playable(self) -> bool:
        return self.status == "verified" and bool(self.evidence)


_BOILERPLATE = re.compile(
    r"\b(cookie|privacy policy|subscribe|all rights reserved|buy now)\b", re.I
)

_NON_LATIN = re.compile(
    r"[\u0370-\u03FF\u0400-\u04FF\u0590-\u05FF\u0600-\u06FF\u0900-\u097F"
    r"\u0E00-\u0E7F\u3040-\u30FF\u3400-\u4DBF\u4E00-\u9FFF\uAC00-\uD7AF]"
)
_ACCENTED = re.compile(
    r"[àâäçéèêëïîôöùûüÿñæœßáíóúýÀÂÄÇÉÈÊËÏÎÔÖÙÛÜÑÁÍÓÚÝ]"
)


def is_english(text: str) -> bool:
    """Deterministic heuristic: non-Latin scripts are never English, and any
    accented Latin character signals a Latin-script foreign language."""
    if _NON_LATIN.search(text):
        return False
    return not _ACCENTED.search(text)


def normalize_claim(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def fact_fingerprint(text: str) -> str:
    """Exact normalized fingerprint of a displayed fact. This is Stage 1 of the
    Near-Duplicate Firewall and the cooldown key; it never includes metadata."""
    return sha256(normalize_claim(text).encode("utf-8")).hexdigest()


def make_candidate(
    document: SourceDocument,
    chunk: Chunk,
    statement: str,
    *,
    provenance: ProvenanceClass,
    topics: tuple[str, ...] = (),
    why: str = "source-grounded candidate",
    extractor_version: str | None = None,
) -> KnowledgeCandidate:
    """Build a candidate whose atom binds to one evidence chunk. The statement
    is the claim being judged; the evidence quote is always the raw chunk text."""
    normalized = normalize_claim(statement)
    contract = extractor_version or stages.EXTRACTOR_VERSION
    evidence_id = deterministic_id(
        "evidence",
        document.source_id,
        document.id,
        chunk.id,
        sha256(normalized.encode()).hexdigest(),
    )
    evidence = Evidence(
        id=evidence_id,
        source_id=document.source_id,
        document_id=document.id,
        chunk_id=chunk.id,
        quote=chunk.text,
        support=EvidenceSupport.DIRECT,
        provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
    )
    atom = KnowledgeAtom(
        id=deterministic_id("atom", chunk.id, contract, sha256(normalized.encode()).hexdigest()),
        statement=statement,
        claim_status=ClaimStatus.CANDIDATE,
        evidence_ids=(evidence.id,),
        provenance=provenance,
        created_at=datetime.now(UTC),
    )
    return KnowledgeCandidate(
        atom,
        (evidence,),
        topics=topics,
        why_interesting=why,
        normalized_hash=sha256(normalized.encode()).hexdigest(),
    )


def extract_no_llm(
    document: SourceDocument,
    chunks: list[Chunk],
    *,
    contract: str | None = None,
) -> list[KnowledgeCandidate]:
    """Deterministically take the first bounded declarative sentence from each useful chunk."""
    candidates: list[KnowledgeCandidate] = []
    seen: set[str] = set()
    for chunk in chunks:
        text = chunk.text.strip()
        if len(text) < 20 or _BOILERPLATE.search(text) or re.fullmatch(r"[\W\d_]+", text):
            continue
        sentence = re.split(r"(?<=[.!?])\s+", text, maxsplit=1)[0].strip()
        if len(sentence) < 20 or (is_english(sentence) and sentence.count(" ") < 2):
            continue
        candidate = make_candidate(
            document,
            chunk,
            sentence,
            provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
            extractor_version=contract,
        )
        if candidate.normalized_hash not in seen:
            candidates.append(candidate)
            seen.add(candidate.normalized_hash)
    return candidates