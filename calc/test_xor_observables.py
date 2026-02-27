"""
Tests for calc/xor_observables.py
"""

from __future__ import annotations

from calc.xor_observables import (
    aggregate_ensemble_observables,
    charge_sign_flip_count,
    decode_base8_int,
    pair_kind_transition_count,
    scenario_observables,
    shannon_entropy_from_counts,
    support_variation_count,
)


def _fake_trace():
    return [
        {
            "charge_signs": {"0": -1, "1": 1},
            "supports": {"0": [0, 7], "1": [0, 7]},
            "pair_interaction_kind": "attractive",
        },
        {
            "charge_signs": {"0": 1, "1": 1},
            "supports": {"0": [0, 7], "1": [0, 7]},
            "pair_interaction_kind": "neutral",
        },
        {
            "charge_signs": {"0": 1, "1": -1},
            "supports": {"0": [0, 7], "1": [1, 2, 3]},
            "pair_interaction_kind": "neutral",
        },
    ]


def test_decode_base8_int():
    assert decode_base8_int("0") == 0
    assert decode_base8_int("10") == 8
    assert decode_base8_int("-10") == -8
    assert decode_base8_int("777") == int("777", 8)


def test_entropy_from_counts():
    assert shannon_entropy_from_counts({"a": 0, "b": 0}) == 0.0
    h = shannon_entropy_from_counts({"a": 1, "b": 1})
    assert abs(h - 1.0) < 1e-12


def test_trace_metrics():
    trace = _fake_trace()
    assert charge_sign_flip_count(trace, "0") == 1
    assert charge_sign_flip_count(trace, "1") == 1
    assert support_variation_count(trace, "0") == 1
    assert support_variation_count(trace, "1") == 2
    assert pair_kind_transition_count(trace) == 1


def test_scenario_observables_shape():
    scenario = {
        "scenario_id": "s1",
        "steps": 2,
        "initial_pair_kind": "attractive",
        "pair_kind_counts": {"attractive": 1, "neutral": 2},
        "periods": {"0": 4, "1": None},
        "trace": _fake_trace(),
        "final_step": {"pair_interaction_kind": "neutral"},
    }
    obs = scenario_observables(scenario)
    assert obs["scenario_id"] == "s1"
    assert "pair_kind_entropy_bits" in obs
    assert obs["final_pair_kind"] == "neutral"
    assert set(obs["node_metrics"].keys()) == {"0", "1"}


def test_aggregate_ensemble_observables():
    rows = [
        {"pair_kind_entropy_bits": 1.0, "pair_kind_transition_count": 2, "pair_kind_counts": {"a": 2}},
        {"pair_kind_entropy_bits": 0.0, "pair_kind_transition_count": 0, "pair_kind_counts": {"b": 3}},
    ]
    agg = aggregate_ensemble_observables(rows)
    assert agg["run_count"] == 2
    assert agg["avg_pair_kind_entropy_bits"] == 0.5
    assert agg["avg_pair_kind_transition_count"] == 1.0
    assert agg["pair_kind_counts_total"] == {"a": 2, "b": 3}

