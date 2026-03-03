"""Seed-sweep wrapper for v3 fixed-manifest gate stack."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from cog_v3.calc import build_v3_fixed_manifest_kernel_gate_stack_v1 as stack
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_fixed_manifest_kernel_gate_stack_seed_sweep_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_fixed_manifest_kernel_gate_stack_seed_sweep_v1.md"
OUT_CSV = ROOT / "cog_v3" / "sources" / "v3_fixed_manifest_kernel_gate_stack_seed_sweep_v1.csv"
SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_fixed_manifest_kernel_gate_stack_seed_sweep_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# v3 Fixed Manifest Gate-Stack Seed Sweep (v1)",
        "",
        f"- convention_id: `{payload['convention_id']}`",
        f"- backend: `{payload['backend']}`",
        f"- seed_count: `{payload['seed_count']}`",
        f"- quick: `{payload['quick']}`",
        "",
        "| candidate | top_count | mean_score | mean_gates_passed |",
        "|---|---:|---:|---:|",
    ]
    for row in payload["candidate_summary"]:
        lines.append(
            f"| `{row['kernel_candidate_id']}` | {int(row['top_count'])} | "
            f"{float(row['mean_score']):.6f} | {float(row['mean_gates_passed']):.3f} |"
        )
    return "\n".join(lines)


def build_payload(*, backend: str, seed_count: int, global_seed: int, quick: bool) -> Dict[str, Any]:
    seeds = [int(global_seed) + 104729 * int(i) for i in range(int(seed_count))]
    run_rows: List[Dict[str, Any]] = []
    all_candidate_rows: List[Dict[str, Any]] = []

    for s in seeds:
        pl = stack.build_payload(backend=str(backend), global_seed=int(s), quick=bool(quick))
        rows = list(pl.get("rows", []))
        if not rows:
            continue
        top = rows[0]
        run_rows.append(
            {
                "global_seed": int(s),
                "top_kernel_candidate_id": str(top["kernel_candidate_id"]),
                "top_channel_policy_id": str(top["channel_policy_id"]),
                "top_score_total": float(top["score_total"]),
                "top_gates_passed": int(sum(1 for v in top["gate_results"].values() if bool(v))),
            }
        )
        for r in rows:
            all_candidate_rows.append(
                {
                    "global_seed": int(s),
                    "kernel_candidate_id": str(r["kernel_candidate_id"]),
                    "channel_policy_id": str(r["channel_policy_id"]),
                    "score_total": float(r["score_total"]),
                    "gates_passed": int(sum(1 for v in r["gate_results"].values() if bool(v))),
                    "gate0": bool(r["gate_results"]["gate0_contract"]),
                    "gate1": bool(r["gate_results"]["gate1_transport"]),
                    "gate2": bool(r["gate_results"]["gate2_detector"]),
                    "gate3": bool(r["gate_results"]["gate3_isotropy_lorentz"]),
                    "gate4": bool(r["gate_results"]["gate4_chirality"]),
                    "gate5": bool(r["gate_results"]["gate5_clock_structure"]),
                }
            )

    cand_ids = sorted(set(str(r["kernel_candidate_id"]) for r in all_candidate_rows))
    cand_summary: List[Dict[str, Any]] = []
    for cid in cand_ids:
        rr = [r for r in all_candidate_rows if str(r["kernel_candidate_id"]) == cid]
        top_count = sum(1 for r in run_rows if str(r["top_kernel_candidate_id"]) == cid)
        cand_summary.append(
            {
                "kernel_candidate_id": cid,
                "top_count": int(top_count),
                "mean_score": float(np.mean(np.asarray([float(r["score_total"]) for r in rr], dtype=np.float64))) if rr else 0.0,
                "mean_gates_passed": float(np.mean(np.asarray([int(r["gates_passed"]) for r in rr], dtype=np.float64)))
                if rr
                else 0.0,
                "gate_pass_rate": {
                    "gate0": float(np.mean(np.asarray([1.0 if r["gate0"] else 0.0 for r in rr], dtype=np.float64))) if rr else 0.0,
                    "gate1": float(np.mean(np.asarray([1.0 if r["gate1"] else 0.0 for r in rr], dtype=np.float64))) if rr else 0.0,
                    "gate2": float(np.mean(np.asarray([1.0 if r["gate2"] else 0.0 for r in rr], dtype=np.float64))) if rr else 0.0,
                    "gate3": float(np.mean(np.asarray([1.0 if r["gate3"] else 0.0 for r in rr], dtype=np.float64))) if rr else 0.0,
                    "gate4": float(np.mean(np.asarray([1.0 if r["gate4"] else 0.0 for r in rr], dtype=np.float64))) if rr else 0.0,
                    "gate5": float(np.mean(np.asarray([1.0 if r["gate5"] else 0.0 for r in rr], dtype=np.float64))) if rr else 0.0,
                },
            }
        )
    cand_summary.sort(key=lambda r: (int(r["top_count"]), float(r["mean_score"])), reverse=True)

    payload: Dict[str, Any] = {
        "schema_version": "v3_fixed_manifest_kernel_gate_stack_seed_sweep_v1",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(ROOT / SCRIPT_REPO_PATH),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(ROOT / KERNEL_REPO_PATH),
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "backend": str(backend),
        "quick": bool(quick),
        "seed_count": int(seed_count),
        "global_seed": int(global_seed),
        "run_rows": run_rows,
        "candidate_summary": cand_summary,
    }
    payload["replay_hash"] = _sha_payload(payload)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    with OUT_MD.open("w", encoding="utf-8") as f:
        f.write(_render_md(payload))
        f.write("\n")
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["global_seed", "top_kernel_candidate_id", "top_channel_policy_id", "top_score_total", "top_gates_passed"])
        for r in run_rows:
            w.writerow(
                [
                    int(r["global_seed"]),
                    str(r["top_kernel_candidate_id"]),
                    str(r["top_channel_policy_id"]),
                    float(r["top_score_total"]),
                    int(r["top_gates_passed"]),
                ]
            )
    return payload


def main() -> None:
    ap = argparse.ArgumentParser(description="Sweep fixed-manifest gate stack across seeds.")
    ap.add_argument("--backend", type=str, default="numba_cpu", choices=["python", "numba_cpu"])
    ap.add_argument("--seed-count", type=int, default=64)
    ap.add_argument("--global-seed", type=int, default=1337)
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()

    payload = build_payload(
        backend=str(args.backend),
        seed_count=int(args.seed_count),
        global_seed=int(args.global_seed),
        quick=bool(args.quick),
    )
    top = payload["candidate_summary"][0] if payload["candidate_summary"] else {}
    print(f"seed_count={payload['seed_count']}")
    print(f"top_candidate={top.get('kernel_candidate_id')}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_CSV}")


if __name__ == "__main__":
    main()

