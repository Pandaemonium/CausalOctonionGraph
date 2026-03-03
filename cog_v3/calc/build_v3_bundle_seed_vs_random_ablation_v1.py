"""RFC-014 ablation: bundle seeds vs random controls on S960."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np

from cog_v3.calc import build_v3_c12_phase_sector_metrics_v1 as psec
from cog_v3.calc import build_v3_c12_singlet_doublet_clock_shift_sparse_v1 as c12
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]
SEED_BANK_CSV = ROOT / "cog_v3" / "sources" / "v3_order3_order12_bundle_seed_bank_v1.csv"
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_bundle_seed_vs_random_ablation_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_bundle_seed_vs_random_ablation_v1.md"
SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_bundle_seed_vs_random_ablation_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"


@dataclass(frozen=True)
class AblationParams:
    seed_budget: int = 1200
    ticks: int = 96
    warmup_ticks: int = 18
    size_x: int = 27
    size_y: int = 11
    size_z: int = 11
    stencil_id: str = "cube26"
    boundary_mode: str = "fixed_vacuum"
    channel_policy_id: str = "uniform_all"
    panel_id: str = "P0_s960_bundle_ablation"
    global_seed: int = 1337


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _load_seed_bank() -> List[Dict[str, Any]]:
    if not SEED_BANK_CSV.exists():
        from cog_v3.calc import build_v3_order3_order12_bundle_seed_bank_v1 as bank

        bank.build_payload()
    rows: List[Dict[str, Any]] = []
    with SEED_BANK_CSV.open("r", newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            rows.append(
                {
                    "bundle_id": int(row["bundle_id"]),
                    "generator_id": int(row["generator_id"]),
                    "core_order3_id": int(row["core_order3_id"]),
                    "bundle4_ids": [int(x) for x in str(row["bundle4_ids"]).split("|")],
                }
            )
    return rows


def _centroid(world: np.ndarray, nx: int, ny: int, nz: int, vac_id: int) -> Tuple[float, float, float]:
    ids = np.flatnonzero(world != np.uint16(vac_id))
    if ids.size == 0:
        return (float(nx // 2), float(ny // 2), float(nz // 2))
    xs = ids // (ny * nz)
    rem = ids % (ny * nz)
    ys = rem // nz
    zs = rem % nz
    return (float(np.mean(xs)), float(np.mean(ys)), float(np.mean(zs)))


def _seed_positions4() -> List[Tuple[int, int, int]]:
    return [(-1, 0, 0), (0, 0, 0), (1, 0, 0), (0, 1, 0)]


def _place(world: np.ndarray, nx: int, ny: int, nz: int, dx: int, dy: int, dz: int, sid: int) -> None:
    cx, cy, cz = nx // 2, ny // 2, nz // 2
    x, y, z = cx + int(dx), cy + int(dy), cz + int(dz)
    if 0 <= x < nx and 0 <= y < ny and 0 <= z < nz:
        world[(x * ny + y) * nz + z] = np.uint16(int(sid))


def _apply_seed(
    world: np.ndarray,
    nx: int,
    ny: int,
    nz: int,
    *,
    strategy: str,
    rr: random.Random,
    bank_rows: Sequence[Dict[str, Any]],
    nonidentity_ids: Sequence[int],
) -> Dict[str, Any]:
    st = str(strategy)
    picked = dict(rr.choice(list(bank_rows)))
    if st == "bundle4":
        pos = _seed_positions4()
        for p, sid in zip(pos, picked["bundle4_ids"]):
            _place(world, nx, ny, nz, p[0], p[1], p[2], int(sid))
        return {"strategy": st, "bundle_id": int(picked["bundle_id"]), "seed_ids": picked["bundle4_ids"]}
    if st == "random4":
        pos = _seed_positions4()
        sids = [int(rr.choice(nonidentity_ids)) for _ in range(4)]
        for p, sid in zip(pos, sids):
            _place(world, nx, ny, nz, p[0], p[1], p[2], int(sid))
        return {"strategy": st, "seed_ids": sids}
    if st == "single_order12":
        sid = int(picked["generator_id"])
        _place(world, nx, ny, nz, 0, 0, 0, sid)
        return {"strategy": st, "bundle_id": int(picked["bundle_id"]), "seed_ids": [sid]}
    if st == "single_order3":
        sid = int(picked["core_order3_id"])
        _place(world, nx, ny, nz, 0, 0, 0, sid)
        return {"strategy": st, "bundle_id": int(picked["bundle_id"]), "seed_ids": [sid]}
    raise ValueError(f"Unknown strategy: {strategy}")


def _run_one(
    *,
    params: AblationParams,
    strategy: str,
    run_idx: int,
    mul: np.ndarray,
    neighbors: np.ndarray,
    policy_neighbors: Dict[str, np.ndarray],
    bank_rows: Sequence[Dict[str, Any]],
    nonidentity_ids: Sequence[int],
) -> Dict[str, Any]:
    nx, ny, nz = int(params.size_x), int(params.size_y), int(params.size_z)
    vac_id = int(c12.s_identity_id())
    rr = random.Random(int(params.global_seed) + 104729 * (run_idx + 1) + (hash(str(strategy)) & 0x7FFFFFFF))
    world = np.full((nx * ny * nz,), np.uint16(vac_id), dtype=np.uint16)
    seed_meta = _apply_seed(
        world,
        nx,
        ny,
        nz,
        strategy=str(strategy),
        rr=rr,
        bank_rows=bank_rows,
        nonidentity_ids=nonidentity_ids,
    )
    c0 = _centroid(world, nx, ny, nz, vac_id)
    h_seen: Dict[int, int] = {}
    first_repeat = None
    sig_rows: List[np.ndarray] = []
    qn = int(k.ALPHABET_SIZE)

    for t in range(1, int(params.ticks) + 1):
        combo = psec._policy_combo(str(params.channel_policy_id), int(t), int(params.global_seed) + int(run_idx))  # noqa: SLF001
        nb = policy_neighbors.get(combo, neighbors)
        world = psec._step_sync(world, nb, mul, vac_id=vac_id)  # noqa: SLF001
        if t < int(params.warmup_ticks):
            continue
        h = hash(world.tobytes())
        if first_repeat is None:
            prev = h_seen.get(int(h))
            if prev is not None:
                first_repeat = {"t_prev": int(prev), "t_now": int(t), "period": int(t - prev)}
            else:
                h_seen[int(h)] = int(t)
        phases = (world.astype(np.int32) // qn) % 4
        counts = np.bincount(phases.astype(np.int32), minlength=4).astype(np.float64)
        counts /= float(np.sum(counts))
        sig_rows.append(counts)

    c1 = _centroid(world, nx, ny, nz, vac_id)
    disp = float(np.sqrt((c1[0] - c0[0]) ** 2 + (c1[1] - c0[1]) ** 2 + (c1[2] - c0[2]) ** 2))
    arr = np.asarray(sig_rows, dtype=np.float64)
    drift = float(np.mean(np.sum(np.abs(arr[1:, :] - arr[:-1, :]), axis=1))) if arr.shape[0] >= 2 else 0.0
    nonvac_final = int(np.count_nonzero(world != np.uint16(vac_id)))
    period = int(first_repeat["period"]) if isinstance(first_repeat, dict) else None

    candidate_lock = bool(period is not None and drift <= 0.40 and nonvac_final >= 4)
    propagating = bool(disp >= 0.75)
    score = float(max(0.0, 1.0 - drift) * 0.6 + min(1.0, disp / 3.0) * 0.4)

    return {
        "seed_strategy_id": str(strategy),
        "run_idx": int(run_idx),
        "seed_meta": seed_meta,
        "period": period,
        "clock_signature_drift": float(drift),
        "centroid_displacement": float(disp),
        "nonvac_final": int(nonvac_final),
        "candidate_lock_flag": bool(candidate_lock),
        "propagating_flag": bool(propagating),
        "score": float(score),
    }


def _summary(rows: Sequence[Dict[str, Any]], strategy: str) -> Dict[str, Any]:
    rr = [r for r in rows if str(r["seed_strategy_id"]) == str(strategy)]
    n = max(1, len(rr))
    scores = np.asarray([float(r["score"]) for r in rr], dtype=np.float64) if rr else np.asarray([0.0], dtype=np.float64)
    periods = sorted(int(r["period"]) for r in rr if r["period"] is not None)
    return {
        "seed_strategy_id": str(strategy),
        "seed_count": int(len(rr)),
        "candidate_lock_yield": float(sum(1 for r in rr if bool(r["candidate_lock_flag"])) / n),
        "propagating_yield": float(sum(1 for r in rr if bool(r["propagating_flag"])) / n),
        "score_distribution": {
            "mean": float(np.mean(scores)),
            "p50": float(np.percentile(scores, 50)),
            "p90": float(np.percentile(scores, 90)),
            "median_period": float(periods[len(periods) // 2]) if periods else None,
        },
    }


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# v3 Bundle Seed vs Random Ablation (v1)",
        "",
        f"- panel_id: `{payload['panel_id']}`",
        f"- convention_id: `{payload['convention_id']}`",
        f"- seed_budget: `{payload['params']['seed_budget']}`",
        "",
        "| strategy | seed_count | candidate_lock_yield | propagating_yield | score_mean | score_p90 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in payload["strategy_summary"]:
        sd = r["score_distribution"]
        lines.append(
            f"| `{r['seed_strategy_id']}` | {int(r['seed_count'])} | {float(r['candidate_lock_yield']):.4f} | "
            f"{float(r['propagating_yield']):.4f} | {float(sd['mean']):.4f} | {float(sd['p90']):.4f} |"
        )
    lines.extend(
        [
            "",
            "## Effect Size vs Control (`random4`)",
            "",
            f"- {json.dumps(payload['effect_size_vs_control'], sort_keys=True)}",
            "",
            "## Gate Results",
            "",
            f"- {json.dumps(payload['gate_results'], sort_keys=True)}",
        ]
    )
    return "\n".join(lines)


def build_payload(params: AblationParams) -> Dict[str, Any]:
    bank_rows = _load_seed_bank()
    qmul = c12.build_qmul_table()
    mul = c12.build_mul_table(phase_count=4, qmul=qmul)  # S960 lane
    nx, ny, nz = int(params.size_x), int(params.size_y), int(params.size_z)
    offsets = psec._offsets(str(params.stencil_id))  # noqa: SLF001
    neighbors = psec._build_neighbors(nx, ny, nz, offsets, boundary_mode=str(params.boundary_mode))  # noqa: SLF001
    policy_neighbors = psec._prepare_policy_neighbors(nx, ny, nz, str(params.stencil_id), str(params.boundary_mode))  # noqa: SLF001
    nonidentity_ids = [i for i in range(int(mul.shape[0])) if int(i) != int(c12.s_identity_id())]

    strategies = ["random4", "bundle4", "single_order12", "single_order3"]
    n_each = max(1, int(params.seed_budget) // len(strategies))
    rows: List[Dict[str, Any]] = []
    for st in strategies:
        for i in range(n_each):
            rows.append(
                _run_one(
                    params=params,
                    strategy=st,
                    run_idx=i,
                    mul=mul,
                    neighbors=neighbors,
                    policy_neighbors=policy_neighbors,
                    bank_rows=bank_rows,
                    nonidentity_ids=nonidentity_ids,
                )
            )

    summary = [_summary(rows, st) for st in strategies]
    ctrl = next(r for r in summary if r["seed_strategy_id"] == "random4")
    ctrl_lock = float(ctrl["candidate_lock_yield"])
    ctrl_prop = float(ctrl["propagating_yield"])
    ctrl_score = float(ctrl["score_distribution"]["mean"])

    effect: Dict[str, Dict[str, float]] = {}
    for r in summary:
        sid = str(r["seed_strategy_id"])
        effect[sid] = {
            "delta_candidate_lock_yield": float(r["candidate_lock_yield"] - ctrl_lock),
            "delta_propagating_yield": float(r["propagating_yield"] - ctrl_prop),
            "delta_score_mean": float(r["score_distribution"]["mean"] - ctrl_score),
        }

    bundle = next(r for r in summary if r["seed_strategy_id"] == "bundle4")
    gate_results = {
        "gate1_bundle_beats_random_lock": bool(float(bundle["candidate_lock_yield"]) > float(ctrl_lock)),
        "gate2_bundle_beats_random_prop": bool(float(bundle["propagating_yield"]) > float(ctrl_prop)),
        "gate3_bundle_beats_random_score": bool(float(bundle["score_distribution"]["mean"]) > float(ctrl_score)),
    }

    payload: Dict[str, Any] = {
        "schema_version": "v3_bundle_seed_vs_random_ablation_v1",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(ROOT / SCRIPT_REPO_PATH),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(ROOT / KERNEL_REPO_PATH),
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "panel_id": str(params.panel_id),
        "params": {
            "seed_budget": int(params.seed_budget),
            "ticks": int(params.ticks),
            "warmup_ticks": int(params.warmup_ticks),
            "size_x": int(params.size_x),
            "size_y": int(params.size_y),
            "size_z": int(params.size_z),
            "stencil_id": str(params.stencil_id),
            "boundary_mode": str(params.boundary_mode),
            "channel_policy_id": str(params.channel_policy_id),
            "global_seed": int(params.global_seed),
        },
        "strategy_summary": summary,
        "effect_size_vs_control": effect,
        "gate_results": gate_results,
    }
    payload["replay_hash"] = _sha_payload(payload)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    with OUT_MD.open("w", encoding="utf-8") as f:
        f.write(_render_md(payload))
        f.write("\n")
    return payload


def main() -> None:
    ap = argparse.ArgumentParser(description="Run S960 bundle seed vs random ablation.")
    ap.add_argument("--seed-budget", type=int, default=1200)
    ap.add_argument("--ticks", type=int, default=96)
    ap.add_argument("--warmup-ticks", type=int, default=18)
    ap.add_argument("--size-x", type=int, default=27)
    ap.add_argument("--size-y", type=int, default=11)
    ap.add_argument("--size-z", type=int, default=11)
    ap.add_argument("--stencil-id", type=str, default="cube26", choices=["axial6", "cube26"])
    ap.add_argument("--boundary-mode", type=str, default="fixed_vacuum", choices=["fixed_vacuum", "periodic"])
    ap.add_argument("--channel-policy-id", type=str, default="uniform_all")
    ap.add_argument("--global-seed", type=int, default=1337)
    args = ap.parse_args()

    params = AblationParams(
        seed_budget=int(args.seed_budget),
        ticks=int(args.ticks),
        warmup_ticks=int(args.warmup_ticks),
        size_x=int(args.size_x),
        size_y=int(args.size_y),
        size_z=int(args.size_z),
        stencil_id=str(args.stencil_id),
        boundary_mode=str(args.boundary_mode),
        channel_policy_id=str(args.channel_policy_id),
        global_seed=int(args.global_seed),
    )
    payload = build_payload(params)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"bundle4 lock yield={next(r for r in payload['strategy_summary'] if r['seed_strategy_id']=='bundle4')['candidate_lock_yield']:.6f}")


if __name__ == "__main__":
    main()

