"""calc/mass_drag.py

MU-001: Proton-to-Electron Mass Ratio from Algorithmic Drag.

Architecture (RFC-001 Phase II):
  - Nodes: discrete events, state OctIdx in {0..6} (0-indexed e1..e7)
  - Edges: causal dependencies carrying a gluon operator (OctIdx)
  - Update rule: 3-body product s_L=(e_src*e_g)*e_dst, s_R=e_src*(e_g*e_dst)
      * Associative (Fano collinear OR repeated element): cost 1, 1 successor
      * Non-associative (off-line, all distinct): cost 2, 2 successors
  - Mass ratio = C_p / C_e (tick counts to first recurrence)

Gluon assignment (calc/gluon_assignment.py, locked RFC-001 §5.1):
  Color 1<->2 (Witt pairs 0<->1): gluons {e3,e4} = {idx 2,3}
  Color 1<->3 (Witt pairs 0<->2): gluons {e2,e5} = {idx 1,4}
  Color 2<->3 (Witt pairs 1<->2): gluons {e1,e6} = {idx 0,5}

Particle motifs:
  Electron: directed 2-body cycle within L1 = {e1,e2,e3}.
            e1 -[g=e2]-> e3 -[g=e1]-> e2 -[g=e3]-> e1, period 3. C_e = 3.
  Proton:   3 quarks in initial state (e5=4, e1=0, e3=2) (0-indexed),
            one from each Witt pair (Color2, Color1, Color3).
"""

import sys
import pathlib
from dataclasses import dataclass, field

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from conftest import FANO_CYCLES, FANO_SIGN, FANO_THIRD, WITT_PAIRS, VACUUM_AXIS

# ── Fano lookup ──────────────────────────────────────────────────────────────
FANO_TRIPLE_SET: set[frozenset] = set()
for _a, _b, _c in FANO_CYCLES:
    FANO_TRIPLE_SET.add(frozenset({_a, _b, _c}))


def is_fano_collinear(a: int, g: int, b: int) -> bool:
    """True if {a,g,b} is one of the 7 Fano lines (all distinct required)."""
    if len({a, g, b}) < 3:
        return False          # repeated element → not a Fano triple
    return frozenset({a, g, b}) in FANO_TRIPLE_SET


def triggers(a: int, g: int, b: int) -> bool:
    """
    Alternativity Trigger: True when the 3-body product is non-associative.
    By the alternativity property of octonions, the alternator [x,y,z]
    vanishes whenever any two of x,y,z are equal.  So:
      - repeated element → associative → returns False
      - Fano collinear   → associative → returns False
      - otherwise        → non-associative → returns True
    """
    if len({a, g, b}) < 3:
        return False          # alternativity: [x,x,y] = [x,y,y] = 0
    return not is_fano_collinear(a, g, b)


def fano_product(i: int, j: int) -> tuple[int, int]:
    """e_i * e_j -> (sign, result_index). Returns (sign, -1) for e_i^2 = -1."""
    if i == j:
        return (-1, -1)       # e_i^2 = -e_0 (real part, no imaginary index)
    return (FANO_SIGN[(i, j)], FANO_THIRD[(i, j)])


def three_body(a: int, g: int, b: int) -> tuple[tuple[int, int], tuple[int, int]]:
    """
    Both bracketings of (e_a, e_g, e_b):
      s_L = (e_a * e_g) * e_b
      s_R = e_a * (e_g * e_b)
    Returns ((sign_L, idx_L), (sign_R, idx_R)).
    idx = -1 means the result is real (±1), not an imaginary unit.
    """
    # Left bracketing
    sign_ag, idx_ag = fano_product(a, g)
    if idx_ag < 0:
        # e_a * e_g = -1 (a == g); then (-1)*e_b = -e_b
        s_L = (-sign_ag, b)
    else:
        sign_L, idx_L = fano_product(idx_ag, b)
        s_L = (sign_ag * sign_L, idx_L)

    # Right bracketing
    sign_gb, idx_gb = fano_product(g, b)
    if idx_gb < 0:
        # e_g * e_b = -1 (g == b); then e_a * (-1) = -e_a
        s_R = (-sign_gb, a)
    else:
        sign_R, idx_R = fano_product(a, idx_gb)
        s_R = (sign_gb * sign_R, idx_R)

    return s_L, s_R


# ── DAG data structures ──────────────────────────────────────────────────────
@dataclass
class Node:
    id: int
    state: int        # 0-indexed OctIdx in {0..6}
    tick_count: int   # cumulative ticks to generate this node


@dataclass
class DAG:
    nodes: list[Node] = field(default_factory=list)
    _next_id: int = 0

    def add_node(self, state: int, tick_count: int) -> Node:
        n = Node(id=self._next_id, state=state, tick_count=tick_count)
        self.nodes.append(n)
        self._next_id += 1
        return n


