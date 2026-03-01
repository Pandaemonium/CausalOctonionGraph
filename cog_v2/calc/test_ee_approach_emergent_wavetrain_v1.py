from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_ee_approach_emergent_wavetrain_v1 import (
    OUT_JSON,
    OUT_MD,
    SimulationParams,
    build_payload,
    write_artifacts,
)


def test_payload_deterministic() -> None:
    a = build_payload()
    b = build_payload()
    assert a["replay_hash"] == b["replay_hash"]
    assert a["simulation"]["summary"] == b["simulation"]["summary"]


def test_expected_shape_and_emergence_signal() -> None:
    payload = build_payload()
    assert payload["schema_version"] == "ee_approach_emergent_wavetrain_v1"
    assert payload["kernel_profile"] == "cog_v2_projective_unity_v1"
    assert payload["projector_id"] == "pi_unity_axis_dominance_v1"

    sim = payload["simulation"]
    rows = list(sim["tick_rows"])
    summary = sim["summary"]
    assert len(rows) == int(sim["params"]["ticks"])
    assert int(summary["recorded_row_count"]) == len(rows)
    assert int(summary["total_tick_count"]) == int(sim["params"]["ticks"])
    assert int(sim["params"]["thin_output_step"]) == 1
    assert all(len(r["left_state_vector"]) == 8 for r in rows)
    assert all(len(r["right_state_vector"]) == 8 for r in rows)
    assert all(len(r["mediator_state_vector"]) == 8 for r in rows)
    assert summary["first_interaction_tick"] is not None
    assert summary["first_wavetrain_tick"] is not None
    assert float(summary["max_wavetrain_coherence"]) > 0.0
    assert bool(summary["any_reversal"]) is True
    assert bool(summary["any_separation_after_approach"]) is True


def test_thin_output_mode_keeps_key_rows() -> None:
    payload = build_payload(
        params=SimulationParams(
            ticks=4000,
            x_left_0=-400.0,
            x_right_0=400.0,
            thin_output_step=100,
        )
    )
    sim = payload["simulation"]
    rows = list(sim["tick_rows"])
    summary = sim["summary"]
    assert int(sim["params"]["thin_output_step"]) == 100
    assert len(rows) < int(sim["params"]["ticks"])
    assert rows[0]["tick"] == 0
    assert rows[-1]["tick"] == int(sim["params"]["ticks"]) - 1
    assert int(summary["recorded_row_count"]) == len(rows)
    # key event ticks should be retained even if not on stride boundary
    event_ticks = {
        int(summary["first_interaction_tick"]),
        int(summary["first_wavetrain_tick"]),
        int(summary["first_separation_tick"]),
    }
    row_ticks = {int(r["tick"]) for r in rows}
    assert event_ticks.issubset(row_ticks)


def test_write_artifacts(tmp_path: Path) -> None:
    payload = build_payload(params=SimulationParams(ticks=64))
    out_json = tmp_path / OUT_JSON.name
    out_md = tmp_path / OUT_MD.name
    write_artifacts(payload, json_paths=[out_json], md_paths=[out_md])
    assert out_json.exists()
    assert out_md.exists()
    loaded = json.loads(out_json.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
    md = out_md.read_text(encoding="utf-8")
    assert "Two-Electron Approach Emergent Wavetrain (v1)" in md
    assert "Outcome Summary" in md
