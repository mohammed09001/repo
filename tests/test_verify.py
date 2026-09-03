from datetime import UTC, datetime

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
from curiosity.verify.engine import VerificationStatus, verify_candidate

NOW = datetime(2026, 9, 3, tzinfo=UTC)
SOURCE = SourceRecord(
    id=deterministic_id("source", "verify"),
    source_type=SourceType.NOTE,
    canonical_locator="local://verify",
    title="Verify",
    trust=TrustClass.LOCAL,
    provenance=ProvenanceClass.USER_AUTHORED,
    retrieved_at=NOW,
)
DOC = SourceDocument(
    id=deterministic_id("document", "verify"),
    source_id=SOURCE.id,
    content_sha256="a" * 64,
    raw_text="Mars has two small moons.",
    captured_at=NOW,
    provenance=ProvenanceClass.USER_AUTHORED,
)
CHUNK = Chunk(
    id=deterministic_id("chunk", "verify"),
    document_id=DOC.id,
    ordinal=0,
    text="Mars has two small moons. They are named Phobos and Deimos.",
    char_start=0,
    char_end=56,
    provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
)


def test_valid_and_stale_bindings_are_distinguished():
    candidate = extract_no_llm(DOC, [CHUNK])[0]
    assert verify_candidate(candidate, SOURCE, DOC, [CHUNK]).status is VerificationStatus.VERIFIED
    assert verify_candidate(candidate, SOURCE, DOC, []).status is VerificationStatus.REJECTED


def test_numeric_missing_anchor_is_uncertain_and_risk_blocks_playback():
    candidate = extract_no_llm(DOC, [CHUNK])[0]
    changed = candidate.atom.model_copy(update={"statement": "Mars has 3 small moons."})
    numeric = candidate.__class__(changed, candidate.evidence)
    assert verify_candidate(numeric, SOURCE, DOC, [CHUNK]).status is VerificationStatus.UNCERTAIN
    risky = candidate.atom.model_copy(update={"statement": "Medical treatment always works."})
    result = verify_candidate(candidate.__class__(risky, candidate.evidence), SOURCE, DOC, [CHUNK])
    assert "high_risk_actionable_domain" in result.risk_flags and not result.playable
