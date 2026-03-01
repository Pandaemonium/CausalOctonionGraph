from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_operational_mass_targeted_lock_v1 import (
    OUT_JSON,
    OUT_MD,
    MassTargetedLockParams,
    build_payload,
    write_artifacts,
)


def test_payload_deterministic_small() -> None:
    params = MassTargetedLockParams(
        ticks=80,
        burn_in_ticks=18,
        measure_ticks=36,
        impulse_window_start=4,
        impulse_window_len=12,
        delta_v_eps=1e-6,
        fold_mass_span_tol=1.0,
        profile_mass_gap_tol=1.0,
        fallback_targets=(("left_spinor_muon_motif", "E2_center_plus_shell1"),),
    )
    a = build_payload(params)
    b = build_payload(params)
    assert a["replay_hash"] == b["replay_hash"]
    assert a["checks"] == b["checks"]


def test_schema_and_target_fields() -> None:
    payload = build_payload(
        MassTargetedLockParams(
            ticks=80,
            burn_in_ticks=18,
            measure_ticks=36,
            impulse_window_start=4,
            impulse_window_len=12,
            delta_v_eps=1e-6,
            fold_mass_span_tol=1.0,
            profile_mass_gap_tol=1.0,
            fallback_targets=(("left_spinor_muon_motif", "E2_center_plus_shell1"),),
        )
    )
    assert payload["schema_version"] == "operational_mass_targeted_lock_v1"
    assert payload["checks"]["target_count"] >= 1
    for row in payload["targets"]:
        assert "particle_id" in row
        assert "energy_id" in row
        assert "run_count" in row
        assert row["run_count"] == len(row["runs"])
        for rr in row["runs"]:
            assert rr["window_len"] >= 0


def test_write_artifacts(tmp_path: Path) -> None:
    payload = build_payload(
        MassTargetedLockParams(
            ticks=80,
            burn_in_ticks=18,
            measure_ticks=36,
            impulse_window_start=4,
            impulse_window_len=12,
            delta_v_eps=1e-6,
            fold_mass_span_tol=1.0,
            profile_mass_gap_tol=1.0,
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
    assert "Operational Mass Targeted Lock Campaign (v1)" in md
