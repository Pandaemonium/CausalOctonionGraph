from __future__ import annotations

import json

from cog_v2.calc.build_theta001_uv_exhaustive_microstates_v1 import (
    OUT_JSON,
    OUT_MD,
    build_payload,
    write_artifacts,
)


def test_payload_deterministic_subset() -> None:
    a = build_payload(max_states=625)
    b = build_payload(max_states=625)
    assert a["replay_hash"] == b["replay_hash"]
    assert a["global_checks"] == b["global_checks"]


def test_payload_expected_structure_subset() -> None:
    payload = build_payload(max_states=625)
    assert payload["schema_version"] == "theta001_uv_exhaustive_microstates_v1"
    assert payload["event_semantics"]["states_are_events"] is True
    assert payload["state_space"]["enumeration_mode"] == "bounded_subset"
    assert payload["global_checks"]["all_lanes_all_ticks_hold"] is True
    assert payload["global_checks"]["all_lanes_full_exhaustive"] is False
    assert isinstance(payload["uv_lanes"], list)
    assert len(payload["uv_lanes"]) == 2
    for lane in payload["uv_lanes"]:
        assert lane["lane_all_ticks_hold"] is True
        assert lane["full_exhaustive"] is False
        assert lane["enumerated_microstates"] == 625
        assert lane["ticks"] == 4
        rows = lane["tick_rows"]
        assert len(rows) == 5
        for r in rows:
            assert r["cp_dual_parity_holds_all"] is True
            assert r["expected_mode_holds_all"] is True
            assert r["strong_cp_delta_sum"] == 0
            assert r["strong_dual_delta_sum"] == 0


def test_write_artifacts_subset(tmp_path) -> None:
    payload = build_payload(max_states=625)
    json_path = tmp_path / OUT_JSON.name
    md_path = tmp_path / OUT_MD.name
    write_artifacts(payload, json_paths=[json_path], md_paths=[md_path])
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
    md = md_path.read_text(encoding="utf-8")
    assert "THETA-001 UV Exhaustive Microstate/Event Witness (v1)" in md
    assert "states_are_events" in md
    assert "Global Checks" in md
