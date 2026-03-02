"""Experimental closed multiplicative kernel with shared phase per state.

State alphabet:
1) nonzero elements are (global_phase) * (single octonion basis unit),
2) global_phase in {+1, -1, +i, -i},
3) basis unit in {e000..e111}.

This yields a finite closed set of 32 nonzero states under multiplication.
Runtime update uses multiplication only:
1) payload = ordered product of parent states,
2) new = payload * current.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


BASIS_LABELS: Tuple[str, ...] = (
    "e000",
    "e001",
    "e010",
    "e011",
    "e100",
    "e101",
    "e110",
    "e111",
)

PHASE_LABELS: Tuple[str, ...] = ("+1", "-1", "+i", "-i")

XOR_ORIENTED_TRIPLES: Tuple[Tuple[int, int, int], ...] = (
    (1, 2, 3),
    (1, 4, 5),
    (1, 6, 7),
    (2, 4, 6),
    (2, 5, 7),
    (3, 4, 7),
    (3, 5, 6),
)

KERNEL_PROFILE = "cog_v2_phase_shared_unit_loop_v1"
ALPHABET_SIZE = 32


def _phase_mul(pi: int, pj: int) -> int:
    # 0:+1, 1:-1, 2:+i, 3:-i
    table = (
        (0, 1, 2, 3),
        (1, 0, 3, 2),
        (2, 3, 1, 0),
        (3, 2, 0, 1),
    )
    return int(table[int(pi)][int(pj)])


def _phase_neg(pi: int) -> int:
    # multiply by -1
    return _phase_mul(1, int(pi))


def _xor_sign_table() -> Dict[Tuple[int, int], int]:
    table: Dict[Tuple[int, int], int] = {}
    for a, b, c in XOR_ORIENTED_TRIPLES:
        if (a ^ b) != c:
            raise ValueError(f"Invalid XOR triple {(a, b, c)}")
        table[(a, b)] = 1
        table[(b, c)] = 1
        table[(c, a)] = 1
        table[(b, a)] = -1
        table[(c, b)] = -1
        table[(a, c)] = -1
    return table


XOR_SIGN_TABLE = _xor_sign_table()


def _basis_mul(i: int, j: int) -> Tuple[int, int]:
    if i == 0:
        return 1, j
    if j == 0:
        return 1, i
    if i == j:
        return -1, 0
    k = i ^ j
    try:
        return int(XOR_SIGN_TABLE[(i, j)]), int(k)
    except KeyError as exc:
        raise ValueError(f"Invalid basis pair ({i}, {j})") from exc


def _encode(phase_idx: int, basis_idx: int) -> int:
    return int(phase_idx) * 8 + int(basis_idx)


def _decode(elem: int) -> Tuple[int, int]:
    if int(elem) < 0 or int(elem) >= ALPHABET_SIZE:
        raise ValueError(f"Invalid element id: {elem}")
    return int(elem) // 8, int(elem) % 8


def label(elem: int) -> str:
    p, b = _decode(int(elem))
    return f"{PHASE_LABELS[p]}*{BASIS_LABELS[b]}"


def _build_mul_table() -> Tuple[Tuple[int, ...], ...]:
    rows: List[List[int]] = []
    for a in range(ALPHABET_SIZE):
        pa, ba = _decode(a)
        row: List[int] = []
        for b in range(ALPHABET_SIZE):
            pb, bb = _decode(b)
            sign, bk = _basis_mul(ba, bb)
            pk = _phase_mul(pa, pb)
            if sign < 0:
                pk = _phase_neg(pk)
            row.append(_encode(pk, bk))
        rows.append(row)
    return tuple(tuple(int(v) for v in r) for r in rows)


MUL_TABLE = _build_mul_table()


def multiply(a: int, b: int) -> int:
    return int(MUL_TABLE[int(a)][int(b)])


def fold_product(messages: List[int]) -> int:
    acc = _encode(0, 0)  # +1*e000
    for msg in messages:
        acc = multiply(acc, int(msg))
    return int(acc)


@dataclass
class World:
    node_ids: List[str]
    parents: Dict[str, List[str]]
    states: Dict[str, int]
    event_order: List[str] | None = None
    tick: int = 0


def _canonical_node_order(world: World) -> List[str]:
    if world.event_order is not None:
        return world.event_order
    return sorted(world.node_ids)


def step(world: World) -> World:
    old = world.states
    nxt: Dict[str, int] = {}
    for nid in _canonical_node_order(world):
        pids = sorted(world.parents.get(nid, []))
        payload = fold_product([old[pid] for pid in pids])
        nxt[nid] = multiply(payload, old[nid])
    return World(
        node_ids=world.node_ids,
        parents=world.parents,
        states=nxt,
        event_order=world.event_order,
        tick=world.tick + 1,
    )


def run(world: World, steps: int) -> World:
    cur = world
    for _ in range(int(steps)):
        cur = step(cur)
    return cur

