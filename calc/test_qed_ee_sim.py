"""calc/test_qed_ee_sim.py
Tests for Goal C Phase 1: Electron-Electron Dynamic Graph Simulation.

Run with: pytest calc/test_qed_ee_sim.py -v

All tests use the locked Furey Fano convention from calc/conftest.py.
Expected results are derived from RFC-013 and the Goal A calibration (C_e = 4).
"""

import numpy as np
import pytest

from calc.qed_ee_sim import (
    oct_mul_basis,
    oct_mul_full,
    state_is_vacuum_orbit,
    state_is_matter,
    simulate_ee,
    verify_left_mult_orbit,
    verify_vacuum_relay,
    run_calibration_check,
    E0, E1, E7, OMEGA, VACUUM_ORBIT, PHOTON_IDX, SPAWN,
)


# ================================================================
# Fixtures
# ================================================================

@pytest.fixture
def E6():
    v = np.zeros(8, dtype=complex)
    v[6] = 1.0
    return v


# ================================================================
# TestOctMulBasis
# ================================================================

class TestOctMulBasis:
    """Unit tests for oct_mul_basis: e_i * e_j = sign * e_k."""

    def test_identity_left(self):
        """e0 * e_k = e_k for all k."""
        for k in range(8):
            idx, sgn = oct_mul_basis(0, k)
            assert idx == k and sgn == 1

    def test_identity_right(self):
        """e_k * e0 = e_k for all k."""
        for k in range(8):
            idx, sgn = oct_mul_basis(k, 0)
            assert idx == k and sgn == 1

    def test_square_to_minus_one(self):
        """e_k * e_k = -e0 for all imaginary units k=1..7."""
        for k in range(1, 8):
            idx, sgn = oct_mul_basis(k, k)
            assert idx == 0 and sgn == -1

    def test_e7_times_e1_left_mult(self):
        """e7 * e1 = -e6 (left-mult, RFC-013 section 4.2 step 1)."""
        idx, sgn = oct_mul_basis(7, 1)
        assert idx == 6 and sgn == -1

    def test_e7_times_e6_left_mult(self):
        """e7 * e6 = +e1 (RFC-013 section 4.2 step 4: e7*(+e6) = +e1)."""
        idx, sgn = oct_mul_basis(7, 6)
        assert idx == 1 and sgn == +1

    def test_e1_times_e7_right_mult(self):
        """e1 * e7 = +e6 (Fano cycle (e1,e7,e6) cyclic, right-mult)."""
        idx, sgn = oct_mul_basis(1, 7)
        assert idx == 6 and sgn == +1

    def test_antisymmetry_of_imaginary_product(self):
        """e_i * e_j = -(e_j * e_i) for all distinct imaginary units i,j."""
        for i in range(1, 8):
            for j in range(1, 8):
                if i == j:
                    continue
                ki, si = oct_mul_basis(i, j)
                kj, sj = oct_mul_basis(j, i)
                assert ki == kj, f"i={i},j={j}: result indices differ"
                assert si == -sj, f"i={i},j={j}: signs not opposite"


# ================================================================
# TestOctMulFull
# ================================================================

