#!/usr/bin/env python3
"""
Nightly prediction oracle stub.

Compares selected model predictions to fixed reference targets and writes:
1) sources/oracle_report.json
2) sources/oracle_mismatch_events.json
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from calc.derive_sm_quantum_numbers import derive_all


OUT_REPORT = ROOT / "sources" / "oracle_report.json"
OUT_EVENTS = ROOT / "sources" / "oracle_mismatch_events.json"


@dataclass(frozen=True)
class Target:
    claim_id: str
    quantity: str
    expected: float
    tolerance_abs: float
    source: str


TARGETS: tuple[Target, ...] = (
    Target(
        claim_id="QN-006",
        quantity="sin2_theta_W_MZ",
        expected=0.23122,
        tolerance_abs=0.005,
        source="PDG-style electroweak reference target (configured in oracle stub)",
    ),
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _observed_predictions() -> dict[str, dict[str, Any]]:
    by_id = {row["claim"]: row for row in derive_all()}
    out: dict[str, dict[str, Any]] = {}
    if "QN-006" in by_id:
        out["QN-006"] = {
            "quantity": "sin2_theta_W_MZ",
            "value": float(by_id["QN-006"]["sin2_theta_W_float"]),
            "provenance": "calc.derive_sm_quantum_numbers::derive_weinberg_angle",
        }
    return out


def run_oracle() -> dict[str, Any]:
    observed = _observed_predictions()
    comparisons: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []

    now = _utc_now()
    for target in TARGETS:
        obs = observed.get(target.claim_id)
        if obs is None:
            comparisons.append(
                {
                    "claim_id": target.claim_id,
                    "quantity": target.quantity,
                    "status": "missing_observation",
                    "expected": target.expected,
                    "tolerance_abs": target.tolerance_abs,
                    "source": target.source,
                }
            )
            continue

        observed_value = float(obs["value"])
        abs_error = abs(observed_value - target.expected)
        within_tolerance = abs_error <= target.tolerance_abs
        record = {
            "claim_id": target.claim_id,
            "quantity": target.quantity,
            "expected": target.expected,
            "observed": observed_value,
            "abs_error": abs_error,
            "tolerance_abs": target.tolerance_abs,
            "within_tolerance": within_tolerance,
            "source": target.source,
            "provenance": obs.get("provenance", ""),
            "status": "ok" if within_tolerance else "mismatch",
        }
        comparisons.append(record)
        if not within_tolerance:
            mismatches.append(record)

    mismatch_events = []
    for idx, mismatch in enumerate(mismatches):
        mismatch_events.append(
            {
                "event_id": f"oracle_mismatch_{now}_{idx}",
                "event_type": "oracle_mismatch",
                "created_at_utc": now,
                "claim_id": mismatch["claim_id"],
                "quantity": mismatch["quantity"],
                "expected": mismatch["expected"],
                "observed": mismatch["observed"],
                "abs_error": mismatch["abs_error"],
                "tolerance_abs": mismatch["tolerance_abs"],
                "source": mismatch["source"],
                "recommended_task_type": "prediction_review",
            }
        )

    return {
        "schema_version": "oracle_report_v1",
        "generated_at_utc": now,
        "comparison_count": len(comparisons),
        "mismatch_count": len(mismatch_events),
        "comparisons": comparisons,
        "mismatch_events": mismatch_events,
    }


def write_outputs(report: dict[str, Any]) -> None:
    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_EVENTS.write_text(json.dumps(report["mismatch_events"], indent=2) + "\n", encoding="utf-8")


def main() -> int:
    report = run_oracle()
    write_outputs(report)
    print(f"Wrote {OUT_REPORT}")
    print(f"Wrote {OUT_EVENTS}")
    print(f"Oracle mismatch_count={report['mismatch_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
