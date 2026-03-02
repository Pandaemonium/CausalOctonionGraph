"""Autonomous overnight runner for v3 motif search.

This runner executes indefinitely (unless externally stopped), alternating:
1) photon-first scan batches,
2) detector exclusivity probes,
3) chirality/conjugation proxy panels,
4) periodic literature-log checkpoints and course corrections.

Artifacts:
- cog_v3/sources/v3_overnight_progress_log_v1.md
- cog_v3/sources/v3_overnight_state_v1.json
- cog_v3/sources/v3_overnight_batch_summary_v1.json
- cog_v3/sources/v3_overnight_runs_v1/*
"""

from __future__ import annotations

import argparse
import json
import math
import random
import time
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np

from cog_v3.python import kernel_octavian240_accel_v1 as accel
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]
RUN_DIR = ROOT / "cog_v3" / "sources" / "v3_overnight_runs_v1"
LOG_MD = ROOT / "cog_v3" / "sources" / "v3_overnight_progress_log_v1.md"
STATE_JSON = ROOT / "cog_v3" / "sources" / "v3_overnight_state_v1.json"
SUMMARY_JSON = ROOT / "cog_v3" / "sources" / "v3_overnight_batch_summary_v1.json"
LIT_LOG_MD = ROOT / "cog_v3" / "sources" / "v3_lit_review_log_v1.md"
LONG_BACKLOG_MD = ROOT / "cog_v3" / "sources" / "v3_long_horizon_research_backlog_v1.md"


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _append_log(lines: Sequence[str]) -> None:
    LOG_MD.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_MD.exists():
        LOG_MD.write_text(
            "# v3 Overnight Progress Log (v1)\n\n"
            f"Started: {_now_utc()}\n\n",
            encoding="utf-8",
        )
    with LOG_MD.open("a", encoding="utf-8") as f:
        for line in lines:
            f.write(line.rstrip() + "\n")
        f.write("\n")


