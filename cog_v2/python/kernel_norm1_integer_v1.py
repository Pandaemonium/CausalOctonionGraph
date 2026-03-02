"""Experimental COG kernel: CxO over Z[i], multiplicative update, no projector.

This module is an exploratory lane only. It keeps the same XOR/Fano basis
multiplication but removes project-to-unity from the update rule.
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

XOR_ORIENTED_TRIPLES: Tuple[Tuple[int, int, int], ...] = (
    (1, 2, 3),
    (1, 4, 5),
    (1, 6, 7),
    (2, 4, 6),
    (2, 5, 7),
    (3, 4, 7),
    (3, 5, 6),
)

KERNEL_PROFILE = "cog_v2_norm1_integer_multiplicative_v1"


@dataclass(frozen=True)
class GInt:
    re: int
    im: int


ZERO_G = GInt(0, 0)
ONE_G = GInt(1, 0)

CxO = Tuple[GInt, GInt, GInt, GInt, GInt, GInt, GInt, GInt]


def g_add(a: GInt, b: GInt) -> GInt:
    return GInt(a.re + b.re, a.im + b.im)


def g_neg(a: GInt) -> GInt:
    return GInt(-a.re, -a.im)


def g_mul(a: GInt, b: GInt) -> GInt:
    return GInt(a.re * b.re - a.im * b.im, a.re * b.im + a.im * b.re)


def g_sq(a: GInt) -> GInt:
    return g_mul(a, a)


def g_is_zero(a: GInt) -> bool:
    return a.re == 0 and a.im == 0


def g_abs_linf(a: GInt) -> int:
    return int(max(abs(a.re), abs(a.im)))


def cxo_one() -> CxO:
    return (ONE_G, ZERO_G, ZERO_G, ZERO_G, ZERO_G, ZERO_G, ZERO_G, ZERO_G)


def _xor_sign_table() -> Dict[Tuple[int, int], int]:
    table: Dict[Tuple[int, int], int] = {}
    for a, b, c in XOR_ORIENTED_TRIPLES:
        if (a ^ b) != c:
            raise ValueError(f"Invalid oriented triple {(a, b, c)} for XOR basis.")
        table[(a, b)] = 1
        table[(b, c)] = 1
        table[(c, a)] = 1
        table[(b, a)] = -1
        table[(c, b)] = -1
        table[(a, c)] = -1
    return table


XOR_SIGN_TABLE = _xor_sign_table()


def basis_mul(i: int, j: int) -> Tuple[int, int]:
    if i == 0:
        return 1, j
    if j == 0:
        return 1, i
    if i == j:
        return -1, 0
    k = i ^ j
    try:
        return XOR_SIGN_TABLE[(i, j)], k
    except KeyError as exc:
        raise ValueError(f"Invalid basis pair ({i}, {j})") from exc


def cxo_mul(a: CxO, b: CxO) -> CxO:
    out = [ZERO_G for _ in range(8)]
    for i, ai in enumerate(a):
        if g_is_zero(ai):
            continue
        for j, bj in enumerate(b):
            if g_is_zero(bj):
                continue
            sign, k = basis_mul(i, j)
            term = g_mul(ai, bj)
            if sign < 0:
                term = g_neg(term)
            out[k] = g_add(out[k], term)
    return (out[0], out[1], out[2], out[3], out[4], out[5], out[6], out[7])


def cxo_bar(x: CxO) -> CxO:
    return (x[0], g_neg(x[1]), g_neg(x[2]), g_neg(x[3]), g_neg(x[4]), g_neg(x[5]), g_neg(x[6]), g_neg(x[7]))


def cxo_composition_norm(x: CxO) -> GInt:
    # N(x) = x * x_bar, scalar component under composition algebra law.
    prod = cxo_mul(x, cxo_bar(x))
    return prod[0]


def cxo_norm_residual_linf(x: CxO) -> int:
    prod = cxo_mul(x, cxo_bar(x))
    return int(max(g_abs_linf(prod[i]) for i in range(1, 8)))


def cxo_is_norm_one(x: CxO) -> bool:
    n = cxo_composition_norm(x)
    return n == ONE_G and cxo_norm_residual_linf(x) == 0


def cxo_max_coeff_linf(x: CxO) -> int:
    return int(max(g_abs_linf(v) for v in x))


@dataclass
class World:
    node_ids: List[str]
    parents: Dict[str, List[str]]
    states: Dict[str, CxO]
    event_order: List[str] | None = None
    tick: int = 0


def interaction_fold(messages: List[CxO]) -> CxO:
    acc = cxo_one()
    for msg in messages:
        acc = cxo_mul(acc, msg)
    return acc


def update_rule(current: CxO, parent_messages: List[CxO]) -> CxO:
    payload = interaction_fold(parent_messages)
    return cxo_mul(payload, current)


def _canonical_node_order(world: World) -> List[str]:
    if world.event_order is not None:
        return world.event_order
    return sorted(world.node_ids)


def step(world: World) -> World:
    old = world.states
    nxt: Dict[str, CxO] = {}
    for nid in _canonical_node_order(world):
        pids = sorted(world.parents.get(nid, []))
        msgs = [old[pid] for pid in pids]
        nxt[nid] = update_rule(old[nid], msgs)
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

