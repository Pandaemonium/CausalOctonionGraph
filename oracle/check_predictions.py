#!/usr/bin/env python3
"""
Nightly prediction oracle with hard + soft classification.

Outputs:
1) sources/oracle_report.json
2) sources/oracle_mismatch_events.json (backward-compatible subset)
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
    tolerance_rel_soft: float
    tolerance_rel_critical: float
    source: str


TARGETS: tuple[Target, ...] = (
    Target(
        claim_id="QN-006",
        quantity="sin2_theta_W_MZ",
        expected=0.23122,
        tolerance_abs=0.005,
        tolerance_rel_soft=0.75,
        tolerance_rel_critical=2.0,
        source="PDG-style electroweak reference target (configured in oracle)",
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


def _classify(target: Target, observed_value: float) -> tuple[str, float, float]:
    abs_error = abs(observed_value - target.expected)
    denom = abs(target.expected) if abs(target.expected) > 1e-12 else 1.0
    rel_error = abs_error / denom
    if abs_error <= target.tolerance_abs:
        return "hard_pass", abs_error, rel_error
    if rel_error <= target.tolerance_rel_soft:
        return "soft_pass", abs_error, rel_error
    if rel_error <= target.tolerance_rel_critical:
        return "mismatch", abs_error, rel_error
    return "critical_mismatch", abs_error, rel_error


def _event_for_comparison(now: str, idx: int, cmp_row: dict[str, Any]) -> dict[str, Any]:
    status = str(cmp_row.get("status", ""))
    claim_id = str(cmp_row.get("claim_id", ""))
    quantity = str(cmp_row.get("quantity", ""))
    if status == "soft_pass":
        event_type = "oracle_soft_pass"
        task_type = "prediction_review"
    elif status == "mismatch":
        event_type = "oracle_mismatch"
        task_type = "falsification_task"
    elif status == "critical_mismatch":
        event_type = "oracle_critical_mismatch"
        task_type = "direction_review"
    elif status == "missing_observation":
        event_type = "oracle_missing_observation"
        task_type = "prediction_review"
    else:
        event_type = "oracle_info"
        task_type = "none"

    return {
        "event_id": f"{event_type}_{now}_{idx}",
        "event_type": event_type,
        "created_at_utc": now,
        "claim_id": claim_id,
        "quantity": quantity,
        "expected": cmp_row.get("expected"),
        "observed": cmp_row.get("observed"),
        "abs_error": cmp_row.get("abs_error"),
        "rel_error": cmp_row.get("rel_error"),
        "tolerance_abs": cmp_row.get("tolerance_abs"),
        "tolerance_rel_soft": cmp_row.get("tolerance_rel_soft"),
        "tolerance_rel_critical": cmp_row.get("tolerance_rel_critical"),
        "source": cmp_row.get("source"),
        "recommended_task_type": task_type,
    }


def run_oracle() -> dict[str, Any]:
    observed = _observed_predictions()
    comparisons: list[dict[str, Any]] = []
    action_events: list[dict[str, Any]] = []

    now = _utc_now()
    for target in TARGETS:
        obs = observed.get(target.claim_id)
        if obs is None:
            row = {
                "claim_id": target.claim_id,
                "quantity": target.quantity,
                "status": "missing_observation",
                "expected": target.expected,
                "observed": None,
                "abs_error": None,
                "rel_error": None,
                "tolerance_abs": target.tolerance_abs,
                "tolerance_rel_soft": target.tolerance_rel_soft,
                "tolerance_rel_critical": target.tolerance_rel_critical,
                "source": target.source,
                "provenance": "",
            }
            comparisons.append(row)
            action_events.append(_event_for_comparison(now, len(action_events), row))
            continue

        observed_value = float(obs["value"])
        status, abs_error, rel_error = _classify(target, observed_value)
        row = {
            "claim_id": target.claim_id,
            "quantity": target.quantity,
            "status": status,
            "expected": target.expected,
            "observed": observed_value,
            "abs_error": abs_error,
            "rel_error": rel_error,
            "tolerance_abs": target.tolerance_abs,
            "tolerance_rel_soft": target.tolerance_rel_soft,
            "tolerance_rel_critical": target.tolerance_rel_critical,
            "source": target.source,
            "provenance": obs.get("provenance", ""),
        }
        comparisons.append(row)
        if status in {"soft_pass", "mismatch", "critical_mismatch"}:
            action_events.append(_event_for_comparison(now, len(action_events), row))

    hard_pass_count = sum(1 for row in comparisons if row.get("status") == "hard_pass")
    soft_pass_count = sum(1 for row in comparisons if row.get("status") == "soft_pass")
    mismatch_count = sum(1 for row in comparisons if row.get("status") == "mismatch")
    critical_mismatch_count = sum(1 for row in comparisons if row.get("status") == "critical_mismatch")

    # Backward-compatible mismatch subset for existing consumers.
    mismatch_events = [
        ev for ev in action_events if ev.get("event_type") in {"oracle_mismatch", "oracle_critical_mismatch"}
    ]

    return {
        "schema_version": "oracle_report_v2",
        "generated_at_utc": now,
        "comparison_count": len(comparisons),
        "hard_pass_count": hard_pass_count,
        "soft_pass_count": soft_pass_count,
        "mismatch_count": mismatch_count,
        "critical_mismatch_count": critical_mismatch_count,
        "action_event_count": len(action_events),
        "comparisons": comparisons,
        "action_events": action_events,
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
    print(
        "Oracle counts: "
        f"hard={report['hard_pass_count']} "
        f"soft={report['soft_pass_count']} "
        f"mismatch={report['mismatch_count']} "
        f"critical={report['critical_mismatch_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

