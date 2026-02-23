"""calc/qed_scatter.py
RFC-012: Two-particle QED vertex simulation in a vacuum lattice.

Two scattering systems:
  System A -- Moller scattering (e- + e-):   vertex cost = 1 tick   (native XOR)
  System B -- e- + mu- scattering:           vertex cost = 15 ticks (14 triality + 1 XOR)

Photon operator: O_gamma = e_7 (state index 7, vacuum axis, U(1)_EM generator).
Vacuum hop cost: 1 tick each (defines c = 1 hop/tick; see RFC-012 sec 4.3 and
Sorkin 2009 arXiv:0910.0673).

Key results:
  N_TAU = 14 = dim(G_2):  proved 2026-02-22 by count_circuit_depth_greedy(H)
                           in calc/triality_map.py (McRae 2025 arXiv:2502.14016, eq 8).
  vertex_cost_ratio = (N_TAU + 1) / 1 = 15:  lower bound on m_mu/m_e.
  Full orbit ratio C_mu/C_e (target ~206.768):  open (LEPTON-001, RFC-012 sec 5.1).

References:
  rfc/RFC-012_QED_Scattering_Graph_Simulation.md  (full spec)
  rfc/CONVENTIONS.md  (locked Fano/Furey convention)
  McRae (2025) arXiv:2502.14016, eq. (8)  --  H matrix
  Sorkin (2009) arXiv:0910.0673  --  c = 1 hop/tick
  calc/triality_map.py  --  count_circuit_depth_greedy(H) = 14
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import Literal, Optional

from calc.conftest import FANO_SIGN, FANO_THIRD, VACUUM_AXIS


# ================================================================
# Constants
# ================================================================

N_TAU: int = 14
"""Circuit depth of McRae H matrix = dim(G_2).
Proved 2026-02-22 by count_circuit_depth_greedy(H) in calc/triality_map.py.
Breakdown: 4 shift ticks + 2 intermediate ticks + 8 summation ticks = 14.
"""

# McRae (2025) arXiv:2502.14016, eq. (8): 4x4 Euclidean triality quartet matrix.
# Properties: H^3 = I_4, H^T H = I_4 (order-3 orthogonal matrix).
# count_circuit_depth_greedy(H) = 14 = dim(G_2).
MCRAE_H: np.ndarray = np.array([
    [-1, -1,  1,  1],
    [ 1,  1,  1,  1],
    [-1,  1,  1, -1],
    [-1,  1, -1,  1],
], dtype=float) / 2.0

PHOTON_OP: int = 7
"""Photon operator = e_7 (state index 7, vacuum axis, U(1)_EM generator).
VACUUM_AXIS (conftest.py) = 6 is the 0-indexed Fano point for e_7;
state index = VACUUM_AXIS + 1 = 7.
"""

ELECTRON_STATE: int = 6
"""Representative electron state used in THIS FILE: e_6 (state index 6).

DEPRECATION WARNING (2026-02-23): e_6 is the Witt nil-element (Furey color-sector
excited state), NOT the correct electron rest state.  The electron lives in the L1
associative triad {e_1, e_2, e_3}.  See calc/qed_calibration.py for the corrected
model (L1_ELECTRON_STATE = 1).

