"""Governance tests for RFC-029 H2 policy-locked Weinberg ablations."""

from pathlib import Path

import pytest

from calc.weinberg_s4_decomp import (
    POLICY_FILE_DEFAULT,
    predeclared_h2_policy_ids,
    run_h2_ablation,
    run_h2_policy,
    structural_invariants,
)


def test_policy_file_exists() -> None:
    assert POLICY_FILE_DEFAULT.exists()
    assert POLICY_FILE_DEFAULT.name == "weinberg_h2_policies.json"
    assert POLICY_FILE_DEFAULT.parent.name == "calc"


def test_structural_invariants_pinned() -> None:
    inv = structural_invariants()
    assert inv["s4_class_sizes"] == {
        "1^4": 1,
        "2,1,1": 6,
        "2,2": 3,
        "3,1": 8,
        "4": 6,
    }
    assert inv["s4_irrep_dims"] == [1, 1, 2, 3, 3]
    assert inv["s4_subgroup_order_histogram"] == {
        1: 1,
        2: 9,
        3: 4,
        4: 7,
        6: 4,
        8: 3,
        12: 1,
        24: 1,
    }
    assert inv["structural_checksum"] == "155ea4d148067b38355d6d23dff2f635e61ef236fc84468607e0e96632169c83"


def test_predeclared_policy_ids_are_frozen() -> None:
    assert predeclared_h2_policy_ids() == [
        "h2_baseline_half",
        "h2_exclusive_u1_quarter",
        "h2_weak_boost_third",
    ]


def test_unknown_policy_fails() -> None:
    with pytest.raises(KeyError):
        run_h2_policy("unknown_policy")


def test_ablation_runs_all_policies_once() -> None:
    rows = run_h2_ablation()
    assert [r["policy_id"] for r in rows] == predeclared_h2_policy_ids()
    assert len({r["policy_checksum"] for r in rows}) == len(rows)
    assert all(r["target_scale"] == "M_Z" for r in rows)


def test_expected_baseline_values() -> None:
    baseline = run_h2_policy("h2_baseline_half")
    assert baseline["observable"]["sin2_theta_w_obs"] == pytest.approx(0.5, rel=1e-12)

    quarter = run_h2_policy("h2_exclusive_u1_quarter")
    assert quarter["observable"]["sin2_theta_w_obs"] == pytest.approx(0.25, rel=1e-12)

    third = run_h2_policy("h2_weak_boost_third")
    assert third["observable"]["sin2_theta_w_obs"] == pytest.approx(1.0 / 3.0, rel=1e-12)
