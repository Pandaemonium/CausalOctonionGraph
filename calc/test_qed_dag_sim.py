"""calc/test_qed_dag_sim.py
Goal C Phase 2: Tests for the Architecture A immutable-node causal DAG simulation.

Covers:
  TestCausalGraphInit         -- initial state of graph (10 tests)
  TestSpawnBehavior           -- SPAWN events and spawn_count == D (10 tests)
  TestCeExact                 -- Ce_exact=4 and total_ticks=4*(D+1) (10 tests)
  TestNodeEdgeCounts          -- node_count, edge_count, edge=2*ticks (10 tests)
  TestElectronTrajectory      -- state sequence for E1 and E2 (10 tests)
  TestVacuumTrajectory        -- state/proper_time sequence for vacuum (10 tests)
  TestAbsorptionHistory       -- AbsorptionEvent records (8 tests)
  TestCausalGraphMisc         -- adjacency, trajectories, calibration (8 tests)

Total: 76 tests.
"""

from __future__ import annotations

import numpy as np
import pytest

from calc.qed_ee_sim import E0, E1, E7, OMEGA, VACUUM_ORBIT, oct_mul_full
from calc.qed_dag_sim import (
    CausalGraph,
    Node,
    PhotonEdge,
    simulate_ee_dag,
    run_dag_calibration_check,
)

# ----------------------------------------------------------------
# Shared constants
# ----------------------------------------------------------------

E6 = np.zeros(8, dtype=complex)
E6[6] = 1.0 + 0j

# Expected electron orbit under left-mult by E7 (RFC-013 §4.2)
# +E1 -> -E6 -> -E1 -> +E6 -> +E1  (period 4)
ELECTRON_ORBIT = [E1, -E6, -E1, +E6, E1]

# Vacuum orbit: OMEGA -> -i*OMEGA -> -OMEGA -> +i*OMEGA -> OMEGA
# After 2 simultaneous hits per tick (D=1): alternates -OMEGA, +OMEGA
VACUUM_D1_STATES = [-OMEGA, OMEGA, -OMEGA, OMEGA]

TOL = 1e-10


# ================================================================
# TestCausalGraphInit
# ================================================================

class TestCausalGraphInit:
    """Initial state of a freshly constructed CausalGraph."""

    def test_d0_initial_node_count(self):
        """D=0: two root nodes at initialization."""
        g = CausalGraph(D=0)
        assert g.node_count == 2

    def test_d1_initial_node_count(self):
        """D=1: two root nodes at initialization."""
        g = CausalGraph(D=1)
        assert g.node_count == 2

    def test_initial_edge_count_is_zero(self):
        """No edges before simulation starts."""
        g = CausalGraph(D=2)
        assert g.edge_count == 0

    def test_initial_spawn_count_is_zero(self):
        """No SPAWN events at initialization."""
        g = CausalGraph(D=3)
        assert g.spawn_count == 0

    def test_root_e1_state(self):
        """Root node at pos=0 has state E1."""
        g = CausalGraph(D=0)
        root = g._nodes[0]
        assert np.allclose(root.state, E1, atol=TOL)

    def test_root_e2_state(self):
        """Root node at pos=D+1 has state E1."""
        g = CausalGraph(D=1)
        # pos=D+1=2 is the second root (node_id=1)
        root = g._nodes[1]
        assert np.allclose(root.state, E1, atol=TOL)

    def test_root_proper_time_zero(self):
        """Both root nodes have proper_time=0."""
        g = CausalGraph(D=2)
        assert g._nodes[0].proper_time == 0
        assert g._nodes[1].proper_time == 0

    def test_root_from_spawn_false(self):
        """Root nodes are not SPAWN events."""
        g = CausalGraph(D=1)
        assert g._nodes[0].from_spawn is False
        assert g._nodes[1].from_spawn is False

    def test_root_node_type_electron(self):
        """Root nodes have node_type='electron'."""
        g = CausalGraph(D=0)
        assert g._nodes[0].node_type == 'electron'
        assert g._nodes[1].node_type == 'electron'

    def test_custom_initial_state(self):
        """CausalGraph respects a non-default initial_state."""
        custom = np.zeros(8, dtype=complex)
        custom[2] = 1.0  # e2 basis
        g = CausalGraph(D=0, initial_state=custom)
        assert np.allclose(g._nodes[0].state, custom, atol=TOL)
        assert np.allclose(g._nodes[1].state, custom, atol=TOL)


