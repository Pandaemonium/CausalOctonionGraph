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


# ── RFC-029: Z4 EM-phase and photon tests ─────────────────────────────────────


def test_z4_phase_shift_properties() -> None:
    qmul = kp.default_qmul_table()
    qn = int(qmul.shape[0])
    world = _rng_world(100, s_size=12 * qn, seed=42)
    p = world.astype(np.int32) // qn

    # T_Z4 leaves generation g = p mod 3 unchanged.
    shifted = kp.z4_phase_shift_T(world, qn=qn, k_shift=1)
    p_s = shifted.astype(np.int32) // qn
    assert np.array_equal(p % 3, p_s % 3), "T_Z4 must not change generation"

    # T_Z4 with k_shift=1 shifts a = p mod 4 by +3 mod 4 (= -1 mod 4).
    assert np.array_equal((p % 4 + 3) % 4, p_s % 4), "T_Z4 (k=1) must shift a by 3 mod 4"

    # T_Z4^4 = identity: 4 * Dp = 4*3 = 12 = 0 mod 12.
    assert np.array_equal(world, kp.z4_phase_shift_T(world, qn=qn, k_shift=4))


def test_z4_sum_conserved_by_em_round() -> None:
    qmul = kp.default_qmul_table()
    qn = int(qmul.shape[0])
    rounds = kp.build_pair_rounds(9, 7, 7, stencil_id="axial6", boundary_mode="fixed_vacuum")
    world = _rng_world(9 * 7 * 7, s_size=12 * qn, seed=20260303)
    z4_before = kp.z4_sum(world, qn=qn)
    cur = world.copy()
    for t in range(16):
        cur = kp.step_em_photon_round(cur, rounds, qn=qn, tick=t)
        assert kp.z4_sum(cur, qn=qn) % 4 == z4_before % 4, f"Z4 sum (mod 4) changed at tick {t}"


def test_em_round_leaves_g_and_q_unchanged() -> None:
    qmul = kp.default_qmul_table()
    qn = int(qmul.shape[0])
    rounds = kp.build_pair_rounds(8, 6, 6, stencil_id="axial6", boundary_mode="fixed_vacuum")
    world = _rng_world(8 * 6 * 6, s_size=12 * qn, seed=20260303)
    g_before = world.astype(np.int32) // qn % 3
    q_before = world.astype(np.int32) % qn
    cur = world.copy()
    for t in range(16):
        cur = kp.step_em_photon_round(cur, rounds, qn=qn, tick=t)
    assert np.array_equal(g_before, cur.astype(np.int32) // qn % 3), "R3 hops changed generation"
    assert np.array_equal(q_before, cur.astype(np.int32) % qn), "R3 hops changed Q240"


def test_z4_equivariance_step_conservative() -> None:
    qmul = kp.default_qmul_table()
    qn = int(qmul.shape[0])
    rounds = kp.build_pair_rounds(8, 6, 6, stencil_id="axial6", boundary_mode="fixed_vacuum")
    world = _rng_world(8 * 6 * 6, s_size=12 * qn, seed=2026)
    for tick in range(8):
        ok = kp.check_z4_equivariance(world, rounds, qmul=qmul, tick=tick)
        assert ok, f"Z4 equivariance failed for step_pair_conservative at tick {tick}"


def test_z4_equivariance_em_round() -> None:
    qmul = kp.default_qmul_table()
    qn = int(qmul.shape[0])
    rounds = kp.build_pair_rounds(8, 6, 6, stencil_id="axial6", boundary_mode="fixed_vacuum")
    world = _rng_world(8 * 6 * 6, s_size=12 * qn, seed=99)
    for tick in range(8):
        lhs = kp.step_em_photon_round(
            kp.z4_phase_shift_T(world, qn=qn, k_shift=1), rounds, qn=qn, tick=tick
        )
        rhs = kp.z4_phase_shift_T(
            kp.step_em_photon_round(world, rounds, qn=qn, tick=tick), qn=qn, k_shift=1
        )
        assert np.array_equal(lhs, rhs), f"Z4 equivariance failed for step_em_photon_round at tick {tick}"


def test_audit_triality_zero_violations() -> None:
    qmul = kp.default_qmul_table()
    qn = int(qmul.shape[0])
    rounds = kp.build_pair_rounds(8, 6, 6, stencil_id="axial6", boundary_mode="fixed_vacuum")
    world = _rng_world(8 * 6 * 6, s_size=12 * qn, seed=5555)
    n_rounds = len(rounds.rounds)
    cur = world.copy()
    for t in range(12):
        ridx = t % n_rounds
        post_t = kp.step_pair_conservative(cur, rounds, qmul=qmul, tick=t)
        ok_t, n_t = kp.audit_per_event_triality(cur, post_t, rounds, qn=qn, ridx=ridx)
        assert ok_t, f"Triality violation in conservative step at tick {t}: {n_t} events"
        post_em = kp.step_em_photon_round(cur, rounds, qn=qn, tick=t)
        ok_em, n_em = kp.audit_per_event_triality(cur, post_em, rounds, qn=qn, ridx=ridx)
        assert ok_em, f"Triality violation in EM step at tick {t}: {n_em} events"
        cur = post_t


def main() -> None:
    test_pair_rounds_are_disjoint_per_round()
    test_gamma_conservation_exact_per_tick()
    test_global_z3_equivariance_one_step()
    test_z4_phase_shift_properties()
    test_z4_sum_conserved_by_em_round()
    test_em_round_leaves_g_and_q_unchanged()
    test_z4_equivariance_step_conservative()
    test_z4_equivariance_em_round()
    test_audit_triality_zero_violations()
    print("ok: test_v3_s2880_pair_conservative_kernel_v1")


if __name__ == "__main__":
    main()