This constant is kept here ONLY because the vertex-cost-ratio calculations in this
file (V rep = 1 tick, S+ rep = 15 ticks) do not depend on which specific state index
is used -- only on the V/S+ rep type.  The 81 tests for qed_scatter.py remain valid
for that limited purpose.  Do NOT import ELECTRON_STATE from this module for new work.
"""

MUON_STATE: int = 5
"""Representative muon state: e_5 (state index 5).
Placeholder for psi_mu; true muon state is from CausalGraphTheory/Spinors.lean.
e_5 is in the second Witt pair (e_2, e_5) -- conftest.py WITT_PAIRS[1] = (1, 4).
"""


# ================================================================
# Data structures (RFC-012 sec 6.2)
# ================================================================

RepType = Literal['V', 'Sp', 'Vac']


@dataclass
class Node:
    """A particle or vacuum node in the COG causal graph.

    id:        Strictly increasing integer label (simplified DAG ordering).
    rep:       Representation type:
                 'V'   = Vector / electron (generation 1)
                 'Sp'  = Spinor+ / muon    (generation 2)
                 'Vac' = Vacuum node (state omega = 1/2*(1 + i*e_7))
    state:     Dominant octonion basis index (0..7).
                 0 = e_0 (real unit / scalar), 1..7 = e_1..e_7 (imaginary units).
    tick_cost: Cumulative ticks consumed to reach this node from tick_cost=0.
    """
    id: int
    rep: RepType
    state: int
    tick_cost: int = 0


@dataclass
class Edge:
    """A directed causal edge carrying an operator.

    src: Source Node.id.
    dst: Destination Node.id.
    op:  Octonion basis index of the carried operator (0..7);
         None = free propagation (identity operator).
    """
    src: int
    dst: int
    op: Optional[int]


# ================================================================
# Octonion basis multiplication
# ================================================================

def oct_mul_idx(k: int, j: int) -> tuple[int, int]:
    """Left-multiply basis element e_k by basis element e_j.

    Returns (result_idx, sign) such that e_k * e_j = sign * e_{result_idx}.

    State index convention: 0 = e_0 (real unit), 1..7 = e_1..e_7 (imaginary).
    The locked Fano convention from rfc/CONVENTIONS.md / calc/conftest.py
    determines all signs and products.

    Rules:
      e_0 * e_j = e_j         (real unit is the multiplicative identity)
      e_k * e_0 = e_k
      e_k * e_k = -e_0        (imaginary units square to -1)
      e_i * e_j (i != j, nonzero): look up FANO_SIGN and FANO_THIRD.

    Args:
        k: State index of left factor (0..7).
        j: State index of right factor (0..7).

    Returns:
        (result_idx, sign): result_idx in 0..7, sign in {-1, +1}.
    """
    if k == 0:
        return (j, +1)
    if j == 0:
        return (k, +1)
    if k == j:
        return (0, -1)   # e_k^2 = -1 (result is -e_0)
    fano_k = k - 1      # 0-indexed Fano point for e_k
    fano_j = j - 1      # 0-indexed Fano point for e_j
    sign = FANO_SIGN[(fano_k, fano_j)]
    result_fano = FANO_THIRD[(fano_k, fano_j)]
    return (result_fano + 1, sign)


# ================================================================
# Triality translation (RFC-012 sec 4.2)
# ================================================================

def apply_triality_h(op_idx: int) -> int:
    """Translate a V-rep operator index to S+-rep via the McRae H matrix.

    IMPLEMENTATION STATUS: PLACEHOLDER (pending RFC-010 Phase D).

    The true 8x8 SO(8) outer triality intertwiner maps each V-rep basis
    vector to a +/-1/2 superposition of four S+-rep basis vectors
    (McRae 2025, arXiv:2502.14016, sec 2.2).  Deriving the intertwiner T
    requires solving:
        T . V_ij . T^{-1} = L_{H(ij)}
    for all 28 SO(8) generator pairs (i,j).  This is tracked as RFC-010
    Phase D and is the main blocker for the full LEPTON-001 computation.

    Current placeholder: the G2 inner automorphism cycling the three Witt
    color planes.  Permutation on state indices: (1->2->4->1), (3->6->5->3);
    e_0 and e_7 are fixed.  This is an automorphism of O (order 3, element
    of G_2 = Aut(O)), but is NOT the SO(8) outer triality.

    The tick cost N_TAU = 14 is CORRECT regardless of this placeholder:
    it is computed from the 4x4 McRae H matrix circuit depth, which is
    independent of the 8x8 intertwiner.

    Args:
        op_idx: State index (0..7) of the V-rep operator.

    Returns:
        State index (0..7) of the translated (placeholder) S+-rep operator.
    """
    _PERM: dict[int, int] = {0: 0, 1: 2, 2: 4, 3: 6, 4: 1, 5: 3, 6: 5, 7: 7}
    return _PERM[op_idx]


# ================================================================
# Core update step (RFC-012 sec 6.3)
# ================================================================

def update_step(
    node: Node,
    incoming_edges: list[Edge],
    n_tau: int = N_TAU,
) -> Node:
    """Compute the successor node after all incoming edges are resolved.

    Conflict Resolver priority (RFC-001 sec 4):
      1. Photon edges (op is not None) processed first.
      2. Propagation edges (op is None) applied last.

    Tick costs (RFC-012 sec 4.1, 4.2, 4.3):
      V   node + photon edge:  +1 tick    (native XOR; no triality needed)
      Sp  node + photon edge:  +n_tau+1   (triality emulation + XOR)
      Vac node + photon edge:  +1 tick    (e_7*omega associative; defines c=1)
      Any node + prop edge:    +1 tick    (free propagation, state unchanged)

    Vacuum nodes are NOT transparent: each photon hop through a Vac node
    costs exactly 1 tick (defines c = 1 vacuum hop per graph tick).

    Algebraic basis for Vac cost=1: e_7 * omega = 1/2*(e_7 - i).
    Both e_7 and omega = 1/2*(1+i*e_7) live in Span_C{1, e_7}, a commutative
    associative sub-algebra of C x O.  The Alternativity Trigger does not fire.
    See RFC-012 sec 4.3 and Sorkin 2009 arXiv:0910.0673.

    Args:
        node:           The node receiving edges.
        incoming_edges: All directed edges arriving at node.
        n_tau:          Triality emulation ticks (default N_TAU = 14).

    Returns:
        Successor Node with updated state and accumulated tick_cost.
    """
    total_ticks = node.tick_cost
    state = node.state

    photon_edges = [e for e in incoming_edges if e.op is not None]
    prop_edges   = [e for e in incoming_edges if e.op is None]

    for edge in photon_edges:
        if node.rep == 'Sp':
            # S+ node: V-rep photon operator (e_7) is incompatible with S+-rep
            # hardware.  Must run McRae H-matrix triality emulation first.
            # Cost = n_tau (H-matrix emulation) + 1 (native S+-rep XOR).
            translated = apply_triality_h(edge.op)
            result_idx, _sign = oct_mul_idx(translated, state)
            state = result_idx
            total_ticks += n_tau + 1
        else:
            # V or Vac node: native XOR, 1 tick.
            # Vac: e_7 * omega -> 1/2*(e_7 - i), associative, no penalty.
            result_idx, _sign = oct_mul_idx(edge.op, state)
            state = result_idx
            total_ticks += 1

    for _edge in prop_edges:
        # Free propagation: identity operator, 1 tick, state unchanged.
        total_ticks += 1

    return Node(id=node.id + 1, rep=node.rep, state=state, tick_cost=total_ticks)


# ================================================================
# Photon propagation through a vacuum chain (RFC-012 sec 3.4)
# ================================================================

def propagate_photon(
    chain: list[Node],
    photon_op: int = PHOTON_OP,
    n_tau: int = N_TAU,
) -> tuple[list[Node], int]:
    """Route a photon sequentially through a chain of nodes.

    chain[0] is the emitter (passed through unchanged -- already emitted).
    chain[1:] each absorb the photon in order, incurring tick costs:
      - Vac nodes: 1 tick each (defines c = 1 vacuum hop per tick).
      - V absorber: 1 tick.
      - Sp absorber: n_tau + 1 ticks.

    The photon operator (e_7 by default) is relayed unchanged through
    each node; the node's internal state updates via oct_mul_idx.

    Args:
        chain:      [emitter, vac_0, ..., vac_{n-1}, absorber].
        photon_op:  Operator carried by the photon (default: PHOTON_OP = e_7).
        n_tau:      Triality cost for Sp nodes (default: N_TAU = 14).

    Returns:
        (updated_chain, vacuum_tick_cost):
          - updated_chain: chain[0] unchanged; chain[1:] are successor nodes.
          - vacuum_tick_cost: sum of ticks from Vac nodes only.
    """
    updated: list[Node] = [chain[0]]   # emitter: pass through unchanged
    total_vac_ticks: int = 0

    for i, node in enumerate(chain[1:], start=1):
        photon_edge = Edge(src=chain[i - 1].id, dst=node.id, op=photon_op)
        successor = update_step(node, [photon_edge], n_tau=n_tau)
        if node.rep == 'Vac':
            total_vac_ticks += 1     # count vacuum hops separately
        updated.append(successor)

    return updated, total_vac_ticks


# ================================================================
# Scattering simulation runner (RFC-012 sec 6.4)
# ================================================================

def run_scattering(
    system: Literal['ee', 'emu'],
    n_vacuum: int = 4,
    n_interactions: int = 1,
    n_tau: int = N_TAU,
) -> dict:
    """Simulate photon emission/absorption cycle(s) in a vacuum lattice.

    System A ('ee') -- Moller scattering (e- + e-):
      Both particles are V-rep.
      Photon absorbed at V node: 1 tick.

    System B ('emu') -- Electron-muon scattering (e- + mu-):
      Particle 1 is V-rep (electron), Particle 2 is Sp-rep (muon).
      Photon absorbed at Sp node: n_tau + 1 = 15 ticks.

    The n_vacuum vacuum nodes between the two particles are NOT transparent.
    Each hop costs 1 tick; total vacuum cost = n_vacuum per interaction.
    This defines c = 1 vacuum hop per graph tick (Sorkin 2009 arXiv:0910.0673).

    Args:
        system:         'ee' (Moller) or 'emu' (electron-muon).
        n_vacuum:       Number of vacuum nodes between the two particles.
        n_interactions: Number of photon exchange cycles to simulate.
        n_tau:          Triality emulation ticks for Sp nodes (default: N_TAU=14).

    Returns:
        dict with keys:
          'system':           'ee' | 'emu'
          'particle1_rep':    'V'
          'particle2_rep':    'V' | 'Sp'
          'n_vacuum':         n_vacuum
          'vertex_tick_cost': ticks at the absorber vertex (accumulated over cycles)
          'n_tau':            n_tau
          'vacuum_tick_cost': ticks crossing vacuum nodes (accumulated over cycles)
          'total_tick_cost':  vertex_tick_cost + vacuum_tick_cost
          'particle1_state':  octonion basis index of particle 1 after simulation
          'particle2_state':  octonion basis index of particle 2 after simulation
    """
    if system not in ('ee', 'emu'):
        raise ValueError(f"Unknown system {system!r}. Use 'ee' or 'emu'.")

    # --- Build the initial node chain ---
    node_id = 0
    p1 = Node(id=node_id, rep='V', state=ELECTRON_STATE, tick_cost=0)
    node_id += 1

    vac_nodes: list[Node] = []
    for _ in range(n_vacuum):
        vac_nodes.append(Node(id=node_id, rep='Vac', state=0, tick_cost=0))
        node_id += 1

    p2_rep: RepType = 'V' if system == 'ee' else 'Sp'
    p2_init_state = ELECTRON_STATE if system == 'ee' else MUON_STATE
    p2 = Node(id=node_id, rep=p2_rep, state=p2_init_state, tick_cost=0)

    # --- Run photon exchange cycles ---
    # For each cycle: route the photon operator (e_7) sequentially from
    # p1 through the vacuum chain to p2.  p1 is the emitter and is
    # not charged a tick in this model; the tick cost is at the absorber (p2).
    vacuum_tick_cost_total = 0
    for _ in range(n_interactions):
        chain = [p1] + vac_nodes + [p2]
        updated_chain, vac_ticks = propagate_photon(
            chain, photon_op=PHOTON_OP, n_tau=n_tau
        )
        vacuum_tick_cost_total += vac_ticks
        # chain[0] (p1/emitter) is unchanged; update state references
        p1 = updated_chain[0]
        vac_nodes = updated_chain[1:1 + n_vacuum]
        p2 = updated_chain[1 + n_vacuum]

    # vertex_tick_cost = tick cost accumulated at the absorber (p2)
    vertex_tick_cost = p2.tick_cost

    return {
        'system': system,
        'particle1_rep': 'V',
        'particle2_rep': p2_rep,
        'n_vacuum': n_vacuum,
        'vertex_tick_cost': vertex_tick_cost,
        'n_tau': n_tau,
        'vacuum_tick_cost': vacuum_tick_cost_total,
        'total_tick_cost': vertex_tick_cost + vacuum_tick_cost_total,
        'particle1_state': p1.state,
        'particle2_state': p2.state,
    }


# ================================================================
# Orbit return time (RFC-012 sec 5.1)
# ================================================================

def orbit_return_time(
    particle_rep: RepType,
    initial_state: int,
    photon_op: int = PHOTON_OP,
    n_tau: int = N_TAU,
    max_steps: int = 10_000,
) -> int:
    """Compute the orbit return time C_p for a particle.

    Apply repeated photon absorptions until the state returns to initial_state.
    Return the total tick count accumulated over the orbit.

    Definition (RFC-012 sec 5.1):
      C_p = total ticks from first photon absorption until the state vector
            returns to its exact initial baseline.

    Implementation note: Uses integer state indices (dominant basis component).
    The full orbit calculation requires the 8x8 SO(8) triality intertwiner from
    RFC-010 Phase D.  With the current G2 placeholder for apply_triality_h:
      C_e (V-rep, state 6):   2 ticks  (orbit: e_6 -> e_1 -> e_6, period=2)
      C_mu (Sp-rep, state 5): 30 ticks (placeholder: same orbit period, 15x cost)
      Placeholder ratio:      30/2 = 15.0  (= vertex cost ratio only)
    The true ratio C_mu/C_e ~ 206.768 requires the true S+-rep intertwiner.

    Args:
        particle_rep:  'V' or 'Sp'.
        initial_state: Starting octonion basis index (0..7).
        photon_op:     Operator applied each step (default: PHOTON_OP = e_7 = 7).
        n_tau:         Triality cost for Sp nodes (default: N_TAU = 14).
        max_steps:     Safety limit; returns -1 if orbit not found.

    Returns:
        Total tick count for one full orbit, or -1 if not found within max_steps.
    """
    node = Node(id=0, rep=particle_rep, state=initial_state, tick_cost=0)
    start_state = initial_state
    start_tick = node.tick_cost   # = 0

    for step in range(max_steps):
        photon_edge = Edge(src=node.id - 1, dst=node.id, op=photon_op)
        node = update_step(node, [photon_edge], n_tau=n_tau)
        if node.state == start_state and step > 0:
            return node.tick_cost - start_tick

    return -1   # orbit not found within max_steps


def vertex_cost_ratio(n_tau: int = N_TAU) -> float:
    """Single-vertex photon absorption cost ratio: muon / electron.

    Returns (n_tau + 1) / 1 = 15.0 for n_tau = 14.

    This is the LOWER BOUND on m_mu/m_e from a single photon vertex.
    The full orbit ratio C_mu/C_e (target: ~206.768) also includes the
    orbit recovery cost (RFC-012 sec 5.1, LEPTON-001).
    """
    return float(n_tau + 1) / 1.0


# ================================================================
# McRae H matrix verification
# ================================================================

def verify_mcrae_h(tol: float = 1e-10) -> dict:
    """Verify the McRae H matrix: H^3 = I_4 and H^T H = I_4.

    Returns dict with 'order_3' (bool), 'orthogonal' (bool), 'all_ok' (bool).
    """
    H = MCRAE_H
    I4 = np.eye(4)
    order_3    = bool(np.allclose(H @ H @ H, I4, atol=tol))
    orthogonal = bool(np.allclose(H.T @ H, I4, atol=tol))
    return {
        'order_3': order_3,
        'orthogonal': orthogonal,
        'all_ok': order_3 and orthogonal,
    }


# ================================================================
# Main: print analysis for both systems
# ================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("RFC-012 QED Scattering Simulation")
    print("=" * 60)

    h_ok = verify_mcrae_h()
    print(f"\nMcRae H matrix: order_3={h_ok['order_3']}, orthogonal={h_ok['orthogonal']}")

    print(f"\nN_TAU = {N_TAU} = dim(G_2)  (proved 2026-02-22)")
    print(f"vertex_cost_ratio = {vertex_cost_ratio():.1f}  (lower bound on m_mu/m_e)")

    for sys in ('ee', 'emu'):
        r = run_scattering(sys, n_vacuum=4)
        print(f"\nSystem '{sys}':")
        print(f"  particle2_rep:    {r['particle2_rep']}")
        print(f"  vertex_tick_cost: {r['vertex_tick_cost']}")
        print(f"  vacuum_tick_cost: {r['vacuum_tick_cost']}  ({r['n_vacuum']} vacuum hops x 1)")
        print(f"  total_tick_cost:  {r['total_tick_cost']}")
        print(f"  particle2_state:  e_{r['particle2_state']} after photon absorption")

    Ce  = orbit_return_time('V',  ELECTRON_STATE)
    Cmu = orbit_return_time('Sp', MUON_STATE)
    print(f"\nOrbit return times (placeholder triality):")
    print(f"  C_e  (V-rep,  state e_{ELECTRON_STATE}): {Ce} ticks")
    print(f"  C_mu (Sp-rep, state e_{MUON_STATE}): {Cmu} ticks")
    if Ce > 0:
        print(f"  C_mu/C_e (placeholder): {Cmu/Ce:.3f}  (target: ~206.768 with true intertwiner)")
    print("\nNOTE: Placeholder ratio = vertex_cost_ratio (expected).")
    print("      True ratio requires the 8x8 SO(8) intertwiner (RFC-010 Phase D).")