# ================================================================
# TestSpawnBehavior
# ================================================================

class TestSpawnBehavior:
    """SPAWN events: vacuum positions instantiated on first photon arrival."""

    def test_d0_spawn_count_zero(self):
        """No SPAWN for D=0 (no vacuum positions)."""
        r = simulate_ee_dag(D=0)
        assert r['spawn_count'] == 0

    def test_d1_spawn_count_one(self):
        """Exactly 1 SPAWN for D=1."""
        r = simulate_ee_dag(D=1)
        assert r['spawn_count'] == 1

    def test_d2_spawn_count_two(self):
        """Exactly 2 SPAWNs for D=2."""
        r = simulate_ee_dag(D=2)
        assert r['spawn_count'] == 2

    def test_d3_spawn_count_three(self):
        """Exactly 3 SPAWNs for D=3."""
        r = simulate_ee_dag(D=3)
        assert r['spawn_count'] == 3

    def test_spawn_equals_d_for_range(self):
        """spawn_count == D for D in 0..4."""
        for D in range(5):
            assert simulate_ee_dag(D)['spawn_count'] == D

    def test_d1_spawn_position(self):
        """D=1 SPAWN fires at position 1."""
        r = simulate_ee_dag(D=1)
        assert r['spawn_events'][0]['position'] == 1

    def test_d1_spawn_tick(self):
        """D=1 SPAWN fires at tick 1."""
        r = simulate_ee_dag(D=1)
        assert r['spawn_events'][0]['tick'] == 1

    def test_d2_spawn_positions(self):
        """D=2: SPAWNs at positions 1 and 2."""
        r = simulate_ee_dag(D=2)
        positions = {ev['position'] for ev in r['spawn_events']}
        assert positions == {1, 2}

    def test_d1_first_vacuum_node_from_spawn(self):
        """The first node created at vacuum pos=1 has from_spawn=True."""
        g = CausalGraph(D=1)
        g.simulate()
        traj = g.position_trajectory(1)
        assert traj[0]['from_spawn'] is True

    def test_d1_subsequent_vacuum_nodes_not_from_spawn(self):
        """Subsequent vacuum nodes at pos=1 have from_spawn=False."""
        g = CausalGraph(D=1)
        g.simulate()
        traj = g.position_trajectory(1)
        for entry in traj[1:]:
            assert entry['from_spawn'] is False

    def test_d0_no_nodes_from_spawn(self):
        """D=0: no node has from_spawn=True."""
        g = CausalGraph(D=0)
        g.simulate()
        assert not any(n.from_spawn for n in g._nodes.values())


# ================================================================
# TestCeExact
# ================================================================

class TestCeExact:
    """Ce_exact == 4 and total_ticks == 4*(D+1) for all D."""

    def test_ce_d0(self):
        assert simulate_ee_dag(D=0)['Ce_exact'] == 4

    def test_ce_d1(self):
        assert simulate_ee_dag(D=1)['Ce_exact'] == 4

    def test_ce_d2(self):
        assert simulate_ee_dag(D=2)['Ce_exact'] == 4

    def test_ce_d3(self):
        assert simulate_ee_dag(D=3)['Ce_exact'] == 4

    def test_ce_d4(self):
        assert simulate_ee_dag(D=4)['Ce_exact'] == 4

    def test_total_ticks_d0(self):
        assert simulate_ee_dag(D=0)['total_ticks'] == 4

    def test_total_ticks_d1(self):
        assert simulate_ee_dag(D=1)['total_ticks'] == 8

    def test_total_ticks_d2(self):
        assert simulate_ee_dag(D=2)['total_ticks'] == 12

    def test_total_ticks_d3(self):
        assert simulate_ee_dag(D=3)['total_ticks'] == 16

    def test_tick_per_cycle(self):
        """tick_per_cycle == D+1 for all D in 0..3."""
        for D in range(4):
            r = simulate_ee_dag(D)
            assert r['tick_per_cycle'] == D + 1


