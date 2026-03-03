"""RFC-017 phase-boundary sweep on S2880 with w3 and optional memory bias."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Sequence

import numpy as np

from cog_v3.calc import build_v3_c12_phase_sector_metrics_v1 as psec
from cog_v3.calc import build_v3_c12_singlet_doublet_clock_shift_sparse_v1 as c12
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_phase_boundary_sweep_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_phase_boundary_sweep_v1.md"
OUT_CSV = ROOT / "cog_v3" / "sources" / "v3_phase_boundary_sweep_v1.csv"
SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_phase_boundary_kernel_sweep_v1.py"
PHASE_SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_c12_phase_sector_metrics_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"

PHASE_COUNT = 12


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _safe_div(a: float, b: float) -> float:
    if abs(float(b)) < 1e-12:
        return 0.0
    return float(a) / float(b)


def _s_id(phase: int, qid: int, qn: int) -> int:
    return int((int(phase) % PHASE_COUNT) * int(qn) + int(qid))


def _parse_float_list(text: str) -> List[float]:
    vals: List[float] = []
    for x in str(text).split(","):
        x = x.strip()
        if not x:
            continue
        vals.append(float(x))
    if not vals:
        raise ValueError("empty float list")
    return vals


def _trial_bank_odd_lane(qn: int) -> List[Dict[str, Any]]:
    e111 = psec._q_basis_id(7, +1)  # noqa: SLF001
    e001 = psec._q_basis_id(1, +1)  # noqa: SLF001
    out: List[Dict[str, Any]] = []
    for p in (1, 5, 9):
        out.append(
            {
                "trial_id": f"sheet_x_oddp{p}",
                "seed_family": "sheet_x",
                "state_id": _s_id(int(p), int(e111), int(qn)),
                "kick_id": _s_id(0, int(e001), int(qn)),
            }
        )
    return out


def _kuramoto_r(phases: np.ndarray) -> float:
    if phases.size == 0:
        return 0.0
    ang = (2.0 * math.pi / float(PHASE_COUNT)) * phases.astype(np.float64)
    z = np.exp(1j * ang)
    return float(np.abs(np.mean(z)))


def _spectral_entropy(series: Sequence[float]) -> float:
    x = np.asarray(series, dtype=np.float64)
    if x.size < 8:
        return 1.0
    x = x - float(np.mean(x))
    psd = np.abs(np.fft.rfft(x)) ** 2
    psd = psd[1:] if psd.size > 1 else psd
    s = float(np.sum(psd))
    if s <= 1e-12:
        return 1.0
    p = psd / s
    p = np.clip(p, 1e-12, 1.0)
    h = float(-np.sum(p * np.log(p)))
    hmax = float(np.log(float(p.size))) if p.size > 1 else 1.0
    return float(h / max(1e-12, hmax))


def _phase_classification(r_mean: float, r_std: float, r3: float, h_spec: float) -> str:
    # RFC-017 heuristic bands
    if r_mean > 0.7 and r_std < 0.02:
        return "O"
    if r3 >= 2.0 and r_mean >= 0.15 and h_spec < 0.7:
        return "M"
    return "D"


def _build_w3_prob(w3: float) -> np.ndarray:
    # Weight by |Δp| class where class-3 gets weight w3, others weight 1, class-0 weight 1.
    w = np.ones((PHASE_COUNT,), dtype=np.float64)
    for d in range(PHASE_COUNT):
        mag = int(min(d, PHASE_COUNT - d))
        if mag == 3:
            w[d] = float(max(0.0, w3))
    s = float(np.sum(w))
    if s <= 1e-12:
        w[:] = 1.0 / float(PHASE_COUNT)
    else:
        w /= s
    return w


def _step_sync_biased(
    world: np.ndarray,
    prev_world: np.ndarray,
    neighbors: np.ndarray,
    mul: np.ndarray,
    vac_id: int,
    *,
    w3: float,
    p_mem: float,
    rng: np.random.Generator,
    qn: int,
) -> np.ndarray:
    base = psec._step_sync(world, neighbors, mul, vac_id=vac_id)  # noqa: SLF001
    out = base.copy()
    support = (world != np.uint16(vac_id)) | (base != np.uint16(vac_id))
    idx = np.flatnonzero(support)
    if idx.size == 0:
        return out

    # Keep Q240 content from canonical multiplicative step, but control the phase-channel
    # update explicitly for phase-boundary probing.
    phase_old = (world[idx].astype(np.int32) // int(qn)).astype(np.int16)
    phase_prev = (prev_world[idx].astype(np.int32) // int(qn)).astype(np.int16)
    q_part = (base[idx].astype(np.int32) % int(qn)).astype(np.int32)
    phase_new = phase_old.copy()

    # Memory-2 style bias: continue prior phase velocity.
    if float(p_mem) > 0.0:
        take_mem = rng.random(idx.size) < float(max(0.0, min(1.0, p_mem)))
        if np.any(take_mem):
            d_prev = ((phase_old - phase_prev) % PHASE_COUNT).astype(np.int16)
            phase_new[take_mem] = ((phase_new[take_mem] + d_prev[take_mem]) % PHASE_COUNT).astype(np.int16)

    # w3 channel weighting: sample phase shift and apply on support voxels.
    probs = _build_w3_prob(float(w3))
    shifts = rng.choice(np.arange(PHASE_COUNT), size=idx.size, p=probs).astype(np.int16)
    phase_new = ((phase_new + shifts) % PHASE_COUNT).astype(np.int16)
    out[idx] = (phase_new.astype(np.int32) * int(qn) + q_part).astype(np.uint16)
    return out


def _run_point(
    *,
    global_seed: int,
    w3: float,
    p_mem: float,
    seed_count: int,
    ticks: int,
    warmup_ticks: int,
    size_x: int,
    size_y: int,
    size_z: int,
    stencil_id: str,
    boundary_mode: str,
    channel_policy_id: str,
) -> Dict[str, Any]:
    qmul = c12.build_qmul_table()
    mul = c12.build_mul_table(phase_count=PHASE_COUNT, qmul=qmul)
    qn = int(qmul.shape[0])
    vac_id = int(c12.s_identity_id())
    trials = _trial_bank_odd_lane(int(qn))
    policy_neighbors = psec._prepare_policy_neighbors(  # noqa: SLF001
        int(size_x), int(size_y), int(size_z), str(stencil_id), str(boundary_mode)
    )
    neighbors = policy_neighbors["all"]
    n_cells = int(size_x) * int(size_y) * int(size_z)

    r_mean_runs: List[float] = []
    r_std_runs: List[float] = []
    h_runs: List[float] = []
    r3_runs: List[float] = []
    gls_var_runs: List[float] = []
    a1_runs: List[float] = []
    a2_runs: List[float] = []

    for si in range(int(seed_count)):
        tr = trials[int(si % len(trials))]
        rr = np.random.default_rng(int(global_seed) + 10007 * (si + 1) + int(1000.0 * float(w3)) + int(10000.0 * float(p_mem)))
        world = np.full((n_cells,), np.uint16(vac_id), dtype=np.uint16)
        psec._apply_seed(  # noqa: SLF001
            world,
            int(size_x),
            int(size_y),
            int(size_z),
            family=str(tr["seed_family"]),
            state_id=int(tr["state_id"]),
            kick_id=int(tr["kick_id"]),
            mul=mul,
        )
        prev_world = world.copy()

        delta_counts = np.zeros((PHASE_COUNT,), dtype=np.int64)
        signed_p1 = signed_m1 = signed_p2 = signed_m2 = 0
        r_series: List[float] = []
        gls_series: List[float] = []

        for t in range(1, int(ticks) + 1):
            combo = psec._policy_combo(str(channel_policy_id), int(t), int(global_seed) + int(si))  # noqa: SLF001
            nb = policy_neighbors.get(combo, neighbors)
            new_world = _step_sync_biased(
                world,
                prev_world,
                nb,
                mul,
                vac_id=vac_id,
                w3=float(w3),
                p_mem=float(p_mem),
                rng=rr,
                qn=int(qn),
            )
            prev_world, world = world, new_world
            if t <= int(warmup_ticks):
                continue

            old_phase = (prev_world.astype(np.int32) // int(qn)).astype(np.int16)
            new_phase = (world.astype(np.int32) // int(qn)).astype(np.int16)
            d = ((new_phase - old_phase) % PHASE_COUNT).astype(np.int16)
            support = (prev_world != np.uint16(vac_id)) | (world != np.uint16(vac_id))
            if not bool(np.any(support)):
                continue

            d_sup = d[support]
            bc = np.bincount(d_sup.astype(np.int32), minlength=PHASE_COUNT)
            delta_counts += bc.astype(np.int64)

            signed = d_sup.copy()
            signed[signed > 6] -= 12
            signed_p1 += int(np.count_nonzero(signed == 1))
            signed_m1 += int(np.count_nonzero(signed == -1))
            signed_p2 += int(np.count_nonzero(signed == 2))
            signed_m2 += int(np.count_nonzero(signed == -2))

            phases_live = new_phase[support]
            r_series.append(_kuramoto_r(phases_live))
            g = (phases_live % 3).astype(np.int16)
            p = np.bincount(g.astype(np.int32), minlength=3).astype(np.float64)
            p /= float(np.sum(p))
            gls_series.append(float(np.max(np.abs(p - (1.0 / 3.0)))))

        mag_counts = {m: 0 for m in (0, 1, 2, 3, 4, 5, 6)}
        for d in range(PHASE_COUNT):
            m = int(min(d, PHASE_COUNT - d))
            mag_counts[m] = int(mag_counts.get(m, 0) + int(delta_counts[d]))
        num = float(mag_counts[3])
        den = float(mag_counts[1] + mag_counts[2] + mag_counts[4] + mag_counts[5] + mag_counts[6])
        r3_runs.append(_safe_div(num, den))
        r_arr = np.asarray(r_series, dtype=np.float64) if r_series else np.asarray([0.0], dtype=np.float64)
        r_mean_runs.append(float(np.mean(r_arr)))
        r_std_runs.append(float(np.std(r_arr)))
        h_runs.append(float(_spectral_entropy(r_series)))
        gls_var_runs.append(float(np.var(np.asarray(gls_series, dtype=np.float64))) if gls_series else 0.0)
        a1_runs.append(_safe_div(float(signed_p1 - signed_m1), float(signed_p1 + signed_m1)))
        a2_runs.append(_safe_div(float(signed_p2 - signed_m2), float(signed_p2 + signed_m2)))

    r3 = float(np.mean(np.asarray(r3_runs, dtype=np.float64))) if r3_runs else 0.0
    r_mean = float(np.mean(np.asarray(r_mean_runs, dtype=np.float64))) if r_mean_runs else 0.0
    r_std = float(np.mean(np.asarray(r_std_runs, dtype=np.float64))) if r_std_runs else 0.0
    h_spec = float(np.mean(np.asarray(h_runs, dtype=np.float64))) if h_runs else 1.0
    gls_var = float(np.mean(np.asarray(gls_var_runs, dtype=np.float64))) if gls_var_runs else 0.0
    a1 = float(np.mean(np.asarray(a1_runs, dtype=np.float64))) if a1_runs else 0.0
    a2 = float(np.mean(np.asarray(a2_runs, dtype=np.float64))) if a2_runs else 0.0
    phase_class = _phase_classification(r_mean=r_mean, r_std=r_std, r3=r3, h_spec=h_spec)

    return {
        "w3": float(w3),
        "p_mem": float(p_mem),
        "seed_count": int(seed_count),
        "R3": float(r3),
        "r_mean": float(r_mean),
        "r_std": float(r_std),
        "spectral_entropy": float(h_spec),
        "GLS_var": float(gls_var),
        "A1": float(a1),
        "A2": float(a2),
        "phase_class": str(phase_class),
    }


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# v3 Phase Boundary Sweep (v1)",
        "",
        f"- kernel_profile: `{payload['kernel_profile']}`",
        f"- convention_id: `{payload['convention_id']}`",
        f"- seed_count: `{payload['params']['seed_count']}`",
        f"- ticks: `{payload['params']['ticks']}`",
        "",
        "| w3 | p_mem | R3 | r_mean | r_std | spectral_entropy | GLS_var | A1 | A2 | phase_class |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in payload["rows"]:
        lines.append(
            f"| {float(r['w3']):.4g} | {float(r['p_mem']):.4g} | {float(r['R3']):.6f} | "
            f"{float(r['r_mean']):.6f} | {float(r['r_std']):.6f} | {float(r['spectral_entropy']):.6f} | "
            f"{float(r['GLS_var']):.6f} | {float(r['A1']):.6f} | {float(r['A2']):.6f} | `{r['phase_class']}` |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- `w3` is implemented as a phase-channel weighting on |Δp|=3 shifts (exploratory kernel-control lane).",
            "- `p_mem` is a memory-2 continuation bias using prior phase velocity (RFC-019 exploratory lane).",
            "- Use this sweep for phase-map detection, then re-validate candidates in canonical kernel lanes.",
        ]
    )
    return "\n".join(lines)


def build_payload(
    *,
    global_seed: int = 1337,
    seed_count: int = 5,
    ticks: int = 200,
    warmup_ticks: int = 30,
    size_x: int = 23,
    size_y: int = 9,
    size_z: int = 9,
    stencil_id: str = "cube26",
    boundary_mode: str = "fixed_vacuum",
    channel_policy_id: str = "uniform_all",
    w3_values: Sequence[float] = (0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0),
    p_mem_values: Sequence[float] = (0.0,),
) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    for p_mem in p_mem_values:
        for w3 in w3_values:
            rows.append(
                _run_point(
                    global_seed=int(global_seed),
                    w3=float(w3),
                    p_mem=float(p_mem),
                    seed_count=int(seed_count),
                    ticks=int(ticks),
                    warmup_ticks=int(warmup_ticks),
                    size_x=int(size_x),
                    size_y=int(size_y),
                    size_z=int(size_z),
                    stencil_id=str(stencil_id),
                    boundary_mode=str(boundary_mode),
                    channel_policy_id=str(channel_policy_id),
                )
            )

    payload: Dict[str, Any] = {
        "schema_version": "v3_phase_boundary_sweep_v1",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(ROOT / SCRIPT_REPO_PATH),
        "phase_metrics_script": PHASE_SCRIPT_REPO_PATH,
        "phase_metrics_script_sha256": _sha_file(ROOT / PHASE_SCRIPT_REPO_PATH),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(ROOT / KERNEL_REPO_PATH),
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "params": {
            "global_seed": int(global_seed),
            "seed_count": int(seed_count),
            "ticks": int(ticks),
            "warmup_ticks": int(warmup_ticks),
            "size_x": int(size_x),
            "size_y": int(size_y),
            "size_z": int(size_z),
            "stencil_id": str(stencil_id),
            "boundary_mode": str(boundary_mode),
            "channel_policy_id": str(channel_policy_id),
            "w3_values": [float(x) for x in w3_values],
            "p_mem_values": [float(x) for x in p_mem_values],
        },
        "rows": rows,
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def write_artifacts(payload: Dict[str, Any]) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_render_md(payload), encoding="utf-8")
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["w3", "p_mem", "R3", "r_mean", "r_std", "spectral_entropy", "GLS_var", "A1", "A2", "phase_class", "seed_count"],
        )
        w.writeheader()
        for row in payload["rows"]:
            w.writerow(row)


def main() -> int:
    ap = argparse.ArgumentParser(description="Run v3 phase-boundary sweep.")
    ap.add_argument("--global-seed", type=int, default=1337)
    ap.add_argument("--seed-count", type=int, default=5)
    ap.add_argument("--ticks", type=int, default=200)
    ap.add_argument("--warmup-ticks", type=int, default=30)
    ap.add_argument("--size-x", type=int, default=23)
    ap.add_argument("--size-y", type=int, default=9)
    ap.add_argument("--size-z", type=int, default=9)
    ap.add_argument("--stencil-id", type=str, default="cube26", choices=["axial6", "cube26"])
    ap.add_argument("--boundary-mode", type=str, default="fixed_vacuum", choices=["fixed_vacuum", "periodic"])
    ap.add_argument("--channel-policy-id", type=str, default="uniform_all")
    ap.add_argument("--w3-values", type=str, default="0.25,0.5,1,2,4,8,16,32")
    ap.add_argument("--p-mem-values", type=str, default="0.0")
    args = ap.parse_args()

    payload = build_payload(
        global_seed=int(args.global_seed),
        seed_count=int(args.seed_count),
        ticks=int(args.ticks),
        warmup_ticks=int(args.warmup_ticks),
        size_x=int(args.size_x),
        size_y=int(args.size_y),
        size_z=int(args.size_z),
        stencil_id=str(args.stencil_id),
        boundary_mode=str(args.boundary_mode),
        channel_policy_id=str(args.channel_policy_id),
        w3_values=_parse_float_list(str(args.w3_values)),
        p_mem_values=_parse_float_list(str(args.p_mem_values)),
    )
    write_artifacts(payload)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
