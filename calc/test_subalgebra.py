"""
Tests for subalgebra detection and non-associativity counting.
Mirrors SubalgebraDetect.lean.
"""

import pytest
from calc.octonion import Octonion
from calc.fano import fano_line_points, FANO_CYCLES

def is_associative(i, j, k):
    """Check if (ei * ej) * ek == ei * (ej * ek)."""
    # Use 0-indexed indices for Octonion.basis (0 is e0, 1 is e1...)
    # Inputs i,j,k are 0-indexed Fano points (0..6) -> Octonion indices 1..7
    ei = Octonion.basis(i + 1)
    ej = Octonion.basis(j + 1)
    ek = Octonion.basis(k + 1)
    return (ei * ej) * ek == ei * (ej * ek)

def test_batchable_fano_lines():
    """Verify that every Fano line generates an associative triple."""
    for line in FANO_CYCLES:
        i, j, k = line
        # Check all permutations? Or just the line points?
        # Fano line points are always associative.
        assert is_associative(i, j, k)
        assert is_associative(j, k, i)
        assert is_associative(k, i, j)
        # Also with repeated elements? (always associative if 2 are same)
        assert is_associative(i, i, k)

def test_non_associative_count():
    """
    Verify exactly 28 out of 35 unordered triples are non-associative.
    35 total triples of distinct points from 7.
    7 are lines (associative).
    28 should be non-associative.
    """
    assoc_count = 0
    non_assoc_count = 0
    
    # Iterate all unique unordered triples {i, j, k}
    for i in range(7):
        for j in range(i + 1, 7):
            for k in range(j + 1, 7):
                if is_associative(i, j, k):
                    assoc_count += 1
                else:
                    non_assoc_count += 1
                    
    assert assoc_count == 7
    assert non_assoc_count == 28

def test_specific_non_associative():
    """Test a known non-associative triple: e1, e2, e4 (0, 1, 3)."""
    # e1=0, e2=1, e4=3.
    # Lines: (0,1,2), (0,3,4). No line contains {0,1,3}.
    assert not is_associative(0, 1, 3)
