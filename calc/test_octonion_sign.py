"""Tests for canonical octonion sign table (Primitive-2)."""

from __future__ import annotations

from calc.octonion_sign import FANO_LINES, INDEX_TABLE, octonion_product, sign, sign_table

EXPECTED_FANO_LINES = [
    (1, 2, 3),
    (1, 4, 5),
    (1, 7, 6),
    (2, 4, 6),
    (2, 5, 7),
    (3, 4, 7),
    (3, 6, 5),
]


def multiply_basis(i: int, j: int) -> int:
    """Return signed basis index as integer (negative = -e_k)."""
    if i == 0:
        return j
    if j == 0:
        return i
    if i == j:
        return 0
    k, s = octonion_product(i, j)
    return s * k


def test_fano_lines_count() -> None:
    assert len(FANO_LINES) == 7


def test_fano_lines_match_conventions() -> None:
    assert FANO_LINES == EXPECTED_FANO_LINES


def test_index_is_xor() -> None:
    for i in range(1, 8):
        for j in range(1, 8):
            if i == j:
                continue
            assert INDEX_TABLE[(i, j)] == (i ^ j)
            assert 1 <= INDEX_TABLE[(i, j)] <= 7


def test_sign_returns_plus_or_minus_one() -> None:
    for i in range(1, 8):
        for j in range(1, 8):
            if i == j:
                continue
            assert sign(i, j) in {1, -1}


def test_sign_antisymmetry() -> None:
    for i in range(1, 8):
        for j in range(1, 8):
            if i == j:
                continue
            assert sign(i, j) == -sign(j, i)


def test_sign_cyclic_on_fano_lines() -> None:
    for a, b, c in FANO_LINES:
        assert sign(a, b) == 1
        assert sign(b, c) == 1
        assert sign(a, c) == -1


def test_octonion_product_index() -> None:
    for i in range(1, 8):
        for j in range(1, 8):
            if i == j:
                continue
            assert octonion_product(i, j)[0] == (i ^ j)


def test_octonion_product_associator_spot_check() -> None:
    triples = [
        (1, 2, 4),
        (1, 2, 5),
        (2, 3, 4),
    ]
    for a, b, c in triples:
        left = multiply_basis(a, multiply_basis(b, c))
        right = multiply_basis(multiply_basis(a, b), c)
        assert left != right


def test_sign_table_completeness() -> None:
    assert len(sign_table()) == 42


def test_no_sign_ambiguity() -> None:
    for a, b, c in FANO_LINES:
        assert sign(a, b) * sign(b, c) == sign(a, c) * (-1)


# Gauss