# ================================================================
# TestNodeEdgeCounts
# ================================================================

class TestNodeEdgeCounts:
    """node_count, edge_count, and the invariant edge_count == 2*total_ticks."""

    def test_node_count_d0(self):
        assert simulate_ee_dag(D=0)['node_count'] == 10

    def test_node_count_d1(self):
        assert simulate_ee_dag(D=1)['node_count'] == 14

    def test_node_count_d2(self):
        assert simulate_ee_dag(D=2)['node_count'] == 26

    def test_edge_count_d0(self):
        assert simulate_ee_dag(D=0)['edge_count'] == 8

    def test_edge_count_d1(self):
        assert simulate_ee_dag(D=1)['edge_count'] == 16

    def test_edge_count_d2(self):
        assert simulate_ee_dag(D=2)['edge_count'] == 24

    def test_edge_equals_two_times_total_ticks(self):
        """edge_count == 2 * total_ticks for D in 0..3 (2 photons per tick)."""
        for D in range(4):
            r = simulate_ee_dag(D)
            assert r['edge_count'] == 2 * r['total_ticks']

    def test_edge_equals_eight_times_d_plus_one(self):
        """edge_count == 8*(D+1) for D in 0..3."""
        for D in range(4):
            r = simulate_ee_dag(D)
            assert r['edge_count'] == 8 * (D + 1)

    def test_d0_no_vacuum_nodes(self):
        """D=0: no vacuum trajectories."""
        r = simulate_ee_dag(D=0)
        assert r['vacuum_trajectories'] == {}

    def test_d1_vacuum_trajectory_length(self):
        """D=1: 4 event nodes at vacuum pos=1 (one per absorption cycle)."""
        g = CausalGraph(D=1)
        g.simulate()
        # pos=1: trajectory excludes root (no root for vacuum positions).
        traj = g.position_trajectory(1)
        assert len(traj) == 4


# ================================================================
# TestElectronTrajectory
# ================================================================

class TestElectronTrajectory:
    """State sequence for E1 (pos=0) and E2 (pos=D+1)."""

    def _e1_traj(self, D):
        g = CausalGraph(D=D)
        g.simulate()
        return g.position_trajectory(0)

    def test_d0_e1_trajectory_length(self):
        """D=0: E1 trajectory has 5 entries (root + 4 absorptions)."""
        assert len(self._e1_traj(0)) == 5

    def test_d0_e1_root_state(self):
        """D=0: E1 root state is +E1."""
        traj = self._e1_traj(0)
        assert np.allclose(traj[0]['state'], E1, atol=TOL)

    def test_d0_e1_step1_state(self):
        """D=0: E1 after first absorption is -E6."""
        traj = self._e1_traj(0)
        assert np.allclose(traj[1]['state'], -E6, atol=TOL)

    def test_d0_e1_step2_state(self):
        """D=0: E1 after second absorption is -E1."""
        traj = self._e1_traj(0)
        assert np.allclose(traj[2]['state'], -E1, atol=TOL)

    def test_d0_e1_step3_state(self):
        """D=0: E1 after third absorption is +E6."""
        traj = self._e1_traj(0)
        assert np.allclose(traj[3]['state'], E6, atol=TOL)

    def test_d0_e1_step4_state(self):
        """D=0: E1 after fourth absorption returns to +E1."""
        traj = self._e1_traj(0)
        assert np.allclose(traj[4]['state'], E1, atol=TOL)

    def test_d0_e1_proper_times(self):
        """D=0: E1 proper_times are [0, 1, 2, 3, 4]."""
        traj = self._e1_traj(0)
        assert [e['proper_time'] for e in traj] == [0, 1, 2, 3, 4]

    def test_d1_e1_trajectory_length(self):
        """D=1: E1 trajectory has 5 entries (root + 4 absorptions)."""
        assert len(self._e1_traj(1)) == 5

    def test_d1_e1_orbit_matches_left_mult(self):
        """D=1: E1 state at each absorption step matches left-mult orbit."""
        traj = self._e1_traj(1)
        for step, expected in enumerate(ELECTRON_ORBIT):
            assert np.allclose(traj[step]['state'], expected, atol=TOL), \
                f"Step {step}: expected {expected}, got {traj[step]['state']}"

    def test_d1_e2_trajectory_length(self):
        """D=1: E2 trajectory has 5 entries."""
        g = CausalGraph(D=1)
        g.simulate()
        traj = g.position_trajectory(2)
        assert len(traj) == 5


