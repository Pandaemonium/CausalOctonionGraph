"""
Tests for calc/xor_basis_conformance.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from calc.conftest import FANO_SIGN, FANO_THIRD
from calc.xor_basis_conformance import (
    build_xor_basis_conformance_dataset,
    write_xor_basis_conformance_artifacts,
)


def test_basis_conformance_summary_is_fully_true():
    data = build_xor_basis_conformance_dataset()
    summary = data["summary"]
    assert data["schema_version"] == "xor_basis_conformance_v1"
    assert summary["basis_row_count"] == 64
    assert summary["expected_match_count"] == 64
    assert summary["xor_channel_checked_count"] == 42
    assert summary["xor_channel_match_count"] == 42
    assert summary["handed_alignment_match_count"] == 64
    assert summary["anti_comm_checked_count"] == 42
    assert summary["anti_comm_match_count"] == 42
    assert summary["all_expected_match"] is True
    assert summary["all_xor_channel_match"] is True
    assert summary["all_handed_alignment_match"] is True
    assert summary["all_anti_comm_match"] is True


def test_basis_hash_shape_and_basis_row_integrity():
    data = build_xor_basis_conformance_dataset()
    h = data["table_sha256"]
    assert isinstance(h, str)
    assert len(h) == 64
    assert all(ch in "0123456789abcdef" for ch in h)

    rows = data["basis_rows"]
    assert len(rows) == 64
    keys = {
        "i",
        "j",
        "out_idx",
        "sign",
        "expected_out_idx",
        "expected_sign",
        "matches_expected",
        "handed_alignment_match",
    }
    assert keys.issubset(rows[0].keys())


def test_matches_reference_fano_products():
    rows = build_xor_basis_conformance_dataset()["basis_rows"]
    for i in range(8):
        for j in range(8):
            row = rows[i * 8 + j]
            if i == 0:
                assert row["out_idx"] == j
                assert row["sign"] == 1
            elif j == 0:
                assert row["out_idx"] == i
                assert row["sign"] == 1
            elif i == j:
                assert row["out_idx"] == 0
                assert row["sign"] == -1
            else:
                fi, fj = i - 1, j - 1
                assert row["out_idx"] == FANO_THIRD[(fi, fj)] + 1
                assert row["sign"] == FANO_SIGN[(fi, fj)]


def test_write_artifacts_json_csv(tmp_path: Path):
    data = build_xor_basis_conformance_dataset()
    json_path = tmp_path / "xor_basis_conformance.json"
    csv_path = tmp_path / "xor_basis_conformance.csv"
    write_xor_basis_conformance_artifacts(
        data,
        json_paths=[json_path],
        csv_paths=[csv_path],
    )

    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "xor_basis_conformance_v1"

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 64
    assert "i" in rows[0]
    assert "j" in rows[0]
    assert "out_idx" in rows[0]
    assert "sign" in rows[0]
