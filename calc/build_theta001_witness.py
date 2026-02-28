"""Build deterministic THETA-001 CP-invariance witness artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from calc.theta001_cp_invariant import (
    FANO_TRIPLES,
    cp_dual_trace_relation_holds,
    cp_weighted_trace_delta,
    fano_sign_balance_counts,
    orientation_reversal_closed_on_fano_lines,
    weak_leakage_strong_residual,
)

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "sources" / "theta001_cp_witness.json"
OUT_MD = ROOT / "sources" / "theta001_cp_witness.md"

SCRIPT_REPO_PATH = "calc/build_theta001_witness.py"
WITNESS_MODULE_REPO_PATH = "calc/theta001_cp_invariant.py"

DEFAULT_WEIGHTS: Tuple[int, ...] = (1, 2, 3, 4, 5, 6, 7, 8)
WITNESS_CASES: Tuple[Tuple[str, Tuple[int, ...], Tuple[int, ...]], ...] = (
    (
        "theta_case_001",
        (1, 2, -1, 0, 3, -2, 1, 4),
        (1, 7, 3, 5, 2, 6, 4, 1, 2, 3),
    ),
    (
        "theta_case_002",
        (2, -1, 0, 3, -2, 1, 4, -3),
        (7, 1, 4, 2, 6, 3, 5, 7, 4, 2),
    ),
    (
        "theta_case_003",
        (-3, 1, 2, -4, 5, -6, 7, -8),
        (3, 5, 7, 2, 4, 6, 1, 3, 5, 7),
    ),
)
WEAK_LEAKAGE_CASE: Dict[str, Any] = {
    "case_id": "theta_weak_leakage_001",
    "initial_state": [1, -2, 3, -4, 5, -6, 7, -1],
    "op_sequence": [7, 1, 7, 2, 7, 3, 7, 4, 7, 5, 7, 6, 7, 1, 2, 3],
    "weak_kick": 5,
    "phase_shift": 3,
}


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _to_repo_path(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def _build_trace_suite(
    *,
    weights: Sequence[int],
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for case_id, initial_state, op_sequence in WITNESS_CASES:
        cp_dual_ok = cp_dual_trace_relation_holds(initial_state, op_sequence)
        weighted_delta = cp_weighted_trace_delta(initial_state, op_sequence, weights)
        rows.append(
            {
                "case_id": case_id,
                "initial_state": list(initial_state),
                "op_sequence": list(op_sequence),
                "cp_dual_relation_holds": cp_dual_ok,
                "weighted_trace_delta": int(weighted_delta),
            }
        )
    return rows


def build_witness_payload(
    *,
    policy_id: str = "theta001_cp_invariance_v1",
    weights: Sequence[int] = DEFAULT_WEIGHTS,
) -> Dict[str, Any]:
    script_path = ROOT / SCRIPT_REPO_PATH
    witness_module_path = ROOT / WITNESS_MODULE_REPO_PATH

    pos_count, neg_count, signed_sum = fano_sign_balance_counts()
    orientation_closed = orientation_reversal_closed_on_fano_lines(FANO_TRIPLES)
    trace_suite = _build_trace_suite(weights=weights)
    weak_leakage_delta = weak_leakage_strong_residual(
        tuple(int(x) for x in WEAK_LEAKAGE_CASE["initial_state"]),
        tuple(int(x) for x in WEAK_LEAKAGE_CASE["op_sequence"]),
        weak_kick=int(WEAK_LEAKAGE_CASE["weak_kick"]),
        phase_shift=int(WEAK_LEAKAGE_CASE["phase_shift"]),
    )

    max_abs_weighted_delta = max(abs(int(row["weighted_trace_delta"])) for row in trace_suite)
    all_cp_dual_hold = all(bool(row["cp_dual_relation_holds"]) for row in trace_suite)
    all_weighted_zero = all(int(row["weighted_trace_delta"]) == 0 for row in trace_suite)

    payload: Dict[str, Any] = {
        "schema_version": "theta001_cp_witness_v1",
        "claim_id": "THETA-001",
        "policy_id": policy_id,
        "closure_scope": "structure_first",
        "continuum_value_derivation": False,
        "validation_scale": "reduced_scale",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "witness_module": WITNESS_MODULE_REPO_PATH,
        "witness_module_sha256": _sha_file(witness_module_path),
        "fano_sign_balance": {
            "positive_count": int(pos_count),
            "negative_count": int(neg_count),
            "signed_sum": int(signed_sum),
        },
        "orientation_reversal_closed_on_fano_lines": bool(orientation_closed),
        "orientation_triple_count": len(FANO_TRIPLES),
        "weights": [int(w) for w in weights],
        "trace_suite": trace_suite,
        "weak_leakage_case": WEAK_LEAKAGE_CASE,
        "weak_leakage_strong_residual": int(weak_leakage_delta),
        "theta_residual_summary": {
            "cp_dual_all_hold": all_cp_dual_hold,
            "weighted_trace_all_zero": all_weighted_zero,
            "weak_leakage_strong_residual_zero": int(weak_leakage_delta) == 0,
            "max_abs_weighted_trace_delta": int(max_abs_weighted_delta),
            "fano_signed_sum_zero": int(signed_sum) == 0,
            "discrete_fano_cp_residual_zero": bool(
                all_cp_dual_hold
                and all_weighted_zero
                and int(weak_leakage_delta) == 0
                and int(signed_sum) == 0
                and orientation_closed
            ),
        },
    }
    # Backward-compatibility key for existing downstream consumers.
    payload["theta_residual_summary"]["theta_cp_odd_residual_forced_zero"] = payload[
        "theta_residual_summary"
    ]["discrete_fano_cp_residual_zero"]
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def render_markdown(payload: Dict[str, Any]) -> str:
    bal = payload["fano_sign_balance"]
    res = payload["theta_residual_summary"]
    lines = [
        "# THETA-001 CP-Invariance Witness",
        "",
        f"- Claim: `{payload['claim_id']}`",
        f"- Policy: `{payload['policy_id']}`",
        f"- Replay hash: `{payload['replay_hash']}`",
        f"- Source script: `{payload['source_script']}`",
        f"- Witness module: `{payload['witness_module']}`",
        "",
        "## Scope And Scale",
        f"- Closure scope: `{payload['closure_scope']}`",
        f"- Continuum value derivation: `{payload['continuum_value_derivation']}`",
        f"- Validation scale: `{payload['validation_scale']}`",
        f"- Trace case count: `{len(payload['trace_suite'])}`",
        "",
        "## Replay Verification",
        "Run `python -m calc.build_theta001_witness --write-sources` and verify the replay hash in the JSON output is unchanged.",
        "",
        "## Fano Sign Balance",
        f"- Positive count: {bal['positive_count']}",
        f"- Negative count: {bal['negative_count']}",
        f"- Signed sum: {bal['signed_sum']}",
        "",
        "## Orientation Witness",
        f"- Orientation reversal closed on Fano lines: `{payload['orientation_reversal_closed_on_fano_lines']}`",
        f"- Canonical triple count: {payload['orientation_triple_count']}",
        "",
        "## Trace Suite",
        "",
        "| Case | CP-dual relation | Weighted trace delta |",
        "|---|---|---:|",
    ]
    for row in payload["trace_suite"]:
        lines.append(
            f"| {row['case_id']} | {row['cp_dual_relation_holds']} | {row['weighted_trace_delta']} |"
        )

    lines.extend(
        [
            "",
            "## Residual Summary",
            f"- CP-dual all hold: `{res['cp_dual_all_hold']}`",
            f"- Weighted trace all zero: `{res['weighted_trace_all_zero']}`",
            f"- Weak-leakage strong residual zero: `{res['weak_leakage_strong_residual_zero']}`",
            f"- Weak-leakage strong residual value: `{payload['weak_leakage_strong_residual']}`",
            f"- Max abs weighted trace delta: {res['max_abs_weighted_trace_delta']}",
            f"- Fano signed sum zero: `{res['fano_signed_sum_zero']}`",
            f"- `discrete_fano_cp_residual_zero`: `{res['discrete_fano_cp_residual_zero']}`",
            f"- Legacy alias `theta_cp_odd_residual_forced_zero`: `{res['theta_cp_odd_residual_forced_zero']}`",
            "",
            "## Governance Notes",
            "- Witness cases and weights are predeclared constants in this script.",
            "- No output-driven tuning is allowed for claim-grade promotion.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_artifacts(
    payload: Dict[str, Any],
    *,
    json_paths: Sequence[Path] | None = None,
    md_paths: Sequence[Path] | None = None,
) -> None:
    json_out = list(json_paths) if json_paths is not None else [OUT_JSON]
    md_out = list(md_paths) if md_paths is not None else [OUT_MD]

    for path in json_out:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = render_markdown(payload)
    for path in md_out:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(md, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build THETA-001 deterministic CP witness artifacts")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON payload to stdout.",
    )
    parser.add_argument(
        "--write-sources",
        action="store_true",
        help="Write artifacts to sources/theta001_cp_witness.{json,md}.",
    )
    args = parser.parse_args()

    payload = build_witness_payload()

    if args.write_sources:
        write_artifacts(payload)
        print(f"Wrote {_to_repo_path(OUT_JSON)}")
        print(f"Wrote {_to_repo_path(OUT_MD)}")
        return

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return

    print(
        "theta001_cp_witness: "
        f"residual_zero={payload['theta_residual_summary']['discrete_fano_cp_residual_zero']}, "
        f"replay_hash={payload['replay_hash'][:16]}..."
    )


if __name__ == "__main__":
    main()
