"""
calc/koide_associator_derive.py

Exploration: Does B/A = sqrt(2) arise from the ratio of associator norms
across non-collinear vs collinear Fano triples?

Hypothesis: The ratio ||[e_i,e_j,e_k]||^2 / ||e_i||^2 evaluated over
non-collinear Fano triples yields a value related to 2 (linking to B^2/A^2 = 2).

Uses the octonion multiplication table from CONVENTIONS.md §2 via conftest.py.
References: rfc/CONVENTIONS.md, claims/KOIDE-001.yml
"""

import math
import sys
import os
import numpy as np
from itertools import combinations

# ---------------------------------------------------------------------------
# Import the canonical octonion multiplication data from conftest.py
# (Never redefine locally — always import from conftest)
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(__file__))
from conftest import FANO_CYCLES, FANO_SIGN, FANO_THIRD

# conftest.py uses 0-indexed Fano points (0..6 corresponding to e1..e7)
# FANO_CYCLES: list of (a, b, c) where e_{a+1} * e_{b+1} = +e_{c+1}
# FANO_SIGN[(a,b)] = +/-1 for e_{a+1} * e_{b+1}
# FANO_THIRD[(a,b)] = c  (0-indexed result index)

# Collinear sets (0-indexed)
COLLINEAR_SETS_0 = [frozenset(line) for line in FANO_CYCLES]


def oct_mult_0indexed(i, j):
    """
    Multiply imaginary octonion basis elements e_{i+1} * e_{j+1}, 0-indexed.
    i, j in {0,...,6}.
    Returns (sign, k) where e_{i+1} * e_{j+1} = sign * e_{k+1}, k in {0,...,6}.
    For i == j: returns (-1, None) since e_{i+1}^2 = -e_0.
    """
    if i == j:
        return (-1, None)
    sign = FANO_SIGN.get((i, j))
    k = FANO_THIRD.get((i, j))
    if sign is None or k is None:
        raise ValueError(f"No Fano multiplication found for 0-indexed e_{i} * e_{j}")
    return (sign, k)


def oct_mult_vec(a_vec, b_vec):
    """
    Multiply two octonion vectors (length-8 arrays).
    Index 0 = e_0 (real unit), indices 1..7 = imaginary units (1-indexed physics).
    Internal: maps to 0-indexed Fano data for imaginary products.
    """
    result = np.zeros(8, dtype=float)
    for i in range(8):
        if a_vec[i] == 0.0:
            continue
        for j in range(8):
            if b_vec[j] == 0.0:
                continue
            coeff = a_vec[i] * b_vec[j]
            if i == 0:
                # e_0 * e_j = e_j
                result[j] += coeff
            elif j == 0:
                # e_i * e_0 = e_i
                result[i] += coeff
            else:
                # i, j in {1..7} (1-indexed physics) => 0-indexed: i-1, j-1
                sign, k0 = oct_mult_0indexed(i - 1, j - 1)
                if k0 is None:
                    # e_i^2 = -e_0
                    result[0] += sign * coeff  # sign = -1
                else:
                    result[k0 + 1] += sign * coeff
    return result


def basis_vec(idx, dim=8):
    """
    Return basis vector e_idx (length-8 array).
    idx=0: real unit e_0; idx=1..7: imaginary units e_1..e_7.
    """
    v = np.zeros(dim, dtype=float)
    v[idx] = 1.0
    return v


def compute_associator(i, j, k):
    """
    Compute the associator [e_i, e_j, e_k] = (e_i * e_j) * e_k - e_i * (e_j * e_k).
    i, j, k in {1,...,7} (1-indexed physics convention).
    Returns an 8-dimensional octonion vector (index 0 = real, 1..7 = imaginary).
    """
    ei = basis_vec(i)
    ej = basis_vec(j)
    ek = basis_vec(k)
    lhs = oct_mult_vec(oct_mult_vec(ei, ej), ek)
    rhs = oct_mult_vec(ei, oct_mult_vec(ej, ek))
    return lhs - rhs


def norm_sq(v):
    """Return the squared Euclidean norm of vector v."""
    return float(np.dot(v, v))


def is_collinear(i, j, k):
    """
    Return True if {i, j, k} is a Fano line (collinear triple).
    i, j, k in {1,...,7} (1-indexed). Converts to 0-indexed for comparison.
    """
    return frozenset({i - 1, j - 1, k - 1}) in COLLINEAR_SETS_0


def get_all_imaginary_triples():
    """Return all C(7,3) = 35 unordered triples from {1,...,7} (1-indexed)."""
    return list(combinations(range(1, 8), 3))


