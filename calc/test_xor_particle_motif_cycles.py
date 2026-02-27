"""
Tests for calc/xor_particle_motif_cycles.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from calc.xor_particle_motif_cycles import (
    build_particle_motif_cycle_dataset,
    write_particle_motif_cycle_artifacts,
)


def _motif_by_id(dataset: dict, motif_id: str) -> dict:
    for m in dataset["motifs"]:
        if m["motif_id"] == motif_id:
            return m
    raise KeyError(motif_id)


def test_dataset_contains_named_motifs_and_schema():
    dataset = build_particle_motif_cycle_dataset(max_steps=64)
    assert dataset["schema_version"] == "xor_particle_motif_cycles_v1"
    assert "generated_at_utc" in dataset

    motif_ids = {m["motif_id"] for m in dataset["motifs"]}
    assert "electron_line_l1" in motif_ids
    assert "proton_proto_t124" in motif_ids
    assert "fano_line_l1" in motif_ids


def test_electron_and_proton_proto_cycle_signatures():
    dataset = build_particle_motif_cycle_dataset(max_steps=64)
    electron = _motif_by_id(dataset, "electron_line_l1")
    proton = _motif_by_id(dataset, "proton_proto_t124")

    e_vac = electron["policies"]["vacuum_left_e7"]
    assert e_vac["cycle_found"] is True
    assert e_vac["period"] == 4

    e_internal = electron["policies"]["internal_oriented_alternating"]
    assert e_internal["support_closure_within_motif_plus_e0"] is True

    p_internal = proton["policies"]["internal_oriented_alternating"]
    assert p_internal["support_closure_within_motif_plus_e0"] is False

    # New update-rule variants are present and cycle-detectable.
    e_temporal_first = electron["policies"]["temporal_first_internal_alternating_left"]
    e_temporal_last = electron["policies"]["internal_alternating_then_temporal_left"]
    assert e_temporal_first["cycle_found"] is True
    assert e_temporal_last["cycle_found"] is True
    assert e_temporal_first["period"] is not None
    assert e_temporal_last["period"] is not None


def test_write_artifacts_json_and_csv(tmp_path: Path):
    dataset = build_particle_motif_cycle_dataset(max_steps=32)
    json_path = tmp_path / "motif_cycles.json"
    csv_path = tmp_path / "motif_cycles.csv"

    write_particle_motif_cycle_artifacts(
        dataset,
        json_paths=[json_path],
        csv_paths=[csv_path],
    )

    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "xor_particle_motif_cycles_v1"

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) > 0
    headers = set(rows[0].keys())
    assert "motif_id" in headers
    assert "policy_id" in headers
    assert "period" in headers
    assert "support_closure_within_motif_plus_e0" in headers
