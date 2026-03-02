"""Closed 240-unit Octavian alphabet over a valid cyclic octonion basis.

This module uses:
1) A cyclic Fano orientation (composition-compatible octonion multiplication),
2) An explicit Z-basis for an Octavian integer lattice,
3) Exact extraction of norm-1 lattice units (240 states).

Runtime update is multiplication-only over that finite closed alphabet.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
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

# Cyclic Fano orientation:
# e_i = e_{i+1} e_{i+3} mod 7 (indices 1..7)
CYCLIC_ORIENTED_TRIPLES: Tuple[Tuple[int, int, int], ...] = (
    (1, 2, 4),
    (2, 3, 5),
    (3, 4, 6),
    (4, 5, 7),
    (5, 6, 1),
    (6, 7, 2),
    (7, 1, 3),
)

KERNEL_PROFILE = "cog_v2_octavian240_closed_v1"

Oct = Tuple[Fraction, Fraction, Fraction, Fraction, Fraction, Fraction, Fraction, Fraction]


def _cyclic_sign_table() -> Dict[Tuple[int, int], int]:
    table: Dict[Tuple[int, int], int] = {}
    for a, b, c in CYCLIC_ORIENTED_TRIPLES:
        table[(a, b)] = 1
        table[(b, c)] = 1
        table[(c, a)] = 1
        table[(b, a)] = -1
        table[(c, b)] = -1
        table[(a, c)] = -1
    return table


CYCLIC_SIGN_TABLE = _cyclic_sign_table()


def _basis_mul(i: int, j: int) -> Tuple[int, int]:
    if i == 0:
        return 1, j
    if j == 0:
        return 1, i
    if i == j:
        return -1, 0

    for a, b, c in CYCLIC_ORIENTED_TRIPLES:
        line = {a, b, c}
        if i in line and j in line:
            k = next(t for t in (a, b, c) if t not in (i, j))
            return int(CYCLIC_SIGN_TABLE[(i, j)]), int(k)
    raise ValueError(f"Invalid imaginary basis pair ({i}, {j})")


def oct_mul(a: Oct, b: Oct) -> Oct:
    out = [Fraction(0, 1) for _ in range(8)]
    for i, ai in enumerate(a):
        if ai == 0:
            continue
        for j, bj in enumerate(b):
            if bj == 0:
                continue
            s, k = _basis_mul(i, j)
            out[k] += Fraction(s, 1) * ai * bj
    return (out[0], out[1], out[2], out[3], out[4], out[5], out[6], out[7])


def oct_conj(x: Oct) -> Oct:
    return (x[0], -x[1], -x[2], -x[3], -x[4], -x[5], -x[6], -x[7])


def oct_norm_scalar(x: Oct) -> Fraction:
    return oct_mul(x, oct_conj(x))[0]


def oct_norm_residual_zero(x: Oct) -> bool:
    p = oct_mul(x, oct_conj(x))
    return all(p[i] == 0 for i in range(1, 8))


def _invert_q_matrix(a: Tuple[Tuple[int, ...], ...]) -> Tuple[Tuple[Fraction, ...], ...]:
    n = len(a)
    aug: List[List[Fraction]] = []
    for r in range(n):
        row = [Fraction(a[r][c], 1) for c in range(n)]
        row.extend(Fraction(1 if r == c else 0, 1) for c in range(n))
        aug.append(row)

    for col in range(n):
        piv = None
        for r in range(col, n):
            if aug[r][col] != 0:
                piv = r
                break
        if piv is None:
            raise ValueError("Singular matrix in Octavian basis inversion.")
        aug[col], aug[piv] = aug[piv], aug[col]
        f = aug[col][col]
        aug[col] = [v / f for v in aug[col]]
        for r in range(n):
            if r == col:
                continue
            fac = aug[r][col]
            if fac == 0:
                continue
            aug[r] = [aug[r][k] - fac * aug[col][k] for k in range(2 * n)]

    return tuple(tuple(aug[r][n + c] for c in range(n)) for r in range(n))


# Octavian lattice basis vectors, scaled by 2, as columns in e000..e111 coordinates.
# Derived from a standard Octavian Z-basis in a cyclic octonion frame.
_BASIS_MATRIX_TWICE: Tuple[Tuple[int, ...], ...] = (
    (0, 0, 0, 0, 0, 0, 0, -1),
    (-1, -1, 0, 1, 0, 0, -1, 1),
    (0, -1, 1, 0, -1, 1, 0, 0),
    (0, 0, 1, -1, 1, 0, -1, 0),
    (0, -1, 0, 1, 0, -1, 1, -1),
    (1, 0, -1, 1, -1, 1, -1, 0),
    (1, 0, 0, 0, 0, -1, 0, 1),
    (1, -1, -1, 0, 1, 0, 0, 0),
)

_BASIS_MATRIX_INV = _invert_q_matrix(_BASIS_MATRIX_TWICE)


def _mat_vec_mul_q(
    m: Tuple[Tuple[Fraction, ...], ...], v: Tuple[int, ...]
) -> Tuple[Fraction, ...]:
    n = len(v)
    return tuple(
        sum(m[r][c] * Fraction(v[c], 1) for c in range(n)) for r in range(n)
    )


def _build_alphabet() -> List[Oct]:
    vals: List[Oct] = []
    for w in product(range(-2, 3), repeat=8):
        if sum(t * t for t in w) != 4:
            continue
        pre = _mat_vec_mul_q(_BASIS_MATRIX_INV, tuple(int(t) for t in w))
        if not all(v.denominator == 1 for v in pre):
            continue
        x = tuple(Fraction(int(wi), 2) for wi in w)
        vals.append(x)  # type: ignore[arg-type]
    vals = sorted(set(vals))
    return vals


ALPHABET: List[Oct] = _build_alphabet()
ALPHABET_SIZE = len(ALPHABET)
if ALPHABET_SIZE != 240:
    raise ValueError(f"Expected 240 alphabet states, got {ALPHABET_SIZE}")

ALPHABET_INDEX: Dict[Oct, int] = {x: i for i, x in enumerate(ALPHABET)}

_ONE: Oct = (
    Fraction(1, 1),
    Fraction(0, 1),
    Fraction(0, 1),
    Fraction(0, 1),
    Fraction(0, 1),
    Fraction(0, 1),
    Fraction(0, 1),
    Fraction(0, 1),
)
if _ONE not in ALPHABET_INDEX:
    raise ValueError("Identity element not present in Octavian 240 alphabet.")
IDENTITY_ID = int(ALPHABET_INDEX[_ONE])


def in_alphabet(x: Oct) -> bool:
    return x in ALPHABET_INDEX


def elem_label(elem_id: int) -> str:
    x = ALPHABET[int(elem_id)]
    pieces = [f"{x[i]}*{BASIS_LABELS[i]}" for i in range(8) if x[i] != 0]
    return " + ".join(pieces) if pieces else "0"


def multiply_ids(a_id: int, b_id: int) -> int:
    prod = oct_mul(ALPHABET[int(a_id)], ALPHABET[int(b_id)])
    out = ALPHABET_INDEX.get(prod)
    if out is None:
        raise ValueError(f"Product left closed 240 alphabet: a={a_id}, b={b_id}")
    return int(out)


def fold_product(messages: List[int]) -> int:
    acc = int(IDENTITY_ID)
    for msg in messages:
        acc = multiply_ids(acc, int(msg))
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
        out = multiply_ids(int(payload), int(old[nid]))
        nxt[nid] = int(out)
    return World(
        node_ids=world.node_ids,
        parents=world.parents,
        states=nxt,
        event_order=world.event_order,
        tick=world.tick + 1,
    )

