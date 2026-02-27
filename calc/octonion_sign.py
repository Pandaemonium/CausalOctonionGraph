"""Primitive-2 sign table for octonion multiplication (H7 mode)."""

from __future__ import annotations

from typing import Dict, List, Tuple

FANO_LINES: List[Tuple[int, int, int]] = [
    (1, 2, 3),
    (1, 4, 5),
    (1, 7, 6),
    (2, 4, 6),
    (2, 5, 7),
    (3, 4, 7),
    (3, 6, 5),
]

INDEX_TABLE: Dict[Tuple[int, int], int] = {
    (i, j): i ^ j for i in range(1, 8) for j in range(1, 8) if i != j
}


def _sign_map() -> Dict[Tuple[int, int], int]:
    mapping: Dict[Tuple[int, int], int] = {}
    for a, b, c in FANO_LINES:
        mapping[(a, b)] = 1
        mapping[(b, c)] = 1
        mapping[(c, a)] = 1
        mapping[(b, a)] = -1
        mapping[(c, b)] = -1
        mapping[(a, c)] = -1
    return mapping


def sign(i: int, j: int) -> int:
    """
    Return +1 or -1 for e_i * e_j = sign(i,j) * e_{i^j}.
    i, j in {1,...,7}, i != j.
    Raises ValueError for i == j or i,j == 0.
    Derived from FANO_LINES orientation per CONVENTIONS.md §2.
    """
    if i == 0 or j == 0:
        raise ValueError("sign is only defined for imaginary units e1..e7")
    if i == j:
        raise ValueError("sign is undefined for i == j")
    if not (1 <= i <= 7 and 1 <= j <= 7):
        raise ValueError("indices must be in 1..7")
    mapping = _sign_map()
    try:
        return mapping[(i, j)]
    except KeyError as exc:
        raise ValueError(f"pair ({i}, {j}) is not on a Fano line") from exc


def octonion_product(i: int, j: int) -> tuple[int, int]:
    """
    Return (k, s) where e_i * e_j = s * e_k.
    k = i ^ j (Primitive-1), s = sign(i,j) (Primitive-2).
    Handles i == j -> returns (0, 1) [e_i^2 = -e_0 = -1 convention].
    """
    if i == j:
        return (0, 1)
    return (i ^ j, sign(i, j))


def sign_table() -> dict[tuple[int, int], int]:
    """Return the full 7x7 sign table (excluding diagonal) as a dict."""
    return {(i, j): sign(i, j) for i in range(1, 8) for j in range(1, 8) if i != j}


# Gauss