from __future__ import annotations

import json

from cog_v2.calc.build_weinberg_ir_bridge_microstate_v1 import (
    OUT_JSON,
    OUT_MD,
    build_payload,
    write_artifacts,
)


def test_payload_deterministic() -> None:
    a = build_payload()
    b = build_payload()
    assert a["replay_hash"] == b["replay_hash"]
    assert a["stationary_summary"] == b["stationary_summary"]


def test_payload_expected_shape() -> None:
    payload = build_payload()
    assert payload["schema_version"] == "weinberg_ir_bridge_microstate_v1"
    assert payload["claim_id"] == "WEINBERG-001"
    assert payload["preregistered_inputs"]["policy_id"] == "weinberg_ir_bridge_microstate_v1"
    assert payload["preregistered_inputs"]["kernel_profile_id"] == "cog_v2_projective_unity_v1"

    rows = payload["running_trace"]
    assert len(rows) == 65
    assert abs(float(rows[0]["direct_sin2_theta_w"]) - 0.25) < 1e-12

    checks = payload["checks"]
    assert checks["uv_anchor_exact_at_tick0"] is True
    assert checks["stationary_period_detected"] is True
    assert checks["no_output_tuned_parameter"] is True
    assert checks["ir_bridge_within_2pct_target"] is True
    assert payload["bridge_pass"] is True


def test_write_artifacts(tmp_path) -> None:
    payload = build_payload()
    json_path = tmp_path / OUT_JSON.name
    md_path = tmp_path / OUT_MD.name
    write_artifacts(payload, json_paths=[json_path], md_paths=[md_path])
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
    md = md_path.read_text(encoding="utf-8")
    assert "WEINBERG IR Bridge from Exact Lightcone Microstate (v1)" in md
    assert "Stationary Summary" in md
