from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_operational_kinematics_mass_energy_v1 import (
    OUT_JSON,
    OUT_MD,
    MeasureParams,
    build_payload,
    write_artifacts,
)


def test_payload_deterministic_small() -> None:
    params = MeasureParams(
        ticks=28,
        burn_in_ticks=10,
        measure_ticks=10,
        kick_ops=(1, 2),
        profiles=(
            ("test_1d_x11", 11, 1, 1),
            ("test_3d_x11_y3_z3", 11, 3, 3),
        ),
        particle_ids=("left_spinor_electron_ideal",),
        velocity_span_tol=0.25,
        delta_velocity_span_tol=0.25,
    )
    a = build_payload(params)
    b = build_payload(params)
    assert a["replay_hash"] == b["replay_hash"]
    assert a["checks"] == b["checks"]


def test_schema_and_fields() -> None:
    payload = build_payload(
        MeasureParams(
            ticks=24,
            burn_in_ticks=8,
            measure_ticks=10,
            kick_ops=(1,),
            profiles=(
                ("test_1d_x11", 11, 1, 1),
                ("test_3d_x11_y3_z3", 11, 3, 3),
            ),
            particle_ids=("left_spinor_electron_ideal",),
            velocity_span_tol=0.25,
            delta_velocity_span_tol=0.25,
        )
    )
    assert payload["schema_version"] == "operational_kinematics_mass_energy_v1"
    assert payload["checks"]["particle_count_processed"] == 1
    assert payload["checks"]["any_profile_elongated_x_over_10"] is True
    assert payload["checks"]["has_large_offaxis_profile_yz_ge_11"] is False
    assert len(payload["fold_order_variants"]) == 4
    assert len(payload["params"]["profiles"]) >= 2
    prow = payload["particles"][0]
    assert prow["particle_id"] == "left_spinor_electron_ideal"
    assert len(prow["profiles"]) >= 2
    for pr in prow["profiles"]:
        assert "control" in pr
        assert "energies" in pr
        assert len(pr["energies"]) == 3
        for er in pr["energies"]:
            assert er["energy_id"] in {"E1_center_kick", "E2_center_plus_shell1", "E3_center_plus_shell2"}
            assert "aggregates" in er
            assert "canonical_trace" in er


def test_write_artifacts(tmp_path: Path) -> None:
    payload = build_payload(
        MeasureParams(
            ticks=24,
            burn_in_ticks=8,
            measure_ticks=10,
            kick_ops=(1,),
            profiles=(
                ("test_1d_x11", 11, 1, 1),
                ("test_3d_x11_y3_z3", 11, 3, 3),
            ),
            particle_ids=("left_spinor_electron_ideal",),
            velocity_span_tol=0.25,
            delta_velocity_span_tol=0.25,
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
    assert "Operational Kinematics / Mass / Kinetic Suite (v1)" in md
