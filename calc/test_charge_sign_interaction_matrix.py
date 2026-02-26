"""Tests for calc/charge_sign_interaction_matrix.py."""

import numpy as np

from calc.charge_sign_interaction_matrix import (
    E0,
    benchmark_states,
    build_charge_sign_matrix,
    interaction_fold,
    interaction_kind,
    is_energy_exchange_locked,
    same_u1_charge_sign,
    two_node_round,
    u1_charge,
)

TOL = 1e-10


def test_benchmark_charge_signs():
    states = benchmark_states()
    assert u1_charge(states["electron"]) < -TOL
    assert u1_charge(states["positron_like"]) > TOL
    assert abs(u1_charge(states["vacuum"])) <= TOL


def test_energy_exchange_empty_false():
    assert is_energy_exchange_locked([]) is False


def test_energy_exchange_identity_false():
    assert is_energy_exchange_locked([E0.copy()]) is False


def test_energy_exchange_non_identity_true():
    states = benchmark_states()
    assert is_energy_exchange_locked([states["electron"]]) is True


def test_same_sign_helper():
    states = benchmark_states()
    assert same_u1_charge_sign(states["electron"], states["electron"]) is True
    assert same_u1_charge_sign(states["electron"], states["positron_like"]) is False


def test_interaction_kind_repulsive_for_electron_electron():
    states = benchmark_states()
    assert interaction_kind(states["electron"], states["electron"]) == "repulsive"


def test_interaction_kind_attractive_for_opposite_sign():
    states = benchmark_states()
    assert (
        interaction_kind(states["electron"], states["positron_like"]) == "attractive"
    )
    assert (
        interaction_kind(states["positron_like"], states["electron"]) == "attractive"
    )


def test_interaction_kind_neutral_for_vacuum():
    states = benchmark_states()
    assert interaction_kind(states["electron"], states["vacuum"]) == "neutral"
    assert interaction_kind(states["vacuum"], states["electron"]) == "neutral"


def test_matrix_expected_entries():
    matrix = build_charge_sign_matrix()
    assert matrix["electron"]["electron"] == "repulsive"
    assert matrix["electron"]["positron_like"] == "attractive"
    assert matrix["electron"]["vacuum"] == "neutral"
    assert matrix["vacuum"]["vacuum"] == "neutral"


def test_interaction_fold_singleton_identity():
    states = benchmark_states()
    folded = interaction_fold([states["electron"]])
    assert np.allclose(folded, states["electron"], atol=TOL)


def test_two_node_round_deterministic():
    states = benchmark_states()
    a1, b1 = two_node_round(states["electron"], states["positron_like"])
    a2, b2 = two_node_round(states["electron"], states["positron_like"])
    assert np.allclose(a1, a2, atol=TOL)
    assert np.allclose(b1, b2, atol=TOL)

