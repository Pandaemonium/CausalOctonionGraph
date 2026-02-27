"""
Tests for calc/complex_octonion.py
Mirrors properties in WittBasis.lean.
"""

import pytest
import numpy as np
from calc.complex_octonion import witt_basis, VACUUM, ComplexOctonion

def test_witt_anticommute():
    """Check {alpha_j, alpha_k} = 0 and {alpha_j_dag, alpha_k_dag} = 0."""
    basis = witt_basis() # list of (a, adag)
    alphas = [p[0] for p in basis]
    adags = [p[1] for p in basis]
    
    for j in range(3):
        for k in range(3):
            # {alpha_j, alpha_k} = 0
            val = alphas[j] * alphas[k] + alphas[k] * alphas[j]
            assert np.allclose(val.c, 0)
            
            # {alpha_j_dag, alpha_k_dag} = 0
            val = adags[j] * adags[k] + adags[k] * adags[j]
            assert np.allclose(val.c, 0)

def test_witt_clifford():
    """Check {alpha_j, alpha_k_dag} = delta_jk."""
    basis = witt_basis()
    alphas = [p[0] for p in basis]
    adags = [p[1] for p in basis]
    
    for j in range(3):
        for k in range(3):
            val = alphas[j] * adags[k] + adags[k] * alphas[j]
            
            if j == k:
                # Should be 1 (e0)
                assert np.allclose(val.c, [1] + [0]*7)
            else:
                assert np.allclose(val.c, 0)

def test_vacuum_idempotent():
    """omega * omega = omega"""
    val = VACUUM * VACUUM
    assert np.allclose(val.c, VACUUM.c)

def test_vacuum_annihilation():
    """alpha_j * omega = 0"""
    basis = witt_basis()
    alphas = [p[0] for p in basis]
    
    for j in range(3):
        val = alphas[j] * VACUUM
        assert np.allclose(val.c, 0)

def test_vacuum_creation():
    """alpha_j_dag * omega != 0 (creates a state)"""
    basis = witt_basis()
    adags = [p[1] for p in basis]
    
    for j in range(3):
        val = adags[j] * VACUUM
        assert not np.allclose(val.c, 0)
