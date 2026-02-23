"""calc/test_koide_sl23.py
Tests for calc/koide_sl23.py:
  SL(2,3) character table -> Z3 phase spacing -> Brannen parametrization -> Koide Q=2/3.

Verifies the following chain (KOIDE-001, claims/koide_exactness.yml):
  1. Z3 character table orthogonality
  2. Brannen masses have Z3-forced cosine-sum = 0
  3. B = A*sqrt(2) gives Q = 2/3 (numerical check of Lean theorem brannen_b_squared)
  4. SL(2,3) structure: order 24, Q8 normal, Z3 quotient, 3 x 1D reps
  5. Full derivation chain verified end-to-end
"""

import numpy as np
import pytest

from calc.koide_sl23 import (
    OMEGA,
    Z3_GENERATOR_PHASES,
    z3_character_table,
    z3_orthogonality_check,
    sl23_structure,
    brannen_masses,
    koide_ratio,
    z3_cosine_sum_zero,
    verify_b_squared_2,
    verify_full_chain,
)

TOL = 1e-10


# ================================================================
# TestOmega: primitive cube root of unity
# ================================================================

class TestOmega:
    def test_omega_cubed_is_1(self):
        assert np.isclose(OMEGA ** 3, 1.0, atol=TOL)

    def test_omega_is_not_1(self):
        assert not np.isclose(OMEGA.real, 1.0, atol=1e-5)

    def test_omega_squared_is_conjugate(self):
        assert np.isclose(OMEGA ** 2, np.conj(OMEGA), atol=TOL)

    def test_sum_of_three_roots_is_zero(self):
        s = 1.0 + OMEGA + OMEGA ** 2
        assert np.isclose(abs(s), 0.0, atol=TOL)

    def test_omega_real_part(self):
        assert np.isclose(OMEGA.real, -0.5, atol=TOL)

    def test_omega_imag_part(self):
        assert np.isclose(OMEGA.imag, np.sqrt(3) / 2.0, atol=TOL)


# ================================================================
# TestZ3GeneratorPhases: phases in Z3 generator images
# ================================================================

class TestZ3GeneratorPhases:
    def test_three_phases(self):
        assert len(Z3_GENERATOR_PHASES) == 3

    def test_all_cube_roots_of_unity(self):
        for p in Z3_GENERATOR_PHASES:
            assert np.isclose(abs(p) ** 3, 1.0, atol=TOL)

    def test_phases_are_1_omega_omega2(self):
        assert np.isclose(Z3_GENERATOR_PHASES[0], 1.0, atol=TOL)
        assert np.isclose(Z3_GENERATOR_PHASES[1], OMEGA, atol=TOL)
        assert np.isclose(Z3_GENERATOR_PHASES[2], OMEGA ** 2, atol=TOL)

    def test_phases_sum_to_zero(self):
        s = sum(Z3_GENERATOR_PHASES)
        assert np.isclose(abs(s), 0.0, atol=TOL)


# ================================================================
# TestZ3CharacterTable: character table structure
# ================================================================

class TestZ3CharacterTable:
    def test_shape_3x3(self):
        chi = z3_character_table()
        assert chi.shape == (3, 3)

    def test_trivial_rep_all_ones(self):
        chi = z3_character_table()
        assert np.allclose(chi[0], [1.0, 1.0, 1.0], atol=TOL)

    def test_identity_column_all_ones(self):
        """Column 0 (g^0 = identity) has all characters = 1."""
        chi = z3_character_table()
        assert np.allclose(chi[:, 0], [1.0, 1.0, 1.0], atol=TOL)

    def test_omega_rep_second_row(self):
        chi = z3_character_table()
        assert np.isclose(chi[1, 0], 1.0, atol=TOL)
        assert np.isclose(chi[1, 1], OMEGA, atol=TOL)
        assert np.isclose(chi[1, 2], OMEGA ** 2, atol=TOL)

    def test_omega2_rep_third_row(self):
        chi = z3_character_table()
        assert np.isclose(chi[2, 0], 1.0, atol=TOL)
        assert np.isclose(chi[2, 1], OMEGA ** 2, atol=TOL)
        assert np.isclose(abs(chi[2, 2] - OMEGA ** 4), 0.0, atol=TOL)

    def test_orthogonality(self):
        result = z3_orthogonality_check()
        assert result['orthonormal'], "Z3 character table must be orthonormal"

    def test_gram_matrix_diagonal(self):
        result = z3_orthogonality_check()
        gram = result['gram']
        # Off-diagonal entries must be ~0
        for i in range(3):
            for j in range(3):
                if i != j:
                    assert np.isclose(abs(gram[i, j]), 0.0, atol=TOL), \
                        f"Off-diagonal gram[{i},{j}] = {gram[i,j]} != 0"

    def test_gram_matrix_diagonal_equals_3(self):
        result = z3_orthogonality_check()
        gram = result['gram']
        for i in range(3):
            assert np.isclose(gram[i, i].real, 3.0, atol=TOL), \
                f"Diagonal gram[{i},{i}] = {gram[i,i]} != 3"


