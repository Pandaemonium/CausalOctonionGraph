"""
calc/graph_sim.py
Phase 3A: Causal Graph DAG Simulator

Mirrors the Lean kernel (State.lean, Tick.lean, Update.lean) in Python.
Uses NetworkX DiGraph for graph storage and analysis.

Nodes carry:  id (int), label (NodeLabel), state (ComplexOctonion coeffs), tick_count (int)
Edges carry:  label (EdgeLabel), operator (ComplexOctonion coeffs)

ComplexOctonion is represented as a list of 8 tuples (re: int, im: int),
one per octonion basis element e0..e7. This mirrors Octonion(FormalComplex Z).

Convention: indices 0..6 are 0-indexed Fano points corresponding to e1..e7.
            index 7 is the vacuum axis e7 (= Fano point 6) used for U(1)/vacuum.
"""

import networkx as nx
from calc.fano import incident, FANO_CYCLES

# ---------------------------------------------------------------------------
# Data types (mirrors Lean NodeLabel / EdgeLabel)
# ---------------------------------------------------------------------------

VALID_LABELS = frozenset({"V", "S_plus", "S_minus", "vacuum"})

# A ComplexOctonion state: list of 8 (re, im) integer pairs.
# state[i] = coefficient of e_i (0 = real/e0, 1..7 = imaginary/e1..e7).
State = list[tuple[int, int]]


def zero_state() -> State:
    """Return the zero element of C⊗O (all coefficients zero)."""
    return [(0, 0)] * 8


def e7_state() -> State:
    """Return the vacuum axis element: coefficient of e7 is +1 (real)."""
    s = list(zero_state())
    s[7] = (1, 0)
    return s


def unit_state(index: int, *, imag: bool = False) -> State:
    """Return a state with a unit coefficient at e_{index}. 0 ≤ index ≤ 7."""
    assert 0 <= index <= 7
    s = list(zero_state())
    s[index] = (0, 1) if imag else (1, 0)
    return s


# ---------------------------------------------------------------------------
# CausalGraph class
# ---------------------------------------------------------------------------

class CausalGraph:
    """
    A directed acyclic causal graph.
    DAG invariant: every edge (src → tgt) has src.id < tgt.id.

    Mirrors CausalGraphTheory.CausalGraph from State.lean.
    """

    def __init__(self):
        self._graph: nx.DiGraph = nx.DiGraph()
        self._next_id: int = 0

    # -----------------------------------------------------------------------
    # Mutators
    # -----------------------------------------------------------------------

    def add_node(
        self,
        label: str,
        state: State | None = None,
        tick_count: int = 0,
    ) -> int:
        """
        Add a node with the next available ID and return that ID.
        Mirrors the Node struct in State.lean.
        """
        assert label in VALID_LABELS, f"Unknown NodeLabel: {label!r}"
        nid = self._next_id
        self._next_id += 1
        self._graph.add_node(
            nid,
            label=label,
            state=list(state) if state is not None else zero_state(),
            tick_count=tick_count,
        )
        return nid

    def add_edge(
        self,
        source: int,
        target: int,
        label: str,
        operator: State | None = None,
    ) -> None:
        """
        Add a directed edge source → target.
        Enforces the DAG invariant: source < target.
        Mirrors the Edge struct in State.lean.
        """
        if source >= target:
            raise ValueError(
                f"DAG invariant violated: edge {source} → {target} "
                f"(source must be strictly less than target)"
            )
        self._graph.add_edge(
            source,
            target,
            label=label,
            operator=list(operator) if operator is not None else zero_state(),
        )

    # -----------------------------------------------------------------------
    # Accessors
    # -----------------------------------------------------------------------

    def node_attr(self, nid: int) -> dict:
        return self._graph.nodes[nid]

    def nodes(self) -> list[tuple[int, dict]]:
        """Return list of (node_id, attr_dict) pairs, sorted by ID."""
        return sorted(self._graph.nodes(data=True), key=lambda x: x[0])

    def edges(self) -> list[tuple[int, int, dict]]:
        """Return list of (source, target, attr_dict) triples."""
        return list(self._graph.edges(data=True))

    @property
    def graph(self) -> nx.DiGraph:
        return self._graph

    def copy(self) -> "CausalGraph":
        """Return a deep-enough copy for evolution (preserves all node/edge data)."""
        new_g = CausalGraph()
        new_g._next_id = self._next_id
        new_g._graph = self._graph.copy()
        # NetworkX .copy() gives a shallow copy of the graph with *copied* attr dicts
        # sufficient since we never mutate individual node dicts in-place
        return new_g

    # -----------------------------------------------------------------------
    # Tick / Batch classification  (mirrors Tick.lean)
    # -----------------------------------------------------------------------

    def incoming_basis_indices(self, nid: int) -> list[int]:
        """
        Return the set of 0-indexed Fano points (0..6, representing e1..e7)
        for which any incoming edge carries a non-zero coefficient.

        Mirrors CausalGraph.incomingBasis in Tick.lean.
        """
        active: set[int] = set()
        for src, tgt, data in self._graph.edges(data=True):
            if tgt == nid:
                op: State = data["operator"]
                # Imaginary basis: component index 1..7 ↔ Fano point 0..6
                for fano_pt in range(7):
                    re, im = op[fano_pt + 1]
                    if re != 0 or im != 0:
                        active.add(fano_pt)
        return list(active)

    def is_batchable(self, indices: list[int]) -> bool:
        """
        Return True iff all Fano points in `indices` lie on a single Fano line.
        Mirrors SubalgebraDetect.batchable.

        Semantics: operators whose imaginary components are collinear on the Fano
        plane form an associative (quaternionic) subalgebra and can be evaluated
        in any order without forcing a time tick.
        """
        if len(indices) <= 1:
            return True
        # Any single line containing all points?
        for line_idx in range(7):
            if all(incident(p, line_idx) for p in indices):
                return True
        return False

    def classify(self, nid: int) -> str:
        """
        Return 'Batch' or 'Tick' for the given node.
        Mirrors CausalGraph.classify in Tick.lean.

        'Tick' means the incoming operators span a non-associative region of the
        octonion algebra, forcing sequential (ordered) evaluation — a logical clock tick.
        """
        indices = self.incoming_basis_indices(nid)
        return "Batch" if self.is_batchable(indices) else "Tick"


