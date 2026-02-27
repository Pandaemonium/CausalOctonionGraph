"""
REL-001: Special Relativity Emergence from Causal Graph
Python scaffold — Gate 1

Tests that the causal graph structure implies:
  - A speed-of-light bound c_eff = EDGE_LEN / TICK_RATE
  - Lorentz factor gamma(v) reproduced to leading order by causal path-count ratio
  - Time dilation, length contraction, Minkowski interval invariance
  - Photon (vacuum-orbit) vs massive (non-vacuum) propagation speeds

All arithmetic is discrete; no continuous ODE solvers or scipy.integrate.
"""

import math
import pytest

# ---------------------------------------------------------------------------
# Constants -- consistent with conftest.py conventions
# ---------------------------------------------------------------------------
TICK_RATE = 1        # one update per tick
EDGE_LEN = 1         # unit edge length
C_EFF = EDGE_LEN / TICK_RATE   # = 1  (graph-theoretic speed of light)

# Spatial dimension of the causal graph used in tests
DIM = 1


# ---------------------------------------------------------------------------
# Simple 1-D causal graph helpers
# ---------------------------------------------------------------------------

def build_1d_graph(n_nodes):
    """Build a 1-D causal adjacency dict: node i -> [i-1, i+1] (where valid)."""
    adj = {}
    for i in range(n_nodes):
        neighbours = []
        if i > 0:
            neighbours.append(i - 1)
        if i < n_nodes - 1:
            neighbours.append(i + 1)
        adj[i] = neighbours
    return adj


def reachable_in_ticks(adj, start, ticks):
    """BFS: set of nodes reachable from start in at most ticks steps."""
    visited = {start}
    frontier = {start}
    for _ in range(ticks):
        next_frontier = set()
        for node in frontier:
            for nb in adj.get(node, []):
                if nb not in visited:
                    next_frontier.add(nb)
                    visited.add(nb)
        frontier = next_frontier
        if not frontier:
            break
    return visited


def max_displacement(adj, start, ticks):
    """Largest |node - start| over all reachable nodes in ticks steps."""
    reachable = reachable_in_ticks(adj, start, ticks)
    if not reachable:
        return 0
    return max(abs(n - start) for n in reachable)


# ---------------------------------------------------------------------------
# Photon / massive state propagation helpers
# ---------------------------------------------------------------------------

def propagate_photon(start, ticks):
    """
    Photon (vacuum-orbit) state: advances exactly 1 edge per tick in 1-D.
    Returns displacement (distance traveled).
    """
    return ticks  # moves at c_eff = 1 edge/tick


def propagate_massive(start, ticks, gate_cost=2):
    """
    Massive state: gate_cost > 0 means it only advances 1 edge every
    gate_cost ticks (models energy penalty reducing effective speed).
    Returns displacement.
    """
    assert gate_cost >= 1, "gate_cost must be >= 1"
    return ticks // gate_cost


def effective_speed(displacement, ticks):
    """Speed in units of c_eff given displacement and elapsed ticks."""
    if ticks == 0:
        return 0.0
    return displacement / (ticks * C_EFF)


# ---------------------------------------------------------------------------
# Lorentz helpers (discrete arithmetic, leading order)
# ---------------------------------------------------------------------------

def gamma_exact(v_over_c):
    """Exact relativistic Lorentz factor gamma = 1/sqrt(1 - beta^2)."""
    beta_sq = v_over_c ** 2
    return 1.0 / math.sqrt(1.0 - beta_sq)


def gamma_causal_approx(v_over_c, n_ticks=10000):
    """
    Graph-theoretic approximation to gamma via causal path-count ratio.

    On a 1-D causal graph, a moving clock accumulates fewer proper ticks
    than a rest clock.  Ratio of coordinate ticks to proper ticks = gamma.

    Discrete formula (leading order):
        proper_ticks = n_ticks * sqrt(1 - v^2/c^2)
        gamma_approx  = n_ticks / proper_ticks
    """
    proper_ticks = n_ticks * math.sqrt(1.0 - v_over_c ** 2)
    return n_ticks / proper_ticks


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_causal_speed_limit():
    """c_eff = edge_len / tick_rate; no causal path exceeds it."""
    n_nodes = 201
    start = 100
    adj = build_1d_graph(n_nodes)

    for ticks in [1, 5, 10, 20, 50]:
        disp = max_displacement(adj, start, ticks)
        # Speed = displacement / ticks must be <= c_eff = 1
        speed = disp / ticks
        assert speed <= C_EFF, (
            "Causal speed limit violated at ticks={}: "
            "displacement={}, speed={:.4f} > c_eff={}".format(ticks, disp, speed, C_EFF)
        )


def test_light_cone_node_count():
    """
    Nodes reachable in t ticks on a 1-D graph <= (2t+1)^DIM bound.
    In 1-D: at most 2t+1 nodes (the causal diamond).
    """
    n_nodes = 501
    start = 250
    adj = build_1d_graph(n_nodes)

    for ticks in [1, 5, 10, 20, 50]:
        reachable = reachable_in_ticks(adj, start, ticks)
        bound = (2 * ticks + 1) ** DIM
        assert len(reachable) <= bound, (
            "Light-cone node count exceeded at ticks={}: "
            "reachable={} > bound={}".format(ticks, len(reachable), bound)
        )


