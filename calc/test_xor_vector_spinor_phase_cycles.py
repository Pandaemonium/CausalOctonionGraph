"""
Tests for calc/xor_vector_spinor_phase_cycles.py
"""

from pathlib import Path
import csv
import json

from calc.xor_vector_spinor_phase_cycles import (
    build_vector_spinor_phase_cycle_dataset,
    run_cycle_trace,
    vector_motif_state,
    write_vector_spinor_phase_cycle_artifacts,
)


def test_vector_electron_favored_state_integer_count():
    s = vector_motif_state((1, 2, 3), coeff=1)
    # integer count on favored orientation channels
    assert s[1] == (1, 0)
    assert s[2] == (1, 0)
    assert s[3] == (1, 0)
    # no imaginary complex part for vector-count seed
    assert all(c[1] == 0 for c in s)


def test_repeated_xor_product_on_vector_electron_vacuum_pass_period4():
    s = vector_motif_state((1, 2, 3), coeff=1)
    left = run_cycle_trace(s, op_cycle=[7], hand="left", max_steps=16)
    right = run_cycle_trace(s, op_cycle=[7], hand="right", max_steps=16)
    assert left["cycle_found"] is True
    assert right["cycle_found"] is True
    assert left["period"] == 4
    assert right["period"] == 4


def test_same_basis_sequences_for_vector_and_spinor_electron_motifs():
    data = build_vector_spinor_phase_cycle_dataset(max_steps=32)
    seqs = data["operator_sequences"]
    assert set(seqs.keys()) == {"vacuum_pass_e7", "interaction_pass_123"}

    comp = data["electron_comparison"]
    labels = set(comp.keys())
    assert labels == {
        "vector_electron_favored",
        "left_spinor_electron_ideal",
        "right_spinor_electron_ideal",
    }

    for label in labels:
        for hand in ("left", "right"):
            for seq_id in seqs.keys():
                rec = comp[label]["traces"][hand][seq_id]
                assert "cycle_found" in rec
                assert "period" in rec
                assert rec["steps_recorded"] >= 1


def test_artifact_write_json_csv(tmp_path: Path):
    data = build_vector_spinor_phase_cycle_dataset(max_steps=24)
    json_path = tmp_path / "vector_spinor_cycles.json"
    csv_path = tmp_path / "vector_spinor_cycles.csv"
    write_vector_spinor_phase_cycle_artifacts(
        data,
        json_paths=[json_path],
        csv_paths=[csv_path],
    )

    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "xor_vector_spinor_phase_cycles_v1"

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) > 0
    assert {"label", "hand", "sequence_id", "period"}.issubset(rows[0].keys())

