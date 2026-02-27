"""
Tests for calc/xor_hydrogen_binding_scan.py

Guided scaffold tests:
1) lock baseline structural expectations,
2) enforce deterministic artifact shape,
3) provide safe extension points for XCALC-103.
"""

from pathlib import Path
import csv
import json

from calc.xor_hydrogen_binding_scan import (
    build_hydrogen_coupled_summary,
    build_hydrogen_scan_dataset,
    build_hydrogen_structural_summary,
    build_hydrogen_xor_cycle_summary,
    write_hydrogen_scan_artifacts,
)


def test_structural_summary_baseline():
    s = build_hydrogen_structural_summary()
    assert s["electron_motif"] == [1, 2, 3]
    assert s["proton_proto_motif"] == [1, 2, 4]
    assert s["shared_pair"] == [1, 2]
    assert set(s["line_through_shared_pair"]) == {1, 2, 3}
    assert s["binding_proxy"]["numerator"] > 0
    assert s["binding_proxy"]["denominator"] > 0


def test_dynamic_summary_has_both_motifs_hands_sequences():
    d = build_hydrogen_xor_cycle_summary(max_steps=32)
    assert set(d.keys()) == {"electron_favored_vector", "proton_proto_vector"}
    for motif in d.values():
        assert set(motif.keys()) == {"left", "right"}
        for hand in ("left", "right"):
            assert set(motif[hand].keys()) == {"vacuum_pass_e7", "interaction_pass_123"}
            for seq in motif[hand].values():
                assert "cycle_found" in seq
                assert "period" in seq
                assert seq["steps_recorded"] >= 1


def test_coupled_summary_deterministic():
    c1 = build_hydrogen_coupled_summary(max_steps=96)
    c2 = build_hydrogen_coupled_summary(max_steps=96)
    assert c1 == c2


def test_dataset_schema_and_sections():
    ds = build_hydrogen_scan_dataset(max_steps=24)
    assert ds["schema_version"] == "xor_hydrogen_binding_scan_v1"
    assert "structural" in ds
    assert "dynamic" in ds
    assert "coupled" in ds
    assert len(ds["csv_rows"]) >= 1


def test_artifact_write_json_csv(tmp_path: Path):
    ds = build_hydrogen_scan_dataset(max_steps=16)
    json_path = tmp_path / "xor_hydrogen_binding_scan.json"
    csv_path = tmp_path / "xor_hydrogen_binding_scan.csv"
    write_hydrogen_scan_artifacts(ds, json_paths=[json_path], csv_paths=[csv_path])

    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "xor_hydrogen_binding_scan_v1"

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) >= 1
    assert {"section", "label", "hand", "sequence_id", "period"}.issubset(rows[0].keys())

