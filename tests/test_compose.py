from datetime import UTC, datetime

import pytest

from curiosity.compose.engine import CompositionError, compose_card, compose_sequence
from curiosity.contracts.models import (
    Chunk,
    ProvenanceClass,
    SourceDocument,
    SourceRecord,
    SourceType,
    TrustClass,
    deterministic_id,
)
from curiosity.knowledge.engine import extract_no_llm
from curiosity.verify.engine import verify_candidate

NOW = datetime(2026, 9, 3, tzinfo=UTC)
SOURCE = SourceRecord(
    id=deterministic_id("source", "compose"),
    source_type=SourceType.NOTE,
    canonical_locator="local://compose",
    title="Compose",
    trust=TrustClass.LOCAL,
    provenance=ProvenanceClass.USER_AUTHORED,
    retrieved_at=NOW,
)
DOC = SourceDocument(
    id=deterministic_id("document", "compose"),
    source_id=SOURCE.id,
    content_sha256="b" * 64,
    raw_text="Earth has an atmosphere.",
    captured_at=NOW,
    provenance=ProvenanceClass.USER_AUTHORED,
)


def candidate(value):
    chunk = Chunk(
        id=deterministic_id("chunk", value),
        document_id=DOC.id,
        ordinal=0,
        text=value,
        char_start=0,
        char_end=len(value),
        provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
    )
    item = extract_no_llm(DOC, [chunk])[0]
    return item, verify_candidate(item, SOURCE, DOC, [chunk])


def test_verified_card_is_bounded_and_traceable():
    item, result = candidate("Earth has an atmosphere that supports weather patterns.")
    card = compose_card(item, result)
    assert card.atom_ids == (item.atom.id,) and card.evidence_ids == item.atom.evidence_ids
    assert len(card.hook) <= 180 and len(card.body) <= 500
    assert card.card.prompt == card.body
    assert "why does this matter" not in card.card.prompt.casefold()


def test_unverified_and_unrelated_sequence_restrictions():
    item, result = candidate("Earth has an atmosphere that supports weather patterns.")
    with pytest.raises(CompositionError):
        compose_card(
            item,
            result.__class__(
                result.status.__class__.UNCERTAIN,
                result.bindings,
                result.reason_codes,
                result.risk_flags,
            ),
        )
    with pytest.raises(CompositionError):
        compose_sequence([(item, result)], relationship="same_concept")
    assert (
        len(
            compose_sequence(
                [
                    candidate("Earth has an atmosphere that supports weather patterns."),
                    candidate("Atmospheres can retain heat near a planet."),
                ],
                relationship="mechanism",
            )
        )
        == 2
    )
