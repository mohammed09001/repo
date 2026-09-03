from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from typing import Protocol

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


class StructuredProvider(Protocol):
    model_id: str

    def generate_structured(self, prompt: str) -> tuple[str, int, int, float]: ...


@dataclass
class ExtractionBudget:
    max_calls: int = 10
    max_input_chars: int = 20_000
    used_calls: int = 0

    def consume(self, text: str) -> None:
        if self.used_calls >= self.max_calls or len(text) > self.max_input_chars:
            raise KnowledgeError("structured extraction budget exhausted")
        self.used_calls += 1


_BOILERPLATE = re.compile(
    r"\b(cookie|privacy policy|subscribe|all rights reserved|buy now)\b", re.I
)


def normalize_claim(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def topic_slug(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.casefold()).strip("-")
    if not slug:
        raise ValueError("topic must contain letters or numbers")
    return slug


def _candidate(
    document: SourceDocument,
    chunk: Chunk,
    statement: str,
    *,
    provenance: ProvenanceClass,
    topics: tuple[str, ...] = (),
    why: str = "source-grounded candidate",
) -> KnowledgeCandidate:
    normalized = normalize_claim(statement)
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
        id=deterministic_id("atom", chunk.id, sha256(normalized.encode()).hexdigest()),
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


def extract_no_llm(document: SourceDocument, chunks: list[Chunk]) -> list[KnowledgeCandidate]:
    """Deterministically take the first bounded declarative sentence from each useful chunk."""
    candidates: list[KnowledgeCandidate] = []
    seen: set[str] = set()
    for chunk in chunks:
        text = chunk.text.strip()
        if len(text) < 20 or _BOILERPLATE.search(text) or re.fullmatch(r"[\W\d_]+", text):
            continue
        sentence = re.split(r"(?<=[.!?])\s+", text, maxsplit=1)[0].strip()
        if len(sentence) < 20 or sentence.count(" ") < 2:
            continue
        candidate = _candidate(
            document, chunk, sentence, provenance=ProvenanceClass.DERIVED_DETERMINISTIC
        )
        if candidate.normalized_hash not in seen:
            candidates.append(candidate)
            seen.add(candidate.normalized_hash)
    return candidates


def extract_structured(
    document: SourceDocument,
    chunks: list[Chunk],
    provider: StructuredProvider,
    budget: ExtractionBudget,
) -> list[KnowledgeCandidate]:
    context = "\n".join(f"[{chunk.id}] {chunk.text}" for chunk in chunks[:3])
    budget.consume(context)
    raw, _, _, _ = provider.generate_structured(
        "Return JSON claims with statement, chunk_id, topics, why_interesting.\n" + context
    )
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise KnowledgeError("provider returned invalid JSON") from exc
    if not isinstance(payload, list):
        raise KnowledgeError("provider output must be a list")
    by_id = {chunk.id: chunk for chunk in chunks}
    candidates: list[KnowledgeCandidate] = []
    seen: set[str] = set()
    for item in payload:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("statement"), str)
            or item.get("chunk_id") not in by_id
        ):
            raise KnowledgeError("provider output has invalid claim or evidence chunk")
        topics = tuple(
            topic_slug(str(topic)) for topic in item.get("topics", []) if str(topic).strip()
        )
        candidate = _candidate(
            document,
            by_id[item["chunk_id"]],
            item["statement"],
            provenance=ProvenanceClass.DERIVED_MODEL,
            topics=topics,
            why=str(item.get("why_interesting") or "model-selected source-grounded candidate"),
        )
        if candidate.normalized_hash not in seen:
            candidates.append(candidate)
            seen.add(candidate.normalized_hash)
    return candidates
