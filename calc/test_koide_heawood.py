"""
Tests for KOIDE-HEAWOOD-001 spectral witness.
"""

from __future__ import annotations

import math

import numpy as np

from calc.koide_heawood import (
    build_heawood_adjacency,
    build_incidence_matrix,
    heawood_spectrum,
    koide_heawood_ratio,
    rounded_spectrum_counts,
)


def _approx_count(vals: np.ndarray, target: float, tol: float = 1e-9) -> int:
    return int(np.sum(np.abs(vals - target) <= tol))


def test_incidence_shape_and_degrees() -> None:
    b = build_incidence_matrix()
    assert b.shape == (7, 7)
    # Every point lies on 3 lines; every line has 3 points.
    assert np.all(np.sum(b, axis=0) == 3)
    assert np.all(np.sum(b, axis=1) == 3)


def test_heawood_is_3_regular() -> None:
    a = build_heawood_adjacency()
    assert a.shape == (14, 14)
    deg = np.sum(a, axis=1)
    assert np.all(deg == 3)


def test_point_line_bilinear_identity() -> None:
    b = build_incidence_matrix()
    bbt = b @ b.T
    # For PG(2,2): diagonal=3, off-diagonal=1 => B B^T = 2I + J.
    expected = 2 * np.eye(7, dtype=int) + np.ones((7, 7), dtype=int)
    assert np.array_equal(bbt, expected)


def test_heawood_spectrum_expected_multiplicities() -> None:
    vals = heawood_spectrum()
    sqrt2 = math.sqrt(2.0)

    assert _approx_count(vals, 3.0) == 1
    assert _approx_count(vals, -3.0) == 1
    assert _approx_count(vals, sqrt2) == 6
    assert _approx_count(vals, -sqrt2) == 6

    counts = rounded_spectrum_counts()
    assert counts.get(3.0, 0) == 1
    assert counts.get(-3.0, 0) == 1


def test_secondary_mode_matches_koide_sqrt2() -> None:
    ratio = koide_heawood_ratio()
    assert abs(ratio - math.sqrt(2.0)) < 1e-9
