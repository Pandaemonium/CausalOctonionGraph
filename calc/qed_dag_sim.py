"""calc/qed_dag_sim.py
Goal C Phase 2 -- Architecture A: Immutable-Node Causal DAG

Implements RFC-013 Architecture A (locked decision §8.1):
  * Each photon-absorption event creates a NEW immutable Node.
  * In-place state mutation is forbidden; the full history is retained.
  * Vacuum nodes are created on demand via the SPAWN protocol (RFC-013 §6).
  * The full microstate (all nodes and edges) is preserved for audit.

Topology: E1(pos=0) -- V[0](pos=1) -- ... -- V[D-1](pos=D) -- E2(pos=D+1)

Node types (determined algebraically via Axiom of Identity, RFC-013 §2.3):
  'electron' : positions 0 and D+1; state lives in L1 orbit under L_e7
  'vacuum'   : positions 1..D;  state lives in vacuum idempotent orbit

SPAWN (RFC-013 §6.1):
  When a photon arrives at a vacuum position that has no prior node,
  the vacuum idempotent omega is instantiated as a fresh Node with from_spawn=True.
  spawn_count == D for the symmetric e-e seed topology.

Simultaneous arrivals:
  If n photons arrive at the same position in the same tick, ONE new Node is
  created with L_e7 applied n times to the current state.  proper_time increments
  by n.  Each incoming photon generates one outgoing relay/re-emission.

Key results (all convention-invariant):
  Ce_exact    == 4 for all D >= 0  (matches Phase 1 right-mult baseline)
  total_ticks == 4 * (D + 1)
  spawn_count == D
  node_count: D=0->10, D=1->14, D=2->26
  edge_count: D=0->8,  D=1->16, D=2->24  (= 2 * total_ticks)

References:
  rfc/RFC-013_Algebraic_Vacuum_and_Causal_Spawning.md
  calc/qed_ee_sim.py  (Phase 1 mutable-chain baseline)
  calc/conftest.py    (FANO_SIGN, FANO_THIRD, VACUUM_AXIS -- Furey convention)
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

import numpy as np

from calc.qed_ee_sim import (
    oct_mul_full,
    state_is_vacuum_orbit,
    E1,
    E7,
    OMEGA,
    VACUUM_ORBIT,
    SPAWN,
    AbsorptionEvent,
)


# ================================================================
# Immutable graph primitives
# ================================================================

@dataclass
class Node:
    """Immutable event node in the causal DAG.

    Created once per absorption event; must not be mutated after creation.
    state is stored as a defensive copy (dtype=complex) in __post_init__.
    """
    node_id: int
    state: np.ndarray   # length-8 complex; copy of state at this event
    node_type: str      # 'electron' | 'vacuum'  (Axiom of Identity)
    position: int       # chain position (0 = E1, D+1 = E2, 1..D = vacuum)
    tick: int           # simulation tick at which this node was created
    proper_time: int    # cumulative photon hits at this position (0 for root nodes)
    from_spawn: bool    # True iff this is the first node ever at this position

    def __post_init__(self) -> None:
        # Defensive copy: prevent aliasing to the caller's array.
        self.state = np.array(self.state, dtype=complex)


@dataclass
class PhotonEdge:
    """Directed photon edge in the causal DAG."""
    edge_id: int
    src_node_id: int    # emitter or relay node
    dst_node_id: int    # absorber node
    direction: int      # +1 (E1->E2) or -1 (E2->E1)
    tick_arrival: int   # tick at which this photon arrived at dst


# ================================================================
# CausalGraph: Architecture A DAG
# ================================================================

class CausalGraph:
    """Architecture A immutable-node causal DAG for e-e scattering on a 1D chain.

    Maintains an append-only graph: each photon-absorption event creates a new
    Node; no node is ever deleted or mutated.  Vacuum positions are unpopulated
    until the first photon arrives (SPAWN protocol).

    Usage::

        graph = CausalGraph(D=1)
        result = graph.simulate()
        print(result['Ce_exact'])      # 4
        print(result['node_count'])    # 14
        print(result['spawn_count'])   # 1
    """

    def __init__(self, D: int, initial_state: Optional[np.ndarray] = None) -> None:
        self._D = D
        self._nodes: dict[int, Node] = {}
        self._edges: list[PhotonEdge] = []
        # pos -> node_id of the most recently created node at that position
        self._position_latest: dict[int, int] = {}
        self._node_counter: int = 0
        self._edge_counter: int = 0
        # tick -> list of (target_pos, direction, src_node_id) tuples
        self._pending: defaultdict[int, list] = defaultdict(list)
        # SPAWN event records (populated by _create_node)
        self._spawn_events: list[dict] = []

        # Initial electron state (symmetric: both electrons start identical)
        e_state = E1.copy() if initial_state is None else np.array(initial_state, dtype=complex)
        self._initial_state = e_state.copy()

        # Root nodes (tick=0, proper_time=0, not from SPAWN)
        root_e1 = self._create_node(e_state.copy(), 'electron', 0,     0, 0, False)
        root_e2 = self._create_node(e_state.copy(), 'electron', D + 1, 0, 0, False)

        # Schedule first photon arrivals at tick=1
        if D == 0:
            # Direct: E1's photon -> E2 (pos=D+1); E2's photon -> E1 (pos=0)
            self._pending[1].append((D + 1, +1, root_e1.node_id))
            self._pending[1].append((0,     -1, root_e2.node_id))
        else:
            # Via vacuum: E1's photon -> V[0] (pos=1); E2's photon -> V[D-1] (pos=D)
            self._pending[1].append((1,   +1, root_e1.node_id))
            self._pending[1].append((D,   -1, root_e2.node_id))

    # ----------------------------------------------------------------
    # Internal builders
    # ----------------------------------------------------------------

    def _create_node(
        self,
        state: np.ndarray,
        node_type: str,
        position: int,
        tick: int,
        proper_time: int,
        from_spawn: bool,
    ) -> Node:
        nid = self._node_counter
        self._node_counter += 1
        node = Node(
            node_id=nid,
            state=state,
            node_type=node_type,
            position=position,
            tick=tick,
            proper_time=proper_time,
            from_spawn=from_spawn,
        )
        self._nodes[nid] = node
        self._position_latest[position] = nid
        if from_spawn:
            self._spawn_events.append({
                'node_id': nid,
                'position': position,
                'tick': tick,
            })
        return node

    def _create_edge(
        self,
        src_id: int,
        dst_id: int,
        direction: int,
        tick_arrival: int,
    ) -> PhotonEdge:
        eid = self._edge_counter
        self._edge_counter += 1
        edge = PhotonEdge(
            edge_id=eid,
            src_node_id=src_id,
            dst_node_id=dst_id,
            direction=direction,
            tick_arrival=tick_arrival,
        )
        self._edges.append(edge)
        return edge

    # ----------------------------------------------------------------
    # Simulation step
    # ----------------------------------------------------------------

    def step(self, tick: int) -> bool:
        """Process all photon arrivals scheduled at this tick.

        For each position that receives one or more photons this tick:

        1. Look up the current state at that position (SPAWN -> OMEGA if not present).
        2. Apply L_e7 once per incoming photon (sequential, by alternativity).
        3. Create ONE new immutable Node with the resulting state.
        4. Create PhotonEdge(s) from each source node to the new node.
        5. Schedule relay or re-emission photons.

        Returns True if any events were processed.
        """
        events = self._pending.pop(tick, [])
        if not events:
            return False

        # Group arrivals by target position (deterministic ascending order)
        by_pos: dict[int, list] = defaultdict(list)
        for (tgt_pos, direction, src_id) in events:
            by_pos[tgt_pos].append((direction, src_id))

        for pos in sorted(by_pos.keys()):
            arrivals = by_pos[pos]
            n_hits = len(arrivals)

            # ── determine starting state at this position ──────────────
            if pos in self._position_latest:
                prev_node = self._nodes[self._position_latest[pos]]
                current_state = prev_node.state.copy()
                prev_pt = prev_node.proper_time
                is_spawn = False
            else:
                # SPAWN: first photon at this vacuum position
                current_state = OMEGA.copy()
                prev_pt = 0
                is_spawn = True

            # ── apply L_e7 once per incoming photon ────────────────────
            # By octonion alternativity: (e7*e7)*s = e7*(e7*s) = -s,
            # so sequential application is associative-equivalent here.
            new_state = current_state
            for _ in range(n_hits):
                new_state = oct_mul_full(E7, new_state)

            new_pt = prev_pt + n_hits

            # ── determine node type (Axiom of Identity, RFC-013 §2.3) ──
            if state_is_vacuum_orbit(new_state):
                node_type = 'vacuum'
            else:
                node_type = 'electron'

            # ── create new immutable node ──────────────────────────────
            new_node = self._create_node(new_state, node_type, pos, tick, new_pt, is_spawn)

            # ── create one edge per incoming photon ────────────────────
            for (direction, src_id) in arrivals:
                self._create_edge(src_id, new_node.node_id, direction, tick)

            # ── schedule outgoing photons ──────────────────────────────
            is_electron_pos = (pos == 0 or pos == self._D + 1)
            if is_electron_pos:
                # Electron: re-emit each absorbed photon in the opposite direction
                for (direction, _) in arrivals:
                    out_dir = -direction
                    next_pos = pos + out_dir
                    # Always valid for the symmetric e-e chain
                    self._pending[tick + 1].append((next_pos, out_dir, new_node.node_id))
            else:
                # Vacuum: relay each photon in its original direction
                for (direction, _) in arrivals:
                    next_pos = pos + direction
                    if 0 <= next_pos <= self._D + 1:
                        self._pending[tick + 1].append((next_pos, direction, new_node.node_id))

        return True

    # ----------------------------------------------------------------
    # Properties
    # ----------------------------------------------------------------

    @property
    def spawn_count(self) -> int:
        """Number of SPAWN events (== D for the symmetric e-e chain)."""
        return len(self._spawn_events)

    @property
    def node_count(self) -> int:
        """Total number of nodes in the graph (roots + event nodes)."""
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        """Total number of photon edges in the graph."""
        return len(self._edges)

    # ----------------------------------------------------------------
    # Query helpers
    # ----------------------------------------------------------------

    def position_trajectory(self, position: int) -> list[dict]:
        """Return all nodes at position in chronological order (by tick).

        Each entry is a dict with keys:
          node_id, state (copy), node_type, tick, proper_time, from_spawn.
        """
        nodes_at_pos = [n for n in self._nodes.values() if n.position == position]
        nodes_at_pos.sort(key=lambda n: n.tick)
        return [
            {
                'node_id': n.node_id,
                'state': n.state.copy(),
                'node_type': n.node_type,
                'tick': n.tick,
                'proper_time': n.proper_time,
                'from_spawn': n.from_spawn,
            }
            for n in nodes_at_pos
        ]

    def adjacency(self) -> dict[int, list[int]]:
        """Return adjacency list mapping node_id -> [dst_node_id, ...]."""
        adj: dict[int, list[int]] = {nid: [] for nid in self._nodes}
        for edge in self._edges:
            adj[edge.src_node_id].append(edge.dst_node_id)
        return adj

    # ----------------------------------------------------------------
    # Main simulation driver
    # ----------------------------------------------------------------

    def simulate(self, max_cycles: int = 20) -> dict:
        """Run until both electrons simultaneously return to their initial states.

        Termination: both electrons have equal proper_time AND both states
        match the initial state (np.allclose, atol=1e-10).

        Returns a result dict with keys:
          D, Ce_exact, total_ticks, tick_per_cycle,
          node_count, edge_count, spawn_count, spawn_events,
          absorption_history, electron_trajectory_E1, electron_trajectory_E2,
          vacuum_trajectories, vacuum_period_tick.
        """
        D = self._D
        e1_pos = 0
        e2_pos = D + 1

        absorption_history: list[AbsorptionEvent] = []
        vacuum_period_tick: Optional[int] = None
        max_ticks = max_cycles * (D + 2) + 20

        for t in range(1, max_ticks + 1):
            if not self.step(t):
                continue

            # ── check for joint absorption ─────────────────────────────
            e1_id = self._position_latest.get(e1_pos)
            e2_id = self._position_latest.get(e2_pos)
            if e1_id is None or e2_id is None:
                continue

            e1_node = self._nodes[e1_id]
            e2_node = self._nodes[e2_id]

            # Joint absorption: both electron nodes must have been created THIS tick
            # (proper_time > 0 and equal).  Checking tick == t excludes vacuum-only
            # ticks where electron nodes are unchanged since the last absorption.
            if (
                e1_node.tick != t
                or e2_node.tick != t
                or e1_node.proper_time == 0
                or e1_node.proper_time != e2_node.proper_time
            ):
                continue

            cycle_n = e1_node.proper_time

            # ── snapshot vacuum states ─────────────────────────────────
            vac_states: list = []
            vac_at_init = True
            for vpos in range(1, D + 1):
                vid = self._position_latest.get(vpos)
                if vid is None:
                    vac_at_init = False
                    vac_states.append(None)
                else:
                    vs = self._nodes[vid].state.copy()
                    vac_states.append(vs)
                    if not np.allclose(vs, OMEGA, atol=1e-10):
                        vac_at_init = False

            e1_at_init = np.allclose(e1_node.state, self._initial_state, atol=1e-10)
            e2_at_init = np.allclose(e2_node.state, self._initial_state, atol=1e-10)

            if vacuum_period_tick is None and D > 0 and vac_at_init:
                vacuum_period_tick = t

            absorption_history.append(AbsorptionEvent(
                cycle=cycle_n,
                tick=t,
                e1_state=e1_node.state.copy(),
                e2_state=e2_node.state.copy(),
                vacuum_states=vac_states,
                e1_at_initial=e1_at_init,
                e2_at_initial=e2_at_init,
                vacuum_at_initial=vac_at_init,
            ))

            if e1_at_init and e2_at_init:
                return self._build_result(
                    D, cycle_n, t, absorption_history, vacuum_period_tick
                )

        # Not found within max_ticks
        return self._build_result(D, -1, max_ticks, absorption_history, vacuum_period_tick)

    def _build_result(
        self,
        D: int,
        Ce_exact: int,
        total_ticks: int,
        absorption_history: list,
        vacuum_period_tick: Optional[int],
    ) -> dict:
        return {
            'D': D,
            'Ce_exact': Ce_exact,
            'total_ticks': total_ticks,
            'tick_per_cycle': D + 1,
            'node_count': self.node_count,
            'edge_count': self.edge_count,
            'spawn_count': self.spawn_count,
            'spawn_events': list(self._spawn_events),
            'absorption_history': absorption_history,
            'electron_trajectory_E1': self.position_trajectory(0),
            'electron_trajectory_E2': self.position_trajectory(D + 1),
            'vacuum_trajectories': {
                vpos: self.position_trajectory(vpos)
                for vpos in range(1, D + 1)
            },
            'vacuum_period_tick': vacuum_period_tick,
        }


# ================================================================
# Top-level convenience wrapper
# ================================================================

def simulate_ee_dag(
    D: int,
    max_cycles: int = 20,
    initial_state: Optional[np.ndarray] = None,
) -> dict:
    """Construct a CausalGraph and simulate until both electrons return to initial state.

    Convenience wrapper around CausalGraph(D).simulate().

    Args:
      D:            Number of vacuum nodes (>= 0).
      max_cycles:   Safety limit on absorption cycles.
      initial_state: Initial electron state (default: E1).

    Returns the same dict as CausalGraph.simulate().
    """
    graph = CausalGraph(D, initial_state)
    return graph.simulate(max_cycles)


# ================================================================
# Calibration check
# ================================================================

def run_dag_calibration_check() -> dict:
    """Run all Goal C Phase 2 calibration checks.

    Checks:
      1. ce_D0 : Ce_exact=4, total_ticks=4,  node_count=10, edge_count=8,  spawn=0
      2. ce_D1 : Ce_exact=4, total_ticks=8,  node_count=14, edge_count=16, spawn=1
      3. ce_D2 : Ce_exact=4, total_ticks=12, node_count=26, edge_count=24, spawn=2
      4. spawn : spawn_count == D for D=0,1,2,3
      5. d_independence : Ce_exact == 4 for D=0,1,2,4

    Returns dict with 'checks' and 'all_passed'.
    """
    expected = {
        0: {'Ce': 4, 'ticks': 4,  'nodes': 10, 'edges': 8,  'spawn': 0},
        1: {'Ce': 4, 'ticks': 8,  'nodes': 14, 'edges': 16, 'spawn': 1},
        2: {'Ce': 4, 'ticks': 12, 'nodes': 26, 'edges': 24, 'spawn': 2},
    }
    checks: dict = {}

    for D, exp in expected.items():
        res = simulate_ee_dag(D)
        ok = (
            res['Ce_exact']    == exp['Ce']
            and res['total_ticks'] == exp['ticks']
            and res['node_count']  == exp['nodes']
            and res['edge_count']  == exp['edges']
            and res['spawn_count'] == exp['spawn']
        )
        checks[f'ce_D{D}'] = {
            'D': D,
            'Ce_exact':    res['Ce_exact'],
            'total_ticks': res['total_ticks'],
            'node_count':  res['node_count'],
            'edge_count':  res['edge_count'],
            'spawn_count': res['spawn_count'],
            'expected':    exp,
            'passed':      ok,
        }

    # spawn_count == D for D=0,1,2,3
    spawn_ok = all(simulate_ee_dag(D)['spawn_count'] == D for D in range(4))
    checks['spawn_equals_D'] = {
        'D_values': list(range(4)),
        'passed': spawn_ok,
    }

    # D-independence of Ce_exact
    D_vals = [0, 1, 2, 4]
    Ce_vals = [simulate_ee_dag(D)['Ce_exact'] for D in D_vals]
    d_indep = len(set(Ce_vals)) == 1 and Ce_vals[0] == 4
    checks['d_independence'] = {
        'D_values': D_vals,
        'Ce_exact_values': Ce_vals,
        'passed': d_indep,
    }

    all_passed = all(c['passed'] for c in checks.values())
    return {'checks': checks, 'all_passed': all_passed}


# ================================================================
# Entry point: print calibration report
# ================================================================

if __name__ == '__main__':
    print('=' * 65)
    print('QED E-E DAG Simulation: Goal C Phase 2 (Architecture A)')
    print('=' * 65)

    calib = run_dag_calibration_check()
    for name, check in calib['checks'].items():
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f'  [{status}] {name}')
        if 'Ce_exact' in check:
            exp = check['expected']
            print(
                f'         Ce={check["Ce_exact"]} (exp {exp["Ce"]})'
                f'  ticks={check["total_ticks"]} (exp {exp["ticks"]})'
                f'  nodes={check["node_count"]} (exp {exp["nodes"]})'
                f'  edges={check["edge_count"]} (exp {exp["edges"]})'
                f'  spawn={check["spawn_count"]} (exp {exp["spawn"]})'
            )

    print(f'\nCalibration: all_passed={calib["all_passed"]}')

    # Detailed trajectory for D=1
    print('\n--- D=1 vacuum trajectory (pos=1) ---')
    g = CausalGraph(D=1)
    r = g.simulate()
    for entry in r['vacuum_trajectories'][1]:
        s = entry['state']
        dominant = int(np.argmax(np.abs(s)))
        phase = s[dominant]
        sign = '+' if phase.real > 0 or (phase.real == 0 and phase.imag > 0) else '-'
        spawn_tag = '  [SPAWN]' if entry['from_spawn'] else ''
        print(
            f"  tick={entry['tick']:2d}  pt={entry['proper_time']}  "
            f"state~{sign}omega  {spawn_tag}"
        )
