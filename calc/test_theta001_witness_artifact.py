"""Tests for calc/build_theta001_witness.py."""

from __future__ import annotations

import json
from pathlib import Path

from calc.build_theta001_witness import (
    OUT_JSON,
    OUT_MD,
    build_witness_payload,
    write_artifacts,
)


def test_build_witness_payload_is_deterministic() -> None:
    a = build_witness_payload()
    b = build_witness_payload()
    assert a["replay_hash"] == b["replay_hash"]
    assert a["theta_residual_summary"] == b["theta_residual_summary"]
    assert a["trace_suite"] == b["trace_suite"]


def test_payload_has_expected_schema_and_zero_residual() -> None:
    payload = build_witness_payload()
    assert payload["schema_version"] == "theta001_cp_witness_v1"
    assert payload["claim_id"] == "THETA-001"
    assert payload["fano_sign_balance"]["positive_count"] == 21
    assert payload["fano_sign_balance"]["negative_count"] == 21
    assert payload["fano_sign_balance"]["signed_sum"] == 0
    assert payload["orientation_reversal_closed_on_fano_lines"] is True
    assert payload["weak_leakage_strong_residual"] == 0
    assert payload["theta_residual_summary"]["weak_leakage_strong_residual_zero"] is True
    assert payload["theta_residual_summary"]["theta_cp_odd_residual_forced_zero"] is True
    assert all(row["cp_dual_relation_holds"] is True for row in payload["trace_suite"])
    assert all(int(row["weighted_trace_delta"]) == 0 for row in payload["trace_suite"])


def test_source_hashes_look_valid() -> None:
    payload = build_witness_payload()
    assert len(payload["source_script_sha256"]) == 64
    assert len(payload["witness_module_sha256"]) == 64
    int(payload["source_script_sha256"], 16)
    int(payload["witness_module_sha256"], 16)


def test_write_artifacts_emits_json_and_markdown(tmp_path: Path) -> None:
    payload = build_witness_payload()
    json_path = tmp_path / OUT_JSON.name
    md_path = tmp_path / OUT_MD.name
    write_artifacts(payload, json_paths=[json_path], md_paths=[md_path])

    assert json_path.exists()
    assert md_path.exists()

    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
    md = md_path.read_text(encoding="utf-8")
    assert "THETA-001 CP-Invariance Witness" in md
    assert "theta_cp_odd_residual_forced_zero" in md
