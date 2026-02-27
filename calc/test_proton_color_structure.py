"""
calc/test_proton_color_structure.py

PROTON-001 Gate 1 — Python verification of non-collinear Fano triple count.

Tests that the 7-point Fano plane (PG(2,2)) has exactly 28 non-collinear
triples, matching the number of non-associative triples in the octonions.

Fano lines follow rfc/CONVENTIONS.md / HydrogenBinding.lean convention.
Using 1-indexed points {1..7}:
  {1,2,4}, {2,3,5}, {3,4,6}, {4,5,7}, {5,6,1}, {6,7,2}, {7,1,3}
(These are the 0-indexed lines (0,1,3),(1,2,4),(2,3,5),(3,4,6),(4,5,0),(5,6,1),(6,0,2)
 shifted by +1 to 1-indexed form.)
"""

import itertools

# Canonical Fano lines (1-indexed points 1..7)
# Matching 0-indexed Lean lines: (0,1,3),(1,2,4),(2,3,5),(3,4,6),(4,5,0),(5,6,1),(6,0,2)
# Shifted to 1-indexed:          {1,2,4},{2,3,5},{3,4,6},{4,5,7},{5,6,1},{6,7,2},{7,1,3}
FANO_LINES = [
    frozenset({1, 2, 4}),
    frozenset({2, 3, 5}),
    frozenset({3, 4, 6}),
    frozenset({4, 5, 7}),
    frozenset({5, 6, 1}),
    frozenset({6, 7, 2}),
    frozenset({7, 1, 3}),
]


def is_collinear(triple, fano_lines) -> bool:
    """Return True if all 3 points in triple lie on a common Fano line."""
    s = frozenset(triple)
    return any(s == line for line in fano_lines)


def enumerate_noncollinear_triples(fano_lines) -> list:
    """Return all 3-element subsets of {1..7} that are NOT collinear."""
    points = list(range(1, 8))
    all_triples = [frozenset(c) for c in itertools.combinations(points, 3)]
    return [t for t in all_triples if not is_collinear(t, fano_lines)]


# ── Tests ──────────────────────────────────────────────────────────────────────

def test_fano_line_count():
    """The Fano plane has exactly 7 lines."""
    assert len(FANO_LINES) == 7


def test_collinear_triple_count():
    """There are exactly 7 collinear triples (one per Fano line)."""
    points = list(range(1, 8))
    all_triples = [frozenset(c) for c in itertools.combinations(points, 3)]
    collinear = [t for t in all_triples if is_collinear(t, FANO_LINES)]
    assert len(collinear) == 7


def test_noncollinear_triple_count():
    """There are exactly 28 non-collinear triples: C(7,3) - 7 = 35 - 7 = 28."""
    result = enumerate_noncollinear_triples(FANO_LINES)
    assert len(result) == 28


def test_proton_coloring_exists():
    """
    The triple {1, 2, 3} is NOT collinear, so it is a valid proton coloring.
    Note: {1,2,3} is not in FANO_LINES (which contains {1,2,4}, not {1,2,3}).
    Verifies that at least one non-collinear triple exists.
    """
    triple = frozenset({1, 2, 3})
    assert not is_collinear(triple, FANO_LINES), \
        "{1,2,3} should not be a Fano line (it is not in the canonical 7 lines)"


def test_each_point_in_triple_distinct():
    """Every non-collinear triple has exactly 3 distinct points."""
    triples = enumerate_noncollinear_triples(FANO_LINES)
    for triple in triples:
        assert len(triple) == 3, f"Triple {triple} does not have 3 distinct points"


def test_28_equals_su3_adjoint_dim():
    """
    The count of non-collinear Fano triples equals 28.
    In the COG model this matches the number of non-associative triples in O:
    C(7,3) - 7 collinear = 35 - 7 = 28.
    This is also dim(so(8)) = 28, connecting quark color to octonionic symmetry.
    """
    noncollinear_count = len(enumerate_noncollinear_triples(FANO_LINES))
    assert noncollinear_count == 28  # COG color configuration count


def test_all_fano_lines_have_three_points():
    """Each Fano line contains exactly 3 points."""
    for line in FANO_LINES:
        assert len(line) == 3, f"Fano line {line} does not have 3 points"


def test_fano_lines_are_distinct():
    """All 7 Fano lines are distinct sets."""
    assert len(set(FANO_LINES)) == 7

# Leibniz