def update_step(
    src_state: int,
    g: int,
    dst_node: Node,
    dag: DAG,
) -> list[Node]:
    """
    Apply the 3-body interaction (src_state, g, dst_node.state) per RFC-001 §3.3.
    Returns list of successor nodes (1 if associative, 2 if non-associative).
    Returns [] if both bracketings produce real results (blocked interaction).
    """
    a = src_state
    b = dst_node.state
    s_L, s_R = three_body(a, g, b)

    if not triggers(a, g, b):
        # Associative: s_L == s_R, cost 1
        if s_L[1] < 0:
            return []    # real result, no imaginary successor
        new_node = dag.add_node(state=s_L[1], tick_count=dst_node.tick_count + 1)
        return [new_node]
    else:
        # Non-associative: both bracketings, cost 2 each
        new_nodes = []
        for (sign, idx) in (s_L, s_R):
            if idx >= 0:
                new_nodes.append(dag.add_node(state=idx, tick_count=dst_node.tick_count + 2))
        return new_nodes


# ── Electron simulation ───────────────────────────────────────────────────────
# The electron cycles through the directed L1 orbit:
#   e1 -[g=e2]-> e3 -[g=e1]-> e2 -[g=e3]-> e1   (period 3)
# Each hop is a 2-body product within the associative L1 subalgebra.
# No Alternativity Trigger fires. Cost = 1 tick / hop. C_e = 3.

# 0-indexed: L1 = {e1, e2, e3} = {0, 1, 2}
ELECTRON_CYCLE = [
    (0, 1),   # state e1(0), gluon e2(1)  -> e1*e2 = +e3
    (2, 0),   # state e3(2), gluon e1(0)  -> e3*e1 = +e2
    (1, 2),   # state e2(1), gluon e3(2)  -> e2*e3 = +e1
]


def simulate_electron() -> int:
    """
    Simulate the electron's directed L1 cycle.
    Returns tick count C_e at first recurrence of the initial state.
    """
    dag = DAG()
    initial_state = ELECTRON_CYCLE[0][0]    # e1 = index 0
    current_node = dag.add_node(state=initial_state, tick_count=0)

    for hop, (state, g) in enumerate(ELECTRON_CYCLE):
        assert current_node.state == state, (
            f"Electron: expected state {state} at hop {hop}, "
            f"got {current_node.state}"
        )
        sign, result_idx = fano_product(state, g)
        assert result_idx >= 0, f"Electron hop {hop} gave real result"
        assert not triggers(state, g, result_idx), (
            f"Electron hop {hop}: unexpected Alternativity Trigger "
            f"({state}, {g}, {result_idx})"
        )
        # Verify the product lands correctly
        new_node = dag.add_node(state=result_idx, tick_count=current_node.tick_count + 1)
        current_node = new_node

    assert current_node.state == initial_state, (
        f"Electron did not return to initial state {initial_state}: "
        f"got {current_node.state}"
    )
    return current_node.tick_count


# ── Proton simulation ─────────────────────────────────────────────────────────
# Proton initial state (RFC-001 §4.3, 0-indexed):
#   Q[0]: state=4 (e5, Color 2 lowering, Witt pair 1)
#   Q[1]: state=0 (e1, Color 1 raising, Witt pair 0)
#   Q[2]: state=2 (e3, Color 3 raising, Witt pair 2)
#
# Witt pair IDs: 0=Color1, 1=Color2, 2=Color3
# Exchange schedule (using QUARK indices, not Witt pair IDs):
#   Q[1](Color1) <-> Q[0](Color2): gluon pair {e3,e4}={2,3}  [Witt pair 2 = Color3]
#   Q[1](Color1) <-> Q[2](Color3): gluon pair {e2,e5}={1,4}  [Witt pair 1 = Color2]
#   Q[0](Color2) <-> Q[2](Color3): gluon pair {e1,e6}={0,5}  [Witt pair 0 = Color1]

PROTON_INIT = (4, 0, 2)      # (e5, e1, e3) 0-indexed

WITT_PAIR_MAP: dict[int, int] = {
    idx: pair_id for pair_id, pair in enumerate(WITT_PAIRS) for idx in pair
}

# Exchange schedule: (quark_src_idx, quark_dst_idx, [gluon_candidates])
# Quark src emits gluon; quark dst absorbs. Dst state is updated.
PROTON_EXCHANGE_SCHEDULE = [
    (1, 0, [2, 3]),   # Color1(Q[1]) -> Color2(Q[0]), gluon {e3,e4}
    (1, 2, [1, 4]),   # Color1(Q[1]) -> Color3(Q[2]), gluon {e2,e5}
    (0, 2, [0, 5]),   # Color2(Q[0]) -> Color3(Q[2]), gluon {e1,e6}
]


