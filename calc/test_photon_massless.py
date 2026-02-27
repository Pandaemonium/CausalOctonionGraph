"""
PHOTON-001 Gate 1: Photon masslessness from vacuum orbit structure.

The photon in the COG model corresponds to an excitation that remains
within the associative subalgebra orbit of the vacuum state (e7 axis).
Gate density for a vacuum-orbit excitation = 0.0.

Criterion: photon_motif must be a subset of lines through the vacuum
Fano point (index 6 = e7 in 0-indexed), giving associator = 0.

Conventions (rfc/CONVENTIONS.md s2):
  Seven directed triples (1-indexed basis {e1,...,e7}):
    L1:(1,2,3) L2:(1,4,5) L3:(1,7,6) L4:(2,4,6)
    L5:(2,5,7) L6:(3,4,7) L7:(3,6,5)
  e7 is the vacuum axis (symmetry-breaking direction).
  Lines through e7 (1-indexed): L3=(1,7,6), L5=(2,5,7), L6=(3,4,7).
  VACUUM_FANO_POINT = 6 (0-indexed), corresponding to e7.
"""

# ============================================================
# Octonion multiplication from CONVENTIONS.md s2
# ============================================================

DIRECTED_TRIPLES = [
    (1, 2, 3),   # L1
    (1, 4, 5),   # L2
    (1, 7, 6),   # L3: through e7
    (2, 4, 6),   # L4
    (2, 5, 7),   # L5: through e7
    (3, 4, 7),   # L6: through e7
    (3, 6, 5),   # L7
]


def _build_mult_table(directed_triples):
    """Build octonion multiplication table from directed triples."""
    table = {}
    for i in range(1, 8):
        table[(i, i)] = (-1, 0)
    for (a, b, c) in directed_triples:
        table[(a, b)] = (+1, c)
        table[(b, a)] = (-1, c)
        table[(b, c)] = (+1, a)
        table[(c, b)] = (-1, a)
        table[(c, a)] = (+1, b)
        table[(a, c)] = (-1, b)
    return table


_MULT = _build_mult_table(DIRECTED_TRIPLES)


def oct_mult_basis(i, j):
    """Multiply e_i * e_j for i,j in {0,...,7} (0 = real unit e0=1).
    Returns (sign, index)."""
    if i == 0:
        return (1, j)
    if j == 0:
        return (1, i)
    if i == j:
        return (-1, 0)
    return _MULT[(i, j)]


def associator(a, b, c):
    """Compute [e_a, e_b, e_c] = (e_a*e_b)*e_c - e_a*(e_b*e_c).
    Arguments a,b,c are 1-indexed. Returns dict {index: coeff}."""
    s1, ab = oct_mult_basis(a, b)
    s2, left_idx = oct_mult_basis(ab, c)
    left_sign = s1 * s2
    s3, bc = oct_mult_basis(b, c)
    s4, right_idx = oct_mult_basis(a, bc)
    right_sign = s3 * s4
    coeffs = {}
    coeffs[left_idx] = coeffs.get(left_idx, 0) + left_sign
    coeffs[right_idx] = coeffs.get(right_idx, 0) - right_sign
    return {k: v for k, v in coeffs.items() if v != 0}


def associator_is_zero(a, b, c):
    """Return True iff [e_a, e_b, e_c] = 0 (1-indexed)."""
    return len(associator(a, b, c)) == 0


# ============================================================
# Fano lines and vacuum point (rfc/CONVENTIONS.md s2, s5)
# ============================================================

# VACUUM_FANO_POINT: e7 axis, 0-indexed (e7 in 1-indexed = index 7 -> 0-idx = 6)
VACUUM_FANO_POINT = 6

# Fano lines through e7 (1-indexed triples from CONVENTIONS.md s2):
FANO_LINES_THROUGH_E7_1IDX = [
    (1, 7, 6),   # L3
    (2, 5, 7),   # L5
    (3, 4, 7),   # L6
]

# Same lines in 0-indexed (subtract 1 from each element):
FANO_LINES_THROUGH_VACUUM_0IDX = [
    (0, 6, 5),   # L3: {e1,e7,e6}
    (1, 4, 6),   # L5: {e2,e5,e7}
    (2, 3, 6),   # L6: {e3,e4,e7}
]

