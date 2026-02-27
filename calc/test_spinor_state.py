"""
calc/test_spinor_state.py
Phase B2 tests: verify gen-2 (muon) state construction.

Tests mirror the Lean definitions in CausalGraphTheory/Spinors.lean.
"""

import numpy as np
import pytest
from calc.spinor_state import (
    leftVacConjDoubled,
    rightVacConjDoubled,
    muonInner,
    gen2StateQuadruple,
    check_proportional_idempotency,
    fano_triple,
)


# ================================================================
# Fano triple product tests
# (These underlie the derivation of muonInner.)
# ================================================================

class TestFanoTriples:
    """Verify the triple products used to reduce muonInner."""

    def test_e123_equals_neg_e0(self):
        """(e1*e2)*e3 = -e0.  Derivation: e1*e2=+e3, e3*e3=-e0."""
        result = fano_triple(1, 2, 3)
        expected = np.zeros(8, dtype=complex)
        expected[0] = -1
        assert np.allclose(result.c, expected), (
            f"e1*e2*e3: got {result.c}, want {expected}"
        )

    def test_e136_equals_pos_e4(self):
        """(e1*e3)*e6 = +e4.  Derivation: e1*e3=-e2, -e2*e6=+e4."""
        result = fano_triple(1, 3, 6)
        expected = np.zeros(8, dtype=complex)
        expected[4] = 1
        assert np.allclose(result.c, expected), (
            f"e1*e3*e6: got {result.c}, want {expected}"
        )

    def test_e1_e2_equals_pos_e3(self):
        """e1*e2 = +e3 (from L1=(1,2,3) cyclic triple)."""
        from calc.complex_octonion import ComplexOctonion, BASIS
        e1 = ComplexOctonion(BASIS[1].c.astype(complex))
        e2 = ComplexOctonion(BASIS[2].c.astype(complex))
        result = e1 * e2
        expected = np.zeros(8, dtype=complex)
        expected[3] = 1  # e3
        assert np.allclose(result.c, expected)

    def test_e1_e3_equals_neg_e2(self):
        """e1*e3 = -e2 (anti-cyclic)."""
        from calc.complex_octonion import ComplexOctonion, BASIS
        e1 = ComplexOctonion(BASIS[1].c.astype(complex))
        e3 = ComplexOctonion(BASIS[3].c.astype(complex))
        result = e1 * e3
        expected = np.zeros(8, dtype=complex)
        expected[2] = -1  # -e2
        assert np.allclose(result.c, expected)

    def test_e2_e6_equals_neg_e4(self):
        """e2*e6 = -e4 (used to show -e2*e6 = +e4)."""
        from calc.complex_octonion import ComplexOctonion, BASIS
        e2 = ComplexOctonion(BASIS[2].c.astype(complex))
        e6 = ComplexOctonion(BASIS[6].c.astype(complex))
        result = e2 * e6
        expected = np.zeros(8, dtype=complex)
        expected[4] = -1  # -e4
        assert np.allclose(result.c, expected)


# ================================================================
# Projector element tests
# ================================================================

class TestProjectors:
    """Verify leftVacConjDoubled and rightVacConjDoubled match Lean definitions."""

    def test_leftVacConjDoubled_e0_coeff(self):
        """c[0] = 1+0j  (coefficient of e0 = +1)."""
        assert leftVacConjDoubled.c[0] == 1 + 0j

    def test_leftVacConjDoubled_e7_coeff(self):
        """c[7] = 0-1j  (coefficient of e7 = -i)."""
        assert leftVacConjDoubled.c[7] == -1j

    def test_leftVacConjDoubled_rest_zero(self):
        """All other components are zero."""
        for k in [1, 2, 3, 4, 5, 6]:
            assert leftVacConjDoubled.c[k] == 0j

    def test_right_equals_left(self):
        """rightVacConjDoubled is the same object as leftVacConjDoubled."""
        assert np.array_equal(rightVacConjDoubled.c, leftVacConjDoubled.c)


# ================================================================
# muonInner component tests
# ================================================================