# ================================================================
# TestVacuumTrajectory
# ================================================================

class TestVacuumTrajectory:
    """Vacuum node state sequence and proper_time tracking (D=1)."""

    @pytest.fixture
    def vac_traj_d1(self):
        g = CausalGraph(D=1)
        g.simulate()
        return g.position_trajectory(1)

    def test_d1_vacuum_trajectory_length(self, vac_traj_d1):
        """D=1: vacuum trajectory at pos=1 has exactly 4 entries."""
        assert len(vac_traj_d1) == 4

    def test_d1_vacuum_state_cycle1(self, vac_traj_d1):
        """D=1: vacuum state after tick=1 (2 hits) is -OMEGA."""
        assert np.allclose(vac_traj_d1[0]['state'], -OMEGA, atol=TOL)

    def test_d1_vacuum_state_cycle2(self, vac_traj_d1):
        """D=1: vacuum state after tick=3 (4 hits) is +OMEGA."""
        assert np.allclose(vac_traj_d1[1]['state'], OMEGA, atol=TOL)

    def test_d1_vacuum_state_cycle3(self, vac_traj_d1):
        """D=1: vacuum state after tick=5 (6 hits) is -OMEGA."""
        assert np.allclose(vac_traj_d1[2]['state'], -OMEGA, atol=TOL)

    def test_d1_vacuum_state_cycle4(self, vac_traj_d1):
        """D=1: vacuum state after tick=7 (8 hits) is +OMEGA."""
        assert np.allclose(vac_traj_d1[3]['state'], OMEGA, atol=TOL)

    def test_d1_vacuum_proper_times(self, vac_traj_d1):
        """D=1: vacuum proper_times are [2, 4, 6, 8] (2 hits per tick)."""
        assert [e['proper_time'] for e in vac_traj_d1] == [2, 4, 6, 8]

    def test_d1_vacuum_ticks(self, vac_traj_d1):
        """D=1: vacuum events occur at ticks [1, 3, 5, 7]."""
        assert [e['tick'] for e in vac_traj_d1] == [1, 3, 5, 7]

    def test_d1_first_vacuum_from_spawn(self, vac_traj_d1):
        """D=1: first vacuum node has from_spawn=True."""
        assert vac_traj_d1[0]['from_spawn'] is True

    def test_d1_subsequent_vacuum_not_from_spawn(self, vac_traj_d1):
        """D=1: subsequent vacuum nodes have from_spawn=False."""
        for entry in vac_traj_d1[1:]:
            assert entry['from_spawn'] is False

    def test_vacuum_period_tick_d1(self):
        """D=1: vacuum first returns to OMEGA at tick 4 (cycle 2)."""
        r = simulate_ee_dag(D=1)
        assert r['vacuum_period_tick'] == 4

    def test_vacuum_period_tick_d2(self):
        """D=2: vacuum first returns to OMEGA at tick 6 (cycle 2)."""
        r = simulate_ee_dag(D=2)
        assert r['vacuum_period_tick'] == 6


# ================================================================
# TestAbsorptionHistory
# ================================================================

