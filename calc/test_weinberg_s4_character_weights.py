"""Tests for calc/weinberg_s4_character_weights.py."""

import pytest

from calc.weinberg_s4_character_weights import (
    S4_CHAR_TABLE,
    class_weight_vector,
    predeclared_character_policies,
    run_scan,
    transform_weight,
    weighted_sum,
)
from calc.weinberg_s4_decomp import s4_conjugacy_class_sizes


def test_char_table_keys() -> None:
    assert set(S4_CHAR_TABLE.keys()) == {
        "chi_trivial",
        "chi_sign",
        "chi_2d",
        "chi_3d_std",
        "chi_3d_twist",
    }


def test_transform_weight() -> None:
    assert transform_weight(-3, "square") == pytest.approx(9.0, rel=1e-12)
    assert transform_weight(-3, "absolute") == pytest.approx(3.0, rel=1e-12)
    with pytest.raises(ValueError):
        transform_weight(1, "bad_transform")


def test_weighted_sum_examples() -> None:
    class_sizes = s4_conjugacy_class_sizes()
    w_sq_2d = class_weight_vector("chi_2d", "square")
    w_sq_3d = class_weight_vector("chi_3d_std", "square")
    assert weighted_sum(class_sizes, w_sq_2d) == pytest.approx(24.0, rel=1e-12)
    assert weighted_sum(class_sizes, w_sq_3d) == pytest.approx(24.0, rel=1e-12)


def test_policy_count() -> None:
    # 2 transforms x 5 u1 irreps x 5 ew irreps
    assert len(predeclared_character_policies()) == 50


def test_run_scan_payload() -> None:
    payload = run_scan()
    assert payload["target_sin2_theta_w"] == pytest.approx(0.23122, rel=1e-12)
    assert len(payload["rows"]) == 50
    best = payload["best_by_abs_gap"]
    assert best is not None
    assert "sin2_theta_w_obs" in best
    assert "gap_from_target" in best