class TestOctMulFull:
    """Tests for oct_mul_full: left-multiplication in C(x)O."""

    def test_e7_left_mult_e1_gives_minus_e6(self, E6):
        """e7 * e1 = -e6 (state-array level)."""
        result = oct_mul_full(E7, E1)
        assert np.allclose(result, -E6, atol=1e-10)

    def test_e7_left_mult_minus_e6_gives_minus_e1(self, E6):
        """e7 * (-e6) = -e1 (RFC-013 section 4.2 step 2)."""
        result = oct_mul_full(E7, -E6)
        assert np.allclose(result, -E1, atol=1e-10)

    def test_e7_left_mult_minus_e1_gives_plus_e6(self, E6):
        """e7 * (-e1) = +e6 (RFC-013 section 4.2 step 3)."""
        result = oct_mul_full(E7, -E1)
        assert np.allclose(result, E6, atol=1e-10)

    def test_e7_left_mult_plus_e6_gives_plus_e1(self, E6):
        """e7 * (+e6) = +e1 (RFC-013 section 4.2 step 4, orbit return)."""
        result = oct_mul_full(E7, E6)
        assert np.allclose(result, E1, atol=1e-10)

    def test_vacuum_relay_identity(self):
        """e7 * omega = -i * omega (RFC-013 section 5.1)."""
        result = oct_mul_full(E7, OMEGA)
        assert np.allclose(result, -1j * OMEGA, atol=1e-10)

    def test_vacuum_orbit_period_4(self):
        """Applying e7 four times to omega gives omega back."""
        state = OMEGA.copy()
        for _ in range(4):
            state = oct_mul_full(E7, state)
        assert np.allclose(state, OMEGA, atol=1e-10)

    def test_e1_orbit_period_4(self):
        """Applying e7 four times to e1 gives e1 back."""
        state = E1.copy()
        for _ in range(4):
            state = oct_mul_full(E7, state)
        assert np.allclose(state, E1, atol=1e-10)

    def test_identity_element_left(self):
        """e0 * e_k = e_k for all k (full-state level)."""
        for k in range(8):
            ek = np.zeros(8, dtype=complex)
            ek[k] = 1.0
            result = oct_mul_full(E0, ek)
            assert np.allclose(result, ek, atol=1e-10)

    def test_linearity_in_second_argument(self):
        """oct_mul_full(a, b+c) = oct_mul_full(a,b) + oct_mul_full(a,c)."""
        a = np.array([1, 0.5j, 0, 0, 0, 0, 0, 0], dtype=complex)
        b = E1.copy()
        c = E7.copy()
        lhs = oct_mul_full(a, b + c)
        rhs = oct_mul_full(a, b) + oct_mul_full(a, c)
        assert np.allclose(lhs, rhs, atol=1e-10)

    def test_vacuum_relay_numerical_value(self):
        """e7 * omega = [-0.5j, 0, 0, 0, 0, 0, 0, 0.5] (component check)."""
        result = oct_mul_full(E7, OMEGA)
        assert np.isclose(result[0], -0.5j, atol=1e-10), f"index 0: {result[0]}"
        assert np.isclose(result[7], 0.5 + 0j, atol=1e-10), f"index 7: {result[7]}"
        assert np.allclose(result[1:7], 0, atol=1e-10), f"middle: {result[1:7]}"


# ================================================================
# TestAxiomOfIdentity
# ================================================================

class TestAxiomOfIdentity:
    """Tests for state_is_vacuum_orbit (RFC-013 section 2.3)."""

    def test_omega_is_vacuum(self):
        assert state_is_vacuum_orbit(OMEGA)

    def test_minus_i_omega_is_vacuum(self):
        assert state_is_vacuum_orbit(-1j * OMEGA)

    def test_minus_omega_is_vacuum(self):
        assert state_is_vacuum_orbit(-1.0 * OMEGA)

    def test_plus_i_omega_is_vacuum(self):
        assert state_is_vacuum_orbit(+1j * OMEGA)

    def test_e1_is_not_vacuum(self):
        assert not state_is_vacuum_orbit(E1)

    def test_e7_is_not_vacuum(self):
        assert not state_is_vacuum_orbit(E7)

    def test_zero_is_not_vacuum(self):
        assert not state_is_vacuum_orbit(np.zeros(8, dtype=complex))

    def test_all_four_orbit_elements_detected(self):
        for v in VACUUM_ORBIT:
            assert state_is_vacuum_orbit(v), f"Orbit element {v} not detected"

    def test_matter_states_are_not_vacuum(self):
        """e1..e6 are matter states (not vacuum)."""
        for k in range(1, 7):
            ek = np.zeros(8, dtype=complex)
            ek[k] = 1.0
            assert state_is_matter(ek), f"e{k} incorrectly classified as vacuum"

    def test_vacuum_orbit_closed_under_e7(self):
        """Applying e7 to any vacuum orbit element gives another vacuum orbit element."""
        for v in VACUUM_ORBIT:
            next_v = oct_mul_full(E7, v)
            assert state_is_vacuum_orbit(next_v), \
                f"e7 * {v} = {next_v} not in vacuum orbit"

    def test_state_is_matter_is_complement(self):
        """state_is_matter is the logical complement of state_is_vacuum_orbit."""
        test_states = [OMEGA, -1j * OMEGA, E1, E7, np.zeros(8, dtype=complex)]
        for s in test_states:
            assert state_is_vacuum_orbit(s) != state_is_matter(s)


# ================================================================
# TestVerifyLeftMultOrbit
# ================================================================

class TestVerifyLeftMultOrbit:
    """Tests for verify_left_mult_orbit helper."""

    def test_period_is_4(self):
        result = verify_left_mult_orbit()
        assert result['period'] == 4

    def test_passed_flag_is_true(self):
        result = verify_left_mult_orbit()
        assert result['passed'] is True

    def test_trajectory_length_equals_period(self):
        result = verify_left_mult_orbit()
        assert len(result['trajectory']) == result['period']

    def test_orbit_steps_match_rfc013_table(self, E6):
        """RFC-013 section 4.2: +e1 -> -e6 -> -e1 -> +e6."""
        result = verify_left_mult_orbit()
        traj = result['trajectory']
        assert np.allclose(traj[0],  E1, atol=1e-10), "step 0: expected +e1"
        assert np.allclose(traj[1], -E6, atol=1e-10), "step 1: expected -e6"
        assert np.allclose(traj[2], -E1, atol=1e-10), "step 2: expected -e1"
        assert np.allclose(traj[3],  E6, atol=1e-10), "step 3: expected +e6"


