"""
calc/complex_octonion.py
Phase 1.3: Complex Octonions and Witt Basis

Mirrors CausalGraphTheory/ComplexOctonion.lean and WittBasis.lean.
"""

import numpy as np
from calc.octonion import Octonion

# Vacuum axis is e7 (0-indexed: 6)
VACUUM_AXIS = 6

def complex_basis(i):
    """Return basis element e_i with complex coefficients."""
    o = Octonion.basis(i)
    o.c = o.c.astype(complex)
    return o

class ComplexOctonion(Octonion):
    """
    Octonion with complex coefficients.
    Inherits from Octonion but ensures complex dtype.
    """
    def __init__(self, coeffs):
        super().__init__(coeffs)
        if self.c.dtype != complex:
            self.c = self.c.astype(complex)

    @classmethod
    def basis(cls, i):
        o = super().basis(i)
        return cls(o.c)

# Precomputed basis elements
E0 = ComplexOctonion.basis(0)
E1 = ComplexOctonion.basis(1)
E2 = ComplexOctonion.basis(2)
E3 = ComplexOctonion.basis(3)
E4 = ComplexOctonion.basis(4)
E5 = ComplexOctonion.basis(5)
E6 = ComplexOctonion.basis(6)
E7 = ComplexOctonion.basis(7)

BASIS = [E0, E1, E2, E3, E4, E5, E6, E7]

# Witt Pairings (0-indexed)
# (6, 1) -> (e6, e1)
# (2, 5) -> (e2, e5)
# (3, 4) -> (e3, e4)
WITT_PAIRS = [
    (5, 0), # j=1: (e6, e1)
    (1, 4), # j=2: (e2, e5)
    (2, 3), # j=3: (e3, e4)
]

def witt_operator(j, dag=False):
    """
    Construct Witt operator alpha_j or alpha_j_dagger.
    alpha_j = 0.5 * (e_a + i * e_b)
    alpha_j_dagger = 0.5 * (e_a - i * e_b)
    """
    a, b = WITT_PAIRS[j] # a, b are 0-indexed indices into 1..7 (e_{a+1}, e_{b+1})
    
    # Octonion.basis(k) expects 0..7.
    # The pairs in WITT_PAIRS are 0-indexed Fano points (0..6).
    # So we need to map them to Octonion indices (1..7).
    # Actually, Fano 0 is Octonion 1.
    ea = BASIS[a + 1]
    eb = BASIS[b + 1]
    
    i_unit = 1j
    
    if dag:
        # alpha_dag = (alpha)* = (0.5 * (ea + i*eb))* 
        #           = 0.5 * (ea* + (i*eb)*)
        #           = 0.5 * (-ea + (-i)(-eb))
        #           = 0.5 * (-ea + i*eb)
        #           = -0.5 * (ea - i*eb)
        # Note: CONVENTIONS.md lists 0.5*(ea - i*eb), which is just complex conjugate.
        # But to satisfy {alpha, alpha_dag} = 1, we need the full adjoint.
        return (eb * i_unit - ea) * 0.5
    else:
        # 0.5 * (e_a + i * e_b)
        return (ea + eb * i_unit) * 0.5

def witt_basis():
    """Return list of (alpha_j, alpha_j_dagger) for j=0,1,2."""
    return [(witt_operator(j, dag=False), witt_operator(j, dag=True)) for j in range(3)]

# Vacuum State
# omega = 0.5 * (1 + i * e7)
VACUUM = (E0 + E7 * 1j) * 0.5
