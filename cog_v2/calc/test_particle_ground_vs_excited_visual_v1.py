from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_particle_ground_vs_excited_visual_v1 import (
    OUT_JSON,
    OUT_MD,
    VizParams,
    build_payload,
    write_artifacts,
)


def test_payload_deterministic_no_render() -> None:
    params = VizParams(
        particle_id="left_spinor_muon_motif",
        ticks_ground=14,
        burn_in_ground=4,
        max_period_ground=8,
        size_xyz_ground=7,
        render_gif=False,
    )
    a = build_payload(params)
    b = build_payload(params)
    assert a["replay_hash"] == b["replay_hash"]
    assert [l["period_ticks"] for l in a["lanes"]] == [l["period_ticks"] for l in b["lanes"]]


def test_schema_and_lane_shapes() -> None:
    payload = build_payload(
        VizParams(
            particle_id="left_spinor_tau_motif",
            ticks_ground=14,
            burn_in_ground=4,
            max_period_ground=8,
            size_xyz_ground=7,
            render_gif=False,
        )
    )
    assert payload["schema_version"] == "particle_ground_vs_excited_visual_v1"
    assert len(payload["lanes"]) == 3
    assert payload["lanes"][0]["energy_id"] == "E0_control"
    assert payload["lanes"][1]["energy_id"].startswith("E")
    assert payload["lanes"][2]["energy_id"].startswith("E")
    assert payload["gif_repo_path"] is None


def test_write_artifacts(tmp_path: Path) -> None:
    payload = build_payload(
        VizParams(
            particle_id="left_spinor_muon_motif",
            ticks_ground=14,
            burn_in_ground=4,
            max_period_ground=8,
            size_xyz_ground=7,
            render_gif=False,
        )
    )
    out_json = tmp_path / OUT_JSON.name
    out_md = tmp_path / OUT_MD.name
    write_artifacts(payload, json_paths=[out_json], md_paths=[out_md])
    assert out_json.exists()
    assert out_md.exists()
    loaded = json.loads(out_json.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
    md = out_md.read_text(encoding="utf-8")
    assert "Particle Ground vs Excited Visualization (v1)" in md
