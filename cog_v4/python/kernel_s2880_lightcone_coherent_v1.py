"""COG v4: deterministic full-lightcone coherent kernel for small systems.

This lane encodes the v4 axiom:
  - Future states are uniquely determined by the full causal past lightcone.
  - No RNG is used in state updates.
  - Pair events are conservative in triality (generation sum mod 3).

State alphabet:
  S2880 = Z3 x Z4 x Q240  (equivalently Z12 x Q240)
  sid = phase * 240 + q_id
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional, Sequence, Tuple

import numpy as np

from cog_v3.calc import build_v3_c12_singlet_doublet_clock_shift_sparse_v1 as c12
from cog_v3.python import kernel_s2880_pair_conservative_v1 as kpair


KERNEL_PROFILE = "cog_v4_s2880_lightcone_coherent_v1"
PHASE_COUNT = 12
Q_COUNT = 240


@dataclass(frozen=True)
class VolumeBox:
    """Axis-aligned inclusive-exclusive box: [x0,x1) x [y0,y1) x [z0,z1)."""

    x0: int
    x1: int
    y0: int
    y1: int
    z0: int
    z1: int

    def clamp(self, shape: Tuple[int, int, int]) -> "VolumeBox":
        nx, ny, nz = (int(shape[0]), int(shape[1]), int(shape[2]))
        return VolumeBox(
            x0=max(0, min(nx, int(self.x0))),
            x1=max(0, min(nx, int(self.x1))),
            y0=max(0, min(ny, int(self.y0))),
            y1=max(0, min(ny, int(self.y1))),
            z0=max(0, min(nz, int(self.z0))),
            z1=max(0, min(nz, int(self.z1))),
        )

    def is_nonempty(self) -> bool:
        return int(self.x1) > int(self.x0) and int(self.y1) > int(self.y0) and int(self.z1) > int(self.z0)


@dataclass(frozen=True)
class CoherentConfig:
    """v4 coherence config: explicit and minimal, no hidden fit constants."""

    history_depth: int = 4
    stencil_id: str = "axial6"
    boundary_mode: str = "fixed_vacuum"
    cone_metric: str = "l1"  # "l1" (axial6 semantics) or "linf" (cube26 semantics)


@dataclass(frozen=True)
class IntegerEnergyConfig:
    """Integer Z-energy lane.

    Interpretation:
    - Each C4 spin step (+1 / -1) transfers one integer energy quantum.
    - Local energy is never allowed below zero.
    """

    seed_z: int = 1
    vacuum_z: int = 0


class LightconeCache:
    """Cache neighborhood spheres within hop radius for graph/lightcone queries."""

    def __init__(self, adjacency: Tuple[np.ndarray, ...]) -> None:
        self.adjacency = adjacency
        self._within: Dict[Tuple[int, int], np.ndarray] = {}

    @classmethod
    def from_pair_rounds(cls, pair_rounds: kpair.PairRounds) -> "LightconeCache":
        n_nodes = int(pair_rounds.nx) * int(pair_rounds.ny) * int(pair_rounds.nz)
        neigh: list[list[int]] = [[] for _ in range(n_nodes)]
        for arr in pair_rounds.rounds:
            if arr.size == 0:
                continue
            for a, b in arr.tolist():
                ia = int(a)
                ib = int(b)
                neigh[ia].append(ib)
                neigh[ib].append(ia)
        adjacency = tuple(np.asarray(sorted(set(v)), dtype=np.int32) for v in neigh)
        return cls(adjacency=adjacency)

    def nodes_within_hops(self, start: int, hops: int) -> np.ndarray:
        key = (int(start), int(hops))
        cached = self._within.get(key)
        if cached is not None:
            return cached

        s = int(start)
        h = int(hops)
        if h <= 0:
            out0 = np.asarray([s], dtype=np.int32)
            self._within[key] = out0
            return out0

        visited = {s}
        frontier = {s}
        for _ in range(h):
            nxt: set[int] = set()
            for node in frontier:
                for nb in self.adjacency[node].tolist():
                    ib = int(nb)
                    if ib not in visited:
                        nxt.add(ib)
            if not nxt:
                break
            visited.update(nxt)
            frontier = nxt
        out = np.asarray(sorted(visited), dtype=np.int32)
        self._within[key] = out
        return out


def default_qmul_table() -> np.ndarray:
    return c12.build_qmul_table()


def phase_from_ga(g: int, a: int) -> int:
    """CRT reconstruction: p = (9*a + 4*g) mod 12."""

    return int((9 * int(a) + 4 * int(g)) % 12)


def decode_sid(sid: np.ndarray, *, qn: int = Q_COUNT) -> Tuple[np.ndarray, np.ndarray]:
    s = np.asarray(sid, dtype=np.int32)
    return s // int(qn), s % int(qn)


def encode_sid(phase: np.ndarray, q: np.ndarray, *, qn: int = Q_COUNT) -> np.ndarray:
    return (np.asarray(phase, dtype=np.int32) * int(qn) + np.asarray(q, dtype=np.int32)).astype(np.uint16)


def gamma_sum_mod3(world: np.ndarray, *, qn: int = Q_COUNT) -> int:
    p, _q = decode_sid(np.asarray(world, dtype=np.uint16), qn=int(qn))
    return int(np.sum(p % 3) % 3)


def total_energy_z(z_field: np.ndarray) -> int:
    z = np.asarray(z_field, dtype=np.int64)
    return int(np.sum(z))


def assert_energy_nonnegative(z_field: np.ndarray) -> None:
    z = np.asarray(z_field, dtype=np.int64)
    if z.size <= 0:
        return
    mn = int(np.min(z))
    if mn < 0:
        raise ValueError(f"Hard invariant violated: integer energy below zero (min={mn}).")


def _neighbors(mask: np.ndarray, *, stencil_id: str, boundary_mode: str) -> np.ndarray:
    nx, ny, nz = mask.shape
    out = np.zeros_like(mask, dtype=np.bool_)
    if str(stencil_id) == "axial6":
        offsets = [(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)]
    elif str(stencil_id) == "cube26":
        offsets = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    offsets.append((dx, dy, dz))
    else:
        raise ValueError(f"Unknown stencil_id: {stencil_id}")

    wrap = str(boundary_mode) == "periodic"
    xs, ys, zs = np.where(mask)
    for i in range(xs.shape[0]):
        x = int(xs[i])
        y = int(ys[i])
        z = int(zs[i])
        out[x, y, z] = True
        for dx, dy, dz in offsets:
            qx = x + int(dx)
            qy = y + int(dy)
            qz = z + int(dz)
            if wrap:
                qx %= int(nx)
                qy %= int(ny)
                qz %= int(nz)
                out[qx, qy, qz] = True
            else:
                if 0 <= qx < int(nx) and 0 <= qy < int(ny) and 0 <= qz < int(nz):
                    out[qx, qy, qz] = True
    return out


def measurement_mask(shape: Tuple[int, int, int], volume: VolumeBox) -> np.ndarray:
    nx, ny, nz = (int(shape[0]), int(shape[1]), int(shape[2]))
    v = volume.clamp((nx, ny, nz))
    out = np.zeros((nx, ny, nz), dtype=np.bool_)
    if not v.is_nonempty():
        return out
    out[int(v.x0) : int(v.x1), int(v.y0) : int(v.y1), int(v.z0) : int(v.z1)] = True
    return out


def backward_lightcone_start_mask(
    shape: Tuple[int, int, int],
    measurement_volume: VolumeBox,
    *,
    decoherence_ticks: int,
    stencil_id: str = "axial6",
    boundary_mode: str = "fixed_vacuum",
) -> np.ndarray:
    """Backward-project measurement volume by c=1 for `decoherence_ticks`.

    Operationally: repeated one-hop dilation on the chosen stencil graph.
    """

    mask = measurement_mask(shape, measurement_volume)
    for _ in range(int(max(0, decoherence_ticks))):
        mask = _neighbors(mask, stencil_id=str(stencil_id), boundary_mode=str(boundary_mode))
    return mask


def seed_state_id(*, domain_g: int, energy_a: int, q_id: int) -> int:
    p = phase_from_ga(int(domain_g) % 3, int(energy_a) % 4)
    q = int(q_id) % Q_COUNT
    return int(p * Q_COUNT + q)


def seed_world(
    shape: Tuple[int, int, int],
    *,
    start_mask: np.ndarray,
    seed_sid: int,
    vacuum_sid: int = 0,
    seed_rule: Optional[Callable[[int, int, int], int]] = None,
) -> np.ndarray:
    """Create t0 world from start mask and deterministic seed assignment."""

    nx, ny, nz = (int(shape[0]), int(shape[1]), int(shape[2]))
    n = nx * ny * nz
    world = np.full((n,), int(vacuum_sid), dtype=np.uint16)
    xs, ys, zs = np.where(np.asarray(start_mask, dtype=np.bool_))
    for i in range(xs.shape[0]):
        x = int(xs[i])
        y = int(ys[i])
        z = int(zs[i])
        idx = (x * ny + y) * nz + z
        if seed_rule is None:
            world[idx] = np.uint16(int(seed_sid))
        else:
            world[idx] = np.uint16(int(seed_rule(x, y, z)))
    return world


def initialize_history(world_t0: np.ndarray, *, depth: int) -> Tuple[np.ndarray, ...]:
    """Initialize [t-depth, ..., t0] as repeated t0 image."""

    d = int(max(0, depth))
    base = np.asarray(world_t0, dtype=np.uint16)
    return tuple(base.copy() for _ in range(d + 1))


def initialize_energy_field(
    shape: Tuple[int, int, int],
    *,
    start_mask: np.ndarray,
    seed_z: int,
    vacuum_z: int = 0,
) -> np.ndarray:
    """Build integer Z-energy field aligned with world indexing."""

    if int(seed_z) < 0 or int(vacuum_z) < 0:
        raise ValueError("Hard invariant violated: seed_z and vacuum_z must be >= 0.")

    nx, ny, nz = (int(shape[0]), int(shape[1]), int(shape[2]))
    n = int(nx * ny * nz)
    out = np.full((n,), int(vacuum_z), dtype=np.int32)
    xs, ys, zs = np.where(np.asarray(start_mask, dtype=np.bool_))
    for i in range(xs.shape[0]):
        x = int(xs[i])
        y = int(ys[i])
        z = int(zs[i])
        idx = (x * ny + y) * nz + z
        out[idx] = int(seed_z)
    return out


def _choose_dg(
    *,
    gl: int,
    gr: int,
    base_dg: int,
    left_hist: np.ndarray,
    right_hist: np.ndarray,
) -> int:
    """Deterministic choice from full-cone evidence, no tuned weights."""

    score = np.zeros((3,), dtype=np.int64)
    for d in range(3):
        score[d] = int(left_hist[(int(gl) + d) % 3]) * int(right_hist[(int(gr) - d) % 3])
    top = int(np.max(score))
    winners = np.where(score == top)[0].astype(np.int32)
    if int(base_dg) in winners.tolist():
        return int(base_dg)
    return int(winners[0])


def _dg_to_signed_step(dg: int) -> int:
    """Map dg in {0,1,2} to signed C4 step in {-1,0,+1}."""

    d = int(dg) % 3
    if d == 0:
        return 0
    if d == 1:
        return 1
    return -1


def step_coherent_full_lightcone(
    history: Sequence[np.ndarray],
    pair_rounds: kpair.PairRounds,
    *,
    qmul: np.ndarray,
    cache: LightconeCache,
    tick: int,
    history_depth: int,
    phase_count: int = PHASE_COUNT,
) -> np.ndarray:
    """One deterministic coherent step from full past cone."""

    if len(history) <= 0:
        raise ValueError("history cannot be empty")
    cur = np.asarray(history[-1], dtype=np.uint16)
    qn = int(qmul.shape[0])
    n_rounds = int(len(pair_rounds.rounds))
    if n_rounds <= 0:
        return cur.copy()
    ridx = int(tick) % n_rounds
    pairs = pair_rounds.rounds[ridx]
    if pairs.size == 0:
        return cur.copy()

    base = cur.astype(np.int32)
    nxt = cur.copy()
    li = pairs[:, 0].astype(np.int32)
    ri = pairs[:, 1].astype(np.int32)
    sl = base[li]
    sr = base[ri]
    pl = sl // qn
    pr = sr // qn
    ql = sl % qn
    qr = sr % qn

    ql_new = qmul[ql, qr].astype(np.int32)
    qr_new = qmul[qr, ql].astype(np.int32)

    pl_new = pl.copy()
    pr_new = pr.copy()

    depth_use = min(int(history_depth), max(0, len(history) - 1))
    for row in range(int(li.shape[0])):
        lnode = int(li[row])
        rnode = int(ri[row])
        gl = int(pl[row] % 3)
        gr = int(pr[row] % 3)
        base_dg = int((ql[row] + 2 * qr[row] + int(ridx)) % 3)

        left_hist = np.zeros((3,), dtype=np.int64)
        right_hist = np.zeros((3,), dtype=np.int64)
        for lag in range(1, depth_use + 1):
            frame = np.asarray(history[-1 - lag], dtype=np.uint16)
            lnodes = cache.nodes_within_hops(lnode, lag)
            rnodes = cache.nodes_within_hops(rnode, lag)
            lg = (frame[lnodes].astype(np.int32) // qn) % 3
            rg = (frame[rnodes].astype(np.int32) // qn) % 3
            left_hist += np.bincount(lg, minlength=3).astype(np.int64)
            right_hist += np.bincount(rg, minlength=3).astype(np.int64)

        dg_sel = _choose_dg(gl=gl, gr=gr, base_dg=base_dg, left_hist=left_hist, right_hist=right_hist)
        pl_new[row] = (pl[row] + int(dg_sel)) % int(phase_count)
        pr_new[row] = (pr[row] - int(dg_sel)) % int(phase_count)

    nxt[li] = (pl_new * qn + ql_new).astype(np.uint16)
    nxt[ri] = (pr_new * qn + qr_new).astype(np.uint16)
    return nxt


def run_coherent_reconstruction(
    *,
    shape: Tuple[int, int, int],
    measurement_volume: VolumeBox,
    decoherence_ticks: int,
    domain_g: int,
    energy_a: int,
    q_id: int,
    config: CoherentConfig,
    vacuum_sid: int = 0,
) -> Dict[str, object]:
    """High-level v4 run:
    1) define measurement volume,
    2) backward-project lightcone to decoherence time,
    3) seed start volume with (domain, energy, octavian),
    4) forward deterministic coherent reconstruction to measurement tick.
    """

    nx, ny, nz = (int(shape[0]), int(shape[1]), int(shape[2]))
    meas_mask = measurement_mask((nx, ny, nz), measurement_volume)
    start_mask = backward_lightcone_start_mask(
        (nx, ny, nz),
        measurement_volume,
        decoherence_ticks=int(decoherence_ticks),
        stencil_id=str(config.stencil_id),
        boundary_mode=str(config.boundary_mode),
    )

    seed_sid = seed_state_id(domain_g=int(domain_g), energy_a=int(energy_a), q_id=int(q_id))
    world_t0 = seed_world(
        (nx, ny, nz),
        start_mask=start_mask,
        seed_sid=seed_sid,
        vacuum_sid=int(vacuum_sid),
    )

    qmul = default_qmul_table()
    rounds = kpair.build_pair_rounds(
        nx,
        ny,
        nz,
        stencil_id=str(config.stencil_id),
        boundary_mode=str(config.boundary_mode),
    )
    cache = LightconeCache.from_pair_rounds(rounds)
    history = list(initialize_history(world_t0, depth=int(config.history_depth)))

    g0 = gamma_sum_mod3(world_t0, qn=qmul.shape[0])
    for t in range(int(max(0, decoherence_ticks))):
        nxt = step_coherent_full_lightcone(
            history,
            rounds,
            qmul=qmul,
            cache=cache,
            tick=int(t),
            history_depth=int(config.history_depth),
            phase_count=PHASE_COUNT,
        )
        history.append(nxt)
        keep = int(max(1, int(config.history_depth) + 1))
        if len(history) > keep:
            history = history[-keep:]

    world_meas = np.asarray(history[-1], dtype=np.uint16)
    g1 = gamma_sum_mod3(world_meas, qn=qmul.shape[0])
    n_cells = int(nx * ny * nz)
    n_meas = int(np.sum(meas_mask))
    n_start = int(np.sum(start_mask))

    # flatten mask index extraction
    xs, ys, zs = np.where(meas_mask)
    flat_idx = ((xs.astype(np.int64) * int(ny) + ys.astype(np.int64)) * int(nz) + zs.astype(np.int64)).astype(np.int64)
    meas_states = world_meas[flat_idx.astype(np.int32)]
    phases, qvals = decode_sid(meas_states, qn=qmul.shape[0])

    return {
        "kernel_profile": KERNEL_PROFILE,
        "shape": [nx, ny, nz],
        "stencil_id": str(config.stencil_id),
        "boundary_mode": str(config.boundary_mode),
        "history_depth": int(config.history_depth),
        "decoherence_ticks": int(decoherence_ticks),
        "seed": {
            "domain_g": int(domain_g) % 3,
            "energy_a": int(energy_a) % 4,
            "q_id": int(q_id) % Q_COUNT,
            "seed_sid": int(seed_sid),
        },
        "counts": {
            "cells_total": int(n_cells),
            "start_volume_cells": int(n_start),
            "measurement_cells": int(n_meas),
        },
        "triality": {
            "gamma_t0": int(g0),
            "gamma_t_meas": int(g1),
            "conserved": bool(int(g0) == int(g1)),
        },
        "measurement_summary": {
            "phase_hist_12": np.bincount(phases.astype(np.int32), minlength=12).astype(int).tolist(),
            "q_hist_nonzero": int(np.sum(np.bincount(qvals.astype(np.int32), minlength=Q_COUNT) > 0)),
        },
        "measurement_states": meas_states.astype(int).tolist(),
    }


def step_coherent_full_lightcone_with_integer_energy(
    history: Sequence[np.ndarray],
    z_history: Sequence[np.ndarray],
    pair_rounds: kpair.PairRounds,
    *,
    qmul: np.ndarray,
    cache: LightconeCache,
    tick: int,
    history_depth: int,
    energy_cfg: IntegerEnergyConfig,
    phase_count: int = PHASE_COUNT,
) -> Tuple[np.ndarray, np.ndarray]:
    """One coherent step with integer Z-energy transfer.

    Rule:
    - Chosen dg determines desired signed C4 step s in {-1,0,+1}.
    - s=+1 means transfer one Z quantum right->left.
    - s=-1 means transfer one Z quantum left->right.
    - If desired emitter has no available quantum, direction flips if opposite side
      can emit; otherwise s=0.

    Hard invariant:
    - Z must never go below zero. Any violation raises immediately.
    """

    if len(history) <= 0 or len(z_history) <= 0:
        raise ValueError("history and z_history cannot be empty")
    if len(history) != len(z_history):
        raise ValueError("history and z_history must have same length")

    cur = np.asarray(history[-1], dtype=np.uint16)
    z_cur = np.asarray(z_history[-1], dtype=np.int32)
    qn = int(qmul.shape[0])
    n_rounds = int(len(pair_rounds.rounds))
    if n_rounds <= 0:
        return cur.copy(), z_cur.copy()
    ridx = int(tick) % n_rounds
    pairs = pair_rounds.rounds[ridx]
    if pairs.size == 0:
        return cur.copy(), z_cur.copy()

    base = cur.astype(np.int32)
    base_z = z_cur.astype(np.int32)
    nxt = cur.copy()
    z_nxt = z_cur.copy()

    li = pairs[:, 0].astype(np.int32)
    ri = pairs[:, 1].astype(np.int32)
    sl = base[li]
    sr = base[ri]
    pl = sl // qn
    pr = sr // qn
    ql = sl % qn
    qr = sr % qn

    ql_new = qmul[ql, qr].astype(np.int32)
    qr_new = qmul[qr, ql].astype(np.int32)

    pl_new = pl.copy()
    pr_new = pr.copy()
    zl_new = base_z[li].copy()
    zr_new = base_z[ri].copy()

    depth_use = min(int(history_depth), max(0, len(history) - 1))
    for row in range(int(li.shape[0])):
        lnode = int(li[row])
        rnode = int(ri[row])
        gl = int(pl[row] % 3)
        gr = int(pr[row] % 3)
        base_dg = int((ql[row] + 2 * qr[row] + int(ridx)) % 3)

        left_hist = np.zeros((3,), dtype=np.int64)
        right_hist = np.zeros((3,), dtype=np.int64)
        for lag in range(1, depth_use + 1):
            frame = np.asarray(history[-1 - lag], dtype=np.uint16)
            lnodes = cache.nodes_within_hops(lnode, lag)
            rnodes = cache.nodes_within_hops(rnode, lag)
            lg = (frame[lnodes].astype(np.int32) // qn) % 3
            rg = (frame[rnodes].astype(np.int32) // qn) % 3
            left_hist += np.bincount(lg, minlength=3).astype(np.int64)
            right_hist += np.bincount(rg, minlength=3).astype(np.int64)

        dg_sel = _choose_dg(gl=gl, gr=gr, base_dg=base_dg, left_hist=left_hist, right_hist=right_hist)
        s = _dg_to_signed_step(dg_sel)

        lz = int(zl_new[row])
        rz = int(zr_new[row])

        if s > 0:
            # Desired transfer: right -> left.
            if rz <= 0:
                s = -1 if lz > 0 else 0
        elif s < 0:
            # Desired transfer: left -> right.
            if lz <= 0:
                s = 1 if rz > 0 else 0

        if s > 0:
            # right loses one, left gains one
            zr_new[row] = int(zr_new[row]) - 1
            zl_new[row] = int(zl_new[row]) + 1
            pl_new[row] = (pl[row] + 1) % int(phase_count)
            pr_new[row] = (pr[row] - 1) % int(phase_count)
        elif s < 0:
            # left loses one, right gains one
            zl_new[row] = int(zl_new[row]) - 1
            zr_new[row] = int(zr_new[row]) + 1
            pl_new[row] = (pl[row] - 1) % int(phase_count)
            pr_new[row] = (pr[row] + 1) % int(phase_count)
        else:
            pl_new[row] = int(pl[row])
            pr_new[row] = int(pr[row])

    # Hard non-negativity check: no clipping, fail fast on violation.
    if np.min(zl_new) < 0 or np.min(zr_new) < 0:
        raise ValueError("Hard invariant violated: integer energy below zero during pair update.")

    nxt[li] = (pl_new * qn + ql_new).astype(np.uint16)
    nxt[ri] = (pr_new * qn + qr_new).astype(np.uint16)
    z_nxt[li] = zl_new.astype(np.int32)
    z_nxt[ri] = zr_new.astype(np.int32)
    return nxt, z_nxt


def run_coherent_reconstruction_with_integer_energy(
    *,
    shape: Tuple[int, int, int],
    measurement_volume: VolumeBox,
    decoherence_ticks: int,
    domain_g: int,
    energy_a: int,
    q_id: int,
    config: CoherentConfig,
    energy_cfg: IntegerEnergyConfig,
    vacuum_sid: int = 0,
) -> Dict[str, object]:
    """High-level reconstruction with integer Z-energy transfer enabled."""

    nx, ny, nz = (int(shape[0]), int(shape[1]), int(shape[2]))
    meas_mask = measurement_mask((nx, ny, nz), measurement_volume)
    start_mask = backward_lightcone_start_mask(
        (nx, ny, nz),
        measurement_volume,
        decoherence_ticks=int(decoherence_ticks),
        stencil_id=str(config.stencil_id),
        boundary_mode=str(config.boundary_mode),
    )
    seed_sid = seed_state_id(domain_g=int(domain_g), energy_a=int(energy_a), q_id=int(q_id))
    world_t0 = seed_world((nx, ny, nz), start_mask=start_mask, seed_sid=seed_sid, vacuum_sid=int(vacuum_sid))
    z_t0 = initialize_energy_field(
        (nx, ny, nz),
        start_mask=start_mask,
        seed_z=int(energy_cfg.seed_z),
        vacuum_z=int(energy_cfg.vacuum_z),
    )
    assert_energy_nonnegative(z_t0)

    qmul = default_qmul_table()
    rounds = kpair.build_pair_rounds(
        nx,
        ny,
        nz,
        stencil_id=str(config.stencil_id),
        boundary_mode=str(config.boundary_mode),
    )
    cache = LightconeCache.from_pair_rounds(rounds)
    history = list(initialize_history(world_t0, depth=int(config.history_depth)))
    z_history = [z_t0.copy() for _ in range(int(config.history_depth) + 1)]

    g0 = gamma_sum_mod3(world_t0, qn=qmul.shape[0])
    e0 = total_energy_z(z_t0)
    for t in range(int(max(0, decoherence_ticks))):
        nxt, z_nxt = step_coherent_full_lightcone_with_integer_energy(
            history,
            z_history,
            rounds,
            qmul=qmul,
            cache=cache,
            tick=int(t),
            history_depth=int(config.history_depth),
            energy_cfg=energy_cfg,
            phase_count=PHASE_COUNT,
        )
        history.append(nxt)
        z_history.append(z_nxt)
        keep = int(max(1, int(config.history_depth) + 1))
        if len(history) > keep:
            history = history[-keep:]
        if len(z_history) > keep:
            z_history = z_history[-keep:]
        assert_energy_nonnegative(z_history[-1])

    world_meas = np.asarray(history[-1], dtype=np.uint16)
    z_meas = np.asarray(z_history[-1], dtype=np.int32)
    assert_energy_nonnegative(z_meas)
    g1 = gamma_sum_mod3(world_meas, qn=qmul.shape[0])
    e1 = total_energy_z(z_meas)

    n_cells = int(nx * ny * nz)
    n_meas = int(np.sum(meas_mask))
    n_start = int(np.sum(start_mask))
    xs, ys, zs = np.where(meas_mask)
    flat_idx = ((xs.astype(np.int64) * int(ny) + ys.astype(np.int64)) * int(nz) + zs.astype(np.int64)).astype(np.int64)
    meas_states = world_meas[flat_idx.astype(np.int32)]
    meas_energy = z_meas[flat_idx.astype(np.int32)]
    phases, qvals = decode_sid(meas_states, qn=qmul.shape[0])

    return {
        "kernel_profile": KERNEL_PROFILE + "_with_integer_energy",
        "shape": [nx, ny, nz],
        "stencil_id": str(config.stencil_id),
        "boundary_mode": str(config.boundary_mode),
        "history_depth": int(config.history_depth),
        "decoherence_ticks": int(decoherence_ticks),
        "seed": {
            "domain_g": int(domain_g) % 3,
            "energy_a": int(energy_a) % 4,
            "q_id": int(q_id) % Q_COUNT,
            "seed_sid": int(seed_sid),
            "seed_z": int(energy_cfg.seed_z),
            "vacuum_z": int(energy_cfg.vacuum_z),
        },
        "counts": {
            "cells_total": int(n_cells),
            "start_volume_cells": int(n_start),
            "measurement_cells": int(n_meas),
        },
        "triality": {
            "gamma_t0": int(g0),
            "gamma_t_meas": int(g1),
            "conserved": bool(int(g0) == int(g1)),
        },
        "energy_z": {
            "total_t0": int(e0),
            "total_t_meas": int(e1),
            "conserved": bool(int(e0) == int(e1)),
            "min_t_meas": int(np.min(z_meas)) if z_meas.size > 0 else 0,
            "nonnegative": bool(np.min(z_meas) >= 0) if z_meas.size > 0 else True,
            "measurement_sum": int(np.sum(meas_energy)),
        },
        "measurement_summary": {
            "phase_hist_12": np.bincount(phases.astype(np.int32), minlength=12).astype(int).tolist(),
            "q_hist_nonzero": int(np.sum(np.bincount(qvals.astype(np.int32), minlength=Q_COUNT) > 0)),
        },
        "measurement_states": meas_states.astype(int).tolist(),
        "measurement_energy_z": meas_energy.astype(int).tolist(),
    }
