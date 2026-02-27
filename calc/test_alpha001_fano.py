"""Tests for ALPHA-001 Gate 1 proxy formulas."""

from __future__ import annotations

from calc.alpha_fano import (
    FANO_LINES,
    FANO_POINTS,
    G2_ORDER,
    GL32_ORDER,
    POINTS_PER_LINE,
    alpha_pdg,
    alpha_proxy_v1,
    alpha_proxy_v2,
    alpha_proxy_v3,
    best_proxy,
)


def test_alpha_pdg_value() -> None:
    assert abs(alpha_pdg() - 1 / 137.036) < 1e-12


def test_alpha_proxy_v1_range() -> None:
    assert 0.0 < alpha_proxy_v1() < 0.1


def test_alpha_proxy_v2_range() -> None:
    assert 0.0 < alpha_proxy_v2() < 0.1


def test_alpha_proxy_v3_range() -> None:
    assert 0.0 < alpha_proxy_v3() < 0.1


def test_best_proxy_returns_tuple() -> None:
    name, value, error = best_proxy()
    assert isinstance(name, str)
    assert isinstance(value, float)
    assert isinstance(error, float)


def test_best_proxy_error_below_50pct() -> None:
    _, _, error = best_proxy()
    assert error < 0.50


def test_fano_constants_correct() -> None:
    assert FANO_POINTS == 7
    assert FANO_LINES == 7
    assert POINTS_PER_LINE == 3
    assert GL32_ORDER == 168


def test_alpha_proxy_v2_denominator() -> None:
    assert GL32_ORDER - G2_ORDER - 1 == 153

