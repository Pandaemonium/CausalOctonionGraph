#!/usr/bin/env python3
"""
Run claim battery checks from claims/CLAIM_STATUS_MATRIX.yml.

For selected statuses (default: supported), this script:
1. ensures each battery artifact exists (for file paths),
2. runs pytest selectors for artifacts containing "::",
3. runs pytest on test files referenced directly (e.g. calc/test_x.py).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "claims" / "CLAIM_STATUS_MATRIX.yml"


def _read_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        return {}
    return loaded


def _run(cmd: list[str]) -> int:
    print(f"+ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=ROOT, check=False).returncode


def _is_test_file(path: Path) -> bool:
    return path.name.startswith("test_") and path.suffix == ".py"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--statuses",
        default="supported",
        help="Comma-separated statuses to enforce (default: supported).",
    )
    args = parser.parse_args()
    statuses = {s.strip() for s in args.statuses.split(",") if s.strip()}

    if not MATRIX_PATH.exists():
        print(f"ERROR: matrix file not found: {MATRIX_PATH}")
        return 1

    matrix = _read_yaml(MATRIX_PATH)
    rows = matrix.get("rows", {})
    if not isinstance(rows, dict):
        print("ERROR: matrix.rows missing or invalid")
        return 1

    selected: list[tuple[str, dict[str, Any]]] = []
    for claim_id, row in rows.items():
        if not isinstance(row, dict):
            continue
        if row.get("status") in statuses:
            selected.append((claim_id, row))

    if not selected:
        print(f"No claims with statuses {sorted(statuses)}; battery check is a no-op.")
        return 0

    failures: list[str] = []
    ran_pytest_targets: set[str] = set()

    for claim_id, row in selected:
        artifacts = row.get("battery_artifacts") or []
        if not isinstance(artifacts, list) or not artifacts:
            failures.append(f"{claim_id}: empty battery_artifacts")
            continue

        print(f"== {claim_id} ({row.get('status')}) ==")
        for artifact in artifacts:
            if not isinstance(artifact, str) or not artifact.strip():
                failures.append(f"{claim_id}: invalid battery artifact {artifact!r}")
                continue
            artifact = artifact.strip()

            if "::" in artifact:
                if artifact not in ran_pytest_targets:
                    rc = _run([sys.executable, "-m", "pytest", "-q", artifact])
                    ran_pytest_targets.add(artifact)
                    if rc != 0:
                        failures.append(f"{claim_id}: pytest selector failed: {artifact}")
                continue

            artifact_path = ROOT / artifact
            if not artifact_path.exists():
                failures.append(f"{claim_id}: missing artifact path: {artifact}")
                continue

            if _is_test_file(artifact_path):
                target = artifact
                if target not in ran_pytest_targets:
                    rc = _run([sys.executable, "-m", "pytest", "-q", target])
                    ran_pytest_targets.add(target)
                    if rc != 0:
                        failures.append(f"{claim_id}: pytest file failed: {target}")

    if failures:
        print(f"Battery checks failed ({len(failures)}):")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"Battery checks passed for {len(selected)} claim(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
