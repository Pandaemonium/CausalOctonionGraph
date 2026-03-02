"""Enumerate singleton vacuum-driven cycles over S960 for COG v3.

Definition:
- Q240 is the closed Octavian-240 multiplicative alphabet from v3.
- C4 = {1, i, -1, -i} is a shared phase lane.
- S960 = C4 x Q240 with multiplication:
    (p1, q1) * (p2, q2) = (p1*p2, q1*q2)

Singleton orbit rule:
- x0 = vacuum = (1, e000)
- x_{t+1} = a * x_t
for fixed seed a in S960.

This script computes exact cycle periods for all 960 seeds.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_singleton_s960_cycles_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_singleton_s960_cycles_v1.md"
SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_singleton_s960_cycles_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"

PHASE_LABELS: Tuple[str, ...] = ("1", "i", "-1", "-i")
PHASE_COUNT = 4
S960_SIZE = PHASE_COUNT * int(k.ALPHABET_SIZE)
MAX_PERIOD_BOUND = S960_SIZE


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _phase_mul(a: int, b: int) -> int:
    # 1, i, -1, -i mapped to 0,1,2,3 and multiplied by addition mod 4.
    return int((int(a) + int(b)) % 4)


def _s_mul(lhs: Tuple[int, int], rhs: Tuple[int, int]) -> Tuple[int, int]:
    p = _phase_mul(int(lhs[0]), int(rhs[0]))
    q = int(k.multiply_ids(int(lhs[1]), int(rhs[1])))
    return (p, q)


def _sid(phase_idx: int, q_id: int) -> int:
    return int(phase_idx) * int(k.ALPHABET_SIZE) + int(q_id)


def _phase_q_from_sid(sid: int) -> Tuple[int, int]:
    qn = int(k.ALPHABET_SIZE)
    return (int(sid) // qn, int(sid) % qn)


def _singleton_period(seed: Tuple[int, int], max_steps: int = MAX_PERIOD_BOUND) -> int:
    vac = (0, int(k.IDENTITY_ID))  # (phase=1, e000)
    x = vac
    for t in range(1, int(max_steps) + 1):
        x = _s_mul(seed, x)
        if x == vac:
            return int(t)
    raise ValueError(f"Cycle did not return to vacuum within {max_steps} steps: seed={seed}")


def _trace(seed: Tuple[int, int], ticks: int) -> List[Dict[str, Any]]:
    vac = (0, int(k.IDENTITY_ID))
    x = vac
    rows: List[Dict[str, Any]] = [
        {
            "tick": 0,
            "phase_idx": 0,
            "phase_label": PHASE_LABELS[0],
            "q_id": int(k.IDENTITY_ID),
            "q_label": k.elem_label(int(k.IDENTITY_ID)),
            "sid": int(_sid(0, int(k.IDENTITY_ID))),
        }
    ]
    for t in range(1, int(ticks) + 1):
        x = _s_mul(seed, x)
        rows.append(
            {
                "tick": int(t),
                "phase_idx": int(x[0]),
                "phase_label": PHASE_LABELS[int(x[0])],
                "q_id": int(x[1]),
                "q_label": k.elem_label(int(x[1])),
                "sid": int(_sid(int(x[0]), int(x[1]))),
            }
        )
    return rows


def build_payload(example_ticks: int = 12, top_n: int = 16) -> Dict[str, Any]:
    if int(example_ticks) < 4:
        raise ValueError("example_ticks must be >= 4")
    if int(top_n) < 1:
        raise ValueError("top_n must be >= 1")

    rows: List[Dict[str, Any]] = []
    period_hist: Dict[int, int] = {}
    period_to_first_seed: Dict[int, int] = {}
    by_phase: Dict[str, Dict[int, int]] = {pl: {} for pl in PHASE_LABELS}
    errors: List[str] = []

    for phase_idx in range(PHASE_COUNT):
        for q_id in range(int(k.ALPHABET_SIZE)):
            seed = (int(phase_idx), int(q_id))
            sid = int(_sid(int(phase_idx), int(q_id)))
            try:
                period = int(_singleton_period(seed, max_steps=MAX_PERIOD_BOUND))
            except ValueError as exc:
                errors.append(str(exc))
                period = -1
            period_hist[period] = int(period_hist.get(period, 0) + 1)
            phase_name = PHASE_LABELS[int(phase_idx)]
            phase_hist = by_phase[phase_name]
            phase_hist[period] = int(phase_hist.get(period, 0) + 1)
            if period > 0 and period not in period_to_first_seed:
                period_to_first_seed[period] = int(sid)
            rows.append(
                {
                    "sid": int(sid),
                    "seed_phase_idx": int(phase_idx),
                    "seed_phase_label": phase_name,
                    "seed_q_id": int(q_id),
                    "period": int(period),
                }
            )

    rows = sorted(rows, key=lambda r: int(r["sid"]))
    valid_periods = sorted([p for p in period_hist.keys() if p > 0], reverse=True)
    max_period = int(valid_periods[0]) if valid_periods else -1
    min_period = int(min(p for p in period_hist.keys() if p > 0)) if valid_periods else -1

    longest: List[Dict[str, Any]] = []
    for p in valid_periods[: int(top_n)]:
        sid = int(period_to_first_seed[p])
        phase_idx, q_id = _phase_q_from_sid(int(sid))
        seed = (int(phase_idx), int(q_id))
        longest.append(
            {
                "period": int(p),
                "representative_seed_sid": int(sid),
                "representative_seed_phase_label": PHASE_LABELS[int(phase_idx)],
                "representative_seed_q_id": int(q_id),
                "representative_seed_q_label": k.elem_label(int(q_id)),
                "trace": _trace(seed, ticks=min(int(example_ticks), int(p))),
            }
        )

    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH
    payload: Dict[str, Any] = {
        "schema_version": "v3_singleton_s960_cycles_v1",
        "claim_id": "COG-V3-S960-SINGLETON-CYCLES-001",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(kernel_path),
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "alphabet_id": "s960_shared_phase_v1",
        "params": {
            "phase_labels": list(PHASE_LABELS),
            "phase_count": int(PHASE_COUNT),
            "q_alphabet_size": int(k.ALPHABET_SIZE),
            "s960_size": int(S960_SIZE),
            "vacuum_phase_idx": 0,
            "vacuum_q_id": int(k.IDENTITY_ID),
            "orbit_rule": "x_{t+1}=a*x_t",
            "max_period_bound": int(MAX_PERIOD_BOUND),
            "example_ticks": int(example_ticks),
            "top_n": int(top_n),
        },
        "period_histogram": {str(int(kp)): int(vp) for kp, vp in sorted(period_hist.items(), key=lambda kv: int(kv[0]))},
        "period_histogram_by_phase": {
            phase: {str(int(kp)): int(vp) for kp, vp in sorted(h.items(), key=lambda kv: int(kv[0]))}
            for phase, h in by_phase.items()
        },
        "summary": {
            "seed_count": int(len(rows)),
            "min_period": int(min_period),
            "max_period": int(max_period),
            "distinct_period_count": int(len(valid_periods)),
            "distinct_periods_desc": [int(p) for p in valid_periods],
            "longest_examples": longest,
            "error_count": int(len(errors)),
        },
        "seed_period_rows": rows,
        "checks": {
            "seed_count_ok": bool(len(rows) == int(S960_SIZE)),
            "all_periods_positive": bool(all(int(r["period"]) > 0 for r in rows)),
            "all_periods_within_bound": bool(all(0 < int(r["period"]) <= int(MAX_PERIOD_BOUND) for r in rows)),
            "no_scan_errors": bool(len(errors) == 0),
        },
        "errors": errors,
        "notes": [
            "This is a singleton census only; multi-voxel stabilization is handled by voxel-loop search.",
            "Because left multiplication by a fixed loop element is bijective, singleton trajectories are periodic.",
            "Use this artifact to seed restricted alphabets for tractable 3D motif scans.",
        ],
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def _render_md(payload: Dict[str, Any]) -> str:
    p = payload["params"]
    s = payload["summary"]
    lines = [
        "# COG v3 Singleton S960 Cycle Census (v1)",
        "",
        "## Scope",
        "",
        "- Alphabet: `S960 = C4 x Q240`",
        "- Rule: `x_{t+1} = a * x_t`, `x0 = vacuum`",
        "- All seeds scanned exactly once",
        "",
        "## Params",
        "",
        f"- phase_count: `{p['phase_count']}`",
        f"- q_alphabet_size: `{p['q_alphabet_size']}`",
        f"- s960_size: `{p['s960_size']}`",
        f"- max_period_bound: `{p['max_period_bound']}`",
        "",
        "## Summary",
        "",
        f"- seed_count: `{s['seed_count']}`",
        f"- min_period: `{s['min_period']}`",
        f"- max_period: `{s['max_period']}`",
        f"- distinct_period_count: `{s['distinct_period_count']}`",
        f"- no_scan_errors: `{payload['checks']['no_scan_errors']}`",
        "",
        "## Longest Representative Seeds",
        "",
        "| period | sid | phase | q_id |",
        "|---:|---:|---|---:|",
    ]
    for row in s["longest_examples"]:
        lines.append(
            f"| {row['period']} | {row['representative_seed_sid']} | "
            f"`{row['representative_seed_phase_label']}` | {row['representative_seed_q_id']} |"
        )
    lines.extend(["", "## Checks", ""])
    for kck, vck in payload["checks"].items():
        lines.append(f"- {kck}: `{vck}`")
    lines.append("")
    return "\n".join(lines)


def write_artifacts(
    payload: Dict[str, Any],
    json_paths: Sequence[Path] = (OUT_JSON,),
    md_paths: Sequence[Path] = (OUT_MD,),
) -> None:
    for path in json_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = _render_md(payload)
    for path in md_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(md, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--example-ticks", type=int, default=12)
    parser.add_argument("--top-n", type=int, default=16)
    args = parser.parse_args()

    payload = build_payload(example_ticks=int(args.example_ticks), top_n=int(args.top_n))
    write_artifacts(payload)
    print(
        "v3_singleton_s960_cycles_v1: "
        f"seeds={payload['summary']['seed_count']}, "
        f"distinct_periods={payload['summary']['distinct_period_count']}, "
        f"max_period={payload['summary']['max_period']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
