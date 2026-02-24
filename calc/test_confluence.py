"""
Claim-level tests for REL-001 confluence/permutation invariance.
"""

from itertools import permutations

from calc.graph_sim import CausalGraph, unit_state


def _graph_with_incoming(ops: list[tuple[int, int]]) -> CausalGraph:
    """
    Build a graph with three sources (0,1,2) and one target (3).
    `ops` entries are (source_node, fano_point_0_indexed).
    """
    G = CausalGraph()
    for _ in range(4):
        G.add_node("vacuum")
    for src, fano_pt in ops:
        G.add_edge(src, 3, "U1", unit_state(fano_pt + 1))
    return G


def test_spacelike_permutations_preserve_tick_classification() -> None:
    # Non-collinear triple {e1,e2,e4} -> Tick.
    base_ops = [(0, 0), (1, 1), (2, 3)]
    baseline = _graph_with_incoming(base_ops).classify(3)
    assert baseline == "Tick"

    for perm in permutations(base_ops):
        assert _graph_with_incoming(list(perm)).classify(3) == baseline


def test_spacelike_permutations_preserve_batch_classification() -> None:
    # Collinear triple {e1,e2,e3} -> Batch.
    base_ops = [(0, 0), (1, 1), (2, 2)]
    baseline = _graph_with_incoming(base_ops).classify(3)
    assert baseline == "Batch"

    for perm in permutations(base_ops):
        assert _graph_with_incoming(list(perm)).classify(3) == baseline
