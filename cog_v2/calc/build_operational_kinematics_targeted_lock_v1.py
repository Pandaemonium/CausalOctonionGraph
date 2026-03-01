"""Targeted lock campaign for operational kinematics/mass/kinetic estimators (v1).

Strategy:
1) read prior operational suite artifact,
2) select shape-robust particle/energy lanes,
3) rerun those lanes with longer horizon,
4) detect transient ablation and post-transient cycle stability.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Any, Dict, List, Sequence, Tuple

from calc.xor_scenario_loader import canonical_motif_state_map
from cog_v2.calc.build_operational_kinematics_mass_energy_v1 import (
    KERNEL_REPO_PATH,
    MeasureParams,
    SCRIPT_REPO_PATH as BASE_SCRIPT_REPO_PATH,
    _build_fold_orders,
    _default_bands,
    _default_profiles,
    _simulate_case,
    _to_cxo,
)
from cog_v2.python import kernel_projective_unity as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "operational_kinematics_targeted_lock_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "operational_kinematics_targeted_lock_v1.md"
SCRIPT_REPO_PATH = "cog_v2/calc/build_operational_kinematics_targeted_lock_v1.py"
PREV_SUITE_JSON = ROOT / "cog_v2" / "sources" / "operational_kinematics_mass_energy_v1.json"


@dataclass(frozen=True)
class TargetedLockParams:
    ticks: int = 220
    burn_in_ticks: int = 56
    measure_ticks: int = 120
    min_burn_ticks_for_stabilization: int = 48
    stabilization_window: int = 18
    stabilization_confirm_windows: int = 3
    stabilization_velocity_tol: float = 0.02
    stabilization_e000_tol: float = 0.02
    period_min: int = 2
    period_max: int = 24
    cycle_error_tol: float = 0.02
    min_stable_cycles: int = 4
    post_transient_fold_span_tol: float = 0.08
    post_transient_profile_gap_tol: float = 0.35
    fallback_targets: Tuple[Tuple[str, str], ...] = (
        ("left_spinor_muon_motif", "E2_center_plus_shell1"),
        ("left_spinor_tau_motif", "E2_center_plus_shell1"),
    )


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _mean(xs: Sequence[float]) -> float:
    return float(sum(float(x) for x in xs) / float(len(xs))) if xs else 0.0


def _window_means(trace: Sequence[float], *, start: int, window: int, count: int) -> List[float]:
    out: List[float] = []
    for j in range(int(count)):
        a = int(start + j * window)
        b = int(a + window)
        if b > len(trace):
            return []
        out.append(_mean(trace[a:b]))
    return out


def _find_transient_end(
    velocity_trace: Sequence[float],
    e000_trace: Sequence[float],
    *,
    min_burn: int,
    window: int,
    confirm_windows: int,
    vel_tol: float,
    e000_tol: float,
) -> int | None:
    t_max = min(len(velocity_trace), len(e000_trace))
    need = int(window * confirm_windows)
    if t_max <= int(min_burn) + need:
        return None
    for t0 in range(int(min_burn), int(t_max - need + 1)):
        vms = _window_means(velocity_trace, start=t0, window=window, count=confirm_windows)
        ems = _window_means(e000_trace, start=t0, window=window, count=confirm_windows)
        if not vms or not ems:
            continue
        if (max(vms) - min(vms) <= float(vel_tol)) and (max(ems) - min(ems) <= float(e000_tol)):
            return int(t0)
    return None


def _estimate_period(
    velocity_trace: Sequence[float],
    *,
    start: int,
    period_min: int,
    period_max: int,
    error_tol: float,
) -> Tuple[int | None, float | None]:
    tail = [float(v) for v in velocity_trace[int(start) :]]
    n = len(tail)
    best_p: int | None = None
    best_err: float | None = None
    for p in range(int(period_min), int(period_max) + 1):
        if n <= p + 2:
            continue
        errs = [abs(tail[i] - tail[i + p]) for i in range(0, n - p)]
        err = _mean(errs)
        if best_err is None or err < best_err:
            best_err = float(err)
            best_p = int(p)
    if best_p is None or best_err is None:
        return None, None
    if best_err > float(error_tol):
        return None, float(best_err)
    return int(best_p), float(best_err)


def _count_stable_cycles(
    velocity_trace: Sequence[float],
    *,
    start: int,
    period: int,
    error_tol: float,
) -> int:
    tail = [float(v) for v in velocity_trace[int(start) :]]
    n = len(tail)
    if period <= 0 or n <= period:
        return 0
    cycles = (n // period) - 1
    if cycles <= 0:
        return 0
    good = 0
    for c in range(cycles):
        a0 = int(c * period)
        a1 = int(a0 + period)
        b0 = int((c + 1) * period)
        b1 = int(b0 + period)
        seg_a = tail[a0:a1]
        seg_b = tail[b0:b1]
        if len(seg_a) != period or len(seg_b) != period:
            break
        err = _mean([abs(x - y) for x, y in zip(seg_a, seg_b)])
        if err <= float(error_tol):
            good += 1
        else:
            break
    return int(good)


def _load_previous_payload(path: Path = PREV_SUITE_JSON) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"previous suite artifact not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _select_targets(prev: Dict[str, Any], fallback: Sequence[Tuple[str, str]]) -> List[Tuple[str, str]]:
    robust = [
        (str(r["particle_id"]), str(r["energy_id"]))
        for r in prev.get("shape_comparisons", [])
        if bool(r.get("shape_robust", False))
    ]
    if robust:
        return sorted(list(set(robust)))
    return sorted(list(set((str(p), str(e)) for p, e in fallback)))


def _lookup_selected_op(prev: Dict[str, Any], particle_id: str, profile_id: str, energy_id: str) -> int | None:
    for prow in prev.get("particles", []):
        if str(prow.get("particle_id")) != str(particle_id):
            continue
        for pr in prow.get("profiles", []):
            if str(pr.get("profile_id")) != str(profile_id):
                continue
            for er in pr.get("energies", []):
                if str(er.get("energy_id")) != str(energy_id):
                    continue
                v = er.get("selected_op_idx")
                if v is None:
                    return None
                return int(v)
    return None


def build_payload(params: TargetedLockParams | None = None) -> Dict[str, Any]:
    p = params if params is not None else TargetedLockParams()
    prev = _load_previous_payload()
    targets = _select_targets(prev, p.fallback_targets)

    motifs = canonical_motif_state_map()
    vacuum_state = _to_cxo(motifs["su_vacuum_omega"])
    bands = {b.energy_id: b for b in _default_bands()}
    folds = _build_fold_orders()
    profiles = _default_profiles()

    sim_params = MeasureParams(
        ticks=int(p.ticks),
        burn_in_ticks=int(p.burn_in_ticks),
        measure_ticks=int(p.measure_ticks),
        kick_ops=(1,),
        particle_ids=tuple(),
        velocity_span_tol=0.25,
        delta_velocity_span_tol=0.25,
    )

    target_rows: List[Dict[str, Any]] = []
    for particle_id, energy_id in targets:
        if particle_id not in motifs:
            continue
        if energy_id not in bands:
            continue
        particle_state = _to_cxo(motifs[particle_id])
        band = bands[energy_id]
        run_rows: List[Dict[str, Any]] = []

        for profile in profiles:
            op_idx = _lookup_selected_op(prev, particle_id, profile.profile_id, energy_id)
            if op_idx is None:
                # conservative fallback: do not guess op from scratch in lock lane
                continue
            for fold in folds:
                sim = _simulate_case(
                    params=sim_params,
                    profile=profile,
                    fold=fold,
                    particle_state=particle_state,
                    vacuum_state=vacuum_state,
                    band=band,
                    op_idx=int(op_idx),
                )
                vtrace = [float(x) for x in sim["traces"]["velocity_x"]]
                etrace = [float(x) for x in sim["traces"]["e000_share"]]
                t_end = _find_transient_end(
                    vtrace,
                    etrace,
                    min_burn=int(p.min_burn_ticks_for_stabilization),
                    window=int(p.stabilization_window),
                    confirm_windows=int(p.stabilization_confirm_windows),
                    vel_tol=float(p.stabilization_velocity_tol),
                    e000_tol=float(p.stabilization_e000_tol),
                )
                period_est: int | None = None
                period_err: float | None = None
                stable_cycles = 0
                tail_v_mean: float | None = None
                tail_e0_mean: float | None = None
                if t_end is not None:
                    period_est, period_err = _estimate_period(
                        vtrace,
                        start=int(t_end),
                        period_min=int(p.period_min),
                        period_max=int(p.period_max),
                        error_tol=float(p.cycle_error_tol),
                    )
                    if period_est is not None:
                        stable_cycles = _count_stable_cycles(
                            vtrace,
                            start=int(t_end),
                            period=int(period_est),
                            error_tol=float(p.cycle_error_tol),
                        )
                    tail_v = vtrace[int(t_end) :]
                    tail_e0 = etrace[int(t_end) :]
                    tail_v_mean = _mean(tail_v) if tail_v else None
                    tail_e0_mean = _mean(tail_e0) if tail_e0 else None

                pass_run = bool(
                    t_end is not None
                    and period_est is not None
                    and stable_cycles >= int(p.min_stable_cycles)
                )
                run_rows.append(
                    {
                        "profile_id": profile.profile_id,
                        "size_xyz": [int(profile.size_x), int(profile.size_y), int(profile.size_z)],
                        "fold_order_id": fold.order_id,
                        "selected_op_idx": int(op_idx),
                        "transient_end_tick": t_end,
                        "period_estimate": period_est,
                        "period_error": period_err,
                        "stable_cycles_count": int(stable_cycles),
                        "tail_mean_velocity_x": tail_v_mean,
                        "tail_mean_e000_share": tail_e0_mean,
                        "pass_run": bool(pass_run),
                    }
                )

        profile_to_vs: Dict[str, List[float]] = {}
        for rr in run_rows:
            if not rr["pass_run"] or rr["tail_mean_velocity_x"] is None:
                continue
            profile_to_vs.setdefault(str(rr["profile_id"]), []).append(float(rr["tail_mean_velocity_x"]))

        fold_spans_ok = True
        for profile in profiles:
            vals = profile_to_vs.get(profile.profile_id, [])
            if not vals:
                fold_spans_ok = False
                break
            span = max(vals) - min(vals)
            if span > float(p.post_transient_fold_span_tol):
                fold_spans_ok = False
                break

        profile_gap_ok = False
        if len(profiles) >= 2:
            a_vals = profile_to_vs.get(profiles[0].profile_id, [])
            b_vals = profile_to_vs.get(profiles[1].profile_id, [])
            if a_vals and b_vals:
                ma = float(median(a_vals))
                mb = float(median(b_vals))
                denom = max(abs(ma), abs(mb), 1e-12)
                rel_gap = abs(ma - mb) / denom
                profile_gap_ok = bool(rel_gap <= float(p.post_transient_profile_gap_tol))
            else:
                profile_gap_ok = False

        all_runs_pass = bool(run_rows) and all(bool(r["pass_run"]) for r in run_rows)
        lock_ready = bool(all_runs_pass and fold_spans_ok and profile_gap_ok)
        target_rows.append(
            {
                "particle_id": particle_id,
                "energy_id": energy_id,
                "run_count": int(len(run_rows)),
                "all_runs_pass": bool(all_runs_pass),
                "fold_span_post_transient_ok": bool(fold_spans_ok),
                "profile_gap_post_transient_ok": bool(profile_gap_ok),
                "lock_ready": bool(lock_ready),
                "runs": run_rows,
            }
        )

    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH
    base_script = ROOT / BASE_SCRIPT_REPO_PATH
    payload: Dict[str, Any] = {
        "schema_version": "operational_kinematics_targeted_lock_v1",
        "claim_id": "KINEMATICS-MASS-ENERGY-001a",
        "mode": "targeted_lock_campaign",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "base_suite_script": BASE_SCRIPT_REPO_PATH,
        "base_suite_script_sha256": _sha_file(base_script),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(kernel_path),
        "kernel_profile": k.KERNEL_PROFILE,
        "projector_id": k.PROJECTOR_ID,
        "previous_suite_path": str(PREV_SUITE_JSON.relative_to(ROOT)),
        "previous_suite_replay_hash": prev.get("replay_hash"),
        "params": {
            "ticks": int(p.ticks),
            "burn_in_ticks": int(p.burn_in_ticks),
            "measure_ticks": int(p.measure_ticks),
            "min_burn_ticks_for_stabilization": int(p.min_burn_ticks_for_stabilization),
            "stabilization_window": int(p.stabilization_window),
            "stabilization_confirm_windows": int(p.stabilization_confirm_windows),
            "stabilization_velocity_tol": float(p.stabilization_velocity_tol),
            "stabilization_e000_tol": float(p.stabilization_e000_tol),
            "period_min": int(p.period_min),
            "period_max": int(p.period_max),
            "cycle_error_tol": float(p.cycle_error_tol),
            "min_stable_cycles": int(p.min_stable_cycles),
            "post_transient_fold_span_tol": float(p.post_transient_fold_span_tol),
            "post_transient_profile_gap_tol": float(p.post_transient_profile_gap_tol),
            "targets": [{"particle_id": pid, "energy_id": eid} for pid, eid in targets],
        },
        "targets": target_rows,
        "checks": {
            "target_count": int(len(target_rows)),
            "any_lock_ready": bool(any(bool(r["lock_ready"]) for r in target_rows)),
            "all_lock_ready": bool(target_rows) and all(bool(r["lock_ready"]) for r in target_rows),
        },
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# Operational Kinematics Targeted Lock Campaign (v1)",
        "",
        "## Campaign Checks",
        "",
    ]
    for k0, v0 in payload["checks"].items():
        lines.append(f"- {k0}: `{v0}`")
    lines.extend(
        [
            "",
            "## Targets",
            "",
            "| particle_id | energy_id | run_count | all_runs_pass | fold_span_ok | profile_gap_ok | lock_ready |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in payload["targets"]:
        lines.append(
            f"| `{row['particle_id']}` | `{row['energy_id']}` | {row['run_count']} | "
            f"{row['all_runs_pass']} | {row['fold_span_post_transient_ok']} | "
            f"{row['profile_gap_post_transient_ok']} | {row['lock_ready']} |"
        )
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
    parser.add_argument("--ticks", type=int, default=TargetedLockParams.ticks)
    parser.add_argument("--burn-in", type=int, default=TargetedLockParams.burn_in_ticks)
    parser.add_argument("--measure-ticks", type=int, default=TargetedLockParams.measure_ticks)
    args = parser.parse_args()
    params = TargetedLockParams(
        ticks=int(args.ticks),
        burn_in_ticks=int(args.burn_in),
        measure_ticks=int(args.measure_ticks),
    )
    payload = build_payload(params)
    write_artifacts(payload)
    print(
        "operational_kinematics_targeted_lock_v1: "
        f"targets={payload['checks']['target_count']}, "
        f"any_lock_ready={payload['checks']['any_lock_ready']}, "
        f"all_lock_ready={payload['checks']['all_lock_ready']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
