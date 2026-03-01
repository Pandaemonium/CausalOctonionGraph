from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_operational_kinematics_targeted_lock_v1 import (
    OUT_JSON,
    OUT_MD,
    TargetedLockParams,
    build_payload,
    write_artifacts,
)


def test_payload_deterministic_small() -> None:
    params = TargetedLockParams(
        ticks=72,
        burn_in_ticks=20,
        measure_ticks=30,
        min_burn_ticks_for_stabilization=12,
        stabilization_window=8,
        stabilization_confirm_windows=2,
        period_min=2,
        period_max=10,
        cycle_error_tol=0.05,
        min_stable_cycles=1,
        fallback_targets=(("left_spinor_muon_motif", "E2_center_plus_shell1"),),
    )
    a = build_payload(params)
    b = build_payload(params)
    assert a["replay_hash"] == b["replay_hash"]
    assert a["checks"] == b["checks"]


def test_schema_and_target_fields() -> None:
    payload = build_payload(
        TargetedLockParams(
            ticks=72,
            burn_in_ticks=20,
            measure_ticks=30,
            min_burn_ticks_for_stabilization=12,
            stabilization_window=8,
            stabilization_confirm_windows=2,
            period_min=2,
            period_max=10,
            cycle_error_tol=0.05,
            min_stable_cycles=1,
            fallback_targets=(("left_spinor_muon_motif", "E2_center_plus_shell1"),),
        )
    )
    assert payload["schema_version"] == "operational_kinematics_targeted_lock_v1"
    assert payload["checks"]["target_count"] >= 1
    assert len(payload["targets"]) >= 1
    for row in payload["targets"]:
        assert "particle_id" in row
        assert "energy_id" in row
        assert "run_count" in row
        assert "runs" in row
        assert row["run_count"] == len(row["runs"])


def test_write_artifacts(tmp_path: Path) -> None:
    payload = build_payload(
        TargetedLockParams(
            ticks=72,
            burn_in_ticks=20,
            measure_ticks=30,
            min_burn_ticks_for_stabilization=12,
            stabilization_window=8,
            stabilization_confirm_windows=2,
            period_min=2,
            period_max=10,
            cycle_error_tol=0.05,
            min_stable_cycles=1,
            fallback_targets=(("left_spinor_muon_motif", "E2_center_plus_shell1"),),
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
    assert "Operational Kinematics Targeted Lock Campaign (v1)" in md
