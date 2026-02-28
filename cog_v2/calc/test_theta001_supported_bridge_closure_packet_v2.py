from __future__ import annotations

import json

from cog_v2.calc.build_theta001_supported_bridge_closure_packet_v2 import (
    OUT_JSON,
    OUT_MD,
    build_payload,
    write_artifacts,
)


def test_payload_deterministic() -> None:
    a = build_payload()
    b = build_payload()
    assert a["replay_hash"] == b["replay_hash"]
    assert a["recommendation"] == b["recommendation"]
    assert a["supported_bridge_evidence"] == b["supported_bridge_evidence"]


def test_payload_expected_shape() -> None:
    payload = build_payload()
    assert payload["schema_version"] == "theta001_supported_bridge_closure_packet_v2"
    assert payload["claim_id"] == "THETA-001"
    assert payload["claim_status"] == "supported_bridge"
    assert payload["closure_scope"] == "structure_first"
    assert payload["all_gates_done"] is True
    assert payload["supported_bridge_evidence"]["triplet_robustness_lane"]["topology_family_count"] >= 2
    assert payload["recommendation"]["supported_bridge_now"] is True
    assert payload["recommendation"]["proved_core_now"] is False
    assert isinstance(payload["proved_core_blockers"], list)
    assert len(payload["proved_core_blockers"]) >= 3


def test_write_artifacts(tmp_path) -> None:
    payload = build_payload()
    json_path = tmp_path / OUT_JSON.name
    md_path = tmp_path / OUT_MD.name
    write_artifacts(payload, json_paths=[json_path], md_paths=[md_path])
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
    md = md_path.read_text(encoding="utf-8")
    assert "THETA-001 Supported-Bridge Closure Packet (v2)" in md
    assert "Proved-Core Blockers" in md
    assert "Required Next Steps" in md
