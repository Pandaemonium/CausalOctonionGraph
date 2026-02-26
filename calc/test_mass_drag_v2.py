"""
Tests for Gate-Density Simulation (Gate 2) — RFC-009 §7b.10
MU-001: Proton-to-electron mass ratio via non-associative gate counting.
"""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import mass_drag_v2 as m


def test_run_proton_no_exception():
    """Proton simulation runs N=100 steps without raising."""
    result = m.run_proton(100)
    assert isinstance(result, int)
    assert result >= 0


def test_run_electron_no_exception():
    """Electron simulation runs N=100 steps without raising."""
    result = m.run_electron(100)
    assert isinstance(result, int)
    assert result >= 0


def test_electron_is_associative():
    """L1 = {e1, e2, e3} is the quaternion subalgebra — fully associative.
    The electron motif cycling through L1 should fire zero non-associative gates.
    """
    result = m.run_electron(300)
    assert result == 0, (
        f"Expected 0 gates for associative electron motif, got {result}"
    )


def test_proton_has_nonzero_gates():
    """Proton uud motif should fire a non-zero number of non-associative gates."""
    result = m.run_proton(300)
    assert result > 0, (
        f"Expected >0 gates for non-associative proton motif, got {result}"
    )


def test_gate_density_ratio():
    """Gate density simulation runs end-to-end and returns a result."""
    N = 100
    p = m.run_proton(N)
    e = m.run_electron(N)
    # Either DEGENERATE (e==0) or a finite ratio — both are valid outputs
    if e == 0:
        pass  # OK — confirmed associativity of electron motif
    else:
        ratio = (p / N) / (e / N)
        assert ratio > 0


def test_fano_tables_complete():
    """All 42 ordered pairs of distinct Fano indices should be in the tables."""
    # 7 indices, each ordered pair appears once: 7*6 = 42 entries
    assert len(m.FANO_SIGN) == 42
    assert len(m.FANO_THIRD) == 42


def test_oct_mul_anticommutativity():
    """e_i * e_j = -e_j * e_i for i != j (octonion anti-commutativity)."""
    for i in range(7):
        for j in range(7):
            if i == j:
                continue
            idx_ij, sign_ij = m.oct_mul(i, +1, j, +1)
            idx_ji, sign_ji = m.oct_mul(j, +1, i, +1)
            assert idx_ij == idx_ji, f"Index mismatch for e{i}*e{j} vs e{j}*e{i}"
            assert sign_ij == -sign_ji, (
                f"Sign mismatch: e{i}*e{j} sign={sign_ij}, e{j}*e{i} sign={sign_ji}"
            )


# ---- Required tests from RFC-009 Gate 2 spec --------------------------------

def test_electron_associativity():
    """Assert that the {e1, e2, e3} cycle produces exactly 0 gates over 100 steps."""
    result = m.run_electron(100)
    assert result == 0, (
        f"Expected 0 gates for associative electron motif {'{e1,e2,e3}'}, got {result}"
    )


def test_proton_activity():
    """Assert that the {e1, e2, e4} cycle produces >0 gates over 100 steps."""
    result = m.run_proton(100)
    assert result > 0, (
        f"Expected >0 gates for non-associative proton motif {'{e1,e2,e4}'}, got {result}"
    )


def test_sign_tracking():
    """Specific check that (-e1) * e2 is handled correctly (result sign flips).

    e1 * e2 = +e3  (Fano cycle (0,1,2), FANO_SIGN[(0,1)] = +1)
    (-e1) * e2 = -e3  (combined_sign = -1 * +1 = -1)
    """
    # Positive case: e1 * e2 = +e3
    idx_pos, sign_pos = m.oct_mul(0, +1, 1, +1)
    assert idx_pos == 2, f"e1*e2 should give e3 (idx=2), got idx={idx_pos}"
    assert sign_pos == +1, f"e1*e2 should be +e3, got sign={sign_pos}"

    # Negative case: (-e1) * e2 = -e3
    idx_neg, sign_neg = m.oct_mul(0, -1, 1, +1)
    assert idx_neg == 2, f"(-e1)*e2 should give e3 (idx=2), got idx={idx_neg}"
    assert sign_neg == -1, f"(-e1)*e2 should be -e3, got sign={sign_neg}"

    # Double-negative: (-e1) * (-e2) = +e3
    idx_pp, sign_pp = m.oct_mul(0, -1, 1, -1)
    assert idx_pp == 2, f"(-e1)*(-e2) should give e3 (idx=2), got idx={idx_pp}"
    assert sign_pp == +1, f"(-e1)*(-e2) should be +e3, got sign={sign_pp}"