from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.theta_eft_map_v2 import (
    build_theta_eft_bridge_payload,
    q_density_proxy,
    q_top_proxy,
)
from cog_v2.scripts.run_theta_eft_sweep_v2 import OUT_JSON, OUT_MD, write_artifacts


def test_q_density_proxy_is_cp_odd_under_sign_flip() -> None:
    s = (0, 2, -3, 4, -5, 6, -7, 8)
    s_cp = (s[0], -s[1], -s[2], -s[3], -s[4], -s[5], -s[6], -s[7])
    assert q_density_proxy(s_cp) == -q_density_proxy(s)


def test_q_top_proxy_sums_density() -> None:
    trace = [
        (0, 1, 0, 0, 0, 0, 0, 1),
        (0, 2, 0, 0, 0, 0, 0, 1),
    ]
    assert q_top_proxy(trace) == q_density_proxy(trace[0]) + q_density_proxy(trace[1])


def test_theta_eft_payload_is_deterministic() -> None:
    a = build_theta_eft_bridge_payload()
    b = build_theta_eft_bridge_payload()
    assert a["replay_hash"] == b["replay_hash"]
    assert a["map_suite"] == b["map_suite"]
    assert a["q_top_proxy_suite"] == b["q_top_proxy_suite"]


def test_theta_eft_payload_has_expected_keys() -> None:
    payload = build_theta_eft_bridge_payload()
    assert payload["schema_version"] == "theta001_eft_bridge_v2"
    assert payload["claim_id"] == "THETA-001"
    assert "map_suite" in payload
    assert "map_identification" in payload
    assert "q_top_proxy_suite" in payload
    assert "continuum_eft_bridge_readiness" in payload
    assert payload["continuum_eft_bridge_readiness"]["cp_odd_proxy_consistent"] is True
    assert payload["map_identification"]["policy_id"] == "theta_map_identification_linear_unit_v1"
    assert payload["map_identification"]["selected_unique"] is True
    assert payload["map_identification"]["selected_map_id"] == "linear_scale_1_v1"
    assert payload["continuum_eft_bridge_readiness"]["map_identification_locked"] is True
    assert "CausalGraphV2.theta_zero_if_linear_bridge" in payload["lean_bridge_theorems"]
    assert "CausalGraphV2.theta_zero_if_zero_anchored_bridge" in payload["lean_bridge_theorems"]


def test_write_theta_eft_artifacts(tmp_path: Path) -> None:
    payload = build_theta_eft_bridge_payload()
    json_path = tmp_path / OUT_JSON.name
    md_path = tmp_path / OUT_MD.name
    write_artifacts(payload, json_paths=[json_path], md_paths=[md_path])

    assert json_path.exists()
    assert md_path.exists()
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
    md = md_path.read_text(encoding="utf-8")
    assert "THETA-001 EFT Bridge Probe (v2)" in md
    assert "Map Identification" in md
    assert "Q_top Proxy Suite" in md
