"""
Tests for calc/xor_perturbation_attractor_matrix.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from calc.xor_perturbation_attractor_matrix import (
    apply_basis_hit,
    build_xor_perturbation_attractor_dataset,
    canonical_cycle_key,
    detect_cycle,
    write_xor_perturbation_attractor_artifacts,
)
from calc.xor_vector_spinor_phase_cycles import vector_motif_state


def test_apply_basis_hit_changes_state_deterministically():
    s = vector_motif_state((1, 2, 3), coeff=1)
    l = apply_basis_hit(s, 7, "left")
    r = apply_basis_hit(s, 7, "right")
    assert l != s
    assert r != s
    assert l != r


def test_cycle_detection_under_vacuum_policy():
    s = vector_motif_state((1, 2, 3), coeff=1)
    cyc = detect_cycle(s, lambda x: apply_basis_hit(x, 7, "left"), max_steps=32)
    assert cyc["cycle_found"] is True
    assert cyc["period"] == 4
    key = canonical_cycle_key(cyc["cycle_states"])
    assert isinstance(key, str)
    assert len(key) == 64


def test_dataset_shape_and_counts():
    data = build_xor_perturbation_attractor_dataset(max_steps=64)
    assert data["schema_version"] == "xor_perturbation_attractor_matrix_v1"
    assert data["baseline"]["seed_count"] == 27
    assert data["summary"]["transition_count"] == 27 * 14
    assert len(data["transitions"]) == 27 * 14
    assert len(data["retention"]) == 27
    assert len(data["csv_rows"]) == 27 * 14


def test_known_attractor_coverage_present():
    data = build_xor_perturbation_attractor_dataset(max_steps=64)
    known_hits = data["summary"]["known_attractor_hits"]
    assert known_hits > 0
    assert data["baseline"]["known_attractor_count"] > 0


def test_write_artifacts_json_csv(tmp_path: Path):
    data = build_xor_perturbation_attractor_dataset(max_steps=64)
    json_path = tmp_path / "xor_perturbation_attractor_matrix.json"
    csv_path = tmp_path / "xor_perturbation_attractor_matrix.csv"
    write_xor_perturbation_attractor_artifacts(
        data,
        json_paths=[json_path],
        csv_paths=[csv_path],
    )

    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "xor_perturbation_attractor_matrix_v1"

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == len(data["csv_rows"])
    assert "source_motif_id" in rows[0]
    assert "attractor_rep_id" in rows[0]

