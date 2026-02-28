"""Deterministic search for nonzero CP-odd candidates in THETA alternative lane.

This search keeps the current squared residual as control and evaluates the
sign-sensitive oriented Fano-cubic residual across randomized finite traces.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from cog_v2.calc import theta001_cp_invariant_v2 as t
from cog_v2.calc.build_theta001_bridge_closure_v2 import CKM_PHASES, CKM_TRANSPORT_PERIODS, WEAK_KICKS
from cog_v2.calc.build_theta001_nonzero_candidate_probe_v1 import oriented_fano_cubic


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "theta001_nonzero_search_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "theta001_nonzero_search_v1.md"
SCRIPT_REPO_PATH = "cog_v2/calc/build_theta001_nonzero_search_v1.py"
RNG_SEED = 20260228
SAMPLE_COUNT = 512
OP_DEPTH = 36
TOP_K = 20


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _to_repo_path(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def _rand_state(rng: random.Random) -> t.State8:
    while True:
        vals = tuple(int(rng.randint(-3, 3)) for _ in range(8))
        if any(v != 0 for v in vals):
            return vals  # type: ignore[return-value]


def _rand_ops(rng: random.Random, depth: int) -> Tuple[int, ...]:
    return tuple(int(rng.randint(1, 7)) for _ in range(depth))


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


def _search_rows() -> List[Dict[str, Any]]:
    rng = random.Random(RNG_SEED)
    rows: List[Dict[str, Any]] = []
    for idx in range(SAMPLE_COUNT):
        init = list(_rand_state(rng))
        weak_kick = int(rng.choice(WEAK_KICKS))
        init[7] += weak_kick
        init_t = tuple(init)  # type: ignore[assignment]
        ops = _rand_ops(rng, OP_DEPTH)
        ckm_phase = int(rng.choice(CKM_PHASES))
        transport_period = int(rng.choice(CKM_TRANSPORT_PERIODS))

        # Weak lane
        weak_orig = t.run_update_trace(init_t, ops, t.FANO_SIGN)
        weak_dual = t.run_update_trace(t.cp_map(init_t), ops, t.flipped_sign_table())
        weak_sq = int(t.cp_weighted_trace_delta(init_t, ops, t.STRONG_SECTOR_WEIGHTS))
        weak_cubic = _trace_delta_oriented_cubic(weak_orig, weak_dual, exclude_t0=False)
        weak_cubic_ex_t0 = _trace_delta_oriented_cubic(weak_orig, weak_dual, exclude_t0=True)

        # CKM-like lane
        ckm_orig = t.run_update_trace_ckm_transport(
            init_t,
            ops,
            t.FANO_SIGN,
            ckm_phase=ckm_phase,
            transport_period=transport_period,
        )
        ckm_dual = t.run_update_trace_ckm_transport(
            t.cp_map(init_t),
            ops,
            t.flipped_sign_table(),
            ckm_phase=ckm_phase,
            transport_period=transport_period,
        )
        ckm_sq = int(
            t.weak_leakage_ckm_like_strong_residual(
                tuple(int(x) for x in init_t),
                ops,
                weak_kick=0,
                ckm_phase=ckm_phase,
                transport_period=transport_period,
            )
        )
        ckm_cubic = _trace_delta_oriented_cubic(ckm_orig, ckm_dual, exclude_t0=False)
        ckm_cubic_ex_t0 = _trace_delta_oriented_cubic(ckm_orig, ckm_dual, exclude_t0=True)

        rows.append(
            {
                "sample_id": int(idx),
                "initial_state": [int(x) for x in init_t],
                "weak_kick": int(weak_kick),
                "op_sequence": [int(x) for x in ops],
                "ckm_phase": int(ckm_phase),
                "transport_period": int(transport_period),
                "weak_lane": {
                    "squared_residual": int(weak_sq),
                    "oriented_cubic_residual": int(weak_cubic),
                    "oriented_cubic_residual_excluding_t0": int(weak_cubic_ex_t0),
                },
                "ckm_lane": {
                    "squared_residual": int(ckm_sq),
                    "oriented_cubic_residual": int(ckm_cubic),
                    "oriented_cubic_residual_excluding_t0": int(ckm_cubic_ex_t0),
                },
            }
        )
    return rows


def build_payload() -> Dict[str, Any]:
    script_path = ROOT / SCRIPT_REPO_PATH
    rows = _search_rows()

    weak_sq_all_zero = all(int(r["weak_lane"]["squared_residual"]) == 0 for r in rows)
    ckm_sq_all_zero = all(int(r["ckm_lane"]["squared_residual"]) == 0 for r in rows)
    weak_nonzero_ex_t0 = [r for r in rows if int(r["weak_lane"]["oriented_cubic_residual_excluding_t0"]) != 0]
    ckm_nonzero_ex_t0 = [r for r in rows if int(r["ckm_lane"]["oriented_cubic_residual_excluding_t0"]) != 0]

    top_weak = sorted(
        weak_nonzero_ex_t0,
        key=lambda r: abs(int(r["weak_lane"]["oriented_cubic_residual_excluding_t0"])),
        reverse=True,
    )[:TOP_K]
    top_ckm = sorted(
        ckm_nonzero_ex_t0,
        key=lambda r: abs(int(r["ckm_lane"]["oriented_cubic_residual_excluding_t0"])),
        reverse=True,
    )[:TOP_K]

    payload: Dict[str, Any] = {
        "schema_version": "theta001_nonzero_search_v1",
        "claim_id": "THETA-001",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "search_profile": {
            "rng_seed": int(RNG_SEED),
            "sample_count": int(SAMPLE_COUNT),
            "op_depth": int(OP_DEPTH),
            "coefficient_range": [-3, 3],
            "weak_kicks": [int(x) for x in WEAK_KICKS],
            "ckm_phases": [int(x) for x in CKM_PHASES],
            "ckm_transport_periods": [int(x) for x in CKM_TRANSPORT_PERIODS],
            "top_k": int(TOP_K),
        },
        "summary": {
            "weak_squared_all_zero": bool(weak_sq_all_zero),
            "ckm_squared_all_zero": bool(ckm_sq_all_zero),
            "weak_nonzero_excluding_t0_count": int(len(weak_nonzero_ex_t0)),
            "ckm_nonzero_excluding_t0_count": int(len(ckm_nonzero_ex_t0)),
            "weak_nonzero_excluding_t0_rate": float(len(weak_nonzero_ex_t0) / len(rows)),
            "ckm_nonzero_excluding_t0_rate": float(len(ckm_nonzero_ex_t0) / len(rows)),
            "weak_max_abs_excluding_t0": int(
                max(abs(int(r["weak_lane"]["oriented_cubic_residual_excluding_t0"])) for r in rows)
            ),
            "ckm_max_abs_excluding_t0": int(
                max(abs(int(r["ckm_lane"]["oriented_cubic_residual_excluding_t0"])) for r in rows)
            ),
        },
        "top_weak_nonzero_excluding_t0": top_weak,
        "top_ckm_nonzero_excluding_t0": top_ckm,
        "limits": [
            "Search lane is exploratory and does not alter THETA-001 claim status.",
            "Observable here is oriented_fano_cubic_cp_odd_v1, not the currently promoted squared residual lane.",
            "Promotion impact requires preregistration and independent skeptical review.",
        ],
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def render_markdown(payload: Dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        "# THETA-001 Nonzero Search (v1)",
        "",
        f"- Claim: `{payload['claim_id']}`",
        f"- Replay hash: `{payload['replay_hash']}`",
        f"- RNG seed: `{payload['search_profile']['rng_seed']}`",
        f"- Samples: `{payload['search_profile']['sample_count']}`",
        f"- Op depth: `{payload['search_profile']['op_depth']}`",
        "",
        "## Summary",
        f"- weak_squared_all_zero: `{s['weak_squared_all_zero']}`",
        f"- ckm_squared_all_zero: `{s['ckm_squared_all_zero']}`",
        f"- weak_nonzero_excluding_t0_count: `{s['weak_nonzero_excluding_t0_count']}` ({s['weak_nonzero_excluding_t0_rate']:.3f})",
        f"- ckm_nonzero_excluding_t0_count: `{s['ckm_nonzero_excluding_t0_count']}` ({s['ckm_nonzero_excluding_t0_rate']:.3f})",
        f"- weak_max_abs_excluding_t0: `{s['weak_max_abs_excluding_t0']}`",
        f"- ckm_max_abs_excluding_t0: `{s['ckm_max_abs_excluding_t0']}`",
        "",
        "## Top Weak Nonzero Cases (excluding t0)",
    ]
    for row in payload["top_weak_nonzero_excluding_t0"][:10]:
        lines.append(
            "- "
            f"sample={row['sample_id']}, weak_kick={row['weak_kick']}, "
            f"res={row['weak_lane']['oriented_cubic_residual_excluding_t0']}, "
            f"sq={row['weak_lane']['squared_residual']}"
        )
    lines.extend(["", "## Top CKM Nonzero Cases (excluding t0)"])
    for row in payload["top_ckm_nonzero_excluding_t0"][:10]:
        lines.append(
            "- "
            f"sample={row['sample_id']}, weak_kick={row['weak_kick']}, "
            f"phase={row['ckm_phase']}, period={row['transport_period']}, "
            f"res={row['ckm_lane']['oriented_cubic_residual_excluding_t0']}, "
            f"sq={row['ckm_lane']['squared_residual']}"
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
    parser = argparse.ArgumentParser(description="Build THETA nonzero search artifact")
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
        "theta001_nonzero_search_v1: "
        f"weak_nonzero_rate={payload['summary']['weak_nonzero_excluding_t0_rate']:.3f}, "
        f"ckm_nonzero_rate={payload['summary']['ckm_nonzero_excluding_t0_rate']:.3f}, "
        f"replay_hash={payload['replay_hash'][:16]}..."
    )


if __name__ == "__main__":
    main()

