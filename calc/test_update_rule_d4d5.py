"""
Tests for RFC-028 D4 (spawnPredicate) and D5 (piObs) definitions.

These tests verify the Python-level semantics of the spawn predicate
and observable projection, matching the Lean definitions in
CausalGraphTheory/UpdateRule.lean.
"""

import pytest


# ---------------------------------------------------------------------------
# Python implementations mirroring the Lean definitions
# ---------------------------------------------------------------------------

def interaction_fold(psi_list):
    """
    interactionFold: ordered product of ComplexOctonion elements.
    Here represented as integers for simplicity (identity = 1).
    """
    result = 1
    for p in psi_list:
        result = result * p
    return result


def is_energy_exchange_locked(msgs):
    """
    isEnergyExchangeLocked: k > 0 AND interactionFold(msgs) != 1.
    Args:
        msgs: list of psi values (scalars in this test model)
    """
    if len(msgs) == 0:
        return False
    fold_result = interaction_fold(msgs)
    return fold_result != 1


def is_energy_exchange_locked_nodes(u, v):
    """
    isEnergyExchangeLockedNodes: symmetric energy gate for node pair.
    Returns True iff either ordering of [u.psi, v.psi] is non-trivial.
    """
    return (is_energy_exchange_locked([u['psi'], v['psi']]) or
            is_energy_exchange_locked([v['psi'], u['psi']]))


def spawn_predicate(u, v):
    """
    spawnPredicate u v (RFC-028 D4):
    True iff:
    1. isEnergyExchangeLockedNodes u v  (D3 gate open, symmetric)
    2. u.colorLabel != v.colorLabel      (distinct Fano lines)
    3. u.tickCount == v.tickCount        (synchronous tick)
    """
    energy_ok = is_energy_exchange_locked_nodes(u, v)
    color_distinct = u['color_label'] != v['color_label']
    tick_sync = u['tick_count'] == v['tick_count']
    return energy_ok and color_distinct and tick_sync


def pi_obs(s):
    """
    piObs (RFC-028 D5): projects NodeStateV2 onto ZMod 7 scalar.
    Returns s.colorLabel.val as an integer in [0, 6].
    """
    return s['color_label'] % 7


def make_node(node_id, psi, color_label, tick_count, topo_depth=0):
    """Helper to construct a node state dict."""
    assert 0 <= color_label < 7, f"colorLabel must be in [0,6], got {color_label}"
    return {
        'node_id': node_id,
        'psi': psi,
        'color_label': color_label,
        'tick_count': tick_count,
        'topo_depth': topo_depth,
    }


# ---------------------------------------------------------------------------
# Test 1: Same colorLabel → spawnPredicate = False
# ---------------------------------------------------------------------------

def test_same_color_label_no_spawn():
    """
    Two nodes with the same colorLabel cannot spawn a child,
    regardless of energy or tick state.
    """
    u = make_node(0, psi=2, color_label=3, tick_count=5)
    v = make_node(1, psi=3, color_label=3, tick_count=5)  # same color
    result = spawn_predicate(u, v)
    assert result is False, (
        f"Expected spawnPredicate=False for same colorLabel, got {result}"
    )


def test_same_color_label_no_spawn_even_with_energy():
    """
    Even when k > 0 and fold ≠ 1, same colorLabel blocks spawning.
    """
    # psi=2 so fold([2,2])=4 ≠ 1, k=2 > 0, but color is same
    u = make_node(0, psi=2, color_label=0, tick_count=10)
    v = make_node(1, psi=2, color_label=0, tick_count=10)
    assert spawn_predicate(u, v) is False


# ---------------------------------------------------------------------------
# Test 2: Different colorLabels, same tick, k > 0 → spawnPredicate = True
# ---------------------------------------------------------------------------

def test_different_color_same_tick_spawn():
    """
    Two nodes with different colorLabels, same tick, and non-trivial
    energy exchange (k > 0, fold ≠ 1) should spawn a child.
    """
    # psi=2, so fold([2,3]) = 6 ≠ 1 → energy gate passes
    u = make_node(0, psi=2, color_label=1, tick_count=7)
    v = make_node(1, psi=3, color_label=4, tick_count=7)
    result = spawn_predicate(u, v)
    assert result is True, (
        f"Expected spawnPredicate=True for distinct color, same tick, k>0, got {result}"
    )


def test_different_tick_no_spawn():
    """
    Two nodes with different tickCounts cannot spawn (async ticks).
    """
    u = make_node(0, psi=2, color_label=1, tick_count=5)
    v = make_node(1, psi=3, color_label=4, tick_count=6)  # different tick
    assert spawn_predicate(u, v) is False, (
        "Expected spawnPredicate=False for different tickCounts"
    )


# ---------------------------------------------------------------------------
# Test 3: piObs returns value in 0..6
# ---------------------------------------------------------------------------

