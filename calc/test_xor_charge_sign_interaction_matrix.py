"""
Tests for calc/xor_charge_sign_interaction_matrix.py

These tests are intended to be both:
1) correctness checks, and
2) implementation clues for XCALC-101 extensions.
"""

from pathlib import Path
import csv
import json

from calc.xor_charge_sign_interaction_matrix import (
    benchmark_states_xor,
    build_charge_sign_matrix_xor,
    interaction_kind_xor,
    opposite_u1_charge_sign_xor,
    same_u1_charge_sign_xor,
    summarize_xor,
    two_node_round_xor,
    write_xor_charge_sign_artifacts,
)


def test_benchmark_state_labels_present():
    states = benchmark_states_xor()
    assert set(states.keys()) == {
        "vector_electron_favored",
        "left_spinor_electron_ideal",
        "right_spinor_electron_ideal",
        "vacuum_doubled",
    }


def test_sign_predicates_on_spinor_electron_pair():
    s = benchmark_states_xor()
    assert same_u1_charge_sign_xor(s["left_spinor_electron_ideal"], s["left_spinor_electron_ideal"]) is True
    assert opposite_u1_charge_sign_xor(s["left_spinor_electron_ideal"], s["right_spinor_electron_ideal"]) is True


def test_interaction_kind_expected_baselines():
    s = benchmark_states_xor()
    assert interaction_kind_xor(s["left_spinor_electron_ideal"], s["left_spinor_electron_ideal"]) == "repulsive"
    assert interaction_kind_xor(s["left_spinor_electron_ideal"], s["right_spinor_electron_ideal"]) == "attractive"
    assert interaction_kind_xor(s["left_spinor_electron_ideal"], s["vacuum_doubled"]) == "neutral"


def test_matrix_contains_core_entries():
    matrix = build_charge_sign_matrix_xor()
    assert matrix["left_spinor_electron_ideal"]["left_spinor_electron_ideal"] == "repulsive"
    assert matrix["left_spinor_electron_ideal"]["right_spinor_electron_ideal"] == "attractive"
    assert matrix["left_spinor_electron_ideal"]["vacuum_doubled"] == "neutral"


def test_two_node_round_deterministic():
    s = benchmark_states_xor()
    a1, b1 = two_node_round_xor(s["left_spinor_electron_ideal"], s["right_spinor_electron_ideal"])
    a2, b2 = two_node_round_xor(s["left_spinor_electron_ideal"], s["right_spinor_electron_ideal"])
    assert a1 == a2
    assert b1 == b2


def test_artifact_write_json_csv(tmp_path: Path):
    summary = summarize_xor()
    json_path = tmp_path / "xor_charge_sign_interaction_matrix.json"
    csv_path = tmp_path / "xor_charge_sign_interaction_matrix.csv"
    write_xor_charge_sign_artifacts(summary, json_paths=[json_path], csv_paths=[csv_path])

    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "xor_charge_sign_interaction_matrix_v1"
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) >= 1
    assert {"row_label", "col_label", "kind", "row_charge", "col_charge"}.issubset(rows[0].keys())

