"""Tests for calc/xor_e7_muon_ablation_scan.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from calc.xor_e7_muon_ablation_scan import (
    run_e7_muon_ablation_suite,
    write_e7_muon_ablation_artifacts,
)


def test_suite_schema_and_baseline_present() -> None:
    ds = run_e7_muon_ablation_suite(conditions_path="calc/e7_muon_ablation_conditions.json")
    assert ds["schema_version"] == "xor_e7_muon_ablation_scan_v1"
    assert ds["baseline_case_id"] == "electron_electron"
    case_ids = {c["case_id"] for c in ds["cases"]}
    assert ds["baseline_case_id"] in case_ids


def test_suite_is_deterministic() -> None:
    a = run_e7_muon_ablation_suite(conditions_path="calc/e7_muon_ablation_conditions.json")
    b = run_e7_muon_ablation_suite(conditions_path="calc/e7_muon_ablation_conditions.json")
    assert a["suite_replay_hash"] == b["suite_replay_hash"]


def test_baseline_projected_ablation_is_zero() -> None:
    ds = run_e7_muon_ablation_suite(conditions_path="calc/e7_muon_ablation_conditions.json")
    base_id = ds["baseline_case_id"]
    base_case = next(c for c in ds["cases"] if c["case_id"] == base_id)
    vals = [int(r["projected_ablation_vs_baseline"]) for r in base_case["projected_e7_ablation"]]
    assert all(v == 0 for v in vals)
    assert int(base_case["summary"]["cumulative_projected_ablation_vs_baseline"]) == 0


def test_invalid_baseline_rejected(tmp_path: Path) -> None:
    bad = {
        "schema_version": "e7_muon_ablation_conditions_v1",
        "baseline_case_id": "missing",
        "depth_horizon": 4,
        "initial_edge_distance": 2,
        "background_id": "vacuum_doubled",
        "cases": [
            {
                "case_id": "electron_electron",
                "left_motif_id": "furey_electron_doubled",
                "right_motif_id": "furey_electron_doubled",
            }
        ],
    }
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ValueError, match="baseline_case_id"):
        run_e7_muon_ablation_suite(conditions_path=p)


def test_non_integer_initial_edge_distance_rejected(tmp_path: Path) -> None:
    bad = {
        "schema_version": "e7_muon_ablation_conditions_v1",
        "baseline_case_id": "electron_electron",
        "depth_horizon": 4,
        "initial_edge_distance": 2.5,
        "background_id": "vacuum_doubled",
        "cases": [
            {
                "case_id": "electron_electron",
                "left_motif_id": "furey_electron_doubled",
                "right_motif_id": "furey_electron_doubled",
            }
        ],
    }
    p = tmp_path / "bad_nonint.json"
    p.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(TypeError, match="initial_edge_distance must be an integer"):
        run_e7_muon_ablation_suite(conditions_path=p)


def test_write_artifacts(tmp_path: Path) -> None:
    ds = run_e7_muon_ablation_suite(conditions_path="calc/e7_muon_ablation_conditions.json")
    jp = tmp_path / "e7.json"
    cp = tmp_path / "e7.csv"
    write_e7_muon_ablation_artifacts(ds, json_paths=[jp], csv_paths=[cp])

    loaded = json.loads(jp.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "xor_e7_muon_ablation_scan_v1"
    assert cp.exists()
