from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from curiosity.contracts.models import (
    CONTRACT_VERSION,
    CardType,
    Chunk,
    CuriosityCard,
    Evidence,
    EvidenceSupport,
    Exposure,
    HarnessEvent,
    JobStatus,
    KnowledgeAtom,
    PlaybackSession,
    Profile,
    ProvenanceClass,
    SessionStatus,
    SourceDocument,
    SourceRecord,
    SourceType,
    TrustClass,
    deterministic_id,
)

NOW = datetime(2026, 9, 3, tzinfo=UTC)
SOURCE_ID = deterministic_id("source", "https://example.test/a")


def test_contract_round_trip_and_schema_version():
    source = SourceRecord(
        id=SOURCE_ID,
        source_type=SourceType.WEB,
        canonical_locator="https://example.test/a",
        title="Example",
        trust=TrustClass.REMOTE_UNTRUSTED,
        provenance=ProvenanceClass.SOURCE,
        retrieved_at=NOW,
    )
    restored = SourceRecord.model_validate_json(source.model_dump_json())
    assert restored == source
    assert restored.schema_version == CONTRACT_VERSION
    assert (
        SourceRecord.model_json_schema()["properties"]["schema_version"]["const"]
        == CONTRACT_VERSION
    )


def test_every_canonical_record_round_trips():
    document_id = deterministic_id("document", "immutable-document")
    chunk_id = deterministic_id("chunk", "immutable-chunk")
    evidence_id = deterministic_id("evidence", "immutable-evidence")
    atom_id = deterministic_id("atom", "immutable-atom")
    profile_id = deterministic_id("profile", "immutable-profile")
    card_id = deterministic_id("card", "immutable-card")
    records = (
        SourceDocument(
            id=document_id,
            source_id=SOURCE_ID,
            content_sha256="a" * 64,
            raw_text="Authoritative raw text.",
            captured_at=NOW,
            provenance=ProvenanceClass.SOURCE,
        ),
        Chunk(
            id=chunk_id,
            document_id=document_id,
            ordinal=0,
            text="Authoritative raw text.",
            char_start=0,
            char_end=23,
            provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
        ),
        Evidence(
            id=evidence_id,
            source_id=SOURCE_ID,
            document_id=document_id,
            chunk_id=chunk_id,
            quote="Authoritative raw text.",
            support=EvidenceSupport.DIRECT,
            provenance=ProvenanceClass.SOURCE,
        ),
        KnowledgeAtom(
            id=atom_id,
            statement="A claim backed by evidence.",
            claim_status="supported",
            evidence_ids=(evidence_id,),
            provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
            created_at=NOW,
        ),
        CuriosityCard(
            id=card_id,
            card_type=CardType.QUESTION,
            prompt="What follows?",
            atom_ids=(atom_id,),
            evidence_ids=(evidence_id,),
            provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
            created_at=NOW,
        ),
        Profile(
            id=profile_id,
            display_name="Ada",
            created_at=NOW,
            provenance=ProvenanceClass.USER_AUTHORED,
        ),
        Exposure(
            id=deterministic_id("exposure", "immutable-exposure"),
            profile_id=profile_id,
            card_id=card_id,
            exposed_at=NOW,
            outcome="shown",
            provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
        ),
        PlaybackSession(
            id=deterministic_id("session", "immutable-session"),
            profile_id=profile_id,
            status=SessionStatus.ACTIVE,
            card_ids=(card_id,),
            started_at=NOW,
            provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
        ),
        HarnessEvent(
            id=deterministic_id("event", "immutable-event"),
            job_status=JobStatus.SUCCEEDED,
            event_type="fixture_playback",
            occurred_at=NOW,
            provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
        ),
    )
    for record in records:
        assert type(record).model_validate_json(record.model_dump_json()) == record


def test_unknown_values_and_extra_fields_fail():
    with pytest.raises(ValidationError):
        SourceRecord(
            id=SOURCE_ID,
            source_type="invented",
            canonical_locator="x",
            title="x",
            trust=TrustClass.LOCAL,
            provenance=ProvenanceClass.SOURCE,
            retrieved_at=NOW,
        )
    with pytest.raises(ValidationError):
        SourceRecord(
            id=SOURCE_ID,
            source_type=SourceType.NOTE,
            canonical_locator="x",
            title="x",
            trust=TrustClass.LOCAL,
            provenance=ProvenanceClass.SOURCE,
            retrieved_at=NOW,
            provider_payload={},
        )


def test_card_cannot_masquerade_as_source_evidence():
    card = CuriosityCard(
        id=deterministic_id("card", "immutable-card"),
        card_type=CardType.QUESTION,
        prompt="Why?",
        atom_ids=(deterministic_id("atom", "immutable-atom"),),
        provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
        created_at=NOW,
    )
    with pytest.raises(ValidationError):
        Evidence.model_validate(card.model_dump())


def test_deterministic_ids_do_not_depend_on_display_text():
    assert deterministic_id("source", "https://example.test/a") == SOURCE_ID
    assert deterministic_id("source", "https://example.test/a") != deterministic_id(
        "source", "https://example.test/b"
    )
