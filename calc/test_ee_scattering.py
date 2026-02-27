"""
calc/test_ee_scattering.py

Phase 5b — e-e Scattering Distance Test
========================================

Implements a minimal discrete graph distance model for two-electron scattering,
bridging the interaction semantics proved in CausalGraphTheory/TwoNodeSystem.lean
(Phase 5a) with a falsifiable numerical scaffold.

Physical model:
  - graph_distance: discrete causal graph distance = |tick_a - tick_b|
  - coulomb_proxy:  charge_product / dist  (COG Coulomb proxy)
  - ee_trajectory:  two identical-charge nodes repelling (separation grows by 1/tick)

Convention: charge_product = +1 for two electrons (same sign -> repulsion).
FANO_LINES = 7 (from conftest, not redefined here).
"""

import pytest

# ---------------------------------------------------------------------------
# Module-level helper functions
# ---------------------------------------------------------------------------

def graph_distance(tick_a: int, tick_b: int) -> int:
    """
    Discrete causal graph distance = |tick_a - tick_b|.
    This is the number of edges on the shortest path between two nodes
    whose causal positions are tick_a and tick_b.
    """
    return abs(tick_a - tick_b)


def coulomb_proxy(dist: int, charge_product: int = 1) -> float:
    """
    COG Coulomb proxy: charge_product / dist.

    This models the discrete analogue of the Coulomb potential 1/r,
    where r is replaced by the graph distance.

    Raises ValueError if dist == 0 (undefined, analogous to the 1/r singularity).
    """
    if dist == 0:
        raise ValueError("coulomb_proxy is undefined at dist=0 (graph singularity).")
    return charge_product / dist


def ee_trajectory(n_ticks: int, initial_sep: int) -> list:
    """
    Simulate two identical-charge nodes repelling each other for n_ticks steps.

    Each tick: separation increases by 1 (pure repulsion, no binding force).
    The two electrons carry charge_product = +1 (same sign), so they always repel.

    Returns a list of separations at each tick (length = n_ticks + 1, including tick 0).
    """
    separations = []
    sep = initial_sep
    for _ in range(n_ticks + 1):
        separations.append(sep)
        sep += 1
    return separations


# ---------------------------------------------------------------------------
# Required tests (10 total)
# ---------------------------------------------------------------------------

def test_graph_distance_zero_same_tick():
    """Distance from a tick to itself is zero."""
    assert graph_distance(5, 5) == 0
    assert graph_distance(0, 0) == 0


def test_graph_distance_positive():
    """Distance between distinct ticks is positive and symmetric."""
    assert graph_distance(3, 7) == 4
    assert graph_distance(7, 3) == 4
    assert graph_distance(0, 10) == 10


def test_coulomb_proxy_unit_distance():
    """At distance 1, proxy equals charge_product."""
    assert coulomb_proxy(1, charge_product=1) == 1.0
    assert coulomb_proxy(1, charge_product=4) == 4.0


def test_coulomb_proxy_falls_off():
    """Proxy decreases as distance increases (inverse-distance falloff)."""
    assert coulomb_proxy(1) > coulomb_proxy(2)
    assert coulomb_proxy(2) > coulomb_proxy(5)
    assert coulomb_proxy(5) > coulomb_proxy(10)


def test_coulomb_proxy_zero_distance_raises():
    """Proxy raises ValueError at dist=0 (undefined, like 1/r singularity)."""
    with pytest.raises(ValueError):
        coulomb_proxy(0)


def test_ee_trajectory_length():
    """Trajectory list has length n_ticks + 1 (includes tick-0 initial state)."""
    traj = ee_trajectory(n_ticks=10, initial_sep=3)
    assert len(traj) == 11  # ticks 0..10 inclusive

    traj2 = ee_trajectory(n_ticks=0, initial_sep=1)
    assert len(traj2) == 1


def test_ee_trajectory_monotone_increasing():
    """Repulsion: separation never decreases (strictly increases each tick)."""
    traj = ee_trajectory(n_ticks=20, initial_sep=1)
    for i in range(len(traj) - 1):
        assert traj[i + 1] > traj[i], (
            f"Separation decreased at tick {i}: {traj[i]} -> {traj[i+1]}"
        )


def test_ee_trajectory_initial_sep_respected():
    """The first entry in the trajectory equals the requested initial separation."""
    for sep in [1, 3, 7, 42]:
        traj = ee_trajectory(n_ticks=5, initial_sep=sep)
        assert traj[0] == sep, f"Expected initial sep {sep}, got {traj[0]}"


def test_coulomb_proxy_at_tick_10():
    """
    After 10 ticks starting at separation 1, the separation is 11.
    The Coulomb proxy at that distance = 1/11 ~ 0.0909.
    """
    traj = ee_trajectory(n_ticks=10, initial_sep=1)
    sep_at_tick_10 = traj[10]
    assert sep_at_tick_10 == 11
    proxy = coulomb_proxy(sep_at_tick_10, charge_product=1)
    assert abs(proxy - 1.0 / 11.0) < 1e-12


def test_ee_total_work_positive():
    """
    Sum of Coulomb proxy values over a trajectory is positive.

    Physical meaning: the total 'work done' repelling two electrons apart
    is positive (like-charge repulsion requires positive energy expenditure).
    charge_product = +1 for two electrons.
    """
    traj = ee_trajectory(n_ticks=10, initial_sep=1)
    total_work = sum(coulomb_proxy(sep, charge_product=1) for sep in traj)
    assert total_work > 0, f"Expected positive total work, got {total_work}"

# Leibniz