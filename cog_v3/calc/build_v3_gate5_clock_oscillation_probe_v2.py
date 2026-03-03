"""Gate-5 v2 probe: separate stable clock structure from coherent oscillation."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

from cog_v3.calc import build_v3_fixed_manifest_kernel_gate_stack_v1 as gate_stack
from cog_v3.calc import run_v3_overnight_autonomous_v1 as runner
from cog_v3.python import kernel_octavian240_accel_v1 as accel
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]

IN_GATE_STACK_JSON = ROOT / "cog_v3" / "sources" / "v3_fixed_manifest_kernel_gate_stack_v1.json"
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_gate5_clock_oscillation_probe_v2.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_gate5_clock_oscillation_probe_v2.md"

SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_gate5_clock_oscillation_probe_v2.py"
GATE_STACK_SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_fixed_manifest_kernel_gate_stack_v1.py"
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


def _load_or_build_manifest(*, backend: str, global_seed: int, quick: bool, refresh: bool) -> Dict[str, Any]:
    if bool(refresh) or (not IN_GATE_STACK_JSON.exists()):
        payload = gate_stack.build_payload(backend=str(backend), global_seed=int(global_seed), quick=bool(quick))
        gate_stack.write_artifacts(payload)
        return payload
    return json.loads(IN_GATE_STACK_JSON.read_text(encoding="utf-8"))


def _clock_trace(
    *,
    backend: str,
    channel_policy_id: str,
    policy_seed: int,
    ticks: int,
    warmup_ticks: int,
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
    classes = [1, 2, 3, 4, 6, 12]
    class_idx = {v: i for i, v in enumerate(classes)}
    rows: List[List[float]] = []
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
                o = int(order_map.get(int(sid), 1))
                if o in class_idx:
                    vec[class_idx[o]] += 1.0
            vec /= float(np.sum(vec)) if float(np.sum(vec)) > 0 else 1.0
        rows.append([float(x) for x in vec.tolist()])

    arr = np.asarray(rows, dtype=np.float64)
    if arr.shape[0] < 4:
        arr = np.vstack([arr, np.zeros((4 - arr.shape[0], arr.shape[1]), dtype=np.float64)])

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
    hmax = math.log(arr.shape[1])
    noise_plateau_flag = bool(np.mean(np.asarray(entropy) / max(1e-12, hmax) > 0.95) > 0.8)

    return {
        "clock_classes": classes,
        "clock_signature_series": arr.tolist(),
        "clock_signature_drift": float(drift),
        "clock_collapse_flag": bool(collapse_flag),
        "clock_noise_plateau_flag": bool(noise_plateau_flag),
        "first_repeat": first_repeat,
    }


def _spectral_features(series: np.ndarray) -> Dict[str, Any]:
    # Use principal dynamic mode (PC1) so flat single-channel traces do not hide oscillation.
    if series.ndim != 2 or series.shape[0] < 8:
        return {
            "dominant_period_ticks": None,
            "spectral_peak_ratio": 0.0,
            "spectral_peak_index": None,
            "oscillation_amplitude": 0.0,
        }
    x = series.astype(np.float64)
    x = x - np.mean(x, axis=0, keepdims=True)
    try:
        _, _, vt = np.linalg.svd(x, full_matrices=False)
        mode = vt[0, :]
        y = np.dot(x, mode)
    except np.linalg.LinAlgError:
        y = x[:, -1]
    y = y.astype(np.float64)
    amp = float(np.std(y))
    if not np.any(np.abs(y) > 1e-12):
        return {
            "dominant_period_ticks": None,
            "spectral_peak_ratio": 0.0,
            "spectral_peak_index": None,
            "oscillation_amplitude": float(amp),
        }

    fft = np.fft.rfft(y)
    pw = (fft.real * fft.real + fft.imag * fft.imag).astype(np.float64)
    if pw.shape[0] <= 1:
        return {
            "dominant_period_ticks": None,
            "spectral_peak_ratio": 0.0,
            "spectral_peak_index": None,
            "oscillation_amplitude": float(amp),
        }
    pw0 = pw.copy()
    pw0[0] = 0.0
    k_idx = int(np.argmax(pw0))
    peak = float(pw0[k_idx])
    tot = float(np.sum(pw0))
    ratio = float(peak / max(1e-12, tot))
    period = float(series.shape[0] / k_idx) if k_idx > 0 else None
    return {
        "dominant_period_ticks": float(period) if period is not None else None,
        "spectral_peak_ratio": float(ratio),
        "spectral_peak_index": int(k_idx) if k_idx > 0 else None,
        "oscillation_amplitude": float(amp),
    }


def _classify(trace: Dict[str, Any], spec: Dict[str, Any]) -> str:
    repeat = trace.get("first_repeat")
    drift = float(trace["clock_signature_drift"])
    collapse = bool(trace["clock_collapse_flag"])
    noise = bool(trace["clock_noise_plateau_flag"])
    peak_ratio = float(spec["spectral_peak_ratio"])
    amp = float(spec["oscillation_amplitude"])

    if repeat is not None and drift <= 0.35 and (not collapse) and (not noise):
        return "stable_in_sector"
    if (
        repeat is None
        and (not collapse)
        and (not noise)
        and drift <= 0.45
        and peak_ratio >= 0.35
        and amp >= 0.01
    ):
        return "coherent_oscillatory"
    return "diffusive_or_decay"


def _median(vals: List[float]) -> float:
    if not vals:
        return 0.0
    v = sorted(float(x) for x in vals)
    return float(v[len(v) // 2])


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# v3 Gate-5 Clock Oscillation Probe (v2)",
        "",
        f"- kernel_profile: `{payload['kernel_profile']}`",
        f"- convention_id: `{payload['convention_id']}`",
        f"- backend: `{payload['backend']}`",
        "",
        "| kernel_candidate_id | channel_policy_id | stable_count | oscillatory_count | diffusive_count | median_peak_ratio | median_period |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for r in payload["candidate_summary"]:
        lines.append(
            f"| `{r['kernel_candidate_id']}` | `{r['channel_policy_id']}` | {int(r['stable_in_sector_count'])} | "
            f"{int(r['coherent_oscillatory_count'])} | {int(r['diffusive_or_decay_count'])} | "
            f"{float(r['median_peak_ratio']):.4f} | {float(r['median_period']):.2f} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- `coherent_oscillatory` requires spectral peak evidence, not just gate-5 failure.",
            "- This is a diagnostic classifier, not a particle identification claim.",
        ]
    )
    return "\n".join(lines)


def build_payload(
    *,
    backend: str = "numba_cpu",
    global_seed: int = 1337,
    quick: bool = False,
    refresh_manifest: bool = False,
) -> Dict[str, Any]:
    manifest = _load_or_build_manifest(
        backend=str(backend),
        global_seed=int(global_seed),
        quick=bool(quick),
        refresh=bool(refresh_manifest),
    )
    if str(manifest.get("schema_version", "")) != "v3_fixed_manifest_kernel_gate_stack_v1":
        raise ValueError("Unexpected gate-stack schema.")

    horizons = [96, 160] if bool(quick) else [128, 256]
    seeds_per_h = 2 if bool(quick) else 4
    candidate_rows: List[Dict[str, Any]] = []
    candidate_summary: List[Dict[str, Any]] = []

    for ci, row in enumerate(manifest.get("rows", [])):
        rid = str(row["kernel_candidate_id"])
        ch = str(row["channel_policy_id"])
        runs: List[Dict[str, Any]] = []
        for h in horizons:
            for s in range(seeds_per_h):
                policy_seed = int(global_seed) + 15013 * (ci + 1) + 97 * h + 19 * s
                warmup = max(8, int(h) // 6)
                trace = _clock_trace(
                    backend=str(backend),
                    channel_policy_id=ch,
                    policy_seed=int(policy_seed),
                    ticks=int(h),
                    warmup_ticks=int(warmup),
                )
                series = np.asarray(trace["clock_signature_series"], dtype=np.float64)
                spec = _spectral_features(series)
                cls = _classify(trace, spec)
                runs.append(
                    {
                        "kernel_candidate_id": rid,
                        "channel_policy_id": ch,
                        "horizon_ticks": int(h),
                        "seed_idx": int(s),
                        "policy_seed": int(policy_seed),
                        "warmup_ticks": int(warmup),
                        "first_repeat": trace["first_repeat"],
                        "clock_signature_drift": float(trace["clock_signature_drift"]),
                        "clock_collapse_flag": bool(trace["clock_collapse_flag"]),
                        "clock_noise_plateau_flag": bool(trace["clock_noise_plateau_flag"]),
                        "dominant_period_ticks": spec["dominant_period_ticks"],
                        "spectral_peak_ratio": float(spec["spectral_peak_ratio"]),
                        "oscillation_amplitude": float(spec["oscillation_amplitude"]),
                        "classification": str(cls),
                    }
                )
        candidate_rows.extend(runs)

        stable = [r for r in runs if r["classification"] == "stable_in_sector"]
        osc = [r for r in runs if r["classification"] == "coherent_oscillatory"]
        diff = [r for r in runs if r["classification"] == "diffusive_or_decay"]
        peaks = [float(r["spectral_peak_ratio"]) for r in runs]
        periods = [float(r["dominant_period_ticks"]) for r in runs if isinstance(r["dominant_period_ticks"], (int, float))]
        candidate_summary.append(
            {
                "kernel_candidate_id": rid,
                "channel_policy_id": ch,
                "run_count": int(len(runs)),
                "stable_in_sector_count": int(len(stable)),
                "coherent_oscillatory_count": int(len(osc)),
                "diffusive_or_decay_count": int(len(diff)),
                "median_peak_ratio": float(_median(peaks)),
                "median_period": float(_median(periods)) if periods else 0.0,
            }
        )

    payload: Dict[str, Any] = {
        "schema_version": "v3_gate5_clock_oscillation_probe_v2",
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "backend": str(backend),
        "global_seed": int(global_seed),
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(ROOT / SCRIPT_REPO_PATH),
        "gate_stack_script": GATE_STACK_SCRIPT_REPO_PATH,
        "gate_stack_script_sha256": _sha_file(ROOT / GATE_STACK_SCRIPT_REPO_PATH),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(ROOT / KERNEL_REPO_PATH),
        "horizons": [int(x) for x in horizons],
        "seeds_per_horizon": int(seeds_per_h),
        "candidate_summary": candidate_summary,
        "candidate_rows": candidate_rows,
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def write_artifacts(payload: Dict[str, Any]) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_render_md(payload), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", type=str, default="numba_cpu", choices=["python", "numba_cpu"])
    parser.add_argument("--global-seed", type=int, default=1337)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--refresh-manifest", action="store_true")
    args = parser.parse_args()

    payload = build_payload(
        backend=str(args.backend),
        global_seed=int(args.global_seed),
        quick=bool(args.quick),
        refresh_manifest=bool(args.refresh_manifest),
    )
    write_artifacts(payload)
    print(
        "v3_gate5_clock_oscillation_probe_v2: "
        f"candidates={len(payload['candidate_summary'])}, "
        f"rows={len(payload['candidate_rows'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
