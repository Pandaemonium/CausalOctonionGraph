"""
calc/test_h7_sign.py

Pytest mirror of CausalGraphTheory/H7SignFunction.lean.
Tests the h7_sign function against the canonical oriented Fano triples
from CONVENTIONS.md §2.

Canonical positive triples (1-indexed):
  L1: (1,2,3), L2: (1,4,5), L3: (1,7,6),
  L4: (2,4,6), L5: (2,5,7), L6: (3,4,7), L7: (3,6,5)
"""

# Canonical oriented Fano triples from CONVENTIONS.md §2
# Each (i, j, k) means e_i * e_j = +e_k
FANO_LINES = [
    (1, 2, 3),  # L1
    (1, 4, 5),  # L2
    (1, 7, 6),  # L3
    (2, 4, 6),  # L4
    (2, 5, 7),  # L5
    (3, 4, 7),  # L6
    (3, 6, 5),  # L7
]


def _is_positive_pair(i: int, j: int) -> bool:
    """Check if (i, j) is a positive (cyclic) ordered pair in the Fano lines."""
    for (a, b, c) in FANO_LINES:
        # Direct: (a,b), cyclic: (b,c), (c,a)
        if a == i and b == j:
            return True
        if b == i and c == j:
            return True
        if c == i and a == j:
            return True
    return False


def h7_sign(i: int, j: int) -> int:
    """
    Return the sign of e_i * e_j in the octonion multiplication table.

    Returns:
      +1 if (i, j, ?) is a cyclic pair in the canonical Fano triples
      -1 if (j, i, ?) is a cyclic pair (reversed)
       0 if i == j (or pair not found, treated as error)
    """
    if i == j:
        return 0
    if _is_positive_pair(i, j):
        return 1
    if _is_positive_pair(j, i):
        return -1
    return 0


def _all_ordered_pairs():
    """Generate all 42 ordered distinct pairs from the 7 Fano lines."""
    pairs = []
    for (a, b, c) in FANO_LINES:
        for p, q in [(a, b), (b, a), (b, c), (c, b), (c, a), (a, c)]:
            if (p, q) not in pairs:
                pairs.append((p, q))
    return pairs


def test_h7sign_antisymmetry():
    """sign(i,j) == -sign(j,i) for all 42 ordered distinct pairs from the 7 Fano lines."""
    pairs = _all_ordered_pairs()
    assert len(pairs) == 42, f"Expected 42 ordered pairs, got {len(pairs)}"
    for (i, j) in pairs:
        assert i != j, f"Pair ({i},{j}) should be distinct"
        s_ij = h7_sign(i, j)
        s_ji = h7_sign(j, i)
        assert s_ij == -s_ji, (
            f"Antisymmetry failed: h7_sign({i},{j})={s_ij}, "
            f"h7_sign({j},{i})={s_ji}, expected {s_ij} == -{s_ji}"
        )


def test_h7sign_self_zero():
    """sign(i,i) == 0 for all 7 imaginaries."""
    for i in range(1, 8):
        result = h7_sign(i, i)
        assert result == 0, f"Expected h7_sign({i},{i}) = 0, got {result}"


def test_h7sign_positive_on_canonical():
    """sign(i,j) == +1 for all 7 canonical oriented triples from CONVENTIONS.md §2."""
    for (i, j, k) in FANO_LINES:
        # Direct canonical pair
        result = h7_sign(i, j)
        assert result == 1, (
            f"Expected h7_sign({i},{j}) = +1 (canonical triple ({i},{j},{k})), got {result}"
        )
        # Cyclic rotation 1: (j,k)
        result_jk = h7_sign(j, k)
        assert result_jk == 1, (
            f"Expected h7_sign({j},{k}) = +1 (cyclic from ({i},{j},{k})), got {result_jk}"
        )
        # Cyclic rotation 2: (k,i)
        result_ki = h7_sign(k, i)
        assert result_ki == 1, (
            f"Expected h7_sign({k},{i}) = +1 (cyclic from ({i},{j},{k})), got {result_ki}"
        )


def test_h7sign_covers_all_pairs():
    """Every distinct pair from {1..7} appears with a nonzero sign."""
    nonzero_pairs = set()
    for i in range(1, 8):
        for j in range(1, 8):
            if i != j:
                s = h7_sign(i, j)
                assert s != 0, (
                    f"Expected nonzero sign for distinct pair ({i},{j}), got 0"
                )
                nonzero_pairs.add((min(i, j), max(i, j)))
    # All C(7,2) = 21 unordered pairs should be covered
    assert len(nonzero_pairs) == 21, (
        f"Expected 21 unordered pairs covered, got {len(nonzero_pairs)}"
    )

# Leibniz