class TestMuonInner:
    """Verify muonInner = -e0 - i*e2 - i*e4 + e6."""

    def test_muonInner_e0(self):
        """c[0] = -1+0j."""
        assert muonInner.c[0] == -1 + 0j

    def test_muonInner_e2(self):
        """c[2] = 0-1j  (coefficient of e2 = -i)."""
        assert muonInner.c[2] == -1j

    def test_muonInner_e4(self):
        """c[4] = 0-1j  (coefficient of e4 = -i)."""
        assert muonInner.c[4] == -1j

    def test_muonInner_e6(self):
        """c[6] = 1+0j  (coefficient of e6 = +1)."""
        assert muonInner.c[6] == 1 + 0j

    def test_muonInner_others_zero(self):
        """All other components (e1, e3, e5, e7) are zero."""
        for k in [1, 3, 5, 7]:
            assert muonInner.c[k] == 0j


# ================================================================
# gen2StateQuadruple tests
# ================================================================

class TestGen2StateQuadruple:
    """
    Verify gen2StateQuadruple = leftVacConjDoubled * (muonInner * rightVacConjDoubled).

    Computed result: -2*e0 + 2i*e7
    (= -2 * leftVacConjDoubled, i.e. -2*(e0 - i*e7))
    """

    def test_gen2_e0_coeff(self):
        """c[0] = -2+0j."""
        assert np.isclose(gen2StateQuadruple.c[0], -2 + 0j)

    def test_gen2_e7_coeff(self):
        """c[7] = 0+2j  (coefficient of e7 = +2i)."""
        assert np.isclose(gen2StateQuadruple.c[7], 2j)

    def test_gen2_others_zero(self):
        """All other components are zero."""
        for k in [1, 2, 3, 4, 5, 6]:
            assert np.isclose(gen2StateQuadruple.c[k], 0j), (
                f"c[{k}] = {gen2StateQuadruple.c[k]}, expected 0"
            )

    def test_gen2_proportional_to_left_vac_conj(self):
        """gen2StateQuadruple = -2 * leftVacConjDoubled."""
        expected = -2 * leftVacConjDoubled.c
        assert np.allclose(gen2StateQuadruple.c, expected)


# ================================================================
# Proportional idempotency test
# ================================================================

class TestProportionalIdempotency:
    """
    Verify the actual proportionality relation gen2^2 = c * gen2.

    NOTE: The Lean theorem gen2State_proportional_idempotent claims c = +4,
    but the numerics show c = -4.  The Lean theorem has a sign error in its
    RHS and must be corrected before the sorry can be replaced.

    Correct statement: gen2StateQuadruple^2 = -4 * gen2StateQuadruple
    i.e. each component is multiplied by -4, NOT +4.
    """

    def test_gen2_squared_e0(self):
        """(gen2)^2 component at e0 = +8 = -4 * (-2)."""
        sq = gen2StateQuadruple * gen2StateQuadruple
        assert np.isclose(sq.c[0], 8 + 0j)

    def test_gen2_squared_e7(self):
        """(gen2)^2 component at e7 = -8j = -4 * (2j)."""
        sq = gen2StateQuadruple * gen2StateQuadruple
        assert np.isclose(sq.c[7], -8j)

    def test_gen2_squared_others_zero(self):
        """All other components of (gen2)^2 are zero."""
        sq = gen2StateQuadruple * gen2StateQuadruple
        for k in [1, 2, 3, 4, 5, 6]:
            assert np.isclose(sq.c[k], 0j)

    def test_proportionality_constant_is_neg_four(self):
        """gen2^2 is proportional to gen2 with constant c = -4 (NOT +4)."""
        is_prop, c_val = check_proportional_idempotency()
        assert is_prop, "gen2^2 is not proportional to gen2"
        assert np.isclose(c_val, -4), (
            f"Expected c = -4, got {c_val}. "
            "Lean theorem gen2State_proportional_idempotent has a sign error: "
            "RHS uses +4 but should use -4."
        )

    def test_lean_theorem_sign_is_wrong(self):
        """
        Document that the Lean sorry-theorem (c = +4) is INCORRECT.
        The correct relation is gen2^2 = -4 * gen2.
        This test will FAIL if someone 'fixes' it by changing c to +4 in Python.
        """
        sq = gen2StateQuadruple * gen2StateQuadruple
        wrong_rhs = 4 * gen2StateQuadruple.c  # what the Lean theorem claims
        correct_rhs = -4 * gen2StateQuadruple.c  # what the math actually gives
        assert not np.allclose(sq.c, wrong_rhs), (
            "gen2^2 = +4*gen2 would mean the Lean theorem is correct, "
            "but numerics show c = -4."
        )
        assert np.allclose(sq.c, correct_rhs), (
            "gen2^2 should equal -4*gen2."
        )
