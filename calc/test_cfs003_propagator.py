"""
test_cfs003_propagator.py -- Python verification of CFS-003 discrete propagator.

The Fano plane has 7 points (0-6) and 7 lines:
  (0,1,3), (1,2,4), (2,3,5), (3,4,6), (4,5,0), (5,6,1), (6,0,2)

Propagator K(i,j) = 1 if i and j share a Fano line (or i == j), else 0.

Tests correspond to Lean theorems in CausalGraphTheory/CFS003Propagator.lean.
"""

import pytest

# ---- Fano plane definition ------------------------------------------------

FANO_LINES = [(0, 1, 3), (1, 2, 4), (2, 3, 5), (3, 4, 6), (4, 5, 0), (5, 6, 1), (6, 0, 2)]
FANO_POINTS = list(range(7))


def fano_incidence(i, j):
    """True if points i and j share at least one Fano line, or i == j."""
    if i == j:
        return True
    return any(i in line and j in line for line in FANO_LINES)


def propagator_kernel(i, j):
    """K(i,j): 1 if collinear (or equal) on the Fano plane, else 0."""
    return 1 if fano_incidence(i, j) else 0


def kernel_matrix():
    """Full 7x7 propagator kernel matrix."""
    return [[propagator_kernel(i, j) for j in FANO_POINTS] for i in FANO_POINTS]


# ---- Tests ----------------------------------------------------------------

def test_propagator_finset_support():
    """
    Corresponds to: propagatorKernel_support_le
    Each row has support (nonzero entries) of size <= 7.
    Also checks support is non-empty (non-degenerate).
    """
    K = kernel_matrix()
    for i in FANO_POINTS:
        support = [j for j in FANO_POINTS if K[i][j] != 0]
        assert len(support) <= 7, f"Row {i}: support size {len(support)} > 7"
        assert len(support) > 0, f"Row {i}: support is empty (degenerate)"


def test_propagator_symmetry():
    """
    Corresponds to: propagatorKernel_symmetric
    K(i,j) = K(j,i) for all Fano point pairs.
    """
    for i in FANO_POINTS:
        for j in FANO_POINTS:
            kij = propagator_kernel(i, j)
            kji = propagator_kernel(j, i)
            assert kij == kji, f"Symmetry failed: K({i},{j})={kij} != K({j},{i})={kji}"


def test_propagator_causal_support_bound():
    """
    Corresponds to: propagatorKernel_support_le
    In PG(2,2) every two distinct points share a line, so each row sum = 7.
    """
    K = kernel_matrix()
    for i in FANO_POINTS:
        support_size = sum(K[i])
        assert 1 <= support_size <= 7, (
            f"Row {i} support sum {support_size} out of [1,7]"
        )
        assert support_size == 7, (
            f"Row {i} sum = {support_size}, expected 7 (complete Fano design)"
        )


def test_propagator_vacuum_normalization():
    """
    Corresponds to: propagatorKernel_diag_one
    K(i,i) = 1 for all points i (vacuum normalization).
    """
    for i in FANO_POINTS:
        val = propagator_kernel(i, i)
        assert val == 1, f"Diagonal K({i},{i}) = {val}, expected 1"


def test_propagator_discrete_spectrum():
    """
    Corresponds to: propagatorKernel_bound
    K takes values in {0, 1} only (discrete integer spectrum).
    """
    K = kernel_matrix()
    for i in FANO_POINTS:
        for j in FANO_POINTS:
            val = K[i][j]
            assert val in (0, 1), (
                f"K({i},{j}) = {val} not in {{0,1}} (not discrete spectrum)"
            )


def test_propagator_row_sum_positive():
    """
    Corresponds to: propagatorKernel_row_sum_pos
    Each row sum is strictly positive (propagator is non-degenerate).
    """
    K = kernel_matrix()
    for i in FANO_POINTS:
        row_sum = sum(K[i])
        assert row_sum > 0, f"Row {i} sum = {row_sum}, propagator is degenerate"


def test_propagator_fano_line_count():
    """
    Structural check: Fano plane has exactly 7 lines, each with 3 distinct points.
    """
    assert len(FANO_LINES) == 7, f"Expected 7 Fano lines, got {len(FANO_LINES)}"
    for line in FANO_LINES:
        pts = list(line)
        assert len(pts) == 3, f"Line {line} does not have 3 points"
        assert len(set(pts)) == 3, f"Line {line} has repeated points"
        for p in pts:
            assert 0 <= p <= 6, f"Point {p} out of Fano range [0,6]"


def test_propagator_kernel_full_matrix():
    """
    In PG(2,2), every pair of distinct points shares exactly one line.
    So K is the 7x7 all-ones matrix.
    """
    for i in FANO_POINTS:
        for j in FANO_POINTS:
            val = propagator_kernel(i, j)
            assert val == 1, (
                f"K({i},{j}) = {val}, expected 1 "
                f"(any two Fano points share a line)"
            )

# Leibniz