"""Probe for nonzero-theta candidate under an alternative CP-odd observable.

This does NOT modify THETA-001 claim semantics. It is an exploratory diagnostic:
1) evaluate the current squared strong residual (expected zero in supported_bridge lane),
2) evaluate an oriented Fano-cubic CP-odd residual candidate (sign-sensitive),
3) report concrete parameter cases where the alternative residual is nonzero.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from cog_v2.calc.build_theta001_bridge_closure_v2 import (
    CASE_DEFINITIONS,
    CKM_PHASES,
    CKM_TRANSPORT_PERIODS,
    SCRIPT_REPO_PATH as BRIDGE_SCRIPT_REPO_PATH,
    WEAK_KICKS,
)
from cog_v2.calc import theta001_cp_invariant_v2 as t


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "theta001_nonzero_candidate_probe_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "theta001_nonzero_candidate_probe_v1.md"
SCRIPT_REPO_PATH = "cog_v2/calc/build_theta001_nonzero_candidate_probe_v1.py"


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _to_repo_path(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def _iter_cases() -> List[Tuple[str, Tuple[int, ...], Tuple[int, ...]]]:
    rows: List[Tuple[str, Tuple[int, ...], Tuple[int, ...]]] = []
    for row in CASE_DEFINITIONS:
        rows.append(
            (
                str(row["case_id"]),
                tuple(int(x) for x in row["initial_state"]),
                tuple(int(x) for x in row["op_sequence"]),
            )
        )
    return rows


def oriented_fano_cubic(state: t.State8) -> int:
    """Sign-sensitive combinatoric CP-odd candidate observable.

    Uses oriented Fano triplets over imaginary channels (1..7):
      Q(state) = sum_{(a,b,c) in FANO_CYCLES} state[a+1] * state[b+1] * state[c+1]
    """
    total = 0
    for a, b, c in t.FANO_CYCLES:
        ia, ib, ic = a + 1, b + 1, c + 1
        total += int(state[ia]) * int(state[ib]) * int(state[ic])
    return int(total)


def oriented_cubic_trace_delta(initial: t.State8, op_sequence: Sequence[int]) -> int:
    orig_trace = t.run_update_trace(initial, op_sequence, t.FANO_SIGN)
    dual_trace = t.run_update_trace(t.cp_map(initial), op_sequence, t.flipped_sign_table())
    delta = 0
    for s1, s2 in zip(orig_trace, dual_trace):
        delta += oriented_fano_cubic(s1) - oriented_fano_cubic(s2)
    return int(delta)


def oriented_cubic_trace_delta_ckm(
    initial: t.State8,
    op_sequence: Sequence[int],
    *,
    ckm_phase: int,
    transport_period: int,
) -> int:
    orig_trace = t.run_update_trace_ckm_transport(
        initial,
        op_sequence,
        t.FANO_SIGN,
        ckm_phase=int(ckm_phase),
        transport_period=int(transport_period),
    )
    dual_trace = t.run_update_trace_ckm_transport(
        t.cp_map(initial),
        op_sequence,
        t.flipped_sign_table(),
        ckm_phase=int(ckm_phase),
        transport_period=int(transport_period),
    )
    delta = 0
    for s1, s2 in zip(orig_trace, dual_trace):
        delta += oriented_fano_cubic(s1) - oriented_fano_cubic(s2)
    return int(delta)


def build_payload() -> Dict[str, Any]:
    script_path = ROOT / SCRIPT_REPO_PATH
    bridge_script_path = ROOT / BRIDGE_SCRIPT_REPO_PATH
    cases = _iter_cases()

    baseline_rows: List[Dict[str, Any]] = []
    weak_rows: List[Dict[str, Any]] = []
    ckm_rows: List[Dict[str, Any]] = []

    for case_id, initial, ops in cases:
        sq_delta = t.cp_weighted_trace_delta(initial, ops, t.STRONG_SECTOR_WEIGHTS)
        cubic_delta = oriented_cubic_trace_delta(initial, ops)
        baseline_rows.append(
            {
                "case_id": case_id,
                "squared_strong_residual": int(sq_delta),
                "oriented_cubic_residual": int(cubic_delta),
            }
        )

        for weak_kick in WEAK_KICKS:
            perturbed = list(initial)
            perturbed[7] += int(weak_kick)
            pert = tuple(perturbed)

            sq_res = t.cp_weighted_trace_delta(pert, ops, t.STRONG_SECTOR_WEIGHTS)
            cubic_res = oriented_cubic_trace_delta(pert, ops)
            weak_rows.append(
                {
                    "case_id": case_id,
                    "weak_kick": int(weak_kick),
                    "squared_strong_residual": int(sq_res),
                    "oriented_cubic_residual": int(cubic_res),
                }
            )

            for ckm_phase in CKM_PHASES:
                for transport_period in CKM_TRANSPORT_PERIODS:
                    sq_ckm = t.weak_leakage_ckm_like_strong_residual(
                        initial,
                        ops,
                        weak_kick=int(weak_kick),
                        ckm_phase=int(ckm_phase),
                        transport_period=int(transport_period),
                    )
                    cubic_ckm = oriented_cubic_trace_delta_ckm(
                        pert,
                        ops,
                        ckm_phase=int(ckm_phase),
                        transport_period=int(transport_period),
                    )
                    ckm_rows.append(
                        {
                            "case_id": case_id,
                            "weak_kick": int(weak_kick),
                            "ckm_phase": int(ckm_phase),
                            "transport_period": int(transport_period),
                            "squared_strong_residual": int(sq_ckm),
                            "oriented_cubic_residual": int(cubic_ckm),
                        }
                    )

    weak_nonzero = [r for r in weak_rows if int(r["oriented_cubic_residual"]) != 0]
    ckm_nonzero = [r for r in ckm_rows if int(r["oriented_cubic_residual"]) != 0]
    weak_top = sorted(weak_nonzero, key=lambda r: abs(int(r["oriented_cubic_residual"])), reverse=True)[:12]
    ckm_top = sorted(ckm_nonzero, key=lambda r: abs(int(r["oriented_cubic_residual"])), reverse=True)[:12]

    payload: Dict[str, Any] = {
        "schema_version": "theta001_nonzero_candidate_probe_v1",
        "claim_id": "THETA-001",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "bridge_script_reference": BRIDGE_SCRIPT_REPO_PATH,
        "bridge_script_reference_sha256": _sha_file(bridge_script_path),
        "note": (
            "Exploratory only: compares current squared residual lane to a sign-sensitive "
            "oriented Fano-cubic candidate residual."
        ),
        "baseline_rows": baseline_rows,
        "weak_leakage_summary": {
            "rows": int(len(weak_rows)),
            "squared_all_zero": all(int(r["squared_strong_residual"]) == 0 for r in weak_rows),
            "oriented_cubic_nonzero_count": int(len(weak_nonzero)),
            "oriented_cubic_max_abs": int(max(abs(int(r["oriented_cubic_residual"])) for r in weak_rows)),
            "top_nonzero_rows": weak_top,
        },
        "ckm_like_summary": {
            "rows": int(len(ckm_rows)),
            "squared_all_zero": all(int(r["squared_strong_residual"]) == 0 for r in ckm_rows),
            "oriented_cubic_nonzero_count": int(len(ckm_nonzero)),
            "oriented_cubic_max_abs": int(max(abs(int(r["oriented_cubic_residual"])) for r in ckm_rows)),
            "top_nonzero_rows": ckm_top,
        },
        "falsification_candidate": {
            "candidate_observable_id": "oriented_fano_cubic_cp_odd_v1",
            "rationale": "sign-sensitive CP-odd combinatoric observable over oriented Fano triplets",
            "has_nonzero_cases": bool(len(weak_nonzero) > 0 or len(ckm_nonzero) > 0),
        },
        "limits": [
            "This artifact does not change THETA-001 contract status.",
            "A nonzero candidate here means the observable definition is sensitive to CP-odd sign structure.",
            "Promotion impact requires preregistration and independent skeptical review.",
        ],
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def render_markdown(payload: Dict[str, Any]) -> str:
    lines = [
        "# THETA-001 Nonzero Candidate Probe (v1)",
        "",
        f"- Claim: `{payload['claim_id']}`",
        f"- Replay hash: `{payload['replay_hash']}`",
        f"- Source script: `{payload['source_script']}`",
        "",
        "## Summary",
        f"- Weak rows: {payload['weak_leakage_summary']['rows']}",
        f"- Weak squared residual all zero: `{payload['weak_leakage_summary']['squared_all_zero']}`",
        f"- Weak oriented-cubic nonzero count: `{payload['weak_leakage_summary']['oriented_cubic_nonzero_count']}`",
        f"- Weak oriented-cubic max abs: `{payload['weak_leakage_summary']['oriented_cubic_max_abs']}`",
        "",
        f"- CKM-like rows: {payload['ckm_like_summary']['rows']}",
        f"- CKM-like squared residual all zero: `{payload['ckm_like_summary']['squared_all_zero']}`",
        f"- CKM-like oriented-cubic nonzero count: `{payload['ckm_like_summary']['oriented_cubic_nonzero_count']}`",
        f"- CKM-like oriented-cubic max abs: `{payload['ckm_like_summary']['oriented_cubic_max_abs']}`",
        "",
        "## Candidate Conclusion",
        f"- Observable: `{payload['falsification_candidate']['candidate_observable_id']}`",
        f"- has_nonzero_cases: `{payload['falsification_candidate']['has_nonzero_cases']}`",
        "",
        "## Top Weak Nonzero Rows",
    ]
    for row in payload["weak_leakage_summary"]["top_nonzero_rows"]:
        lines.append(
            "- "
            f"case={row['case_id']}, weak_kick={row['weak_kick']}, "
            f"oriented_cubic_residual={row['oriented_cubic_residual']}, "
            f"squared_strong_residual={row['squared_strong_residual']}"
        )
    lines.extend(["", "## Top CKM-like Nonzero Rows"])
    for row in payload["ckm_like_summary"]["top_nonzero_rows"]:
        lines.append(
            "- "
            f"case={row['case_id']}, weak_kick={row['weak_kick']}, ckm_phase={row['ckm_phase']}, "
            f"period={row['transport_period']}, oriented_cubic_residual={row['oriented_cubic_residual']}, "
            f"squared_strong_residual={row['squared_strong_residual']}"
        )
    lines.extend(["", "## Limits"])
    for lim in payload["limits"]:
        lines.append(f"- {lim}")
    return "\n".join(lines) + "\n"


def write_artifacts(
    payload: Dict[str, Any],
    *,
    json_paths: Sequence[Path] | None = None,
    md_paths: Sequence[Path] | None = None,
) -> None:
    j_paths = list(json_paths) if json_paths is not None else [OUT_JSON]
    m_paths = list(md_paths) if md_paths is not None else [OUT_MD]
    for path in j_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = render_markdown(payload)
    for path in m_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(md, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build THETA-001 nonzero candidate probe artifact")
    parser.add_argument("--json", action="store_true", help="Print JSON payload")
    parser.add_argument("--write-sources", action="store_true", help="Write artifacts to cog_v2/sources")
    args = parser.parse_args()

    payload = build_payload()
    if args.write_sources:
        write_artifacts(payload)
        print(f"Wrote {_to_repo_path(OUT_JSON)}")
        print(f"Wrote {_to_repo_path(OUT_MD)}")
        return
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(
        "theta001_nonzero_candidate_probe_v1: "
        f"has_nonzero_cases={payload['falsification_candidate']['has_nonzero_cases']}, "
        f"replay_hash={payload['replay_hash'][:16]}..."
    )


if __name__ == "__main__":
    main()
