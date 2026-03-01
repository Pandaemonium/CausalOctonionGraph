from __future__ import annotations

import json

from cog_v2.calc.build_weinberg_ir_bridge_combinatoric_exact_v2 import (
    OUT_JSON,
    OUT_MD,
    _derive_leakage_coeff,
    _derive_uv_anchor,
    build_payload,
    write_artifacts,
)


def test_combinatoric_constants_exact() -> None:
    uv_anchor = _derive_uv_anchor()
    leakage_coeff = _derive_leakage_coeff()
    assert uv_anchor.numerator == 1
    assert uv_anchor.denominator == 4
    assert leakage_coeff.numerator == 1
    assert leakage_coeff.denominator == 7


def test_payload_deterministic() -> None:
    a = build_payload()
    b = build_payload()
    assert a["replay_hash"] == b["replay_hash"]
    assert a["stationary_summary"] == b["stationary_summary"]


def test_payload_expected_shape() -> None:
    payload = build_payload()
    assert payload["schema_version"] == "weinberg_ir_bridge_combinatoric_exact_v2"
    assert payload["claim_id"] == "WEINBERG-001"
    assert payload["preregistered_inputs"]["policy_id"] == "weinberg_ir_bridge_combinatoric_exact_v2"
    assert payload["preregistered_inputs"]["kernel_profile_id"] == "cog_v2_projective_unity_v1"

    constants = payload["combinatoric_constants"]
    assert constants["uv_anchor"]["rational"] == "1/4"
    assert constants["leakage_coeff"]["rational"] == "1/7"

    rows = payload["running_trace"]
    assert len(rows) == 65
    assert rows[0]["direct_sin2_theta_w"]["rational"] == "1/4"

    checks = payload["checks"]
    assert checks["uv_anchor_exact_at_tick0"] is True
    assert checks["stationary_period_detected"] is True
    assert checks["combinatoric_constants_exact"] is True
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
    assert "WEINBERG IR Bridge with Exact Combinatoric Constants (v2)" in md
    assert "Exact Constants (No Tuning)" in md
