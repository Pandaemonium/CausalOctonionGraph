from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_particle_excited_propagation_cycle_library_v1 import (
    OUT_JSON,
    OUT_MD,
    LibraryParams,
    build_payload,
    write_artifacts,
)


def test_payload_deterministic_small() -> None:
    params = LibraryParams(
        ticks=24,
        size_xyz=7,
        burn_in_ticks=6,
        min_period=2,
        max_period=10,
        max_shift_x=2,
        kick_ops=(1, 2, 7),
        particle_ids=("left_spinor_electron_ideal", "left_spinor_muon_motif"),
    )
    a = build_payload(params)
    b = build_payload(params)
    assert a["replay_hash"] == b["replay_hash"]
    assert a["checks"] == b["checks"]


def test_schema_and_case_shapes() -> None:
    payload = build_payload(
        LibraryParams(
            ticks=20,
            size_xyz=7,
            burn_in_ticks=5,
            min_period=2,
            max_period=8,
            max_shift_x=2,
            kick_ops=(1, 2),
            particle_ids=("left_spinor_electron_ideal", "vector_proton_proto_t124"),
        )
    )
    assert payload["schema_version"] == "particle_excited_propagation_cycle_library_v1"
    assert payload["checks"]["particle_count_processed"] == 2
    assert len(payload["particles"]) == 2
    for prow in payload["particles"]:
        assert "particle_id" in prow
        assert "selected_case_count" in prow
        assert "selected_cases" in prow
        assert isinstance(prow["selected_cases"], list)
        for case in prow["selected_cases"]:
            assert case["period_N"] >= payload["params"]["min_period"]
            assert case["period_N"] <= payload["params"]["max_period"]
            assert case["closure_witness"]["closure_check_passed"] is True
            assert len(case["cycle_rows_post_transient"]) == case["period_N"]
            assert case["energy_id"] in {"E1_center_kick", "E2_center_plus_shell1", "E3_center_plus_shell2"}


def test_write_artifacts(tmp_path: Path) -> None:
    payload = build_payload(
        LibraryParams(
            ticks=16,
            size_xyz=7,
            burn_in_ticks=4,
            min_period=2,
            max_period=6,
            max_shift_x=2,
            kick_ops=(1,),
            particle_ids=("left_spinor_electron_ideal",),
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
    assert "Particle Excited Propagation Cycle Library (v1)" in md
