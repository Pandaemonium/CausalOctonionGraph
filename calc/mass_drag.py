"""calc/mass_drag.py

MU-001: Proton-to-Electron Mass Ratio from Algorithmic Drag.

Architecture (RFC-001 Phase II, revised RFC-009 2026-02-22):
  - Nodes: discrete events, state (OctIdx, sign) where OctIdx in {0..6},
           sign in {+1, -1}.  Signs MUST NOT be collapsed (RFC-009 §2b.4).
  - Edges: causal dependencies carrying a gluon operator (OctIdx)
  - Update rule: 3-body product s_L=(e_src*e_g)*e_dst, s_R=e_src*(e_g*e_dst)
      * Associative (Fano collinear OR repeated element): cost 1, 1 successor
      * Non-associative (off-line, all distinct): cost 2, 2 successors
  - Mass ratio = gate_density(proton) / gate_density(electron)
    where gate_density = (total non-assoc gates fired) / (ticks elapsed)
    measured over a long simulation window (thermodynamic limit approach).

  DO NOT look for an integer recurrence at 1836.  The physical ratio
  1836.15267 is a thermodynamic limit of gate frequencies, not a static
  cycle period (RFC-009 §7b note, Gemini 2026-02-22).

Gluon assignment (calc/gluon_assignment.py, locked RFC-001 §5.1):
  Color 1<->2 (Witt pairs 0<->1): gluons {e3,e4} = {idx 2,3}
  Color 1<->3 (Witt pairs 0<->2): gluons {e2,e5} = {idx 1,4}
  Color 2<->3 (Witt pairs 1<->2): gluons {e1,e6} = {idx 0,5}

Particle motifs:
  Electron: directed 2-body cycle within L1 = {e1,e2,e3}.
            e1 -[g=e2]-> e3 -[g=e1]-> e2 -[g=e3]-> e1, period 3. C_e = 3.
  Proton:   3 quarks in initial state (e5=4, e1=0, e3=2) (0-indexed),
            one from each Witt pair (Color2, Color1, Color3).
            CORRECTED cyclic exchange C1->C2->C3->C1 (RFC-009 §3).
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
        return False
    return frozenset({a, g, b}) in FANO_TRIPLE_SET


def triggers(a: int, g: int, b: int) -> bool:
    """
    Alternativity Trigger: True when the 3-body product is non-associative.
    - repeated element -> associative -> False
    - Fano collinear   -> associative -> False
    - otherwise        -> non-associative -> True
    """
    if len({a, g, b}) < 3:
        return False
    return not is_fano_collinear(a, g, b)


def fano_product(i: int, j: int) -> tuple[int, int]:
    """e_i * e_j -> (sign, result_index). Returns (sign, -1) for e_i^2 = -1."""
    if i == j:
        return (-1, -1)
    return (FANO_SIGN[(i, j)], FANO_THIRD[(i, j)])


def three_body(
    a: int, sign_a: int, g: int, b: int, sign_b: int
) -> tuple[tuple[int, int], tuple[int, int]]:
    """
    Both bracketings of (sign_a * e_a, e_g, sign_b * e_b).
    Signs propagate multiplicatively through the products.
    Returns ((sign_L, idx_L), (sign_R, idx_R)).
    idx = -1 means the result is real (±1), not an imaginary unit.
    """
    # Left bracketing: (sign_a * e_a * e_g) * sign_b * e_b
    sign_ag, idx_ag = fano_product(a, g)
    sign_ag *= sign_a          # propagate sign_a
    if idx_ag < 0:
        # e_a * e_g = real; result = sign_ag * sign_b * e_b
        s_L = (sign_ag * sign_b, b)
    else:
        sign_L, idx_L = fano_product(idx_ag, b)
        s_L = (sign_ag * sign_L * sign_b, idx_L)

    # Right bracketing: sign_a * e_a * (e_g * sign_b * e_b)
    sign_gb, idx_gb = fano_product(g, b)
    sign_gb *= sign_b          # propagate sign_b
    if idx_gb < 0:
        # e_g * e_b = real; result = sign_a * sign_gb * e_a
        s_R = (sign_a * sign_gb, a)
    else:
        sign_R, idx_R = fano_product(a, idx_gb)
        s_R = (sign_a * sign_gb * sign_R, idx_R)

    return s_L, s_R


# ── DAG data structures ──────────────────────────────────────────────────────
@dataclass
class Node:
    id: int
    idx: int          # 0-indexed OctIdx in {0..6}
    sign: int         # +1 or -1  (DO NOT COLLAPSE, RFC-009 §2b.4)
    tick_count: int   # cumulative ticks to generate this node


@dataclass
class DAG:
    nodes: list[Node] = field(default_factory=list)
    _next_id: int = 0

    def add_node(self, idx: int, sign: int, tick_count: int) -> Node:
        n = Node(id=self._next_id, idx=idx, sign=sign, tick_count=tick_count)
        self.nodes.append(n)
        self._next_id += 1
        return n


def update_step(
    src_idx: int,
    src_sign: int,
    g: int,
    dst_node: Node,
    dag: DAG,
    gate_counter: list[int],
) -> list[Node]:
    """
    Apply the 3-body interaction per RFC-001 §3.3.
    Signs are tracked on src and dst (RFC-009 §2b.4).
    gate_counter[0] is incremented for each non-associative trigger.
    Returns list of successor nodes (1 if associative, 2 if non-associative).
    Returns [] if both bracketings produce real results (blocked).
    """
    a, sign_a = src_idx, src_sign
    b, sign_b = dst_node.idx, dst_node.sign
    s_L, s_R = three_body(a, sign_a, g, b, sign_b)

    if not triggers(a, g, b):
        # Associative: s_L == s_R (idx-wise), cost 1 tick
        if s_L[1] < 0:
            return []    # real result, no imaginary successor
        new_node = dag.add_node(
            idx=s_L[1], sign=s_L[0], tick_count=dst_node.tick_count + 1
        )
        return [new_node]
    else:
        # Non-associative Alternativity Trigger fires: cost 2 ticks each
        gate_counter[0] += 1
        new_nodes = []
        for (s, idx) in (s_L, s_R):
            if idx >= 0:
                new_nodes.append(dag.add_node(
                    idx=idx, sign=s, tick_count=dst_node.tick_count + 2
                ))
        return new_nodes


# ── Electron simulation ───────────────────────────────────────────────────────
# The electron cycles through the directed L1 orbit:
#   e1 -[g=e2]-> e3 -[g=e1]-> e2 -[g=e3]-> e1   (period 3)
# All hops are within the associative L1 subalgebra. No Alternativity Trigger.
# Cost = 1 tick/hop. C_e = 3.  Gate density = 0 non-assoc triggers per tick.

ELECTRON_CYCLE = [
    (0, 1),   # state e1(0), gluon e2(1)  -> e1*e2 = +e3
    (2, 0),   # state e3(2), gluon e1(0)  -> e3*e1 = +e2
    (1, 2),   # state e2(1), gluon e3(2)  -> e2*e3 = +e1
]


def simulate_electron() -> int:
    """
    Simulate the electron's directed L1 cycle.
    Returns tick count C_e at first recurrence of the initial state.
    Signs are +1 throughout (associative subalgebra, no sign flips).
    """
    dag = DAG()
    initial_idx = ELECTRON_CYCLE[0][0]    # e1 = index 0
    current_node = dag.add_node(idx=initial_idx, sign=+1, tick_count=0)

    for hop, (idx, g) in enumerate(ELECTRON_CYCLE):
        assert current_node.idx == idx, (
            f"Electron: expected idx {idx} at hop {hop}, got {current_node.idx}"
        )
        sign, result_idx = fano_product(idx, g)
        assert result_idx >= 0, f"Electron hop {hop} gave real result"
        assert not triggers(idx, g, result_idx), (
            f"Electron hop {hop}: unexpected Alternativity Trigger"
        )
        new_node = dag.add_node(
            idx=result_idx, sign=sign * current_node.sign,
            tick_count=current_node.tick_count + 1
        )
        current_node = new_node

    assert current_node.idx == initial_idx, (
        f"Electron did not return to initial idx {initial_idx}: "
        f"got {current_node.idx}"
    )
    return current_node.tick_count


# ── Proton simulation ─────────────────────────────────────────────────────────
# Proton initial state (RFC-001 §4.3, 0-indexed):
#   Q[0]: idx=4 (e5, Color 2, Witt pair 1)
#   Q[1]: idx=0 (e1, Color 1, Witt pair 0)
#   Q[2]: idx=2 (e3, Color 3, Witt pair 2)
# Initial signs: all +1.
#
# CORRECTED cyclic exchange schedule (RFC-009 §3.1):
#   C1(Q[1]) -> C2(Q[0]), gluon {e3,e4}={2,3}  [C1->C2]
#   C2(Q[0]) -> C3(Q[2]), gluon {e1,e6}={0,5}  [C2->C3]
#   C3(Q[2]) -> C1(Q[1]), gluon {e2,e5}={1,4}  [C3->C1]
# Every quark is src exactly once and dst exactly once per 3-step period.

PROTON_INIT = (4, 0, 2)      # (e5, e1, e3) 0-indexed

PROTON_EXCHANGE_SCHEDULE = [
    (1, 0, [2, 3]),   # C1(Q[1]) -> C2(Q[0]), gluon {e3,e4}  [C1->C2]
    (0, 2, [0, 5]),   # C2(Q[0]) -> C3(Q[2]), gluon {e1,e6}  [C2->C3]
    (2, 1, [1, 4]),   # C3(Q[2]) -> C1(Q[1]), gluon {e2,e5}  [C3->C1]
]


def simulate_proton_gate_density(
    n_steps: int = 3_000,
    max_branches: int = 500,
) -> dict:
    """
    Simulate the proton motif for n_steps exchanges and measure gate density.

    Returns a dict with:
      total_steps:        number of exchange steps taken
      total_ticks:        max tick_count across surviving branches
      gate_fires:         total non-assoc Alternativity Triggers fired
      gate_density:       gate_fires / total_ticks (non-assoc per tick)
      branch_count:       number of branches at end
      first_recurrence:   (step, tick_cost) if recurrence found, else None
    """
    dag = DAG()
    gate_counter = [0]    # mutable counter passed to update_step

    q0 = dag.add_node(idx=PROTON_INIT[0], sign=+1, tick_count=0)
    q1 = dag.add_node(idx=PROTON_INIT[1], sign=+1, tick_count=0)
    q2 = dag.add_node(idx=PROTON_INIT[2], sign=+1, tick_count=0)

    # Each branch: (Q[0], Q[1], Q[2]) as Node objects
    branches: list[tuple[Node, Node, Node]] = [(q0, q1, q2)]

    first_recurrence = None

    for step in range(n_steps):
        q_src_idx, q_dst_idx, gluon_candidates = PROTON_EXCHANGE_SCHEDULE[step % 3]
        new_branches: list[tuple[Node, Node, Node]] = []

        for branch in branches:
            quarks = list(branch)
            q_src = quarks[q_src_idx]
            q_dst = quarks[q_dst_idx]

            any_valid = False
            for g in gluon_candidates:
                successors = update_step(
                    src_idx=q_src.idx,
                    src_sign=q_src.sign,
                    g=g,
                    dst_node=q_dst,
                    dag=dag,
                    gate_counter=gate_counter,
                )
                for new_dst in successors:
                    new_quarks = quarks.copy()
                    new_quarks[q_dst_idx] = new_dst
                    new_branches.append(tuple(new_quarks))
                    any_valid = True

            if not any_valid:
                new_branches.append(tuple(quarks))

        if not new_branches:
            break

        branches = new_branches

        # Check for recurrence (signed state match)
        if first_recurrence is None:
            for b in branches:
                if (b[0].idx, b[1].idx, b[2].idx) == PROTON_INIT and \
                   b[0].sign == +1 and b[1].sign == +1 and b[2].sign == +1:
                    cost = max(b[0].tick_count, b[1].tick_count, b[2].tick_count)
                    if cost > 0:
                        first_recurrence = (step + 1, cost)

        # Prune: keep cheapest branches to control exponential blowup
        if len(branches) > max_branches:
            branches.sort(
                key=lambda b: max(b[0].tick_count, b[1].tick_count, b[2].tick_count)
            )
            branches = branches[:max_branches // 2]

    total_ticks = max(
        max(b[0].tick_count, b[1].tick_count, b[2].tick_count)
        for b in branches
    ) if branches else 0

    gate_density = gate_counter[0] / total_ticks if total_ticks > 0 else 0.0

    return {
        "total_steps":      n_steps,
        "total_ticks":      total_ticks,
        "gate_fires":       gate_counter[0],
        "gate_density":     gate_density,
        "branch_count":     len(branches),
        "first_recurrence": first_recurrence,
    }


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    print("=" * 66)
    print("MU-001: Proton-to-Electron Mass Ratio (COG Gate-Density Simulation)")
    print("=" * 66)
    print()
    print("ARCHITECTURE NOTE (RFC-009 §7b, 2026-02-22):")
    print("  Mass = gate density (non-assoc triggers per tick),")
    print("  NOT a static recurrence period.  1836.15 is a thermodynamic")
    print("  limit, not a magic integer.  Signs are tracked (+/-1 on state).")
    print()

    # ── Electron ──────────────────────────────────────────────────────────────
    print("Electron motif (directed L1 cycle, 3 hops, all associative):")
    C_e = simulate_electron()
    print(f"  Cycle: e1 -> e3 -> e2 -> e1")
    print(f"  C_e = {C_e} ticks  (no Alternativity Trigger, 0 non-assoc gates)")
    print(f"  Electron gate density = 0.000 non-assoc gates/tick")
    print()

    # ── Proton ────────────────────────────────────────────────────────────────
    print("Proton motif (corrected cyclic exchange C1->C2->C3->C1):")
    print("  Initial state: Q[0]=(e5,+), Q[1]=(e1,+), Q[2]=(e3,+)")
    print("  Exchange: C1->C2, C2->C3, C3->C1  (RFC-009 §3)")
    print()

    # Run at increasing horizons to show convergence
    for n_steps in [100, 500, 2000]:
        result = simulate_proton_gate_density(n_steps=n_steps)
        print(f"  n_steps={n_steps:5d}: "
              f"ticks={result['total_ticks']:6d}  "
              f"gate_fires={result['gate_fires']:5d}  "
              f"gate_density={result['gate_density']:.4f}  "
              f"branches={result['branch_count']:4d}")
        if result["first_recurrence"]:
            step, cost = result["first_recurrence"]
            print(f"             first_recurrence: step={step}, tick_cost={cost}  "
                  f"(naive C_p={cost}, mu_naive={cost/C_e:.3f})")

    print()
    print("=" * 66)
    print("INTERPRETATION:")
    print("  The gate_density ratio = proton_density / electron_density")
    print("  Electron gate density = 0 (fully associative L1 cycle)")
    print("  Non-zero proton gate density = Alternativity Trigger overhead")
    print("  The convergence of this ratio toward mu_exp = 1836.15 as")
    print("  n_steps -> infinity is the COG prediction for MU-001.")
    print("  (If first_recurrence tick_cost / C_e already approaches 1836,")
    print("   the simpler cycle-count interpretation is still in play.)")
    mu_exp = 1836.15267343
    print(f"  Target: mu_exp = {mu_exp}")
    print()
    print("See RFC-009 §3, §7b.10 and claims/proton_electron_ratio.yml.")


if __name__ == "__main__":
    main()
