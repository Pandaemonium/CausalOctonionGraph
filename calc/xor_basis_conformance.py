"""
calc/xor_basis_conformance.py

Exhaustive conformance audit for XOR octonion basis multiplication.

Goals:
1) Verify all 64 basis products e_i * e_j against canonical Fano sign/third tables.
2) Verify XOR index-channel law on the distinct-imaginary domain.
3) Verify handed-operator alignment and anti-commutation invariants.
4) Emit deterministic JSON/CSV artifacts with a stable table hash.
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from calc.conftest import FANO_SIGN, FANO_THIRD
from calc.xor_octonion_gate import Handedness, apply_handed_operator, mul_basis_fast


def expected_basis_product(i: int, j: int) -> tuple[int, int, str]:
    """
    Canonical expected product for e_i * e_j in basis index form (0..7).
    Returns (out_idx, sign, rule_tag).
    """
    if i == 0:
        return j, 1, "left_identity"
    if j == 0:
        return i, 1, "right_identity"
    if i == j:
        return 0, -1, "imag_square"

    fi, fj = i - 1, j - 1
    return int(FANO_THIRD[(fi, fj)] + 1), int(FANO_SIGN[(fi, fj)]), "distinct_imag"


def _hash_rows(rows: list[dict[str, Any]]) -> str:
    """
    Stable hash over canonical product table rows.
    """
    payload = "\n".join(
        f"{row['i']},{row['j']},{row['out_idx']},{row['sign']}"
        for row in rows
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_xor_basis_conformance_dataset() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    anti_rows: list[dict[str, Any]] = []

    xor_checked = 0
    xor_matched = 0
    expected_matched = 0
    handed_alignment_matched = 0
    anti_checked = 0
    anti_matched = 0

    for i in range(8):
        for j in range(8):
            core = mul_basis_fast(i, j)
            expected_out, expected_sign, rule = expected_basis_product(i, j)

            row: dict[str, Any] = {
                "i": i,
                "j": j,
                "out_idx": core.out_idx,
                "sign": core.sign,
                "expected_out_idx": expected_out,
                "expected_sign": expected_sign,
                "rule": rule,
            }

            row["matches_expected"] = (
                core.out_idx == expected_out and core.sign == expected_sign
            )
            if row["matches_expected"]:
                expected_matched += 1

            if 1 <= i <= 7 and 1 <= j <= 7 and i != j:
                xor_checked += 1
                xor_idx = i ^ j
                xor_match = core.out_idx == xor_idx
                row["xor_idx"] = xor_idx
                row["xor_channel_match"] = xor_match
                if xor_match:
                    xor_matched += 1
            else:
                row["xor_idx"] = None
                row["xor_channel_match"] = None

            # Handed semantics check:
            # LEFT with (state=j, op=i) computes e_i * e_j,
            # RIGHT with (state=i, op=j) computes e_i * e_j.
            left_view = apply_handed_operator(j, i, Handedness.LEFT)
            right_view = apply_handed_operator(i, j, Handedness.RIGHT)
            handed_ok = left_view == core and right_view == core
            row["handed_alignment_match"] = handed_ok
            if handed_ok:
                handed_alignment_matched += 1

            rows.append(row)

    # Distinct-imag anti-commutation audit:
    # e_i * e_j and e_j * e_i must have same out index and opposite sign.
    for i in range(1, 8):
        for j in range(1, 8):
            if i == j:
                continue
            anti_checked += 1
            a = mul_basis_fast(i, j)
            b = mul_basis_fast(j, i)
            ok = a.out_idx == b.out_idx and a.sign == -b.sign
            anti_rows.append(
                {
                    "i": i,
                    "j": j,
                    "ij_out_idx": a.out_idx,
                    "ij_sign": a.sign,
                    "ji_out_idx": b.out_idx,
                    "ji_sign": b.sign,
                    "anti_comm_match": ok,
                }
            )
            if ok:
                anti_matched += 1

    table_sha256 = _hash_rows(rows)

    return {
        "schema_version": "xor_basis_conformance_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "table_sha256": table_sha256,
        "summary": {
            "basis_row_count": len(rows),
            "expected_match_count": expected_matched,
            "xor_channel_checked_count": xor_checked,
            "xor_channel_match_count": xor_matched,
            "handed_alignment_match_count": handed_alignment_matched,
            "anti_comm_checked_count": anti_checked,
            "anti_comm_match_count": anti_matched,
            "all_expected_match": expected_matched == len(rows),
            "all_xor_channel_match": xor_checked == xor_matched,
            "all_handed_alignment_match": handed_alignment_matched == len(rows),
            "all_anti_comm_match": anti_checked == anti_matched,
        },
        "basis_rows": rows,
        "anti_comm_rows": anti_rows,
    }


def write_xor_basis_conformance_artifacts(
    dataset: dict[str, Any],
    json_paths: list[Path] | None = None,
    csv_paths: list[Path] | None = None,
) -> None:
    if json_paths is None:
        json_paths = [Path("calc/xor_basis_conformance.json")]
    if csv_paths is None:
        csv_paths = [Path("calc/xor_basis_conformance.csv")]

    for path in json_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(dataset, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "i",
        "j",
        "out_idx",
        "sign",
        "expected_out_idx",
        "expected_sign",
        "rule",
        "matches_expected",
        "xor_idx",
        "xor_channel_match",
        "handed_alignment_match",
    ]
    for path in csv_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in dataset["basis_rows"]:
                writer.writerow(row)


def main() -> int:
    dataset = build_xor_basis_conformance_dataset()
    write_xor_basis_conformance_artifacts(
        dataset,
        json_paths=[
            Path("calc/xor_basis_conformance.json"),
            Path("website/data/xor_basis_conformance.json"),
        ],
        csv_paths=[
            Path("calc/xor_basis_conformance.csv"),
            Path("website/data/xor_basis_conformance.csv"),
        ],
    )
    print("Wrote calc/xor_basis_conformance.json")
    print("Wrote calc/xor_basis_conformance.csv")
    print("Wrote website/data/xor_basis_conformance.json")
    print("Wrote website/data/xor_basis_conformance.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

