from __future__ import annotations

import json

from cog_v2.calc.build_alpha_ir_bridge_combinatoric_exact_v1 import (
    OUT_JSON,
    OUT_MD,
    _derive_degeneracy_subtract_card,
    _derive_line_cardinality,
    _derive_points_per_line,
    build_payload,
    write_artifacts,
)


def test_combinatoric_constants_exact() -> None:
    assert _derive_line_cardinality() == 7
    assert _derive_points_per_line() == 3
    assert _derive_degeneracy_subtract_card() == 2


def test_payload_deterministic() -> None:
    a = build_payload()
    b = build_payload()
    assert a["replay_hash"] == b["replay_hash"]
    assert a["combinatoric_constants"] == b["combinatoric_constants"]


def test_payload_expected_shape() -> None:
    payload = build_payload()
    assert payload["schema_version"] == "alpha_ir_bridge_combinatoric_exact_v1"
    assert payload["claim_id"] == "ALPHA-001"
    assert payload["preregistered_inputs"]["policy_id"] == "alpha_ir_bridge_combinatoric_exact_v1"
    assert payload["preregistered_inputs"]["map_family_id"] == "alpha_denominator_fano_cubic_minus_degeneracy_v1"
    assert payload["preregistered_inputs"]["posthoc_parameter_update"] is False

    constants = payload["combinatoric_constants"]
    assert constants["fano_line_cardinality"] == 7
    assert constants["points_per_fano_line"] == 3
    assert constants["degeneracy_subtract_cardinality"] == 2
    assert constants["uv_anchor"]["rational"] == "1/49"
    assert constants["alpha_denominator"] == 145

    obs = payload["observables"]
    assert obs["alpha_bridge"]["rational"] == "1/145"
    assert obs["value_match"] is True

    checks = payload["checks"]
    assert checks["combinatoric_constants_exact"] is True
    assert checks["denominator_identity_exact"] is True
    assert checks["bridge_formula_locked"] is True
    assert checks["no_output_tuned_parameter"] is True
    assert checks["value_within_6pct_target"] is True
    assert payload["bridge_pass"] is True


def test_write_artifacts(tmp_path) -> None:
    payload = build_payload()
    json_path = tmp_path / OUT_JSON.name
    md_path = tmp_path / OUT_MD.name
    write_artifacts(payload, json_paths=[json_path], md_paths=[md_path])
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
    md = md_path.read_text(encoding="utf-8")
    assert "ALPHA IR Bridge with Exact Combinatoric Constants (v1)" in md
    assert "Exact Constants (No Tuning)" in md

