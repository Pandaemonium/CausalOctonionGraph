"""Build RFC-010 C12 phase-sector metrics artifacts.

This pipeline runs S2880 (Q240 x C12) motif probes and emits:
1) phase-hop histogram CSV,
2) phase-sector metrics JSON + Markdown,
3) rare-hop transition matrix CSV,
4) panel report Markdown.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np

from cog_v3.calc import build_v3_c12_singlet_doublet_clock_shift_sparse_v1 as c12
from cog_v3.python import kernel_s2880_pair_conservative_v1 as kpair
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_HIST = ROOT / "cog_v3" / "sources" / "v3_c12_phase_hop_histograms_v1.csv"
OUT_METRICS_JSON = ROOT / "cog_v3" / "sources" / "v3_c12_phase_sector_metrics_v1.json"
OUT_METRICS_MD = ROOT / "cog_v3" / "sources" / "v3_c12_phase_sector_metrics_v1.md"
OUT_TMAT = ROOT / "cog_v3" / "sources" / "v3_c12_phase_sector_transition_matrix_v1.csv"
OUT_PANEL_MD = ROOT / "cog_v3" / "sources" / "v3_c12_phase_sector_panel_report_v1.md"

SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_c12_phase_sector_metrics_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"

PHASE_COUNT = 12


@dataclass(frozen=True)
class PanelConfig:
    panel_id: str
    boundary_mode: str  # fixed_vacuum | periodic
    event_order_policy: str  # synchronous_parallel_v1 | seeded_async_v1 | pair_conservative_v1
    stencil_id: str  # axial6 | cube26
    ticks: int
    warmup_ticks: int
    runs_per_trial: int
    size_x: int
    size_y: int
    size_z: int
    channel_policy_id: str


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _q_basis_id(i: int, sign: int = 1) -> int:
    v = [k.Fraction(0, 1) for _ in range(8)]
    v[int(i)] = k.Fraction(int(sign), 1)
    return int(k.ALPHABET_INDEX[tuple(v)])  # type: ignore[index]


def _s_id(phase: int, qid: int, qn: int) -> int:
    p = int(phase) % PHASE_COUNT
    return int(p * int(qn) + int(qid))


def _idx(x: int, y: int, z: int, ny: int, nz: int) -> int:
    return (x * ny + y) * nz + z


def _offsets(stencil_id: str) -> List[Tuple[int, int, int]]:
    sid = str(stencil_id)
    if sid == "axial6":
        return [(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)]
    if sid == "cube26":
        out: List[Tuple[int, int, int]] = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    out.append((dx, dy, dz))
        return out
    raise ValueError(f"Unknown stencil_id: {sid}")


def _build_neighbors(
    nx: int,
    ny: int,
    nz: int,
    offsets: Sequence[Tuple[int, int, int]],
    boundary_mode: str,
) -> np.ndarray:
    n = int(nx) * int(ny) * int(nz)
    m = len(offsets)
    tab = np.full((n, m), -1, dtype=np.int32)
    wrap = str(boundary_mode) == "periodic"
    row = 0
    for x in range(nx):
        for y in range(ny):
            for z in range(nz):
                for j, (dx, dy, dz) in enumerate(offsets):
                    qx = x + int(dx)
                    qy = y + int(dy)
                    qz = z + int(dz)
                    if wrap:
                        qx %= nx
                        qy %= ny
                        qz %= nz
                        tab[row, j] = _idx(qx, qy, qz, ny, nz)
                    else:
                        if 0 <= qx < nx and 0 <= qy < ny and 0 <= qz < nz:
                            tab[row, j] = _idx(qx, qy, qz, ny, nz)
                row += 1
    return tab


def _offset_class(dx: int, dy: int, dz: int) -> str:
    nnz = int((dx != 0) + (dy != 0) + (dz != 0))
    if nnz <= 1:
        return "axis"
    if nnz == 2:
        return "face"
    return "corner"


def _prepare_policy_neighbors(
    nx: int,
    ny: int,
    nz: int,
    stencil_id: str,
    boundary_mode: str,
) -> Dict[str, np.ndarray]:
    offsets = _offsets(stencil_id)
    axis = [o for o in offsets if _offset_class(int(o[0]), int(o[1]), int(o[2])) == "axis"]
    face = [o for o in offsets if _offset_class(int(o[0]), int(o[1]), int(o[2])) == "face"]
    corner = [o for o in offsets if _offset_class(int(o[0]), int(o[1]), int(o[2])) == "corner"]

    def tbl(v: List[Tuple[int, int, int]]) -> np.ndarray:
        vv = v if len(v) > 0 else axis
        return _build_neighbors(nx, ny, nz, vv, boundary_mode=boundary_mode)

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


def _apply_seed(
    world: np.ndarray,
    nx: int,
    ny: int,
    nz: int,
    *,
    family: str,
    state_id: int,
    kick_id: int,
    mul: np.ndarray,
) -> None:
    cx, cy, cz = nx // 2, ny // 2, nz // 2

    def set_state(x: int, y: int, z: int, sid: int) -> None:
        if 0 <= x < nx and 0 <= y < ny and 0 <= z < nz:
            world[_idx(x, y, z, ny, nz)] = np.uint16(int(sid))

    fam = str(family)
    if fam == "sheet_x":
        x0 = max(1, nx // 4)
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                set_state(x0, cy + dy, cz + dz, int(mul[int(kick_id), int(state_id)]))
        return
    if fam == "sheet_y":
        y0 = max(1, ny // 4)
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                set_state(cx + dx, y0, cz + dz, int(mul[int(kick_id), int(state_id)]))
        return
    if fam == "sheet_z":
        z0 = max(1, nz // 4)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                set_state(cx + dx, cy + dy, z0, int(mul[int(kick_id), int(state_id)]))
        return
    if fam == "blob3":
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    set_state(cx + dx, cy + dy, cz + dz, int(mul[int(kick_id), int(state_id)]))
        return
    if fam == "single":
        set_state(cx, cy, cz, int(mul[int(kick_id), int(state_id)]))
        return
    raise ValueError(f"Unknown seed family: {fam}")


def _step_sync(world: np.ndarray, neighbors: np.ndarray, mul: np.ndarray, vac_id: int) -> np.ndarray:
    n, m = neighbors.shape
    out = np.empty_like(world)
    vac = int(vac_id)
    for i in range(n):
        acc = vac
        for j in range(m):
            q = int(neighbors[i, j])
            msg = vac if q < 0 else int(world[q])
            acc = int(mul[acc, msg])
        out[i] = np.uint16(int(mul[acc, int(world[i])]))
    return out


def _step_async(
    world: np.ndarray,
    neighbors: np.ndarray,
    mul: np.ndarray,
    vac_id: int,
    rng: random.Random,
) -> np.ndarray:
    n, m = neighbors.shape
    out = world.copy()
    order = list(range(n))
    rng.shuffle(order)
    vac = int(vac_id)
    for i in order:
        acc = vac
        for j in range(m):
            q = int(neighbors[i, j])
            msg = vac if q < 0 else int(out[q])
            acc = int(mul[acc, msg])
        out[i] = np.uint16(int(mul[acc, int(out[i])]))
    return out


def _trial_bank(qn: int) -> List[Dict[str, Any]]:
    e111 = _q_basis_id(7, +1)
    e001 = _q_basis_id(1, +1)
    e010 = _q_basis_id(2, +1)
    e100 = _q_basis_id(4, +1)
    e011 = _q_basis_id(3, +1)
    return [
        {
            "trial_id": "sheet_x_g0",
            "seed_family": "sheet_x",
            "state_id": _s_id(0, e111, qn),
            "kick_id": _s_id(0, e001, qn),
        },
        {
            "trial_id": "sheet_y_g1",
            "seed_family": "sheet_y",
            "state_id": _s_id(1, e111, qn),
            "kick_id": _s_id(1, e010, qn),
        },
        {
            "trial_id": "sheet_z_g2",
            "seed_family": "sheet_z",
            "state_id": _s_id(2, e111, qn),
            "kick_id": _s_id(2, e100, qn),
        },
        {
            "trial_id": "blob3_g0",
            "seed_family": "blob3",
            "state_id": _s_id(0, e111, qn),
            "kick_id": _s_id(0, e011, qn),
        },
        {
            "trial_id": "single_g1",
            "seed_family": "single",
            "state_id": _s_id(1, e111, qn),
            "kick_id": _s_id(1, e001, qn),
        },
    ]


def _mean(values: Sequence[float]) -> float:
    return float(sum(float(v) for v in values) / max(1, len(values)))


def _safe_div(a: float, b: float) -> float:
    if abs(float(b)) < 1e-12:
        return 0.0
    return float(a) / float(b)


def _run_panel(config: PanelConfig, *, global_seed: int) -> Dict[str, Any]:
    qmul = c12.build_qmul_table()
    mul = c12.build_mul_table(phase_count=PHASE_COUNT, qmul=qmul)
    qn = int(qmul.shape[0])
    vac_id = int(c12.s_identity_id())
    trials = _trial_bank(qn)
    policy_neighbors = _prepare_policy_neighbors(
        int(config.size_x),
        int(config.size_y),
        int(config.size_z),
        str(config.stencil_id),
        str(config.boundary_mode),
    )
    neighbors_default = policy_neighbors["all"]
    pair_rounds = None
    if str(config.event_order_policy) == "pair_conservative_v1":
        pair_rounds = kpair.build_pair_rounds(
            int(config.size_x),
            int(config.size_y),
            int(config.size_z),
            stencil_id=str(config.stencil_id),
            boundary_mode=str(config.boundary_mode),
        )
    interior_mask = np.all(neighbors_default >= 0, axis=1)
    interior_count = int(np.count_nonzero(interior_mask))

    n_cells = int(config.size_x) * int(config.size_y) * int(config.size_z)
    prev_g = np.full((n_cells,), -1, dtype=np.int8)
    run_len = np.zeros((n_cells,), dtype=np.int32)

    delta_counts = np.zeros((PHASE_COUNT,), dtype=np.int64)
    transition_counts = np.zeros((3, 3), dtype=np.int64)
    g_old_counts = np.zeros((3,), dtype=np.int64)
    signed_p1 = 0
    signed_m1 = 0
    signed_p2 = 0
    signed_m2 = 0
    run_lengths: List[int] = []
    total_events = 0

    gamma_tick_total = 0
    gamma_global_dmod3_counts = np.zeros((3,), dtype=np.int64)
    gamma_interior_dmod3_counts = np.zeros((3,), dtype=np.int64)

    hist_rows: List[Dict[str, Any]] = []

    for ti, tr in enumerate(trials):
        for r in range(int(config.runs_per_trial)):
            rr = random.Random(int(global_seed) + 10007 * (ti + 1) + 7919 * (r + 1))
            world = np.full((n_cells,), np.uint16(vac_id), dtype=np.uint16)
            _apply_seed(
                world,
                int(config.size_x),
                int(config.size_y),
                int(config.size_z),
                family=str(tr["seed_family"]),
                state_id=int(tr["state_id"]),
                kick_id=int(tr["kick_id"]),
                mul=mul,
            )

            for t in range(1, int(config.ticks) + 1):
                combo = _policy_combo(str(config.channel_policy_id), int(t), int(global_seed) + r + ti)
                neighbors = policy_neighbors.get(combo, neighbors_default)
                old = world
                if str(config.event_order_policy) == "pair_conservative_v1":
                    assert pair_rounds is not None
                    world = kpair.step_pair_conservative(
                        old,
                        pair_rounds,
                        qmul=qmul,
                        phase_count=PHASE_COUNT,
                        global_seed=int(global_seed) + 10007 * (ti + 1) + 7919 * (r + 1),
                        tick=int(t),
                        shuffle_round_order=False,
                    )
                elif str(config.event_order_policy) == "seeded_async_v1":
                    world = _step_async(old, neighbors, mul, vac_id=vac_id, rng=rr)
                else:
                    world = _step_sync(old, neighbors, mul, vac_id=vac_id)

                if t <= int(config.warmup_ticks):
                    continue

                old_phase = (old.astype(np.int32) // int(qn)).astype(np.int16)
                new_phase = (world.astype(np.int32) // int(qn)).astype(np.int16)
                d = ((new_phase - old_phase) % PHASE_COUNT).astype(np.int16)

                # Triality audit (Gamma = phase mod 3): tick-level conservation probes.
                gamma_tick_total += 1
                old_g_sum = int(np.sum(old_phase % 3))
                new_g_sum = int(np.sum(new_phase % 3))
                dg_global = int((new_g_sum - old_g_sum) % 3)
                gamma_global_dmod3_counts[dg_global] += 1
                if interior_count > 0:
                    old_gi_sum = int(np.sum(old_phase[interior_mask] % 3))
                    new_gi_sum = int(np.sum(new_phase[interior_mask] % 3))
                    dg_interior = int((new_gi_sum - old_gi_sum) % 3)
                    gamma_interior_dmod3_counts[dg_interior] += 1

                support = (old != np.uint16(vac_id)) | (world != np.uint16(vac_id))
                if not bool(np.any(support)):
                    continue

                d_sup = d[support]
                old_phase_sup = old_phase[support]
                new_phase_sup = new_phase[support]
                g_old = (old_phase_sup % 3).astype(np.int8)
                g_new = (new_phase_sup % 3).astype(np.int8)

                bc = np.bincount(d_sup.astype(np.int32), minlength=PHASE_COUNT)
                delta_counts += bc.astype(np.int64)
                total_events += int(d_sup.shape[0])

                g_old_bc = np.bincount(g_old.astype(np.int32), minlength=3)
                g_old_counts += g_old_bc.astype(np.int64)

                mix = (d_sup % 3) != 0
                if bool(np.any(mix)):
                    go = g_old[mix].astype(np.int32)
                    gn = g_new[mix].astype(np.int32)
                    for i in range(go.shape[0]):
                        transition_counts[int(go[i]), int(gn[i])] += 1

                signed = d_sup.copy()
                signed[signed > 6] -= 12
                signed_p1 += int(np.count_nonzero(signed == 1))
                signed_m1 += int(np.count_nonzero(signed == -1))
                signed_p2 += int(np.count_nonzero(signed == 2))
                signed_m2 += int(np.count_nonzero(signed == -2))

                support_idx = np.flatnonzero(support)
                old_g_full = (old_phase % 3).astype(np.int8)
                for idx in support_idx.tolist():
                    g = int(old_g_full[int(idx)])
                    if int(prev_g[int(idx)]) < 0:
                        prev_g[int(idx)] = np.int8(g)
                        run_len[int(idx)] = np.int32(1)
                    elif int(prev_g[int(idx)]) == g:
                        run_len[int(idx)] = np.int32(int(run_len[int(idx)]) + 1)
                    else:
                        run_lengths.append(int(run_len[int(idx)]))
                        prev_g[int(idx)] = np.int8(g)
                        run_len[int(idx)] = np.int32(1)

            hist_rows.append(
                {
                    "panel_id": str(config.panel_id),
                    "trial_id": str(tr["trial_id"]),
                    "seed_family": str(tr["seed_family"]),
                    "run_id": int(r),
                    "events_count": int(total_events),
                }
            )

    for i in range(n_cells):
        if int(run_len[i]) > 0:
            run_lengths.append(int(run_len[i]))

    mag_counts = {m: 0 for m in (0, 1, 2, 3, 4, 5, 6)}
    for d in range(PHASE_COUNT):
        m = int(min(d, PHASE_COUNT - d))
        mag_counts[m] = int(mag_counts.get(m, 0) + int(delta_counts[d]))

    numerator = float(mag_counts[3])
    denominator = float(mag_counts[1] + mag_counts[2] + mag_counts[4] + mag_counts[5] + mag_counts[6])
    r3 = _safe_div(numerator, denominator)
    c3 = _safe_div(
        float(sum(int(delta_counts[d]) for d in range(PHASE_COUNT) if (d % 3) == 0)),
        float(max(1, int(total_events))),
    )

    p_g = np.asarray(g_old_counts, dtype=np.float64) / max(1.0, float(np.sum(g_old_counts)))
    l3_null = _safe_div(1.0, float(max(1e-12, 1.0 - float(np.sum(p_g * p_g)))))
    l3 = float(_mean([float(x) for x in run_lengths])) if run_lengths else 0.0

    tmat = np.zeros((3, 3), dtype=np.float64)
    for i in range(3):
        row_sum = int(np.sum(transition_counts[i, :]))
        if row_sum > 0:
            tmat[i, :] = transition_counts[i, :] / float(row_sum)

    a1 = _safe_div(float(signed_p1 - signed_m1), float(signed_p1 + signed_m1))
    a2 = _safe_div(float(signed_p2 - signed_m2), float(signed_p2 + signed_m2))

    gate1 = bool(r3 >= 2.0)
    gate2 = bool(c3 >= (1.0 / 3.0) + 0.05 and l3 >= l3_null)
    gate3 = bool(np.max(tmat) >= 0.45 and np.count_nonzero(tmat > 0.34) <= 4)
    gate4 = bool(abs(a1) >= 0.02 or abs(a2) >= 0.02)

    g_global_total = int(np.sum(gamma_global_dmod3_counts))
    g_interior_total = int(np.sum(gamma_interior_dmod3_counts))
    gamma_global_nonzero = int(gamma_global_dmod3_counts[1] + gamma_global_dmod3_counts[2])
    gamma_interior_nonzero = int(gamma_interior_dmod3_counts[1] + gamma_interior_dmod3_counts[2])
    triality_audit = {
        "gamma_tick_total": int(gamma_tick_total),
        "interior_cell_count": int(interior_count),
        "gamma_global_dmod3_counts": {str(i): int(gamma_global_dmod3_counts[i]) for i in range(3)},
        "gamma_global_nonzero_tick_count": int(gamma_global_nonzero),
        "gamma_global_nonzero_tick_rate": float(_safe_div(float(gamma_global_nonzero), float(max(1, g_global_total)))),
        "gamma_interior_dmod3_counts": {str(i): int(gamma_interior_dmod3_counts[i]) for i in range(3)},
        "gamma_interior_nonzero_tick_count": int(gamma_interior_nonzero),
        "gamma_interior_nonzero_tick_rate": float(_safe_div(float(gamma_interior_nonzero), float(max(1, g_interior_total)))),
        "expected_exact_for_conservative_pair_kernel": {
            "global": "all ticks dGamma_mod3 == 0",
            "interior": "all ticks dGamma_mod3 == 0",
        },
    }

    metrics = {
        "panel_id": str(config.panel_id),
        "boundary_mode": str(config.boundary_mode),
        "event_order_policy": str(config.event_order_policy),
        "stencil_id": str(config.stencil_id),
        "channel_policy_id": str(config.channel_policy_id),
        "ticks": int(config.ticks),
        "warmup_ticks": int(config.warmup_ticks),
        "runs_per_trial": int(config.runs_per_trial),
        "size": [int(config.size_x), int(config.size_y), int(config.size_z)],
        "total_events": int(total_events),
        "delta_counts": {str(i): int(delta_counts[i]) for i in range(PHASE_COUNT)},
        "mag_counts": {str(k): int(v) for k, v in mag_counts.items()},
        "R3": float(r3),
        "C3": float(c3),
        "L3": float(l3),
        "L3_null_baseline": float(l3_null),
        "A1": float(a1),
        "A2": float(a2),
        "T_counts": transition_counts.astype(int).tolist(),
        "T_probs": tmat.tolist(),
        "gate_results": {
            "gate1_dominance": bool(gate1),
            "gate2_sector_conservation": bool(gate2),
            "gate3_mixing_structure": bool(gate3),
            "gate4_signed_asymmetry": bool(gate4),
        },
        "triality_audit": triality_audit,
    }
    return {"metrics": metrics, "hist_rows": hist_rows}


def _render_metrics_md(payload: Dict[str, Any]) -> str:
    m0 = payload["panels"][0]["metrics"] if payload["panels"] else {}
    lines = [
        "# v3 C12 Phase-Sector Metrics (v1)",
        "",
        f"- kernel_profile: `{payload['kernel_profile']}`",
        f"- convention_id: `{payload['convention_id']}`",
        f"- phase_count: `{payload['phase_count']}`",
        f"- panel_count: `{len(payload['panels'])}`",
        "",
        "## Aggregate Snapshot (panel 0)",
        "",
        f"- panel_id: `{m0.get('panel_id')}`",
        f"- R3: `{m0.get('R3')}`",
        f"- C3: `{m0.get('C3')}`",
        f"- L3: `{m0.get('L3')}`",
        f"- L3_null_baseline: `{m0.get('L3_null_baseline')}`",
        f"- A1: `{m0.get('A1')}`",
        f"- A2: `{m0.get('A2')}`",
        f"- gate_results: `{m0.get('gate_results')}`",
        f"- triality_audit: `{m0.get('triality_audit')}`",
        "",
        "## Notes",
        "",
        "- Gate thresholds are exploratory and tied to RFC-010 promotion lanes.",
        "- This artifact is test-contract evidence, not closure evidence.",
    ]
    return "\n".join(lines)


def _render_panel_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# v3 C12 Phase-Sector Panel Report (v1)",
        "",
        "| panel_id | boundary | event_order | stencil | R3 | C3 | L3 | A1 | A2 | dG0_global | dG0_interior | g1 | g2 | g3 | g4 |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|",
    ]
    for p in payload["panels"]:
        m = p["metrics"]
        g = m["gate_results"]
        ta = m.get("triality_audit", {})
        gg = ta.get("gamma_global_dmod3_counts", {"0": 0, "1": 0, "2": 0})
        gi = ta.get("gamma_interior_dmod3_counts", {"0": 0, "1": 0, "2": 0})
        gg0 = _safe_div(float(gg.get("0", 0)), float(max(1, int(ta.get("gamma_tick_total", 0)))))
        gi_total = int(gi.get("0", 0)) + int(gi.get("1", 0)) + int(gi.get("2", 0))
        gi0 = _safe_div(float(gi.get("0", 0)), float(max(1, gi_total)))
        lines.append(
            f"| `{m['panel_id']}` | `{m['boundary_mode']}` | `{m['event_order_policy']}` | `{m['stencil_id']}` | "
            f"{float(m['R3']):.4f} | {float(m['C3']):.4f} | {float(m['L3']):.4f} | {float(m['A1']):.4f} | {float(m['A2']):.4f} | "
            f"{float(gg0):.4f} | {float(gi0):.4f} | "
            f"{g['gate1_dominance']} | {g['gate2_sector_conservation']} | {g['gate3_mixing_structure']} | {g['gate4_signed_asymmetry']} |"
        )
    return "\n".join(lines)


def build_payload(*, global_seed: int = 1337, quick: bool = False) -> Dict[str, Any]:
    if bool(quick):
        panels = [
            PanelConfig(
                panel_id="P0_quick_fixed_sync_axial6",
                boundary_mode="fixed_vacuum",
                event_order_policy="synchronous_parallel_v1",
                stencil_id="axial6",
                ticks=24,
                warmup_ticks=6,
                runs_per_trial=1,
                size_x=11,
                size_y=7,
                size_z=7,
                channel_policy_id="uniform_all",
            ),
            PanelConfig(
                panel_id="P1_quick_fixed_paircon_axial6",
                boundary_mode="fixed_vacuum",
                event_order_policy="pair_conservative_v1",
                stencil_id="axial6",
                ticks=24,
                warmup_ticks=6,
                runs_per_trial=1,
                size_x=11,
                size_y=7,
                size_z=7,
                channel_policy_id="uniform_all",
            ),
        ]
    else:
        panels = [
        PanelConfig(
            panel_id="P0_fixed_sync_cube26",
            boundary_mode="fixed_vacuum",
            event_order_policy="synchronous_parallel_v1",
            stencil_id="cube26",
            ticks=84,
            warmup_ticks=18,
            runs_per_trial=3,
            size_x=23,
            size_y=9,
            size_z=9,
            channel_policy_id="uniform_all",
        ),
        PanelConfig(
            panel_id="P1_fixed_async_cube26",
            boundary_mode="fixed_vacuum",
            event_order_policy="seeded_async_v1",
            stencil_id="cube26",
            ticks=70,
            warmup_ticks=16,
            runs_per_trial=2,
            size_x=19,
            size_y=9,
            size_z=9,
            channel_policy_id="deterministic_cycle_v1",
        ),
        PanelConfig(
            panel_id="P2_periodic_sync_axial6",
            boundary_mode="periodic",
            event_order_policy="synchronous_parallel_v1",
            stencil_id="axial6",
            ticks=64,
            warmup_ticks=14,
            runs_per_trial=2,
            size_x=19,
            size_y=9,
            size_z=9,
            channel_policy_id="uniform_all",
        ),
        ]

    panel_rows: List[Dict[str, Any]] = []
    hist_rows: List[Dict[str, Any]] = []
    for i, cfg in enumerate(panels):
        out = _run_panel(cfg, global_seed=int(global_seed) + 9001 * (i + 1))
        panel_rows.append({"config": asdict(cfg), "metrics": out["metrics"]})
        hist_rows.extend(out["hist_rows"])

    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH
    payload: Dict[str, Any] = {
        "schema_version": "v3_c12_phase_sector_metrics_v1",
        "kernel_profile": k.KERNEL_PROFILE,
        "convention_id": k.CONVENTION_ID,
        "phase_count": int(PHASE_COUNT),
        "global_seed": int(global_seed),
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(kernel_path),
        "panels": panel_rows,
    }
    payload["replay_hash"] = _sha_payload(payload)
    return {"payload": payload, "hist_rows": hist_rows}


def write_artifacts(
    payload: Dict[str, Any],
    hist_rows: Sequence[Dict[str, Any]],
) -> None:
    OUT_METRICS_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_METRICS_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_METRICS_MD.write_text(_render_metrics_md(payload), encoding="utf-8")
    OUT_PANEL_MD.write_text(_render_panel_md(payload), encoding="utf-8")

    with OUT_HIST.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["panel_id", "trial_id", "seed_family", "run_id", "events_count"])
        for r in hist_rows:
            w.writerow(
                [
                    str(r["panel_id"]),
                    str(r["trial_id"]),
                    str(r["seed_family"]),
                    int(r["run_id"]),
                    int(r["events_count"]),
                ]
            )

    with OUT_TMAT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["panel_id", "g_from", "g_to", "probability", "count"])
        for p in payload["panels"]:
            m = p["metrics"]
            t_probs = m["T_probs"]
            t_counts = m["T_counts"]
            for i in range(3):
                for j in range(3):
                    w.writerow(
                        [
                            str(m["panel_id"]),
                            int(i),
                            int(j),
                            float(t_probs[i][j]),
                            int(t_counts[i][j]),
                        ]
                    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--global-seed", type=int, default=1337)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    out = build_payload(global_seed=int(args.global_seed), quick=bool(args.quick))
    write_artifacts(out["payload"], out["hist_rows"])
    p0 = out["payload"]["panels"][0]["metrics"] if out["payload"]["panels"] else {}
    print(
        "v3_c12_phase_sector_metrics_v1: "
        f"panel0_R3={float(p0.get('R3', 0.0)):.4f}, "
        f"panel0_C3={float(p0.get('C3', 0.0)):.4f}, "
        f"panel0_A1={float(p0.get('A1', 0.0)):.4f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
