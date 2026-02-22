"""
calc/fano.py
Phase 1.1: Fano plane arithmetic

Mirrors CausalGraphTheory/Fano.lean and CausalGraphTheory/FanoMul.lean.
Operates on 0-indexed Fano points (0..6), representing e1..e7.
"""

from calc.conftest import FANO_CYCLES

def fano_line_points(l: int) -> list[int]:
    """Return the 3 points on Fano line l (0..6)."""
    return list(FANO_CYCLES[l])

def incident(p: int, l: int) -> bool:
    """True if point p is on line l."""
    return p in FANO_CYCLES[l]

def find_line(p: int, q: int) -> int | None:
    """Find the line index containing points p and q."""
    for l_idx, triple in enumerate(FANO_CYCLES):
        if p in triple and q in triple:
            return l_idx
    return None

def basis_mul(i: int, j: int) -> tuple[int, int]:
    """
    Multiply two imaginary basis units e_{i+1} and e_{j+1}.
    Returns (k, sign) such that e_{i+1} * e_{j+1} = sign * e_{k+1}.
    
    If i == j, returns (i, 0) as a sentinel (since e_i^2 = -1 is not in Fano).
    """
    if i == j:
        return (i, 0)
    
    # Check all lines
    for triple in FANO_CYCLES:
        # Check if {i, j} is a subset of the triple
        if i in triple and j in triple:
            # Determine sign based on cyclic order
            # triple is (a, b, c) -> a*b=c, b*c=a, c*a=b
            a, b, c = triple
            
            if i == a and j == b: return (c, 1)
            if i == b and j == c: return (a, 1)
            if i == c and j == a: return (b, 1)
            
            if i == b and j == a: return (c, -1)
            if i == c and j == b: return (a, -1)
            if i == a and j == c: return (b, -1)
            
    raise ValueError(f"Points {i} and {j} not found on any common line (impossible in Fano)")

def fano_sign(i: int, j: int) -> int:
    """Return +1, -1, or 0 (if i==j)."""
    return basis_mul(i, j)[1]

def fano_third(i: int, j: int) -> int:
    """Return k where e_i * e_j = +/- e_k."""
    return basis_mul(i, j)[0]
