from datetime import UTC, datetime

from curiosity.contracts.models import Chunk, ProvenanceClass, SourceDocument, deterministic_id
from curiosity.knowledge.engine import extract_no_llm, is_english

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


def test_deterministic_english_script_gate():
    assert is_english("Ocean currents transport heat around the planet.")
    assert not is_english("Les courants océaniques transportent la chaleur.")
    assert not is_english("海洋环流在全球传输热量。")
    assert not is_english("Океанские течения переносят тепло.")