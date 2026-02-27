"""
Tests for calc/xor_coupled_motif_cycles.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from calc.xor_coupled_motif_cycles import (
    build_coupled_cycle_dataset,
    detect_pair_cycle,
    stable_triad_set,
    write_coupled_cycle_artifacts,
)


def test_stable_triad_set_size():
    triads = stable_triad_set()
    assert len(triads) == 7


def test_detect_pair_cycle_finds_higher_period_example():
    # Known higher-period pair from deterministic coupled policy.
    sim = detect_pair_cycle((1, 2, 3), (2, 5, 7), max_steps=256)
    assert sim["cycle_found"] is True
    assert sim["period"] is not None
    assert sim["period"] > 4


def test_dataset_has_pairwise_entries_and_period_hist():
    data = build_coupled_cycle_dataset(max_steps=256)
    assert data["schema_version"] == "xor_coupled_motif_cycles_v1"
    assert data["pair_count"] == 21  # C(7,2)
    assert isinstance(data["period_histogram"], dict)
    assert len(data["pairs"]) == 21
    assert any((p["period"] is not None and p["period"] > 4) for p in data["pairs"])


def test_write_artifacts_json_and_csv(tmp_path: Path):
    data = build_coupled_cycle_dataset(max_steps=128)
    json_path = tmp_path / "coupled_cycles.json"
    csv_path = tmp_path / "coupled_cycles.csv"

    write_coupled_cycle_artifacts(
        data,
        json_paths=[json_path],
        csv_paths=[csv_path],
    )

    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "xor_coupled_motif_cycles_v1"

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 21
    assert "period_gt_4" in rows[0]
