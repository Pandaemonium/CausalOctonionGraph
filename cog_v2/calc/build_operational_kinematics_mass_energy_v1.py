"""Build operational velocity/mass/kinetic measurement suite (v1).

Goal:
1) define replay-stable observables from exact kernel traces,
2) run elongated lattices (size_x >> size_y,size_z),
3) report fold-order and cross-shape robustness for candidate definitions.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Any, Dict, List, Sequence, Tuple

from calc.xor_scenario_loader import canonical_motif_state_map
from cog_v2.python import kernel_projective_unity as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "operational_kinematics_mass_energy_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "operational_kinematics_mass_energy_v1.md"
SCRIPT_REPO_PATH = "cog_v2/calc/build_operational_kinematics_mass_energy_v1.py"
KERNEL_REPO_PATH = "cog_v2/python/kernel_projective_unity.py"
MOTIF_SOURCE_REPO_PATH = "calc/xor_scenario_loader.py::canonical_motif_state_map"


@dataclass(frozen=True)
class MeasureParams:
    ticks: int = 56
    burn_in_ticks: int = 20
    measure_ticks: int = 24
    kick_ops: Tuple[int, ...] = (1, 2, 3, 4)
    profiles: Tuple[Tuple[str, int, int, int], ...] = ()
    particle_ids: Tuple[str, ...] = (
        "left_spinor_electron_ideal",
        "left_spinor_muon_motif",
        "left_spinor_tau_motif",
        "right_spinor_electron_ideal",
        "vector_proton_proto_t124",
    )
    velocity_span_tol: float = 0.10
    delta_velocity_span_tol: float = 0.10


@dataclass(frozen=True)
class LatticeProfile:
    profile_id: str
    size_x: int
    size_y: int
    size_z: int


@dataclass(frozen=True)
class FoldOrderVariant:
    order_id: str
    offsets: Tuple[Tuple[int, int, int], ...]


@dataclass(frozen=True)
class EnergyBand:
    energy_id: str
    center_kick: bool
    shell1_vacuum_coherent: bool
    shell2_vacuum_coherent: bool
    description: str


def _default_profiles() -> Tuple[LatticeProfile, ...]:
    return (
        LatticeProfile("elongated_1d_x41", 41, 1, 1),
        LatticeProfile("elongated_3d_offaxis_x41_y11_z11", 41, 11, 11),
    )


def _default_bands() -> Tuple[EnergyBand, ...]:
    return (
        EnergyBand(
            "E0_control",
            center_kick=False,
            shell1_vacuum_coherent=False,
            shell2_vacuum_coherent=False,
            description="Control lane: no explicit kick and no coherent shell vacuum seeding.",
        ),
        EnergyBand(
            "E1_center_kick",
            center_kick=True,
            shell1_vacuum_coherent=False,
            shell2_vacuum_coherent=False,
            description="Low excitation: center motif left-multiplied by eXYZ basis kick at tick 0.",
        ),
        EnergyBand(
            "E2_center_plus_shell1",
            center_kick=True,
            shell1_vacuum_coherent=True,
            shell2_vacuum_coherent=False,
            description=(
                "Medium excitation: center kick plus coherent +x nearest-neighbor vacuum phase seed "
                "(photon-like directional lane)."
            ),
        ),
        EnergyBand(
            "E3_center_plus_shell2",
            center_kick=True,
            shell1_vacuum_coherent=True,
            shell2_vacuum_coherent=True,
            description="Higher excitation: center kick plus coherent +x shell-1 and shell-2 vacuum phase seeding.",
        ),
    )


def _build_fold_orders() -> Tuple[FoldOrderVariant, ...]:
    base = [(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)]
    rev = list(reversed(base))
    axis_cycle = [(0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1), (-1, 0, 0), (1, 0, 0)]
    plus_first = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (-1, 0, 0), (0, -1, 0), (0, 0, -1)]
    return (
        FoldOrderVariant("canonical_xyz", tuple(base)),
        FoldOrderVariant("reverse_xyz", tuple(rev)),
        FoldOrderVariant("axis_cycle_yzx", tuple(axis_cycle)),
        FoldOrderVariant("plus_first", tuple(plus_first)),
    )


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _abs2(z: k.GInt) -> int:
    return int(z.re * z.re + z.im * z.im)


def _to_cxo(state_gi: Sequence[Tuple[int, int]]) -> k.CxO:
    vals = [k.GInt(int(re), int(im)) for re, im in state_gi]
    return k.project_cxo_to_unity((vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7]))


def _serialize_state(state: k.CxO) -> List[List[int]]:
    return [[int(z.re), int(z.im)] for z in state]


def _basis_state(op_idx: int) -> k.CxO:
    vals = [k.ZERO_G] * 8
    vals[int(op_idx)] = k.ONE_G
    return (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7])


def _left_mul_projected(op_idx: int, state: k.CxO) -> k.CxO:
    return k.project_cxo_to_unity(k.cxo_mul(_basis_state(int(op_idx)), state))


def _idx(x: int, y: int, z: int, sy: int, sz: int) -> int:
    return (int(x) * int(sy) + int(y)) * int(sz) + int(z)


def _cell_nonvac_power(state: k.CxO) -> float:
    return float(sum(_abs2(state[i]) for i in range(1, 8)))


def _world_centroid_x_mod(
    world: Sequence[k.CxO],
    *,
    sx: int,
    sy: int,
    sz: int,
) -> float:
    c = 0.0
    s = 0.0
    w_total = 0.0
    twopi = 2.0 * math.pi
    for x, y, z in itertools.product(range(int(sx)), range(int(sy)), range(int(sz))):
        w = _cell_nonvac_power(world[_idx(x, y, z, sy, sz)])
        if w <= 0.0:
            continue
        a = twopi * float(x) / float(sx)
        c += w * math.cos(a)
        s += w * math.sin(a)
        w_total += w
    if w_total <= 0.0:
        return float(sx // 2)
    ang = math.atan2(s, c)
    if ang < 0.0:
        ang += twopi
    return float(ang * float(sx) / twopi)


def _unwrap_mod_trace(trace_mod: Sequence[float], period: int) -> List[float]:
    if not trace_mod:
        return []
    out: List[float] = [float(trace_mod[0])]
    p = float(period)
    for x_mod in trace_mod[1:]:
        prev = out[-1]
        k0 = int(round((prev - float(x_mod)) / p))
        candidate = float(x_mod) + float(k0) * p
        out.append(candidate)
    return out


def _world_e000_share(world: Sequence[k.CxO]) -> float:
    e0 = 0.0
    total = 0.0
    for s in world:
        for i in range(8):
            p = float(_abs2(s[i]))
            total += p
            if i == 0:
                e0 += p
    if total <= 0.0:
        return 0.0
    return float(e0 / total)


def _world_nonvac_total(world: Sequence[k.CxO]) -> float:
    return float(sum(_cell_nonvac_power(s) for s in world))


def _init_world(
    *,
    profile: LatticeProfile,
    particle_state: k.CxO,
    vacuum_state: k.CxO,
    band: EnergyBand,
    op_idx: int,
) -> List[k.CxO]:
    sx, sy, sz = int(profile.size_x), int(profile.size_y), int(profile.size_z)
    center = (sx // 2, sy // 2, sz // 2)
    shell1 = ((center[0] + 1) % sx, center[1], center[2])
    shell2 = ((center[0] + 2) % sx, center[1], center[2])
    world: List[k.CxO] = [k.cxo_one() for _ in range(sx * sy * sz)]
    center_state = _left_mul_projected(op_idx, particle_state) if band.center_kick else particle_state
    world[_idx(center[0], center[1], center[2], sy, sz)] = center_state
    vac_phase = _left_mul_projected(op_idx, vacuum_state)
    if band.shell1_vacuum_coherent:
        world[_idx(shell1[0], shell1[1], shell1[2], sy, sz)] = vac_phase
    if band.shell2_vacuum_coherent:
        world[_idx(shell2[0], shell2[1], shell2[2], sy, sz)] = vac_phase
    return world


def _count_coeff_differences(world_a: Sequence[k.CxO], world_b: Sequence[k.CxO]) -> int:
    if len(world_a) != len(world_b):
        raise ValueError("world size mismatch in difference count")
    diff = 0
    for sa, sb in zip(world_a, world_b):
        for i in range(8):
            if sa[i] != sb[i]:
                diff += 1
    return int(diff)


def _simulate_case(
    *,
    params: MeasureParams,
    profile: LatticeProfile,
    fold: FoldOrderVariant,
    particle_state: k.CxO,
    vacuum_state: k.CxO,
    band: EnergyBand,
    op_idx: int,
) -> Dict[str, Any]:
    sx, sy, sz = int(profile.size_x), int(profile.size_y), int(profile.size_z)
    world = _init_world(
        profile=profile,
        particle_state=particle_state,
        vacuum_state=vacuum_state,
        band=band,
        op_idx=int(op_idx),
    )
    init_world = list(world)

    centroid_mod_trace: List[float] = []
    e000_share_trace: List[float] = []
    nonvac_total_trace: List[float] = []

    def record_snapshot(cur: Sequence[k.CxO]) -> None:
        centroid_mod_trace.append(_world_centroid_x_mod(cur, sx=sx, sy=sy, sz=sz))
        e000_share_trace.append(_world_e000_share(cur))
        nonvac_total_trace.append(_world_nonvac_total(cur))

    record_snapshot(world)
    for _ in range(int(params.ticks)):
        old = world
        nxt: List[k.CxO] = [k.cxo_one() for _ in range(sx * sy * sz)]
        for x, y, z in itertools.product(range(sx), range(sy), range(sz)):
            msgs: List[k.CxO] = []
            for dx, dy, dz in fold.offsets:
                qx = (x + int(dx)) % sx
                qy = (y + int(dy)) % sy
                qz = (z + int(dz)) % sz
                msgs.append(old[_idx(qx, qy, qz, sy, sz)])
            nxt[_idx(x, y, z, sy, sz)] = k.update_rule(old[_idx(x, y, z, sy, sz)], msgs)
        world = nxt
        record_snapshot(world)

    centroid_unwrapped = _unwrap_mod_trace(centroid_mod_trace, period=sx)
    if len(centroid_unwrapped) < 2:
        raise ValueError("centroid trace too short")

    burn = int(max(0, min(params.burn_in_ticks, len(centroid_unwrapped) - 2)))
    t1 = int(min(len(centroid_unwrapped) - 1, burn + int(params.measure_ticks)))
    if t1 <= burn:
        raise ValueError("invalid measurement window")

    velocity_trace = [float(centroid_unwrapped[t + 1] - centroid_unwrapped[t]) for t in range(len(centroid_unwrapped) - 1)]
    v_window = velocity_trace[burn:t1]
    e_window = e000_share_trace[burn:t1]
    n_window = nonvac_total_trace[burn:t1]
    mean_v = float(sum(v_window) / len(v_window)) if v_window else 0.0
    mean_e0 = float(sum(e_window) / len(e_window)) if e_window else 0.0
    mean_nonvac = float(sum(n_window) / len(n_window)) if n_window else 0.0
    net_dx = float(centroid_unwrapped[t1] - centroid_unwrapped[burn])
    avg_speed_abs = float(sum(abs(v) for v in v_window) / len(v_window)) if v_window else 0.0

    return {
        "init_world": init_world,
        "summary": {
            "window_start_tick": int(burn),
            "window_end_tick_exclusive": int(t1),
            "window_len": int(len(v_window)),
            "mean_velocity_x": float(mean_v),
            "mean_speed_abs_x": float(avg_speed_abs),
            "net_displacement_x": float(net_dx),
            "mean_e000_share": float(mean_e0),
            "mean_nonvac_total": float(mean_nonvac),
        },
        "traces": {
            "centroid_x_mod": [float(x) for x in centroid_mod_trace],
            "centroid_x_unwrapped": [float(x) for x in centroid_unwrapped],
            "velocity_x": [float(v) for v in velocity_trace],
            "e000_share": [float(x) for x in e000_share_trace],
            "nonvac_total": [float(x) for x in nonvac_total_trace],
        },
    }


def _median_or_none(vals: Sequence[float]) -> float | None:
    if not vals:
        return None
    return float(median([float(v) for v in vals]))


def build_payload(params: MeasureParams | None = None) -> Dict[str, Any]:
    p = params if params is not None else MeasureParams()
    if int(p.ticks) < 24:
        raise ValueError("ticks must be >= 24")
    if int(p.measure_ticks) < 8:
        raise ValueError("measure_ticks must be >= 8")
    if int(p.burn_in_ticks) >= int(p.ticks) - 1:
        raise ValueError("burn_in_ticks must be < ticks - 1")
    if not p.kick_ops:
        raise ValueError("kick_ops must be non-empty")

    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH
    motifs = canonical_motif_state_map()
    vacuum_state = _to_cxo(motifs["su_vacuum_omega"])
    bands = _default_bands()
    folds = _build_fold_orders()
    if p.profiles:
        profiles = tuple(
            LatticeProfile(str(pid), int(sx), int(sy), int(sz))
            for pid, sx, sy, sz in p.profiles
        )
    else:
        profiles = _default_profiles()
    if not profiles:
        raise ValueError("at least one profile is required")

    by_particle: List[Dict[str, Any]] = []
    profile_energy_index: Dict[Tuple[str, str], Dict[str, Any]] = {}
    shape_comparisons: List[Dict[str, Any]] = []

    for pid in p.particle_ids:
        if pid not in motifs:
            continue
        particle_state = _to_cxo(motifs[pid])
        particle_row: Dict[str, Any] = {
            "particle_id": pid,
            "profiles": [],
        }

        for profile in profiles:
            control_band = next(b for b in bands if b.energy_id == "E0_control")
            control_runs: Dict[str, Dict[str, Any]] = {}
            for fold in folds:
                control_runs[fold.order_id] = _simulate_case(
                    params=p,
                    profile=profile,
                    fold=fold,
                    particle_state=particle_state,
                    vacuum_state=vacuum_state,
                    band=control_band,
                    op_idx=0,
                )

            profile_row: Dict[str, Any] = {
                "profile_id": profile.profile_id,
                "size_xyz": [int(profile.size_x), int(profile.size_y), int(profile.size_z)],
                "aspect_ratio_x_over_max_yz": float(int(profile.size_x) / float(max(1, int(profile.size_y), int(profile.size_z)))),
                "control": {
                    "fold_metrics": [
                        {
                            "fold_order_id": fold.order_id,
                            **control_runs[fold.order_id]["summary"],
                        }
                        for fold in folds
                    ]
                },
                "energies": [],
            }

            control_v_by_fold = {
                fold.order_id: float(control_runs[fold.order_id]["summary"]["mean_velocity_x"])
                for fold in folds
            }
            control_e0_by_fold = {
                fold.order_id: float(control_runs[fold.order_id]["summary"]["mean_e000_share"])
                for fold in folds
            }

            for band in bands:
                if band.energy_id == "E0_control":
                    continue

                op_candidates: List[Dict[str, Any]] = []
                for op_idx in p.kick_ops:
                    fold_case_runs: Dict[str, Dict[str, Any]] = {}
                    dv_vals: List[float] = []
                    for fold in folds:
                        sim = _simulate_case(
                            params=p,
                            profile=profile,
                            fold=fold,
                            particle_state=particle_state,
                            vacuum_state=vacuum_state,
                            band=band,
                            op_idx=int(op_idx),
                        )
                        fold_case_runs[fold.order_id] = sim
                        dv_vals.append(float(sim["summary"]["mean_velocity_x"] - control_v_by_fold[fold.order_id]))

                    score = float(median([abs(v) for v in dv_vals])) if dv_vals else 0.0
                    op_candidates.append(
                        {
                            "op_idx": int(op_idx),
                            "score_median_abs_delta_v": float(score),
                            "fold_case_runs": fold_case_runs,
                        }
                    )

                op_candidates = sorted(op_candidates, key=lambda r: (-float(r["score_median_abs_delta_v"]), int(r["op_idx"])))
                winner = op_candidates[0]
                chosen_op = int(winner["op_idx"])
                chosen_runs = winner["fold_case_runs"]

                control_init = _init_world(
                    profile=profile,
                    particle_state=particle_state,
                    vacuum_state=vacuum_state,
                    band=control_band,
                    op_idx=0,
                )
                case_init = _init_world(
                    profile=profile,
                    particle_state=particle_state,
                    vacuum_state=vacuum_state,
                    band=band,
                    op_idx=int(chosen_op),
                )
                impulse_hamming = int(_count_coeff_differences(case_init, control_init))

                fold_metrics: List[Dict[str, Any]] = []
                case_v_list: List[float] = []
                delta_v_list: List[float] = []
                mass_list: List[float] = []
                k_list: List[float] = []
                for fold in folds:
                    fold_id = fold.order_id
                    case_sum = chosen_runs[fold_id]["summary"]
                    v_case = float(case_sum["mean_velocity_x"])
                    v_ctrl = float(control_v_by_fold[fold_id])
                    dv = float(v_case - v_ctrl)
                    e0_case = float(case_sum["mean_e000_share"])
                    e0_ctrl = float(control_e0_by_fold[fold_id])
                    de0 = float(e0_case - e0_ctrl)
                    mass_est: float | None = None
                    kinetic_est: float | None = None
                    if abs(dv) > 1e-12:
                        mass_est = float(impulse_hamming / abs(dv))
                        kinetic_est = float(0.5 * mass_est * max(0.0, (v_case * v_case - v_ctrl * v_ctrl)))
                        mass_list.append(float(mass_est))
                        k_list.append(float(kinetic_est))
                    case_v_list.append(float(v_case))
                    delta_v_list.append(float(dv))
                    fold_metrics.append(
                        {
                            "fold_order_id": fold_id,
                            "op_idx": int(chosen_op),
                            "impulse_hamming": int(impulse_hamming),
                            "mean_velocity_x_case": float(v_case),
                            "mean_velocity_x_control": float(v_ctrl),
                            "delta_velocity_x": float(dv),
                            "mean_e000_share_case": float(e0_case),
                            "mean_e000_share_control": float(e0_ctrl),
                            "delta_e000_share": float(de0),
                            "mass_estimator_impulse_over_abs_delta_v": mass_est,
                            "kinetic_estimator_half_m_delta_v2": kinetic_est,
                        }
                    )

                v_span = float(max(case_v_list) - min(case_v_list)) if case_v_list else 0.0
                dv_span = float(max(delta_v_list) - min(delta_v_list)) if delta_v_list else 0.0
                nonzero_signs = [1 if v > 0.0 else -1 for v in delta_v_list if abs(v) > 1e-12]
                sign_consistent = bool(len(set(nonzero_signs)) <= 1)
                robust_fold = bool(v_span <= float(p.velocity_span_tol) and dv_span <= float(p.delta_velocity_span_tol) and sign_consistent)

                canonical_trace = chosen_runs["canonical_xyz"]["traces"]
                energy_row = {
                    "energy_id": band.energy_id,
                    "energy_description": band.description,
                    "selected_op_idx": int(chosen_op),
                    "candidate_ops_ranked": [
                        {
                            "op_idx": int(r["op_idx"]),
                            "score_median_abs_delta_v": float(r["score_median_abs_delta_v"]),
                        }
                        for r in op_candidates
                    ],
                    "fold_metrics": fold_metrics,
                    "aggregates": {
                        "median_velocity_x_case": _median_or_none(case_v_list),
                        "median_delta_velocity_x": _median_or_none(delta_v_list),
                        "median_mass_estimator": _median_or_none(mass_list),
                        "median_kinetic_estimator": _median_or_none(k_list),
                        "velocity_span_across_folds": float(v_span),
                        "delta_velocity_span_across_folds": float(dv_span),
                        "delta_velocity_sign_consistent": bool(sign_consistent),
                        "fold_order_robust": bool(robust_fold),
                        "impulse_hamming": int(impulse_hamming),
                    },
                    "canonical_trace": {
                        "centroid_x_mod": canonical_trace["centroid_x_mod"],
                        "centroid_x_unwrapped": canonical_trace["centroid_x_unwrapped"],
                        "velocity_x": canonical_trace["velocity_x"],
                        "e000_share": canonical_trace["e000_share"],
                        "nonvac_total": canonical_trace["nonvac_total"],
                    },
                }
                profile_row["energies"].append(energy_row)
                profile_energy_index[(pid, profile.profile_id, band.energy_id)] = energy_row

            particle_row["profiles"].append(profile_row)
        by_particle.append(particle_row)

    # Cross-shape comparison per particle/energy using medians.
    if len(profiles) >= 2:
        p0 = profiles[0].profile_id
        p1 = profiles[1].profile_id
        for prow in by_particle:
            pid = str(prow["particle_id"])
            for band in [b for b in bands if b.energy_id != "E0_control"]:
                a = profile_energy_index.get((pid, p0, band.energy_id))
                b = profile_energy_index.get((pid, p1, band.energy_id))
                if a is None or b is None:
                    continue
                da = a["aggregates"]["median_delta_velocity_x"]
                db = b["aggregates"]["median_delta_velocity_x"]
                ma = a["aggregates"]["median_mass_estimator"]
                mb = b["aggregates"]["median_mass_estimator"]
                rel_dv: float | None = None
                rel_m: float | None = None
                if da is not None and db is not None and max(abs(float(da)), abs(float(db))) > 0.0:
                    rel_dv = float(abs(float(da) - float(db)) / max(abs(float(da)), abs(float(db))))
                if ma is not None and mb is not None and max(abs(float(ma)), abs(float(mb))) > 0.0:
                    rel_m = float(abs(float(ma) - float(mb)) / max(abs(float(ma)), abs(float(mb))))
                shape_robust = bool(
                    (rel_dv is not None and rel_dv <= 0.35)
                    and (rel_m is not None and rel_m <= 0.50)
                )
                shape_comparisons.append(
                    {
                        "particle_id": pid,
                        "energy_id": band.energy_id,
                        "profile_a": p0,
                        "profile_b": p1,
                        "median_delta_velocity_a": da,
                        "median_delta_velocity_b": db,
                        "relative_delta_velocity_gap": rel_dv,
                        "median_mass_a": ma,
                        "median_mass_b": mb,
                        "relative_mass_gap": rel_m,
                        "shape_robust": bool(shape_robust),
                    }
                )

    payload: Dict[str, Any] = {
        "schema_version": "operational_kinematics_mass_energy_v1",
        "claim_id": "KINEMATICS-MASS-ENERGY-001",
        "mode": "simulation_first_structure_first",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(kernel_path),
        "kernel_profile": k.KERNEL_PROFILE,
        "projector_id": k.PROJECTOR_ID,
        "motif_source": MOTIF_SOURCE_REPO_PATH,
        "params": {
            "ticks": int(p.ticks),
            "burn_in_ticks": int(p.burn_in_ticks),
            "measure_ticks": int(p.measure_ticks),
            "kick_ops": [int(x) for x in p.kick_ops],
            "profiles_override_used": bool(len(p.profiles) > 0),
            "particle_ids": list(p.particle_ids),
            "velocity_span_tol": float(p.velocity_span_tol),
            "delta_velocity_span_tol": float(p.delta_velocity_span_tol),
            "profiles": [
                {
                    "profile_id": pr.profile_id,
                    "size_xyz": [int(pr.size_x), int(pr.size_y), int(pr.size_z)],
                    "aspect_ratio_x_over_max_yz": float(int(pr.size_x) / float(max(1, int(pr.size_y), int(pr.size_z)))),
                }
                for pr in profiles
            ],
            "boundary_mode": "periodic_torus",
        },
        "energy_bands": [
            {
                "energy_id": b.energy_id,
                "description": b.description,
                "center_kick": bool(b.center_kick),
                "shell1_vacuum_coherent": bool(b.shell1_vacuum_coherent),
                "shell2_vacuum_coherent": bool(b.shell2_vacuum_coherent),
            }
            for b in bands
        ],
        "fold_order_variants": [f.order_id for f in folds],
        "particles": by_particle,
        "shape_comparisons": shape_comparisons,
        "checks": {
            "any_profile_elongated_x_over_10": bool(
                any(int(pr.size_x) / float(max(1, int(pr.size_y), int(pr.size_z))) >= 10.0 for pr in profiles)
            ),
            "has_large_offaxis_profile_yz_ge_11": bool(
                any(int(pr.size_y) >= 11 and int(pr.size_z) >= 11 for pr in profiles)
            ),
            "any_shape_robust_case": bool(any(bool(r["shape_robust"]) for r in shape_comparisons)),
            "shape_comparison_count": int(len(shape_comparisons)),
            "particle_count_processed": int(len(by_particle)),
        },
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def _render_md(payload: Dict[str, Any]) -> str:
    p = payload["params"]
    lines = [
        "# Operational Kinematics / Mass / Kinetic Suite (v1)",
        "",
        "## Params",
        "",
        f"- ticks: `{p['ticks']}`",
        f"- burn_in_ticks: `{p['burn_in_ticks']}`",
        f"- measure_ticks: `{p['measure_ticks']}`",
        f"- kick_ops: `{p['kick_ops']}`",
        f"- profiles: `{[r['profile_id'] for r in p['profiles']]}`",
        f"- fold_order_variants: `{payload['fold_order_variants']}`",
        "",
        "## Profile Geometry",
        "",
        "| profile_id | size_xyz | aspect_ratio_x_over_max_yz |",
        "|---|---|---:|",
    ]
    for pr in p["profiles"]:
        lines.append(
            f"| `{pr['profile_id']}` | `{pr['size_xyz']}` | {pr['aspect_ratio_x_over_max_yz']} |"
        )

    lines.extend(
        [
            "",
            "## Shape Robustness Summary",
            "",
            "| particle_id | energy_id | relative_delta_velocity_gap | relative_mass_gap | shape_robust |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for row in payload["shape_comparisons"]:
        lines.append(
            f"| `{row['particle_id']}` | `{row['energy_id']}` | "
            f"{row['relative_delta_velocity_gap']} | {row['relative_mass_gap']} | {row['shape_robust']} |"
        )

    lines.extend(["", "## Checks", ""])
    for key, val in payload["checks"].items():
        lines.append(f"- {key}: `{val}`")
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
    parser.add_argument("--ticks", type=int, default=MeasureParams.ticks)
    parser.add_argument("--burn-in", type=int, default=MeasureParams.burn_in_ticks)
    parser.add_argument("--measure-ticks", type=int, default=MeasureParams.measure_ticks)
    parser.add_argument("--kick-ops", type=int, nargs="*", default=list(MeasureParams.kick_ops))
    args = parser.parse_args()

    kicks = tuple(int(x) for x in args.kick_ops)
    params = MeasureParams(
        ticks=int(args.ticks),
        burn_in_ticks=int(args.burn_in),
        measure_ticks=int(args.measure_ticks),
        kick_ops=kicks,
    )
    payload = build_payload(params)
    write_artifacts(payload)
    print(
        "operational_kinematics_mass_energy_v1: "
        f"particles={payload['checks']['particle_count_processed']}, "
        f"shape_comparisons={payload['checks']['shape_comparison_count']}, "
        f"any_shape_robust_case={payload['checks']['any_shape_robust_case']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
