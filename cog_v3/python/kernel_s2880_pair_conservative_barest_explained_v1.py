"""Barest S2880 kernel, written as a teaching file.

This is a minimal, readable version of the current pair-conservative kernel.

Audience goal:
- You can read this even if you are new to algebra and simulation kernels.
- Every step is commented in plain language: what it does, and why we need it.

Model summary:
- A world is a 3D grid, flattened into a 1D array.
- Each cell stores one integer state id:
      sid = phase * 240 + q_id
  where:
      phase is in Z12 (0..11)
      q_id is in Q240 (0..239)

What this kernel guarantees exactly:
- Pair events are computed from the PREVIOUS tick snapshot only.
- For each pair event, triality (generation sum mod 3) is conserved exactly.

What this kernel does not represent yet:
- Physical energy/momentum/angular momentum are not explicit variables here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np

from cog_v3.calc import build_v3_c12_singlet_doublet_clock_shift_sparse_v1 as c12
from cog_v3.python.kernel_s2880_pair_conservative_v1 import build_pair_rounds


# Fixed alphabet sizes for this lane.
PHASE_COUNT = 12
Q240_COUNT = 240


@dataclass(frozen=True)
class SimpleRounds:
    """Disjoint edge rounds.

    rounds[k] is an int32 array with shape [n_pairs, 2].
    Each row is one pair (left_index, right_index).
    "Disjoint" means no cell appears twice in the same round.
    """

    rounds: Tuple[np.ndarray, ...]


def make_simple_rounds(
    nx: int,
    ny: int,
    nz: int,
    *,
    stencil_id: str = "axial6",
    boundary_mode: str = "fixed_vacuum",
) -> SimpleRounds:
    """Build pair rounds using the existing edge-coloring utility.

    Why this exists:
    - The update rule is pair-based.
    - We need non-overlapping pairs inside each sub-step so one cell is not
      "pulled" by two neighbors in the same instant.
    """

    pr = build_pair_rounds(
        int(nx),
        int(ny),
        int(nz),
        stencil_id=str(stencil_id),
        boundary_mode=str(boundary_mode),
    )
    return SimpleRounds(rounds=pr.rounds)


def decode_sid(sid: np.ndarray, qn: int = Q240_COUNT) -> Tuple[np.ndarray, np.ndarray]:
    """Split state id into (phase, q_id)."""

    sid_i32 = np.asarray(sid, dtype=np.int32)
    phase = sid_i32 // int(qn)
    q_id = sid_i32 % int(qn)
    return phase, q_id


def encode_sid(phase: np.ndarray, q_id: np.ndarray, qn: int = Q240_COUNT) -> np.ndarray:
    """Join (phase, q_id) back into a compact state id."""

    return (np.asarray(phase, dtype=np.int32) * int(qn) + np.asarray(q_id, dtype=np.int32)).astype(np.uint16)


def step_barest(
    world: np.ndarray,
    rounds: SimpleRounds,
    *,
    qmul: np.ndarray,
    tick: int,
    phase_count: int = PHASE_COUNT,
) -> np.ndarray:
    """One tick of the minimal pair-conservative S2880 kernel.

    High-level flow:
    1) Pick one disjoint round for this tick.
    2) Read all pair inputs from the PRE-TICK snapshot.
    3) Compute pair outputs:
       - Q240 channel (non-commutative multiplication table)
       - phase channel (plus/minus transfer that conserves triality per pair)
    4) Write outputs to a new world.

    Why one round per tick?
    - Strict local-causal stepping: each tick uses one non-overlapping edge set.
    - This avoids hidden order bias where some cells update more often inside a tick.
    """

    cur = np.asarray(world, dtype=np.uint16)
    if cur.ndim != 1:
        raise ValueError("world must be a flat uint16 array")
    if len(rounds.rounds) == 0:
        return cur.copy()

    # Pick the round in a deterministic cycle.
    ridx = int(tick) % int(len(rounds.rounds))
    pairs = rounds.rounds[ridx]
    if pairs.size == 0:
        return cur.copy()

    # IMPORTANT: read from PRE-TICK snapshot only.
    # This is what keeps the update physically clean:
    # every pair event at this tick sees the same "old" world.
    base = cur.astype(np.int32)
    nxt = cur.copy()

    left_idx = pairs[:, 0].astype(np.int32)
    right_idx = pairs[:, 1].astype(np.int32)

    left_sid = base[left_idx]
    right_sid = base[right_idx]

    left_phase, left_q = decode_sid(left_sid, qn=qmul.shape[0])
    right_phase, right_q = decode_sid(right_sid, qn=qmul.shape[0])

    # Q240 interaction channel.
    # Why both directions?
    # - Octonion-like multiplication is not commutative.
    # - left acted by right is not the same as right acted by left.
    left_q_new = qmul[left_q, right_q].astype(np.int32)
    right_q_new = qmul[right_q, left_q].astype(np.int32)

    # Triality-conservative phase transfer.
    # dg is in {0,1,2}. We add dg to left and subtract dg from right.
    #
    # Why this pattern?
    # - It guarantees pairwise conservation of generation sum modulo 3:
    #       (gL' + gR') mod 3 = (gL + gR) mod 3
    #   because g = phase mod 3 and we apply +dg / -dg.
    dg = (left_q + 2 * right_q + int(ridx)) % 3
    left_phase_new = (left_phase + dg) % int(phase_count)
    right_phase_new = (right_phase - dg) % int(phase_count)

    nxt[left_idx] = encode_sid(left_phase_new, left_q_new, qn=qmul.shape[0])
    nxt[right_idx] = encode_sid(right_phase_new, right_q_new, qn=qmul.shape[0])
    return nxt


def run_barest(
    world: np.ndarray,
    rounds: SimpleRounds,
    *,
    qmul: np.ndarray,
    ticks: int,
    phase_count: int = PHASE_COUNT,
) -> np.ndarray:
    """Run many ticks with the bare kernel."""

    cur = np.asarray(world, dtype=np.uint16).copy()
    for t in range(int(ticks)):
        cur = step_barest(
            cur,
            rounds,
            qmul=qmul,
            tick=int(t),
            phase_count=int(phase_count),
        )
    return cur


def gamma_sum_mod3(world: np.ndarray, *, qn: int = Q240_COUNT) -> int:
    """Global triality charge: sum(phase mod 3) mod 3."""

    phase, _ = decode_sid(np.asarray(world, dtype=np.uint16), qn=int(qn))
    return int(np.sum(phase % 3) % 3)


def default_qmul_table() -> np.ndarray:
    """Load Q240 multiplication table used by this lane."""

    return c12.build_qmul_table()


if __name__ == "__main__":
    # Tiny sanity check so this file is easy to test quickly.
    nx, ny, nz = 5, 5, 5
    n = nx * ny * nz
    qmul = default_qmul_table()
    rounds = make_simple_rounds(nx, ny, nz, stencil_id="axial6", boundary_mode="fixed_vacuum")

    # Start with all-vacuum-like state sid=0.
    world0 = np.zeros(n, dtype=np.uint16)
    g0 = gamma_sum_mod3(world0, qn=qmul.shape[0])

    world1 = run_barest(world0, rounds, qmul=qmul, ticks=8)
    g1 = gamma_sum_mod3(world1, qn=qmul.shape[0])

    print("Barest kernel sanity check")
    print(f"cells={n}, rounds={len(rounds.rounds)}, gamma0={g0}, gamma1={g1}")
