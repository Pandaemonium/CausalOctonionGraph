#!/usr/bin/env python3
"""
Single-command claim-promotion gate.

Pipeline:
1. sync matrix
2. validate matrix
3. validate claim epistemic schema fields
4. rebuild + validate quantum-number claim ledger
5. run oracle prediction checks
6. build manager context package (includes oracle block)
7. validate claim events
8. validate public accomplishments
9. run battery checks for selected statuses
10. build proof-ledger artifacts
11. optionally enforce matrix/ledger are committed and up-to-date
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _run(cmd: list[str]) -> int:
    print(f"+ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=ROOT, check=False).returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--battery-statuses",
        default="supported_bridge,proved_core",
        help="Comma-separated statuses to evaluate in battery checks (default: supported_bridge,proved_core).",
    )
    parser.add_argument(
        "--enforce-clean-matrix",
        action="store_true",
        help="Fail if claims/CLAIM_STATUS_MATRIX.yml has uncommitted changes after sync.",
    )
    parser.add_argument(
        "--enforce-clean-ledger",
        action="store_true",
        help="Fail if sources/qn_claim_ledger.json has uncommitted changes after rebuild.",
    )
    args = parser.parse_args()

    steps = [
        [sys.executable, "scripts/sync_claim_status_matrix.py"],
        [sys.executable, "scripts/validate_claim_status_matrix.py"],
        [sys.executable, "scripts/validate_claim_epistemic_fields.py"],
        [sys.executable, "-m", "calc.derive_sm_quantum_numbers"],
        [
            sys.executable,
            "scripts/validate_qn_claim_ledger.py",
            "--path",
            "sources/qn_claim_ledger.json",
            "--require-lean-backed-statuses",
            "core_derived",
        ],
        [sys.executable, "oracle/check_predictions.py"],
        [sys.executable, "scripts/build_manager_context_package.py"],
        [sys.executable, "scripts/validate_claim_events.py"],
        [sys.executable, "scripts/validate_public_accomplishments.py"],
        [
            sys.executable,
            "scripts/check_claim_batteries.py",
            "--statuses",
            args.battery_statuses,
        ],
        [sys.executable, "scripts/build_proof_ledger_artifacts.py"],
    ]
    for step in steps:
        rc = _run(step)
        if rc != 0:
            return rc

    if args.enforce_clean_matrix:
        rc = _run(["git", "diff", "--exit-code", "claims/CLAIM_STATUS_MATRIX.yml"])
        if rc != 0:
            print(
                "ERROR: claims/CLAIM_STATUS_MATRIX.yml is stale. "
                "Run scripts/sync_claim_status_matrix.py and commit the result."
            )
            return rc

    if args.enforce_clean_ledger:
        rc = _run(["git", "diff", "--exit-code", "sources/qn_claim_ledger.json"])
        if rc != 0:
            print(
                "ERROR: sources/qn_claim_ledger.json is stale. "
                "Run python -m calc.derive_sm_quantum_numbers and commit the result."
            )
            return rc

    print("Claim-promotion pipeline passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
