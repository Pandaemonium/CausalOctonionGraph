"""Generate deterministic Weinberg-angle test cases using the world_code kernel.

Each case simulates:
1) two electroweak seeds separated by integer edge distance N,
2) relative phase offset P (applied as left e7 temporal commits),
3) optional vacuum preconditioning ticks before measurement (warm start),
4) deterministic per-tick CxO updates on a fixed 1D lightcone corridor.

Outputs:
1) JSON dataset with preconditioning and measurement Weinberg observables,
2) CSV table with per-step rows across all cases and stages.

Performance features in this version:
1) per-case precomputed deterministic traversal order (no per-tick sort),
2) optional case-level multiprocessing,
3) resumable per-case checkpoints + partial summaries.

Rigor:
1) update-rule math is unchanged,
2) fast-step path is a semantic refactor of the same recurrence,
3) optional `--verify-fast-step` executes one reference tick equality check per case.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable, Dict, List, Sequence, Tuple, Type

import minimal_world_kernel as integer_kernel
import minimal_world_kernel_unity as unity_kernel
from minimal_world_kernel import (
    CxO,
    GInt,
    ONE_G,
    ZERO_G,
    World,
    cxo_mul,
    step as step_integer,
)
from minimal_world_kernel_unity import step as step_unity


RESULTS_ROOT = Path("world_code/Python_code/results/weinberg_20_cases")
CHECKPOINT_NAME = "weinberg_20_cases.checkpoint.json"
PARTIAL_SUMMARY_NAME = "weinberg_20_cases.partial.json"
CASE_DIR_NAME = "cases"

# Locked masks from CausalGraphTheory/WeakMixingObservable.lean.
MASK_U1_INCLUSIVE = (0, 7)      # {e0, e7}
MASK_WEAK_INCLUSIVE = (1, 6, 7) # {e1, e6, e7}
MASK_WEAK_EXCLUSIVE = (1, 6)    # weak without shared e7 overlap
MASK_EW = (0, 1, 6, 7)          # union(U1, weak)
MASK_EXCLUSIVE_U1 = (0,)        # U1 without overlap with weak


@dataclass(frozen=True)
class CaseConfig:
    case_id: str
    edge_distance: int
    steps: int
    phase_offset: int


@dataclass(frozen=True)
class KernelProfile:
    step_fn: Callable[[object], object]
    update_rule_fn: Callable[[CxO, List[CxO]], CxO]
    world_cls: Type[object]
    kernel_path: str


@dataclass(frozen=True)
class StepPlan:
    ordered_node_ids: Tuple[str, ...]
    parent_indices: Tuple[Tuple[int, ...], ...]


def _basis_state(idx: int, coeff: GInt) -> CxO:
    vals = [ZERO_G for _ in range(8)]
    vals[idx] = coeff
    return (
        vals[0],
        vals[1],
        vals[2],
        vals[3],
        vals[4],
        vals[5],
        vals[6],
        vals[7],
    )


def _electroweak_seed() -> CxO:
    vals = [ZERO_G for _ in range(8)]
    vals[0] = ONE_G
    vals[1] = ONE_G
    vals[6] = ONE_G
    vals[7] = ONE_G
    return (
        vals[0],
        vals[1],
        vals[2],
        vals[3],
        vals[4],
        vals[5],
        vals[6],
        vals[7],
    )


def _vacuum_seed() -> CxO:
    return _basis_state(7, ONE_G)


def _temporal_commit(state: CxO) -> CxO:
    e7 = _basis_state(7, ONE_G)
    return cxo_mul(e7, state)


def _apply_phase_offset(state: CxO, offset: int) -> CxO:
    out = state
    for _ in range(max(0, int(offset))):
        out = _temporal_commit(out)
    return out


def _g_norm2(z: GInt) -> int:
    return int(z.re) * int(z.re) + int(z.im) * int(z.im)


def _channel_energy(state: CxO, mask: Sequence[int]) -> int:
    return sum(_g_norm2(state[idx]) for idx in mask)


def _node_name(pos: int) -> str:
    if pos < 0:
        return f"x_m{abs(pos)}"
    return f"x_{pos}"


def _build_world(
    edge_distance: int,
    steps: int,
    phase_offset: int,
    world_cls: Type[object] = World,
) -> Tuple[object, List[int], int, int]:
    left_pos = 0
    right_pos = int(edge_distance)
    extent = int(steps)
    min_pos = left_pos - extent
    max_pos = right_pos + extent
    positions = list(range(min_pos, max_pos + 1))
    node_ids = [_node_name(p) for p in positions]
    by_pos = {p: _node_name(p) for p in positions}

    parents: Dict[str, List[str]] = {}
    for p in positions:
        pids: List[str] = []
        for q in (p - 1, p, p + 1):
            if q in by_pos:
                pids.append(by_pos[q])
        parents[by_pos[p]] = pids

    init_state: Dict[str, CxO] = {nid: _vacuum_seed() for nid in node_ids}
    init_state[by_pos[left_pos]] = _electroweak_seed()
    init_state[by_pos[right_pos]] = _apply_phase_offset(_electroweak_seed(), phase_offset)

    world = world_cls(
        node_ids=node_ids,
        parents=parents,
        states=init_state,
        tick=0,
    )
    return world, positions, left_pos, right_pos


def _make_case_grid(max_steps: int | None = None) -> List[CaseConfig]:
    distances = [4, 6, 8, 10, 12]
    phase_offsets = [0, 1, 2, 3]
    out: List[CaseConfig] = []
    idx = 0
    for d in distances:
        for p in phase_offsets:
            steps = d + 8 + 2 * p
            if max_steps is not None:
                steps = min(steps, max_steps)
            out.append(
                CaseConfig(
                    case_id=f"weinberg_case_{idx:02d}",
                    edge_distance=d,
                    steps=steps,
                    phase_offset=p,
                )
            )
            idx += 1
    if len(out) != 20:
        raise ValueError(f"expected 20 cases, got {len(out)}")
    return out


def _select_kernel_profile(kernel_profile: str) -> KernelProfile:
    if kernel_profile == "integer":
        return KernelProfile(
            step_fn=step_integer,
            update_rule_fn=integer_kernel.update_rule,
            world_cls=integer_kernel.World,
            kernel_path="world_code/Python_code/minimal_world_kernel.py",
        )
    if kernel_profile == "unity":
        return KernelProfile(
            step_fn=step_unity,
            update_rule_fn=unity_kernel.update_rule,
            world_cls=unity_kernel.World,
            kernel_path="world_code/Python_code/minimal_world_kernel_unity.py",
        )
    raise ValueError("--kernel-profile must be one of: integer, unity")


def _build_step_plan(world: object) -> StepPlan:
    ordered_node_ids = tuple(sorted(world.node_ids))
    index_by_node = {nid: i for i, nid in enumerate(ordered_node_ids)}
    parent_indices: List[Tuple[int, ...]] = []
    for nid in ordered_node_ids:
        pids = sorted(world.parents.get(nid, []))
        parent_indices.append(tuple(index_by_node[pid] for pid in pids))
    return StepPlan(ordered_node_ids=ordered_node_ids, parent_indices=tuple(parent_indices))


def _build_fast_stepper(
    world: object,
    update_rule_fn: Callable[[CxO, List[CxO]], CxO],
) -> Callable[[object], object]:
    plan = _build_step_plan(world)
    ordered_node_ids = plan.ordered_node_ids
    parent_indices = plan.parent_indices
    node_count = len(ordered_node_ids)

    def _step_fast(cur_world: object) -> object:
        old_states_dict = cur_world.states
        old_states = [old_states_dict[nid] for nid in ordered_node_ids]
        new_states: List[CxO] = [old_states[0] for _ in range(node_count)]

        for i, parent_ixs in enumerate(parent_indices):
            msgs = [old_states[j] for j in parent_ixs]
            new_states[i] = update_rule_fn(old_states[i], msgs)

        next_states = {ordered_node_ids[i]: new_states[i] for i in range(node_count)}
        return cur_world.__class__(
            node_ids=cur_world.node_ids,
            parents=cur_world.parents,
            states=next_states,
            tick=cur_world.tick + 1,
        )

    return _step_fast


def _safe_ratio(num: int, den: int) -> float:
    if den <= 0:
        return 0.0
    return float(num) / float(den)


def _states_equal(a: object, b: object) -> bool:
    if a.tick != b.tick:
        return False
    if list(a.node_ids) != list(b.node_ids):
        return False
    for nid in a.node_ids:
        if a.states[nid] != b.states[nid]:
            return False
    return True


def _step_weinberg_row(
    world: object,
    position_node_ids: Sequence[str],
    min_pos: int,
    max_pos: int,
    left_pos: int,
    right_pos: int,
    overlap_start_tick: int,
) -> Dict[str, object]:
    overlap_min = max(min_pos, right_pos - world.tick)
    overlap_max = min(max_pos, left_pos + world.tick)
    overlap_count = 0
    u1_inclusive_sum = 0
    weak_inclusive_sum = 0
    weak_exclusive_sum = 0
    ew_sum = 0
    exclusive_u1_sum = 0
    if overlap_min <= overlap_max:
        start_idx = overlap_min - min_pos
        end_idx = overlap_max - min_pos
        overlap_count = end_idx - start_idx + 1
        for idx in range(start_idx, end_idx + 1):
            state = world.states[position_node_ids[idx]]
            u1_inclusive_sum += _channel_energy(state, MASK_U1_INCLUSIVE)
            weak_inclusive_sum += _channel_energy(state, MASK_WEAK_INCLUSIVE)
            weak_exclusive_sum += _channel_energy(state, MASK_WEAK_EXCLUSIVE)
            ew_sum += _channel_energy(state, MASK_EW)
            exclusive_u1_sum += _channel_energy(state, MASK_EXCLUSIVE_U1)

    sin2_raw = _safe_ratio(u1_inclusive_sum, ew_sum)
    sin2_exclusive_u1 = _safe_ratio(exclusive_u1_sum, ew_sum)
    sin2_from_couplings = _safe_ratio(u1_inclusive_sum, u1_inclusive_sum + weak_exclusive_sum)
    target_mz = 0.23122
    target_uv = 0.25
    return {
        "global_tick": int(world.tick),
        "overlap_started": bool(world.tick >= overlap_start_tick),
        "overlap_node_count": int(overlap_count),
        "u1_inclusive_load": int(u1_inclusive_sum),
        "weak_inclusive_load": int(weak_inclusive_sum),
        "weak_exclusive_load": int(weak_exclusive_sum),
        "ew_load": int(ew_sum),
        "exclusive_u1_load": int(exclusive_u1_sum),
        "sin2_theta_w_raw": sin2_raw,
        "sin2_theta_w_exclusive_u1": sin2_exclusive_u1,
        "sin2_theta_w_from_couplings": sin2_from_couplings,
        "gap_raw_vs_mz_target": sin2_raw - target_mz,
        "gap_exclusive_vs_mz_target": sin2_exclusive_u1 - target_mz,
        "gap_exclusive_vs_uv_quarter": sin2_exclusive_u1 - target_uv,
    }


def _simulate_case(
    cfg: CaseConfig,
    preconditioning_ticks: int = 0,
    step_fn: Callable[[object], object] = step_integer,
    update_rule_fn: Callable[[CxO, List[CxO]], CxO] | None = None,
    world_cls: Type[object] = World,
    use_fast_step: bool = True,
    verify_fast_step: bool = False,
) -> Dict[str, object]:
    world, positions, left_pos, right_pos = _build_world(
        edge_distance=cfg.edge_distance,
        steps=cfg.steps,
        phase_offset=cfg.phase_offset,
        world_cls=world_cls,
    )

    min_pos = positions[0]
    max_pos = positions[-1]
    position_node_ids = [_node_name(p) for p in positions]
    overlap_start_tick = (cfg.edge_distance + 1) // 2

    if use_fast_step and update_rule_fn is not None:
        stepper = _build_fast_stepper(world, update_rule_fn)
    else:
        stepper = step_fn

    if verify_fast_step and use_fast_step and update_rule_fn is not None:
        ref_world = step_fn(world)
        fast_world = stepper(world)
        if not _states_equal(ref_world, fast_world):
            raise RuntimeError(f"fast-step verification failed for case {cfg.case_id}")
    preconditioning_rows: List[Dict[str, object]] = []
    step_rows: List[Dict[str, object]] = []

    for k in range(1, preconditioning_ticks + 1):
        world = stepper(world)
        row = _step_weinberg_row(
            world=world,
            position_node_ids=position_node_ids,
            min_pos=min_pos,
            max_pos=max_pos,
            left_pos=left_pos,
            right_pos=right_pos,
            overlap_start_tick=overlap_start_tick,
        )
        row["stage"] = "precondition"
        row["stage_tick"] = k
        preconditioning_rows.append(row)

    post_overlap_raw_measurement: List[float] = []
    post_overlap_exclusive_measurement: List[float] = []
    post_overlap_raw_all: List[float] = []
    post_overlap_exclusive_all: List[float] = []
    for t in range(1, cfg.steps + 1):
        world = stepper(world)
        row = _step_weinberg_row(
            world=world,
            position_node_ids=position_node_ids,
            min_pos=min_pos,
            max_pos=max_pos,
            left_pos=left_pos,
            right_pos=right_pos,
            overlap_start_tick=overlap_start_tick,
        )
        row["stage"] = "measure"
        row["stage_tick"] = t
        step_rows.append(row)
        if row["overlap_started"]:
            post_overlap_raw_measurement.append(row["sin2_theta_w_raw"])
            post_overlap_exclusive_measurement.append(row["sin2_theta_w_exclusive_u1"])

    for row in preconditioning_rows:
        if row["overlap_started"]:
            post_overlap_raw_all.append(row["sin2_theta_w_raw"])
            post_overlap_exclusive_all.append(row["sin2_theta_w_exclusive_u1"])
    post_overlap_raw_all.extend(post_overlap_raw_measurement)
    post_overlap_exclusive_all.extend(post_overlap_exclusive_measurement)

    mean_raw_post_measurement = (
        sum(post_overlap_raw_measurement) / len(post_overlap_raw_measurement)
        if post_overlap_raw_measurement
        else 0.0
    )
    mean_exclusive_post_measurement = (
        sum(post_overlap_exclusive_measurement) / len(post_overlap_exclusive_measurement)
        if post_overlap_exclusive_measurement
        else 0.0
    )
    mean_raw_post_all = (
        sum(post_overlap_raw_all) / len(post_overlap_raw_all) if post_overlap_raw_all else 0.0
    )
    mean_exclusive_post_all = (
        sum(post_overlap_exclusive_all) / len(post_overlap_exclusive_all)
        if post_overlap_exclusive_all
        else 0.0
    )
    final_measurement = step_rows[-1] if step_rows else None

    return {
        "case_id": cfg.case_id,
        "edge_distance": cfg.edge_distance,
        "steps": cfg.steps,
        "phase_offset": cfg.phase_offset,
        "preconditioning_ticks": preconditioning_ticks,
        "overlap_start_tick": overlap_start_tick,
        "summary": {
            "mean_sin2_raw_post_overlap_measurement": mean_raw_post_measurement,
            "mean_sin2_exclusive_post_overlap_measurement": mean_exclusive_post_measurement,
            "mean_sin2_raw_post_overlap_all": mean_raw_post_all,
            "mean_sin2_exclusive_post_overlap_all": mean_exclusive_post_all,
            "final_sin2_raw": (final_measurement["sin2_theta_w_raw"] if final_measurement else 0.0),
            "final_sin2_exclusive_u1": (
                final_measurement["sin2_theta_w_exclusive_u1"] if final_measurement else 0.0
            ),
            "final_gap_exclusive_vs_mz_target": (
                final_measurement["gap_exclusive_vs_mz_target"] if final_measurement else 0.0
            ),
        },
        "preconditioning_rows": preconditioning_rows,
        "step_rows": step_rows,
    }


def _simulate_case_worker(task: Tuple[CaseConfig, int, bool, str, bool, bool]) -> Dict[str, object]:
    cfg, preconditioning_ticks, include_cold_baseline, kernel_profile, use_fast_step, verify_fast_step = task
    profile = _select_kernel_profile(kernel_profile)
    case_payload = _simulate_case(
        cfg=cfg,
        preconditioning_ticks=preconditioning_ticks,
        step_fn=profile.step_fn,
        update_rule_fn=profile.update_rule_fn,
        world_cls=profile.world_cls,
        use_fast_step=use_fast_step,
        verify_fast_step=verify_fast_step,
    )
    if include_cold_baseline and preconditioning_ticks > 0:
        cold_baseline = _simulate_case(
            cfg=cfg,
            preconditioning_ticks=0,
            step_fn=profile.step_fn,
            update_rule_fn=profile.update_rule_fn,
            world_cls=profile.world_cls,
            use_fast_step=use_fast_step,
            verify_fast_step=verify_fast_step,
        )
        cold_mean = cold_baseline["summary"]["mean_sin2_exclusive_post_overlap_measurement"]
        warm_mean = case_payload["summary"]["mean_sin2_exclusive_post_overlap_measurement"]
        case_payload["cold_baseline_summary"] = cold_baseline["summary"]
        case_payload["summary"]["delta_mean_exclusive_vs_cold_measurement"] = warm_mean - cold_mean
    return case_payload


def _build_payload(
    payload_cases: Sequence[Dict[str, object]],
    preconditioning_ticks: int,
    include_cold_baseline: bool,
    max_steps: int | None,
    kernel_profile: str,
    kernel_path: str,
) -> Dict[str, object]:
    return {
        "schema_version": "weinberg_20_cases_v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "kernel": kernel_path,
        "kernel_profile": kernel_profile,
        "definition": {
            "signal": "sin2(theta_W)=g'^2/(g'^2+g^2) from overlap-channel loads",
            "overlap_rule": "lightcone overlap when abs(x-left)<=t and abs(x-right)<=t",
            "phase_offset_rule": "right electroweak seed receives P temporal commits before tick 0",
            "mask_contract": {
                "u1_inclusive": [0, 7],
                "weak_inclusive": [1, 6, 7],
                "weak_exclusive": [1, 6],
                "electroweak": [0, 1, 6, 7],
                "exclusive_u1": [0],
            },
            "preconditioning_rule": (
                "warm start applies deterministic update ticks before measurement so vacuum dressing "
                "and early exchange are present at measurement tick 1"
            ),
            "target_values": {
                "sin2_theta_w_mz": 0.23122,
                "sin2_theta_w_uv_exclusive": 0.25,
            },
            "unity_profile_note": (
                "kernel_profile=unity is non-canonical; coefficients are projected to {0,+1,-1,+i,-i} "
                "after fold/update."
            ),
        },
        "preconditioning_ticks": preconditioning_ticks,
        "include_cold_baseline": include_cold_baseline,
        "max_steps_cap": max_steps,
        "case_count": len(payload_cases),
        "cases": list(payload_cases),
    }


def _csv_fieldnames() -> List[str]:
    return [
        "case_id",
        "edge_distance",
        "steps",
        "phase_offset",
        "preconditioning_ticks",
        "overlap_start_tick",
        "stage",
        "stage_tick",
        "global_tick",
        "overlap_started",
        "overlap_node_count",
        "u1_inclusive_load",
        "weak_inclusive_load",
        "weak_exclusive_load",
        "ew_load",
        "exclusive_u1_load",
        "sin2_theta_w_raw",
        "sin2_theta_w_exclusive_u1",
        "sin2_theta_w_from_couplings",
        "gap_raw_vs_mz_target",
        "gap_exclusive_vs_mz_target",
        "gap_exclusive_vs_uv_quarter",
    ]


def write_outputs(payload: Dict[str, object], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "weinberg_20_cases.json"
    csv_path = out_dir / "weinberg_20_cases.csv"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    fieldnames = _csv_fieldnames()
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for case in payload["cases"]:
            case_obj = case
            all_rows = list(case_obj.get("preconditioning_rows", [])) + list(case_obj["step_rows"])
            for row in all_rows:
                w.writerow(
                    {
                        "case_id": case_obj["case_id"],
                        "edge_distance": case_obj["edge_distance"],
                        "steps": case_obj["steps"],
                        "phase_offset": case_obj["phase_offset"],
                        "preconditioning_ticks": case_obj.get("preconditioning_ticks", 0),
                        "overlap_start_tick": case_obj["overlap_start_tick"],
                        "stage": row["stage"],
                        "stage_tick": row["stage_tick"],
                        "global_tick": row["global_tick"],
                        "overlap_started": row["overlap_started"],
                        "overlap_node_count": row["overlap_node_count"],
                        "u1_inclusive_load": row["u1_inclusive_load"],
                        "weak_inclusive_load": row["weak_inclusive_load"],
                        "weak_exclusive_load": row["weak_exclusive_load"],
                        "ew_load": row["ew_load"],
                        "exclusive_u1_load": row["exclusive_u1_load"],
                        "sin2_theta_w_raw": row["sin2_theta_w_raw"],
                        "sin2_theta_w_exclusive_u1": row["sin2_theta_w_exclusive_u1"],
                        "sin2_theta_w_from_couplings": row["sin2_theta_w_from_couplings"],
                        "gap_raw_vs_mz_target": row["gap_raw_vs_mz_target"],
                        "gap_exclusive_vs_mz_target": row["gap_exclusive_vs_mz_target"],
                        "gap_exclusive_vs_uv_quarter": row["gap_exclusive_vs_uv_quarter"],
                    }
                )


def _case_dir(out_dir: Path) -> Path:
    return out_dir / CASE_DIR_NAME


def _case_json_path(out_dir: Path, case_id: str) -> Path:
    return _case_dir(out_dir) / f"{case_id}.json"


def _case_csv_path(out_dir: Path, case_id: str) -> Path:
    return _case_dir(out_dir) / f"{case_id}.csv"


def _checkpoint_path(out_dir: Path) -> Path:
    return out_dir / CHECKPOINT_NAME


def _partial_summary_path(out_dir: Path) -> Path:
    return out_dir / PARTIAL_SUMMARY_NAME


def _ordered_case_ids(cases: Sequence[CaseConfig]) -> List[str]:
    return [cfg.case_id for cfg in cases]


def _write_case_artifacts(out_dir: Path, case_obj: Dict[str, object]) -> None:
    case_id = str(case_obj["case_id"])
    _case_dir(out_dir).mkdir(parents=True, exist_ok=True)
    _case_json_path(out_dir, case_id).write_text(json.dumps(case_obj, indent=2), encoding="utf-8")

    fieldnames = _csv_fieldnames()
    with _case_csv_path(out_dir, case_id).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        all_rows = list(case_obj.get("preconditioning_rows", [])) + list(case_obj["step_rows"])
        for row in all_rows:
            w.writerow(
                {
                    "case_id": case_obj["case_id"],
                    "edge_distance": case_obj["edge_distance"],
                    "steps": case_obj["steps"],
                    "phase_offset": case_obj["phase_offset"],
                    "preconditioning_ticks": case_obj.get("preconditioning_ticks", 0),
                    "overlap_start_tick": case_obj["overlap_start_tick"],
                    "stage": row["stage"],
                    "stage_tick": row["stage_tick"],
                    "global_tick": row["global_tick"],
                    "overlap_started": row["overlap_started"],
                    "overlap_node_count": row["overlap_node_count"],
                    "u1_inclusive_load": row["u1_inclusive_load"],
                    "weak_inclusive_load": row["weak_inclusive_load"],
                    "weak_exclusive_load": row["weak_exclusive_load"],
                    "ew_load": row["ew_load"],
                    "exclusive_u1_load": row["exclusive_u1_load"],
                    "sin2_theta_w_raw": row["sin2_theta_w_raw"],
                    "sin2_theta_w_exclusive_u1": row["sin2_theta_w_exclusive_u1"],
                    "sin2_theta_w_from_couplings": row["sin2_theta_w_from_couplings"],
                    "gap_raw_vs_mz_target": row["gap_raw_vs_mz_target"],
                    "gap_exclusive_vs_mz_target": row["gap_exclusive_vs_mz_target"],
                    "gap_exclusive_vs_uv_quarter": row["gap_exclusive_vs_uv_quarter"],
                }
            )


def _write_checkpoint(
    out_dir: Path,
    settings: Dict[str, object],
    case_order: Sequence[str],
    completed_case_ids: Sequence[str],
    finalized: bool = False,
) -> None:
    checkpoint = {
        "schema_version": "weinberg_20_cases_checkpoint_v1",
        "updated_at_utc": datetime.now(UTC).isoformat(),
        "settings": settings,
        "case_order": list(case_order),
        "completed_case_ids": list(completed_case_ids),
        "completed_case_count": len(completed_case_ids),
        "finalized": bool(finalized),
    }
    _checkpoint_path(out_dir).write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")


def _write_partial_summary(
    out_dir: Path,
    case_order: Sequence[str],
    completed_cases: Dict[str, Dict[str, object]],
    settings: Dict[str, object],
) -> None:
    summaries: List[Dict[str, object]] = []
    for case_id in case_order:
        case_obj = completed_cases.get(case_id)
        if case_obj is None:
            continue
        summaries.append(
            {
                "case_id": case_obj["case_id"],
                "edge_distance": case_obj["edge_distance"],
                "steps": case_obj["steps"],
                "phase_offset": case_obj["phase_offset"],
                "summary": case_obj["summary"],
            }
        )

    payload = {
        "schema_version": "weinberg_20_cases_partial_v1",
        "updated_at_utc": datetime.now(UTC).isoformat(),
        "settings": settings,
        "completed_case_count": len(summaries),
        "case_summaries": summaries,
    }
    _partial_summary_path(out_dir).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _load_completed_cases_from_resume(
    out_dir: Path,
    settings: Dict[str, object],
    case_order: Sequence[str],
) -> Dict[str, Dict[str, object]]:
    checkpoint_file = _checkpoint_path(out_dir)
    if not checkpoint_file.exists():
        return {}

    checkpoint = json.loads(checkpoint_file.read_text(encoding="utf-8"))
    if checkpoint.get("settings") != settings:
        raise ValueError(
            "Checkpoint settings mismatch. Use matching parameters for --resume, "
            "or run without --resume."
        )

    completed_cases: Dict[str, Dict[str, object]] = {}
    for case_id in checkpoint.get("completed_case_ids", []):
        if case_id not in case_order:
            continue
        path = _case_json_path(out_dir, case_id)
        if path.exists():
            completed_cases[case_id] = json.loads(path.read_text(encoding="utf-8"))
    return completed_cases


def run_cases(
    preconditioning_ticks: int = 0,
    include_cold_baseline: bool = False,
    case_limit: int = 20,
    max_steps: int | None = None,
    kernel_profile: str = "integer",
    workers: int = 1,
    use_fast_step: bool = True,
    verify_fast_step: bool = False,
) -> Dict[str, object]:
    profile = _select_kernel_profile(kernel_profile)

    cases = _make_case_grid(max_steps=max_steps)
    if case_limit < 1 or case_limit > len(cases):
        raise ValueError(f"--case-limit must be between 1 and {len(cases)}")
    cases = cases[:case_limit]

    tasks = [
        (
            cfg,
            preconditioning_ticks,
            include_cold_baseline,
            kernel_profile,
            use_fast_step,
            verify_fast_step,
        )
        for cfg in cases
    ]

    payload_by_id: Dict[str, Dict[str, object]] = {}
    if workers == 1:
        for task in tasks:
            case_payload = _simulate_case_worker(task)
            payload_by_id[case_payload["case_id"]] = case_payload
    else:
        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(_simulate_case_worker, task) for task in tasks]
            for fut in concurrent.futures.as_completed(futures):
                case_payload = fut.result()
                payload_by_id[case_payload["case_id"]] = case_payload

    ordered = [payload_by_id[cfg.case_id] for cfg in cases]
    return _build_payload(
        payload_cases=ordered,
        preconditioning_ticks=preconditioning_ticks,
        include_cold_baseline=include_cold_baseline,
        max_steps=max_steps,
        kernel_profile=kernel_profile,
        kernel_path=profile.kernel_path,
    )


def execute_cases_incremental(
    out_dir: Path,
    preconditioning_ticks: int = 0,
    include_cold_baseline: bool = False,
    case_limit: int = 20,
    max_steps: int | None = None,
    kernel_profile: str = "integer",
    workers: int = 1,
    use_fast_step: bool = True,
    verify_fast_step: bool = False,
    resume: bool = False,
) -> Dict[str, object]:
    profile = _select_kernel_profile(kernel_profile)
    cases = _make_case_grid(max_steps=max_steps)
    if case_limit < 1 or case_limit > len(cases):
        raise ValueError(f"--case-limit must be between 1 and {len(cases)}")
    cases = cases[:case_limit]
    case_order = _ordered_case_ids(cases)

    settings = {
        "preconditioning_ticks": preconditioning_ticks,
        "include_cold_baseline": include_cold_baseline,
        "case_limit": case_limit,
        "max_steps": max_steps,
        "kernel_profile": kernel_profile,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    _case_dir(out_dir).mkdir(parents=True, exist_ok=True)

    if resume:
        completed_cases = _load_completed_cases_from_resume(out_dir, settings, case_order)
    else:
        completed_cases = {}

    pending = [cfg for cfg in cases if cfg.case_id not in completed_cases]
    total = len(cases)
    done = len(completed_cases)

    if done:
        print(f"Resuming from checkpoint: {done}/{total} cases already completed")

    tasks = [
        (
            cfg,
            preconditioning_ticks,
            include_cold_baseline,
            kernel_profile,
            use_fast_step,
            verify_fast_step,
        )
        for cfg in pending
    ]

    if workers == 1:
        for task in tasks:
            cfg = task[0]
            case_payload = _simulate_case_worker(task)
            completed_cases[cfg.case_id] = case_payload
            _write_case_artifacts(out_dir, case_payload)
            done += 1
            completed_ids = [cid for cid in case_order if cid in completed_cases]
            _write_checkpoint(out_dir, settings, case_order, completed_ids)
            _write_partial_summary(out_dir, case_order, completed_cases, settings)
            mean_value = case_payload["summary"]["mean_sin2_exclusive_post_overlap_measurement"]
            print(f"[{done:02d}/{total}] completed {cfg.case_id} | mean sin2_exclusive={mean_value:.6f}")
    else:
        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(_simulate_case_worker, task): task[0] for task in tasks}
            for future in concurrent.futures.as_completed(futures):
                cfg = futures[future]
                case_payload = future.result()
                completed_cases[cfg.case_id] = case_payload
                _write_case_artifacts(out_dir, case_payload)
                done += 1
                completed_ids = [cid for cid in case_order if cid in completed_cases]
                _write_checkpoint(out_dir, settings, case_order, completed_ids)
                _write_partial_summary(out_dir, case_order, completed_cases, settings)
                mean_value = case_payload["summary"]["mean_sin2_exclusive_post_overlap_measurement"]
                print(f"[{done:02d}/{total}] completed {cfg.case_id} | mean sin2_exclusive={mean_value:.6f}")

    missing = [cid for cid in case_order if cid not in completed_cases]
    if missing:
        raise RuntimeError(f"Missing completed case artifacts for: {missing}")

    ordered_cases = [completed_cases[cfg.case_id] for cfg in cases]
    payload = _build_payload(
        payload_cases=ordered_cases,
        preconditioning_ticks=preconditioning_ticks,
        include_cold_baseline=include_cold_baseline,
        max_steps=max_steps,
        kernel_profile=kernel_profile,
        kernel_path=profile.kernel_path,
    )
    write_outputs(payload, out_dir)

    completed_ids = [cid for cid in case_order if cid in completed_cases]
    _write_checkpoint(out_dir, settings, case_order, completed_ids, finalized=True)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate 20 Weinberg-angle COG test cases in world_code.")
    parser.add_argument(
        "--output-dir",
        default=str(RESULTS_ROOT),
        help="Output directory for JSON/CSV artifacts.",
    )
    parser.add_argument(
        "--preconditioning-ticks",
        type=int,
        default=0,
        help="Warm-start ticks to run before measurement.",
    )
    parser.add_argument(
        "--include-cold-baseline",
        action="store_true",
        help="Also simulate a cold baseline per case and include summary deltas.",
    )
    parser.add_argument(
        "--case-limit",
        type=int,
        default=20,
        help="Number of cases from the canonical 20-case grid to execute.",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=None,
        help="Optional cap applied to per-case measurement steps.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually run case generation (default is dry-run safety).",
    )
    parser.add_argument(
        "--kernel-profile",
        choices=["integer", "unity"],
        default="integer",
        help="Update kernel profile. 'integer' is canonical, 'unity' is exploratory.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of case-level worker processes.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from weinberg_20_cases.checkpoint.json if available.",
    )
    parser.add_argument(
        "--disable-fast-step",
        action="store_true",
        help="Disable precomputed deterministic stepping and use kernel step() directly.",
    )
    parser.add_argument(
        "--verify-fast-step",
        action="store_true",
        help="Per-case one-tick equivalence check between fast-step and kernel step().",
    )
    args = parser.parse_args()

    if args.preconditioning_ticks < 0:
        raise ValueError("--preconditioning-ticks must be >= 0")
    if args.max_steps is not None and args.max_steps < 1:
        raise ValueError("--max-steps must be >= 1 when provided")
    if args.workers < 1:
        raise ValueError("--workers must be >= 1")
    if args.verify_fast_step and args.disable_fast_step:
        raise ValueError("--verify-fast-step requires fast-step enabled.")

    if not args.execute:
        raise SystemExit(
            "Dry-run safety: add --execute to run generation. "
            "Example: python world_code/Python_code/generate_weinberg_20_cases.py "
            "--execute --workers 8 --resume --preconditioning-ticks 12 --include-cold-baseline"
        )

    payload = execute_cases_incremental(
        out_dir=Path(args.output_dir),
        preconditioning_ticks=args.preconditioning_ticks,
        include_cold_baseline=args.include_cold_baseline,
        case_limit=args.case_limit,
        max_steps=args.max_steps,
        kernel_profile=args.kernel_profile,
        workers=args.workers,
        use_fast_step=not args.disable_fast_step,
        verify_fast_step=args.verify_fast_step,
        resume=args.resume,
    )
    print(f"Generated {payload['case_count']} cases")
    print(f"Wrote {Path(args.output_dir) / 'weinberg_20_cases.json'}")
    print(f"Wrote {Path(args.output_dir) / 'weinberg_20_cases.csv'}")
    print(f"Checkpoint: {Path(args.output_dir) / CHECKPOINT_NAME}")
    print(f"Partial summary: {Path(args.output_dir) / PARTIAL_SUMMARY_NAME}")


if __name__ == "__main__":
    main()
