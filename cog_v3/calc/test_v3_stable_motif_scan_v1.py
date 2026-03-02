from __future__ import annotations

import json
from pathlib import Path

from cog_v3.calc.build_v3_stable_motif_scan_v1 import (
    OUT_JSON,
    OUT_MD,
    ScanParams,
    build_payload,
    write_artifacts,
)
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


def test_payload_deterministic_small() -> None:
    params = ScanParams(
        ticks=32,
        size_x=17,
        size_y=7,
        size_z=7,
        stencil_id="axial6",
        warmup_ticks=8,
        min_period=2,
        max_period=8,
        max_shift_x=3,
        repeat_checks=2,
        min_support_cells=4,
        min_support_match_ratio=0.8,
        min_global_match_ratio=0.6,
        max_trials=3,
        thin_output_step=2,
    )
    a = build_payload(params)
    b = build_payload(params)
    assert a["replay_hash"] == b["replay_hash"]


def test_schema_and_contract() -> None:
    payload = build_payload(
        ScanParams(
            ticks=28,
            size_x=15,
            size_y=7,
            size_z=7,
            stencil_id="axial6",
            warmup_ticks=8,
            min_period=2,
            max_period=8,
            max_shift_x=2,
            repeat_checks=2,
            min_support_cells=4,
            min_support_match_ratio=0.8,
            min_global_match_ratio=0.6,
            max_trials=2,
            thin_output_step=4,
        )
    )
    assert payload["schema_version"] == "v3_stable_motif_scan_v1"
    assert payload["kernel_profile"] == k.KERNEL_PROFILE
    assert payload["convention_id"] == k.CONVENTION_ID
    assert payload["params"]["boundary_mode"] == "fixed_vacuum"
    assert payload["checks"]["trial_count"] == len(payload["trials"])
    assert "any_stationary_candidate" in payload["checks"]
    assert "any_propagating_candidate" in payload["checks"]


def test_write_artifacts(tmp_path: Path) -> None:
    payload = build_payload(
        ScanParams(
            ticks=24,
            size_x=13,
            size_y=7,
            size_z=7,
            stencil_id="axial6",
            warmup_ticks=6,
            min_period=2,
            max_period=6,
            max_shift_x=2,
            repeat_checks=2,
            min_support_cells=3,
            min_support_match_ratio=0.75,
            min_global_match_ratio=0.5,
            max_trials=2,
            thin_output_step=3,
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
    assert "COG v3 Stable Motif Scan (v1)" in md
