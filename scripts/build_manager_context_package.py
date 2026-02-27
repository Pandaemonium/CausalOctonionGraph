#!/usr/bin/env python3
"""
Build compact manager context package with oracle block.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "claims" / "CLAIM_STATUS_MATRIX.yml"
QN_LEDGER_PATH = ROOT / "sources" / "qn_claim_ledger.json"
ORACLE_REPORT_PATH = ROOT / "sources" / "oracle_report.json"
OUT_PATH = ROOT / "sources" / "manager_context_package.json"


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return {}
    if not isinstance(loaded, dict):
        return {}
    return loaded


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(loaded, dict):
        return {}
    return loaded


def _status_rank(status: str) -> int:
    order = {
        "active_hypothesis": 0,
        "partial": 1,
        "stub": 2,
        "supported": 3,
        "falsified": 4,
        "superseded": 5,
    }
    return order.get(status, 99)


def build_package(top_n: int = 10) -> dict[str, Any]:
    matrix = _read_yaml(MATRIX_PATH)
    qn_ledger = _read_json(QN_LEDGER_PATH)
    oracle = _read_json(ORACLE_REPORT_PATH)

    rows = matrix.get("rows", {})
    if not isinstance(rows, dict):
        rows = {}

    counts = Counter()
    open_claims: list[dict[str, Any]] = []
    for claim_id, row in rows.items():
        if not isinstance(row, dict):
            continue
        status = str(row.get("status", "stub"))
        counts[status] += 1
        if status in {"supported", "falsified", "superseded"}:
            continue
        bridge = row.get("bridge_assumptions", [])
        if not isinstance(bridge, list):
            bridge = []
        open_claims.append(
            {
                "claim_id": claim_id,
                "status": status,
                "derivation_status": row.get("derivation_status", "untested"),
                "assumption_load": len([x for x in bridge if isinstance(x, str) and x.strip()]),
                "falsification_condition": row.get("falsification_condition", ""),
                "owner_rfc": row.get("owner_rfc", ""),
            }
        )

    open_claims.sort(key=lambda c: (_status_rank(str(c["status"])), c["assumption_load"], c["claim_id"]))
    top_open_claims = open_claims[:top_n]

    oracle_block = {
        "generated_at_utc": oracle.get("generated_at_utc", ""),
        "mismatch_count": oracle.get("mismatch_count", 0),
        "comparison_count": oracle.get("comparison_count", 0),
        "mismatches": oracle.get("mismatch_events", [])[:10],
    }

    qn_rows = qn_ledger.get("rows", [])
    if not isinstance(qn_rows, list):
        qn_rows = []
    assumption_density = []
    for row in qn_rows:
        if not isinstance(row, dict):
            continue
        assumptions = row.get("assumptions", [])
        if not isinstance(assumptions, list):
            assumptions = []
        assumption_density.append(
            {
                "claim_id": row.get("claim_id", ""),
                "status": row.get("status", ""),
                "assumption_count": len([x for x in assumptions if isinstance(x, str) and x.strip()]),
                "confidence": row.get("confidence", ""),
            }
        )

    return {
        "schema_version": "manager_context_package_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "summary": {
            "matrix_row_count": len(rows),
            "counts_by_status": dict(sorted(counts.items())),
            "top_open_claim_count": len(top_open_claims),
        },
        "top_open_claims": top_open_claims,
        "oracle": oracle_block,
        "qn_assumption_density": assumption_density,
    }


def main() -> int:
    package = build_package(top_n=10)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

