"""Compare S2880 seed strategies: random4 vs bundle4 vs bundle12 vs koide3."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np

from cog_v3.calc import build_v3_c12_phase_sector_metrics_v1 as psec
from cog_v3.calc import build_v3_c12_singlet_doublet_clock_shift_sparse_v1 as c12
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]

OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_bundle12_seed_vs_random_ablation_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_bundle12_seed_vs_random_ablation_v1.md"
OUT_CSV = ROOT / "cog_v3" / "sources" / "v3_bundle12_seed_vs_random_ablation_v1.csv"

SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_bundle12_seed_vs_random_ablation_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"
ORDER_CSV = ROOT / "cog_v3" / "sources" / "v3_octavian240_elements_v1.csv"

PHASE_COUNT = 12


@dataclass(frozen=True)
class AblationParams:
    runs_per_strategy: int = 80
    ticks: int = 84
    warmup_ticks: int = 16
    size_x: int = 27
    size_y: int = 11
    size_z: int = 11
    stencil_id: str = "cube26"
    boundary_mode: str = "fixed_vacuum"
    channel_policy_id: str = "uniform_all"
    global_seed: int = 1337


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _load_order_ids(order_target: int) -> List[int]:
    out: List[int] = []
    with ORDER_CSV.open("r", newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            if int(row["order"]) == int(order_target):
                out.append(int(row["id"]))
    return out


def _load_preferred_qids() -> List[int]:
    # Q240 has no order-12 class; prefer highest dynamic classes available.
    o6 = _load_order_ids(6)
    if o6:
        return o6
    o4 = _load_order_ids(4)
    if o4:
        return o4
    return [i for i in range(int(k.ALPHABET_SIZE)) if int(i) != int(k.IDENTITY_ID)]


def _idx(x: int, y: int, z: int, ny: int, nz: int) -> int:
    return (x * ny + y) * nz + z


def _s_id(phase: int, qid: int, qn: int) -> int:
    return int((int(phase) % PHASE_COUNT) * int(qn) + int(qid))


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


def _seed_positions12() -> List[Tuple[int, int, int]]:
    # 12 distinct near-center offsets (two rings/layers).
    return [
        (-1, -1, 0),
        (-1, 0, 0),
        (-1, 1, 0),
        (0, -1, 0),
        (0, 1, 0),
        (1, -1, 0),
        (1, 0, 0),
        (1, 1, 0),
        (-1, 0, 1),
        (0, 0, 1),
        (1, 0, 1),
        (0, 0, -1),
    ]


def _apply_seed(
    world: np.ndarray,
    nx: int,
    ny: int,
    nz: int,
    *,
    strategy: str,
    rng: random.Random,
    qn: int,
    preferred_qids: Sequence[int],
    nonidentity_ids: Sequence[int],
) -> Dict[str, Any]:
    cx, cy, cz = nx // 2, ny // 2, nz // 2
    placements: List[Tuple[int, int, int, int]] = []

    def put(dx: int, dy: int, dz: int, sid: int) -> None:
        x, y, z = cx + int(dx), cy + int(dy), cz + int(dz)
        if 0 <= x < nx and 0 <= y < ny and 0 <= z < nz:
            world[_idx(x, y, z, ny, nz)] = np.uint16(int(sid))
            placements.append((int(x), int(y), int(z), int(sid)))

    st = str(strategy)
    if st == "random4":
        pos = _seed_positions4()
        for (dx, dy, dz) in pos:
            qid = int(rng.choice(nonidentity_ids))
            phase = int(rng.randrange(0, PHASE_COUNT))
            put(dx, dy, dz, _s_id(phase, qid, qn))
    elif st == "bundle4":
        pos = _seed_positions4()
        qid = int(rng.choice(preferred_qids))
        base = int(rng.randrange(0, PHASE_COUNT))
        phases = [base, base + 3, base + 6, base + 9]
        for (dx, dy, dz), p in zip(pos, phases):
            put(dx, dy, dz, _s_id(int(p), int(qid), qn))
    elif st == "bundle12":
        pos = _seed_positions12()
        qid = int(rng.choice(preferred_qids))
        base = int(rng.randrange(0, PHASE_COUNT))
        for i, (dx, dy, dz) in enumerate(pos):
            put(dx, dy, dz, _s_id(base + i, int(qid), qn))
    elif st == "koide3":
        pos = [(-1, 0, 0), (0, 0, 0), (1, 0, 0)]
        qid = int(rng.choice(preferred_qids))
        base = int(rng.randrange(0, PHASE_COUNT))
        phases = [base, base + 4, base + 8]
        for (dx, dy, dz), p in zip(pos, phases):
            put(dx, dy, dz, _s_id(int(p), int(qid), qn))
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    return {
        "strategy": st,
        "placement_count": int(len(placements)),
        "placements": placements[:12],
    }


def _run_one(
    *,
    params: AblationParams,
    strategy: str,
    run_idx: int,
    mul: np.ndarray,
    qn: int,
    neighbors: np.ndarray,
    policy_neighbors: Dict[str, np.ndarray],
    order12_ids: Sequence[int],
    nonidentity_ids: Sequence[int],
) -> Dict[str, Any]:
    nx, ny, nz = int(params.size_x), int(params.size_y), int(params.size_z)
    n_cells = nx * ny * nz
    vac_id = int(c12.s_identity_id())
    rr = random.Random(int(params.global_seed) + 104729 * (run_idx + 1) + (hash(str(strategy)) & 0x7FFFFFFF))

    world = np.full((n_cells,), np.uint16(vac_id), dtype=np.uint16)
    seed_meta = _apply_seed(
        world,
        nx,
        ny,
        nz,
        strategy=str(strategy),
        rng=rr,
        qn=int(qn),
        preferred_qids=order12_ids,
        nonidentity_ids=nonidentity_ids,
    )

    h_seen: Dict[int, int] = {}
    first_repeat = None
    sig_rows: List[np.ndarray] = []
    c0 = _centroid(world, nx, ny, nz, vac_id)

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

        phases = (world.astype(np.int32) // int(qn)) % PHASE_COUNT
        counts = np.bincount(phases.astype(np.int32), minlength=PHASE_COUNT).astype(np.float64)
        counts /= float(np.sum(counts))
        sig_rows.append(counts)

    c1 = _centroid(world, nx, ny, nz, vac_id)
    disp = float(np.sqrt((c1[0] - c0[0]) ** 2 + (c1[1] - c0[1]) ** 2 + (c1[2] - c0[2]) ** 2))
    arr = np.asarray(sig_rows, dtype=np.float64)
    if arr.shape[0] >= 2:
        drift = float(np.mean(np.sum(np.abs(arr[1:, :] - arr[:-1, :]), axis=1)))
    else:
        drift = 0.0
    phase_std = float(np.std(arr, axis=0).mean()) if arr.size > 0 else 0.0
    nonvac_final = int(np.count_nonzero(world != np.uint16(vac_id)))

    candidate_lock = bool(first_repeat is not None and drift <= 0.40 and nonvac_final >= 4)
    propagating = bool(disp >= 0.50)

    return {
        "strategy": str(strategy),
        "run_idx": int(run_idx),
        "seed_meta": seed_meta,
        "first_repeat": first_repeat,
        "period": int(first_repeat["period"]) if isinstance(first_repeat, dict) else None,
        "clock_signature_drift": float(drift),
        "phase_signature_std_mean": float(phase_std),
        "centroid_displacement": float(disp),
        "nonvac_final": int(nonvac_final),
        "candidate_lock_flag": bool(candidate_lock),
        "propagating_flag": bool(propagating),
    }


def _summary_for(strategy: str, rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    rr = [r for r in rows if str(r["strategy"]) == str(strategy)]
    n = max(1, len(rr))
    periods = sorted(int(r["period"]) for r in rr if r["period"] is not None)
    drifts = sorted(float(r["clock_signature_drift"]) for r in rr)
    disps = sorted(float(r["centroid_displacement"]) for r in rr)
    return {
        "strategy": str(strategy),
        "run_count": int(len(rr)),
        "candidate_lock_yield": float(sum(1 for r in rr if bool(r["candidate_lock_flag"])) / n),
        "propagating_yield": float(sum(1 for r in rr if bool(r["propagating_flag"])) / n),
        "median_period": float(periods[len(periods) // 2]) if periods else None,
        "median_drift": float(drifts[len(drifts) // 2]) if drifts else 0.0,
        "median_displacement": float(disps[len(disps) // 2]) if disps else 0.0,
    }


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# v3 Bundle12 Seed vs Random Ablation (v1)",
        "",
        f"- kernel_profile: `{payload['kernel_profile']}`",
        f"- convention_id: `{payload['convention_id']}`",
        f"- runs_per_strategy: `{int(payload['params']['runs_per_strategy'])}`",
        "",
        "| strategy | run_count | candidate_lock_yield | propagating_yield | median_period | median_drift | median_displacement |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in payload["strategy_summary"]:
        mp = "" if r["median_period"] is None else f"{float(r['median_period']):.2f}"
        lines.append(
            f"| `{r['strategy']}` | {int(r['run_count'])} | {float(r['candidate_lock_yield']):.4f} | "
            f"{float(r['propagating_yield']):.4f} | {mp} | {float(r['median_drift']):.4f} | {float(r['median_displacement']):.4f} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- `bundle4`: phases `[p, p+3, p+6, p+9]` on one qid.",
            "- `bundle12`: phases `[p..p+11]` on one qid.",
            "- `koide3`: phases `[p, p+4, p+8]` on one qid.",
        ]
    )
    return "\n".join(lines)


def build_payload(params: AblationParams) -> Dict[str, Any]:
    qmul = c12.build_qmul_table()
    mul = c12.build_mul_table(phase_count=PHASE_COUNT, qmul=qmul)
    qn = int(qmul.shape[0])
    order12_ids = _load_preferred_qids()
    nonidentity_ids = [i for i in range(int(k.ALPHABET_SIZE)) if int(i) != int(k.IDENTITY_ID)]

    nx, ny, nz = int(params.size_x), int(params.size_y), int(params.size_z)
    policy_neighbors = psec._prepare_policy_neighbors(  # noqa: SLF001
        nx, ny, nz, str(params.stencil_id), str(params.boundary_mode)
    )
    neighbors = policy_neighbors["all"]

    strategies = ["random4", "bundle4", "bundle12", "koide3"]
    rows: List[Dict[str, Any]] = []
    for st in strategies:
        for i in range(int(params.runs_per_strategy)):
            rows.append(
                _run_one(
                    params=params,
                    strategy=str(st),
                    run_idx=int(i),
                    mul=mul,
                    qn=qn,
                    neighbors=neighbors,
                    policy_neighbors=policy_neighbors,
                    order12_ids=order12_ids,
                    nonidentity_ids=nonidentity_ids,
                )
            )

    strategy_summary = [_summary_for(st, rows) for st in strategies]
    payload: Dict[str, Any] = {
        "schema_version": "v3_bundle12_seed_vs_random_ablation_v1",
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "params": asdict(params),
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(ROOT / SCRIPT_REPO_PATH),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(ROOT / KERNEL_REPO_PATH),
        "strategy_summary": strategy_summary,
        "rows": rows,
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def write_artifacts(payload: Dict[str, Any]) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_render_md(payload), encoding="utf-8")
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "strategy",
                "run_idx",
                "candidate_lock_flag",
                "propagating_flag",
                "period",
                "clock_signature_drift",
                "phase_signature_std_mean",
                "centroid_displacement",
                "nonvac_final",
            ]
        )
        for r in payload["rows"]:
            w.writerow(
                [
                    str(r["strategy"]),
                    int(r["run_idx"]),
                    bool(r["candidate_lock_flag"]),
                    bool(r["propagating_flag"]),
                    "" if r["period"] is None else int(r["period"]),
                    float(r["clock_signature_drift"]),
                    float(r["phase_signature_std_mean"]),
                    float(r["centroid_displacement"]),
                    int(r["nonvac_final"]),
                ]
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-per-strategy", type=int, default=80)
    parser.add_argument("--ticks", type=int, default=84)
    parser.add_argument("--warmup-ticks", type=int, default=16)
    parser.add_argument("--size-x", type=int, default=27)
    parser.add_argument("--size-y", type=int, default=11)
    parser.add_argument("--size-z", type=int, default=11)
    parser.add_argument("--global-seed", type=int, default=1337)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    if bool(args.quick):
        params = AblationParams(
            runs_per_strategy=16,
            ticks=42,
            warmup_ticks=8,
            size_x=19,
            size_y=9,
            size_z=9,
            global_seed=int(args.global_seed),
        )
    else:
        params = AblationParams(
            runs_per_strategy=int(args.runs_per_strategy),
            ticks=int(args.ticks),
            warmup_ticks=int(args.warmup_ticks),
            size_x=int(args.size_x),
            size_y=int(args.size_y),
            size_z=int(args.size_z),
            global_seed=int(args.global_seed),
        )

    payload = build_payload(params)
    write_artifacts(payload)
    top = sorted(payload["strategy_summary"], key=lambda r: (float(r["candidate_lock_yield"]), float(r["propagating_yield"])), reverse=True)[0]
    print(
        "v3_bundle12_seed_vs_random_ablation_v1: "
        f"strategies={len(payload['strategy_summary'])}, "
        f"top={top['strategy']}, "
        f"lock_yield={float(top['candidate_lock_yield']):.4f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
