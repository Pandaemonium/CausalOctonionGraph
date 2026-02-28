"""Build exact microstate/event predictions for THETA-002 nonzero domains.

This artifact publishes deterministic, tick-by-tick microstate traces for one
representative case in each nonzero domain:
1) weak positive residual,
2) weak negative residual,
3) ckm positive residual,
4) ckm negative residual.

Each trace includes exact 8-channel state vectors for orig/dual worlds at every
tick, with sign-sensitive oriented-cubic diagnostics.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, Tuple

from cog_v2.calc import theta001_cp_invariant_v2 as t
from cog_v2.calc.build_theta001_nonzero_candidate_probe_v1 import oriented_fano_cubic
from cog_v2.calc.build_theta001_nonzero_robust_casebook_v1 import (
    SCRIPT_REPO_PATH as CASEBOOK_SCRIPT_REPO_PATH,
    build_payload as build_casebook_payload,
)
from cog_v2.calc.build_theta001_nonzero_search_v1 import (
    SCRIPT_REPO_PATH as SEARCH_SCRIPT_REPO_PATH,
    build_payload as build_search_payload,
)


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "theta002_exact_microstate_domains_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "theta002_exact_microstate_domains_v1.md"
SCRIPT_REPO_PATH = "cog_v2/calc/build_theta002_exact_microstate_domains_v1.py"

BASIS_LABELS: Tuple[str, ...] = (
    "e000",
    "e001",
    "e010",
    "e011",
    "e100",
    "e101",
    "e110",
    "e111",
)

# Deterministic domain anchors selected from theta001_nonzero_search_v1 top rows.
DOMAIN_SPECS: Tuple[Tuple[str, str, int], ...] = (
    ("weak_positive", "weak", 166),
    ("weak_negative", "weak", 298),
    ("ckm_positive", "ckm", 340),
    ("ckm_negative", "ckm", 206),
)


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _to_repo_path(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def _strong_action(state: t.State8) -> int:
    return int(t._weighted_action(state, t.STRONG_SECTOR_WEIGHTS))


def _trace_delta_oriented_cubic(
    orig_trace: Sequence[t.State8], dual_trace: Sequence[t.State8], *, exclude_t0: bool
) -> int:
    offset = 1 if exclude_t0 else 0
    return int(
        sum(
            oriented_fano_cubic(s1) - oriented_fano_cubic(s2)
            for s1, s2 in zip(orig_trace[offset:], dual_trace[offset:])
        )
    )


def _to_state_dict(state: Sequence[int]) -> Dict[str, int]:
    return {label: int(state[idx]) for idx, label in enumerate(BASIS_LABELS)}


def _eventual_period(seq: Sequence[Tuple[int, ...]]) -> Dict[str, int | None]:
    n = len(seq)
    if n <= 1:
        return {"preperiod": 0, "period": None}
    for pre in range(n - 1):
        max_p = n - pre - 1
        for p in range(1, max_p + 1):
            ok = True
            for i in range(pre + p, n):
                if seq[i] != seq[i - p]:
                    ok = False
                    break
            if ok:
                return {"preperiod": int(pre), "period": int(p)}
    return {"preperiod": None, "period": None}


def _first_return_tick(trace: Sequence[Tuple[int, ...]]) -> int | None:
    if not trace:
        return None
    s0 = trace[0]
    for i in range(1, len(trace)):
        if trace[i] == s0:
            return int(i)
    return None


def _domain_sign_ok(domain_id: str, value: int) -> bool:
    if domain_id.endswith("_positive"):
        return int(value) > 0
    if domain_id.endswith("_negative"):
        return int(value) < 0
    raise ValueError(f"unknown domain sign policy for {domain_id}")


def _find_anchor_row(
    domain_lane: str,
    sample_id: int,
    *,
    weak_rows: Sequence[Mapping[str, Any]],
    ckm_rows: Sequence[Mapping[str, Any]],
) -> Mapping[str, Any]:
    rows = weak_rows if domain_lane == "weak" else ckm_rows
    for row in rows:
        if int(row["sample_id"]) == int(sample_id):
            return row
    raise ValueError(f"sample_id {sample_id} not found in lane {domain_lane}")


def _robust_metrics(casebook: Mapping[str, Any], *, lane: str, sample_id: int) -> Dict[str, Any] | None:
    for row in casebook.get("developed_candidates", []):
        if str(row.get("lane")) == lane and int(row.get("sample_id")) == int(sample_id):
            return {
                "robust_nonzero_candidate": bool(row.get("robust_nonzero_candidate")),
                "nonzero_rate_excluding_t0": float(row.get("nonzero_rate_excluding_t0", 0.0)),
                "sign_stability_rate": float(row.get("sign_stability_rate", 0.0)),
                "squared_zero_rate": float(row.get("squared_zero_rate", 0.0)),
            }
    return None


def _build_domain_scenario(
    *,
    domain_id: str,
    lane: str,
    anchor_row: Mapping[str, Any],
    robust_metrics: Dict[str, Any] | None,
) -> Dict[str, Any]:
    init = list(int(x) for x in anchor_row["initial_state"])
    weak_kick = int(anchor_row["weak_kick"])
    init[7] += weak_kick
    init_t: t.State8 = tuple(init)  # type: ignore[assignment]

    ops = tuple(int(x) for x in anchor_row["op_sequence"])
    ckm_phase = int(anchor_row["ckm_phase"])
    transport_period = int(anchor_row["transport_period"])

    if lane == "weak":
        orig_trace = t.run_update_trace(init_t, ops, t.FANO_SIGN)
        dual_trace = t.run_update_trace(t.cp_map(init_t), ops, t.flipped_sign_table())
    elif lane == "ckm":
        orig_trace = t.run_update_trace_ckm_transport(
            init_t,
            ops,
            t.FANO_SIGN,
            ckm_phase=ckm_phase,
            transport_period=transport_period,
        )
        dual_trace = t.run_update_trace_ckm_transport(
            t.cp_map(init_t),
            ops,
            t.flipped_sign_table(),
            ckm_phase=ckm_phase,
            transport_period=transport_period,
        )
    else:
        raise ValueError(f"unknown lane {lane}")

    tick_rows: List[Dict[str, Any]] = []
    sq_cum = 0
    cubic_cum = 0
    cubic_cum_ex_t0 = 0
    for tick, (s1, s2) in enumerate(zip(orig_trace, dual_trace)):
        sq_delta = int(_strong_action(s1) - _strong_action(s2))
        cubic_delta = int(oriented_fano_cubic(s1) - oriented_fano_cubic(s2))
        sq_cum += sq_delta
        cubic_cum += cubic_delta
        if tick >= 1:
            cubic_cum_ex_t0 += cubic_delta

        cp_s1 = t.cp_map(s1)
        tick_rows.append(
            {
                "tick": int(tick),
                "op_applied": None if tick == 0 else int(ops[tick - 1]),
                "ckm_transport_applied": bool(
                    lane == "ckm" and tick >= 1 and (tick % int(transport_period) == 0)
                ),
                "orig_state_vector": [int(x) for x in s1],
                "orig_state": _to_state_dict(s1),
                "dual_state_vector": [int(x) for x in s2],
                "dual_state": _to_state_dict(s2),
                "sq_delta": int(sq_delta),
                "sq_cumulative": int(sq_cum),
                "oriented_cubic_delta": int(cubic_delta),
                "oriented_cubic_cumulative": int(cubic_cum),
                "oriented_cubic_cumulative_excluding_t0": int(cubic_cum_ex_t0),
                "cp_map_matches_dual": bool(cp_s1 == s2),
                "cp_map_matches_neg_dual": bool(cp_s1 == tuple(-x for x in s2)),
            }
        )

    oriented_total_ex_t0 = int(_trace_delta_oriented_cubic(orig_trace, dual_trace, exclude_t0=True))
    if not _domain_sign_ok(domain_id, oriented_total_ex_t0):
        raise ValueError(
            f"domain/sign mismatch for {domain_id}: oriented_cubic_total_ex_t0={oriented_total_ex_t0}"
        )

    orig_tuple_trace = [tuple(int(x) for x in s) for s in orig_trace]
    dual_tuple_trace = [tuple(int(x) for x in s) for s in dual_trace]
    cubic_delta_trace = [int(r["oriented_cubic_delta"]) for r in tick_rows]

    return {
        "domain_id": domain_id,
        "lane": lane,
        "sample_id": int(anchor_row["sample_id"]),
        "input": {
            "initial_state_unperturbed": [int(x) for x in anchor_row["initial_state"]],
            "initial_state_with_weak_kick": [int(x) for x in init_t],
            "weak_kick": int(weak_kick),
            "op_sequence": [int(x) for x in ops],
            "ckm_phase": int(ckm_phase),
            "transport_period": int(transport_period),
        },
        "expected_totals": {
            "squared_residual_total": int(sq_cum),
            "oriented_cubic_residual_total": int(cubic_cum),
            "oriented_cubic_residual_total_excluding_t0": int(oriented_total_ex_t0),
            "oriented_cubic_sign": "positive" if int(oriented_total_ex_t0) > 0 else "negative",
        },
        "cycle_diagnostics": {
            "orig_first_return_tick": _first_return_tick(orig_tuple_trace),
            "dual_first_return_tick": _first_return_tick(dual_tuple_trace),
            "orig_eventual_period": _eventual_period(orig_tuple_trace),
            "dual_eventual_period": _eventual_period(dual_tuple_trace),
            "cubic_delta_eventual_period": _eventual_period([tuple([x]) for x in cubic_delta_trace]),
        },
        "robust_casebook_metrics": robust_metrics,
        "tick_rows": tick_rows,
    }


def build_payload() -> Dict[str, Any]:
    script_path = ROOT / SCRIPT_REPO_PATH
    search_script_path = ROOT / SEARCH_SCRIPT_REPO_PATH
    casebook_script_path = ROOT / CASEBOOK_SCRIPT_REPO_PATH

    search = build_search_payload()
    casebook = build_casebook_payload()
    weak_rows = list(search["top_weak_nonzero_excluding_t0"])
    ckm_rows = list(search["top_ckm_nonzero_excluding_t0"])

    scenarios: List[Dict[str, Any]] = []
    for domain_id, lane, sample_id in DOMAIN_SPECS:
        anchor_row = _find_anchor_row(
            lane,
            sample_id,
            weak_rows=weak_rows,
            ckm_rows=ckm_rows,
        )
        scenario = _build_domain_scenario(
            domain_id=domain_id,
            lane=lane,
            anchor_row=anchor_row,
            robust_metrics=_robust_metrics(casebook, lane=lane, sample_id=sample_id),
        )
        scenarios.append(scenario)

    summary = {
        "scenario_count": int(len(scenarios)),
        "all_squared_totals_zero": bool(
            all(int(s["expected_totals"]["squared_residual_total"]) == 0 for s in scenarios)
        ),
        "domain_signs_satisfied": bool(
            all(_domain_sign_ok(str(s["domain_id"]), int(s["expected_totals"]["oriented_cubic_residual_total_excluding_t0"])) for s in scenarios)
        ),
        "max_abs_oriented_cubic_total_excluding_t0": int(
            max(abs(int(s["expected_totals"]["oriented_cubic_residual_total_excluding_t0"])) for s in scenarios)
        ),
    }

    payload: Dict[str, Any] = {
        "schema_version": "theta002_exact_microstate_domains_v1",
        "claim_id": "THETA-002",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "search_script_reference": SEARCH_SCRIPT_REPO_PATH,
        "search_script_reference_sha256": _sha_file(search_script_path),
        "casebook_script_reference": CASEBOOK_SCRIPT_REPO_PATH,
        "casebook_script_reference_sha256": _sha_file(casebook_script_path),
        "basis_labels": list(BASIS_LABELS),
        "selection_policy": {
            "domain_specs": [
                {"domain_id": d, "lane": lane, "sample_id": int(sid)} for d, lane, sid in DOMAIN_SPECS
            ],
            "interpretation": "one representative exact microstate trace per nonzero domain",
        },
        "summary": summary,
        "scenarios": scenarios,
        "limits": [
            "This is an exact finite-trace prediction artifact, not an exhaustive global combinatoric proof.",
            "Anchor cases are deterministic selections from preregistered THETA-002 search outputs.",
            "Lane remains exploratory and does not supersede THETA-001 supported_bridge status.",
        ],
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def render_markdown(payload: Dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        "# THETA-002 Exact Microstate Domains (v1)",
        "",
        f"- Claim: `{payload['claim_id']}`",
        f"- Replay hash: `{payload['replay_hash']}`",
        f"- Scenario count: `{s['scenario_count']}`",
        f"- all_squared_totals_zero: `{s['all_squared_totals_zero']}`",
        f"- domain_signs_satisfied: `{s['domain_signs_satisfied']}`",
        f"- max_abs_oriented_cubic_total_excluding_t0: `{s['max_abs_oriented_cubic_total_excluding_t0']}`",
        "",
        "## Domain Scenarios",
        "",
        "| domain | lane | sample_id | sq_total | cubic_total_ex_t0 | sign | robust_anchor |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    for sc in payload["scenarios"]:
        robust = sc.get("robust_casebook_metrics")
        robust_flag = "" if robust is None else str(bool(robust["robust_nonzero_candidate"]))
        lines.append(
            f"| {sc['domain_id']} | {sc['lane']} | {sc['sample_id']} | "
            f"{sc['expected_totals']['squared_residual_total']} | "
            f"{sc['expected_totals']['oriented_cubic_residual_total_excluding_t0']} | "
            f"{sc['expected_totals']['oriented_cubic_sign']} | {robust_flag} |"
        )

    for sc in payload["scenarios"]:
        lines.extend(
            [
                "",
                f"## {sc['domain_id']}",
                f"- lane: `{sc['lane']}`",
                f"- sample_id: `{sc['sample_id']}`",
                f"- weak_kick: `{sc['input']['weak_kick']}`",
                f"- ckm_phase: `{sc['input']['ckm_phase']}`",
                f"- transport_period: `{sc['input']['transport_period']}`",
                f"- sq_total: `{sc['expected_totals']['squared_residual_total']}`",
                f"- cubic_total_ex_t0: `{sc['expected_totals']['oriented_cubic_residual_total_excluding_t0']}`",
                f"- orig_eventual_period: `{sc['cycle_diagnostics']['orig_eventual_period']}`",
                f"- dual_eventual_period: `{sc['cycle_diagnostics']['dual_eventual_period']}`",
                "",
                "| tick | op | ckm_transport | sq_delta | cubic_delta | orig_state_vector | dual_state_vector |",
                "|---:|---:|---|---:|---:|---|---|",
            ]
        )
        for row in sc["tick_rows"]:
            op = "" if row["op_applied"] is None else str(int(row["op_applied"]))
            lines.append(
                f"| {row['tick']} | {op} | {row['ckm_transport_applied']} | {row['sq_delta']} | "
                f"{row['oriented_cubic_delta']} | {row['orig_state_vector']} | {row['dual_state_vector']} |"
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
    parser = argparse.ArgumentParser(description="Build THETA-002 exact microstate domain traces")
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
        "theta002_exact_microstate_domains_v1: "
        f"scenarios={payload['summary']['scenario_count']}, "
        f"replay_hash={payload['replay_hash'][:16]}..."
    )


if __name__ == "__main__":
    main()

