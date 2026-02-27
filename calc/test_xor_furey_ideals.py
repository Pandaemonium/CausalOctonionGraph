"""
Tests for calc/xor_furey_ideals.py
"""

from pathlib import Path
import csv
import json

from calc.xor_furey_ideals import (
    build_furey_ideal_cycle_dataset,
    detect_period,
    e7_left,
    e7_right,
    furey_dual_electron_doubled,
    furey_electron_doubled,
    oct_mul_xor,
    state_basis,
    state_sparse,
    vacuum_conj_doubled,
    vacuum_doubled,
    witt_lower_doubled,
    witt_raise_doubled,
    write_furey_ideal_cycle_artifacts,
)


def _coeff(state, idx):
    return state[idx]


def test_stepwise_primal_chain_matches_lean_targets():
    # Step 1: alpha3Dag * omega
    step1 = oct_mul_xor(witt_raise_doubled(3), vacuum_doubled())
    assert _coeff(step1, 3) == (-2, 0)
    assert _coeff(step1, 4) == (0, 2)

    # Step 2: alpha2Dag * step1
    step2 = oct_mul_xor(witt_raise_doubled(2), step1)
    assert _coeff(step2, 1) == (4, 0)
    assert _coeff(step2, 6) == (0, -4)

    # Step 3: alpha1Dag * step2 = -8i*e0 - 8*e7
    step3 = oct_mul_xor(witt_raise_doubled(1), step2)
    assert _coeff(step3, 0) == (0, -8)
    assert _coeff(step3, 7) == (-8, 0)
    assert step3 == furey_electron_doubled()


def test_stepwise_dual_chain_matches_lean_targets():
    # Step 1: alpha3 * omega_dag
    step1 = oct_mul_xor(witt_lower_doubled(3), vacuum_conj_doubled())
    assert _coeff(step1, 3) == (2, 0)
    assert _coeff(step1, 4) == (0, 2)

    # Step 2: alpha2 * step1
    step2 = oct_mul_xor(witt_lower_doubled(2), step1)
    assert _coeff(step2, 1) == (4, 0)
    assert _coeff(step2, 6) == (0, 4)

    # Step 3: alpha1 * step2 = -8i*e0 + 8*e7
    step3 = oct_mul_xor(witt_lower_doubled(1), step2)
    assert _coeff(step3, 0) == (0, -8)
    assert _coeff(step3, 7) == (8, 0)
    assert step3 == furey_dual_electron_doubled()


def test_furey_states_have_period_four_under_e7_left_and_right():
    electron = furey_electron_doubled()
    dual = furey_dual_electron_doubled()

    assert detect_period(electron, e7_left, max_steps=32) == 4
    assert detect_period(electron, e7_right, max_steps=32) == 4
    assert detect_period(dual, e7_left, max_steps=32) == 4
    assert detect_period(dual, e7_right, max_steps=32) == 4


def test_dataset_contains_ideal_motifs_and_stability_flags():
    data = build_furey_ideal_cycle_dataset(max_steps=32)
    assert data["schema_version"] == "xor_furey_ideal_cycles_v1"
    assert data["motif_count"] == 16
    ids = {m["motif_id"] for m in data["motifs"]}
    assert "su_triple_electron" in ids
    assert "sd_triple_dual_electron" in ids
    assert all(m["stable_period4"] for m in data["motifs"])


def test_artifact_write_json_csv(tmp_path: Path):
    data = build_furey_ideal_cycle_dataset(max_steps=16)
    json_path = tmp_path / "furey_ideal_cycles.json"
    csv_path = tmp_path / "furey_ideal_cycles.csv"
    write_furey_ideal_cycle_artifacts(data, json_paths=[json_path], csv_paths=[csv_path])

    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "xor_furey_ideal_cycles_v1"

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 16


def test_state_sparse_json_shape():
    s = state_basis(0, (1, 0))
    out = state_sparse(s)
    assert out == {"e0": {"re": 1, "im": 0}}

