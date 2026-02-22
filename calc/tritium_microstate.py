"""
calc/tritium_microstate.py
Phase 3A: Initial microstate for tritium ³H

Specifies the exact 10-node COG initial state for a tritium nucleus.
This is the first physics-specific simulation file; it serves as the
driver for all downstream tritium evolution tests.

Node layout (from sources/nuclear_hadron_physics.md §5.1):
  id=0  : vacuum            — Fock vacuum / sterile neutrino (vacuum axis e7)
  id=1  : V (u-quark)      — up quark in proton
  id=2  : V (d-quark)      — down quark 1 in proton
  id=3  : V (d-quark)      — down quark 2 in proton
  id=4  : V (u-quark)      — up quark in neutron₁
  id=5  : V (d-quark)      — down quark 1 in neutron₁
  id=6  : V (d-quark)      — down quark 2 in neutron₁
  id=7  : V (u-quark)      — up quark in neutron₂
  id=8  : V (d-quark)      — down quark 1 in neutron₂
  id=9  : V (d-quark)      — down quark 2 in neutron₂

Edge layout (from sources/nuclear_hadron_physics.md §5.2):
  Within-proton SU3 color    :  1→2, 2→3, 1→3   (generators 0,1,2)
  Within-neutron₁ SU3 color  :  4→5, 5→6, 4→6   (generators 0,1,2)
  Within-neutron₂ SU3 color  :  7→8, 8→9, 7→9   (generators 0,1,2)
  Proton ↔ Neutron₁ residual :  1→4              (generator 3)
  Proton ↔ Neutron₂ residual :  1→7              (generator 4)
  Neutron₁ ↔ Neutron₂ resid. :  4→7              (generator 5)
  Proton EM (Coulomb U1)     :  0→1
  Vacuum coupling            :  0→4, 0→7          (generator 6 = e7 axis)

All edges satisfy source < target (DAG invariant).
Total: 10 nodes, 14 edges.

CO state conventions (Witt basis, rfc/CONVENTIONS.md §4):
  - u quark: component e1 = +1 (represents the Witt mode α†₁ real part)
  - d quark: component e2 = +1 (represents the Witt mode α†₂ real part)
  - vacuum : component e7 = +1 (vacuum axis, rfc/CONVENTIONS.md §5)
  - SU3 operator(k): unit vector along e_{k+1} for k in 0..5
  - U1  operator   : unit vector along e7 (EM = vacuum axis coupling)

These are placeholder states sufficient for structural/topology tests.
Full physics requires the Witt basis ladder operator construction in WittBasis.lean.
"""

from calc.graph_sim import CausalGraph, zero_state, e7_state, unit_state


# ---------------------------------------------------------------------------
# State templates
# ---------------------------------------------------------------------------

def u_quark_state() -> list:
    """
    CO state for an up quark: unit coefficient on e1.
    Represents the Witt ladder operator α†₁ (real component).
    Convention: rfc/CONVENTIONS.md §4, Witt pair (e6, e1).
    """
    return unit_state(1)   # e1 component = +1 (real)


def d_quark_state() -> list:
    """
    CO state for a down quark: unit coefficient on e2.
    Represents the Witt ladder operator α†₂ (real component).
    Convention: rfc/CONVENTIONS.md §4, Witt pair (e2, e5).
    """
    return unit_state(2)   # e2 component = +1 (real)


# ---------------------------------------------------------------------------
# Operator templates
# ---------------------------------------------------------------------------

def su3_operator(generator: int) -> list:
    """
    SU(3) gluon operator: unit vector along e_{generator+1}.
    generator ∈ {0,..,7} maps to e1..e8 (8 Gell-Mann generators).
    We use generators 0..5 for the color edges in the tritium microstate.
    """
    assert 0 <= generator <= 6, f"SU3 generator must be 0..6, got {generator}"
    return unit_state(generator + 1)   # e_{generator+1}


def u1_operator() -> list:
    """
    U(1) photon operator: unit vector along e7 (vacuum axis).
    Convention: e7 is the electromagnetic / vacuum axis (rfc/CONVENTIONS.md §5).
    """
    return e7_state()   # e7 component = +1


# ---------------------------------------------------------------------------
# Microstate builder
# ---------------------------------------------------------------------------

