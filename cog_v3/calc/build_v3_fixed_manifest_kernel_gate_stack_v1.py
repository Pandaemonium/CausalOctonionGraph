"""Run fixed-manifest kernel gate stack across K0/K1/K2 candidates."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

from cog_v3.calc import run_v3_overnight_autonomous_v1 as runner
from cog_v3.python import kernel_octavian240_accel_v1 as accel
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_fixed_manifest_kernel_gate_stack_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_fixed_manifest_kernel_gate_stack_v1.md"
OUT_CSV = ROOT / "cog_v3" / "sources" / "v3_fixed_manifest_kernel_gate_stack_v1.csv"

SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_fixed_manifest_kernel_gate_stack_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"
ORDER_CSV = ROOT / "cog_v3" / "sources" / "v3_octavian240_elements_v1.csv"


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _load_order_map() -> Dict[int, int]:
    out: Dict[int, int] = {}
    with ORDER_CSV.open("r", newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            out[int(row["id"])] = int(row["order"])
    return out


def _clock_signature_probe(
    *,
    backend: str,
    channel_policy_id: str,
    policy_seed: int,
    ticks: int = 96,
    warmup_ticks: int = 16,
) -> Dict[str, Any]:
    nx, ny, nz = 21, 21, 21
    offsets = accel.offsets_for_stencil("cube26")
    neighbors = accel.build_neighbor_table(nx, ny, nz, offsets)
    policy_tables = runner._prepare_policy_neighbor_tables(nx, ny, nz, "cube26")  # noqa: SLF001
    mul_table = accel.build_mul_table()

    world = accel.make_world(nx, ny, nz, seed_state_id=None)
    world_l = [int(x) for x in world.tolist()]
    e111 = runner._basis_id(7, +1)  # noqa: SLF001
    e001 = runner._basis_id(1, +1)  # noqa: SLF001
    runner._apply_blob3(world_l, nx, ny, nz, state_id=e111, kick_id=e001)  # noqa: SLF001
    world = np.asarray(world_l, dtype=np.uint16)

    order_map = _load_order_map()
    classes = [1, 2, 3, 4, 6]
    class_idx = {v: i for i, v in enumerate(classes)}
    sig_rows: List[List[float]] = []
    seen: Dict[int, int] = {}
    first_repeat = None

    for t in range(1, int(ticks) + 1):
        combo = runner._policy_combo(str(channel_policy_id), int(t), int(policy_seed))  # noqa: SLF001
        nb = policy_tables.get(combo, neighbors)
        if backend == "python":
            world = accel.step_python(world, nb, mul_table, vac_id=k.IDENTITY_ID, identity_id=k.IDENTITY_ID)
        else:
            world = accel.step_numba_cpu(world, nb, mul_table, vac_id=k.IDENTITY_ID, identity_id=k.IDENTITY_ID)

        if t < int(warmup_ticks):
            continue

        h = hash(world.tobytes())
        if first_repeat is None:
            prev = seen.get(int(h))
            if prev is not None:
                first_repeat = {"t_prev": int(prev), "t_now": int(t), "period": int(t - prev)}
            else:
                seen[int(h)] = int(t)

        ids = world[world != np.uint16(k.IDENTITY_ID)].astype(np.int32)
        vec = np.zeros((len(classes),), dtype=np.float64)
        if ids.size > 0:
            for sid in ids.tolist():
                order = int(order_map.get(int(sid), 1))
                if order in class_idx:
                    vec[class_idx[order]] += 1.0
            vec /= float(np.sum(vec)) if float(np.sum(vec)) > 0 else 1.0
        sig_rows.append([float(x) for x in vec.tolist()])

    if not sig_rows:
        sig_rows = [[0.0 for _ in classes]]

    arr = np.asarray(sig_rows, dtype=np.float64)
    if arr.shape[0] >= 2:
        drift = float(np.mean(np.sum(np.abs(arr[1:, :] - arr[:-1, :]), axis=1)))
    else:
        drift = 0.0
    max_share = np.max(arr, axis=1)
    collapse_flag = bool(np.mean(max_share >= 0.98) > 0.8)

    entropy = []
    for r in arr:
        p = np.clip(r, 1e-12, 1.0)
        p /= np.sum(p)
        h = -float(np.sum(p * np.log(p)))
        entropy.append(h)
    hmax = math.log(len(classes))
    noise_plateau_flag = bool(np.mean(np.asarray(entropy) / max(1e-12, hmax) > 0.95) > 0.8)

    quality = float(max(0.0, 1.0 - drift)) * (0.0 if collapse_flag else 1.0) * (0.0 if noise_plateau_flag else 1.0)
    return {
        "clock_signature_series": sig_rows[:: max(1, len(sig_rows) // 24)],
        "clock_signature_drift": float(drift),
        "clock_collapse_flag": bool(collapse_flag),
        "clock_noise_plateau_flag": bool(noise_plateau_flag),
        "clock_quality": float(quality),
        "first_repeat": first_repeat,
    }


def _lorentz_battery(
    *,
    backend: str,
    channel_policy_id: str,
    policy_seed: int,
    mul_table: np.ndarray,
    neighbors_ref: np.ndarray,
    sizes: List[int] | None = None,
) -> Dict[str, Any]:
    e111 = runner._basis_id(7, +1)  # noqa: SLF001
    e001 = runner._basis_id(1, +1)  # noqa: SLF001
    e010 = runner._basis_id(2, +1)  # noqa: SLF001
    e100 = runner._basis_id(4, +1)  # noqa: SLF001

    size_list = list(sizes) if sizes is not None else [17, 21, 25]
    axis_cfg = [("x", e001), ("y", e010), ("z", e100)]
    rows = []
    slopes: Dict[str, float] = {}
    residuals: Dict[str, float] = {}

    for axis, kick in axis_cfg:
        dvals: List[float] = []
        tvals: List[float] = []
        for n in size_list:
            pr = runner.run_twin_detector_probe(
                runner.ProbeParams(
                    runs=10,
                    ticks=90,
                    size_x=int(n),
                    size_y=int(n),
                    size_z=int(n),
                    vacuum_noise_prob=0.002,
                    detector_margin=2,
                    seed_state_id=e111,
                    kick_id=int(kick),
                    global_seed=1337 + int(n) * 13,
                    axis=str(axis),
                    channel_policy_id=str(channel_policy_id),
                    policy_seed=int(policy_seed),
                ),
                backend=backend,
                neighbors=neighbors_ref,
                mul_table=mul_table,
            )
            arr = pr.get("mean_first_arrival_tick")
            dist = int(n // 2 - 2 - 1)
            if isinstance(arr, (int, float)) and float(arr) > 0:
                dvals.append(float(dist))
                tvals.append(float(arr))
            rows.append(
                {
                    "axis": str(axis),
                    "size": int(n),
                    "distance": int(dist),
                    "arrival": float(arr) if isinstance(arr, (int, float)) else None,
                    "detector_exclusivity": float(pr["detector_exclusivity"]),
                }
            )
        if len(dvals) >= 2:
            coef = np.polyfit(np.asarray(dvals), np.asarray(tvals), deg=1)
            pred = np.polyval(coef, np.asarray(dvals))
            rmse = float(np.sqrt(np.mean((pred - np.asarray(tvals)) ** 2)))
            slopes[str(axis)] = float(coef[0])
            residuals[str(axis)] = float(rmse)

    slope_vals = [float(v) for v in slopes.values() if float(v) > 0]
    if len(slope_vals) >= 2:
        spread = float(max(slope_vals) / min(slope_vals) - 1.0)
    else:
        spread = 999.0

    return {
        "lorentz_distance_set": size_list,
        "lorentz_fit_slope_by_direction": slopes,
        "lorentz_fit_residual_summary": residuals,
        "lorentz_front_tensor_eigen_spread": float(spread),
        "lorentz_scale_comparison": rows,
    }


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# v3 Fixed-Manifest Kernel Gate Stack (v1)",
        "",
        f"- kernel_profile: `{payload['kernel_profile']}`",
        f"- convention_id: `{payload['convention_id']}`",
        "",
        "| rank | kernel_candidate_id | channel_policy_id | gates_passed | score_total | gate0 | gate1 | gate2 | gate3 | gate4 | gate5 |",
        "|---:|---|---|---:|---:|---|---|---|---|---|---|",
    ]
    for i, r in enumerate(payload["rows"], start=1):
        g = r["gate_results"]
        gp = sum(1 for v in g.values() if bool(v))
        lines.append(
            f"| {i} | `{r['kernel_candidate_id']}` | `{r['channel_policy_id']}` | {int(gp)} | {float(r['score_total']):.6f} | "
            f"{g['gate0_contract']} | {g['gate1_transport']} | {g['gate2_detector']} | {g['gate3_isotropy_lorentz']} | {g['gate4_chirality']} | {g['gate5_clock_structure']} |"
        )
    return "\n".join(lines)


def build_payload(*, backend: str = "numba_cpu", global_seed: int = 1337, quick: bool = False) -> Dict[str, Any]:
    candidate_defs = [
        {"kernel_candidate_id": "K0_cube26_uniform_v1", "channel_policy_id": "uniform_all", "stencil_id": "cube26"},
        {"kernel_candidate_id": "K1_cube26_det_cycle_v1", "channel_policy_id": "deterministic_cycle_v1", "stencil_id": "cube26"},
        {"kernel_candidate_id": "K2_cube26_stochastic_v1", "channel_policy_id": "stochastic_gating_v1", "stencil_id": "cube26"},
    ]
    scan_manifest = runner.FastScanParams(
        ticks=72,
        size_x=27,
        size_y=9,
        size_z=9,
        stencil_id="cube26",
        thin_step=4,
        max_trials=8,
        global_seed=int(global_seed),
        channel_policy_id="uniform_all",
        policy_seed=int(global_seed + 1009),
    )
    probe_manifest = runner.ProbeParams(
        runs=18,
        ticks=96,
        size_x=21,
        size_y=21,
        size_z=21,
        vacuum_noise_prob=0.002,
        detector_margin=2,
        seed_state_id=runner._basis_id(7, +1),  # noqa: SLF001
        kick_id=runner._basis_id(1, +1),  # noqa: SLF001
        global_seed=int(global_seed),
        axis="x",
        channel_policy_id="uniform_all",
        policy_seed=int(global_seed + 2003),
    )

    if bool(quick):
        scan_manifest = runner.FastScanParams(
            **{
                **asdict(scan_manifest),
                "ticks": 36,
                "size_x": 19,
                "size_y": 9,
                "size_z": 9,
                "max_trials": 3,
            }
        )
        probe_manifest = runner.ProbeParams(
            **{
                **asdict(probe_manifest),
                "runs": 6,
                "ticks": 56,
                "size_x": 17,
                "size_y": 17,
                "size_z": 17,
            }
        )

    mul_table = accel.build_mul_table()
    neighbors_ref = accel.build_neighbor_table(3, 3, 3, accel.offsets_for_stencil("axial6"))
    rows: List[Dict[str, Any]] = []

    for ci, cand in enumerate(candidate_defs):
        scan_cfg = runner.FastScanParams(
            **{
                **asdict(scan_manifest),
                "channel_policy_id": str(cand["channel_policy_id"]),
                "policy_seed": int(global_seed + 4099 + ci * 17),
                "global_seed": int(global_seed + 5003 + ci * 17),
            }
        )
        probe_cfg = runner.ProbeParams(
            **{
                **asdict(probe_manifest),
                "channel_policy_id": str(cand["channel_policy_id"]),
                "policy_seed": int(global_seed + 7001 + ci * 17),
                "global_seed": int(global_seed + 8009 + ci * 17),
            }
        )

        scan_payload = runner.run_fast_motif_scan(scan_cfg, backend=str(backend))
        scan_score = float(runner._score_scan_payload(scan_payload))  # noqa: SLF001
        best = runner._extract_best_candidate(scan_payload)  # noqa: SLF001
        probe = runner.run_twin_detector_probe(probe_cfg, backend=str(backend), neighbors=neighbors_ref, mul_table=mul_table)
        isotropy = runner.run_isotropy_probe(
            base_probe=probe_cfg,
            backend=str(backend),
            neighbors=neighbors_ref,
            mul_table=mul_table,
        )
        lorentz = _lorentz_battery(
            backend=str(backend),
            channel_policy_id=str(cand["channel_policy_id"]),
            policy_seed=int(global_seed + 9001 + ci * 17),
            mul_table=mul_table,
            neighbors_ref=neighbors_ref,
            sizes=([13, 17] if bool(quick) else None),
        )
        clock_metrics = _clock_signature_probe(
            backend=str(backend),
            channel_policy_id=str(cand["channel_policy_id"]),
            policy_seed=int(global_seed + 10007 + ci * 17),
            ticks=(40 if bool(quick) else 96),
            warmup_ticks=(8 if bool(quick) else 16),
        )

        left = float(probe["left_hit_fraction"])
        right = float(probe["right_hit_fraction"])
        denom = max(1e-12, left + right)
        a_chi = float((left - right) / denom)
        a_c = float(1.0 - float(probe["detector_exclusivity"]))
        aniso = isotropy.get("anisotropy_ratio_max_over_min")
        aniso_val = float(aniso) if isinstance(aniso, (int, float)) else 999.0
        lor_spread = float(lorentz.get("lorentz_front_tensor_eigen_spread", 999.0))

        gate0 = True
        gate1 = bool(scan_payload.get("checks", {}).get("any_propagating") or scan_payload.get("checks", {}).get("any_recurrence"))
        gate2 = bool(float(probe["detector_exclusivity"]) >= 0.2)
        gate3 = bool(aniso_val <= 2.0 and lor_spread <= 0.5)
        gate4 = bool(abs(a_chi) >= 0.05)
        gate5 = bool(
            float(clock_metrics["clock_signature_drift"]) <= 0.35
            and (not bool(clock_metrics["clock_collapse_flag"]))
            and (not bool(clock_metrics["clock_noise_plateau_flag"]))
            and bool(scan_payload.get("checks", {}).get("any_recurrence"))
        )

        score_total = (
            0.20 * scan_score
            + 0.20 * float(probe["detector_exclusivity"])
            + 0.20 * float(1.0 / max(1.0, aniso_val))
            + 0.10 * float(1.0 / max(1.0, 1.0 + lor_spread))
            + 0.10 * float(abs(a_chi))
            + 0.10 * float(clock_metrics["clock_quality"])
            + 0.10 * float(gate1)
        )

        rows.append(
            {
                "kernel_candidate_id": str(cand["kernel_candidate_id"]),
                "channel_policy_id": str(cand["channel_policy_id"]),
                "stencil_id": str(cand["stencil_id"]),
                "scan_manifest": asdict(scan_cfg),
                "probe_manifest": asdict(probe_cfg),
                "best_candidate": best,
                "scan_checks": scan_payload.get("checks", {}),
                "scan_score": float(scan_score),
                "photon_probe": probe,
                "anisotropy_metrics": isotropy,
                "A_chi": float(a_chi),
                "A_C": float(a_c),
                "lorentz_metrics": lorentz,
                "clock_metrics": clock_metrics,
                "gate_results": {
                    "gate0_contract": bool(gate0),
                    "gate1_transport": bool(gate1),
                    "gate2_detector": bool(gate2),
                    "gate3_isotropy_lorentz": bool(gate3),
                    "gate4_chirality": bool(gate4),
                    "gate5_clock_structure": bool(gate5),
                },
                "score_total": float(score_total),
            }
        )

    rows = sorted(
        rows,
        key=lambda r: (
            sum(1 for v in r["gate_results"].values() if bool(v)),
            float(r["score_total"]),
        ),
        reverse=True,
    )
    payload: Dict[str, Any] = {
        "schema_version": "v3_fixed_manifest_kernel_gate_stack_v1",
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "event_order_policy": "synchronous_parallel_v1",
        "backend": str(backend),
        "global_seed": int(global_seed),
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(ROOT / SCRIPT_REPO_PATH),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(ROOT / KERNEL_REPO_PATH),
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
                "kernel_candidate_id",
                "channel_policy_id",
                "score_total",
                "gate0",
                "gate1",
                "gate2",
                "gate3",
                "gate4",
                "gate5",
                "detector_exclusivity",
                "anisotropy_ratio",
                "lorentz_spread",
                "A_chi",
                "clock_signature_drift",
                "clock_collapse_flag",
                "clock_noise_plateau_flag",
            ]
        )
        for r in payload["rows"]:
            g = r["gate_results"]
            aniso = r["anisotropy_metrics"].get("anisotropy_ratio_max_over_min")
            lor = r["lorentz_metrics"].get("lorentz_front_tensor_eigen_spread")
            cm = r["clock_metrics"]
            w.writerow(
                [
                    str(r["kernel_candidate_id"]),
                    str(r["channel_policy_id"]),
                    float(r["score_total"]),
                    bool(g["gate0_contract"]),
                    bool(g["gate1_transport"]),
                    bool(g["gate2_detector"]),
                    bool(g["gate3_isotropy_lorentz"]),
                    bool(g["gate4_chirality"]),
                    bool(g["gate5_clock_structure"]),
                    float(r["photon_probe"]["detector_exclusivity"]),
                    float(aniso) if isinstance(aniso, (int, float)) else "",
                    float(lor) if isinstance(lor, (int, float)) else "",
                    float(r["A_chi"]),
                    float(cm["clock_signature_drift"]),
                    bool(cm["clock_collapse_flag"]),
                    bool(cm["clock_noise_plateau_flag"]),
                ]
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", type=str, default="numba_cpu", choices=["python", "numba_cpu"])
    parser.add_argument("--global-seed", type=int, default=1337)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    payload = build_payload(backend=str(args.backend), global_seed=int(args.global_seed), quick=bool(args.quick))
    write_artifacts(payload)
    top = payload["rows"][0] if payload["rows"] else {}
    print(
        "v3_fixed_manifest_kernel_gate_stack_v1: "
        f"rows={len(payload['rows'])}, "
        f"top={top.get('kernel_candidate_id')}, "
        f"score={float(top.get('score_total', 0.0)):.6f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
