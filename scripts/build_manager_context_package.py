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

try:
    from scripts.claim_contract_gates import evaluate_contract_gates, load_claim_docs
except ModuleNotFoundError:
    from claim_contract_gates import evaluate_contract_gates, load_claim_docs


ROOT = Path(__file__).resolve().parents[1]
CLAIMS_DIR = ROOT / "claims"
MATRIX_PATH = ROOT / "claims" / "CLAIM_STATUS_MATRIX.yml"
QN_LEDGER_PATH = ROOT / "sources" / "qn_claim_ledger.json"
ORACLE_REPORT_PATH = ROOT / "sources" / "oracle_report.json"
OUT_PATH = ROOT / "sources" / "manager_context_package.json"

PROMOTED_STATUSES = {"supported", "supported_bridge", "proved_core"}
CLOSED_STATUSES = PROMOTED_STATUSES | {"falsified", "superseded"}


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
        "supported_bridge": 3,
        "proved_core": 4,
        "supported": 5,
        "falsified": 4,
        "superseded": 5,
    }
    return order.get(status, 99)


def _canonical_status(status: str) -> str:
    if status == "supported":
        return "supported_bridge"
    return status


def _extract_claim_id(path: Path, data: dict[str, Any]) -> str:
    for key in ("id", "claim_id", "name"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return path.stem.upper()


def _load_dependencies(valid_claim_ids: set[str]) -> dict[str, list[str]]:
    deps_by_claim: dict[str, list[str]] = {}
    for path in sorted(CLAIMS_DIR.glob("*.yml")):
        if path.name == "CLAIM_STATUS_MATRIX.yml":
            continue
        data = _read_yaml(path)
        if not data:
            continue
        claim_id = _extract_claim_id(path, data)
        raw = data.get("depends_on", [])
        if not isinstance(raw, list):
            continue
        deps = sorted({str(x).strip() for x in raw if isinstance(x, str) and str(x).strip() in valid_claim_ids})
        if deps:
            deps_by_claim[claim_id] = deps
    return deps_by_claim


def build_package(top_n: int = 10) -> dict[str, Any]:
    matrix = _read_yaml(MATRIX_PATH)
    qn_ledger = _read_json(QN_LEDGER_PATH)
    oracle = _read_json(ORACLE_REPORT_PATH)

    rows = matrix.get("rows", {})
    if not isinstance(rows, dict):
        rows = {}
    deps_by_claim = _load_dependencies(set(rows.keys()))
    claim_docs = load_claim_docs(CLAIMS_DIR)

    counts = Counter()
    open_claims: list[dict[str, Any]] = []
    contradictions: list[str] = []
    blocked_promotions: list[dict[str, Any]] = []
    for claim_id, row in rows.items():
        if not isinstance(row, dict):
            continue
        status_raw = str(row.get("status", "stub"))
        status = _canonical_status(status_raw)
        derivation_status = str(row.get("derivation_status", "untested"))
        falsification_condition = str(row.get("falsification_condition", "")).strip()
        bridge = row.get("bridge_assumptions", [])
        if not isinstance(bridge, list):
            bridge = []
        assumption_count = len([x for x in bridge if isinstance(x, str) and x.strip()])

        counts[status] += 1
        if status == "supported_bridge" and derivation_status != "bridge_assumed":
            contradictions.append(
                f"{claim_id} marked supported_bridge but derivation_status={derivation_status}."
            )
        if status == "proved_core" and derivation_status != "core_derived":
            contradictions.append(
                f"{claim_id} marked proved_core but derivation_status={derivation_status}."
            )
        if status == "proved_core" and assumption_count > 0:
            contradictions.append(f"{claim_id} marked proved_core but has {assumption_count} bridge assumptions.")
        if derivation_status == "core_derived" and assumption_count > 0:
            contradictions.append(f"{claim_id} has core_derived with non-empty bridge assumptions.")

        if status in CLOSED_STATUSES:
            continue

        reasons: list[str] = []
        if derivation_status == "untested":
            reasons.append("derivation_status=untested")
        if derivation_status == "bridge_assumed" and assumption_count == 0:
            reasons.append("bridge_assumptions missing")
        if not falsification_condition:
            reasons.append("falsification_condition missing")
        if reasons:
            blocked_promotions.append(
                {
                    "claim_id": claim_id,
                    "status": status,
                    "reasons": reasons,
                }
            )

        open_claims.append(
            {
                "claim_id": claim_id,
                "status": status,
                "derivation_status": derivation_status,
                "assumption_load": assumption_count,
                "falsification_condition": falsification_condition,
                "owner_rfc": row.get("owner_rfc", ""),
                "depends_on": deps_by_claim.get(claim_id, []),
            }
        )

    open_claims.sort(key=lambda c: (_status_rank(str(c["status"])), c["assumption_load"], c["claim_id"]))
    top_open_claims = open_claims[:top_n]

    action_events = oracle.get("action_events", oracle.get("mismatch_events", []))
    if not isinstance(action_events, list):
        action_events = []
    oracle_block = {
        "generated_at_utc": oracle.get("generated_at_utc", ""),
        "mismatch_count": oracle.get("mismatch_count", 0),
        "critical_mismatch_count": oracle.get("critical_mismatch_count", 0),
        "soft_pass_count": oracle.get("soft_pass_count", 0),
        "hard_pass_count": oracle.get("hard_pass_count", 0),
        "comparison_count": oracle.get("comparison_count", 0),
        "action_event_count": oracle.get("action_event_count", len(action_events)),
        "action_events": action_events[:10],
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

    semantic_digest: list[str] = []
    semantic_digest.append(
        f"There are {len(open_claims)} open claims; top-{len(top_open_claims)} are prioritized by status then assumption load."
    )
    for claim in top_open_claims[:5]:
        claim_id = str(claim["claim_id"])
        deps = claim.get("depends_on", [])
        if isinstance(deps, list) and deps:
            semantic_digest.append(
                f"{claim_id} depends on unresolved upstream claims: {', '.join(str(x) for x in deps)}."
            )
        else:
            semantic_digest.append(f"{claim_id} has no declared unresolved dependencies in claim metadata.")
        semantic_digest.append(
            f"{claim_id} is {claim['status']} with derivation_status={claim['derivation_status']} and assumption_load={claim['assumption_load']}."
        )
    if contradictions:
        semantic_digest.append(f"Detected {len(contradictions)} contradiction(s) requiring manager attention.")
    if blocked_promotions:
        semantic_digest.append(f"{len(blocked_promotions)} open claims are currently blocked on governance fields.")
    if int(oracle_block["action_event_count"]) > 0:
        semantic_digest.append(
            f"Oracle generated {oracle_block['action_event_count']} action event(s); prioritize prediction_review/falsification follow-ups."
        )

    contract_gate_issues = evaluate_contract_gates(
        rows=rows,
        claim_docs=claim_docs,
        root=ROOT,
        enforce_for_statuses={"partial", "supported_bridge", "proved_core"},
    )
    contract_gate_errors = [x for x in contract_gate_issues if x.severity == "error"]
    contract_gate_warnings = [x for x in contract_gate_issues if x.severity == "warn"]
    if contract_gate_errors:
        semantic_digest.append(
            f"{len(contract_gate_errors)} contract-gate blocker(s) detected for RFC-080/081/082/083."
        )

    return {
        "schema_version": "manager_context_package_v2",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "summary": {
            "matrix_row_count": len(rows),
            "counts_by_status": dict(sorted(counts.items())),
            "top_open_claim_count": len(top_open_claims),
            "contradiction_count": len(contradictions),
            "blocked_promotion_count": len(blocked_promotions),
            "contract_gate_error_count": len(contract_gate_errors),
            "contract_gate_warning_count": len(contract_gate_warnings),
        },
        "top_open_claims": top_open_claims,
        "contradictions": contradictions[:20],
        "blocked_promotions": blocked_promotions[:20],
        "contract_gate_blockers": [i.message for i in contract_gate_errors[:20]],
        "contract_gate_warnings": [i.message for i in contract_gate_warnings[:20]],
        "oracle": oracle_block,
        "qn_assumption_density": assumption_density,
        "semantic_digest": semantic_digest,
    }


def main() -> int:
    package = build_package(top_n=10)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
