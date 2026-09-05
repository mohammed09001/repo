"""Value-of-information escalation: the QUALITY LANE.

The fast lane runs entirely deterministically. This module escalates a single
candidate to bounded, attributable, cached model work only when the
deterministic lane cannot meet product fidelity/quality requirements.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from typing import Protocol

from curiosity.contracts import stages
from curiosity.contracts.model import (
    ModelCallResult,
    ModelFailure,
    ModelGateway,
)
from curiosity.contracts.models import Chunk, ProvenanceClass, SourceDocument, deterministic_id
from curiosity.knowledge.engine import KnowledgeCandidate, is_english, make_candidate
from curiosity.quality.fidelity import anchor_violations
from curiosity.verify.engine import (
    VerificationResult,
    VerificationStatus,
    verify_candidate,
)


class EscalationReason(StrEnum):
    NON_ENGLISH = "non_english"
    MULTI_CLAIM = "multi_claim"
    FIDELITY_REWRITE = "fidelity_rewrite"
    WEAK_DIRECT_SUPPORT = "weak_direct_support"
    POLICY_AMBIGUITY = "policy_ambiguity"


@dataclass(frozen=True)
class Escalation:
    reason: EscalationReason
    required: bool


@dataclass
class QualityBudget:
    max_calls: int = 10
    max_cost: float | None = None
    used_calls: int = 0
    spent_cost: float = 0.0

    @property
    def exhausted(self) -> bool:
        if self.used_calls >= self.max_calls:
            return True
        if self.max_cost is not None and self.spent_cost >= self.max_cost:
            return True
        return False

    def reserve(self) -> bool:
        if self.exhausted:
            return False
        self.used_calls += 1
        return True

    def charge(self, cost: float | None) -> None:
        if cost is not None and cost > 0:
            self.spent_cost += cost


class ModelLedger(Protocol):
    def record_model_usage(
        self,
        *,
        run_id: str,
        task_type: str,
        model_id: str,
        tier: str,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int,
        latency_ms: float,
        cache_hit: bool,
        failed: bool,
        escalation_reason: str | None,
        source_id: str | None,
        document_id: str | None,
    ) -> None: ...


class ModelCache(Protocol):
    def get_model_cache(self, cache_key: str) -> dict[str, object] | None: ...

    def put_model_cache(
        self,
        *,
        cache_key: str,
        task_type: str,
        model_id: str,
        contract_version: str,
        result_json: str,
        cached_tokens: int,
    ) -> None: ...


@dataclass
class QualityOutcome:
    candidate: KnowledgeCandidate | None
    rejected: bool
    reason: str
    verified: VerificationResult | None = None


_CLICKBAIT = re.compile(r"\b(secret|shocking|you won't believe|urgent|always|never|best|worst)\b", re.I)


def classify_candidate(statement: str, verification: VerificationResult) -> Escalation | None:
    """Decide deterministically whether a candidate needs the quality lane."""
    if not is_english(statement):
        return Escalation(EscalationReason.NON_ENGLISH, required=True)
    if verification.risk_flags and not verification.playable:
        # Policy-sensitive ambiguity is resolved conservatively: never spend
        # tokens polishing a claim the deterministic risk gate already flagged.
        return Escalation(EscalationReason.POLICY_AMBIGUITY, required=True)
    words = statement.rstrip(".").split()
    multi_claim = ":" in statement or ";" in statement or statement.count(".") != 1
    if multi_claim:
        return Escalation(EscalationReason.MULTI_CLAIM, required=True)
    if len(statement) > 240 or len(words) > 40 or _CLICKBAIT.search(statement):
        return Escalation(EscalationReason.FIDELITY_REWRITE, required=True)
    if verification.status is VerificationStatus.UNCERTAIN:
        return Escalation(EscalationReason.WEAK_DIRECT_SUPPORT, required=True)
    if len(words) > 24:
        # Playable but verbose; rewriting is a quality improvement, not a gate.
        return Escalation(EscalationReason.FIDELITY_REWRITE, required=False)
    return None


def model_cache_key(*, task: str, evidence: str, contract: str, model_id: str) -> str:
    bounded = evidence[:2000]
    return deterministic_id(
        "modelcache", task, contract, model_id, sha256(bounded.encode("utf-8")).hexdigest()
    )


_TRANSLATE_INSTRUCTION = (
    "Translate the following sentence into one concise English declarative sentence. "
    "Preserve every number, date, named entity, negation, and comparison direction exactly. "
    "Do not add causes, certainty, superlatives, or new entities. Return only the sentence."
)
_REWRITE_INSTRUCTION = (
    "Rewrite the following sentence into one concise English declarative sentence of 8 to 24 words. "
    "Preserve every number, date, named entity, negation, and comparison direction exactly. "
    "Do not add causes, certainty, superlatives, or new entities. Return only the sentence."
)
_EXTRACT_INSTRUCTION = (
    "From the following text extract exactly one atomic, concise English declarative claim that is "
    "directly supported by the text. Preserve every number, date, named entity, negation, and "
    "comparison direction. Do not add causes, certainty, superlatives, or new entities. "
    "Return only the claim sentence."
)
_VERIFY_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["supported", "contradicted", "uncertain"]},
        "confidence": {"type": "number"},
        "reason": {"type": "string"},
    },
    "required": ["verdict", "confidence", "reason"],
    "additionalProperties": False,
}
_FIDELITY_SCHEMA = {
    "type": "object",
    "properties": {
        "faithful": {"type": "boolean"},
        "violations": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["faithful", "violations"],
    "additionalProperties": False,
}


def _model_call(
    gateway: ModelGateway,
    budget: QualityBudget,
    ledger: ModelLedger,
    cache: ModelCache,
    *,
    run_id: str,
    task_type: str,
    tier: str,
    evidence: str,
    prompt: str,
    source_id: str | None,
    document_id: str | None,
    escalation_reason: str | None,
    response_schema: dict | None = None,
) -> ModelCallResult | None:
    endpoint = gateway.strong if tier == "strong" and gateway.strong else gateway.cheap
    cache_key: str | None = None
    if gateway.cache_enabled:
        cache_key = model_cache_key(
            task=task_type, evidence=evidence, contract=stages.QUALITY_VERSION, model_id=endpoint.model_id
        )
        cached = cache.get_model_cache(cache_key)
        if cached is not None:
            ledger.record_model_usage(
                run_id=run_id,
                task_type=task_type,
                model_id=endpoint.model_id,
                tier=tier,
                input_tokens=0,
                output_tokens=0,
                cached_tokens=int(cached.get("cached_tokens", 0) or 0),
                latency_ms=0.0,
                cache_hit=True,
                failed=False,
                escalation_reason=escalation_reason,
                source_id=source_id,
                document_id=document_id,
            )
            return ModelCallResult(
                content=str(cached["result_json"]),
                cached_tokens=int(cached.get("cached_tokens", 0) or 0),
            )
    if not budget.reserve():
        return None
    try:
        if response_schema is not None:
            result = endpoint.generate_structured(prompt, response_schema=response_schema)
        else:
            result = endpoint.generate(prompt)
    except ModelFailure:
        ledger.record_model_usage(
            run_id=run_id,
            task_type=task_type,
            model_id=endpoint.model_id,
            tier=tier,
            input_tokens=0,
            output_tokens=0,
            cached_tokens=0,
            latency_ms=0.0,
            cache_hit=False,
            failed=True,
            escalation_reason=escalation_reason,
            source_id=source_id,
            document_id=document_id,
        )
        return None
    # The call happened: charge and account it regardless of the remaining budget.
    budget.charge(gateway.cost_for(result.input_tokens, result.output_tokens))
    if cache_key is not None:
        cache.put_model_cache(
            cache_key=cache_key,
            task_type=task_type,
            model_id=endpoint.model_id,
            contract_version=stages.QUALITY_VERSION,
            result_json=result.content,
            cached_tokens=result.cached_tokens,
        )
    ledger.record_model_usage(
        run_id=run_id,
        task_type=task_type,
        model_id=endpoint.model_id,
        tier=tier,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        cached_tokens=result.cached_tokens,
        latency_ms=result.latency_ms,
        cache_hit=False,
        failed=False,
        escalation_reason=escalation_reason,
        source_id=source_id,
        document_id=document_id,
    )
    if budget.exhausted:
        return None
    return result


def _verify_model(
    claim: str,
    evidence: str,
    gateway: ModelGateway,
    budget: QualityBudget,
    ledger: ModelLedger,
    cache: ModelCache,
    *,
    run_id: str,
    source_id: str | None,
    document_id: str | None,
    escalation_reason: str,
) -> tuple[str, float, str]:
    verdict, confidence, reason = _verify_at_tier(
        claim,
        evidence,
        gateway,
        budget,
        ledger,
        cache,
        tier="cheap",
        run_id=run_id,
        source_id=source_id,
        document_id=document_id,
        escalation_reason=escalation_reason,
    )
    if verdict == "uncertain" and gateway.strong is not None:
        verdict, confidence, reason = _verify_at_tier(
            claim,
            evidence,
            gateway,
            budget,
            ledger,
            cache,
            tier="strong",
            run_id=run_id,
            source_id=source_id,
            document_id=document_id,
            escalation_reason=escalation_reason,
        )
    return verdict, confidence, reason


def _verify_at_tier(
    claim: str,
    evidence: str,
    gateway: ModelGateway,
    budget: QualityBudget,
    ledger: ModelLedger,
    cache: ModelCache,
    *,
    tier: str,
    run_id: str,
    source_id: str | None,
    document_id: str | None,
    escalation_reason: str,
) -> tuple[str, float, str]:
    prompt = (
        "Judge whether the claim is directly supported by the evidence. "
        "Return JSON with verdict one of supported, contradicted, uncertain; "
        "confidence 0..1; and a short reason.\n"
        f"CLAIM: {claim}\nEVIDENCE: {evidence[:1500]}"
    )
    result = _model_call(
        gateway,
        budget,
        ledger,
        cache,
        run_id=run_id,
        task_type="verify",
        tier=tier,
        evidence=evidence[:1500],
        prompt=prompt,
        source_id=source_id,
        document_id=document_id,
        escalation_reason=escalation_reason,
        response_schema=_VERIFY_SCHEMA,
    )
    if result is None:
        return "uncertain", 0.0, "model_verify_failed_or_budget"
    try:
        payload = json.loads(result.content)
        verdict = str(payload["verdict"])
        confidence = float(payload["confidence"])
        reason = str(payload.get("reason", ""))
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return "uncertain", 0.0, "malformed_model_verdict"
    if verdict not in {"supported", "contradicted", "uncertain"}:
        return "uncertain", 0.0, "malformed_model_verdict"
    return verdict, confidence, reason


def _model_verifier(
    gateway: ModelGateway,
    budget: QualityBudget,
    ledger: ModelLedger,
    cache: ModelCache,
    *,
    run_id: str,
    source_id: str | None,
    document_id: str | None,
    escalation_reason: str,
):
    class ModelSupportVerifier:
        def judge(self, claim: str, evidence: str) -> tuple[str, float, str]:
            return _verify_model(
                claim,
                evidence,
                gateway,
                budget,
                ledger,
                cache,
                run_id=run_id,
                source_id=source_id,
                document_id=document_id,
                escalation_reason=escalation_reason,
            )

    return ModelSupportVerifier()


def _verify_final(
    candidate: KnowledgeCandidate,
    source,
    document: SourceDocument,
    chunks: list[Chunk],
    gateway: ModelGateway,
    budget: QualityBudget,
    ledger: ModelLedger,
    cache: ModelCache,
    *,
    run_id: str,
    escalation_reason: str,
    source_id: str,
) -> VerificationResult:
    verifier = _model_verifier(
        gateway,
        budget,
        ledger,
        cache,
        run_id=run_id,
        source_id=source_id,
        document_id=document.id,
        escalation_reason=escalation_reason,
    )
    return verify_candidate(candidate, source, document, chunks, verifier=verifier)


def _translate(
    original: str,
    gateway: ModelGateway,
    budget: QualityBudget,
    ledger: ModelLedger,
    cache: ModelCache,
    *,
    run_id: str,
    source_id: str,
    document_id: str,
) -> tuple[str | None, str]:
    prompt = _TRANSLATE_INSTRUCTION + "\n\n" + original[:1500]
    result = _model_call(
        gateway, budget, ledger, cache, run_id=run_id, task_type="translate", tier="cheap",
        evidence=original[:1500], prompt=prompt, source_id=source_id, document_id=document_id,
        escalation_reason="non_english",
    )
    if result is None:
        return None, "translate_failed_or_budget"
    english = result.content.strip()
    if anchor_violations(original, english, translated=True):
        if not gateway.strong:
            return None, "translate_anchor_violation"
        result = _model_call(
            gateway, budget, ledger, cache, run_id=run_id, task_type="translate", tier="strong",
            evidence=original[:1500], prompt=prompt, source_id=source_id, document_id=document_id,
            escalation_reason="non_english",
        )
        if result is None:
            return None, "translate_strong_failed"
        english = result.content.strip()
        violations = anchor_violations(original, english, translated=True)
        if violations:
            return None, f"translate_anchor_violation:{','.join(violations)}"
    faithful, reason = _judge_fidelity(
        original, english, gateway, budget, ledger, cache, run_id=run_id,
        source_id=source_id, document_id=document_id,
    )
    if not faithful:
        return None, reason
    return english, ""


def _rewrite_or_extract(
    source_text: str,
    task_type: str,
    gateway: ModelGateway,
    budget: QualityBudget,
    ledger: ModelLedger,
    cache: ModelCache,
    *,
    run_id: str,
    source_id: str,
    document_id: str,
) -> tuple[str | None, str]:
    instruction = _REWRITE_INSTRUCTION if task_type == "rewrite" else _EXTRACT_INSTRUCTION
    prompt = instruction + "\n\n" + source_text[:1500]
    result = _model_call(
        gateway, budget, ledger, cache, run_id=run_id, task_type=task_type, tier="cheap",
        evidence=source_text[:1500], prompt=prompt, source_id=source_id, document_id=document_id,
        escalation_reason=task_type,
    )
    if result is None:
        return None, f"{task_type}_failed_or_budget"
    rewritten = result.content.strip()
    violations = anchor_violations(source_text, rewritten, translated=False)
    if violations:
        if not gateway.strong:
            return None, f"{task_type}_anchor_violation"
        result = _model_call(
            gateway, budget, ledger, cache, run_id=run_id, task_type=task_type, tier="strong",
            evidence=source_text[:1500], prompt=prompt, source_id=source_id, document_id=document_id,
            escalation_reason=task_type,
        )
        if result is None:
            return None, f"{task_type}_strong_failed"
        rewritten = result.content.strip()
        violations = anchor_violations(source_text, rewritten, translated=False)
        if violations:
            return None, f"{task_type}_anchor_violation:{','.join(violations)}"
    return rewritten, ""


def _judge_fidelity(
    original: str,
    rewritten: str,
    gateway: ModelGateway,
    budget: QualityBudget,
    ledger: ModelLedger,
    cache: ModelCache,
    *,
    run_id: str,
    source_id: str,
    document_id: str,
) -> tuple[bool, str]:
    prompt = (
        "The rewritten sentence must be faithful to the original. "
        "Return JSON with faithful true/false and a list of violations such as numbers, dates, "
        "entities, negation, comparison, causality, superlatives, or modality.\n"
        f"ORIGINAL: {original}\nREWRITTEN: {rewritten}"
    )
    result = _model_call(
        gateway, budget, ledger, cache, run_id=run_id, task_type="fidelity", tier="cheap",
        evidence=original[:1500], prompt=prompt, source_id=source_id, document_id=document_id,
        escalation_reason="fidelity",
        response_schema=_FIDELITY_SCHEMA,
    )
    if result is None:
        return False, "fidelity_judge_failed_or_budget"
    try:
        payload = json.loads(result.content)
        return bool(payload["faithful"]), "fidelity_ok"
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return False, "malformed_fidelity_judge"


def run_quality(
    candidate: KnowledgeCandidate,
    source,
    document: SourceDocument,
    chunks: list[Chunk],
    gateway: ModelGateway,
    budget: QualityBudget,
    ledger: ModelLedger,
    cache: ModelCache,
    *,
    run_id: str,
    escalation: Escalation,
    source_id: str,
    contract: str,
) -> QualityOutcome:
    """Escalate one candidate through the bounded quality lane."""
    chunk = next((item for item in chunks if item.id == (candidate.evidence[0].chunk_id or "")), None)
    if chunk is None:
        return QualityOutcome(None, True, "missing_evidence_chunk")

    def fallback_to_original() -> QualityOutcome:
        verification = verify_candidate(candidate, source, document, chunks)
        if verification.playable:
            return QualityOutcome(candidate, False, "kept_original", verification)
        return QualityOutcome(None, True, "no_playable_fallback")

    reason = escalation.reason
    if reason is EscalationReason.POLICY_AMBIGUITY:
        # Resolve policy-sensitive ambiguity conservatively: never spend tokens
        # to polish a claim the deterministic risk gate already flagged.
        return QualityOutcome(None, True, "policy_ambiguity_rejected")

    if reason is EscalationReason.NON_ENGLISH:
        evidence_text = chunk.text
        english, why = _translate(
            evidence_text, gateway, budget, ledger, cache,
            run_id=run_id, source_id=source_id, document_id=document.id,
        )
        if english is None:
            return QualityOutcome(None, True, why)
        final = make_candidate(
            document, chunk, english,
            provenance=ProvenanceClass.DERIVED_MODEL,
            why="model-translated fact",
            extractor_version=contract,
        )
        verification = _verify_final(
            final, source, document, chunks, gateway, budget, ledger, cache,
            run_id=run_id, escalation_reason="non_english", source_id=source_id,
        )
        if verification.playable:
            return QualityOutcome(final, False, "translated", verification)
        return QualityOutcome(None, True, "translation_not_verified")

    if reason is EscalationReason.MULTI_CLAIM:
        task_type = "extract"
    elif reason is EscalationReason.FIDELITY_REWRITE:
        task_type = "rewrite"
    else:
        task_type = None

    if task_type is not None:
        text, why = _rewrite_or_extract(
            candidate.atom.statement, task_type, gateway, budget, ledger, cache,
            run_id=run_id, source_id=source_id, document_id=document.id,
        )
        if text is None:
            if not escalation.required:
                return fallback_to_original()
            return QualityOutcome(None, True, why)
        final = make_candidate(
            document, chunk, text,
            provenance=ProvenanceClass.DERIVED_MODEL,
            why=f"model-{task_type} fact",
            extractor_version=contract,
        )
        verification = _verify_final(
            final, source, document, chunks, gateway, budget, ledger, cache,
            run_id=run_id, escalation_reason=reason.value, source_id=source_id,
        )
        if verification.playable:
            return QualityOutcome(final, False, f"{task_type}ed", verification)
        if not escalation.required:
            return fallback_to_original()
        return QualityOutcome(None, True, f"{task_type}_not_verified")

    # WEAK_DIRECT_SUPPORT: verify the existing candidate with a bounded model judge.
    verification = _verify_final(
        candidate, source, document, chunks, gateway, budget, ledger, cache,
        run_id=run_id, escalation_reason=reason.value, source_id=source_id,
    )
    if verification.playable:
        return QualityOutcome(candidate, False, "model_verified", verification)
    return QualityOutcome(None, True, "model_verify_rejected")