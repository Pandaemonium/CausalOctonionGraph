from __future__ import annotations

import json

from cog_v2.calc.build_theta001_continuum_bridge_v2 import (
    OUT_JSON,
    OUT_MD,
    build_continuum_bridge_payload,
    write_artifacts,
)


def test_continuum_bridge_payload_is_deterministic() -> None:
    a = build_continuum_bridge_payload()
    b = build_continuum_bridge_payload()
    assert a["replay_hash"] == b["replay_hash"]
    assert a["depth_schedule"] == b["depth_schedule"]
    assert a["convergence_diagnostics"] == b["convergence_diagnostics"]


def test_continuum_bridge_payload_has_expected_properties() -> None:
    payload = build_continuum_bridge_payload()
    assert payload["schema_version"] == "theta001_continuum_bridge_v2"
    assert payload["claim_id"] == "THETA-001"
    assert payload["continuum_identification_contract"]["rfc_id"] == "RFC-003"
    assert payload["continuum_identification_contract"]["policy_id"] == "theta_continuum_linear_identification_v1"
    assert payload["continuum_identification_contract"]["discrete_correction_envelope_id"] == "theta_discrete_correction_envelope_v1"
    assert payload["continuum_identification_contract"]["discrete_correction_robustness_id"] == "theta_discrete_correction_envelope_robustness_v1"
    assert isinstance(payload["depth_rows"], list)
    assert len(payload["depth_rows"]) > 0
    envelope = payload["discrete_correction_envelope"]
    assert envelope["envelope_id"] == "theta_discrete_correction_envelope_v1"
    assert envelope["distance_axis_id"] == "graph_distance_tick_index_v1"
    assert envelope["robustness_envelope_id"] == "theta_discrete_correction_envelope_robustness_v1"
    assert envelope["base_correction_lane_ready"] is True
    assert envelope["robustness_lane_ready"] is True
    assert envelope["correction_lane_ready"] is True
    assert payload["continuum_bridge_readiness"]["finite_size_residual_stable_zero"] is True
    assert payload["continuum_bridge_readiness"]["normalized_residual_stable_zero"] is True
    assert payload["continuum_bridge_readiness"]["discrete_correction_lane_ready"] is True
    assert payload["continuum_bridge_readiness"]["discrete_correction_robustness_ready"] is True
    assert payload["continuum_bridge_readiness"]["full_value_closure_ready"] is False
    targets = payload["continuum_identification_contract"]["lean_theorem_targets"]
    assert "CausalGraphV2.theta_qcd_zero_under_locked_identification_v1" in targets


def test_write_continuum_bridge_artifacts(tmp_path) -> None:
    payload = build_continuum_bridge_payload()
    json_path = tmp_path / OUT_JSON.name
    md_path = tmp_path / OUT_MD.name
    write_artifacts(payload, json_paths=[json_path], md_paths=[md_path])
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
    md = md_path.read_text(encoding="utf-8")
    assert "THETA-001 Continuum Bridge Diagnostics (v2)" in md
    assert "Depth Sweep" in md
    assert "Discrete Correction Envelope" in md
