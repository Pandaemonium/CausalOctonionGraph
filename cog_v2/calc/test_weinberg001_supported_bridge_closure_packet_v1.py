from __future__ import annotations

import json

from cog_v2.calc.build_weinberg001_supported_bridge_closure_packet_v1 import (
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


def test_payload_shape() -> None:
    payload = build_payload()
    assert payload["schema_version"] == "weinberg001_supported_bridge_closure_packet_v1"
    assert payload["claim_id"] == "WEINBERG-001"
    assert payload["supported_bridge_evidence"]["required_checks_all_true"] is True
    assert payload["supported_bridge_evidence"]["bridge_pass"] is True
    assert payload["recommendation"]["supported_bridge_now"] is True
    assert payload["recommendation"]["proved_core_now"] is False


def test_write_artifacts(tmp_path) -> None:
    payload = build_payload()
    json_path = tmp_path / OUT_JSON.name
    md_path = tmp_path / OUT_MD.name
    write_artifacts(payload, json_paths=[json_path], md_paths=[md_path])
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
    md = md_path.read_text(encoding="utf-8")
    assert "WEINBERG-001 Supported-Bridge Closure Packet (v1)" in md
