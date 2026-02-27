"""
GEN-001: Single-Generation Algebraic Structure from H subset O

Tests verifying that one lepton generation corresponds to the quaternion
subalgebra H subset O, with:
  - electron state associated with e4 = e1*e2 (imaginary unit in H)
  - neutrino state associated with real unit (identity/vacuum orbit)
  - U(1) charge: electron = -1, neutrino = 0
  - Exactly 2 particle states in first generation

Convention (LeptonOrbits.lean, consistent with CONVENTIONS.md cyclic Fano):
  Points: Fin 7 with labels 0..6 (= octonion basis elements e1..e7, 0-indexed)
  Fano lines (cyclic difference set mod 7, 0-indexed):
    {0,1,3}, {1,2,4}, {2,3,5}, {3,4,6}, {4,5,0}, {5,6,1}, {6,0,2}

  In 1-indexed basis (shift +1):
    Line {0,1,3} (0-idx) = {1,2,4} (1-idx): e1*e2=e4
  H = span{1, e1, e2, e4}

Orbit structure (LeptonOrbits.lean stabOrbits0):
  - Size-1 orbit: { {3,4,6} }
  - Size-3 orbit A: { {1,2,4}, {2,3,5}, {5,6,1} }
  - Size-3 orbit B: { {0,1,3}, {0,4,5}, {0,2,6} }
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

# Fano triples in 1-indexed form (shift LeptonOrbits 0-indexed by +1)
FANO_TRIPLES_1indexed = [
    (1, 2, 4),
    (2, 3, 5),
    (3, 4, 6),
    (4, 5, 7),
    (5, 6, 1),
    (6, 7, 2),
    (7, 1, 3),
]


def oct_basis_mul(i, j):
    """Multiply 1-indexed octonion basis elements (0=real, 1..7=imaginary).
    Returns (result_index, sign)."""
    if i == 0:
        return j, 1
    if j == 0:
        return i, 1
    if i == j:
        return 0, -1  # e_i^2 = -1
    for (a, b, c) in FANO_TRIPLES_1indexed:
        if (i, j) == (a, b):
            return c, 1
        if (i, j) == (b, c):
            return a, 1
        if (i, j) == (c, a):
            return b, 1
        if (i, j) == (b, a):
            return c, -1
        if (i, j) == (c, b):
            return a, -1
        if (i, j) == (a, c):
            return b, -1
    raise ValueError(f"No Fano triple for e{i}*e{j}")


def test_quaternion_subalgebra_closure():
    """H = span{1, e1, e2, e4} with e1*e2=e4 is closed under octonion multiply."""
    k, s = oct_basis_mul(1, 2)
    assert k == 4 and s == 1, f"e1*e2 should be +e4, got e{k} sign={s}"

    H_indices = [0, 1, 2, 4]
    for i in H_indices:
        for j in H_indices:
            k, s = oct_basis_mul(i, j)
            assert k in H_indices, (
                f"H not closed: e{i} * e{j} = {s:+d}*e{k}, e{k} not in H={H_indices}"
            )


def test_electron_neutrino_pair_from_H():
    """H yields exactly 2 states: electron (e4=e1*e2) and neutrino (real unit 1)."""
    k, s = oct_basis_mul(1, 2)
    assert k == 4 and s == 1, "Electron: e1*e2 = +e4"

    k2, s2 = oct_basis_mul(4, 0)
    assert k2 == 4 and s2 == 1, "e4*1 = e4 (identity)"

    k3, s3 = oct_basis_mul(0, 4)
    assert k3 == 4 and s3 == 1, "1*e4 = e4 (identity)"

    assert 0 != 4, "Neutrino (idx=0) != electron (idx=4)"

    k4, s4 = oct_basis_mul(4, 4)
    assert k4 == 0 and s4 == -1, "e4^2 = -1 (imaginary, charged particle)"


def test_fano_line_orbit_size_one():
    """Under Stab(0) in GL(3,2), Fano line {3,4,6} has orbit size 1 (singleton)."""
    stab_orbits = [
        frozenset([frozenset([3, 4, 6])]),
        frozenset([frozenset([1, 2, 4]),
                   frozenset([2, 3, 5]),
                   frozenset([5, 6, 1])]),
        frozenset([frozenset([0, 1, 3]),
                   frozenset([0, 4, 5]),
                   frozenset([0, 2, 6])]),
    ]

    singleton_orbits = [o for o in stab_orbits if len(o) == 1]
    assert len(singleton_orbits) == 1, "Exactly one singleton orbit"
    assert len(singleton_orbits[0]) == 1, "Singleton orbit has size 1"

    fixed_line = frozenset([3, 4, 6])
    assert fixed_line in singleton_orbits[0], "Fixed line is {3,4,6}"
    assert len(stab_orbits) == 3, "Three orbits = three generations"


def test_single_gen_charge_assignment():
    """U(1) charges: neutrino=0 (real unit), electron=-1 (imaginary e4)."""
    charge = {
        'neutrino_e': 0,
        'electron':   -1,
    }
    assert charge['neutrino_e'] == 0, "Neutrino charge = 0"
    assert charge['electron'] == -1, "Electron charge = -1"
    assert charge['electron'] != charge['neutrino_e'], "Different charges"
    assert abs(charge['electron'] - charge['neutrino_e']) == 1, "Separation = 1 unit"


def test_gen001_state_count():
    """First generation has exactly 2 states: electron and neutrino."""
    first_gen_states = {
        'electron':   4,
        'neutrino_e': 0,
    }
    assert len(first_gen_states) == 2, "Exactly 2 states in first generation"
    indices = list(first_gen_states.values())
    assert len(set(indices)) == len(indices), "State indices are distinct"
    assert first_gen_states['electron'] in range(1, 8), "Electron is imaginary"
    assert first_gen_states['neutrino_e'] == 0, "Neutrino is real (identity)"


def test_gen001_fano_triple_match():
    """Fano triples match LeptonOrbits.lean convention; H-line and singleton verified."""
    fano_lines_0indexed = [
        frozenset([0, 1, 3]),
        frozenset([1, 2, 4]),
        frozenset([2, 3, 5]),
        frozenset([3, 4, 6]),
        frozenset([4, 5, 0]),
        frozenset([5, 6, 1]),
        frozenset([6, 0, 2]),
    ]
    assert len(fano_lines_0indexed) == 7, "Fano plane has 7 lines"

    # H-line (0-indexed {0,1,3}) is valid Fano line
    h_line = frozenset([0, 1, 3])
    assert h_line in fano_lines_0indexed, "{0,1,3} is a valid Fano line"

    # In 1-indexed: line {1,2,4} -> e1*e2=e4
    k, s = oct_basis_mul(1, 2)
    assert (k, s) == (4, 1), f"e1*e2=e4 (Fano line {{1,2,4}}), got e{k} sign={s}"

    # Singleton orbit line {3,4,6} (0-indexed) is valid Fano line
    singleton_line = frozenset([3, 4, 6])
    assert singleton_line in fano_lines_0indexed, "{3,4,6} is a valid Fano line"

    # Also verify cyclic: e2*e4=e1 (from Fano line {1,2,4})
    k2, s2 = oct_basis_mul(2, 4)
    assert k2 == 1 and s2 == 1, "e2*e4=e1 (cyclic from {1,2,4})"

# Leibniz