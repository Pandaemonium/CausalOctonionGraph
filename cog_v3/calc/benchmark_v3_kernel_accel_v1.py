"""Benchmark v3 kernel backends (python vs numba_cpu vs optional numba_cuda)."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np

from cog_v3.python import kernel_octavian240_accel_v1 as accel
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_kernel_accel_benchmark_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_kernel_accel_benchmark_v1.md"
SCRIPT_REPO_PATH = "cog_v3/calc/benchmark_v3_kernel_accel_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_accel_v1.py"


@dataclass(frozen=True)
class BenchCase:
    case_id: str
    size_x: int
    size_y: int
    size_z: int
    ticks: int
    stencil_id: str = "axial6"


@dataclass(frozen=True)
class BenchParams:
    cases: Tuple[BenchCase, ...] = (
        BenchCase("small_15x7x7", 15, 7, 7, 48, "axial6"),
        BenchCase("mid_39x11x11", 39, 11, 11, 24, "axial6"),
        BenchCase("wide_79x21x21", 79, 21, 21, 8, "axial6"),
    )
    reps: int = 3
    warmup_reps: int = 1
    min_measure_sec: float = 0.25
    include_python_for_all_cases: bool = False
    threads_per_block: int = accel.THREADS_PER_BLOCK


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _timed_run(
    world: np.ndarray,
    neighbors: np.ndarray,
    mul_table: np.ndarray,
    *,
    backend: str,
    ticks: int,
    reps: int,
    warmup_reps: int,
    min_measure_sec: float,
    threads_per_block: int,
) -> Dict[str, Any]:
    backend = str(backend)
    timings: List[float] = []
    mults: List[int] = []
    last_world_hash = ""

    # warmup
    for _ in range(int(max(0, warmup_reps))):
        _ = accel.run_ticks(
            world,
            neighbors,
            mul_table,
            ticks=int(ticks),
            backend=backend,
            threads_per_block=int(threads_per_block),
        )

    # Stable semantic hash at base tick budget.
    out_base = accel.run_ticks(
        world,
        neighbors,
        mul_table,
        ticks=int(ticks),
        backend=backend,
        threads_per_block=int(threads_per_block),
    )
    last_world_hash = hashlib.sha256(out_base.tobytes()).hexdigest()

    for _ in range(int(max(1, reps))):
        mult = 1
        dt = 0.0
        while True:
            t0 = time.perf_counter()
            _ = accel.run_ticks(
                world,
                neighbors,
                mul_table,
                ticks=int(ticks) * int(mult),
                backend=backend,
                threads_per_block=int(threads_per_block),
            )
            dt = float(time.perf_counter() - t0)
            if dt >= float(min_measure_sec) or mult >= (1 << 18):
                break
            mult *= 2

        timings.append(dt)
        mults.append(int(mult))

    # Compute rates from the best normalized timing (accounting for multiplier).
    norm_best_idx = min(
        range(len(timings)),
        key=lambda i: timings[i] / max(1, mults[i]),
    )
    best_mult = int(mults[norm_best_idx])
    best_dt = float(timings[norm_best_idx])
    effective_ticks_best = int(ticks) * best_mult
    effective_cells_best = int(world.shape[0]) * effective_ticks_best

    # Mean values over normalized-per-mult timings.
    norm_times = [timings[i] / max(1, mults[i]) for i in range(len(timings))]
    t_best = float(min(norm_times))
    t_mean = float(sum(norm_times) / len(norm_times))
    n = int(world.shape[0])
    cells_updated = n * int(ticks)
    return {
        "backend": backend,
        "timings_sec": [float(x) for x in timings],
        "timing_tick_multipliers": [int(x) for x in mults],
        "best_multiplier": int(best_mult),
        "best_sec": float(t_best),
        "mean_sec": float(t_mean),
        "ticks": int(ticks),
        "cells": int(n),
        "cells_updated": int(cells_updated),
        "best_ticks_per_sec": float(effective_ticks_best / best_dt),
        "best_cells_per_sec": float(effective_cells_best / best_dt),
        "output_hash_sha256": last_world_hash,
    }


def _build_case_world(case: BenchCase) -> Tuple[np.ndarray, np.ndarray]:
    offsets = accel.offsets_for_stencil(case.stencil_id)
    neighbors = accel.build_neighbor_table(case.size_x, case.size_y, case.size_z, offsets)
    world = accel.make_world(
        case.size_x,
        case.size_y,
        case.size_z,
        seed_state_id=accel.default_probe_state_id(),
    )
    return world, neighbors


def build_payload(params: BenchParams | None = None) -> Dict[str, Any]:
    p = params if params is not None else BenchParams()
    info = accel.backend_matrix()
    mul_table = accel.build_mul_table()

    case_rows: List[Dict[str, Any]] = []
    for idx, case in enumerate(p.cases):
        world, neighbors = _build_case_world(case)
        backends: List[str] = ["numba_cpu"]
        if info["numba_cuda"].available:
            backends.append("numba_cuda")
        if bool(p.include_python_for_all_cases) or idx < 2:
            backends.insert(0, "python")

        bench_rows: List[Dict[str, Any]] = []
        for b in backends:
            try:
                row = _timed_run(
                    world,
                    neighbors,
                    mul_table,
                    backend=b,
                    ticks=case.ticks,
                    reps=p.reps,
                    warmup_reps=p.warmup_reps,
                    min_measure_sec=p.min_measure_sec,
                    threads_per_block=p.threads_per_block,
                )
                row["ok"] = True
            except Exception as exc:
                row = {
                    "backend": b,
                    "ok": False,
                    "error": str(exc),
                    "ticks": int(case.ticks),
                    "cells": int(world.shape[0]),
                }
            bench_rows.append(row)

        # sanity hash consistency across successful backends
        good = [r for r in bench_rows if r.get("ok")]
        hashes = sorted(set(r["output_hash_sha256"] for r in good))
        case_rows.append(
            {
                "case_id": case.case_id,
                "size": [int(case.size_x), int(case.size_y), int(case.size_z)],
                "stencil_id": case.stencil_id,
                "ticks": int(case.ticks),
                "cells": int(world.shape[0]),
                "neighbors_per_cell": int(neighbors.shape[1]),
                "hash_consistent_across_backends": bool(len(hashes) <= 1),
                "benchmarks": bench_rows,
            }
        )

    payload: Dict[str, Any] = {
        "schema_version": "v3_kernel_accel_benchmark_v1",
        "claim_id": "COG-V3-KERNEL-ACCEL-BENCH-001",
        "mode": "simulation_first_structure_first",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(ROOT / SCRIPT_REPO_PATH),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(ROOT / KERNEL_REPO_PATH),
        "canonical_kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "backend_availability": {
            bid: {
                "available": bool(v.available),
                "reason": v.reason,
            }
            for bid, v in info.items()
        },
        "params": {
            "reps": int(p.reps),
            "warmup_reps": int(p.warmup_reps),
            "min_measure_sec": float(p.min_measure_sec),
            "include_python_for_all_cases": bool(p.include_python_for_all_cases),
            "threads_per_block": int(p.threads_per_block),
        },
        "cases": case_rows,
        "notes": [
            "numba_cuda path is benchmarked only if runtime reports CUDA available.",
            "All backends must produce the same output hash for each case.",
            "Python reference backend is included for small/mid cases by default.",
        ],
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# V3 Kernel Acceleration Benchmark (v1)",
        "",
        "## Backend Availability",
        "",
    ]
    for bid, meta in payload["backend_availability"].items():
        lines.append(f"- `{bid}`: available=`{meta['available']}` ({meta['reason']})")
    lines.extend(
        [
            "",
            "## Cases",
            "",
            "| case_id | size | ticks | backend | ok | best_sec | best_ticks/s | best_cells/s | hash_ok |",
            "|---|---|---:|---|---|---:|---:|---:|---|",
        ]
    )
    for case in payload["cases"]:
        size = "x".join(str(x) for x in case["size"])
        hash_ok = case["hash_consistent_across_backends"]
        for row in case["benchmarks"]:
            if not row.get("ok"):
                lines.append(
                    f"| `{case['case_id']}` | `{size}` | {case['ticks']} | `{row['backend']}` | `False` | - | - | - | `{hash_ok}` |"
                )
                continue
            lines.append(
                f"| `{case['case_id']}` | `{size}` | {case['ticks']} | `{row['backend']}` | `True` | "
                f"{row['best_sec']:.6f} | {row['best_ticks_per_sec']:.3f} | {row['best_cells_per_sec']:.1f} | `{hash_ok}` |"
            )
    lines.append("")
    return "\n".join(lines)


def write_artifacts(payload: Dict[str, Any]) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_render_md(payload), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reps", type=int, default=BenchParams.reps)
    parser.add_argument("--warmup-reps", type=int, default=BenchParams.warmup_reps)
    parser.add_argument("--min-measure-sec", type=float, default=BenchParams.min_measure_sec)
    parser.add_argument("--threads-per-block", type=int, default=BenchParams.threads_per_block)
    parser.add_argument("--include-python-for-all-cases", action="store_true")
    args = parser.parse_args()

    params = BenchParams(
        reps=int(args.reps),
        warmup_reps=int(args.warmup_reps),
        min_measure_sec=float(args.min_measure_sec),
        include_python_for_all_cases=bool(args.include_python_for_all_cases),
        threads_per_block=int(args.threads_per_block),
    )
    payload = build_payload(params)
    write_artifacts(payload)
    print(
        "v3_kernel_accel_benchmark_v1: "
        f"cases={len(payload['cases'])}, "
        f"cuda_available={payload['backend_availability']['numba_cuda']['available']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
