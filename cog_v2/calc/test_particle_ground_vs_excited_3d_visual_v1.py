from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_particle_ground_vs_excited_3d_visual_v1 import (
    OUT_JSON,
    OUT_MD,
    Viz3DParams,
    build_payload,
    write_artifacts,
)


def test_payload_deterministic_no_render() -> None:
    params = Viz3DParams(
        particle_id="left_spinor_muon_motif",
        fps=2,
        dpi=120,
        render_gif=False,
    )
    a = build_payload(params)
    b = build_payload(params)
    assert a["replay_hash"] == b["replay_hash"]
    assert [l["period_ticks"] for l in a["lanes"]] == [l["period_ticks"] for l in b["lanes"]]


def test_schema_and_artifact_paths_no_render() -> None:
    payload = build_payload(
        Viz3DParams(
            particle_id="left_spinor_muon_motif",
            fps=2,
            dpi=120,
            render_gif=False,
        )
    )
    assert payload["schema_version"] == "particle_ground_vs_excited_3d_visual_v1"
    assert len(payload["lanes"]) == 3
    assert payload["lanes"][0]["energy_id"] == "E0_control"
    assert payload["overview_gif_repo_path"] is None
    assert payload["channel16_gif_repo_path"] is None
    assert payload["overview_render"]["frame_count"] == 0
    assert payload["channel16_render"]["frame_count"] == 0


def test_write_artifacts(tmp_path: Path) -> None:
    payload = build_payload(
        Viz3DParams(
            particle_id="left_spinor_muon_motif",
            fps=2,
            dpi=120,
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
    assert "Particle Ground vs Excited 3D Visualization (v1)" in md
