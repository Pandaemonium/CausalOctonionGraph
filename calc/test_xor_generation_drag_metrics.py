"""Tests for calc/xor_generation_drag_metrics.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from calc.xor_generation_drag_metrics import (
    run_generation_drag_case,
    run_generation_drag_suite,
    write_generation_drag_artifacts,
)


def test_run_generation_drag_case_has_required_fields() -> None:
    out = run_generation_drag_case(
        label="electron",
        motif_id="furey_electron_doubled",
        depth_horizon=6,
        initial_edge_distance=3,
        background_id="vacuum_doubled",
    )
    assert out["label"] == "electron"
    assert out["motif_id"] == "furey_electron_doubled"
    assert out["drag_score"] > 0
    assert len(out["depth_metrics"]) == 7
    for row in out["depth_metrics"]:
        assert set(row.keys()) == {"depth", "node_count", "S_t", "V_t", "M_t", "C_t", "A_t", "D_t"}
        assert int(row["node_count"]) > 0
        assert int(row["S_t"]) >= 0
        assert int(row["V_t"]) >= 0
        assert int(row["M_t"]) >= 0
        assert int(row["C_t"]) >= 0
        assert int(row["A_t"]) >= 0
        assert int(row["D_t"]) >= 0


def test_generation_drag_suite_is_deterministic() -> None:
    a = run_generation_drag_suite(
        mapping_path="calc/generation_drag_motif_mapping.json",
        depth_horizon=6,
        initial_edge_distance=3,
    )
    b = run_generation_drag_suite(
        mapping_path="calc/generation_drag_motif_mapping.json",
        depth_horizon=6,
        initial_edge_distance=3,
    )
    assert a["suite_replay_hash"] == b["suite_replay_hash"]


def test_baseline_mueff_is_one() -> None:
    ds = run_generation_drag_suite(
        mapping_path="calc/generation_drag_motif_mapping.json",
        depth_horizon=6,
        initial_edge_distance=3,
    )
    baseline = ds["baseline_label"]
    case = next(c for c in ds["cases"] if c["label"] == baseline)
    assert case["mu_eff"] == pytest.approx(1.0, abs=1e-12)


def test_invalid_baseline_label_rejected(tmp_path: Path) -> None:
    bad = {
        "schema_version": "generation_drag_motif_mapping_v1",
        "baseline_label": "missing",
        "motifs": [{"label": "electron", "motif_id": "furey_electron_doubled"}],
    }
    p = tmp_path / "bad_mapping.json"
    p.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ValueError, match="baseline_label"):
        run_generation_drag_suite(
            mapping_path=p,
            depth_horizon=4,
            initial_edge_distance=2,
        )


def test_write_generation_drag_artifacts(tmp_path: Path) -> None:
    ds = run_generation_drag_suite(
        mapping_path="calc/generation_drag_motif_mapping.json",
        depth_horizon=4,
        initial_edge_distance=2,
    )
    jp = tmp_path / "drag.json"
    cp = tmp_path / "drag.csv"
    write_generation_drag_artifacts(ds, json_paths=[jp], csv_paths=[cp])

    loaded = json.loads(jp.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "xor_generation_drag_metrics_v1"
    assert cp.exists()


def test_non_integer_initial_edge_distance_rejected() -> None:
    with pytest.raises(TypeError, match="initial_edge_distance must be an integer"):
        run_generation_drag_suite(
            mapping_path="calc/generation_drag_motif_mapping.json",
            depth_horizon=6,
            initial_edge_distance=2.5,  # type: ignore[arg-type]
        )
