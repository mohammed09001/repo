"""Canonical records. Raw source records never share a type with derived output."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

CONTRACT_VERSION = "1.0"
OpaqueId = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_-]*_[a-f0-9]{16,64}$")]


def deterministic_id(kind: str, *identity_parts: str) -> str:
    """Return a stable opaque ID; callers must supply immutable identity inputs."""
    if (
        not kind.replace("_", "").isalnum()
        or not identity_parts
        or any(not part for part in identity_parts)
    ):
        raise ValueError("kind and non-empty immutable identity parts are required")
    digest = sha256("\x1f".join(identity_parts).encode("utf-8")).hexdigest()[:24]
    return f"{kind}_{digest}"


class CanonicalModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, use_enum_values=False)
    schema_version: Literal["1.0"] = CONTRACT_VERSION


class SourceType(StrEnum):
    ARTICLE = "article"
    BOOK = "book"
    NOTE = "note"
    PODCAST = "podcast"
    VIDEO = "video"
    WEB = "web"


class TrustClass(StrEnum):
    USER = "user"
    LOCAL = "local"
    REMOTE_UNTRUSTED = "remote_untrusted"
    CURATED = "curated"


class ProvenanceClass(StrEnum):
    SOURCE = "source"
    DERIVED_DETERMINISTIC = "derived_deterministic"
    DERIVED_MODEL = "derived_model"
    USER_AUTHORED = "user_authored"


class ClaimStatus(StrEnum):
    CANDIDATE = "candidate"
    SUPPORTED = "supported"
    CONTESTED = "contested"
    REJECTED = "rejected"


class EvidenceSupport(StrEnum):
    DIRECT = "direct"
    PARTIAL = "partial"
    CONTRADICTS = "contradicts"
    CONTEXTUAL = "contextual"


class CardType(StrEnum):
    QUESTION = "question"
    INSIGHT = "insight"
    CONNECTION = "connection"
    REVIEW = "review"


class JobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SessionStatus(StrEnum):
    CREATED = "created"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class SourceRecord(CanonicalModel):
    id: OpaqueId
    source_type: SourceType
    canonical_locator: str = Field(min_length=1, max_length=4096)
    title: str = Field(min_length=1, max_length=1000)
    trust: TrustClass
    provenance: Literal[ProvenanceClass.SOURCE, ProvenanceClass.USER_AUTHORED]
    retrieved_at: datetime
    metadata: dict[str, str] = Field(default_factory=dict)


class SourceDocument(CanonicalModel):
    """Raw captured source content; it is authoritative evidence, not an inference."""

    id: OpaqueId
    source_id: OpaqueId
    content_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    raw_text: str = Field(min_length=1)
    captured_at: datetime
    provenance: Literal[ProvenanceClass.SOURCE, ProvenanceClass.USER_AUTHORED]


class Chunk(CanonicalModel):
    id: OpaqueId
    document_id: OpaqueId
    ordinal: int = Field(ge=0)
    text: str = Field(min_length=1)
    char_start: int = Field(ge=0)
    char_end: int = Field(gt=0)
    provenance: Literal[ProvenanceClass.DERIVED_DETERMINISTIC]

    @field_validator("char_end")
    @classmethod
    def end_after_start(cls, value: int, info: Any) -> int:
        if "char_start" in info.data and value <= info.data["char_start"]:
            raise ValueError("char_end must be greater than char_start")
        return value


class Evidence(CanonicalModel):
    id: OpaqueId
    source_id: OpaqueId
    document_id: OpaqueId
    chunk_id: OpaqueId | None = None
    quote: str = Field(min_length=1)
    support: EvidenceSupport
    provenance: Literal[ProvenanceClass.SOURCE, ProvenanceClass.DERIVED_DETERMINISTIC]


class KnowledgeAtom(CanonicalModel):
    id: OpaqueId
    statement: str = Field(min_length=1, max_length=4000)
    claim_status: ClaimStatus
    evidence_ids: tuple[OpaqueId, ...] = Field(min_length=1)
    provenance: ProvenanceClass
    created_at: datetime


class CuriosityCard(CanonicalModel):
    """A derived prompt. It is deliberately not evidence or a raw source record."""

    id: OpaqueId
    card_type: CardType
    prompt: str = Field(min_length=1, max_length=4000)
    atom_ids: tuple[OpaqueId, ...] = Field(min_length=1)
    evidence_ids: tuple[OpaqueId, ...] = Field(default_factory=tuple)
    provenance: Literal[ProvenanceClass.DERIVED_DETERMINISTIC, ProvenanceClass.DERIVED_MODEL]
    created_at: datetime


class CuriosityPulse(CanonicalModel):
    """A playable projection; its display sentence is not the source of truth."""

    id: OpaqueId
    card_id: OpaqueId
    atom_id: OpaqueId
    display_fact: str = Field(min_length=1, max_length=500)
    topics: tuple[str, ...] = Field(default_factory=tuple)
    source_id: OpaqueId
    document_id: OpaqueId
    evidence_ids: tuple[OpaqueId, ...] = Field(min_length=1)
    verified_at: datetime
    provenance: Literal[ProvenanceClass.DERIVED_DETERMINISTIC]


class Profile(CanonicalModel):
    id: OpaqueId
    display_name: str = Field(min_length=1, max_length=200)
    interests: tuple[str, ...] = Field(default_factory=tuple)
    topic_weights: dict[str, float] = Field(default_factory=lambda: {"general": 1.0})
    excluded_topics: tuple[str, ...] = Field(default_factory=tuple)
    unexpected_discovery_weight: float = Field(default=0.1, ge=0.0, le=1.0)
    max_consecutive_topic: int = Field(default=2, ge=1, le=20)
    created_at: datetime
    provenance: Literal[ProvenanceClass.USER_AUTHORED]


class Exposure(CanonicalModel):
    id: OpaqueId
    profile_id: OpaqueId
    card_id: OpaqueId
    exposed_at: datetime
    outcome: Literal["shown", "dismissed", "saved", "completed"]
    provenance: Literal[ProvenanceClass.DERIVED_DETERMINISTIC]


class PlaybackSession(CanonicalModel):
    id: OpaqueId
    profile_id: OpaqueId
    status: SessionStatus
    card_ids: tuple[OpaqueId, ...] = Field(default_factory=tuple)
    started_at: datetime
    ended_at: datetime | None = None
    provenance: Literal[ProvenanceClass.DERIVED_DETERMINISTIC]

    @field_validator("ended_at")
    @classmethod
    def end_after_start(cls, value: datetime | None, info: Any) -> datetime | None:
        if value is not None and "started_at" in info.data and value < info.data["started_at"]:
            raise ValueError("ended_at cannot precede started_at")
        return value


class HarnessEvent(CanonicalModel):
    id: OpaqueId
    job_status: JobStatus
    event_type: str = Field(min_length=1, max_length=200)
    occurred_at: datetime
    details: dict[str, str | int | float | bool | None] = Field(default_factory=dict)
    provenance: Literal[ProvenanceClass.DERIVED_DETERMINISTIC]


def utc_now() -> datetime:
    return datetime.now(UTC)
