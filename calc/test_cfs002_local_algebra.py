"""
CFS-002 Gate 1: Discrete Local Algebra Projectors.
Scaffolded combinatorial checks for rank-1 projectors on Fano points.
"""

import numpy as np

from calc.conftest import FANO_CYCLES, VACUUM_AXIS


def projector(idx: int) -> np.ndarray:
    """Rank-1 projector onto basis vector e_idx in R^7."""
    vec = np.zeros(7, dtype=int)
    vec[idx] = 1
    return np.outer(vec, vec)


def test_fano_projector_rank1():
    """Each basis projector has rank 1 and is idempotent."""
    for i in range(7):
        p_i = projector(i)
        assert np.linalg.matrix_rank(p_i) == 1
        assert np.array_equal(p_i @ p_i, p_i)


def test_projectors_orthogonal_off_line():
    """Distinct basis projectors are orthogonal (P_i P_j = 0 for i != j)."""
    for i in range(7):
        for j in range(7):
            if i == j:
                continue
            p_i = projector(i)
            p_j = projector(j)
            assert np.array_equal(p_i @ p_j, np.zeros((7, 7), dtype=int))


def test_projectors_on_same_line():
    """Projectors on a common Fano line span a 3D subspace."""
    line = FANO_CYCLES[0]
    p_sum = sum(projector(idx) for idx in line)
    assert np.linalg.matrix_rank(p_sum) <= 3


def test_local_algebra_dimension():
    """Seven rank-1 projectors are linearly independent as 7x7 matrices."""
    flattened = [projector(i).reshape(-1) for i in range(7)]
    stacked = np.vstack(flattened)
    assert np.linalg.matrix_rank(stacked) == 7


def test_vacuum_projector_special():
    """Vacuum axis e7 corresponds to a single diagonal 1 at index 6."""
    p_vac = projector(VACUUM_AXIS)
    assert np.trace(p_vac) == 1
    for i in range(7):
        for j in range(7):
            if i == VACUUM_AXIS and j == VACUUM_AXIS:
                assert p_vac[i, j] == 1
            else:
                assert p_vac[i, j] == 0


def test_fano_lines_seven():
    """Fano lines: exactly 7 triples of distinct points."""
    assert len(FANO_CYCLES) == 7
    for line in FANO_CYCLES:
        assert len(line) == 3
        assert len(set(line)) == 3


def test_each_point_on_three_lines():
    """Each point appears on exactly 3 Fano lines."""
    for p in range(7):
        count = sum(1 for line in FANO_CYCLES if p in line)
        assert count == 3


def test_projector_sum_scalar_multiple():
    """Sum of all projectors equals the identity matrix."""
    p_sum = sum(projector(i) for i in range(7))
    assert np.array_equal(p_sum, np.eye(7, dtype=int))

# Gauss