def is_initial_state(states: tuple[int, int, int]) -> bool:
    return states == PROTON_INIT


def simulate_proton(max_steps: int = 30_000) -> tuple[int, str]:
    """
    Simulate the proton motif as a branching DAG per RFC-001 §3.3.

    Returns (C_p, status):
      C_p = minimum tickCount at first initial-state recurrence (across all branches)
      status = 'recurred' | 'max_steps' | 'no_branches'
    """
    dag = DAG()

    q0 = dag.add_node(state=PROTON_INIT[0], tick_count=0)
    q1 = dag.add_node(state=PROTON_INIT[1], tick_count=0)
    q2 = dag.add_node(state=PROTON_INIT[2], tick_count=0)

    # Each branch: (Q[0], Q[1], Q[2]) as Node objects
    branches: list[tuple[Node, Node, Node]] = [(q0, q1, q2)]

    for step in range(max_steps):
        q_src_idx, q_dst_idx, gluon_candidates = PROTON_EXCHANGE_SCHEDULE[step % 3]
        new_branches: list[tuple[Node, Node, Node]] = []

        for branch in branches:
            quarks = list(branch)
            q_src = quarks[q_src_idx]
            q_dst = quarks[q_dst_idx]

            any_valid = False
            for g in gluon_candidates:
                successors = update_step(
                    src_state=q_src.state,
                    g=g,
                    dst_node=q_dst,
                    dag=dag,
                )
                for new_dst in successors:
                    new_quarks = quarks.copy()
                    new_quarks[q_dst_idx] = new_dst
                    new_branches.append(tuple(new_quarks))
                    any_valid = True

            if not any_valid:
                # Blocked branch: no valid gluon interaction.
                # Preserve the branch as-is (quark unchanged this step).
                new_branches.append(tuple(quarks))

        if not new_branches:
            return (0, 'no_branches')

        branches = new_branches

        # Check for recurrence
        found_costs = []
        for b in branches:
            states = (b[0].state, b[1].state, b[2].state)
            if is_initial_state(states):
                cost = max(b[0].tick_count, b[1].tick_count, b[2].tick_count)
                found_costs.append(cost)

        if found_costs:
            return (min(found_costs), 'recurred')

        # Prune: keep cheapest branches to avoid exponential blowup
        if len(branches) > 20_000:
            branches.sort(
                key=lambda b: max(b[0].tick_count, b[1].tick_count, b[2].tick_count)
            )
            branches = branches[:1_000]

    # Did not recur within max_steps
    min_cost = min(
        max(b[0].tick_count, b[1].tick_count, b[2].tick_count)
        for b in branches
    )
    return (min_cost, 'max_steps')


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    print("=" * 62)
    print("MU-001: Proton-to-Electron Mass Ratio (COG DAG Simulation)")
    print("=" * 62)
    print()

    print("Electron motif (directed L1 cycle, 3 hops):")
    C_e = simulate_electron()
    print(f"  Cycle: e1 -> e3 -> e2 -> e1")
    print(f"  C_e = {C_e} ticks  (1 tick/hop, no branching)")
    print()

    print("Proton motif (branching color-singlet DAG, max 30k steps):")
    print("  Initial state: (e5, e1, e3) = (Color2, Color1, Color3)")
    print("  Exchange schedule: C1<->C2, C1<->C3, C2<->C3 (cyclic)")
    C_p, status = simulate_proton()
    print(f"  C_p = {C_p} ticks  (status: {status})")
    print()

    if C_e == 0:
        print("  ERROR: C_e = 0.")
        return

    mu_COG = C_p / C_e
    mu_exp = 1836.15267343    # CODATA 2022

    print("-" * 62)
    print(f"  mu_COG  (computed)   = {mu_COG:.4f}")
    print(f"  mu_exp  (CODATA 2022) = {mu_exp:.8f}")
    print(f"  ratio   mu_COG/mu_exp = {mu_COG/mu_exp:.6f}")
    gap = abs(mu_COG - mu_exp) / mu_exp
    print(f"  relative gap          = {gap:.4%}")
    print()

    if status == 'recurred':
        if gap < 0.001:
            print("  RESULT: Match within 0.1% of experimental value.")
        elif gap < 0.01:
            print("  RESULT: Match within 1% of experimental value.")
        elif gap < 0.10:
            print("  RESULT: Order-of-magnitude match (within 10%).")
        else:
            print("  RESULT: Does not match. Documenting as falsification datum.")
            print("          Record C_p and C_e in claims/proton_electron_ratio.yml.")
    else:
        print(f"  RESULT: Proton cycle did not recur ({status}).")
        print("          This falsifies the current interaction model.")
        print("          Document in RFC-001 and claims/proton_electron_ratio.yml.")
    print()
    print("See RFC-001 §4.4 and claims/proton_electron_ratio.yml.")


if __name__ == "__main__":
    main()
