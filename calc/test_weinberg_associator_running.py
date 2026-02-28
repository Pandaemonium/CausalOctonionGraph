"""Tests for RFC-037 Avenue 13 empirical associator-running."""

import pytest

from calc.weinberg_associator_running import (
    POLICY_FILE_DEFAULT,
    _parse_policies,
    associator,
    e_basis,
    load_policy_bundle,
    predeclared_policy_ids,
    run_all,
    simulate_policy,
)


def test_policy_file_location() -> None:
    assert POLICY_FILE_DEFAULT.exists()
    assert POLICY_FILE_DEFAULT.name == "weinberg_associator_policies.json"
    assert POLICY_FILE_DEFAULT.parent.name == "calc"


def test_predeclared_policy_ids() -> None:
    assert predeclared_policy_ids() == [
        "a13_associative_control_rollout",
        "a13_mixed_nonassoc_rollout",
    ]


def test_associator_sanity_examples() -> None:
    # Associative-control triple: zero associator
    A0 = associator(e_basis(1), e_basis(6), e_basis(7))
    assert not A0.any()
    # Non-associative triple: nonzero associator
    A1 = associator(e_basis(2), e_basis(4), e_basis(7))
    assert A1.any()


def test_control_vs_mixed_seq_signature() -> None:
    payload = run_all()
    assert payload["observable_bounds"] == {"sin2_min": 0.0, "sin2_max": 0.5}
    rows = {row["policy_id"]: row for row in payload["rows"]}

    control = rows["a13_associative_control_rollout"]["summary_seq"]
    mixed = rows["a13_mixed_nonassoc_rollout"]["summary_seq"]

    assert control["changed_sin2_assoc_exclusive"] is False
    assert control["delta_sin2_assoc_exclusive"] == pytest.approx(0.0, abs=1e-12)

    assert mixed["changed_sin2_assoc_exclusive"] is True
    assert mixed["nonincreasing_sin2_assoc_exclusive"] is True
    assert mixed["delta_sin2_assoc_exclusive"] < 0.0


def test_empirical_frequency_reconstruction_tracks_direction() -> None:
    payload = run_all()
    rows = {row["policy_id"]: row for row in payload["rows"]}
    control = rows["a13_associative_control_rollout"]["summary_empirical_avg"]
    mixed = rows["a13_mixed_nonassoc_rollout"]["summary_empirical_avg"]

    assert control["delta_sin2_assoc_exclusive"] == pytest.approx(0.0, abs=1e-12)
    assert mixed["delta_sin2_assoc_exclusive"] < 0.0


def test_basis_selector_perturbation_on_mixed_policy() -> None:
    bundle = load_policy_bundle()
    policies = {p.policy_id: p for p in _parse_policies(bundle)}
    mixed = policies["a13_mixed_nonassoc_rollout"]

    for selector in ("imag_abs_argmax", "imag_pos_argmax", "imag_signed_argmax"):
        row = simulate_policy(mixed, ticks=int(bundle["ticks"]), basis_selector_override=selector)
        assert row["summary_seq"]["delta_sin2_assoc_exclusive"] < 0.0


def test_source_order_perturbation_on_mixed_policy() -> None:
    bundle = load_policy_bundle()
    policies = {p.policy_id: p for p in _parse_policies(bundle)}
    mixed = policies["a13_mixed_nonassoc_rollout"]

    asc = simulate_policy(mixed, ticks=int(bundle["ticks"]), source_order_override="asc")
    desc = simulate_policy(mixed, ticks=int(bundle["ticks"]), source_order_override="desc")

    assert asc["summary_seq"]["delta_sin2_assoc_exclusive"] < 0.0
    assert desc["summary_seq"]["delta_sin2_assoc_exclusive"] < 0.0


def test_all_series_values_stay_in_preregistered_bounds() -> None:
    payload = run_all()
    lo = float(payload["observable_bounds"]["sin2_min"])
    hi = float(payload["observable_bounds"]["sin2_max"])
    for row in payload["rows"]:
        for series_name in ("series_seq", "series_empirical_avg"):
            for point in row[series_name]:
                assert lo <= float(point["sin2_assoc_exclusive"]) <= hi
                assert lo <= float(point["sin2_assoc_inclusive"]) <= hi
