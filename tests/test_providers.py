"""Provider registry and capability honesty (Execution 02 Child A)."""

import json
from datetime import UTC, datetime
from pathlib import Path

from curiosity.config.settings import capability_state, load_config, provider_readiness
from curiosity.contracts.models import (
    Chunk,
    ProvenanceClass,
    SourceDocument,
    SourceRecord,
    SourceType,
    TrustClass,
    deterministic_id,
)
from curiosity.providers import build_gateway
from curiosity.store import LocalStore

NOW = datetime(2026, 9, 3, tzinfo=UTC)


def write_config(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_gateway_builds_real_endpoint_through_cli_path(tmp_path):
    config = load_config(
        config_path=write_config(
            tmp_path / "config.toml",
            'provider_api_key = "sk-test"\nprovider_model = "gpt-4o-mini"\n'
            'provider_base_url = "https://example.test/v1"\nprovider_strong_model = "gpt-4o"\n'
            'provider_max_calls = 7\nprovider_prices = { input = 0.5, output = 1.5 }\n',
        ),
        env={},
        cli={"data_path": tmp_path / "data"},
    )
    gateway = build_gateway(config)
    assert gateway is not None
    assert gateway.cheap.model_id == "gpt-4o-mini"
    assert gateway.strong is not None and gateway.strong.model_id == "gpt-4o"
    assert gateway.max_calls == 7
    assert gateway.prices == {"input": 0.5, "output": 1.5}
    assert gateway.cheap.capabilities.supports_structured
    assert gateway.cheap.capabilities.supports_prompt_cache
    assert not gateway.cheap.capabilities.supports_batch
    assert gateway.cost_for(1_000_000, 500_000) == 0.5 + 0.75


def test_gateway_is_none_without_key_or_model(tmp_path):
    no_key = load_config(
        config_path=write_config(tmp_path / "a.toml", 'provider_model = "gpt-4o-mini"\n'),
        env={},
        cli={"data_path": tmp_path / "d1"},
    )
    assert build_gateway(no_key) is None
    no_model = load_config(
        config_path=write_config(tmp_path / "b.toml", 'provider_api_key = "sk-test"\n'),
        env={},
        cli={"data_path": tmp_path / "d2"},
    )
    assert build_gateway(no_model) is None


def test_capability_state_matches_constructibility(tmp_path):
    offline = load_config(
        config_path=write_config(tmp_path / "c.toml", ""), env={},
        cli={"data_path": tmp_path / "d3"},
    )
    assert "offline" in capability_state(offline)["model_generation"]
    missing_model = load_config(
        config_path=write_config(tmp_path / "d.toml", 'provider_api_key = "sk-test"\n'),
        env={},
        cli={"data_path": tmp_path / "d4"},
    )
    state = capability_state(missing_model)["model_generation"]
    assert "offline" in state and "no provider model" in state
    ready, _ = provider_readiness(missing_model)
    assert not ready and build_gateway(missing_model) is None
    configured = load_config(
        config_path=write_config(
            tmp_path / "e.toml", 'provider_api_key = "sk-test"\nprovider_model = "gpt-4o-mini"\n'
        ),
        env={},
        cli={"data_path": tmp_path / "d5"},
    )
    assert "configured" in capability_state(configured)["model_generation"]
    assert build_gateway(configured) is not None


def test_provider_types_never_leak_into_persisted_canonical_payloads(tmp_path):
    source_id = deterministic_id("source", "leak")
    document_id = deterministic_id("document", "leak")
    chunk_id = deterministic_id("chunk", "leak")
    with LocalStore(tmp_path / "curiosity.db") as store:
        store.put_source(
            SourceRecord(
                id=source_id,
                source_type=SourceType.NOTE,
                canonical_locator="local://leak",
                title="Leak",
                trust=TrustClass.LOCAL,
                provenance=ProvenanceClass.USER_AUTHORED,
                retrieved_at=NOW,
            )
        )
        store.put_document(
            SourceDocument(
                id=document_id,
                source_id=source_id,
                content_sha256="b" * 64,
                raw_text="raw",
                captured_at=NOW,
                provenance=ProvenanceClass.SOURCE,
            )
        )
        store.put_chunk(
            Chunk(
                id=chunk_id,
                document_id=document_id,
                ordinal=0,
                text="A claim that must stay clean.",
                char_start=0,
                char_end=29,
                provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
            )
        )
        card_id = deterministic_id("card", "leak")
        atom_id = deterministic_id("atom", "leak")
        evidence_id = deterministic_id("evidence", "leak")
        from curiosity.contracts.models import (
            CardType,
            ClaimStatus,
            CuriosityCard,
            CuriosityPulse,
            Evidence,
            EvidenceSupport,
            KnowledgeAtom,
        )

        store.put_card(
            CuriosityCard(
                id=card_id,
                card_type=CardType.QUESTION,
                prompt="A claim that must stay clean.",
                atom_ids=(atom_id,),
                evidence_ids=(evidence_id,),
                provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
                created_at=NOW,
            )
        )
        store.put_atom(
            KnowledgeAtom(
                id=atom_id,
                statement="A claim that must stay clean.",
                claim_status=ClaimStatus.SUPPORTED,
                evidence_ids=(evidence_id,),
                provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
                created_at=NOW,
            )
        )
        store.put_evidence(
            Evidence(
                id=evidence_id,
                source_id=source_id,
                document_id=document_id,
                chunk_id=chunk_id,
                quote="A claim that must stay clean.",
                support=EvidenceSupport.DIRECT,
                provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
            )
        )
        for table in ("sources", "documents", "chunks", "cards", "atoms", "evidence"):
            for row in store.connection.execute(f"SELECT payload_json FROM {table}"):
                payload = json.loads(row["payload_json"])
                for key in ("api_key", "base_url", "model_id", "capabilities"):
                    assert key not in payload, f"{table} leaked {key}"
        store.put_pulse(
            CuriosityPulse(
                id=deterministic_id("pulse", "leak"),
                card_id=card_id,
                atom_id=atom_id,
                display_fact="A claim that must stay clean.",
                source_id=source_id,
                document_id=document_id,
                evidence_ids=(evidence_id,),
                verified_at=NOW,
                provenance=ProvenanceClass.DERIVED_DETERMINISTIC,
            ),
            verification={"status": "verified", "reason_codes": [], "risk_flags": [], "provider_used": False},
        )
        payload = json.loads(
            store.connection.execute("SELECT payload_json FROM pulses").fetchone()[0]
        )
        for key in ("api_key", "base_url", "model_id", "capabilities"):
            assert key not in payload