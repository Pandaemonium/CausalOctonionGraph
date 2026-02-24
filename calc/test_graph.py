"""
Graph-level claim tests for DIST-001 and DAG-001.
"""

import networkx as nx

from calc.graph_sim import CausalGraph, is_dag, run, update_step, zero_state


def _dist(G: CausalGraph, src: int, dst: int) -> int:
    """Shortest directed-path length from src to dst (assumes path exists)."""
    return nx.shortest_path_length(G.graph, source=src, target=dst)


def test_distance_triangle() -> None:
    """
    DIST-001:
    If paths a->b, b->c, and a->c exist, then dist(a,c) <= dist(a,b)+dist(b,c).
    """
    G = CausalGraph()
    for _ in range(4):
        G.add_node("vacuum")

    # a=0, b=1, c=2 with both direct and composed paths.
    G.add_edge(0, 1, "U1", zero_state())
    G.add_edge(1, 2, "U1", zero_state())
    G.add_edge(0, 2, "U1", zero_state())

    dab = _dist(G, 0, 1)
    dbc = _dist(G, 1, 2)
    dac = _dist(G, 0, 2)
    assert dac <= dab + dbc

    # Another non-trivial triple a=0, b=2, c=3.
    G.add_edge(2, 3, "U1", zero_state())
    G.add_edge(0, 3, "U1", zero_state())

    dab = _dist(G, 0, 2)
    dbc = _dist(G, 2, 3)
    dac = _dist(G, 0, 3)
    assert dac <= dab + dbc


def test_step_acyclic() -> None:
    """DAG-001: update_step preserves the source<target acyclicity invariant."""
    G = CausalGraph()
    G.add_node("vacuum")
    G = run(G, 25)
    assert is_dag(G)

    G1 = update_step(G)
    assert is_dag(G1)
    for src, dst, _ in G1.edges():
        assert src < dst
