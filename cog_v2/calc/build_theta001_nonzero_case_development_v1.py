"""Develop top THETA nonzero-candidate cases into per-tick diagnostics.

This artifact expands the exploratory probe by producing per-tick trace
diagnostics for the highest-magnitude candidate rows under the
`oriented_fano_cubic_cp_odd_v1` observable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from cog_v2.calc.build_theta001_bridge_closure_v2 import CASE_DEFINITIONS
from cog_v2.calc.build_theta001_nonzero_candidate_probe_v1 import (
    SCRIPT_REPO_PATH as PROBE_SCRIPT_REPO_PATH,
    build_payload as build_probe_payload,
    oriented_fano_cubic,
)
from cog_v2.calc import theta001_cp_invariant_v2 as t


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "theta001_nonzero_case_development_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "theta001_nonzero_case_development_v1.md"
SCRIPT_REPO_PATH = "cog_v2/calc/build_theta001_nonzero_case_development_v1.py"
TOP_WEAK = 6
TOP_CKM = 6


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _to_repo_path(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def _iter_cases() -> Dict[str, Tuple[Tuple[int, ...], Tuple[int, ...]]]:
    out: Dict[str, Tuple[Tuple[int, ...], Tuple[int, ...]]] = {}
    for row in CASE_DEFINITIONS:
        out[str(row["case_id"])] = (
            tuple(int(x) for x in row["initial_state"]),
            tuple(int(x) for x in row["op_sequence"]),
        )
    return out


def _strong_action(state: t.State8) -> int:
    return int(t._weighted_action(state, t.STRONG_SECTOR_WEIGHTS))


def _develop_case_trace(
    *,
    lane: str,
    case_id: str,
    initial: t.State8,
    op_sequence: Sequence[int],
    weak_kick: int,
    ckm_phase: int | None = None,
    transport_period: int | None = None,
) -> Dict[str, Any]:
    pert = list(initial)
    pert[7] += int(weak_kick)
    init = tuple(pert)

    if lane == "weak":
        orig_trace = t.run_update_trace(init, op_sequence, t.FANO_SIGN)
        dual_trace = t.run_update_trace(t.cp_map(init), op_sequence, t.flipped_sign_table())
    elif lane == "ckm":
        if ckm_phase is None or transport_period is None:
            raise ValueError("ckm lane requires ckm_phase and transport_period")
        orig_trace = t.run_update_trace_ckm_transport(
            init,
            op_sequence,
            t.FANO_SIGN,
            ckm_phase=int(ckm_phase),
            transport_period=int(transport_period),
        )
        dual_trace = t.run_update_trace_ckm_transport(
            t.cp_map(init),
            op_sequence,
            t.flipped_sign_table(),
            ckm_phase=int(ckm_phase),
            transport_period=int(transport_period),
        )
    else:
        raise ValueError(f"unknown lane {lane}")

    tick_rows: List[Dict[str, Any]] = []
    sq_cum = 0
    cubic_cum = 0
    sq_cum_ex_t0 = 0
    cubic_cum_ex_t0 = 0
    first_cubic_tick: int | None = None
    first_cubic_tick_ex_t0: int | None = None
    peak_abs_cubic = -1
    peak_tick = 0

    for tick, (s1, s2) in enumerate(zip(orig_trace, dual_trace)):
        sq_delta = int(_strong_action(s1) - _strong_action(s2))
        cubic_delta = int(oriented_fano_cubic(s1) - oriented_fano_cubic(s2))
        sq_cum += sq_delta
        cubic_cum += cubic_delta
        if tick >= 1:
            sq_cum_ex_t0 += sq_delta
            cubic_cum_ex_t0 += cubic_delta

        cp_s1 = t.cp_map(s1)
        cp_match = cp_s1 == s2
        cp_neg_match = cp_s1 == tuple(-x for x in s2)
        if cubic_delta != 0 and first_cubic_tick is None:
            first_cubic_tick = int(tick)
        if tick >= 1 and cubic_delta != 0 and first_cubic_tick_ex_t0 is None:
            first_cubic_tick_ex_t0 = int(tick)
        if abs(cubic_delta) > peak_abs_cubic:
            peak_abs_cubic = abs(cubic_delta)
            peak_tick = int(tick)

        tick_rows.append(
            {
                "tick": int(tick),
                "sq_delta": int(sq_delta),
                "sq_cumulative": int(sq_cum),
                "cubic_delta": int(cubic_delta),
                "cubic_cumulative": int(cubic_cum),
                "cp_map_matches_dual": bool(cp_match),
                "cp_map_matches_neg_dual": bool(cp_neg_match),
            }
        )

    return {
        "lane": lane,
        "case_id": case_id,
        "weak_kick": int(weak_kick),
        "ckm_phase": None if ckm_phase is None else int(ckm_phase),
        "transport_period": None if transport_period is None else int(transport_period),
        "op_depth": int(len(op_sequence)),
        "sq_total": int(sq_cum),
        "sq_total_excluding_t0": int(sq_cum_ex_t0),
        "cubic_total": int(cubic_cum),
        "cubic_total_excluding_t0": int(cubic_cum_ex_t0),
        "cubic_nonzero_tick_count": int(sum(1 for r in tick_rows if int(r["cubic_delta"]) != 0)),
        "cubic_nonzero_tick_count_excluding_t0": int(sum(1 for r in tick_rows[1:] if int(r["cubic_delta"]) != 0)),
        "first_nonzero_cubic_tick": None if first_cubic_tick is None else int(first_cubic_tick),
        "first_nonzero_cubic_tick_excluding_t0": None if first_cubic_tick_ex_t0 is None else int(first_cubic_tick_ex_t0),
        "peak_abs_cubic_tick": int(peak_tick),
        "peak_abs_cubic_value": int(peak_abs_cubic),
        "tick_rows": tick_rows,
    }


def build_payload() -> Dict[str, Any]:
    script_path = ROOT / SCRIPT_REPO_PATH
    probe_script_path = ROOT / PROBE_SCRIPT_REPO_PATH
    case_map = _iter_cases()
    probe = build_probe_payload()

    weak_top = probe["weak_leakage_summary"]["top_nonzero_rows"][:TOP_WEAK]
    ckm_top = probe["ckm_like_summary"]["top_nonzero_rows"][:TOP_CKM]

    developed: List[Dict[str, Any]] = []
    for row in weak_top:
        case_id = str(row["case_id"])
        initial, ops = case_map[case_id]
        developed.append(
            _develop_case_trace(
                lane="weak",
                case_id=case_id,
                initial=initial,
                op_sequence=ops,
                weak_kick=int(row["weak_kick"]),
            )
        )
    for row in ckm_top:
        case_id = str(row["case_id"])
        initial, ops = case_map[case_id]
        developed.append(
            _develop_case_trace(
                lane="ckm",
                case_id=case_id,
                initial=initial,
                op_sequence=ops,
                weak_kick=int(row["weak_kick"]),
                ckm_phase=int(row["ckm_phase"]),
                transport_period=int(row["transport_period"]),
            )
        )

    payload: Dict[str, Any] = {
        "schema_version": "theta001_nonzero_case_development_v1",
        "claim_id": "THETA-001",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "probe_script_reference": PROBE_SCRIPT_REPO_PATH,
        "probe_script_reference_sha256": _sha_file(probe_script_path),
        "selection_policy": {
            "weak_top_n": int(TOP_WEAK),
            "ckm_top_n": int(TOP_CKM),
            "ranking_key": "abs(oriented_cubic_residual)",
        },
        "developed_case_count": int(len(developed)),
        "developed_cases": developed,
        "aggregate": {
            "all_sq_totals_zero": all(int(c["sq_total"]) == 0 for c in developed),
            "all_cubic_totals_nonzero": all(int(c["cubic_total"]) != 0 for c in developed),
            "cases_with_nonzero_cubic_total_excluding_t0": int(
                sum(1 for c in developed if int(c["cubic_total_excluding_t0"]) != 0)
            ),
            "weak_cases_with_nonzero_cubic_total_excluding_t0": int(
                sum(1 for c in developed if c["lane"] == "weak" and int(c["cubic_total_excluding_t0"]) != 0)
            ),
            "ckm_cases_with_nonzero_cubic_total_excluding_t0": int(
                sum(1 for c in developed if c["lane"] == "ckm" and int(c["cubic_total_excluding_t0"]) != 0)
            ),
            "max_abs_cubic_total": int(max(abs(int(c["cubic_total"])) for c in developed)),
            "max_abs_cubic_case": max(developed, key=lambda c: abs(int(c["cubic_total"])))["case_id"],
            "max_abs_cubic_lane": max(developed, key=lambda c: abs(int(c["cubic_total"])))["lane"],
        },
        "limits": [
            "Exploratory diagnostic artifact for case development.",
            "Does not alter THETA-001 supported_bridge status.",
            "Promotion impact requires preregistered observable migration and skeptic review.",
        ],
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def render_markdown(payload: Dict[str, Any]) -> str:
    lines = [
        "# THETA-001 Nonzero Candidate Case Development (v1)",
        "",
        f"- Claim: `{payload['claim_id']}`",
        f"- Replay hash: `{payload['replay_hash']}`",
        f"- Developed cases: `{payload['developed_case_count']}`",
        "",
        "## Aggregate",
        f"- all_sq_totals_zero: `{payload['aggregate']['all_sq_totals_zero']}`",
        f"- all_cubic_totals_nonzero: `{payload['aggregate']['all_cubic_totals_nonzero']}`",
        f"- cases_with_nonzero_cubic_total_excluding_t0: `{payload['aggregate']['cases_with_nonzero_cubic_total_excluding_t0']}`",
        f"- weak_cases_with_nonzero_cubic_total_excluding_t0: `{payload['aggregate']['weak_cases_with_nonzero_cubic_total_excluding_t0']}`",
        f"- ckm_cases_with_nonzero_cubic_total_excluding_t0: `{payload['aggregate']['ckm_cases_with_nonzero_cubic_total_excluding_t0']}`",
        f"- max_abs_cubic_total: `{payload['aggregate']['max_abs_cubic_total']}`",
        f"- max_abs_cubic_case: `{payload['aggregate']['max_abs_cubic_case']}`",
        f"- max_abs_cubic_lane: `{payload['aggregate']['max_abs_cubic_lane']}`",
        "",
        "## Developed Cases (summary)",
        "",
        "| lane | case_id | weak_kick | ckm_phase | period | sq_total | cubic_total | cubic_total_ex_t0 | first_nonzero_tick | first_nonzero_tick_ex_t0 | peak_tick | peak_abs_cubic |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for c in payload["developed_cases"]:
        lines.append(
            f"| {c['lane']} | {c['case_id']} | {c['weak_kick']} | "
            f"{'' if c['ckm_phase'] is None else c['ckm_phase']} | "
            f"{'' if c['transport_period'] is None else c['transport_period']} | "
            f"{c['sq_total']} | {c['cubic_total']} | "
            f"{c['cubic_total_excluding_t0']} | "
            f"{'' if c['first_nonzero_cubic_tick'] is None else c['first_nonzero_cubic_tick']} | "
            f"{'' if c['first_nonzero_cubic_tick_excluding_t0'] is None else c['first_nonzero_cubic_tick_excluding_t0']} | "
            f"{c['peak_abs_cubic_tick']} | {c['peak_abs_cubic_value']} |"
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
    parser = argparse.ArgumentParser(description="Build THETA nonzero-candidate case development artifact")
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
        "theta001_nonzero_case_development_v1: "
        f"all_sq_totals_zero={payload['aggregate']['all_sq_totals_zero']}, "
        f"all_cubic_totals_nonzero={payload['aggregate']['all_cubic_totals_nonzero']}, "
        f"replay_hash={payload['replay_hash'][:16]}..."
    )


if __name__ == "__main__":
    main()
