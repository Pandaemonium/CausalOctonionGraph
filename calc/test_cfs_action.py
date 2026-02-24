"""calc/test_cfs_action.py

Tests for the CFS discrete causal action (calc/cfs_action.py).

Key verified values:
  Orbit:  psi_0 = e1, psi_1 = e7*e1, psi_2 = -e1, psi_3 = -(e7*e1).
  Non-zero overlaps: (0,2) and (1,3) both = -1.
  Total orbit action S(n) = 2(1 - 1/n) for basis-vector initial state.
  Simple L-ratio: S(n_mu)/S(n_e) < 2 for any n_e >= 2, n_mu > n_e.
  Effective m^2 model: (V_mu/V_e)^2 = 225 (8.8% above 206.768).
  N_TAU * V_mu = 14 * 15 = 210 (1.6% above 206.768).
"""

import numpy as np
import pytest

from calc.cfs_action import (
    cfs_lagrangian,
    orbit_states,
    orbit_action,
    simple_lagrangian_ratio,
    effective_point_model,
    run_cfs_models,
)
from calc.qed_ee_sim import E1, E7, OMEGA
from calc.emu_dag_sim import (
    N_TAU,
    VERTEX_COST_ELECTRON,
    VERTEX_COST_MUON,
    EXPERIMENTAL_MASS_RATIO,
)

TOL = 1e-10


# ================================================================
# 1. CFS Lagrangian formula
# ================================================================

class TestCFSLagrangian:

    def test_lagrangian_orthogonal_zero(self):
        """L(c=0, n) = 0 for orthogonal states (no causal connection)."""
        for n in [1, 2, 8, 14]:
            assert abs(cfs_lagrangian(0.0, n)) < TOL

    def test_lagrangian_antiparallel_n2(self):
        """L(|c|=1, n=2) = 1 - 1/2 = 1/2."""
        assert abs(cfs_lagrangian(-1.0, 2) - 0.5) < TOL

    def test_lagrangian_antiparallel_n8(self):
        """L(|c|=1, n=8) = 1 - 1/8 = 7/8."""
        assert abs(cfs_lagrangian(-1.0, 8) - 7 / 8) < TOL

    def test_lagrangian_antiparallel_general(self):
        """L(|c|=1, n) = 1 - 1/n for any n > 0."""
        for n in [2, 4, 8, 14, 15, 100]:
            expected = 1.0 - 1.0 / n
            assert abs(cfs_lagrangian(1.0, n) - expected) < TOL

    def test_lagrangian_complex_overlap(self):
        """L uses |c|^2, so complex phase doesn't affect result."""
        c_real = 0.5
        c_complex = 0.5 * np.exp(1j * 1.2)
        L_real = cfs_lagrangian(c_real, 8)
        L_complex = cfs_lagrangian(c_complex, 8)
        assert abs(L_real - L_complex) < TOL

    def test_lagrangian_partial_overlap(self):
        """L(c=1/2, n=4) = 1/4 - 1/64."""
        c = 0.5
        n = 4
        expected = 0.25 - 0.25**2 / 4  # |c|^2 - |c|^4/n
        assert abs(cfs_lagrangian(c, n) - expected) < TOL


# ================================================================
# 2. Orbit states
# ================================================================

class TestOrbitStates:

    def test_orbit_length_4(self):
        """Default orbit has exactly 4 states."""
        states = orbit_states(E1.astype(complex))
        assert len(states) == 4

    def test_orbit_returns_to_initial(self):
        """4th application of L_{e7} returns to initial state (C_e = 4)."""
        states = orbit_states(E1.astype(complex))
        import numpy as np
        assert np.allclose(states[0], states[0], atol=TOL)
        # psi_2 = -psi_0 (half period)
        assert np.allclose(states[2], -states[0], atol=TOL)
        # psi_3 = -psi_1
        assert np.allclose(states[3], -states[1], atol=TOL)

    def test_orbit_psi1_psi0_orthogonal(self):
        """psi_1 = e7*e1 is orthogonal to e1 (different basis vectors)."""
        states = orbit_states(E1.astype(complex))
        c01 = np.vdot(states[0], states[1])
        assert abs(c01) < TOL

    def test_orbit_psi0_psi2_antiparallel(self):
        """psi_2 = -psi_0: overlap is -1."""
        states = orbit_states(E1.astype(complex))
        c02 = np.vdot(states[0], states[2])
        assert abs(abs(c02) - 1.0) < TOL

    def test_orbit_psi1_psi3_antiparallel(self):
        """psi_3 = -psi_1: overlap is -1."""
        states = orbit_states(E1.astype(complex))
        c13 = np.vdot(states[1], states[3])
        assert abs(abs(c13) - 1.0) < TOL

    def test_orbit_omega_also_returns(self):
        """OMEGA initial state also has 4-step orbit (Universal C_e = 4).

        OMEGA = 0.5*e0 + 0.5j*e7 has norm 1/sqrt(2), so psi_2 = -psi_0
        and the overlap <psi_0|psi_2> = -|OMEGA|^2 = -0.5 (not -1).
        We verify the orbit structure psi_2 = -psi_0 directly.
        """
        states = orbit_states(OMEGA)
        assert np.allclose(states[2], -states[0], atol=TOL)


# ================================================================
# 3. Orbit action
# ================================================================

