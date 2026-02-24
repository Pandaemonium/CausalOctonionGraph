"""
Claim-level tests for GEN-001 triality structure.
"""

from calc.conftest import WITT_PAIRS
from calc.triality_map import g2_color_cycle, verify_order


def _perm_from_matrix(T) -> dict[int, int]:
    perm: dict[int, int] = {}
    for src in range(8):
        for dst in range(8):
            if T[dst, src] > 0.5:
                perm[src] = dst
                break
    return perm


def test_triality_order_3() -> None:
    T = g2_color_cycle()
    is_order_3, order = verify_order(T, expected_order=3)
    assert is_order_3
    assert order == 3


def test_triality_fixes_scalar_and_vacuum_axes() -> None:
    T = g2_color_cycle()
    perm = _perm_from_matrix(T)
    assert perm[0] == 0  # e0 fixed
    assert perm[7] == 7  # e7 fixed


def test_triality_cycles_witt_pairs() -> None:
    T = g2_color_cycle()
    perm = _perm_from_matrix(T)

    witt_state_pairs = [frozenset(fp + 1 for fp in pair) for pair in WITT_PAIRS]
    witt_set = set(witt_state_pairs)

    for pair in witt_state_pairs:
        mapped = frozenset(perm[idx] for idx in pair)
        assert mapped in witt_set
