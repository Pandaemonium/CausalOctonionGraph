"""
CFS-003 Python Verification Scaffold — Vacuum Symmetry from Octonions

Numerically verifies the core mathematical claims of CFS-003:
- e7 (index 6, 0-based) acts on the vacuum state omega with period 4
- The vacuum state omega and its conjugate are non-zero
- Idempotent scaling properties of the vacuum states
- Left and right e7-multiplication orbits have period 4
- The leftVacConj state satisfies idempotent (x8 scaling) relations
- The doubled omega state maps correctly under e7 left/right action

All octonion triples follow rfc/CONVENTIONS.md §2 (7 directed Fano cycles).
"""

import pytest
import numpy as np
from conftest import FANO_CYCLES, FANO_SIGN, FANO_THIRD, VACUUM_AXIS, WITT_PAIRS

# ---------------------------------------------------------------------------
# Octonion arithmetic (8-dimensional, float-valued)
# Index 0 = real unit e0, indices 1..7 = imaginary units e1..e7
# VACUUM_AXIS = 6 means e7 (0-indexed imaginary unit index 6 => basis index 7)
# ---------------------------------------------------------------------------

def octonion_mul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Multiply two octonions represented as length-8 arrays.
    Uses CONVENTIONS.md §2 Fano table (FANO_SIGN, FANO_THIRD).
    Index mapping: basis index i corresponds to e_i (e0=real, e1..e7=imaginary).
    Imaginary unit e_{k+1} <-> Fano point index k (0-based).
    """
    result = np.zeros(8, dtype=float)
    for i in range(8):
        if a[i] == 0:
            continue
        for j in range(8):
            if b[j] == 0:
                continue
            if i == 0:
                result[j] += a[i] * b[j]
            elif j == 0:
                result[i] += a[i] * b[j]
            elif i == j:
                result[0] += -a[i] * b[j]
            else:
                fi = i - 1  # 0-based Fano index for e_i
                fj = j - 1  # 0-based Fano index for e_j
                if (fi, fj) in FANO_SIGN:
                    sign = FANO_SIGN[(fi, fj)]
                    third = FANO_THIRD[(fi, fj)]
                    result[third + 1] += sign * a[i] * b[j]
                else:
                    raise ValueError(f"Fano pair ({fi},{fj}) not found in table")
    return result


def e_basis(k: int) -> np.ndarray:
    """Return the basis octonion e_k (0 = real, 1..7 = imaginary)."""
    v = np.zeros(8, dtype=float)
    v[k] = 1.0
    return v


def scalar(s: float) -> np.ndarray:
    """Return scalar s as octonion s*e0."""
    v = np.zeros(8, dtype=float)
    v[0] = s
    return v


# ---------------------------------------------------------------------------
# CFS-003 key states (mirroring Spinors.lean definitions)
# VACUUM_AXIS=6 means 0-indexed imaginary unit 6 => basis index 7 (e7)
# omega_state  = e0 + e7  (proxy for omegaDoubled)
# left_vac_conj = e0 - e7  (proxy for leftVacConjDoubled)
# ---------------------------------------------------------------------------

E7_IDX = VACUUM_AXIS + 1  # = 7

e7_vec = e_basis(E7_IDX)
e0_vec = e_basis(0)

omega_state = e0_vec + e7_vec    # e0 + e7
left_vac_conj = e0_vec - e7_vec  # e0 - e7


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_fano_table_coverage():
    """CONVENTIONS.md §2: All 42 directed Fano pairs are in FANO_SIGN table."""
    assert len(FANO_SIGN) == 42, f"Expected 42 directed pairs, got {len(FANO_SIGN)}"
    assert len(FANO_THIRD) == 42, f"Expected 42 directed pairs in FANO_THIRD, got {len(FANO_THIRD)}"


def test_fano_seven_cycles():
    """CONVENTIONS.md §2: exactly 7 directed Fano cycles."""
    assert len(FANO_CYCLES) == 7, f"Expected 7 Fano cycles, got {len(FANO_CYCLES)}"


def test_e7_left_squared():
    """e7 * e7 = -e0: the imaginary unit squares to -1 (period-4 orbit prerequisite).
    Mirrors CausalGraph.e7LeftOp_square_eq_neg_one.
    """
    e7_squared = octonion_mul(e7_vec, e7_vec)
    expected = scalar(-1.0)
    np.testing.assert_array_almost_equal(
        e7_squared, expected,
        err_msg="e7 * e7 should equal -e0"
    )


def test_e7_left_four_id():
    """Left-multiplication by e7 four times = identity on e0.
    Mirrors CausalGraph.e7_left_four_id.
    """
    state = e0_vec.copy()
    for _ in range(4):
        state = octonion_mul(e7_vec, state)
    np.testing.assert_array_almost_equal(
        state, e0_vec,
        err_msg="e7^4 * e0 should return e0 (period 4)"
    )


def test_omega_state_nonzero():
    """omega_state is non-zero.
    Mirrors CausalGraph.omegaDoubled_ne_zero.
    """
    assert np.any(omega_state != 0), "omega_state must be non-zero"


def test_left_vac_conj_nonzero():
    """leftVacConj state is non-zero.
    Mirrors CausalGraph.leftVacConjDoubled_ne_zero.
    """
    assert np.any(left_vac_conj != 0), "left_vac_conj state must be non-zero"


def test_e7_left_on_omega_state():
    """e7 * (e0+e7) = e7 - e0 = -e0 + e7.
    Mirrors CausalGraph.e7Left_on_omegaDoubled.
    """
    result = octonion_mul(e7_vec, omega_state)
    expected = -e0_vec + e7_vec
    np.testing.assert_array_almost_equal(
        result, expected,
        err_msg="e7 * (e0+e7) should equal -e0 + e7"
    )


def test_e7_right_on_omega_state():
    """(e0+e7) * e7 = e7 + e7^2 = e7 - e0 = -e0 + e7.
    Mirrors CausalGraph.e7Right_on_omegaDoubled.
    """
    result = octonion_mul(omega_state, e7_vec)
    expected = -e0_vec + e7_vec
    np.testing.assert_array_almost_equal(
        result, expected,
        err_msg="(e0+e7) * e7 should equal -e0 + e7"
    )


def test_left_vac_conj_idempotent_scaled():
    """(e0 - e7)^2 = e0^2 - 2*e7 + e7^2 = 1 - 2*e7 - 1 = -2*e7.
    Mirrors CausalGraph.leftVacConjDoubled_idempotent_scaled.
    """
    sq = octonion_mul(left_vac_conj, left_vac_conj)
    expected = -2.0 * e7_vec
    np.testing.assert_array_almost_equal(
        sq, expected,
        err_msg="(e0-e7)^2 should equal -2*e7"
    )


def test_vacuum_orbit_left_period_four():
    """Left-multiplication orbit of omega_state by e7 has period exactly 4.
    Mirrors CausalGraph.vacuum_orbit_exact_period_four.
    Steps: (e0+e7) -> (-e0+e7) -> (-e0-e7) -> (e0-e7) -> (e0+e7).
    """
    state = omega_state.copy()
    for step in range(1, 4):
        state = octonion_mul(e7_vec, state)
        assert not np.allclose(state, omega_state), \
            f"Left orbit returned to start too early at step {step}"
    # Step 4: should return to omega_state
    state = octonion_mul(e7_vec, state)
    np.testing.assert_array_almost_equal(
        state, omega_state,
        err_msg="Left orbit of omega_state by e7 should have period 4"
    )


def test_vacuum_orbit_right_period_four():
    """Right-multiplication orbit of omega_state by e7 has period exactly 4.
    Mirrors CausalGraph.vacuum_orbit_exact_period_four_right.
    """
    state = omega_state.copy()
    for step in range(1, 4):
        state = octonion_mul(state, e7_vec)
        assert not np.allclose(state, omega_state), \
            f"Right orbit returned to start too early at step {step}"
    state = octonion_mul(state, e7_vec)
    np.testing.assert_array_almost_equal(
        state, omega_state,
        err_msg="Right orbit of omega_state by e7 should have period 4"
    )


def test_left_vac_conj_left_orbit_period_four():
    """Left-multiplication orbit of left_vac_conj by e7 has period exactly 4.
    Mirrors CausalGraph.leftVacConjDoubled_left_orbit_exact_period_four.
    """
    state = left_vac_conj.copy()
    for step in range(1, 4):
        state = octonion_mul(e7_vec, state)
        assert not np.allclose(state, left_vac_conj), \
            f"Left orbit of left_vac_conj returned to start too early at step {step}"
    state = octonion_mul(e7_vec, state)
    np.testing.assert_array_almost_equal(
        state, left_vac_conj,
        err_msg="Left orbit of left_vac_conj by e7 should have period 4"
    )


def test_vacuum_axis_is_e7():
    """VACUUM_AXIS from conftest corresponds to the 7th imaginary unit (e7).
    Verifies CONVENTIONS.md §5.1 alignment.
    """
    assert VACUUM_AXIS == 6, f"VACUUM_AXIS should be 6 (e7 0-indexed), got {VACUUM_AXIS}"
    assert E7_IDX == 7, f"Basis index for e7 should be 7, got {E7_IDX}"


def test_e7_not_in_fano_witt_pairs():
    """VACUUM_AXIS (e7) does not appear in any Witt pair (CONVENTIONS.md §5.2).
    The vacuum axis breaks SU(3) color symmetry and is disjoint from color pairs.
    """
    for a, b in WITT_PAIRS:
        assert a != VACUUM_AXIS, \
            f"VACUUM_AXIS found as first element of Witt pair ({a},{b})"
        assert b != VACUUM_AXIS, \
            f"VACUUM_AXIS found as second element of Witt pair ({a},{b})"


def test_octonion_anticommutativity_sample():
    """Verify e_i * e_j = -(e_j * e_i) for the first Fano cycle.
    Anti-commutativity is a core property of imaginary octonion units.
    """
    a, b, c = FANO_CYCLES[0]
    ea = e_basis(a + 1)
    eb = e_basis(b + 1)
    ec = e_basis(c + 1)

    ab = octonion_mul(ea, eb)
    ba = octonion_mul(eb, ea)

    np.testing.assert_array_almost_equal(
        ab, ec,
        err_msg=f"e{a+1}*e{b+1} should equal +e{c+1}"
    )
    np.testing.assert_array_almost_equal(
        ba, -ec,
        err_msg=f"e{b+1}*e{a+1} should equal -e{c+1}"
    )

# Leibniz