"""Robustness casebook for THETA-002 nonzero candidates.

Takes top candidates from theta001_nonzero_search_v1 and evaluates local
neighborhood stability:
1) perturb initial state coefficients by +-1,
2) perturb weak kick by {-2, 0, +2},
3) rotate op sequence by small offsets.

Primary score is nonzero rate of oriented-cubic residual excluding t0, with
control requirement that squared residual remains zero.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from cog_v2.calc import theta001_cp_invariant_v2 as t
from cog_v2.calc.build_theta001_nonzero_candidate_probe_v1 import oriented_fano_cubic
from cog_v2.calc.build_theta001_nonzero_search_v1 import (
    SCRIPT_REPO_PATH as SEARCH_SCRIPT_REPO_PATH,
    build_payload as build_search_payload,
)


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "theta001_nonzero_robust_casebook_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "theta001_nonzero_robust_casebook_v1.md"
SCRIPT_REPO_PATH = "cog_v2/calc/build_theta001_nonzero_robust_casebook_v1.py"

TOP_WEAK = 12
TOP_CKM = 12
KICK_DELTAS = (-2, 0, 2)
ROTATION_SHIFTS = (0, 1, 2, 3, 4)
ROBUST_NONZERO_RATE_THRESHOLD = 0.90
ROBUST_SIGN_STABILITY_THRESHOLD = 0.80


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _to_repo_path(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


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


def _rotate_ops(ops: Sequence[int], shift: int) -> Tuple[int, ...]:
    n = len(ops)
    if n == 0:
        return tuple()
    k = int(shift) % n
    if k == 0:
        return tuple(int(x) for x in ops)
    return tuple(int(x) for x in ops[k:]) + tuple(int(x) for x in ops[:k])


def _neighbors(initial_state: Sequence[int]) -> List[Tuple[str, Tuple[int, ...]]]:
    base = tuple(int(x) for x in initial_state)
    out: List[Tuple[str, Tuple[int, ...]]] = [("base", base)]
    for idx in range(8):
        for delta in (-1, 1):
            vals = list(base)
            vals[idx] += int(delta)
            out.append((f"state_ch{idx}_{'p1' if delta > 0 else 'm1'}", tuple(vals)))
    return out


def _score_sign_stability(values: Sequence[int]) -> float:
    nz = [int(v) for v in values if int(v) != 0]
    if not nz:
        return 0.0
    pos = sum(1 for v in nz if v > 0)
    neg = sum(1 for v in nz if v < 0)
    return float(max(pos, neg) / len(nz))


def _develop_anchor(anchor: Dict[str, Any], *, lane: str) -> Dict[str, Any]:
    init0 = tuple(int(x) for x in anchor["initial_state"])
    weak_kick0 = int(anchor["weak_kick"])
    ops0 = tuple(int(x) for x in anchor["op_sequence"])
    ckm_phase = int(anchor["ckm_phase"])
    transport_period = int(anchor["transport_period"])

    rows: List[Dict[str, Any]] = []
    values_ex_t0: List[int] = []
    sq_values: List[int] = []
    for n_label, n_state in _neighbors(init0):
        for dk in KICK_DELTAS:
            wk = int(weak_kick0 + dk)
            state_k = list(n_state)
            state_k[7] += wk
            init = tuple(state_k)
            for sh in ROTATION_SHIFTS:
                ops = _rotate_ops(ops0, int(sh))
                if lane == "weak":
                    orig = t.run_update_trace(init, ops, t.FANO_SIGN)
                    dual = t.run_update_trace(t.cp_map(init), ops, t.flipped_sign_table())
                    sq = int(t.cp_weighted_trace_delta(init, ops, t.STRONG_SECTOR_WEIGHTS))
                elif lane == "ckm":
                    orig = t.run_update_trace_ckm_transport(
                        init,
                        ops,
                        t.FANO_SIGN,
                        ckm_phase=ckm_phase,
                        transport_period=transport_period,
                    )
                    dual = t.run_update_trace_ckm_transport(
                        t.cp_map(init),
                        ops,
                        t.flipped_sign_table(),
                        ckm_phase=ckm_phase,
                        transport_period=transport_period,
                    )
                    sq = int(
                        t.weak_leakage_ckm_like_strong_residual(
                            tuple(int(x) for x in init),
                            ops,
                            weak_kick=0,
                            ckm_phase=ckm_phase,
                            transport_period=transport_period,
                        )
                    )
                else:
                    raise ValueError(f"unknown lane {lane}")

                cubic_ex_t0 = _trace_delta_oriented_cubic(orig, dual, exclude_t0=True)
                values_ex_t0.append(int(cubic_ex_t0))
                sq_values.append(int(sq))
                rows.append(
                    {
                        "neighbor": n_label,
                        "kick_delta": int(dk),
                        "rotation_shift": int(sh),
                        "squared_residual": int(sq),
                        "oriented_cubic_residual_excluding_t0": int(cubic_ex_t0),
                    }
                )

    tested = len(rows)
    nonzero = [int(v) for v in values_ex_t0 if int(v) != 0]
    nonzero_rate = float(len(nonzero) / tested) if tested else 0.0
    sq_zero_rate = float(sum(1 for v in sq_values if int(v) == 0) / tested) if tested else 0.0
    sign_stability = _score_sign_stability(values_ex_t0)
    robust = (
        nonzero_rate >= ROBUST_NONZERO_RATE_THRESHOLD
        and sq_zero_rate == 1.0
        and sign_stability >= ROBUST_SIGN_STABILITY_THRESHOLD
    )

    return {
        "lane": lane,
        "sample_id": int(anchor["sample_id"]),
        "weak_kick": int(weak_kick0),
        "ckm_phase": int(ckm_phase),
        "transport_period": int(transport_period),
        "tested_rows": int(tested),
        "nonzero_count_excluding_t0": int(len(nonzero)),
        "nonzero_rate_excluding_t0": float(nonzero_rate),
        "squared_zero_rate": float(sq_zero_rate),
        "sign_stability_rate": float(sign_stability),
        "max_abs_excluding_t0": int(max((abs(v) for v in values_ex_t0), default=0)),
        "min_abs_nonzero_excluding_t0": int(min((abs(v) for v in nonzero), default=0)),
        "robust_nonzero_candidate": bool(robust),
        "rows": rows,
    }


def build_payload() -> Dict[str, Any]:
    script_path = ROOT / SCRIPT_REPO_PATH
    search_script_path = ROOT / SEARCH_SCRIPT_REPO_PATH
    search = build_search_payload()
    weak_anchors = search["top_weak_nonzero_excluding_t0"][:TOP_WEAK]
    ckm_anchors = search["top_ckm_nonzero_excluding_t0"][:TOP_CKM]

    developed: List[Dict[str, Any]] = []
    for anchor in weak_anchors:
        developed.append(_develop_anchor(anchor, lane="weak"))
    for anchor in ckm_anchors:
        developed.append(_develop_anchor(anchor, lane="ckm"))

    robust_weak = [d for d in developed if d["lane"] == "weak" and bool(d["robust_nonzero_candidate"])]
    robust_ckm = [d for d in developed if d["lane"] == "ckm" and bool(d["robust_nonzero_candidate"])]

    payload: Dict[str, Any] = {
        "schema_version": "theta001_nonzero_robust_casebook_v1",
        "claim_id": "THETA-002",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "search_script_reference": SEARCH_SCRIPT_REPO_PATH,
        "search_script_reference_sha256": _sha_file(search_script_path),
        "selection_profile": {
            "top_weak": int(TOP_WEAK),
            "top_ckm": int(TOP_CKM),
            "kick_deltas": [int(x) for x in KICK_DELTAS],
            "rotation_shifts": [int(x) for x in ROTATION_SHIFTS],
            "robust_nonzero_rate_threshold": float(ROBUST_NONZERO_RATE_THRESHOLD),
            "robust_sign_stability_threshold": float(ROBUST_SIGN_STABILITY_THRESHOLD),
        },
        "developed_candidates": developed,
        "summary": {
            "developed_count": int(len(developed)),
            "robust_weak_count": int(len(robust_weak)),
            "robust_ckm_count": int(len(robust_ckm)),
            "robust_total_count": int(len(robust_weak) + len(robust_ckm)),
            "all_squared_zero_rate_one": bool(all(float(d["squared_zero_rate"]) == 1.0 for d in developed)),
            "max_nonzero_rate": float(max(float(d["nonzero_rate_excluding_t0"]) for d in developed)),
            "max_abs_excluding_t0": int(max(int(d["max_abs_excluding_t0"]) for d in developed)),
        },
        "limits": [
            "Robustness casebook remains in exploratory THETA-002 lane.",
            "No automatic impact on THETA-001 supported_bridge status.",
            "Claim progression requires independent replay and skeptic review.",
        ],
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def render_markdown(payload: Dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        "# THETA-002 Nonzero Robust Casebook (v1)",
        "",
        f"- Claim: `{payload['claim_id']}`",
        f"- Replay hash: `{payload['replay_hash']}`",
        "",
        "## Summary",
        f"- developed_count: `{s['developed_count']}`",
        f"- robust_weak_count: `{s['robust_weak_count']}`",
        f"- robust_ckm_count: `{s['robust_ckm_count']}`",
        f"- robust_total_count: `{s['robust_total_count']}`",
        f"- all_squared_zero_rate_one: `{s['all_squared_zero_rate_one']}`",
        f"- max_nonzero_rate: `{s['max_nonzero_rate']:.3f}`",
        f"- max_abs_excluding_t0: `{s['max_abs_excluding_t0']}`",
        "",
        "## Candidate Scores",
        "",
        "| lane | sample_id | nonzero_rate_ex_t0 | sign_stability | sq_zero_rate | max_abs_ex_t0 | robust |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for d in payload["developed_candidates"]:
        lines.append(
            f"| {d['lane']} | {d['sample_id']} | "
            f"{d['nonzero_rate_excluding_t0']:.3f} | {d['sign_stability_rate']:.3f} | "
            f"{d['squared_zero_rate']:.3f} | {d['max_abs_excluding_t0']} | {d['robust_nonzero_candidate']} |"
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
    parser = argparse.ArgumentParser(description="Build THETA nonzero robust casebook artifact")
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
        "theta001_nonzero_robust_casebook_v1: "
        f"robust_total={payload['summary']['robust_total_count']}, "
        f"replay_hash={payload['replay_hash'][:16]}..."
    )


if __name__ == "__main__":
    main()

