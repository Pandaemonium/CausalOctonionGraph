#!/usr/bin/env python3
"""
Validate promotion-time contract gates for RFC-080/081/082/083.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

try:
    from scripts.claim_contract_gates import evaluate_contract_gates, load_claim_docs
except ModuleNotFoundError:
    from claim_contract_gates import evaluate_contract_gates, load_claim_docs


ROOT = Path(__file__).resolve().parents[1]
CLAIMS_DIR = ROOT / "claims"
MATRIX_PATH = CLAIMS_DIR / "CLAIM_STATUS_MATRIX.yml"


def _read_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        return {}
    return loaded


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--statuses",
        default="supported_bridge,proved_core",
        help="Comma-separated statuses to enforce gates for (default: supported_bridge,proved_core).",
    )
    args = parser.parse_args()

    enforce_statuses = {s.strip() for s in args.statuses.split(",") if s.strip()}
    if not MATRIX_PATH.exists():
        print(f"ERROR: matrix file not found: {MATRIX_PATH}")
        return 1

    matrix = _read_yaml(MATRIX_PATH)
    rows = matrix.get("rows", {})
    if not isinstance(rows, dict):
        print("ERROR: matrix.rows missing or invalid")
        return 1

    claim_docs = load_claim_docs(CLAIMS_DIR)
    issues = evaluate_contract_gates(
        rows=rows,
        claim_docs=claim_docs,
        root=ROOT,
        enforce_for_statuses=enforce_statuses,
    )

    errors = [i for i in issues if i.severity == "error"]
    warns = [i for i in issues if i.severity == "warn"]

    for w in warns:
        print(f"WARN: {w.message}")

    if errors:
        print(f"Validation failed with {len(errors)} error(s):")
        for e in errors:
            print(f"- {e.message}")
        return 1

    print(
        f"OK: validated contract gates for statuses {sorted(enforce_statuses)} "
        f"(warnings={len(warns)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
