"""Targeted lock campaign for operational mass estimator (v1).

Mass definition lane:
1) impulse-response window (early fixed window),
2) m_est := I_h / |delta_v_impulse|,
3) fold and cross-shape robustness gates.
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
    _count_coeff_differences,
    _default_bands,
    _default_profiles,
    _init_world,
    _simulate_case,
    _to_cxo,
)
from cog_v2.python import kernel_projective_unity as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "operational_mass_targeted_lock_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "operational_mass_targeted_lock_v1.md"
SCRIPT_REPO_PATH = "cog_v2/calc/build_operational_mass_targeted_lock_v1.py"
PREV_SUITE_JSON = ROOT / "cog_v2" / "sources" / "operational_kinematics_mass_energy_v1.json"


@dataclass(frozen=True)
class MassTargetedLockParams:
    ticks: int = 220
    burn_in_ticks: int = 56
    measure_ticks: int = 120
    impulse_window_start: int = 6
    impulse_window_len: int = 24
    delta_v_eps: float = 1e-6
    fold_mass_span_tol: float = 0.40
    profile_mass_gap_tol: float = 0.50
    require_large_offaxis_primary_profile: bool = True
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


def _impulse_mass_run(
    *,
    sim_case: Dict[str, Any],
    sim_ctrl: Dict[str, Any],
    impulse_hamming: int,
    impulse_window_start: int,
    impulse_window_len: int,
    delta_v_eps: float,
) -> Dict[str, Any]:
    v_case = [float(x) for x in sim_case["traces"]["velocity_x"]]
    v_ctrl = [float(x) for x in sim_ctrl["traces"]["velocity_x"]]
    n = min(len(v_case), len(v_ctrl))
    a = int(max(0, min(impulse_window_start, n)))
    b = int(max(a, min(a + impulse_window_len, n)))
    if b <= a:
        return {
            "window_start": a,
            "window_end_exclusive": b,
            "window_len": 0,
            "delta_v_impulse": None,
            "mass_estimator": None,
            "pass_run": False,
        }
    dv_trace = [float(v_case[t] - v_ctrl[t]) for t in range(a, b)]
    dv = _mean(dv_trace)
    mass_est: float | None = None
    pass_run = False
    if abs(dv) > float(delta_v_eps):
        mass_est = float(float(impulse_hamming) / abs(dv))
        pass_run = True
    return {
        "window_start": int(a),
        "window_end_exclusive": int(b),
        "window_len": int(b - a),
        "delta_v_impulse": float(dv),
        "mass_estimator": mass_est,
        "pass_run": bool(pass_run),
    }


def build_payload(params: MassTargetedLockParams | None = None) -> Dict[str, Any]:
    p = params if params is not None else MassTargetedLockParams()
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
        profiles=tuple((pr.profile_id, pr.size_x, pr.size_y, pr.size_z) for pr in profiles),
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
        control_band = bands["E0_control"]
        run_rows: List[Dict[str, Any]] = []

        for profile in profiles:
            op_idx = _lookup_selected_op(prev, particle_id, profile.profile_id, energy_id)
            if op_idx is None:
                continue
            init_ctrl = _init_world(
                profile=profile,
                particle_state=particle_state,
                vacuum_state=vacuum_state,
                band=control_band,
                op_idx=0,
            )
            init_case = _init_world(
                profile=profile,
                particle_state=particle_state,
                vacuum_state=vacuum_state,
                band=band,
                op_idx=int(op_idx),
            )
            impulse_hamming = int(_count_coeff_differences(init_case, init_ctrl))
            for fold in folds:
                sim_ctrl = _simulate_case(
                    params=sim_params,
                    profile=profile,
                    fold=fold,
                    particle_state=particle_state,
                    vacuum_state=vacuum_state,
                    band=control_band,
                    op_idx=0,
                )
                sim_case = _simulate_case(
                    params=sim_params,
                    profile=profile,
                    fold=fold,
                    particle_state=particle_state,
                    vacuum_state=vacuum_state,
                    band=band,
                    op_idx=int(op_idx),
                )
                rr = _impulse_mass_run(
                    sim_case=sim_case,
                    sim_ctrl=sim_ctrl,
                    impulse_hamming=int(impulse_hamming),
                    impulse_window_start=int(p.impulse_window_start),
                    impulse_window_len=int(p.impulse_window_len),
                    delta_v_eps=float(p.delta_v_eps),
                )
                run_rows.append(
                    {
                        "profile_id": profile.profile_id,
                        "size_xyz": [int(profile.size_x), int(profile.size_y), int(profile.size_z)],
                        "fold_order_id": fold.order_id,
                        "selected_op_idx": int(op_idx),
                        "impulse_hamming": int(impulse_hamming),
                        **rr,
                    }
                )

        profile_to_masses: Dict[str, List[float]] = {}
        for rr in run_rows:
            if not rr["pass_run"] or rr["mass_estimator"] is None:
                continue
            profile_to_masses.setdefault(str(rr["profile_id"]), []).append(float(rr["mass_estimator"]))

        primary_profiles = (
            [pr for pr in profiles if int(pr.size_y) >= 11 and int(pr.size_z) >= 11]
            if bool(p.require_large_offaxis_primary_profile)
            else list(profiles)
        )
        if not primary_profiles:
            primary_profiles = list(profiles)

        fold_spans_ok = True
        for profile in primary_profiles:
            vals = profile_to_masses.get(profile.profile_id, [])
            if not vals:
                fold_spans_ok = False
                break
            span_rel = (max(vals) - min(vals)) / max(abs(median(vals)), 1e-12)
            if span_rel > float(p.fold_mass_span_tol):
                fold_spans_ok = False
                break

        profile_gap_ok = False
        profile_gap_applicable = False
        if len(primary_profiles) >= 2:
            a_vals = profile_to_masses.get(primary_profiles[0].profile_id, [])
            b_vals = profile_to_masses.get(primary_profiles[1].profile_id, [])
            if a_vals and b_vals:
                ma = float(median(a_vals))
                mb = float(median(b_vals))
                rel_gap = abs(ma - mb) / max(abs(ma), abs(mb), 1e-12)
                profile_gap_ok = bool(rel_gap <= float(p.profile_mass_gap_tol))
                profile_gap_applicable = True
        else:
            profile_gap_ok = True

        all_runs_pass = bool(run_rows) and all(bool(r["pass_run"]) for r in run_rows)
        mass_lock_ready = bool(all_runs_pass and fold_spans_ok and profile_gap_ok)

        target_rows.append(
            {
                "particle_id": particle_id,
                "energy_id": energy_id,
                "run_count": int(len(run_rows)),
                "all_runs_pass": bool(all_runs_pass),
                "primary_profile_ids": [pr.profile_id for pr in primary_profiles],
                "fold_span_mass_ok": bool(fold_spans_ok),
                "profile_gap_mass_ok": bool(profile_gap_ok),
                "profile_gap_mass_applicable": bool(profile_gap_applicable),
                "mass_lock_ready": bool(mass_lock_ready),
                "runs": run_rows,
            }
        )

    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH
    base_script = ROOT / BASE_SCRIPT_REPO_PATH
    payload: Dict[str, Any] = {
        "schema_version": "operational_mass_targeted_lock_v1",
        "claim_id": "KINEMATICS-MASS-ENERGY-001b",
        "mode": "targeted_mass_lock_campaign",
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
            "impulse_window_start": int(p.impulse_window_start),
            "impulse_window_len": int(p.impulse_window_len),
            "delta_v_eps": float(p.delta_v_eps),
            "fold_mass_span_tol": float(p.fold_mass_span_tol),
            "profile_mass_gap_tol": float(p.profile_mass_gap_tol),
            "require_large_offaxis_primary_profile": bool(p.require_large_offaxis_primary_profile),
            "targets": [{"particle_id": pid, "energy_id": eid} for pid, eid in targets],
        },
        "targets": target_rows,
        "checks": {
            "target_count": int(len(target_rows)),
            "any_mass_lock_ready": bool(any(bool(r["mass_lock_ready"]) for r in target_rows)),
            "all_mass_lock_ready": bool(target_rows) and all(bool(r["mass_lock_ready"]) for r in target_rows),
        },
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# Operational Mass Targeted Lock Campaign (v1)",
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
            "| particle_id | energy_id | run_count | all_runs_pass | fold_mass_ok | profile_mass_ok | mass_lock_ready |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in payload["targets"]:
        lines.append(
            f"| `{row['particle_id']}` | `{row['energy_id']}` | {row['run_count']} | "
            f"{row['all_runs_pass']} | {row['fold_span_mass_ok']} | "
            f"{row['profile_gap_mass_ok']} | {row['mass_lock_ready']} |"
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
    parser.add_argument("--ticks", type=int, default=MassTargetedLockParams.ticks)
    parser.add_argument("--burn-in", type=int, default=MassTargetedLockParams.burn_in_ticks)
    parser.add_argument("--measure-ticks", type=int, default=MassTargetedLockParams.measure_ticks)
    args = parser.parse_args()
    params = MassTargetedLockParams(
        ticks=int(args.ticks),
        burn_in_ticks=int(args.burn_in),
        measure_ticks=int(args.measure_ticks),
    )
    payload = build_payload(params)
    write_artifacts(payload)
    print(
        "operational_mass_targeted_lock_v1: "
        f"targets={payload['checks']['target_count']}, "
        f"any_mass_lock_ready={payload['checks']['any_mass_lock_ready']}, "
        f"all_mass_lock_ready={payload['checks']['all_mass_lock_ready']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
