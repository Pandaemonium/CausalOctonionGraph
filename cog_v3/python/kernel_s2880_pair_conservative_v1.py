"""S2880 pair-conservative kernel (Phase M target lane).

This module provides synchronous pair-event updates on S2880 states.

Canonical per-site seed tuple:
  (domain in Z3, octavian_id in Q240, energy_n in Z, energy_phase in Z4)

Current runtime state encoding for this lane:
  s = (phase in Z12, q in Q240), encoded as sid = phase * 240 + q_id,
  with phase = 4*domain + 3*energy_phase (mod 12).
  This embeds:
    - domain step +1  => +4 in Z12 (120-degree rotor)
    - energy_phase +1 => +3 in Z12 ( 90-degree rotor)
  energy_n is carried as a parallel metadata/world lane but is not yet evolved.

Design goals:
- Pair updates are computed from a shared pre-round state (no partner desync).
- Updates are committed on disjoint edge rounds (edge coloring).
- Per-pair generation triality is exactly conserved:
    (g_i' + g_j') mod 3 = (g_i + g_j) mod 3
  where g = phase mod 3.

Notes:
- This lane enforces triality conservation exactly.
- Momentum/angular-momentum/energy are not represented in this state-only kernel.
- Default tick semantics are strict light-cone:
  one disjoint pair round is applied per tick, from pre-tick states only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

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


@dataclass(frozen=True)
class SiteSeed:
    """Canonical per-site seed tuple for this lane."""

    domain: int  # Z3 observer-reference domain, in {0,1,2}
    octavian_id: int  # Q240 id, in [0, 239]
    energy_n: int  # integer Z-energy metadata (not evolved in this lane)
    energy_phase: int  # Z4 phase, in {0,1,2,3}


def phase_idx_from_domain_energy_phase(domain: int, energy_phase: int, *, phase_count: int = PHASE_COUNT) -> int:
    """Map (domain, energy_phase) to Z12 index via phase = 4*domain + 3*energy_phase."""
    d = int(domain) % 3
    a = int(energy_phase) % 4
    return int((4 * d + 3 * a) % int(phase_count))


def decode_phase_idx(phase_idx: int, *, phase_count: int = PHASE_COUNT) -> Tuple[int, int]:
    """Inverse map from phase_idx to (domain, energy_phase) under phase = 4d + 3a."""
    p = int(phase_idx) % int(phase_count)
    # Small finite inverse on Z12; unique solution in d in {0,1,2}, a in {0,1,2,3}.
    for d in range(3):
        for a in range(4):
            if int((4 * d + 3 * a) % int(phase_count)) == int(p):
                return int(d), int(a)
    raise ValueError(f"Could not decode phase_idx={phase_idx} in Z{int(phase_count)}")


def sid_from_site_seed(seed: SiteSeed, *, qn: int = 240, phase_count: int = PHASE_COUNT) -> int:
    """Encode SiteSeed to sid used by this S2880 kernel lane."""
    if not (0 <= int(seed.octavian_id) < int(qn)):
        raise ValueError(f"octavian_id must be in [0, {int(qn)-1}]")
    p = phase_idx_from_domain_energy_phase(int(seed.domain), int(seed.energy_phase), phase_count=phase_count)
    return int(p * int(qn) + int(seed.octavian_id))


def site_seed_from_sid(sid: int, *, energy_n: int = 0, qn: int = 240, phase_count: int = PHASE_COUNT) -> SiteSeed:
    """Decode sid back into SiteSeed fields (energy_n injected from metadata lane)."""
    sid_i = int(sid)
    p = int(sid_i // int(qn))
    q = int(sid_i % int(qn))
    d, a = decode_phase_idx(int(p), phase_count=phase_count)
    return SiteSeed(domain=int(d), octavian_id=int(q), energy_n=int(energy_n), energy_phase=int(a))


def build_uniform_seed_world(
    nx: int,
    ny: int,
    nz: int,
    *,
    seed: SiteSeed,
    qn: int = 240,
    phase_count: int = PHASE_COUNT,
) -> Tuple[np.ndarray, np.ndarray]:
    """Create flat world arrays with same seed at every site.

    Returns:
    - world_sid: uint16 flat array used by step_pair_conservative.
    - world_energy: int32 flat array (metadata lane; not evolved in this kernel).
    """
    n = int(nx) * int(ny) * int(nz)
    sid = int(sid_from_site_seed(seed, qn=qn, phase_count=phase_count))
    world_sid = np.full((n,), np.uint16(sid), dtype=np.uint16)
    world_energy = np.full((n,), np.int32(int(seed.energy_n)), dtype=np.int32)
    return world_sid, world_energy


def encode_site_field_arrays(
    domain: np.ndarray,
    octavian_id: np.ndarray,
    energy_n: np.ndarray,
    energy_phase: np.ndarray,
    *,
    qn: int = 240,
    phase_count: int = PHASE_COUNT,
) -> Tuple[np.ndarray, np.ndarray]:
    """Encode per-site field arrays into (world_sid, world_energy).

    All inputs must be broadcast-compatible 1D-equivalent arrays of equal shape.
    The output arrays are flat:
    - world_sid: uint16
    - world_energy: int32 (metadata lane; non-dynamical in this kernel)
    """
    d = np.asarray(domain, dtype=np.int32).reshape(-1)
    q = np.asarray(octavian_id, dtype=np.int32).reshape(-1)
    e = np.asarray(energy_n, dtype=np.int32).reshape(-1)
    a = np.asarray(energy_phase, dtype=np.int32).reshape(-1)
    n = int(d.size)
    if int(q.size) != n or int(e.size) != n or int(a.size) != n:
        raise ValueError("domain, octavian_id, energy_n, energy_phase must have same flattened length")
    if np.any(q < 0) or np.any(q >= int(qn)):
        raise ValueError(f"octavian_id values must be in [0, {int(qn)-1}]")

    p = (4 * (d % 3) + 3 * (a % 4)) % int(phase_count)
    sid = p * int(qn) + q
    world_sid = sid.astype(np.uint16, copy=False)
    world_energy = e.astype(np.int32, copy=False)
    return world_sid, world_energy


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
    use_all_rounds_per_tick: bool = False,
) -> np.ndarray:
    qn = int(qmul.shape[0])
    cur = np.asarray(world, dtype=np.uint16).copy()
    if cur.ndim != 1:
        raise ValueError("world must be a flat uint16 array of sid states")

    n_rounds = int(len(pair_rounds.rounds))
    if n_rounds <= 0:
        return cur

    def _apply_round(base: np.ndarray, ridx: int) -> np.ndarray:
        pairs = pair_rounds.rounds[int(ridx)]
        if pairs.size == 0:
            return base.copy()
        out = base.copy()
        li = pairs[:, 0].astype(np.int32)
        ri = pairs[:, 1].astype(np.int32)
        sl = base[li].astype(np.int32)
        sr = base[ri].astype(np.int32)
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

        out[li] = (pl_new * int(qn) + ql_new).astype(np.uint16)
        out[ri] = (pr_new * int(qn) + qr_new).astype(np.uint16)
        return out

    if not bool(use_all_rounds_per_tick):
        # Strict light-cone semantics: one disjoint round per tick from pre-tick state.
        if bool(shuffle_round_order):
            rr = np.random.default_rng(int(global_seed) + 104729 * (int(tick) + 1))
            ridx = int(rr.integers(0, n_rounds))
        else:
            ridx = int(int(tick) % n_rounds)
        return _apply_round(cur, int(ridx))

    # Optional non-default microstep sweep mode.
    order = list(range(n_rounds))
    if bool(shuffle_round_order) and len(order) > 1:
        rr = np.random.default_rng(int(global_seed) + 104729 * (int(tick) + 1))
        rr.shuffle(order)
    nxt = cur
    for ridx in order:
        nxt = _apply_round(nxt, int(ridx))
    return nxt


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


# ── Z4 EM-phase symmetry tools (RFC-029) ─────────────────────────────────────


def z4_phase_shift_T(
    world: np.ndarray,
    *,
    qn: int,
    phase_count: int = PHASE_COUNT,
    k_shift: int = 1,
) -> np.ndarray:
    """Global EM phase shift: a -> a + k_shift (mod 4) via p -> p + 3*k_shift (mod 12).

    T_Z4 is the generator of the Z4 symmetry of the EM sub-clock.
    It advances every site's Z4 phase by k_shift steps while leaving
    generation g = p mod 3 and all Q240 components unchanged.

    Equivariance target (RFC-029 Section 9):
        K(T_Z4(S)) == T_Z4(K(S))  for any kernel step K.
    """
    sid = np.asarray(world, dtype=np.uint16).astype(np.int32)
    p = sid // int(qn)
    q = sid % int(qn)
    p2 = (p + 3 * int(k_shift)) % int(phase_count)
    return (p2 * int(qn) + q).astype(np.uint16)


def z4_sum(world: np.ndarray, *, qn: int) -> int:
    """Sum of all Z4 sub-clock values (a = p mod 4) across all sites.

    Returns the integer sum (not reduced mod 4).

    Under step_em_photon_round, integer wrapping in Z4 means the integer
    sum can change by multiples of 4 (e.g., +4 when a pair has a_left=0
    and Dp=+3 gives Da=+3 rather than -1). The conserved quantity is
    z4_sum(world) mod 4, not the integer sum itself.
    """
    p, _ = _decode_sid(np.asarray(world, dtype=np.uint16), int(qn))
    return int(np.sum(p % 4))


def step_em_photon_round(
    world: np.ndarray,
    pair_rounds: PairRounds,
    *,
    qn: int,
    phase_count: int = PHASE_COUNT,
    tick: int = 0,
) -> np.ndarray:
    """One disjoint round of R3 (photon) pair hops.

    For each pair (i, j) in the selected disjoint round:
    - The hop fires only when g_i == g_j (generation-matched pairs).
      EM interactions are generation-diagonal; this enforces Dg = 0.
    - Direction (which site emits, which absorbs) is chosen deterministically
      from (p_i + p_j) mod 2 so neither orientation is preferred.
    - Emitter: Dp = +3  ->  Da = -1 mod 4  (loses one Z4 quantum).
    - Absorber: Dp = -3  ->  Da = +1 mod 4  (gains one Z4 quantum).
    - Q240 components are unchanged (photon is color-neutral, RFC-029 Sec 4.3).

    Conserved exactly per event:
    - Triality: Dg = +/-3 mod 3 = 0 on both sites.
    - Z4 total: sum(a) mod 4 is unchanged across the round (integer sum may change by multiples of 4 due to Z4 wrap at a=0/3).

    RFC-029 Acceptance Criterion 1: R3 hops leave g and q unchanged.
    """
    qn_int = int(qn)
    pc = int(phase_count)
    n_rounds = len(pair_rounds.rounds)
    if n_rounds == 0:
        return np.asarray(world, dtype=np.uint16).copy()
    ridx = int(tick) % n_rounds
    pairs = pair_rounds.rounds[ridx]
    if pairs.size == 0:
        return np.asarray(world, dtype=np.uint16).copy()

    cur = np.asarray(world, dtype=np.uint16).copy()
    li = pairs[:, 0].astype(np.int32)
    ri = pairs[:, 1].astype(np.int32)
    sl = cur[li].astype(np.int32)
    sr = cur[ri].astype(np.int32)
    pl = sl // qn_int
    pr = sr // qn_int
    ql = sl % qn_int
    qr = sr % qn_int

    # EM interaction fires only between generation-matched pairs.
    em_active = (pl % 3) == (pr % 3)

    # Direction: (pl + pr) % 2 == 0 -> left emits; else right emits.
    # Both orientations conserve triality and Z4 total.
    left_emits = ((pl + pr) % 2) == 0
    dp_l = np.where(left_emits, 3, -3)
    dp_r = -dp_l

    pl_new = np.where(em_active, (pl + dp_l) % pc, pl)
    pr_new = np.where(em_active, (pr + dp_r) % pc, pr)

    # Q240 components are unchanged.
    cur[li] = (pl_new * qn_int + ql).astype(np.uint16)
    cur[ri] = (pr_new * qn_int + qr).astype(np.uint16)
    return cur


def check_z4_equivariance(
    world: np.ndarray,
    pair_rounds: PairRounds,
    *,
    qmul: np.ndarray,
    phase_count: int = PHASE_COUNT,
    qn: Optional[int] = None,
    k_shift: int = 1,
    tick: int = 0,
) -> bool:
    """Test K(T_Z4(S)) == T_Z4(K(S)) for step_pair_conservative.

    Verifies that the triality kernel commutes with global Z4 phase shifts.
    This is the EM gauge equivariance regression check required by
    RFC-029 Acceptance Criterion 4. A failure means the kernel has a
    preferred Z4 phase and breaks EM symmetry.

    Returns True if equivariance holds exactly (integer arithmetic identity).
    """
    if qn is None:
        qn = int(qmul.shape[0])
    w = np.asarray(world, dtype=np.uint16)

    # Path 1: shift then step.
    lhs = step_pair_conservative(
        z4_phase_shift_T(w, qn=qn, phase_count=phase_count, k_shift=k_shift),
        pair_rounds,
        qmul=qmul,
        phase_count=phase_count,
        tick=tick,
    )
    # Path 2: step then shift.
    rhs = z4_phase_shift_T(
        step_pair_conservative(w, pair_rounds, qmul=qmul, phase_count=phase_count, tick=tick),
        qn=qn,
        phase_count=phase_count,
        k_shift=k_shift,
    )
    return bool(np.array_equal(lhs, rhs))


def audit_per_event_triality(
    world_pre: np.ndarray,
    world_post: np.ndarray,
    pair_rounds: PairRounds,
    *,
    qn: int,
    ridx: int = 0,
) -> Tuple[bool, int]:
    """Verify per-event triality conservation for one round.

    For every active pair (i, j) in round `ridx` checks:
        (g_i' + g_j') mod 3 == (g_i + g_j) mod 3

    Returns (all_conserved, n_violations).
    Per RFC-028 Section 4.2, n_violations must be zero for every round.
    """
    qn_int = int(qn)
    pairs = pair_rounds.rounds[int(ridx)]
    pre = np.asarray(world_pre, dtype=np.uint16)
    post = np.asarray(world_post, dtype=np.uint16)
    li = pairs[:, 0]
    ri = pairs[:, 1]
    gl_pre = (pre[li].astype(np.int32) // qn_int) % 3
    gr_pre = (pre[ri].astype(np.int32) // qn_int) % 3
    gl_post = (post[li].astype(np.int32) // qn_int) % 3
    gr_post = (post[ri].astype(np.int32) // qn_int) % 3
    violations = int(np.sum((gl_pre + gr_pre) % 3 != (gl_post + gr_post) % 3))
    return violations == 0, violations
