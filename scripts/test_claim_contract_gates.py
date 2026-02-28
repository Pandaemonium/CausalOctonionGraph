"""Tests for THETA-specific contract gate checks (RFC-083)."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.claim_contract_gates import evaluate_contract_gates


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _theta_claim_doc(tmp_path: Path, *, verdict: str, gate3_done: bool) -> dict:
    _write_json(
        tmp_path / "sources" / "theta001_cp_witness.json",
        {"schema_version": "theta001_cp_witness_v1", "claim_id": "THETA-001"},
    )
    _write_json(
        tmp_path / "sources" / "theta001_skeptic_review.json",
        {
            "schema_version": "theta001_skeptic_review_v1",
            "claim_id": "THETA-001",
            "verdict": verdict,
            "reviewer_model_family": "gemini",
            "builder_model_family": "openai_gpt",
            "independent_from_builder": True,
        },
    )
    _write_json(
        tmp_path / "sources" / "theta001_bridge_closure.json",
        {
            "schema_version": "theta001_bridge_closure_v1",
            "claim_id": "THETA-001",
            "weak_leakage_suite": {"all_zero": True},
            "continuum_bridge_contract": {
                "conditional_conclusion_theta_zero": True,
                "lean_theorems": ["CausalGraph.theta_zero_if_linear_bridge"],
            },
        },
    )
    return {
        "id": "THETA-001",
        "contract_gates": {
            "required": ["rfc083"],
            "rfc083": {
                "closure_scope": "structure_first",
                "bridge_contract_id": "theta_cp_bridge_v1",
                "bridge_observable_id": "theta_cp_odd_residual_v1",
                "discrete_residual_artifact": "sources/theta001_cp_witness.json",
                "weak_leakage_artifact": "sources/theta001_bridge_closure.json",
                "eft_bridge_artifact": "sources/theta001_bridge_closure.json",
                "skeptic_review_artifact": "sources/theta001_skeptic_review.json",
                "skeptic_model_diversity_required": True,
                "skeptic_verdict": verdict,
            },
        },
        "gates": [{"id": "gate_3", "done": gate3_done}],
        "bridge_assumptions": [
            "Bridge from discrete CP residual to continuum theta-term remains explicit.",
        ],
        "falsification_condition": (
            "Claim is falsified if a CP-violating weak-sector perturbation induces non-zero "
            "strong-sector CP-odd residual after deterministic deep-cone updates."
        ),
    }


def test_theta_partial_allows_pending_skeptic_verdict(tmp_path: Path) -> None:
    rows = {"THETA-001": {"status": "partial"}}
    claim_docs = {"THETA-001": _theta_claim_doc(tmp_path, verdict="pending", gate3_done=False)}
    issues = evaluate_contract_gates(
        rows=rows,
        claim_docs=claim_docs,
        root=tmp_path,
        enforce_for_statuses={"partial"},
    )
    errors = [i for i in issues if i.severity == "error"]
    assert not errors


def test_theta_promoted_blocks_pending_skeptic_verdict(tmp_path: Path) -> None:
    rows = {"THETA-001": {"status": "supported_bridge"}}
    claim_docs = {"THETA-001": _theta_claim_doc(tmp_path, verdict="pending", gate3_done=False)}
    issues = evaluate_contract_gates(
        rows=rows,
        claim_docs=claim_docs,
        root=tmp_path,
        enforce_for_statuses={"supported_bridge"},
    )
    errors = [i.message for i in issues if i.severity == "error"]
    assert any("requires skeptic_verdict in PASS/PASS_WITH_LIMITS" in e for e in errors)


def test_theta_promoted_requires_gate3_done(tmp_path: Path) -> None:
    rows = {"THETA-001": {"status": "supported_bridge"}}
    claim_docs = {"THETA-001": _theta_claim_doc(tmp_path, verdict="PASS", gate3_done=False)}
    issues = evaluate_contract_gates(
        rows=rows,
        claim_docs=claim_docs,
        root=tmp_path,
        enforce_for_statuses={"supported_bridge"},
    )
    errors = [i.message for i in issues if i.severity == "error"]
    assert any("requires gates.gate_3 done=true" in e for e in errors)


def test_theta_promoted_passes_with_pass_and_gate3_done(tmp_path: Path) -> None:
    rows = {"THETA-001": {"status": "supported_bridge"}}
    claim_docs = {"THETA-001": _theta_claim_doc(tmp_path, verdict="PASS_WITH_LIMITS", gate3_done=True)}
    issues = evaluate_contract_gates(
        rows=rows,
        claim_docs=claim_docs,
        root=tmp_path,
        enforce_for_statuses={"supported_bridge"},
    )
    errors = [i for i in issues if i.severity == "error"]
    assert not errors


def test_theta_structure_first_blocks_proved_core(tmp_path: Path) -> None:
    rows = {"THETA-001": {"status": "proved_core"}}
    claim_docs = {"THETA-001": _theta_claim_doc(tmp_path, verdict="PASS", gate3_done=True)}
    issues = evaluate_contract_gates(
        rows=rows,
        claim_docs=claim_docs,
        root=tmp_path,
        enforce_for_statuses={"proved_core"},
    )
    errors = [i.message for i in issues if i.severity == "error"]
    assert any("closure_scope=structure_first cannot be promoted to proved_core" in e for e in errors)


def test_theta_promoted_blocks_when_weak_leakage_not_zero(tmp_path: Path) -> None:
    rows = {"THETA-001": {"status": "supported_bridge"}}
    doc = _theta_claim_doc(tmp_path, verdict="PASS", gate3_done=True)
    # Corrupt weak-leakage artifact to simulate a bridge failure.
    _write_json(
        tmp_path / "sources" / "theta001_bridge_closure.json",
        {
            "schema_version": "theta001_bridge_closure_v1",
            "claim_id": "THETA-001",
            "weak_leakage_suite": {"all_zero": False},
            "continuum_bridge_contract": {
                "conditional_conclusion_theta_zero": True,
                "lean_theorems": ["CausalGraph.theta_zero_if_linear_bridge"],
            },
        },
    )
    issues = evaluate_contract_gates(
        rows=rows,
        claim_docs={"THETA-001": doc},
        root=tmp_path,
        enforce_for_statuses={"supported_bridge"},
    )
    errors = [i.message for i in issues if i.severity == "error"]
    assert any("requires weak_leakage_suite.all_zero=true" in e for e in errors)