# ---------------------------------------------------------------------------
# Graph evolution  (mirrors Update.lean)
# ---------------------------------------------------------------------------

def update_step(G: CausalGraph) -> CausalGraph:
    """
    Single-step structural evolution of the causal graph.
    Mirrors CausalGraph.step in Update.lean.

    Creates a new node (vacuum placeholder, tick_count = last.tick_count + 1)
    and a directed U1 edge from the current last node to the new node.

    If the graph is empty, creates the genesis vacuum node (id=0, tick_count=0).

    Physics note: this is a structural placeholder. The real physics step
    (computing the new node's CO state from incoming operators via Tick/Batch
    classification) is Phase 2B territory. Here we just maintain the DAG invariant.
    """
    new_g = G.copy()
    nodes = [nid for nid, _ in new_g.nodes()]

    if not nodes:
        # Genesis: empty graph → single vacuum node
        new_g.add_node("vacuum", zero_state(), tick_count=0)
        return new_g

    last_id = max(nodes)
    last_tc = new_g.node_attr(last_id)["tick_count"]

    new_id = new_g.add_node("vacuum", zero_state(), tick_count=last_tc + 1)
    new_g.add_edge(last_id, new_id, label="U1", operator=zero_state())
    return new_g


def run(G: CausalGraph, n_steps: int) -> CausalGraph:
    """
    Evolve the causal graph for `n_steps` structural steps.
    Returns the final graph state.
    """
    current = G
    for _ in range(n_steps):
        current = update_step(current)
    return current


# ---------------------------------------------------------------------------
# Analysis helpers
# ---------------------------------------------------------------------------

def count_ticks(G: CausalGraph) -> int:
    """Count the number of nodes classified as Tick."""
    return sum(1 for nid, _ in G.nodes() if G.classify(nid) == "Tick")


def graph_stats(G: CausalGraph) -> dict:
    """Return a summary statistics dict for the graph."""
    nodes = G.nodes()
    labels = [d["label"] for _, d in nodes]
    label_set = set(labels)
    tick_nodes = [nid for nid, _ in nodes if G.classify(nid) == "Tick"]
    return {
        "n_nodes": len(nodes),
        "n_edges": len(G.edges()),
        "label_counts": {lbl: labels.count(lbl) for lbl in label_set},
        "n_ticks": len(tick_nodes),
        "n_batches": len(nodes) - len(tick_nodes),
        "tick_node_ids": tick_nodes,
    }


def is_dag(G: CausalGraph) -> bool:
    """Verify the DAG invariant holds for all edges."""
    return all(src < tgt for src, tgt, _ in G.edges())