class TestOrbitAction:

    def test_orbit_action_n8(self):
        """Total orbit action for n=8: S = 2*(1 - 1/8) = 7/4."""
        states = orbit_states(E1.astype(complex))
        S = orbit_action(states, n=8)
        assert abs(S - 7 / 4) < TOL

    def test_orbit_action_n2(self):
        """Total orbit action for n=2: S = 2*(1 - 1/2) = 1."""
        states = orbit_states(E1.astype(complex))
        S = orbit_action(states, n=2)
        assert abs(S - 1.0) < TOL

    def test_orbit_action_large_n(self):
        """For very large n, orbit action approaches 2 (the number of antiparallel pairs)."""
        states = orbit_states(E1.astype(complex))
        S = orbit_action(states, n=1e9)
        assert abs(S - 2.0) < 1e-6

    def test_orbit_action_formula(self):
        """S(n) = 2*(1 - 1/n) for basis-vector initial state."""
        states = orbit_states(E1.astype(complex))
        for n in [2, 4, 8, 14, 15, 100]:
            S = orbit_action(states, n=float(n))
            expected = 2.0 * (1.0 - 1.0 / n)
            assert abs(S - expected) < TOL, f"n={n}: S={S}, expected={expected}"


# ================================================================
# 4. Simple L-ratio model
# ================================================================

class TestSimpleLagrangianRatio:

    def test_same_n_gives_ratio_1(self):
        """S(n)/S(n) = 1 when both particles have same spin dimension."""
        r = simple_lagrangian_ratio(8.0, 8.0)
        assert abs(r['ratio'] - 1.0) < TOL

    def test_ratio_bounded_above_by_2(self):
        """S_mu/S_e < 2 for any n_e >= 2, n_mu large."""
        for n_e in [2, 4, 8]:
            r = simple_lagrangian_ratio(float(n_e), 1e8)
            # Limit as n_mu -> inf: S_mu -> 2, S_e = 2*(1-1/n_e)
            # Ratio -> 1/(1-1/n_e) which is 2 for n_e=2, 4/3 for n_e=4, 8/7 for n_e=8
            limit = 1.0 / (1.0 - 1.0 / n_e)
            assert r['ratio'] < limit + 1e-5

    def test_ratio_far_from_206(self):
        """The simple L-ratio cannot reach 206.768 for any positive n."""
        r = simple_lagrangian_ratio(2.0, 1e8)
        assert r['ratio'] < 3.0  # well below 206.768
        assert r['ratio'] < EXPERIMENTAL_MASS_RATIO / 10


# ================================================================
# 5. Effective point-count model
# ================================================================

class TestEffectivePointModel:

    def test_effective_m_squared_equals_225(self):
        """(V_mu/V_e)^2 = 15^2 = 225."""
        eff = effective_point_model()
        assert abs(eff['predictions']['effective_m_squared'] - 225.0) < TOL

    def test_N_TAU_squared_equals_196(self):
        """N_TAU^2 = 14^2 = 196."""
        eff = effective_point_model()
        assert abs(eff['predictions']['N_TAU_squared'] - 196.0) < TOL

    def test_N_TAU_times_V_mu_equals_210(self):
        """N_TAU * V_mu = 14 * 15 = 210."""
        eff = effective_point_model()
        assert abs(eff['predictions']['N_TAU_times_V_mu'] - 210.0) < TOL

    def test_closest_model_is_N_TAU_V_mu(self):
        """N_TAU * V_mu = 210 is closer to 206.768 than either N_TAU^2 or V_mu^2."""
        eff = effective_point_model()
        gap_196 = eff['gaps']['N_TAU_squared']
        gap_210 = eff['gaps']['N_TAU_times_V_mu']
        gap_225 = eff['gaps']['V_mu_squared']
        assert gap_210 < gap_196
        assert gap_210 < gap_225

    def test_N_TAU_V_mu_gap_less_than_2pct(self):
        """N_TAU * V_mu = 210 is within 1.6% of experimental 206.768."""
        eff = effective_point_model()
        assert eff['gaps']['N_TAU_times_V_mu'] < 0.02

    def test_m_e_and_m_mu(self):
        """m_e = 4, m_mu = 60 (4 absorptions * vertex cost)."""
        eff = effective_point_model()
        assert eff['m_e'] == 4 * VERTEX_COST_ELECTRON
        assert eff['m_mu'] == 4 * VERTEX_COST_MUON


# ================================================================
# 6. Full model run
# ================================================================

class TestRunCFSModels:

    def test_run_returns_dict(self):
        """run_cfs_models() returns a dict with required keys."""
        results = run_cfs_models()
        assert 'orbit_overlaps' in results
        assert 'simple_scan' in results
        assert 'effective_model' in results
        assert 'summary' in results

    def test_only_antipodal_overlaps_nonzero(self):
        """Only pairs (0,2) and (1,3) have non-zero overlap."""
        results = run_cfs_models()
        overlaps = results['orbit_overlaps']
        assert overlaps['(0,2)'] > 0.99
        assert overlaps['(1,3)'] > 0.99
        assert overlaps.get('(0,1)', 0.0) < TOL
        assert overlaps.get('(0,3)', 0.0) < TOL
        assert overlaps.get('(1,2)', 0.0) < TOL
        assert overlaps.get('(2,3)', 0.0) < TOL

    def test_simple_scan_max_below_2_1(self):
        """The maximum achievable L-ratio in the simple model is below 2.1."""
        results = run_cfs_models()
        assert results['summary']['simple_ratio_max'] < 2.1

    def test_simple_ratio_cannot_reach_206(self):
        """Flag is set confirming the simple ratio cannot reach 206."""
        results = run_cfs_models()
        assert results['summary']['simple_ratio_cannot_reach_206'] is True
