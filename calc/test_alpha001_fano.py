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


# ---------------------------------------------------------------------------
# Gate-1 contract tests — required by ALPHA-001 task specification
# ---------------------------------------------------------------------------

# Physics anchor: CODATA 2018 recommended value of the fine-structure constant.
# Source: Mohr, Newell, Taylor, Tiesinga, Rev. Mod. Phys. 93, 025010 (2021).
ALPHA_PDG_CODATA2018 = 1.0 / 137.035999084


def test_fano_line_count_is_callable_and_returns_7() -> None:
    """fano_line_count() must be a callable that returns exactly 7."""
    from calc.alpha_fano import fano_line_count

    result = fano_line_count()
    assert isinstance(result, int), f"expected int, got {type(result)}"
    assert result == 7, f"expected 7, got {result}"


def test_alpha_fano_proxy_is_positive() -> None:
    """alpha_fano_proxy() must return a positive float."""
    from calc.alpha_fano import alpha_fano_proxy

    result = alpha_fano_proxy()
    assert isinstance(result, float), f"expected float, got {type(result)}"
    assert result > 0.0, f"expected positive value, got {result}"


def test_alpha_upper_bound_exceeds_physical_alpha() -> None:
    """alpha_upper_bound() must be strictly greater than CODATA 2018 alpha.

    Physical alpha = 1/137.035999084 ~ 0.007297.
    The Fano proxy v1 = 1/49 ~ 0.02041 satisfies this.
    v2 (1/153 ~ 0.00654) and v3 (1/145 ~ 0.00690) do NOT -- excluded.
    """
    from calc.alpha_fano import alpha_upper_bound

    result = alpha_upper_bound()
    assert result > ALPHA_PDG_CODATA2018, (
        f"alpha_upper_bound()={result:.8f} must exceed "
        f"physical alpha={ALPHA_PDG_CODATA2018:.8f}"
    )