# ================================================================
# TestSL23Structure: group structure
# ================================================================

class TestSL23Structure:
    def test_order_24(self):
        info = sl23_structure()
        assert info['order'] == 24

    def test_normal_subgroup_q8(self):
        info = sl23_structure()
        assert info['normal_subgroup'] == 'Q8'
        assert info['normal_subgroup_order'] == 8

    def test_quotient_z3(self):
        info = sl23_structure()
        assert info['quotient'] == 'Z3'
        assert info['quotient_order'] == 3

    def test_three_1d_reps(self):
        info = sl23_structure()
        assert info['n_1d_reps'] == 3

    def test_irrep_dim_check_equals_24(self):
        """Sum of squares of irrep dimensions must equal group order."""
        info = sl23_structure()
        assert info['dim_check'] == 24

    def test_irrep_dimensions_correct(self):
        """SL(2,3) has irreps of dimensions 1,1,1,2,2,2,3."""
        info = sl23_structure()
        dims = sorted(info['irrep_dimensions'])
        assert dims == [1, 1, 1, 2, 2, 2, 3]

    def test_1d_rep_phases_cube_roots(self):
        info = sl23_structure()
        for p in info['1d_rep_phases_of_z3_generator']:
            assert np.isclose(abs(p) ** 3, 1.0, atol=TOL)

    def test_1d_rep_phases_sum_zero(self):
        info = sl23_structure()
        s = sum(info['1d_rep_phases_of_z3_generator'])
        assert np.isclose(abs(s), 0.0, atol=TOL)

    def test_references_generation_shift_lean(self):
        info = sl23_structure()
        assert 'generationShift_order3' in info['cog_generation_shift_lean']


# ================================================================
# TestBrannenMasses: Z3-parametrized masses
# ================================================================

class TestBrannenMasses:
    def test_explicit_phi0(self):
        A, B, phi = 2.0, 1.0, 0.0
        masses = brannen_masses(A, B, phi)
        assert np.isclose(masses[0], A + B * np.cos(0), atol=TOL)
        assert np.isclose(masses[1], A + B * np.cos(2 * np.pi / 3), atol=TOL)
        assert np.isclose(masses[2], A + B * np.cos(4 * np.pi / 3), atol=TOL)

    def test_z3_sum_rule_all_phi(self):
        """Core Z3 constraint: sum(f_k) = 3*A for all phi."""
        A, B = 1.5, 1.0
        for phi in np.linspace(0, 2 * np.pi, 50):
            masses = brannen_masses(A, B, phi)
            assert np.isclose(np.sum(masses), 3.0 * A, atol=TOL), \
                f"Sum rule failed at phi={phi:.3f}"

    def test_democratic_limit_b_zero(self):
        """B=0 -> all three masses degenerate at A."""
        masses = brannen_masses(A=3.0, B=0.0, phi=0.5)
        assert np.allclose(masses, 3.0, atol=TOL)

    def test_phase_spacing_2pi_over_3(self):
        """Consecutive mass indices differ by phase 2*pi/3."""
        A, B = 2.0, 1.0
        for phi in [0.0, 0.7, 1.5]:
            m = brannen_masses(A, B, phi)
            m_shift = brannen_masses(A, B, phi + 2 * np.pi / 3)
            # Shifting phi by 2*pi/3 cycles the three f-values: (f0,f1,f2) -> (f2,f0,f1)
            # Proof: f_k(phi+2pi/3) = A + B*cos(phi + 2pi/3 + 2pi*k/3)
            #         = A + B*cos(phi + 2pi*(k+1)/3) = f_{k+1}(phi)
            # So: m_shift[k] = m[k+1 mod 3], i.e. (f0',f1',f2') = (f1,f2,f0)
            assert np.isclose(m_shift[0], m[1], atol=TOL)
            assert np.isclose(m_shift[1], m[2], atol=TOL)
            assert np.isclose(m_shift[2], m[0], atol=TOL)

    def test_shape(self):
        masses = brannen_masses(1.0, 0.5, 0.0)
        assert masses.shape == (3,)


