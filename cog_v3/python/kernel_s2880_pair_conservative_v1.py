"""S2880 pair-conservative kernel (Phase M target lane).

This module provides synchronous pair-event updates on S2880 states:
  s = (phase in Z12, q in Q240), encoded as sid = phase * 240 + q_id.

Design goals:
- Pair updates are computed from a shared pre-round state (no partner desync).
- Updates are committed on disjoint edge rounds (edge coloring).
- Per-pair generation triality is exactly conserved:
    (g_i' + g_j') mod 3 = (g_i + g_j) mod 3
  where g = phase mod 3.

Notes:
- This lane enforces triality conservation exactly.
- Momentum/angular-momentum/energy are not represented in this state-only kernel.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

import numpy as np

from cog_v3.calc import build_v3_c12_singlet_doublet_clock_shift_sparse_v1 as c12


KERNEL_PROFILE = "cog_v3_s2880_pair_conservative_v1"
PHASE_COUNT = 12


@dataclass(frozen=True)
class PairRounds:
    nx: int
    ny: int
    nz: int
    stencil_id: str
    boundary_mode: str
    rounds: Tuple[np.ndarray, ...]  # each: int32 shape [n_pairs, 2], disjoint pairs


def offsets_for_stencil(stencil_id: str) -> List[Tuple[int, int, int]]:
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


def _idx(x: int, y: int, z: int, ny: int, nz: int) -> int:
    return (int(x) * int(ny) + int(y)) * int(nz) + int(z)


def _unique_edges(
    nx: int,
    ny: int,
    nz: int,
    offsets: Sequence[Tuple[int, int, int]],
    boundary_mode: str,
) -> List[Tuple[int, int]]:
    wrap = str(boundary_mode) == "periodic"
    edges: set[Tuple[int, int]] = set()
    for x in range(int(nx)):
        for y in range(int(ny)):
            for z in range(int(nz)):
                a = _idx(x, y, z, ny, nz)
                for dx, dy, dz in offsets:
                    qx = x + int(dx)
                    qy = y + int(dy)
                    qz = z + int(dz)
                    if wrap:
                        qx %= int(nx)
                        qy %= int(ny)
                        qz %= int(nz)
                    else:
                        if not (0 <= qx < int(nx) and 0 <= qy < int(ny) and 0 <= qz < int(nz)):
                            continue
                    b = _idx(qx, qy, qz, ny, nz)
                    if a == b:
                        continue
                    u, v = (a, b) if a < b else (b, a)
                    edges.add((int(u), int(v)))
    return sorted(edges)


def _edge_color_rounds(edges: Sequence[Tuple[int, int]], n_nodes: int) -> Tuple[np.ndarray, ...]:
    # Greedy edge coloring: assign smallest color not used by either endpoint.
    used: List[set[int]] = [set() for _ in range(int(n_nodes))]
    by_color: Dict[int, List[Tuple[int, int]]] = {}
    for (u, v) in edges:
        c = 0
        uu = int(u)
        vv = int(v)
        while c in used[uu] or c in used[vv]:
            c += 1
        used[uu].add(c)
        used[vv].add(c)
        by_color.setdefault(c, []).append((uu, vv))
    rounds: List[np.ndarray] = []
    for c in sorted(by_color.keys()):
        arr = np.asarray(by_color[c], dtype=np.int32)
        if arr.size == 0:
            continue
        rounds.append(arr.reshape((-1, 2)))
    return tuple(rounds)


def build_pair_rounds(
    nx: int,
    ny: int,
    nz: int,
    *,
    stencil_id: str = "axial6",
    boundary_mode: str = "fixed_vacuum",
) -> PairRounds:
    offsets = offsets_for_stencil(str(stencil_id))
    edges = _unique_edges(int(nx), int(ny), int(nz), offsets, str(boundary_mode))
    n_nodes = int(nx) * int(ny) * int(nz)
    rounds = _edge_color_rounds(edges, int(n_nodes))
    return PairRounds(
        nx=int(nx),
        ny=int(ny),
        nz=int(nz),
        stencil_id=str(stencil_id),
        boundary_mode=str(boundary_mode),
        rounds=rounds,
    )


def _decode_sid(world: np.ndarray, qn: int) -> Tuple[np.ndarray, np.ndarray]:
    sid = world.astype(np.int32)
    p = sid // int(qn)
    q = sid % int(qn)
    return p, q


def step_pair_conservative(
    world: np.ndarray,
    pair_rounds: PairRounds,
    *,
    qmul: np.ndarray,
    phase_count: int = PHASE_COUNT,
    global_seed: int = 0,
    tick: int = 0,
    shuffle_round_order: bool = False,
) -> np.ndarray:
    qn = int(qmul.shape[0])
    cur = np.asarray(world, dtype=np.uint16).copy()
    if cur.ndim != 1:
        raise ValueError("world must be a flat uint16 array of sid states")

    order = list(range(len(pair_rounds.rounds)))
    if bool(shuffle_round_order) and len(order) > 1:
        # Deterministic pseudo-shuffle per tick and seed.
        rr = np.random.default_rng(int(global_seed) + 104729 * (int(tick) + 1))
        rr.shuffle(order)

    for ridx in order:
        pairs = pair_rounds.rounds[int(ridx)]
        if pairs.size == 0:
            continue
        li = pairs[:, 0].astype(np.int32)
        ri = pairs[:, 1].astype(np.int32)
        sl = cur[li].astype(np.int32)
        sr = cur[ri].astype(np.int32)
        pl = sl // int(qn)
        pr = sr // int(qn)
        ql = sl % int(qn)
        qr = sr % int(qn)

        # Non-commutative q-channel pair mixing.
        ql_new = qmul[ql, qr].astype(np.int32)
        qr_new = qmul[qr, ql].astype(np.int32)

        # Deterministic triality transfer channel.
        # dg in {0,1,2}; pairwise phase updates are +dg and -dg.
        dg = (ql + 2 * qr + int(ridx)) % 3
        pl_new = (pl + dg) % int(phase_count)
        pr_new = (pr - dg) % int(phase_count)

        cur[li] = (pl_new * int(qn) + ql_new).astype(np.uint16)
        cur[ri] = (pr_new * int(qn) + qr_new).astype(np.uint16)
    return cur


def run_ticks(
    world: np.ndarray,
    pair_rounds: PairRounds,
    *,
    qmul: np.ndarray,
    ticks: int,
    phase_count: int = PHASE_COUNT,
    global_seed: int = 0,
    shuffle_round_order: bool = False,
) -> np.ndarray:
    cur = np.asarray(world, dtype=np.uint16).copy()
    for t in range(int(ticks)):
        cur = step_pair_conservative(
            cur,
            pair_rounds,
            qmul=qmul,
            phase_count=int(phase_count),
            global_seed=int(global_seed),
            tick=int(t),
            shuffle_round_order=bool(shuffle_round_order),
        )
    return cur


def gamma_sum_mod3(world: np.ndarray, *, qn: int) -> int:
    p, _q = _decode_sid(np.asarray(world, dtype=np.uint16), int(qn))
    return int(np.sum(p % 3) % 3)


def generation_shift_T(world: np.ndarray, *, qn: int, phase_count: int = PHASE_COUNT, k_shift: int = 1) -> np.ndarray:
    sid = np.asarray(world, dtype=np.uint16).astype(np.int32)
    p = sid // int(qn)
    q = sid % int(qn)
    p2 = (p + 4 * int(k_shift)) % int(phase_count)
    return (p2 * int(qn) + q).astype(np.uint16)


def default_qmul_table() -> np.ndarray:
    return c12.build_qmul_table()