def test_pi_obs_range():
    """piObs must return a value in [0, 6] for all valid colorLabels."""
    for color in range(7):
        s = make_node(0, psi=1, color_label=color, tick_count=0)
        obs = pi_obs(s)
        assert 0 <= obs < 7, f"piObs out of range for colorLabel={color}: got {obs}"


def test_pi_obs_specific_values():
    """piObs returns exactly the colorLabel value (as ZMod 7)."""
    for color in range(7):
        s = make_node(0, psi=1, color_label=color, tick_count=0)
        assert pi_obs(s) == color, f"piObs({color}) should be {color}"


# ---------------------------------------------------------------------------
# Test 4: D4 symmetry — spawn(u, v) == spawn(v, u)
# ---------------------------------------------------------------------------

def test_spawn_predicate_symmetry_same_color():
    """Symmetry holds when same color (both False)."""
    u = make_node(0, psi=3, color_label=2, tick_count=4)
    v = make_node(1, psi=5, color_label=2, tick_count=4)
    assert spawn_predicate(u, v) == spawn_predicate(v, u)


def test_spawn_predicate_symmetry_different_color():
    """Symmetry holds when different color and same tick."""
    u = make_node(0, psi=2, color_label=0, tick_count=3)
    v = make_node(1, psi=3, color_label=5, tick_count=3)
    assert spawn_predicate(u, v) == spawn_predicate(v, u), (
        "spawnPredicate must be symmetric"
    )


def test_spawn_predicate_symmetry_energy_zero():
    """Symmetry holds when energy gate fails (psi=1, fold=1)."""
    u = make_node(0, psi=1, color_label=1, tick_count=2)
    v = make_node(1, psi=1, color_label=3, tick_count=2)
    # fold([1, 1]) = 1 → energy gate fails
    assert spawn_predicate(u, v) == spawn_predicate(v, u)
    assert spawn_predicate(u, v) is False


def test_spawn_predicate_symmetry_all_conditions_true():
    """Exhaustive symmetry check over small parameter space."""
    colors = list(range(7))
    ticks = [0, 1, 5]
    psi_vals = [1, 2, 3]
    failures = []
    for c1 in colors:
        for c2 in colors:
            for t in ticks:
                for p1 in psi_vals:
                    for p2 in psi_vals:
                        u = make_node(0, psi=p1, color_label=c1, tick_count=t)
                        v = make_node(1, psi=p2, color_label=c2, tick_count=t)
                        if spawn_predicate(u, v) != spawn_predicate(v, u):
                            failures.append((c1, c2, t, p1, p2))
    assert len(failures) == 0, f"Symmetry violations: {failures}"


# ---------------------------------------------------------------------------
# Test 5: piObs is deterministic
# ---------------------------------------------------------------------------

def test_pi_obs_deterministic():
    """piObs is a pure function: same input → same output."""
    s = make_node(42, psi=99, color_label=5, tick_count=100)
    result1 = pi_obs(s)
    result2 = pi_obs(s)
    assert result1 == result2, "piObs must be deterministic"


def test_pi_obs_deterministic_all_colors():
    """piObs is deterministic for every color class."""
    for color in range(7):
        s = make_node(0, psi=7, color_label=color, tick_count=42)
        assert pi_obs(s) == pi_obs(s)


def test_pi_obs_independent_of_other_fields():
    """piObs depends only on colorLabel, not nodeId, psi, tick, or depth."""
    color = 3
    results = set()
    for node_id in [0, 1, 999]:
        for psi in [1, 2, 100]:
            for tick in [0, 1, 50]:
                for depth in [0, 1, 10]:
                    s = make_node(node_id, psi=psi, color_label=color,
                                  tick_count=tick, topo_depth=depth)
                    results.add(pi_obs(s))
    assert results == {color}, (
        f"piObs should always return {color} for colorLabel={color}, got {results}"
    )


# ---------------------------------------------------------------------------
# Test 6: Energy gate (D3) correctly blocks spawn when k=0
# ---------------------------------------------------------------------------

def test_energy_gate_k0_no_spawn():
    """
    When the message list is empty (k=0), isEnergyExchangeLocked = False,
    so spawnPredicate must be False.
    """
    # psi=1 means fold([1,1])=1, energy gate fails
    u = make_node(0, psi=1, color_label=1, tick_count=5)
    v = make_node(1, psi=1, color_label=3, tick_count=5)
    assert is_energy_exchange_locked([]) is False
    assert is_energy_exchange_locked([1, 1]) is False  # fold = 1
    # With psi=1, fold=1, energy gate blocked
    assert spawn_predicate(u, v) is False


def test_energy_gate_non_identity_allows_spawn():
    """
    When fold(msgs) ≠ 1 and k > 0, energy gate passes.
    """
    msgs = [2, 3]  # fold = 6 ≠ 1
    assert is_energy_exchange_locked(msgs) is True


# ---------------------------------------------------------------------------
# Run directly
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    pytest.main([__file__, "-v"])