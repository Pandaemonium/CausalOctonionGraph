"""
calc/test_weinberg_s4_decomp.py

Pytest tests for WEINBERG-001 Gate 4: S4 vs SL(2,3) subgroup decomposition.

Required tests (7):
1. test_s4_histogram          - exact histogram {1:1, 2:9, 3:8, 4:6}
2. test_s4_order              - sum of S4 histogram = 24
3. test_sl23_order            - sum of SL(2,3) histogram = 24
4. test_groups_nonisomorphic  - S4 != SL(2,3) (distinguisher returns True)
5. test_subgroup_chain_indices - consecutive orders satisfy Lagrange's theorem
6. test_weinberg_estimate_range - 0.10 < sin^2(theta_W) < 0.30
7. test_weinberg_formula       - sin^2(theta_W) = 4/24 exactly
"""

import pytest
from calc.weinberg_s4_decomp import (
    s4_element_order_histogram,
    sl23_element_order_histogram,
    s4_subgroup_chain,
    weinberg_angle_estimate,
    s4_vs_sl23_distinguisher,
)


def test_s4_histogram():
    """S4 element order histogram must be exactly {1:1, 2:9, 3:8, 4:6}."""
    expected = {1: 1, 2: 9, 3: 8, 4: 6}
    result = s4_element_order_histogram()
    assert result == expected, (
        f"S4 histogram mismatch. Expected: {expected}, Got: {result}"
    )


def test_s4_order():
    """S4 has exactly 24 elements (sum of histogram values = 24)."""
    hist = s4_element_order_histogram()
    total = sum(hist.values())
    assert total == 24, f"S4 should have 24 elements, got {total}"


def test_sl23_order():
    """SL(2,3) has exactly 24 elements (same order as S4)."""
    hist = sl23_element_order_histogram()
    total = sum(hist.values())
    assert total == 24, f"SL(2,3) should have 24 elements, got {total}"


def test_groups_nonisomorphic():
    """
    S4 is not isomorphic to SL(2,3): the distinguisher must return True.

    Although |S4| = |SL(2,3)| = 24, SL(2,3) has elements of order 6
    while S4 does not (max order in S4 is 4).
    """
    assert s4_vs_sl23_distinguisher() is True, (
        "s4_vs_sl23_distinguisher() returned False -- groups appear isomorphic, "
        "contradicting the known algebraic fact S4 is not isomorphic to SL(2,3)."
    )


def test_subgroup_chain_indices():
    """
    In the chain GL(3,2) > S4 > V4 > Z2 > {1}, each group's order
    must divide the previous group's order (Lagrange's theorem).
    """
    chain = s4_subgroup_chain()
    assert len(chain) >= 2, "Chain must have at least 2 elements"
    for i in range(len(chain) - 1):
        name_big, order_big = chain[i]
        name_small, order_small = chain[i + 1]
        assert order_big % order_small == 0, (
            f"Lagrange violation: |{name_small}|={order_small} does not "
            f"divide |{name_big}|={order_big}"
        )
        assert order_big // order_small >= 1


def test_weinberg_estimate_range():
    """
    sin^2(theta_W) = 4/24 ~ 0.1667 must lie in (0.10, 0.30),
    bracketing the physical value 0.2312.
    """
    theta = weinberg_angle_estimate()
    assert 0.10 < theta < 0.30, (
        f"sin^2(theta_W) = {theta:.6f} outside (0.10, 0.30); "
        f"physical value is 0.2312, COG estimate should be ~0.1667."
    )


def test_weinberg_formula():
    """The Weinberg estimate must equal |V4|/|S4| = 4/24 to within 1e-10."""
    theta = weinberg_angle_estimate()
    expected = 4 / 24
    assert abs(theta - expected) < 1e-10, (
        f"sin^2(theta_W) = {theta:.15f} differs from 4/24 = {expected:.15f} "
        f"by {abs(theta - expected):.2e}"
    )


def test_sl23_has_order6_s4_does_not():
    """Bonus: SL(2,3) has order-6 elements; S4 does not (max order 4)."""
    hist_sl23 = sl23_element_order_histogram()
    hist_s4   = s4_element_order_histogram()
    assert 6 in hist_sl23, "SL(2,3) should have order-6 elements"
    assert 6 not in hist_s4, "S4 should NOT have order-6 elements"