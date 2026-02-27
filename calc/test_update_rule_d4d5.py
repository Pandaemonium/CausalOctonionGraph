"""
Tests for canonical RFC-028 D4/D5 behavior.

D4 (canonical): static-cone profile, no spawning.
D5: interaction-observation identity at kernel level; projection profiles only
choose which already-observed fields are exported.
"""

import pytest


def interaction_fold(msgs):
    """Ordered multiplicative fold with identity 1."""
    out = 1
    for m in msgs:
        out *= m
    return out


def is_energy_exchange_locked(msgs):
    """D3 lock: non-empty boundary and non-identity folded interaction."""
    return len(msgs) > 0 and interaction_fold(msgs) != 1


def interaction_observed(msgs):
    """Kernel-level D5 identity: every non-trivial interaction is observation."""
    return is_energy_exchange_locked(msgs)


def should_spawn_canonical_no_spawn(_parent, _msgs):
    """D4 canonical profile: never spawn during evolution."""
    return False


def apply_spawn_canonical_no_spawn(ms, _parent, _msgs):
    """D4 canonical profile transition: identity map on microstate."""
    return ms


def make_node(node_id, tick_count, topo_depth, u1_charge, u1_sector=None):
    return {
        "node_id": node_id,
        "tick_count": tick_count,
        "topo_depth": topo_depth,
        "u1_charge": u1_charge,
        "u1_sector": u1_sector,
    }


def phi4(node):
    return node["tick_count"] % 4


def sort_nodes_by_id(nodes):
    return sorted(nodes, key=lambda n: n["node_id"])


def pi_obs_node_minimal(node):
    return {
        "node_id": node["node_id"],
        "u1_charge": node["u1_charge"],
        "phase4": phi4(node),
        "topo_depth": node["topo_depth"],
        "u1_sector": None,
    }


def pi_obs_node_with_sector(node):
    out = pi_obs_node_minimal(node)
    out["u1_sector"] = node["u1_sector"]
    return out


def pi_obs_minimal(ms):
    return {"nodes": [pi_obs_node_minimal(n) for n in sort_nodes_by_id(ms["nodes"])]}


def pi_obs_with_sector(ms):
    return {"nodes": [pi_obs_node_with_sector(n) for n in sort_nodes_by_id(ms["nodes"])]}


def obs_equivalent(pi_obs, m1, m2):
    return pi_obs(m1) == pi_obs(m2)


def make_microstate(nodes):
    return {
        "nodes": nodes,
        "pending_msgs": [],
        "pending_edges": [],
        "next_node_id": max([n["node_id"] for n in nodes], default=-1) + 1,
    }


def test_d4_no_spawn_is_uniformly_false():
    parent = {"node_id": 3}
    assert should_spawn_canonical_no_spawn(parent, []) is False
    assert should_spawn_canonical_no_spawn(parent, [2, 3]) is False
    assert should_spawn_canonical_no_spawn(parent, [1, 1, 1]) is False


def test_d4_apply_spawn_is_identity():
    ms = make_microstate([make_node(0, 0, 0, 0), make_node(1, 2, 1, -1)])
    parent = ms["nodes"][0]
    out = apply_spawn_canonical_no_spawn(ms, parent, [2, 3])
    assert out is ms
    assert out == ms


def test_d5_interaction_observed_matches_energy_exchange():
    cases = [
        [],
        [1],
        [1, 1],
        [2],
        [2, 3],
        [-1, -1],
    ]
    for msgs in cases:
        assert interaction_observed(msgs) == is_energy_exchange_locked(msgs)


def test_d5_identity_payload_is_not_observed_as_exchange():
    assert interaction_observed([1]) is False
    assert interaction_observed([1, 1, 1]) is False


def test_pi_obs_minimal_sorts_by_node_id():
    ms = make_microstate(
        [
            make_node(7, 3, 2, -1),
            make_node(2, 1, 1, 0),
            make_node(5, 8, 3, 1),
        ]
    )
    out = pi_obs_minimal(ms)
    assert [n["node_id"] for n in out["nodes"]] == [2, 5, 7]


def test_pi_obs_minimal_hides_sector():
    ms = make_microstate([make_node(1, 5, 2, -1, u1_sector=[1, 0, 0, 0, 0, 0, 0, 0])])
    out = pi_obs_minimal(ms)
    assert out["nodes"][0]["u1_sector"] is None


def test_pi_obs_with_sector_exposes_sector():
    sector = [1, 0, 0, 0, 0, 0, 0, 0]
    ms = make_microstate([make_node(1, 5, 2, -1, u1_sector=sector)])
    out = pi_obs_with_sector(ms)
    assert out["nodes"][0]["u1_sector"] == sector


def test_pi_obs_minimal_permutation_invariant():
    n1 = make_node(1, 1, 2, -1)
    n2 = make_node(2, 2, 3, 1)
    m1 = make_microstate([n1, n2])
    m2 = make_microstate([n2, n1])
    assert obs_equivalent(pi_obs_minimal, m1, m2) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