# ================================================================
# TestVacuumRelay
# ================================================================

class TestVacuumRelay:
    """Tests for verify_vacuum_relay helper (RFC-013 section 5.1)."""

    def test_e7_times_omega_equals_minus_i_omega(self):
        result = verify_vacuum_relay()
        assert result['passed']

    def test_vacuum_orbit_sequence(self):
        """Full orbit sequence: omega -> -i*omega -> -omega -> +i*omega -> omega."""
        states = [OMEGA.copy()]
        s = OMEGA.copy()
        for _ in range(4):
            s = oct_mul_full(E7, s)
            states.append(s.copy())
        expected_phases = [1.0 + 0j, -1j, -1.0 + 0j, +1j, 1.0 + 0j]
        for i, (phase, state) in enumerate(zip(expected_phases, states)):
            assert np.allclose(state, phase * OMEGA, atol=1e-10), \
                f"orbit step {i}: expected {phase}*omega"


# ================================================================
# TestSimulateEE
# ================================================================

class TestSimulateEE:
    """Tests for simulate_ee: the main EE scattering simulation."""

    # --- C_e = 4 for multiple D values ---

    def test_Ce_exact_is_4_for_D0(self):
        assert simulate_ee(D=0)['Ce_exact'] == 4

    def test_Ce_exact_is_4_for_D1(self):
        assert simulate_ee(D=1)['Ce_exact'] == 4

    def test_Ce_exact_is_4_for_D2(self):
        assert simulate_ee(D=2)['Ce_exact'] == 4

    def test_Ce_exact_is_4_for_D4(self):
        assert simulate_ee(D=4)['Ce_exact'] == 4

    # --- tick counts ---

    def test_tick_per_cycle_equals_D_plus_1(self):
        for D in [0, 1, 2, 3, 4]:
            sim = simulate_ee(D)
            assert sim['tick_per_cycle'] == D + 1, f"D={D}"

    def test_total_ticks_D0(self):
        assert simulate_ee(D=0)['total_ticks'] == 4   # 4 * (0+1)

    def test_total_ticks_D1(self):
        assert simulate_ee(D=1)['total_ticks'] == 8   # 4 * (1+1)

    def test_total_ticks_D2(self):
        assert simulate_ee(D=2)['total_ticks'] == 12  # 4 * (2+1)

    def test_total_ticks_formula(self):
        """total_ticks = Ce_exact * (D+1) for all tested D."""
        for D in [0, 1, 2, 3, 4]:
            sim = simulate_ee(D)
            assert sim['total_ticks'] == sim['Ce_exact'] * (D + 1), f"D={D}"

    # --- absorption history ---

    def test_absorption_history_length_is_Ce_exact(self):
        """Exactly Ce_exact absorption events are recorded."""
        for D in [0, 1, 2]:
            sim = simulate_ee(D)
            assert len(sim['absorption_history']) == sim['Ce_exact']

    def test_absorption_cycles_are_sequential(self):
        """Cycles are numbered 1, 2, 3, 4 in order."""
        sim = simulate_ee(D=0)
        cycles = [e.cycle for e in sim['absorption_history']]
        assert cycles == [1, 2, 3, 4]

    def test_absorption_ticks_are_multiples_of_tick_per_cycle(self):
        """Each absorption tick = cycle_number * (D+1)."""
        for D in [0, 1, 2]:
            sim = simulate_ee(D)
            for event in sim['absorption_history']:
                expected_tick = event.cycle * (D + 1)
                assert event.tick == expected_tick, \
                    f"D={D}, cycle {event.cycle}: tick={event.tick} != {expected_tick}"

    # --- state trajectory ---

    def test_electron_state_trajectory_D0(self, E6):
        """D=0: electron states follow +e1 -> -e6 -> -e1 -> +e6 -> +e1."""
        sim = simulate_ee(D=0)
        hist = sim['absorption_history']
        assert len(hist) == 4
        assert np.allclose(hist[0].e1_state, -E6, atol=1e-10), "cycle 1: -e6"
        assert np.allclose(hist[1].e1_state, -E1, atol=1e-10), "cycle 2: -e1"
        assert np.allclose(hist[2].e1_state,  E6, atol=1e-10), "cycle 3: +e6"
        assert np.allclose(hist[3].e1_state,  E1, atol=1e-10), "cycle 4: +e1"

    def test_e1_and_e2_states_synchronized(self):
        """Both electrons have identical states at each joint absorption."""
        for D in [0, 1, 2]:
            sim = simulate_ee(D)
            for event in sim['absorption_history']:
                assert np.allclose(event.e1_state, event.e2_state, atol=1e-10), \
                    f"D={D}, cycle {event.cycle}: e1/e2 out of sync"

    def test_at_initial_flag_only_at_cycle_4(self):
        """e1_at_initial is False for cycles 1-3 and True at cycle 4."""
        sim = simulate_ee(D=0)
        flags = [e.e1_at_initial for e in sim['absorption_history']]
        assert flags == [False, False, False, True]

    # --- final state ---

    def test_final_chain_states_e1_at_initial(self):
        """Both electrons are at their initial state in the final chain."""
        for D in [0, 1, 2]:
            sim = simulate_ee(D)
            assert np.allclose(sim['chain_states_final'][0], E1, atol=1e-10), \
                f"D={D}: E1 final state not at E1"
            assert np.allclose(sim['chain_states_final'][D + 1], E1, atol=1e-10), \
                f"D={D}: E2 final state not at E1"

    def test_final_vacuum_nodes_at_omega(self):
        """All vacuum nodes return to OMEGA at the end of the simulation."""
        for D in [1, 2, 3]:
            sim = simulate_ee(D)
            for k in range(1, D + 1):
                assert np.allclose(
                    sim['chain_states_final'][k], OMEGA, atol=1e-10
                ), f"D={D}, vacuum node {k}: final state {sim['chain_states_final'][k]}"

    # --- D-independence ---

    def test_Ce_exact_d_independence(self):
        """Ce_exact = 4 for all tested D values (vacuum count does not affect period)."""
        Ce_values = [simulate_ee(D)['Ce_exact'] for D in [0, 1, 2, 3, 4, 8]]
        assert all(c == 4 for c in Ce_values), f"Ce_values: {Ce_values}"

    # --- vacuum phase accumulation ---

    def test_vacuum_phase_after_one_cycle_D1(self):
        """D=1: after cycle 1, the single vacuum node is at -omega (2 photon hits)."""
        sim = simulate_ee(D=1)
        hist = sim['absorption_history']
        # After cycle 1: V[0] has been hit by both photons -> e7^2 * omega = -omega
        assert np.allclose(hist[0].vacuum_states[0], -OMEGA, atol=1e-10), \
            f"V[0] after cycle 1: expected -omega, got {hist[0].vacuum_states[0]}"

    def test_vacuum_returns_to_omega_at_cycle_2_D1(self):
        """D=1: vacuum node returns to OMEGA at cycle 2 (4 hits total)."""
        sim = simulate_ee(D=1)
        hist = sim['absorption_history']
        assert hist[1].vacuum_at_initial is True, \
            "Vacuum should return to OMEGA at cycle 2 for D=1"

    def test_vacuum_period_tick_is_set(self):
        """vacuum_period_tick is recorded when vacuum first returns to OMEGA."""
        for D in [0, 1, 2]:
            sim = simulate_ee(D)
            assert sim['vacuum_period_tick'] is not None, \
                f"D={D}: vacuum_period_tick not set"

    def test_vacuum_period_tick_D1_is_4(self):
        """D=1: vacuum returns at tick 4 = 2*(D+1) = 2*2 (cycle 2)."""
        sim = simulate_ee(D=1)
        assert sim['vacuum_period_tick'] == 4

    def test_vacuum_period_tick_D2_is_6(self):
        """D=2: vacuum returns at tick 6 = 2*(D+1) = 2*3 (cycle 2)."""
        sim = simulate_ee(D=2)
        assert sim['vacuum_period_tick'] == 6

    def test_vacuum_at_initial_false_at_cycle_1_for_D1(self):
        """D=1: vacuum is NOT at initial state after cycle 1 (it is at -omega)."""
        sim = simulate_ee(D=1)
        assert sim['absorption_history'][0].vacuum_at_initial is False


# ================================================================
# TestRunCalibrationCheck
# ================================================================

class TestRunCalibrationCheck:
    """Integration tests via run_calibration_check."""

    def test_all_checks_pass(self):
        result = run_calibration_check()
        failed = [k for k, v in result['checks'].items() if not v['passed']]
        assert result['all_passed'], f"Failed checks: {failed}"

    def test_individual_check_names_present(self):
        result = run_calibration_check()
        expected_keys = {
            'left_mult_orbit_period',
            'vacuum_relay',
            'ee_sim_D0',
            'ee_sim_D1',
            'ee_sim_D2',
            'd_independence',
        }
        assert expected_keys.issubset(set(result['checks'].keys()))

    def test_d_independence_reports_correct_Ce(self):
        result = run_calibration_check()
        di = result['checks']['d_independence']
        assert di['passed']
        assert all(c == 4 for c in di['Ce_exact_values'])
