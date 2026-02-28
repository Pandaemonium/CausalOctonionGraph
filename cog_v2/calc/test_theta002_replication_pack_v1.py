from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_theta002_replication_pack_v1 import (
    OUT_JSON,
    OUT_MD,
    build_payload,
    write_artifacts,
)


def test_payload_deterministic() -> None:
    a = build_payload()
    b = build_payload()
    assert a["replay_hash"] == b["replay_hash"]
    assert a["selection"] == b["selection"]
    assert a["smoke_test"] == b["smoke_test"]


def test_payload_expected_properties() -> None:
    payload = build_payload()
    assert payload["schema_version"] == "theta002_replication_pack_v1"
    assert payload["claim_id"] == "THETA-002"
    assert payload["selection"]["selected_total"] == 4
    assert payload["smoke_test"]["scenario_count"] == 4
    assert payload["smoke_test"]["all_squared_zero_expected"] is True
    assert payload["smoke_test"]["all_oriented_cubic_excluding_t0_nonzero_expected"] is True
    for s in payload["scenarios"]:
        assert "scenario_hash" in s
        assert int(s["expected_output"]["squared_residual"]) == 0
        assert int(s["expected_output"]["oriented_cubic_residual_excluding_t0"]) != 0


def test_write_artifacts(tmp_path: Path) -> None:
    payload = build_payload()
    json_path = tmp_path / OUT_JSON.name
    md_path = tmp_path / OUT_MD.name
    scenario_dir = tmp_path / "scenario_bundle"
    write_artifacts(payload, json_paths=[json_path], md_paths=[md_path], scenario_root=scenario_dir)
    assert json_path.exists()
    assert md_path.exists()
    assert scenario_dir.exists()
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
    md = md_path.read_text(encoding="utf-8")
    assert "THETA-002 Replication Pack (v1)" in md
    files = list(scenario_dir.glob("*.json"))
    assert len(files) == 4