# ================================================================
# TestZ3CosineIdentity: algebraic foundation
# ================================================================

class TestZ3CosineIdentity:
    def test_identity_holds(self):
        result = z3_cosine_sum_zero()
        assert result['identity_holds'], \
            f"Z3 cosine identity failed: max dev = {result['max_deviation']}"

    def test_max_deviation_tiny(self):
        result = z3_cosine_sum_zero()
        assert result['max_deviation'] < 1e-10

    def test_explicit_phi_values(self):
        """Spot-check: cos(phi)+cos(phi+2pi/3)+cos(phi+4pi/3) = 0."""
        k = np.array([0, 1, 2], dtype=float)
        for phi in [0.0, np.pi / 6, np.pi / 4, np.pi / 3, np.pi / 2, 1.0, 2.0]:
            total = np.sum(np.cos(phi + 2 * np.pi * k / 3))
            assert np.isclose(total, 0.0, atol=1e-12), \
                f"Identity failed at phi={phi}: sum = {total}"


# ================================================================
# TestKoideRatio: Q = 2/3 <=> B^2 = 2*A^2
# ================================================================

class TestKoideRatio:
    def test_sqrt2_gives_two_thirds(self):
        """B = A*sqrt(2) -> Q = 2/3 (numerical check of brannen_b_squared).

        Note: exactly one f_k will be negative (electron amplitude).
        The algebraic identity Q = sum(f^2)/(sum(f))^2 = 2/3 holds regardless.
        """
        for A in [0.5, 1.0, 1.5, 2.0, 5.0]:
            B = A * np.sqrt(2.0)
            for phi in [0.01, 0.5, 1.0, 1.5, 2.5]:
                f_vals = brannen_masses(A, B, phi)
                Q = koide_ratio(f_vals)
                if not np.isnan(Q):
                    assert np.isclose(Q, 2.0 / 3.0, atol=1e-10), \
                        f"Q = {Q} != 2/3 for A={A}, phi={phi}"

    def test_q_independent_of_phi(self):
        """Q is phi-independent for fixed A, B (pure algebraic identity)."""
        A, B = 2.0, 2.0 * np.sqrt(2.0)
        Q_vals = []
        for phi in np.linspace(0.01, 2 * np.pi - 0.01, 50):
            f_vals = brannen_masses(A, B, phi)
            Q = koide_ratio(f_vals)
            if not np.isnan(Q):
                Q_vals.append(Q)
        assert len(Q_vals) > 0
        assert np.allclose(Q_vals, Q_vals[0], atol=1e-9), \
            "Q must be independent of phi"

    def test_b_less_sqrt2_gives_q_less_two_thirds(self):
        """B < A*sqrt(2) -> Q < 2/3."""
        A = 2.0
        Q_sqrt2 = koide_ratio(brannen_masses(A, A * np.sqrt(2.0), phi=0.5))
        Q_small = koide_ratio(brannen_masses(A, A * 0.5, phi=0.5))
        assert np.isclose(Q_sqrt2, 2.0 / 3.0, atol=1e-10)
        assert Q_small < 2.0 / 3.0 - 1e-6

    def test_b_greater_sqrt2_gives_q_greater_two_thirds(self):
        """B > A*sqrt(2) -> Q > 2/3."""
        A, phi = 5.0, 0.5
        B_large = A * np.sqrt(2.0) * 1.1
        Q = koide_ratio(brannen_masses(A, B_large, phi))
        assert not np.isnan(Q)
        assert Q > 2.0 / 3.0 - 1e-6

    def test_zero_sum_returns_nan(self):
        """sum(f_k) = 0 -> nan (degenerate case)."""
        # Three f-values summing to zero: e.g. 1, 0, -1
        f_vals = np.array([1.0, 0.0, -1.0])
        assert np.isnan(koide_ratio(f_vals))

    def test_all_equal_gives_one_third(self):
        """All f_k equal -> Q = 1/3 (democratic limit)."""
        f_vals = np.array([2.0, 2.0, 2.0])
        assert np.isclose(koide_ratio(f_vals), 1.0 / 3.0, atol=TOL)


