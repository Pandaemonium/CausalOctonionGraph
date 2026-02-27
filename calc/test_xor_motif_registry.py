"""
Tests for calc/xor_motif_registry.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from calc.xor_motif_registry import (
    build_xor_motif_registry_dataset,
    write_xor_motif_registry_artifacts,
)


def _by_id(data: dict, motif_id: str) -> dict:
    for m in data["motifs"]:
        if m["motif_id"] == motif_id:
            return m
    raise KeyError(motif_id)


def test_registry_schema_and_presence():
    data = build_xor_motif_registry_dataset()
    assert data["schema_version"] == "xor_motif_registry_v1"
    assert data["motif_count"] >= 27
    assert set(data["representation_counts"]).issuperset({"vector", "spinor"})

    ids = {m["motif_id"] for m in data["motifs"]}
    assert "vector_electron_favored" in ids
    assert "vector_proton_proto_t124" in ids
    assert "su_triple_electron" in ids
    assert "sd_triple_dual_electron" in ids
    assert "left_spinor_electron_ideal" in ids
    assert "right_spinor_electron_ideal" in ids
    assert "left_spinor_muon_motif" in ids
    assert "left_spinor_tau_motif" in ids


def test_registry_ids_unique_and_support_in_bounds():
    data = build_xor_motif_registry_dataset()
    ids = [m["motif_id"] for m in data["motifs"]]
    assert len(ids) == len(set(ids))

    for m in data["motifs"]:
        support = m["support"]
        assert isinstance(support, list)
        assert all(isinstance(x, int) for x in support)
        assert all(0 <= x <= 7 for x in support)


def test_electron_and_dual_electron_charge_signs():
    data = build_xor_motif_registry_dataset()
    su_e = _by_id(data, "su_triple_electron")
    sd_e = _by_id(data, "sd_triple_dual_electron")
    assert su_e["u1_charge_proxy"] < 0
    assert sd_e["u1_charge_proxy"] > 0


def test_named_vector_electron_support_and_cycle():
    data = build_xor_motif_registry_dataset()
    vec_e = _by_id(data, "vector_electron_favored")
    assert vec_e["representation"] == "vector"
    assert vec_e["support"] == [1, 2, 3]
    assert vec_e["period_left_e7"] == 4
    assert vec_e["period_right_e7"] == 4
    assert vec_e["stable_period4"] is True


def test_named_spinor_muon_tau_support_and_cycle():
    data = build_xor_motif_registry_dataset()
    mu = _by_id(data, "left_spinor_muon_motif")
    tau = _by_id(data, "left_spinor_tau_motif")

    assert mu["representation"] == "spinor"
    assert tau["representation"] == "spinor"
    assert mu["support"] == [3, 4]
    assert tau["support"] == [1, 6]
    assert mu["period_left_e7"] == 4 and mu["period_right_e7"] == 4
    assert tau["period_left_e7"] == 4 and tau["period_right_e7"] == 4


def test_write_registry_artifacts(tmp_path: Path):
    data = build_xor_motif_registry_dataset()
    json_path = tmp_path / "xor_motif_registry.json"
    csv_path = tmp_path / "xor_motif_registry.csv"
    write_xor_motif_registry_artifacts(
        data,
        json_paths=[json_path],
        csv_paths=[csv_path],
    )

    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "xor_motif_registry_v1"

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == data["motif_count"]
    assert "motif_id" in rows[0]
    assert "representation" in rows[0]
    assert "support" in rows[0]
