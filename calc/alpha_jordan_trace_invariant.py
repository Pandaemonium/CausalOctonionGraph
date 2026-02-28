#!/usr/bin/env python3
"""
Target: Fine-Structure Constant (alpha) via J_3(O) Trace Invariant
Claim: ALPHA-001 / J3-TRACE-001
Description: Tests if a 3-node cyclic motif natively generates a Hermitian 
interaction matrix M whose eigenvalue spectrum stabilizes to the Singh (2021) 
trace ratio Tr(M^3) / Tr(M^2)^1.5 ≈ 1/137.

Binary Outcome:
- IF RATIO ≈ 0.007297: The fine-structure constant is a topological invariant 
  of the C x O update rule.
- IF RATIO != 0.007297: The pure integer geometry does not natively yield alpha 
  without a discrete RGE scaling bridge.
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple

# Assuming minimal_world_kernel is accessible in the python path
from minimal_world_kernel_calc_copy import (
    CxO,
    GInt,
    World,
    cxo_mul,
    step,
    ZERO_G,
    ONE_G
)

# ---------------------------------------------------------------------------
# 1. Algebraic Primitives for C x O
# ---------------------------------------------------------------------------

def cxo_conjugate(a: CxO) -> CxO:
    """
    Octonion conjugation: negates the 7 imaginary basis directions.
    e0 remains unchanged. (Assuming standard O conjugation for Albert algebra).
    """
    return (
        a[0],
        GInt(-a[1].re, -a[1].im),
        GInt(-a[2].re, -a[2].im),
        GInt(-a[3].re, -a[3].im),
        GInt(-a[4].re, -a[4].im),
        GInt(-a[5].re, -a[5].im),
        GInt(-a[6].re, -a[6].im),
        GInt(-a[7].re, -a[7].im)
    )

def gint_add(g1: GInt, g2: GInt) -> GInt:
    return GInt(g1.re + g2.re, g1.im + g2.im)

def cxo_add(a: CxO, b: CxO) -> CxO:
    return tuple(gint_add(a[i], b[i]) for i in range(8))

def cxo_real_trace(a: CxO) -> float:
    """Extracts the real part of the e0 component."""
    return float(a[0].re)

# ---------------------------------------------------------------------------
# 2. Albert Algebra J_3(O) Trace Constructors
# ---------------------------------------------------------------------------

def build_interaction_matrix(psi_0: CxO, psi_1: CxO, psi_2: CxO) -> List[List[CxO]]:
    """
    Constructs the 3x3 Hermitian matrix M where M_ij = psi_i * psi_j^dagger.
    This maps the 3-node graph state into the exceptional Jordan algebra J_3(O).
    """
    psis = [psi_0, psi_1, psi_2]
    M = [[tuple(ZERO_G for _ in range(8)) for _ in range(3)] for _ in range(3)]
    
    for i in range(3):
        for j in range(3):
            # M_ij = psi_i * conjugate(psi_j)
            M[i][j] = cxo_mul(psis[i], cxo_conjugate(psis[j]))
            
    return M

def compute_jordan_traces(M: List[List[CxO]]) -> Tuple[float, float]:
    """
    Computes Tr(M^2) and Tr(M^3) for the 3x3 matrix M.
    Because M is Hermitian over O, the traces of powers are real and well-defined 
    (the algebra is power-associative).
    """
    # Tr(M^2) = sum_{i,j} (M_ij * M_ji)
    tr_m2_cxo = tuple(ZERO_G for _ in range(8))
    for i in range(3):
        for j in range(3):
            # cxo_mul is used here, but for J_3(O) elements we just need the trace
            tr_m2_cxo = cxo_add(tr_m2_cxo, cxo_mul(M[i][j], M[j][i]))
    
    # Tr(M^3) = sum_{i,j,k} (M_ij * (M_jk * M_ki))
    tr_m3_cxo = tuple(ZERO_G for _ in range(8))
    for i in range(3):
        for j in range(3):
            for k in range(3):
                term = cxo_mul(M[i][j], cxo_mul(M[j][k], M[k][i]))
                tr_m3_cxo = cxo_add(tr_m3_cxo, term)
                
    return cxo_real_trace(tr_m2_cxo), cxo_real_trace(tr_m3_cxo)

# ---------------------------------------------------------------------------
# 3. Dynamic Test Execution
# ---------------------------------------------------------------------------

def _basis_state(idx: int) -> CxO:
    vals = [ZERO_G for _ in range(8)]
    vals[idx] = ONE_G
    return tuple(vals)

def run_deep_cone_invariant_test(steps: int = 50):
    """
    Initializes a 3-node cyclic motif (representing the 3 Witt pairs) and 
    tracks the J_3(O) trace invariant over N discrete update ticks.
    """
    ALPHA_PHYSICAL = 1 / 137.035999
    
    # Initialize a simple closed 3-node cycle
    node_ids = ["n0", "n1", "n2"]
    parents = {
        "n0": ["n2"], # n2 -> n0
        "n1": ["n0"], # n0 -> n1
        "n2": ["n1"]  # n1 -> n2
    }
    
    # Seed with the 3 color planes (Witt pair generators)
    states = {
        "n0": cxo_add(_basis_state(6), _basis_state(1)), # P1
        "n1": cxo_add(_basis_state(2), _basis_state(5)), # P2
        "n2": cxo_add(_basis_state(3), _basis_state(4))  # P3
    }
    
    world = World(node_ids=node_ids, parents=parents, states=states, tick=0)
    
    print(f"Target physical ratio: {ALPHA_PHYSICAL:.6f} (1/137.036)")
    print("-" * 65)
    print(f"{'Tick':<6} | {'Tr(M^2)':<10} | {'Tr(M^3)':<12} | {'Ratio R':<12} | {'% Error':<10}")
    print("-" * 65)
    
    for t in range(1, steps + 1):
        world = step(world)
        
        # Extract the 3 states to build the matrix
        psi_0 = world.states["n0"]
        psi_1 = world.states["n1"]
        psi_2 = world.states["n2"]
        
        M = build_interaction_matrix(psi_0, psi_1, psi_2)
        tr_m2, tr_m3 = compute_jordan_traces(M)
        
        if tr_m2 <= 0:
            ratio = 0.0
        else:
            # R = Tr(M^3) / (Tr(M^2)^(3/2))
            ratio = tr_m3 / (tr_m2 ** 1.5)
            
        error = abs(ratio - ALPHA_PHYSICAL) / ALPHA_PHYSICAL * 100 if ratio != 0 else float('inf')
        
        print(f"{t:<6} | {tr_m2:<10.1f} | {tr_m3:<12.1f} | {ratio:<12.6f} | {error:<10.2f}%")
        
        # If the ratio blows up or zeroes out, break early
        if tr_m2 > 1e12 or tr_m2 == 0:
            break

if __name__ == "__main__":
    print("=== EXCEPTIONAL JORDAN ALGEBRA TRACE INVARIANT TEST ===")
    run_deep_cone_invariant_test(steps=20)