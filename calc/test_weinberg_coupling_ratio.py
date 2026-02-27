"""Tests for RFC-037 Avenue 7 coupling-ratio scaffold."""

import pytest

from calc.weinberg_coupling_ratio import (
    POLICY_FILE_DEFAULT,
    best_row_by_abs_gap,
    locked_discrete_observables,
    observables_checksum,
    predeclared_policy_ids,
    run_all_policies,
    run_policy,
)


def test_policy_file_location() -> None:
    assert POLICY_FILE_DEFAULT.exists()
    assert POLICY_FILE_DEFAULT.name == "weinberg_coupling_policies.json"
    assert POLICY_FILE_DEFAULT.parent.name == "calc"


def test_locked_observables_and_checksum() -> None:
    obs = locked_discrete_observables()
    assert obs == {
        "u1_card": 2,
        "weak_card": 3,
        "ew_card": 4,
        "u1_weak_overlap_card": 1,
        "exclusive_u1_card": 1,
        "weak_exclusive_card": 2,
        "ew_minus_u1_card": 2,
    }
    assert (
        observables_checksum(obs)
        == "b608c67c789a8030ead484e44ddd37c53885940ea54ff399496741065515b839"
    )


def test_predeclared_policy_ids_frozen() -> None:
    assert predeclared_policy_ids() == [
        "a7_baseline_half",
        "a7_exclusive_u1_quarter",
        "a7_overlap_shift_third",
    ]


def test_expected_policy_values() -> None:
    baseline = run_policy("a7_baseline_half")
    assert baseline["sin2_theta_w_obs"] == pytest.approx(0.5, rel=1e-12)

    quarter = run_policy("a7_exclusive_u1_quarter")
    assert quarter["sin2_theta_w_obs"] == pytest.approx(0.25, rel=1e-12)

    third = run_policy("a7_overlap_shift_third")
    assert third["sin2_theta_w_obs"] == pytest.approx(1.0 / 3.0, rel=1e-12)


def test_best_row_is_exclusive_u1_quarter() -> None:
    rows = run_all_policies()
    best = best_row_by_abs_gap(rows)
    assert best is not None
    assert best["policy_id"] == "a7_exclusive_u1_quarter"
