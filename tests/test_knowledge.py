from datetime import UTC, datetime

import pytest

from curiosity.contracts.models import Chunk, ProvenanceClass, SourceDocument, deterministic_id
from curiosity.knowledge.engine import (
    ExtractionBudget,
    KnowledgeError,
    extract_no_llm,
    extract_structured,
)

NOW = datetime(2026, 9, 3, tzinfo=UTC)
DOC = SourceDocument(
    id=deterministic_id("document", "knowledge"),
    source_id=deterministic_id("source", "knowledge"),
    content_sha256="a" * 64,
    raw_text="Raw truth",
    captured_at=NOW,
    provenance=ProvenanceClass.SOURCE,
)


def chunk(text, value="one"):
    return Chunk(
        id=deterministic_id("chunk", value),
        document_id=DOC.id,
        ordinal=0,
        text=text,
        char_start=0,
        char_end=len(text),
        provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
    )


def test_no_llm_candidates_are_evidence_grounded_non_playable_and_idempotent():
    results = extract_no_llm(
        DOC, [chunk("Ocean currents transport heat around the planet. This affects climate.")]
    )
    assert len(results) == 1 and results[0].evidence[0].chunk_id
    assert not results[0].playable and results[0].atom.claim_status == "candidate"
    assert (
        results[0].atom.id
        == extract_no_llm(
            DOC, [chunk("Ocean currents transport heat around the planet. This affects climate.")]
        )[0].atom.id
    )


def test_boilerplate_and_duplicate_ideas_are_filtered():
    chunks = [
        chunk("Subscribe now for exclusive offers and buy now.", "promo"),
        chunk("Plants convert light into chemical energy.", "a"),
        chunk("Plants convert light into chemical energy.", "b"),
    ]
    assert len(extract_no_llm(DOC, chunks)) == 1


class FakeProvider:
    model_id = "fake"

    def __init__(self, value):
        self.value = value

    def generate_structured(self, prompt):
        return self.value, 1, 1, 0.01


def test_structured_provider_validates_evidence_and_budgets():
    source = chunk("Mars has polar ice caps that change with seasons.", "mars")
    valid = (
        '[{"statement":"Mars has polar ice caps.","chunk_id":"'
        + source.id
        + '","topics":["Planet Science"],"why_interesting":"observable cycles"}]'
    )
    result = extract_structured(DOC, [source], FakeProvider(valid), ExtractionBudget())
    assert result[0].topics == ("planet-science",) and result[0].atom.provenance == "derived_model"
    with pytest.raises(KnowledgeError):
        extract_structured(DOC, [source], FakeProvider("[]"), ExtractionBudget(max_calls=0))
    with pytest.raises(KnowledgeError):
        extract_structured(
            DOC,
            [source],
            FakeProvider('[{"statement":"x","chunk_id":"missing"}]'),
            ExtractionBudget(),
        )