# The photon motif: two Fano lines incident to the e7 vacuum point.
photon_motif = [
    FANO_LINES_THROUGH_VACUUM_0IDX[0],   # L3
    FANO_LINES_THROUGH_VACUUM_0IDX[1],   # L5
]


def gate_density_for_motif(motif_0idx):
    """Gate density = 0.0 iff all associators vanish, else 1.0."""
    for line in motif_0idx:
        a, b, c = [x + 1 for x in line]
        if not associator_is_zero(a, b, c):
            return 1.0
    return 0.0


def motif_on_vacuum_orbit(motif_0idx):
    """Return True iff every line in motif passes through VACUUM_FANO_POINT."""
    return all(VACUUM_FANO_POINT in line for line in motif_0idx)


# ============================================================
# Tests
# ============================================================

def test_vacuum_point_is_e7():
    """VACUUM_FANO_POINT = 6 (0-indexed), matching e7 as the vacuum axis."""
    assert VACUUM_FANO_POINT == 6


def test_photon_gate_density_is_zero():
    """Gate density of the photon motif = 0.0.

    The associator [e_a, e_b, e_c] vanishes for every triple on a Fano
    line through the vacuum point e7. Collinear triples generate an
    associative quaternionic subalgebra, so V_photon = 0.
    """
    density = gate_density_for_motif(photon_motif)
    assert density == 0.0, (
        f"Expected photon gate density = 0.0, got {density}. "
        f"Photon motif (0-indexed): {photon_motif}"
    )


def test_photon_motif_on_vacuum_orbit():
    """The photon motif lies on lines incident to the e7 vacuum point.

    Every Fano line in the motif passes through VACUUM_FANO_POINT = 6 (e7),
    confirming the photon is a gauge excitation, not a color excitation.
    """
    assert motif_on_vacuum_orbit(photon_motif), (
        f"Photon motif {photon_motif} does not pass through "
        f"vacuum point {VACUUM_FANO_POINT}."
    )


def test_all_lines_through_vacuum_have_zero_associator():
    """For ALL three Fano lines through e7, the associator vanishes.

    Stronger check: every triple on a line through e7 is associative.
    """
    for line_0idx in FANO_LINES_THROUGH_VACUUM_0IDX:
        a, b, c = [x + 1 for x in line_0idx]
        result = associator(a, b, c)
        assert len(result) == 0, (
            f"Non-zero associator for line {line_0idx} "
            f"(1-indexed: e{a},e{b},e{c}): {result}"
        )


def test_fano_lines_through_e7_count():
    """Exactly 3 Fano lines pass through the vacuum point e7 (PG(2,2))."""
    lines_through_e7 = [line for line in DIRECTED_TRIPLES if 7 in line]
    assert len(lines_through_e7) == 3, (
        f"Expected 3 lines through e7, got {len(lines_through_e7)}: "
        f"{lines_through_e7}"
    )


def test_photon_motif_size():
    """The photon motif contains exactly 2 Fano lines."""
    assert len(photon_motif) == 2


def test_conventions_sign_table_spot_check():
    """Spot-check the multiplication table against CONVENTIONS.md s2."""
    checks = [
        (1, 2, +1, 3),
        (2, 4, +1, 6),
        (3, 4, +1, 7),
        (1, 7, +1, 6),
        (2, 5, +1, 7),
    ]
    for (i, j, expected_sign, expected_k) in checks:
        sign, k = oct_mult_basis(i, j)
        assert (sign, k) == (expected_sign, expected_k), (
            f"e{i}*e{j}: expected ({expected_sign},e{expected_k}), "
            f"got ({sign},e{k})"
        )

if __name__ == "__main__":
    import sys
    tests = [
        test_vacuum_point_is_e7,
        test_photon_gate_density_is_zero,
        test_photon_motif_on_vacuum_orbit,
        test_all_lines_through_vacuum_have_zero_associator,
        test_fano_lines_through_e7_count,
        test_photon_motif_size,
        test_conventions_sign_table_spot_check,
    ]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
        except AssertionError as e:
            print(f"  FAIL  {t.__name__}: {e}")
            failures += 1
    if failures == 0:
        print("\nAll PHOTON-001 Gate 1 tests passed.")
    else:
        print(f"\n{failures} test(s) FAILED.")
        sys.exit(1)