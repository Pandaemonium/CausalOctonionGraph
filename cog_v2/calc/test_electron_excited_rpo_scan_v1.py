from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_electron_excited_rpo_scan_v1 import (
    OUT_JSON,
    OUT_MD,
    RPOParams,
    build_payload,
    write_artifacts,
)


def test_payload_deterministic_small() -> None:
    params = RPOParams(
        ticks=24,
        size_xyz=7,
        burn_in_ticks=6,
        min_period=2,
        max_period=10,
        kick_ops=(1, 7),
        max_shift_x=2,
    )
    a = build_payload(params)
    b = build_payload(params)
    assert a["replay_hash"] == b["replay_hash"]
    assert a["robust_rpo_case_ids"] == b["robust_rpo_case_ids"]


def test_schema_and_case_shapes() -> None:
    payload = build_payload(
        RPOParams(
            ticks=20,
            size_xyz=7,
            burn_in_ticks=5,
            min_period=2,
            max_period=8,
            kick_ops=(1, 7),
            max_shift_x=2,
        )
    )
    assert payload["schema_version"] == "electron_excited_rpo_scan_v1"
    assert payload["checks"]["rpo_requires_order_robustness_gate"] is True
    assert len(payload["cases"]) == 1 + 3 * len(payload["params"]["kick_ops"])
    for c in payload["cases"]:
        assert "summary" in c
        assert "variant_results" in c
        assert c["summary"]["variant_count"] == len(payload["fold_order_variants"])
    assert "kick_cases" in payload
    assert len(payload["kick_cases"]) == len(payload["cases"])


def test_write_artifacts(tmp_path: Path) -> None:
    payload = build_payload(
        RPOParams(
            ticks=16,
            size_xyz=7,
            burn_in_ticks=4,
            min_period=2,
            max_period=6,
            kick_ops=(1,),
            max_shift_x=2,
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
    assert "Electron Excited RPO Scan (v1)" in md
