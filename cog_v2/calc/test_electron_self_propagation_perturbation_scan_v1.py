from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_electron_self_propagation_perturbation_scan_v1 import (
    OUT_JSON,
    OUT_MD,
    ScanParams,
    build_payload,
    write_artifacts,
)


def test_payload_deterministic_small() -> None:
    params = ScanParams(
        ticks=10,
        size_xyz=9,
        warmup_ticks=2,
        directionality_threshold=0.5,
        net_displacement_threshold=0.5,
        min_speed_threshold=0.02,
    )
    a = build_payload(params)
    b = build_payload(params)
    assert a["replay_hash"] == b["replay_hash"]
    assert a["ranked_case_ids"] == b["ranked_case_ids"]


def test_schema_and_control_presence() -> None:
    payload = build_payload(
        ScanParams(
            ticks=10,
            size_xyz=9,
            warmup_ticks=2,
            directionality_threshold=0.5,
            net_displacement_threshold=0.5,
            min_speed_threshold=0.02,
        )
    )
    assert payload["schema_version"] == "electron_self_propagation_perturbation_scan_v1"
    assert payload["checks"]["has_control_case"] is True
    assert payload["checks"]["rows_match_ticks_all_cases"] is True
    assert "control_none" in payload["ranked_case_ids"]
    cases = {r["case_id"]: r for r in payload["cases"]}
    assert cases["control_none"]["summary"]["rows_recorded"] == payload["params"]["ticks"]


def test_write_artifacts(tmp_path: Path) -> None:
    payload = build_payload(
        ScanParams(
            ticks=8,
            size_xyz=7,
            warmup_ticks=1,
            directionality_threshold=0.5,
            net_displacement_threshold=0.5,
            min_speed_threshold=0.02,
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
    assert "Electron Self-Propagation Perturbation Scan (v1)" in md