# ================================================================
# TestVerifyBSquared2: numerical validation of Lean theorem
# ================================================================

class TestVerifyBSquared2:
    def test_all_passed(self):
        """B = A*sqrt(2) gives Q = 2/3 for all (A, phi) with sum(f_k) != 0.

        Note: exactly one f_k will be negative for each (A, phi) pair.
        The algebraic identity holds regardless of individual f_k signs.
        """
        result = verify_b_squared_2(n_A=10, n_phi=10)
        assert result['all_passed'], \
            f"{result['n_passed']}/{result['n_tests']} passed, max error={result['max_Q_error']}"

    def test_max_error_tiny(self):
        result = verify_b_squared_2(n_A=10, n_phi=10)
        assert result['max_Q_error'] < 1e-8

    def test_b_over_a_is_sqrt2(self):
        result = verify_b_squared_2()
        assert np.isclose(result['B_over_A'], np.sqrt(2.0), atol=TOL)


# ================================================================
# TestFullChain: end-to-end verification
# ================================================================

class TestFullChain:
    def test_chain_complete_with_sqrt2(self):
        result = verify_full_chain(A=1.5, phi=0.5)
        assert result['chain_complete'], \
            f"Chain incomplete: {result}"

    def test_q_equals_two_thirds(self):
        result = verify_full_chain(A=2.0, phi=1.0)
        assert result['step6_Q_equals_2_3'], \
            f"Q = {result['step6_Q']} != 2/3"

    def test_chain_phi_independence(self):
        """Q = 2/3 for all phi when B = A*sqrt(2).

        No positivity guard: exactly one f_k is negative for each phi.
        The algebraic identity Q = sum(f^2)/(sum(f))^2 = 2/3 holds always.
        """
        for phi in [0.01, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
            result = verify_full_chain(A=1.5, phi=phi)
            assert result['step6_Q_equals_2_3'], \
                f"Q != 2/3 at phi={phi}: Q={result['step6_Q']}"

    def test_sl23_step_ok(self):
        result = verify_full_chain()
        assert result['step1_ok'], "SL(2,3) order check failed"
        assert result['step2_quotient_z3'], "Z3 quotient check failed"
        assert result['step3_three_1d_reps'], "Three 1D reps check failed"
        assert result['step3_phases_cube_roots'], "Phase cube-root check failed"

    def test_z3_steps_ok(self):
        result = verify_full_chain()
        assert result['step4_z3_orthogonal'], "Z3 orthogonality failed"
        assert result['step4_cosine_sum_zero'], "Cosine sum identity failed"



# ================================================================
# TestPositivityBand: the narrow band of phase angles where all f_k > 0
# ================================================================

class TestPositivityBand:
    """Verify the positivity band condition for B = A*sqrt(2).

    Key finding (2026-02-22): B = A*sqrt(2) does NOT universally force a
    negative f_k. The three amplitudes are ALL positive if and only if:

        min_k cos(phi + 2*pi*k/3) > -1/sqrt(2) ~= -0.7071

    This defines a narrow allowed band of phase angles. The physical
    charged-lepton phase phi ~= 2/9 rad gives:

        min cosine ~= -0.6795 > -0.7071   (margin ~= 0.028)

    So the empirical Q = 2/3 for (e, mu, tau) is achieved with ALL POSITIVE
    square-root amplitudes. The formula Q = sum(f^2)/(sum(f))^2 = 2/3 also
    holds algebraically for phi outside this band (where one f_k < 0), but
    the physical lepton masses correspond to the positive-amplitude regime.

    Correction note (2026-02-22): An earlier iteration of this module
    incorrectly claimed that B = A*sqrt(2) universally forces one f_k < 0
    (confusing the charged-lepton formula with a neutrino Koide extension).
    That claim was retracted and replaced with the correct positivity band
    condition documented here.
    """

    def test_physical_phase_all_positive(self):
        """At the physical phase phi = 2/9 rad, all f_k > 0 with B = A*sqrt(2)."""
        phi_phys = 2.0 / 9.0  # ~= 0.2222 rad, empirical charged-lepton phase
        A = 1.0
        B = A * np.sqrt(2.0)
        f = brannen_masses(A, B, phi_phys)
        assert np.all(f > 0), \
            f"Expected all positive f_k at phi=2/9, got {f}"

    def test_positivity_iff_min_cosine_above_threshold(self):
        """All f_k > 0 iff min_k cos(phi + 2*pi*k/3) > -1/sqrt(2)."""
        A = 1.0
        B = A * np.sqrt(2.0)
        threshold = -1.0 / np.sqrt(2.0)
        k = np.array([0, 1, 2])
        for phi in np.linspace(0.0, 2 * np.pi, 120, endpoint=False):
            f = brannen_masses(A, B, phi)
            min_cos = np.min(np.cos(phi + 2 * np.pi * k / 3))
            all_positive = np.all(f > 0)
            should_be_positive = min_cos > threshold
            assert all_positive == should_be_positive, \
                f"Positivity mismatch at phi={phi:.4f}: " \
                f"min_cos={min_cos:.5f}, all_positive={all_positive}"

    def test_physical_phase_minimum_cosine(self):
        """Physical phase phi = 2/9 has min cosine ~= -0.6795, margin ~= 0.028."""
        phi_phys = 2.0 / 9.0
        cosines = np.cos(phi_phys + 2 * np.pi * np.array([0, 1, 2]) / 3)
        min_cos = np.min(cosines)
        assert min_cos > -1.0 / np.sqrt(2.0), \
            f"Physical phase min cosine {min_cos:.5f} must be > -0.7071"
        margin = min_cos - (-1.0 / np.sqrt(2.0))
        assert 0.02 < margin < 0.04, \
            f"Margin should be ~0.028 (tight!), got {margin:.5f}"

    def test_physical_leptons_give_two_thirds_positive_sqrt(self):
        """Empirical: charged lepton masses with ALL POSITIVE sqrt give Q = 2/3.

        The Koide formula works for (m_e, m_mu, m_tau) with unsigned (positive)
        square roots. The physical phase phi ~= 2/9 keeps all amplitudes above
        zero. Q error is ~6e-6 due to the physical masses not being exactly at
        the Koide prediction (experimental uncertainty ~0.5 MeV in m_tau).
        """
        # CODATA 2022 charged lepton masses in MeV
        m_e   = 0.51099895
        m_mu  = 105.6583755
        m_tau = 1776.86
        f = np.sqrt(np.array([m_e, m_mu, m_tau]))   # all positive
        assert np.all(f > 0), "Physical sqrt masses must all be positive"
        Q = koide_ratio(f)
        assert np.isclose(Q, 2.0 / 3.0, atol=1e-3), \
            f"Physical leptons (positive sqrt) give Q={Q:.8f}, expected 2/3"

    def test_q_algebraic_identity_holds_outside_band(self):
        """Q = 2/3 holds algebraically even for phi outside the positivity band.

        For phi outside the allowed band, one f_k < 0, but the ring identity
        Q = sum(f^2)/(sum(f))^2 = 2/3 still holds. The algebraic verification
        in verify_b_squared_2 tests this across all phi, including outside-band.
        """
        A = 1.0
        B = A * np.sqrt(2.0)
        threshold = -1.0 / np.sqrt(2.0)
        k = np.array([0, 1, 2])
        outside_band_tested = 0
        for phi in np.linspace(0.0, 2 * np.pi, 100, endpoint=False):
            min_cos = np.min(np.cos(phi + 2 * np.pi * k / 3))
            if min_cos <= threshold:    # outside the positivity band
                f = brannen_masses(A, B, phi)
                Q = koide_ratio(f)
                if not np.isnan(Q):
                    assert np.isclose(Q, 2.0 / 3.0, atol=1e-10), \
                        f"Algebraic Q = 2/3 failed at phi={phi:.4f}: Q={Q}"
                    outside_band_tested += 1
        assert outside_band_tested > 0, "Should have tested outside-band phi values"
