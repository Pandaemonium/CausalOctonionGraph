"""Tests for calc/build_theta001_bridge_closure.py."""

from __future__ import annotations

import json
from pathlib import Path

from calc.build_theta001_bridge_closure import (
    OUT_JSON,
    OUT_MD,
    build_bridge_closure_payload,
    write_artifacts,
)


def test_bridge_closure_payload_is_deterministic() -> None:
    a = build_bridge_closure_payload()
    b = build_bridge_closure_payload()
    assert a["replay_hash"] == b["replay_hash"]
    assert a["weak_leakage_suite"] == b["weak_leakage_suite"]


def test_bridge_closure_payload_has_expected_properties() -> None:
    payload = build_bridge_closure_payload()
    assert payload["schema_version"] == "theta001_bridge_closure_v1"
    assert payload["claim_id"] == "THETA-001"
    assert payload["discrete_cp_residual"]["signed_sum"] == 0
    assert payload["discrete_cp_residual"]["is_zero"] is True
    assert payload["weak_leakage_suite"]["all_zero"] is True
    assert payload["weak_leakage_suite"]["max_abs_residual"] == 0
    assert payload["bridge_ready_supported_bridge"] is True
    assert "CausalGraph.theta_zero_if_linear_bridge" in payload["continuum_bridge_contract"]["lean_theorems"]


def test_write_bridge_closure_artifacts(tmp_path: Path) -> None:
    payload = build_bridge_closure_payload()
    json_path = tmp_path / OUT_JSON.name
    md_path = tmp_path / OUT_MD.name
    write_artifacts(payload, json_paths=[json_path], md_paths=[md_path])

    assert json_path.exists()
    assert md_path.exists()
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
    md = md_path.read_text(encoding="utf-8")
    assert "THETA-001 Bridge Closure Artifact" in md
    assert "bridge_ready_supported_bridge" in md