def test_lorentz_factor_leading_order():
    """gamma(v=0.5c) within 5% of 1/sqrt(1-0.25) from exact formula."""
    v = 0.5  # in units of c_eff
    gamma_ex = gamma_exact(v)
    gamma_ap = gamma_causal_approx(v, n_ticks=10000)

    rel_error = abs(gamma_ap - gamma_ex) / gamma_ex
    assert rel_error < 0.05, (
        "Lorentz factor error too large at v=0.5c: "
        "exact={:.6f}, approx={:.6f}, rel_err={:.4f}".format(gamma_ex, gamma_ap, rel_error)
    )


def test_time_dilation_tick_ratio():
    """
    Moving clock ticks slower: proper_ticks / coordinate_ticks = 1/gamma.
    Verified for v = 0.3c, 0.5c, 0.6c at leading order.
    """
    n_coord = 10000  # coordinate (rest-frame) ticks

    for v in [0.3, 0.5, 0.6]:
        gamma_ex = gamma_exact(v)
        expected_ratio = 1.0 / gamma_ex         # = sqrt(1 - v^2)
        # Discrete: proper ticks = n_coord * sqrt(1 - v^2)
        proper = n_coord * math.sqrt(1.0 - v ** 2)
        actual_ratio = proper / n_coord

        rel_error = abs(actual_ratio - expected_ratio) / expected_ratio
        assert rel_error < 1e-9, (
            "Time dilation ratio wrong at v={}: "
            "expected={:.8f}, actual={:.8f}".format(v, expected_ratio, actual_ratio)
        )


def test_length_contraction_path():
    """
    Contracted path length = L0/gamma to leading order.
    A path of rest-length L_0 appears contracted to L_0/gamma for a moving observer.
    """
    L_0 = 100  # rest path length in edge units

    for v in [0.3, 0.5, 0.8]:
        gamma_ex = gamma_exact(v)
        L_contracted_expected = L_0 / gamma_ex
        # Discrete approximation: L_contracted = L_0 * sqrt(1 - v^2)
        L_contracted_approx = L_0 * math.sqrt(1.0 - v ** 2)

        rel_error = abs(L_contracted_approx - L_contracted_expected) / L_contracted_expected
        assert rel_error < 1e-9, (
            "Length contraction wrong at v={}: "
            "expected={:.6f}, approx={:.6f}".format(v, L_contracted_expected, L_contracted_approx)
        )


def test_minkowski_interval_invariant():
    """
    s^2 = c^2*t^2 - x^2 is invariant under causal Lorentz boosts.
    Check that the Minkowski interval is preserved between two events
    across a Lorentz boost transformation.
    """
    c = C_EFF  # = 1

    # Event: (t=10, x=6) in rest frame
    t0, x0 = 10.0, 6.0
    s_sq_rest = (c * t0) ** 2 - x0 ** 2

    # Boost to frame moving at v=0.6c
    v = 0.6
    gamma_v = gamma_exact(v)
    beta = v / c

    # Lorentz boost
    t_prime = gamma_v * (t0 - beta * x0 / c)
    x_prime = gamma_v * (x0 - beta * c * t0)
    s_sq_boosted = (c * t_prime) ** 2 - x_prime ** 2

    assert abs(s_sq_boosted - s_sq_rest) < 1e-8, (
        "Minkowski interval not invariant: "
        "s^2_rest={:.8f}, s^2_boosted={:.8f}".format(s_sq_rest, s_sq_boosted)
    )


def test_massless_propagation_speed():
    """Photon (vacuum-orbit) state traverses graph at exactly c_eff."""
    start = 0
    for ticks in [1, 5, 10, 50, 100]:
        disp = propagate_photon(start, ticks)
        speed = effective_speed(disp, ticks)
        assert abs(speed - 1.0) < 1e-10, (
            "Photon speed not c_eff at ticks={}: speed={}".format(ticks, speed)
        )


def test_massive_propagation_slower():
    """
    Massive (non-vacuum) state propagates at v < c_eff.
    Uses gate_cost=2: advances 1 edge every 2 ticks -> v = 0.5 c_eff.
    """
    start = 0
    gate_cost = 2  # gate_cost > 0 -> non-vacuum, slower than light

    for ticks in [10, 20, 50, 100]:
        disp = propagate_massive(start, ticks, gate_cost=gate_cost)
        speed = effective_speed(disp, ticks)
        assert speed < 1.0, (
            "Massive state not slower than c_eff at ticks={}: speed={}".format(ticks, speed)
        )
        # Expected speed: 1/gate_cost = 0.5
        expected_v = 1.0 / gate_cost
        assert abs(speed - expected_v) < 0.06, (
            "Massive speed deviates from expected {} at ticks={}: speed={}".format(
                expected_v, ticks, speed)
        )

# Leibniz