class TestAbsorptionHistory:
    """AbsorptionEvent records in absorption_history."""

    def test_d0_history_length(self):
        """D=0: absorption_history has 4 entries (one per cycle)."""
        r = simulate_ee_dag(D=0)
        assert len(r['absorption_history']) == 4

    def test_d0_cycle_numbers(self):
        """D=0: cycle numbers are 1, 2, 3, 4."""
        r = simulate_ee_dag(D=0)
        assert [e.cycle for e in r['absorption_history']] == [1, 2, 3, 4]

    def test_d0_tick_numbers(self):
        """D=0: absorption ticks are 1, 2, 3, 4."""
        r = simulate_ee_dag(D=0)
        assert [e.tick for e in r['absorption_history']] == [1, 2, 3, 4]

    def test_d0_final_cycle_e1_at_initial(self):
        """D=0: cycle 4 event has e1_at_initial=True."""
        r = simulate_ee_dag(D=0)
        assert r['absorption_history'][-1].e1_at_initial is True

    def test_d1_history_length(self):
        """D=1: absorption_history has 4 entries."""
        r = simulate_ee_dag(D=1)
        assert len(r['absorption_history']) == 4

    def test_d1_tick_numbers(self):
        """D=1: absorption ticks are 2, 4, 6, 8."""
        r = simulate_ee_dag(D=1)
        assert [e.tick for e in r['absorption_history']] == [2, 4, 6, 8]

    def test_d1_final_cycle_both_at_initial(self):
        """D=1: cycle 4 has both electrons at initial state."""
        r = simulate_ee_dag(D=1)
        last = r['absorption_history'][-1]
        assert last.e1_at_initial is True
        assert last.e2_at_initial is True

    def test_d1_cycle1_vacuum_not_at_initial(self):
        """D=1: cycle 1 vacuum is NOT at OMEGA (it's at -OMEGA)."""
        r = simulate_ee_dag(D=1)
        first = r['absorption_history'][0]
        assert first.vacuum_at_initial is False


# ================================================================
# TestCausalGraphMisc
# ================================================================

class TestCausalGraphMisc:
    """Miscellaneous: adjacency, node_type, calibration, invariants."""

    def test_calibration_all_passed(self):
        """run_dag_calibration_check() passes all checks."""
        result = run_dag_calibration_check()
        assert result['all_passed'] is True

    def test_d0_adjacency_root_e1_has_edges(self):
        """D=0: root E1 (node_id=0) emits at least one outgoing photon."""
        g = CausalGraph(D=0)
        g.simulate()
        adj = g.adjacency()
        assert len(adj[0]) > 0

    def test_d0_no_vacuum_trajectories_key(self):
        """D=0: vacuum_trajectories is an empty dict."""
        r = simulate_ee_dag(D=0)
        assert r['vacuum_trajectories'] == {}

    def test_d1_vacuum_trajectories_has_key_1(self):
        """D=1: vacuum_trajectories has key 1."""
        r = simulate_ee_dag(D=1)
        assert 1 in r['vacuum_trajectories']

    def test_node_state_defensive_copy_on_creation(self):
        """Node stores a defensive copy: mutating the input array does not corrupt it."""
        arr = np.array(E1, dtype=complex)  # mutable array passed in
        g = CausalGraph(D=0, initial_state=arr)
        arr[1] = 42.0 + 0j             # mutate the original input AFTER construction
        # Node should still hold the original E1 value, not 42
        assert np.allclose(g._nodes[0].state, E1, atol=TOL)

    def test_d1_all_electron_nodes_have_correct_type(self):
        """D=1: all nodes at pos=0 and pos=2 have node_type='electron'."""
        g = CausalGraph(D=1)
        g.simulate()
        for pos in [0, 2]:
            for entry in g.position_trajectory(pos):
                assert entry['node_type'] == 'electron'

    def test_d1_all_vacuum_nodes_have_correct_type(self):
        """D=1: all nodes at pos=1 have node_type='vacuum'."""
        g = CausalGraph(D=1)
        g.simulate()
        for entry in g.position_trajectory(1):
            assert entry['node_type'] == 'vacuum'

    def test_simulate_ee_dag_wrapper_matches_causal_graph(self):
        """simulate_ee_dag(D) gives same Ce_exact as CausalGraph(D).simulate()."""
        for D in range(4):
            r1 = simulate_ee_dag(D)
            g = CausalGraph(D)
            r2 = g.simulate()
            assert r1['Ce_exact'] == r2['Ce_exact']
            assert r1['node_count'] == r2['node_count']
            assert r1['edge_count'] == r2['edge_count']
