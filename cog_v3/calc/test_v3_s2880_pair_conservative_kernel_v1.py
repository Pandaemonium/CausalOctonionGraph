from __future__ import annotations

import numpy as np

from cog_v3.python import kernel_s2880_pair_conservative_v1 as kp


def _rng_world(n: int, s_size: int, seed: int) -> np.ndarray:
    rr = np.random.default_rng(int(seed))
    return rr.integers(0, int(s_size), size=(int(n),), dtype=np.uint16)


def test_pair_rounds_are_disjoint_per_round() -> None:
    rounds = kp.build_pair_rounds(11, 7, 7, stencil_id="axial6", boundary_mode="fixed_vacuum")
    n = int(11 * 7 * 7)
    for arr in rounds.rounds:
        used = np.zeros((n,), dtype=np.bool_)
        for a, b in arr.tolist():
            ia = int(a)
            ib = int(b)
            assert ia != ib
            assert not bool(used[ia])
            assert not bool(used[ib])
            used[ia] = True
            used[ib] = True


def test_gamma_conservation_exact_per_tick() -> None:
    qmul = kp.default_qmul_table()
    qn = int(qmul.shape[0])
    s_size = int(12 * qn)
    rounds = kp.build_pair_rounds(9, 7, 7, stencil_id="axial6", boundary_mode="fixed_vacuum")
    world = _rng_world(9 * 7 * 7, s_size=s_size, seed=20260303)
    g0 = kp.gamma_sum_mod3(world, qn=qn)
    cur = world
    for t in range(16):
        cur = kp.step_pair_conservative(cur, rounds, qmul=qmul, tick=t, global_seed=1337)
        g1 = kp.gamma_sum_mod3(cur, qn=qn)
        assert int(g1) == int(g0)


def test_global_z3_equivariance_one_step() -> None:
    qmul = kp.default_qmul_table()
    qn = int(qmul.shape[0])
    s_size = int(12 * qn)
    rounds = kp.build_pair_rounds(8, 6, 6, stencil_id="axial6", boundary_mode="fixed_vacuum")
    world = _rng_world(8 * 6 * 6, s_size=s_size, seed=77)

    lhs = kp.step_pair_conservative(
        kp.generation_shift_T(world, qn=qn, k_shift=1),
        rounds,
        qmul=qmul,
        tick=5,
        global_seed=999,
    )
    rhs = kp.generation_shift_T(
        kp.step_pair_conservative(world, rounds, qmul=qmul, tick=5, global_seed=999),
        qn=qn,
        k_shift=1,
    )
    assert np.array_equal(lhs, rhs)


def main() -> None:
    test_pair_rounds_are_disjoint_per_round()
    test_gamma_conservation_exact_per_tick()
    test_global_z3_equivariance_one_step()
    print("ok: test_v3_s2880_pair_conservative_kernel_v1")


if __name__ == "__main__":
    main()
