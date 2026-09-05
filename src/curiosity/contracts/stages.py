"""Incremental build fingerprints. Stage keys answer: did this derived stage's
semantic inputs change? A stage key never includes display text or user intent;
it hashes only immutable identity and contract versions."""

from __future__ import annotations

from curiosity.contracts.models import deterministic_id

EXTRACTOR_VERSION = "extract-no-llm-v1"
VERIFIER_VERSION = "verify-deterministic-v1"
COMPOSER_VERSION = "compose-question-v1"
QUALITY_VERSION = "quality-lane-v1"
FACT_VERSION = "fact-fidelity-v1"


def derived_contract(*, extractor: str, model_id: str | None, quality: bool) -> str:
    """Identity for derived atoms. Folds in every contract that can change a
    derived fact, so a provider/model/quality change produces fresh rows and
    old pulses become historical instead of being orphaned by a stage-key move."""
    return "|".join(
        [
            extractor,
            QUALITY_VERSION,
            FACT_VERSION,
            model_id or "no-model",
            "quality" if quality else "fast",
        ]
    )


def stage_key(
    document_id: str,
    *,
    model_id: str | None = None,
    quality: bool = False,
) -> str:
    """Return the fingerprint for the extract->verify->compose branch of one document.

    The quality/fact contract versions are folded in so that changing the
    escalation prompts or the final-fact fidelity rules triggers an intentional
    rebuild, even when raw content is unchanged.
    """
    return deterministic_id(
        "stage",
        "build-v2",
        document_id,
        derived_contract(
            extractor=EXTRACTOR_VERSION, model_id=model_id, quality=quality
        ),
        VERIFIER_VERSION,
        COMPOSER_VERSION,
    )