def build_tritium_microstate() -> CausalGraph:
    """
    Construct the 10-node COG initial state for tritium ³H = proton + neutron₁ + neutron₂.

    Returns a CausalGraph with 10 nodes and 14 directed edges satisfying the DAG
    invariant (source.id < target.id for all edges).

    This is the canonical starting point for all tritium evolution simulations.
    To evolve: call update_step() or run() from graph_sim.py.

    Notation:
      p_u, p_d1, p_d2    = proton quarks (u,d,d)
      n1_u, n1_d1, n1_d2 = neutron₁ quarks
      n2_u, n2_d1, n2_d2 = neutron₂ quarks
      vac                = vacuum
    """
    G = CausalGraph()

    # -----------------------------------------------------------------------
    # Nodes
    # -----------------------------------------------------------------------

    # id=0: Vacuum node
    vac = G.add_node("vacuum", state=e7_state(), tick_count=0)
    assert vac == 0

    # id=1,2,3: Proton (u d d)
    p_u  = G.add_node("V", state=u_quark_state(), tick_count=0)   # id=1
    p_d1 = G.add_node("V", state=d_quark_state(), tick_count=0)   # id=2
    p_d2 = G.add_node("V", state=d_quark_state(), tick_count=0)   # id=3

    # id=4,5,6: Neutron₁ (u d d)
    n1_u  = G.add_node("V", state=u_quark_state(), tick_count=0)  # id=4
    n1_d1 = G.add_node("V", state=d_quark_state(), tick_count=0)  # id=5
    n1_d2 = G.add_node("V", state=d_quark_state(), tick_count=0)  # id=6

    # id=7,8,9: Neutron₂ (u d d)  — candidate for beta decay
    n2_u  = G.add_node("V", state=u_quark_state(), tick_count=0)  # id=7
    n2_d1 = G.add_node("V", state=d_quark_state(), tick_count=0)  # id=8
    n2_d2 = G.add_node("V", state=d_quark_state(), tick_count=0)  # id=9

    # -----------------------------------------------------------------------
    # Edges — Within-nucleon color confinement (SU3)
    # Each nucleon is a color-singlet: 3 quarks connected by SU3 operators.
    # DAG ordering uses the assigned IDs above.
    # -----------------------------------------------------------------------

    # Proton color (generators 0, 1, 2 → e1, e2, e3)
    G.add_edge(p_u,  p_d1, label="SU3_0", operator=su3_operator(0))  # 1→2
    G.add_edge(p_d1, p_d2, label="SU3_1", operator=su3_operator(1))  # 2→3
    G.add_edge(p_u,  p_d2, label="SU3_2", operator=su3_operator(2))  # 1→3

    # Neutron₁ color
    G.add_edge(n1_u,  n1_d1, label="SU3_0", operator=su3_operator(0))  # 4→5
    G.add_edge(n1_d1, n1_d2, label="SU3_1", operator=su3_operator(1))  # 5→6
    G.add_edge(n1_u,  n1_d2, label="SU3_2", operator=su3_operator(2))  # 4→6

    # Neutron₂ color
    G.add_edge(n2_u,  n2_d1, label="SU3_0", operator=su3_operator(0))  # 7→8
    G.add_edge(n2_d1, n2_d2, label="SU3_1", operator=su3_operator(1))  # 8→9
    G.add_edge(n2_u,  n2_d2, label="SU3_2", operator=su3_operator(2))  # 7→9

    # -----------------------------------------------------------------------
    # Edges — Inter-nucleon residual strong force
    # The three nucleons are coupled pairwise via residual color leakage.
    # We connect the representative (u-quark) of each nucleon.
    # -----------------------------------------------------------------------

    G.add_edge(p_u,  n1_u, label="SU3_3", operator=su3_operator(3))  # 1→4
    G.add_edge(p_u,  n2_u, label="SU3_4", operator=su3_operator(4))  # 1→7
    G.add_edge(n1_u, n2_u, label="SU3_5", operator=su3_operator(5))  # 4→7

    # -----------------------------------------------------------------------
    # Edges — Proton EM (Coulomb repulsion, U1)
    # -----------------------------------------------------------------------

    G.add_edge(vac, p_u, label="U1", operator=u1_operator())           # 0→1

    # -----------------------------------------------------------------------
    # Edges — Vacuum coupling (sterile neutrino / color neutrality stabilization)
    # The vacuum couples to each neutron's u-quark via the SU3_6 generator.
    # -----------------------------------------------------------------------

    G.add_edge(vac, n1_u, label="SU3_6", operator=su3_operator(6))    # 0→4
    G.add_edge(vac, n2_u, label="SU3_6", operator=su3_operator(6))    # 0→7

    return G


# ---------------------------------------------------------------------------
# Convenience: pre-built instance for import
# ---------------------------------------------------------------------------

def get_tritium() -> CausalGraph:
    """Return a fresh copy of the tritium initial microstate."""
    return build_tritium_microstate()
