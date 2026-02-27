"""
Tests for calc/xor_ensemble_runner.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from calc.xor_ensemble_runner import (
    run_ensemble_from_yaml,
    run_ensemble_specs,
    write_xor_ensemble_artifacts,
)
from calc.xor_scenario_loader import load_scenario_specs


def _write_two_specs(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "scenarios:",
                "  - scenario_id: a",
                "    title: opposite pair",
                "    steps: 3",
                "    nodes:",
                "      - node_id: 0",
                "        motif_id: left_spinor_electron_ideal",
                "      - node_id: 1",
                "        motif_id: right_spinor_electron_ideal",
                "    edges:",
                "      - src_node_id: 0",
                "        dst_node_id: 1",
                "        op_idx: 7",
                "        hand: left",
                "      - src_node_id: 1",
                "        dst_node_id: 0",
                "        op_idx: 7",
                "        hand: left",
                "  - scenario_id: b",
                "    title: single",
                "    steps: 2",
                "    nodes:",
                "      - node_id: 0",
                "        motif_id: vector_electron_favored",
                "    edges: []",
            ]
        ),
        encoding="utf-8",
    )


def test_run_ensemble_specs(tmp_path: Path):
    p = tmp_path / "specs.yml"
    _write_two_specs(p)
    specs = load_scenario_specs(p)
    data = run_ensemble_specs(specs)
    assert data["schema_version"] == "xor_ensemble_runner_v1"
    assert data["run_count"] == 2
    assert len(data["runs"]) == 2
    assert "aggregate_observables" in data
    assert len(data["csv_rows"]) == 2


def test_run_ensemble_from_yaml(tmp_path: Path):
    p = tmp_path / "specs.yml"
    _write_two_specs(p)
    data = run_ensemble_from_yaml(p)
    assert data["run_count"] == 2
    ids = {r["scenario_id"] for r in data["runs"]}
    assert ids == {"a", "b"}


def test_write_artifacts(tmp_path: Path):
    p = tmp_path / "specs.yml"
    _write_two_specs(p)
    data = run_ensemble_from_yaml(p)
    json_path = tmp_path / "ensemble.json"
    csv_path = tmp_path / "ensemble.csv"
    write_xor_ensemble_artifacts(data, json_paths=[json_path], csv_paths=[csv_path])

    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "xor_ensemble_runner_v1"

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    assert "scenario_id" in rows[0]

