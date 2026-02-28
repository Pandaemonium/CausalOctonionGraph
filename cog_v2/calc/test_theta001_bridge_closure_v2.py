from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_theta001_bridge_closure_v2 import (
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
    assert a["ckm_like_weak_leakage_suite"] == b["ckm_like_weak_leakage_suite"]


def test_bridge_closure_payload_has_expected_properties() -> None:
    payload = build_bridge_closure_payload()
    assert payload["schema_version"] == "theta001_bridge_closure_v2"
    assert payload["claim_id"] == "THETA-001"
    assert payload["fano_sign_balance"]["signed_sum"] == 0
    assert payload["orientation_reversal_closed_on_fano_lines"] is True
    assert payload["weak_leakage_suite"]["all_zero"] is True
    assert payload["ckm_like_weak_leakage_suite"]["all_zero"] is True
    assert payload["periodic_angle_lane"]["status"] == "stub_non_blocking"
    assert payload["periodic_angle_lane"]["promotion_blocking"] is False
    linear_lane = payload["continuum_bridge_contract"]["linear_map_lane"]
    assert linear_lane["status"] == "primary_blocking"
    assert linear_lane["promotion_blocking"] is True
    assert linear_lane["cp_odd_all_hold"] is True
    assert linear_lane["zero_anchor_all_hold"] is True
    assert payload["lean_bridge_file"] == "cog_v2/lean/CausalGraphV2/ThetaEFTBridge.lean"
    theorems = payload["continuum_bridge_contract"]["lean_theorems"]
    assert "CausalGraphV2.theta_zero_if_linear_bridge" in theorems
    assert "CausalGraphV2.theta_zero_if_affine_bridge" in theorems
    assert "CausalGraphV2.theta_zero_if_zero_anchored_bridge" in theorems
    assert payload["bridge_ready_supported_bridge"] is True


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
    assert "THETA-001 Bridge Closure Artifact (v2)" in md
    assert "bridge_ready_supported_bridge" in md
