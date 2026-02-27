#!/usr/bin/env python3
"""
Build XOR ensemble + report artifacts from a scenario YAML file.

Usage:
  python scripts/build_xor_ensemble_report.py
  python scripts/build_xor_ensemble_report.py path/to/scenarios.yml
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calc.xor_ensemble_runner import run_ensemble_from_yaml, write_xor_ensemble_artifacts
from calc.xor_report_builder import build_ensemble_report, write_xor_report_artifacts


def main() -> int:
    if len(sys.argv) > 1:
        spec_path = Path(sys.argv[1])
    else:
        spec_path = Path("sources/xor_scenarios_sample.yml")

    dataset = run_ensemble_from_yaml(spec_path)
    write_xor_ensemble_artifacts(
        dataset,
        json_paths=[
            Path("calc/xor_ensemble_results.json"),
            Path("website/data/xor_ensemble_results.json"),
        ],
        csv_paths=[
            Path("calc/xor_ensemble_results.csv"),
            Path("website/data/xor_ensemble_results.csv"),
        ],
    )

    report = build_ensemble_report(dataset)
    write_xor_report_artifacts(
        report,
        json_paths=[
            Path("calc/xor_ensemble_report.json"),
            Path("website/data/xor_ensemble_report.json"),
        ],
        md_paths=[
            Path("sources/xor_ensemble_report.md"),
        ],
    )

    print(f"Loaded scenarios from {spec_path}")
    print("Wrote calc/xor_ensemble_results.json")
    print("Wrote calc/xor_ensemble_results.csv")
    print("Wrote website/data/xor_ensemble_results.json")
    print("Wrote website/data/xor_ensemble_results.csv")
    print("Wrote calc/xor_ensemble_report.json")
    print("Wrote website/data/xor_ensemble_report.json")
    print("Wrote sources/xor_ensemble_report.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

