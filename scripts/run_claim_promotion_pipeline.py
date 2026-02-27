#!/usr/bin/env python3
"""
Single-command claim-promotion gate.

Pipeline:
1. sync matrix
2. validate matrix
3. run battery checks for selected statuses
4. optionally enforce matrix is committed/up-to-date
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
        default="supported",
        help="Comma-separated statuses to evaluate in battery checks (default: supported).",
    )
    parser.add_argument(
        "--enforce-clean-matrix",
        action="store_true",
        help="Fail if claims/CLAIM_STATUS_MATRIX.yml has uncommitted changes after sync.",
    )
    args = parser.parse_args()

    steps = [
        [sys.executable, "scripts/sync_claim_status_matrix.py"],
        [sys.executable, "scripts/validate_claim_status_matrix.py"],
        [
            sys.executable,
            "scripts/check_claim_batteries.py",
            "--statuses",
            args.battery_statuses,
        ],
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

    print("Claim-promotion pipeline passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
