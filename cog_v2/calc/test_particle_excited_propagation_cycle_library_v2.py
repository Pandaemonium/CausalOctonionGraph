from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_particle_excited_propagation_cycle_library_v2 import (
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
        burn_in_ticks=0,
        min_period=2,
        max_period=10,
        max_shift_x=2,
        kick_ops=(1, 2, 3, 4),
        particle_ids=("left_spinor_muon_motif", "left_spinor_tau_motif"),
    )
    a = build_payload(params)
    b = build_payload(params)
    assert a["replay_hash"] == b["replay_hash"]
    assert a["checks"] == b["checks"]


def test_schema_and_nontriviality_gates() -> None:
    payload = build_payload(
        LibraryParams(
            ticks=24,
            size_xyz=7,
            burn_in_ticks=0,
            min_period=2,
            max_period=10,
            max_shift_x=2,
            kick_ops=(1, 2, 3, 4, 5, 6, 7),
            particle_ids=("left_spinor_muon_motif",),
        )
    )
    assert payload["schema_version"] == "particle_excited_propagation_cycle_library_v2"
    assert payload["checks"]["particle_count_processed"] == 1
    prow = payload["particles"][0]
    assert "has_two_cases" in prow
    for case in prow["selected_cases"]:
        cm = case["cycle_metrics"]
        assert cm["min_nonzero_coeff_count"] >= 1
        assert cm["min_nonvac_nonzero_coeff_count"] >= 1
        assert cm["temporal_hamming_vs_step0"] >= 1
        assert case["closure_witness"]["closure_shift_multiplicity"] == 1


def test_write_artifacts(tmp_path: Path) -> None:
    payload = build_payload(
        LibraryParams(
            ticks=20,
            size_xyz=7,
            burn_in_ticks=0,
            min_period=2,
            max_period=8,
            max_shift_x=2,
            kick_ops=(1, 2, 3, 4),
            particle_ids=("left_spinor_muon_motif",),
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
    assert "Particle Excited Propagation Cycle Library (v2)" in md