def _append_lit_log(entry: Dict[str, Any]) -> None:
    LIT_LOG_MD.parent.mkdir(parents=True, exist_ok=True)
    if not LIT_LOG_MD.exists():
        LIT_LOG_MD.write_text("# v3 Literature Review Log (v1)\n\n", encoding="utf-8")
    ts = str(entry.get("timestamp", _now_utc()))
    lines = [
        f"### Entry {ts}",
        "",
        f"1. `focus_type`: `{entry.get('focus_type', 'long_horizon')}`",
        f"2. `question`: {entry.get('question', '-')}",
        f"3. `sources_checked`: {entry.get('sources_checked', '-')}",
        f"4. `key_finding`: {entry.get('key_finding', '-')}",
        f"5. `confidence`: `{entry.get('confidence', 'medium')}`",
        f"6. `immediate_action`: `{entry.get('immediate_action', 'defer')}`",
        f"7. `reason`: {entry.get('reason', '-')}",
        f"8. `follow_up_test`: {entry.get('follow_up_test', '-')}",
        "",
    ]
    with LIT_LOG_MD.open("a", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")


def _ensure_backlog_note() -> None:
    if not LONG_BACKLOG_MD.exists():
        LONG_BACKLOG_MD.parent.mkdir(parents=True, exist_ok=True)
        LONG_BACKLOG_MD.write_text(
            "# v3 Long-Horizon Research Backlog (v1)\n\n"
            "Initialized by autonomous runner.\n",
            encoding="utf-8",
        )


def _basis_id(i: int, sign: int = 1) -> int:
    v = [k.Fraction(0, 1) for _ in range(8)]
    v[int(i)] = k.Fraction(int(sign), 1)
    return int(k.ALPHABET_INDEX[tuple(v)])  # type: ignore[index]


def _idx(x: int, y: int, z: int, ny: int, nz: int) -> int:
    return (x * ny + y) * nz + z


def _slice_nonvac_count(world: np.ndarray, nx: int, ny: int, nz: int, x: int) -> int:
    base = x * ny * nz
    slab = world[base : base + ny * nz]
    return int(np.count_nonzero(slab != np.uint16(k.IDENTITY_ID)))


def _slice_nonvac_count_axis(
    world: np.ndarray, nx: int, ny: int, nz: int, axis: str, pos: int
) -> int:
    a = str(axis)
    if a == "x":
        return _slice_nonvac_count(world, nx, ny, nz, int(pos))
    if a == "y":
        cnt = 0
        y = int(pos)
        for x in range(nx):
            base = (x * ny + y) * nz
            cnt += int(np.count_nonzero(world[base : base + nz] != np.uint16(k.IDENTITY_ID)))
        return int(cnt)
    if a == "z":
        cnt = 0
        z = int(pos)
        for x in range(nx):
            for y in range(ny):
                idx = (x * ny + y) * nz + z
                if world[idx] != np.uint16(k.IDENTITY_ID):
                    cnt += 1
        return int(cnt)
    raise ValueError(f"Unknown axis: {axis}")


def _apply_photon_sheet_axis(
    world_l: List[int],
    nx: int,
    ny: int,
    nz: int,
    *,
    axis: str,
    state_id: int,
    kick_id: int,
) -> None:
    cx, cy, cz = nx // 2, ny // 2, nz // 2
    a = str(axis)
    if a == "x":
        x0 = max(1, nx // 4)
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                y = cy + dy
                z = cz + dz
                idx = _idx(x0, y, z, ny, nz)
                world_l[idx] = int(k.multiply_ids(int(kick_id), int(state_id)))
        return
    if a == "y":
        y0 = max(1, ny // 4)
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                x = cx + dx
                z = cz + dz
                idx = _idx(x, y0, z, ny, nz)
                world_l[idx] = int(k.multiply_ids(int(kick_id), int(state_id)))
        return
    if a == "z":
        z0 = max(1, nz // 4)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                x = cx + dx
                y = cy + dy
                idx = _idx(x, y, z0, ny, nz)
                world_l[idx] = int(k.multiply_ids(int(kick_id), int(state_id)))
        return
    raise ValueError(f"Unknown axis: {axis}")


def _apply_blob3(
    world_l: List[int],
    nx: int,
    ny: int,
    nz: int,
    *,
    state_id: int,
    kick_id: int,
) -> None:
    cx, cy, cz = nx // 2, ny // 2, nz // 2
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                x = cx + dx
                y = cy + dy
                z = cz + dz
                if 0 <= x < nx and 0 <= y < ny and 0 <= z < nz:
                    idx = _idx(x, y, z, ny, nz)
                    world_l[idx] = int(k.multiply_ids(int(kick_id), int(state_id)))


def _apply_single(
    world_l: List[int],
    nx: int,
    ny: int,
    nz: int,
    *,
    state_id: int,
    kick_id: int,
) -> None:
    cx, cy, cz = nx // 2, ny // 2, nz // 2
    idx = _idx(cx, cy, cz, ny, nz)
    world_l[idx] = int(k.multiply_ids(int(kick_id), int(state_id)))


@dataclass
class ProbeParams:
    runs: int = 16
    ticks: int = 120
    size_x: int = 39
    size_y: int = 11
    size_z: int = 11
    vacuum_noise_prob: float = 0.004
    detector_margin: int = 1
    seed_state_id: int = 0
    kick_id: int = 0
    global_seed: int = 1337
    axis: str = "x"
    channel_policy_id: str = "uniform_all"
    policy_seed: int = 0


def _random_non_identity_id(rng: random.Random) -> int:
    while True:
        x = rng.randrange(0, k.ALPHABET_SIZE)
        if x != k.IDENTITY_ID:
            return int(x)


def _inject_vacuum_noise(
    world: np.ndarray, nx: int, ny: int, nz: int, p: float, rng: random.Random
) -> int:
    n = int(nx * ny * nz)
    if p <= 0.0:
        return 0
    count = 0
    for i in range(n):
        if rng.random() < p:
            world[i] = np.uint16(_random_non_identity_id(rng))
            count += 1
    return int(count)


def _offset_class(dx: int, dy: int, dz: int) -> str:
    nnz = int((dx != 0) + (dy != 0) + (dz != 0))
    if nnz <= 1:
        return "axis"
    if nnz == 2:
        return "face"
    return "corner"


def _prepare_policy_neighbor_tables(nx: int, ny: int, nz: int, stencil_id: str) -> Dict[str, np.ndarray]:
    offsets = accel.offsets_for_stencil(str(stencil_id))
    axis = [o for o in offsets if _offset_class(int(o[0]), int(o[1]), int(o[2])) == "axis"]
    face = [o for o in offsets if _offset_class(int(o[0]), int(o[1]), int(o[2])) == "face"]
    corner = [o for o in offsets if _offset_class(int(o[0]), int(o[1]), int(o[2])) == "corner"]

    def tbl(v: List[Tuple[int, int, int]]) -> np.ndarray:
        vv = v if len(v) > 0 else axis
        return accel.build_neighbor_table(int(nx), int(ny), int(nz), vv)

    axis_face = axis + face if len(face) > 0 else axis
    axis_corner = axis + corner if len(corner) > 0 else axis
    all_offsets = axis + face + corner if len(face) + len(corner) > 0 else axis
    return {
        "axis": tbl(axis),
        "axis_face": tbl(axis_face),
        "axis_corner": tbl(axis_corner),
        "all": tbl(all_offsets),
    }


def _policy_combo(policy_id: str, tick: int, seed: int) -> str:
    pid = str(policy_id)
    t = int(tick)
    if pid == "uniform_all":
        return "all"
    if pid == "deterministic_cycle_v1":
        m = t % 12
        face_on = m in {0, 1, 2, 3, 4, 6, 8, 10}
        corner_on = m in {0, 1, 3, 5, 7, 9, 10}
        if face_on and corner_on:
            return "all"
        if face_on and (not corner_on):
            return "axis_face"
        if (not face_on) and corner_on:
            return "axis_corner"
        return "axis"
    if pid == "stochastic_gating_v1":
        rr = random.Random(int(seed) + 104729 * (t + 1))
        face_on = rr.random() < 0.70710678
        corner_on = rr.random() < 0.57735027
        if face_on and corner_on:
            return "all"
        if face_on and (not corner_on):
            return "axis_face"
        if (not face_on) and corner_on:
            return "axis_corner"
        return "axis"
    return "all"


def run_twin_detector_probe(
    params: ProbeParams,
    *,
    backend: str,
    neighbors: np.ndarray,
    mul_table: np.ndarray,
) -> Dict[str, Any]:
    nx, ny, nz = int(params.size_x), int(params.size_y), int(params.size_z)
    axis = str(params.axis)
    if axis == "x":
        n_axis = nx
    elif axis == "y":
        n_axis = ny
    elif axis == "z":
        n_axis = nz
    else:
        raise ValueError(f"Unknown axis: {axis}")

    left_x = int(params.detector_margin)
    right_x = int(n_axis - 1 - params.detector_margin)
    if left_x >= right_x:
        raise ValueError("Invalid detector placement: left/right overlap.")

    seed_rng = random.Random(int(params.global_seed))
    runs: List[Dict[str, Any]] = []
    left_hits = 0
    right_hits = 0
    tie_hits = 0
    neither_hits = 0
    first_hit_delta_sum = 0.0
    first_hit_delta_count = 0
    policy_tables = _prepare_policy_neighbor_tables(nx, ny, nz, "cube26")

    for rid in range(int(params.runs)):
        rr = random.Random(seed_rng.randrange(0, 2**31 - 1))
        world = accel.make_world(nx, ny, nz, seed_state_id=None)
        _inject_vacuum_noise(world, nx, ny, nz, float(params.vacuum_noise_prob), rr)

        world_l = [int(x) for x in world.tolist()]
        _apply_photon_sheet_axis(
            world_l,
            nx,
            ny,
            nz,
            axis=axis,
            state_id=int(params.seed_state_id),
            kick_id=int(params.kick_id),
        )
        world = np.asarray(world_l, dtype=np.uint16)

        outcome = "none"
        left_first_tick = None
        right_first_tick = None

        for t in range(int(params.ticks)):
            combo = _policy_combo(str(params.channel_policy_id), int(t), int(params.policy_seed) + int(rid) * 31)
            nb = policy_tables.get(combo, neighbors)
            if backend == "python":
                world = accel.step_python(world, nb, mul_table, vac_id=k.IDENTITY_ID, identity_id=k.IDENTITY_ID)
            else:
                world = accel.step_numba_cpu(world, nb, mul_table, vac_id=k.IDENTITY_ID, identity_id=k.IDENTITY_ID)

            l_nonvac = _slice_nonvac_count_axis(world, nx, ny, nz, axis, left_x)
            r_nonvac = _slice_nonvac_count_axis(world, nx, ny, nz, axis, right_x)

            left_on = bool(l_nonvac > 0)
            right_on = bool(r_nonvac > 0)
            if left_on and left_first_tick is None:
                left_first_tick = int(t + 1)
            if right_on and right_first_tick is None:
                right_first_tick = int(t + 1)

            if left_on or right_on:
                if left_on and (not right_on):
                    outcome = "left"
                elif right_on and (not left_on):
                    outcome = "right"
                else:
                    # One-shot absorbing detector with deterministic tie resolution.
                    tie_hits += 1
                    choose_left = bool((int(params.policy_seed) + int(rid) + int(t)) % 2 == 0)
                    outcome = "left" if choose_left else "right"
                break

        if outcome == "left":
            left_hits += 1
        elif outcome == "right":
            right_hits += 1
        else:
            neither_hits += 1

        if left_first_tick is not None and right_first_tick is not None:
            first_hit_delta_sum += float(abs(int(left_first_tick) - int(right_first_tick)))
            first_hit_delta_count += 1

        runs.append(
            {
                "run_id": int(rid),
                "outcome": str(outcome),
                "left_first_tick": left_first_tick,
                "right_first_tick": right_first_tick,
            }
        )

    n = max(1, int(params.runs))
    front_balance = float(abs(left_hits - right_hits) / max(1, left_hits + right_hits))
    double_hit_rate = float(tie_hits / n)
    detector_exclusivity = float(1.0 - double_hit_rate)
    mean_first_hit_delta = float(first_hit_delta_sum / first_hit_delta_count) if first_hit_delta_count > 0 else None
    first_arrivals = []
    for r in runs:
        vals = [x for x in [r["left_first_tick"], r["right_first_tick"]] if x is not None]
        if vals:
            first_arrivals.append(min(vals))
    mean_first_arrival_tick = float(sum(first_arrivals) / len(first_arrivals)) if first_arrivals else None

    if left_hits + right_hits == 0:
        front_class = "diffuse_nonpropagating"
    elif front_balance < 0.20:
        front_class = "two_front_balanced"
    else:
        front_class = "one_front_dominant"

    return {
        "params": asdict(params),
        "backend": backend,
        "front_balance": float(front_balance),
        "double_hit_rate": float(double_hit_rate),
        "detector_exclusivity": float(detector_exclusivity),
        "left_hit_fraction": float(left_hits / n),
        "right_hit_fraction": float(right_hits / n),
        "both_hit_fraction": float(tie_hits / n),
        "neither_hit_fraction": float(neither_hits / n),
        "mean_first_hit_delta_ticks": mean_first_hit_delta,
        "mean_first_arrival_tick": mean_first_arrival_tick,
        "wave_transport_class": front_class,
        "runs": runs,
    }


@dataclass
class FastScanParams:
    ticks: int = 64
    size_x: int = 27
    size_y: int = 9
    size_z: int = 9
    stencil_id: str = "cube26"
    thin_step: int = 4
    max_trials: int = 4
    global_seed: int = 1337
    channel_policy_id: str = "uniform_all"
    policy_seed: int = 0


def _centroid(world: np.ndarray, nx: int, ny: int, nz: int) -> Tuple[float, float, float]:
    ids = np.flatnonzero(world != np.uint16(k.IDENTITY_ID))
    if ids.size == 0:
        return (float(nx // 2), float(ny // 2), float(nz // 2))
    xs = ids // (ny * nz)
    rem = ids % (ny * nz)
    ys = rem // nz
    zs = rem % nz
    return (float(np.mean(xs)), float(np.mean(ys)), float(np.mean(zs)))


def run_fast_motif_scan(params: FastScanParams, *, backend: str) -> Dict[str, Any]:
    nx, ny, nz = int(params.size_x), int(params.size_y), int(params.size_z)
    offsets = accel.offsets_for_stencil(str(params.stencil_id))
    neighbors = accel.build_neighbor_table(nx, ny, nz, offsets)
    policy_tables = _prepare_policy_neighbor_tables(nx, ny, nz, str(params.stencil_id))
    mul_table = accel.build_mul_table()
    rng = random.Random(int(params.global_seed))

    e111 = _basis_id(7, +1)
    e001 = _basis_id(1, +1)
    e010 = _basis_id(2, +1)
    e100 = _basis_id(4, +1)
    e011 = _basis_id(3, +1)

    trial_bank = [
        {"trial_id": "photon_sheet_x_e111_kick_e001", "family": "sheet_x", "state_id": e111, "kick_id": e001},
        {"trial_id": "photon_sheet_y_e111_kick_e010", "family": "sheet_y", "state_id": e111, "kick_id": e010},
        {"trial_id": "photon_sheet_z_e111_kick_e100", "family": "sheet_z", "state_id": e111, "kick_id": e100},
        {"trial_id": "blob3_e111_kick_e011", "family": "blob3", "state_id": e111, "kick_id": e011},
        {"trial_id": "single_e111_kick_e001", "family": "single", "state_id": e111, "kick_id": e001},
    ]
    # Add random exploratory seeds to avoid family collapse.
    families = ["sheet_x", "sheet_y", "sheet_z", "blob3", "single"]
    for i in range(16):
        sid = _random_non_identity_id(rng)
        kid = _random_non_identity_id(rng)
        fam = families[i % len(families)]
        trial_bank.append(
            {
                "trial_id": f"rand_{i:02d}_{fam}",
                "family": fam,
                "state_id": int(sid),
                "kick_id": int(kid),
            }
        )
    rng.shuffle(trial_bank)
    trials = trial_bank[: max(1, int(params.max_trials))]

    rows = []
    for tr in trials:
        world = accel.make_world(nx, ny, nz, seed_state_id=None)
        world_l = [int(x) for x in world.tolist()]
        fam = str(tr["family"])
        if fam == "sheet_x":
            _apply_photon_sheet_axis(world_l, nx, ny, nz, axis="x", state_id=int(tr["state_id"]), kick_id=int(tr["kick_id"]))
        elif fam == "sheet_y":
            _apply_photon_sheet_axis(world_l, nx, ny, nz, axis="y", state_id=int(tr["state_id"]), kick_id=int(tr["kick_id"]))
        elif fam == "sheet_z":
            _apply_photon_sheet_axis(world_l, nx, ny, nz, axis="z", state_id=int(tr["state_id"]), kick_id=int(tr["kick_id"]))
        elif fam == "blob3":
            _apply_blob3(world_l, nx, ny, nz, state_id=int(tr["state_id"]), kick_id=int(tr["kick_id"]))
        elif fam == "single":
            _apply_single(world_l, nx, ny, nz, state_id=int(tr["state_id"]), kick_id=int(tr["kick_id"]))
        else:
            raise ValueError(f"Unknown trial family: {fam}")
        world = np.asarray(world_l, dtype=np.uint16)

        seen = {}
        first_repeat = None
        centroid0 = _centroid(world, nx, ny, nz)
        thin = []
        for t in range(1, int(params.ticks) + 1):
            combo = _policy_combo(str(params.channel_policy_id), int(t), int(params.policy_seed) + int(params.global_seed))
            nb = policy_tables.get(combo, neighbors)
            if backend == "python":
                world = accel.step_python(world, nb, mul_table, vac_id=k.IDENTITY_ID, identity_id=k.IDENTITY_ID)
            else:
                world = accel.step_numba_cpu(world, nb, mul_table, vac_id=k.IDENTITY_ID, identity_id=k.IDENTITY_ID)
            h = hash(world.tobytes())
            if first_repeat is None:
                prev_t = seen.get(h)
                if prev_t is not None:
                    first_repeat = {"t_prev": int(prev_t), "t_now": int(t), "period": int(t - prev_t)}
                else:
                    seen[h] = int(t)
            if (t % max(1, int(params.thin_step)) == 0) or (t == int(params.ticks)):
                c = _centroid(world, nx, ny, nz)
                nonvac = int(np.count_nonzero(world != np.uint16(k.IDENTITY_ID)))
                thin.append(
                    {
                        "tick": int(t),
                        "nonvac_cells": int(nonvac),
                        "centroid": [float(c[0]), float(c[1]), float(c[2])],
                    }
                )

        centroidf = _centroid(world, nx, ny, nz)
        dx = float(centroidf[0] - centroid0[0])
        dy = float(centroidf[1] - centroid0[1])
        dz = float(centroidf[2] - centroid0[2])
        disp = float(math.sqrt(dx * dx + dy * dy + dz * dz))
        nonvac_final = int(np.count_nonzero(world != np.uint16(k.IDENTITY_ID)))
        rec_score = float(1.0 / max(1, first_repeat["period"])) if first_repeat is not None else 0.0
        motion_bonus = float(min(1.0, disp / 3.0))
        lock_bonus = 1.0 if first_repeat is not None else 0.0
        stationary_penalty = 1.0 if disp < 0.5 else 0.0
        score = float(0.75 * rec_score + 0.35 * motion_bonus + 0.20 * lock_bonus - 0.20 * stationary_penalty)
        motion_class = "stationary" if disp < 0.5 else "propagating"

        rows.append(
            {
                "trial_id": str(tr["trial_id"]),
                "seed_family": fam,
                "seed_state_label": k.elem_label(int(tr["state_id"])),
                "kick_label": k.elem_label(int(tr["kick_id"])),
                "first_repeat": first_repeat,
                "recurrence_score": float(rec_score),
                "displacement_norm": float(disp),
                "motion_class": motion_class,
                "nonvac_final": int(nonvac_final),
                "score": float(score),
                "trace_thin": thin,
            }
        )

    rows = sorted(rows, key=lambda r: float(r["score"]), reverse=True)
    checks = {
        "trial_count": int(len(rows)),
        "any_recurrence": bool(any(r["first_repeat"] is not None for r in rows)),
        "any_propagating": bool(any(str(r["motion_class"]) == "propagating" for r in rows)),
        "best_score": float(rows[0]["score"]) if rows else 0.0,
    }
    return {
        "schema_version": "v3_fast_motif_scan_v1",
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "params": asdict(params),
        "checks": checks,
        "trials": rows,
        "event_order_policy": "synchronous_parallel_v1",
    }


def run_isotropy_probe(
    *,
    base_probe: ProbeParams,
    backend: str,
    neighbors: np.ndarray,
    mul_table: np.ndarray,
) -> Dict[str, Any]:
    cube_n = int(max(21, min(31, max(int(base_probe.size_x), int(base_probe.size_y), int(base_probe.size_z)))))
    if cube_n % 2 == 0:
        cube_n += 1
    e001 = _basis_id(1, +1)
    e010 = _basis_id(2, +1)
    e100 = _basis_id(4, +1)
    configs = [
        ("x", e001),
        ("y", e010),
        ("z", e100),
    ]
    rows = []
    speeds = {}
    for axis, kick in configs:
        p = ProbeParams(
            **{
                **asdict(base_probe),
                "axis": axis,
                "kick_id": int(kick),
                "runs": max(8, int(base_probe.runs // 2)),
                "size_x": int(cube_n),
                "size_y": int(cube_n),
                "size_z": int(cube_n),
            }
        )
        pr = run_twin_detector_probe(p, backend=backend, neighbors=neighbors, mul_table=mul_table)
        arrival = pr.get("mean_first_arrival_tick")
        if isinstance(arrival, (int, float)) and float(arrival) > 0:
            dist = int(cube_n // 2 - int(base_probe.detector_margin) - 1)
            speeds[axis] = float(max(1, dist) / float(arrival))
        rows.append(
            {
                "axis": axis,
                "kick_id": int(kick),
                "detector_exclusivity": float(pr["detector_exclusivity"]),
                "front_balance": float(pr["front_balance"]),
                "mean_first_arrival_tick": pr["mean_first_arrival_tick"],
            }
        )
    vals = [float(v) for v in speeds.values() if v is not None and v > 0]
    anisotropy_ratio = float(max(vals) / min(vals)) if len(vals) >= 2 else None
    return {
        "axis_rows": rows,
        "speed_proxy": speeds,
        "anisotropy_ratio_max_over_min": anisotropy_ratio,
    }


def _score_scan_payload(payload: Dict[str, Any]) -> float:
    if str(payload.get("schema_version", "")) == "v3_fast_motif_scan_v1":
        vals = [float(r.get("score", 0.0)) for r in payload.get("trials", [])]
        return float(max(vals) if vals else 0.0)
    best = None
    for tr in payload.get("trials", []):
        for cand in tr.get("top_candidates", []):
            s = float(cand.get("score", 0.0))
            if best is None or s > best:
                best = s
    return float(best if best is not None else 0.0)


def _extract_best_candidate(payload: Dict[str, Any]) -> Dict[str, Any] | None:
    if str(payload.get("schema_version", "")) == "v3_fast_motif_scan_v1":
        trials = payload.get("trials", [])
        if not trials:
            return None
        best_row = max(trials, key=lambda r: float(r.get("score", 0.0)))
        return {
            "trial_id": best_row.get("trial_id"),
            "seed_family": best_row.get("seed_family"),
            "seed_state_label": best_row.get("seed_state_label"),
            "kick_label": best_row.get("kick_label"),
            "classification": "candidate_lock" if best_row.get("first_repeat") is not None else "no_lock",
            "motion_class": best_row.get("motion_class"),
            "period_N": (
                int(best_row["first_repeat"]["period"])
                if isinstance(best_row.get("first_repeat"), dict) and best_row["first_repeat"].get("period") is not None
                else None
            ),
            "shift_dx": None,
            "mean_support_match_ratio": float(best_row.get("recurrence_score", 0.0)),
            "score": float(best_row.get("score", 0.0)),
        }
    best = None
    best_score = -1e18
    for tr in payload.get("trials", []):
        for cand in tr.get("top_candidates", []):
            s = float(cand.get("score", 0.0))
            if s > best_score:
                best_score = s
                best = {
                    "trial_id": tr.get("trial_id"),
                    "seed_family": tr.get("seed", {}).get("seed_family"),
                    "seed_state_label": tr.get("seed", {}).get("seed_state_label"),
                    "kick_label": tr.get("seed", {}).get("kick_label"),
                    **cand,
                }
    return best


def _course_correct(streak: int, base: FastScanParams) -> FastScanParams:
    if streak <= 0:
        return base
    # Escalate search breadth slowly to avoid blowing compute.
    size_x = int(base.size_x + min(12, 2 * streak))
    size_y = int(base.size_y + (2 if streak >= 2 else 0))
    size_z = int(base.size_z + (2 if streak >= 2 else 0))
    ticks = int(base.ticks + min(96, 12 * streak))
    max_trials = int(min(8, base.max_trials + (1 if streak >= 2 else 0)))
    stencil = "cube26"
    return FastScanParams(
        ticks=ticks,
        size_x=size_x,
        size_y=size_y,
        size_z=size_z,
        stencil_id=stencil,
        max_trials=max_trials,
        thin_step=base.thin_step,
        global_seed=base.global_seed,
        channel_policy_id=base.channel_policy_id,
        policy_seed=base.policy_seed,
    )


def _save_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _run_batch(
    batch_index: int,
    *,
    backend: str,
    global_seed: int,
    no_improve_streak: int,
) -> Dict[str, Any]:
    base = FastScanParams(
        ticks=64,
        size_x=27,
        size_y=9,
        size_z=9,
        stencil_id="cube26",
        max_trials=4,
        thin_step=4,
        global_seed=int(global_seed + 17 * (batch_index + 1)),
    )
    p = _course_correct(no_improve_streak, base)
    if batch_index % 6 == 3:
        p = FastScanParams(**{**asdict(p), "ticks": int(p.ticks + 12), "max_trials": int(min(10, p.max_trials + 1))})

    candidate_defs = [
        {"kernel_candidate_id": "K0_cube26_uniform_v1", "channel_policy_id": "uniform_all", "stencil_id": "cube26"},
        {"kernel_candidate_id": "K1_cube26_det_cycle_v1", "channel_policy_id": "deterministic_cycle_v1", "stencil_id": "cube26"},
        {"kernel_candidate_id": "K2_cube26_stochastic_v1", "channel_policy_id": "stochastic_gating_v1", "stencil_id": "cube26"},
    ]
    if no_improve_streak >= 40:
        candidate_defs = [
            {"kernel_candidate_id": "K1_cube26_det_cycle_v1", "channel_policy_id": "deterministic_cycle_v1", "stencil_id": "cube26"},
            {"kernel_candidate_id": "K2_cube26_stochastic_v1", "channel_policy_id": "stochastic_gating_v1", "stencil_id": "cube26"},
            {"kernel_candidate_id": "K0_cube26_uniform_v1", "channel_policy_id": "uniform_all", "stencil_id": "cube26"},
        ]

    mul_table = accel.build_mul_table()
    dummy_neighbors = accel.build_neighbor_table(3, 3, 3, accel.offsets_for_stencil("axial6"))
    e111 = _basis_id(7, +1)
    e001 = _basis_id(1, +1)
    e010 = _basis_id(2, +1)

    matrix_rows: List[Dict[str, Any]] = []
    t_batch_start = time.time()
    for ci, cand in enumerate(candidate_defs):
        pp = FastScanParams(
            **{
                **asdict(p),
                "stencil_id": str(cand["stencil_id"]),
                "channel_policy_id": str(cand["channel_policy_id"]),
                "policy_seed": int(global_seed + 4049 * (batch_index + 1) + ci * 17),
            }
        )
        t0 = time.time()
        payload = run_fast_motif_scan(pp, backend=backend)
        dt_scan = float(time.time() - t0)
        best = _extract_best_candidate(payload)
        scan_score = _score_scan_payload(payload)

        kick = e001 if (batch_index % 2 == 0) else e010
        probe = run_twin_detector_probe(
            ProbeParams(
                runs=16,
                ticks=96,
                size_x=21,
                size_y=21,
                size_z=21,
                vacuum_noise_prob=0.002 + 0.001 * min(3, no_improve_streak),
                detector_margin=2,
                seed_state_id=e111,
                kick_id=kick,
                global_seed=int(global_seed + 7919 * (batch_index + 1) + ci),
                axis="x",
                channel_policy_id=str(cand["channel_policy_id"]),
                policy_seed=int(global_seed + 10007 * (batch_index + 1) + ci),
            ),
            backend=backend,
            neighbors=dummy_neighbors,
            mul_table=mul_table,
        )
        isotropy = run_isotropy_probe(
            base_probe=ProbeParams(
                runs=12,
                ticks=96,
                size_x=21,
                size_y=21,
                size_z=21,
                vacuum_noise_prob=0.002,
                detector_margin=2,
                seed_state_id=e111,
                kick_id=e001,
                global_seed=int(global_seed + 9001 * (batch_index + 1) + ci),
                axis="x",
                channel_policy_id=str(cand["channel_policy_id"]),
                policy_seed=int(global_seed + 12007 * (batch_index + 1) + ci),
            ),
            backend=backend,
            neighbors=dummy_neighbors,
            mul_table=mul_table,
        )

        left = float(probe["left_hit_fraction"])
        right = float(probe["right_hit_fraction"])
        denom = max(1e-12, left + right)
        a_chi_proxy = float((left - right) / denom)
        a_c_proxy = float(1.0 - probe["detector_exclusivity"])
        aniso = isotropy.get("anisotropy_ratio_max_over_min")
        aniso_val = float(aniso) if isinstance(aniso, (int, float)) else 999.0

        gate0 = True
        gate1 = bool(payload.get("checks", {}).get("any_propagating") or payload.get("checks", {}).get("any_recurrence"))
        gate2 = bool(float(probe["detector_exclusivity"]) >= 0.2)
        gate3 = bool(aniso_val <= 2.0)
        gate4 = bool(abs(a_chi_proxy) >= 0.05)

        score_total = (
            0.20 * float(scan_score)
            + 0.20 * float(probe["detector_exclusivity"])
            + 0.25 * float(1.0 / max(1.0, aniso_val))
            + 0.15 * float(abs(a_chi_proxy))
            + 0.10 * float(gate1)
            + 0.10 * float(1.0 / max(1e-6, dt_scan))
        )

        matrix_rows.append(
            {
                "kernel_candidate_id": str(cand["kernel_candidate_id"]),
                "channel_policy_id": str(cand["channel_policy_id"]),
                "stencil_id": str(cand["stencil_id"]),
                "scan_params": asdict(pp),
                "scan_elapsed_sec": float(dt_scan),
                "scan_checks": payload.get("checks", {}),
                "best_candidate": best,
                "scan_score": float(scan_score),
                "photon_probe": probe,
                "anisotropy_metrics": isotropy,
                "a_chi_proxy": float(a_chi_proxy),
                "a_c_proxy": float(a_c_proxy),
                "gate_results": {
                    "gate0_contract": bool(gate0),
                    "gate1_transport": bool(gate1),
                    "gate2_detector": bool(gate2),
                    "gate3_isotropy": bool(gate3),
                    "gate4_chirality": bool(gate4),
                },
                "score_total": float(score_total),
            }
        )

    # Prefer candidates passing more gates, then score_total.
    matrix_rows = sorted(
        matrix_rows,
        key=lambda r: (
            sum(1 for v in r["gate_results"].values() if bool(v)),
            float(r["score_total"]),
        ),
        reverse=True,
    )
    sel = matrix_rows[0]
    out = {
        "batch_index": int(batch_index),
        "timestamp_utc": _now_utc(),
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "event_order_policy": "synchronous_parallel_v1",
        "global_seed": int(global_seed),
        "kernel_candidate_id": sel["kernel_candidate_id"],
        "channel_policy_id": sel["channel_policy_id"],
        "stencil_id": sel["stencil_id"],
        "scan_params": sel["scan_params"],
        "scan_elapsed_sec": float(time.time() - t_batch_start),
        "scan_checks": sel["scan_checks"],
        "best_candidate": sel["best_candidate"],
        "best_score": float(sel["score_total"]),
        "photon_probe": sel["photon_probe"],
        "a_chi_proxy": float(sel["a_chi_proxy"]),
        "a_c_proxy": float(sel["a_c_proxy"]),
        "anisotropy_metrics": sel["anisotropy_metrics"],
        "gate_results": sel["gate_results"],
        "kernel_selection_matrix": matrix_rows,
        "course_correction_level": int(no_improve_streak),
    }
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-batches", type=int, default=0, help="0 means run forever")
    parser.add_argument("--sleep-sec", type=float, default=1.0)
    parser.add_argument("--global-seed", type=int, default=1337)
    parser.add_argument("--force-backend", type=str, default="", choices=["", "python", "numba_cpu", "numba_cuda"])
    args = parser.parse_args()

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    _ensure_backlog_note()

    if str(args.force_backend):
        backend = str(args.force_backend)
    else:
        backend = "numba_cpu"

    _append_log(
        [
            f"## Session start {_now_utc()}",
            "",
            f"- backend: `{backend}`",
            f"- kernel_profile: `{k.KERNEL_PROFILE}`",
            f"- convention_id: `{k.CONVENTION_ID}`",
            f"- max_batches: `{int(args.max_batches)}` (`0` means infinite)",
            "",
        ]
    )

    all_rows: List[Dict[str, Any]] = []
    batch = 0
    no_improve_streak = 0
    best_score_so_far = -1e18
    seed_offset = 0

    while True:
        if int(args.max_batches) > 0 and batch >= int(args.max_batches):
            break
        try:
            row = _run_batch(
                batch,
                backend=backend,
                global_seed=int(args.global_seed) + int(seed_offset),
                no_improve_streak=no_improve_streak,
            )
            all_rows.append(row)

            stamp = _stamp()
            out_json = RUN_DIR / f"{stamp}_batch_{batch:06d}.json"
            _save_json(out_json, row)

            score = float(row["best_score"])
            improved = score > best_score_so_far + 1e-12
            if improved:
                best_score_so_far = score
                no_improve_streak = 0
            else:
                no_improve_streak += 1
                if no_improve_streak > 0 and (no_improve_streak % 40 == 0):
                    seed_offset += 1000003
                    _append_log(
                        [
                            f"#### Stall pivot @ {_now_utc()}",
                            f"- reason: `no_improve_streak={no_improve_streak}`",
                            f"- action: `seed_offset += 1000003 -> {seed_offset}`",
                            "- action: keep K1/K2 prioritized in selection matrix",
                        ]
                    )
                    _append_lit_log(
                        {
                            "timestamp": _now_utc(),
                            "focus_type": "blocker",
                            "question": "Long plateau in kernel selection score. What immediate pivot should be applied?",
                            "sources_checked": "internal-run-evidence",
                            "key_finding": "Rotate seed basin and keep matrix comparison active to avoid local attractor overfitting.",
                            "confidence": "high",
                            "immediate_action": "apply",
                            "reason": "Observed prolonged no-improvement streak.",
                            "follow_up_test": "Check next 20 batches for gate pass-rate change.",
                        }
                    )

            summary = {
                "schema_version": "v3_overnight_batch_summary_v1",
                "updated_utc": _now_utc(),
                "backend": backend,
                "kernel_profile": k.KERNEL_PROFILE,
                "convention_id": k.CONVENTION_ID,
                "batch_count": int(len(all_rows)),
                "best_score_so_far": float(best_score_so_far),
                "no_improve_streak": int(no_improve_streak),
                "latest": row,
                "recent_batches": all_rows[-12:],
            }
            _save_json(SUMMARY_JSON, summary)
            _save_json(
                STATE_JSON,
                {
                    "updated_utc": _now_utc(),
                    "batch_index": int(batch),
                    "best_score_so_far": float(best_score_so_far),
                    "no_improve_streak": int(no_improve_streak),
                    "seed_offset": int(seed_offset),
                    "latest_output": str(out_json.relative_to(ROOT)),
                    "backend": backend,
                },
            )

            _append_log(
                [
                    f"### Batch {batch} @ {_now_utc()}",
                    f"- output: `{out_json.relative_to(ROOT).as_posix()}`",
                    f"- best_score: `{score:.6f}`",
                    f"- improved: `{improved}`",
                    f"- kernel_candidate_id: `{row.get('kernel_candidate_id')}`",
                    f"- channel_policy_id: `{row.get('channel_policy_id')}`",
                    f"- wave_transport_class: `{row['photon_probe']['wave_transport_class']}`",
                    f"- detector_exclusivity: `{row['photon_probe']['detector_exclusivity']:.6f}`",
                    f"- front_balance: `{row['photon_probe']['front_balance']:.6f}`",
                    f"- anisotropy_ratio_max_over_min: `{row['anisotropy_metrics'].get('anisotropy_ratio_max_over_min')}`",
                    f"- A_chi_proxy: `{row['a_chi_proxy']:.6f}`",
                    f"- gates: `{row.get('gate_results')}`",
                    f"- no_improve_streak: `{no_improve_streak}`",
                ]
            )

            # Periodic "lit review if stuck" hooks with concrete next tests.
            if (batch + 1) % 3 == 0:
                if no_improve_streak >= 2:
                    _append_lit_log(
                        {
                            "timestamp": _now_utc(),
                            "focus_type": "blocker",
                            "question": "Photon lane shows limited improvement. Which search policy change has highest expected value?",
                            "sources_checked": "internal-run-evidence",
                            "key_finding": "Increase exploration pressure while keeping cube26 primary; use sparse axial6 control sweeps only.",
                            "confidence": "medium",
                            "immediate_action": "apply",
                            "reason": "Current lane may be overfitting a narrow seed manifold or stencil-specific artifact.",
                            "follow_up_test": "Compare top-k yield over next 6 batches with expanded search breadth.",
                        }
                    )
                else:
                    _append_lit_log(
                        {
                            "timestamp": _now_utc(),
                            "focus_type": "long_horizon",
                            "question": "How to make coarse-graining useful for triplet-scale planning?",
                            "sources_checked": "internal-roadmap",
                            "key_finding": "Use descriptor invariance over scale-up runs as promotion gate before full large-box expansion.",
                            "confidence": "medium",
                            "immediate_action": "defer",
                            "reason": "Need more robust motif candidates first.",
                            "follow_up_test": "When two candidates stabilize, run descriptor invariance suite.",
                        }
                    )

            batch += 1
            time.sleep(max(0.0, float(args.sleep_sec)))
        except Exception:
            err = traceback.format_exc()
            _append_log(
                [
                    f"### Batch {batch} ERROR @ {_now_utc()}",
                    "```text",
                    err.rstrip(),
                    "```",
                    "- action: continue after backoff",
                ]
            )
            time.sleep(5.0)

    _append_log([f"## Session end {_now_utc()}"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
