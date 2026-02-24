"""
Claim-level tests for VAC-001 (sterile vacuum stability).
"""

import numpy as np

from calc.qed_ee_sim import E7, OMEGA, oct_mul_full, simulate_ee, state_is_vacuum_orbit


def test_vacuum_orbit_is_closed_under_e7() -> None:
    state = OMEGA.copy()
    for _ in range(12):
        assert state_is_vacuum_orbit(state)
        state = oct_mul_full(E7, state)


def test_vacuum_orbit_period_is_4() -> None:
    state = OMEGA.copy()
    for _ in range(4):
        state = oct_mul_full(E7, state)
    assert np.allclose(state, OMEGA, atol=1e-10)


def test_vacuum_nodes_remain_in_vacuum_orbit_in_ee_sim() -> None:
    D = 3
    sim = simulate_ee(D=D)
    for pos in range(1, D + 1):
        assert state_is_vacuum_orbit(sim["chain_states_final"][pos])
