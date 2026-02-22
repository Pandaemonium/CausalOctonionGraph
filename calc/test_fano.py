"""
Tests for calc/fano.py
Mirrors properties in CausalGraphTheory/Fano.lean and FanoMul.lean
"""

import pytest
from calc.fano import fano_line_points, incident, find_line, basis_mul, fano_sign, fano_third
from calc.conftest import FANO_CYCLES

def test_fano_cycles_structure():
    """Verify strictly 7 lines, each length 3."""
    assert len(FANO_CYCLES) == 7
    for triple in FANO_CYCLES:
        assert len(triple) == 3
        # Distinct points
        assert len(set(triple)) == 3
        # Points in range 0..6
        assert all(0 <= p <= 6 for p in triple)

def test_each_point_on_three_lines():
    """Each point 0..6 should appear in exactly 3 lines."""
    for p in range(7):
        count = sum(1 for line in FANO_CYCLES if p in line)
        assert count == 3

def test_two_points_determine_line():
    """Any pair of distinct points lies on exactly one line."""
    for p in range(7):
        for q in range(7):
            if p == q: continue
            
            # Count lines containing both
            lines = [l_idx for l_idx, triple in enumerate(FANO_CYCLES) 
                     if p in triple and q in triple]
            assert len(lines) == 1
            
            # Check find_line returns correct index
            assert find_line(p, q) == lines[0]

def test_basis_mul_specific_cases():
    """Verify specific multiplications against CONVENTIONS.md."""
    # L1: (0, 1, 2) -> e1*e2 = e3
    assert basis_mul(0, 1) == (2, 1)
    assert basis_mul(1, 0) == (2, -1)
    
    # L2: (0, 3, 4) -> e1*e4 = e5
    assert basis_mul(0, 3) == (4, 1)
    
    # L3: (0, 6, 5) -> e1*e7 = e6
    assert basis_mul(0, 6) == (5, 1)
    
    # L5: (1, 4, 6) -> e2*e5 = e7
    assert basis_mul(1, 4) == (6, 1)

def test_basis_mul_sentinel():
    """i == j returns (i, 0)."""
    for i in range(7):
        assert basis_mul(i, i) == (i, 0)

def test_fano_sign_antisymmetric():
    """fano_sign(i, j) == -fano_sign(j, i) for i != j."""
    for i in range(7):
        for j in range(7):
            if i == j: continue
            assert fano_sign(i, j) == -fano_sign(j, i)
            assert fano_sign(i, j) != 0
