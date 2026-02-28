from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_triplet_decay_exact_simulation_v1 import (
    OUT_JSON,
    OUT_MD,
    SimulationParams,
    build_payload,
    write_artifacts,
)


def test_payload_deterministic() -> None:
    p1 = build_payload(params=SimulationParams(ticks=64))
    p2 = build_payload(params=SimulationParams(ticks=64))
    assert p1["replay_hash"] == p2["replay_hash"]
    assert p1["summary"] == p2["summary"]


def test_default_payload_expected_properties() -> None:
    payload = build_payload()
    assert payload["schema_version"] == "triplet_decay_exact_simulation_v1"
    assert payload["kernel_profile"] == "cog_v2_projective_unity_v1"
    assert payload["projector_id"] == "pi_unity_axis_dominance_v1"
    assert payload["summary"]["scenario_count"] == 2
    assert payload["summary"]["decay_hit_count"] >= 1
    assert payload["summary"]["xy_proxy_decay_hit_count"] >= 1

    by_pert = {str(s["perturber_motif_id"]): s for s in payload["scenarios"]}
    assert "high_energy_perturber_v1" in by_pert
    assert "xy_gut_boson_proxy_v1" in by_pert

    for sc in payload["scenarios"]:
        ss = sc["summary"]
        rows = list(sc["tick_rows"])
        assert len(rows) == int(sc["params"]["ticks"])
        assert bool(ss["any_motif_break"]) is True
        assert bool(ss["any_decay"]) is True
        assert int(ss["first_motif_break_tick"]) >= 0
        for row in rows:
            assert len(row["quark_state_vector"]) == 8
            assert len(row["perturber_state_vector"]) == 8


def test_write_artifacts(tmp_path: Path) -> None:
    payload = build_payload(params=SimulationParams(ticks=24))
    out_json = tmp_path / OUT_JSON.name
    out_md = tmp_path / OUT_MD.name
    write_artifacts(payload, json_paths=[out_json], md_paths=[out_md])
    assert out_json.exists()
    assert out_md.exists()
    loaded = json.loads(out_json.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
    md = out_md.read_text(encoding="utf-8")
    assert "Triplet Decay Exact Simulation (v1)" in md
    assert "xy_gut_boson_proxy_v1" in md