def main():
    all_triples = get_all_imaginary_triples()
    collinear_triples = [(i, j, k) for (i, j, k) in all_triples if is_collinear(i, j, k)]
    noncollinear_triples = [(i, j, k) for (i, j, k) in all_triples if not is_collinear(i, j, k)]

    print("=" * 70)
    print("KOIDE-001 EXPLORATION: Associator Norms and B/A = sqrt(2)")
    print("=" * 70)
    print(f"\nTotal triples C(7,3) = {len(all_triples)} (expect 35)")
    print(f"Collinear (Fano lines): {len(collinear_triples)} (expect 7)")
    print(f"Non-collinear:          {len(noncollinear_triples)} (expect 28)")

    # Verify counts match CONVENTIONS.md §3
    assert len(all_triples) == 35, f"Expected 35 triples, got {len(all_triples)}"
    assert len(collinear_triples) == 7, f"Expected 7 collinear, got {len(collinear_triples)}"
    assert len(noncollinear_triples) == 28, f"Expected 28 non-collinear, got {len(noncollinear_triples)}"

    # --- Collinear triples: associator should be 0 ---
    print("\n" + "-" * 70)
    print("COLLINEAR TRIPLES (associative, H ⊂ O => associator = 0):")
    print("-" * 70)
    print(f"  {'Triple':12s}  {'||assoc||^2':12s}  Notes")
    for (i, j, k) in collinear_triples:
        assoc = compute_associator(i, j, k)
        ns = norm_sq(assoc)
        ok = "✓ zero" if ns < 1e-10 else f"✗ NONZERO: {ns:.6f}"
        print(f"  e{i},e{j},e{k}       {ns:12.6f}  {ok}")

    # --- Non-collinear triples: associator should be nonzero ---
    print("\n" + "-" * 70)
    print("NON-COLLINEAR TRIPLES (non-associative => associator ≠ 0):")
    print("-" * 70)
    print(f"  {'Triple':12s}  {'||assoc||^2':12s}  {'Associator (nonzero components)':30s}")
    norm_sq_values = []
    for (i, j, k) in noncollinear_triples:
        assoc = compute_associator(i, j, k)
        ns = norm_sq(assoc)
        norm_sq_values.append(ns)
        nonzero = {idx: f"{assoc[idx]:+.1f}" for idx in range(8) if abs(assoc[idx]) > 1e-12}
        print(f"  e{i},e{j},e{k}       {ns:12.6f}  {str(nonzero)}")

    # --- Summary statistics ---
    mean_norm_sq = np.mean(norm_sq_values)
    min_ns = min(norm_sq_values)
    max_ns = max(norm_sq_values)
    distinct = sorted(set(round(v, 6) for v in norm_sq_values))

    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS (non-collinear triples):")
    print("=" * 70)
    print(f"  Number of non-collinear triples:   {len(noncollinear_triples)}")
    print(f"  Distinct ||assoc||^2 values:       {distinct}")
    print(f"  Min / Max:                         {min_ns:.4f} / {max_ns:.4f}")
    print(f"  Mean ||[e_i,e_j,e_k]||^2:          {mean_norm_sq:.8f}")
    print(f"  sqrt(mean ||assoc||^2):             {math.sqrt(mean_norm_sq):.8f}")
    print(f"  Reference: sqrt(2)  =               {math.sqrt(2):.8f}")
    print(f"  Reference: 2.0      =               {2.0:.8f}")
    print()

    if abs(mean_norm_sq - 2.0) < 1e-10:
        print("  *** RESULT: Mean ||assoc||^2 = 2.0 EXACTLY ***")
        print("  *** => sqrt(mean) = sqrt(2) = B/A  ***")
        print("  *** SUPPORTS: B^2/A^2 = 2, i.e., B/A = sqrt(2) from octonion geometry ***")
    else:
        print(f"  *** RESULT: Mean ||assoc||^2 = {mean_norm_sq:.8f} (NOT equal to 2.0) ***")
        print(f"  *** sqrt(mean) = {math.sqrt(mean_norm_sq):.8f} vs sqrt(2) = {math.sqrt(2):.8f} ***")
        print(f"  # KOIDE-001: B/A derivation gap — actual mean ||assoc||^2 = {mean_norm_sq:.8f}")

    # --- Proton motif {e1, e2, e4}: non-collinear ---
    print("\n" + "-" * 70)
    print("PROTON MOTIF {e1, e2, e4} (non-associative Fano triple):")
    print("-" * 70)
    e1, e2, e4 = basis_vec(1), basis_vec(2), basis_vec(4)
    lhs = oct_mult_vec(oct_mult_vec(e1, e2), e4)
    rhs = oct_mult_vec(e1, oct_mult_vec(e2, e4))
    assoc_proton = lhs - rhs
    lhs_str = {i: f"{v:+.1f}" for i, v in enumerate(lhs) if abs(v) > 1e-12}
    rhs_str = {i: f"{v:+.1f}" for i, v in enumerate(rhs) if abs(v) > 1e-12}
    assoc_str = {i: f"{v:+.1f}" for i, v in enumerate(assoc_proton) if abs(v) > 1e-12}
    print(f"  (e1*e2)*e4 = {lhs_str}")
    print(f"  e1*(e2*e4) = {rhs_str}")
    print(f"  Associator = {assoc_str}")
    print(f"  ||assoc||^2 = {norm_sq(assoc_proton):.6f}")

    # --- Electron motif {e1, e2, e3}: collinear ---
    print("\n" + "-" * 70)
    print("ELECTRON MOTIF {e1, e2, e3} (associative, H ⊂ O, Fano line L1):")
    print("-" * 70)
    assoc_electron = compute_associator(1, 2, 3)
    assoc_e_str = {i: f"{v:+.1f}" for i, v in enumerate(assoc_electron) if abs(v) > 1e-12}
    print(f"  [e1, e2, e3] = {assoc_e_str if assoc_e_str else '{} (zero vector)'}")
    print(f"  ||assoc||^2 = {norm_sq(assoc_electron):.6f}  (Expected: 0.0)")

    return mean_norm_sq, norm_sq_values


if __name__ == "__main__":
    mean_val, all_vals = main()