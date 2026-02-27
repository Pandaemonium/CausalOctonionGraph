"""Tests for RFC-037 Avenue 13 ensemble pipeline."""

import pytest

from calc.weinberg_associator_ensemble import (
    CONDITION_FILE_DEFAULT,
    predeclared_condition_ids,
    run_all,
)


def test_condition_file_location() -> None:
    assert CONDITION_FILE_DEFAULT.exists()
    assert CONDITION_FILE_DEFAULT.name == "weinberg_associator_ensemble_conditions.json"
    assert CONDITION_FILE_DEFAULT.parent.name == "calc"


def test_predeclared_condition_ids() -> None:
    assert predeclared_condition_ids() == [
        "c0_ew_core_associative",
        "c1_mixed_nonassoc_moderate",
        "c2_mixed_nonassoc_heavy",
    ]


def test_run_all_structure() -> None:
    payload = run_all()
    assert payload["rfc"] == "RFC-037"
    assert payload["avenue"] == "A13-ensemble"
    assert payload["ticks"] == 24
    assert len(payload["rows"]) == 3


def test_control_condition_flat() -> None:
    payload = run_all()
    rows = {row["condition_id"]: row for row in payload["rows"]}
    control = rows["c0_ew_core_associative"]["summary"]

    assert control["summary_tickwise_avg"]["delta_sin2_assoc_exclusive"] == pytest.approx(0.0, abs=1e-12)
    assert control["summary_hist_avg"]["delta_sin2_assoc_exclusive"] == pytest.approx(0.0, abs=1e-12)
    assert control["fraction_negative_delta"] == pytest.approx(0.0, abs=1e-12)


def test_mixed_conditions_show_negative_drift() -> None:
    payload = run_all()
    rows = {row["condition_id"]: row for row in payload["rows"]}

    for cid in ("c1_mixed_nonassoc_moderate", "c2_mixed_nonassoc_heavy"):
        s = rows[cid]["summary"]
        assert s["summary_tickwise_avg"]["delta_sin2_assoc_exclusive"] < 0.0
        assert s["summary_hist_avg"]["delta_sin2_assoc_exclusive"] < 0.0
        assert s["fraction_negative_delta"] > 0.5
