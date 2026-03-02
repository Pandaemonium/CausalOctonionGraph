"""COG v3 kernel: closed Octavian-240 basis, multiplication-only update.

Design notes:
- Uses a convention transform on top of `cog_v2` closed-240 kernel.
- Keeps exact finite closed alphabet (240 states) and multiplicative update only.
- No additive folding outside multiplicative accumulation, no projector snapping.

Convention transform chosen to satisfy positive triplets:
  e110 * e111 = +e001
  e100 * e111 = +e011
  e010 * e111 = +e101
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, List, Tuple

from cog_v2.python import kernel_octavian240_closed_v1 as base


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

# Basis convention map:
# f_i = SIGN[i] * e_{NEW_TO_OLD[i]}
# where e_* is base kernel basis and f_* is v3 basis.
NEW_TO_OLD: Tuple[int, ...] = (0, 1, 2, 3, 4, 7, 5, 6)
SIGN: Tuple[int, ...] = (1, 1, 1, 1, 1, 1, 1, 1)

KERNEL_PROFILE = "cog_v3_octavian240_multiplicative_v1"
CONVENTION_ID = "v3_octavian240_perm_0-1-2-3-4-7-5-6_sign_all_plus"

Oct = Tuple[Fraction, Fraction, Fraction, Fraction, Fraction, Fraction, Fraction, Fraction]


def _old_to_new(x_old: base.Oct) -> Oct:
    # new[i] = sign[i] * old[NEW_TO_OLD[i]]
    y = [Fraction(0, 1) for _ in range(8)]
    for i in range(8):
        y[i] = Fraction(SIGN[i], 1) * x_old[NEW_TO_OLD[i]]
    return (y[0], y[1], y[2], y[3], y[4], y[5], y[6], y[7])


def _new_to_old(x_new: Oct) -> base.Oct:
    # old[NEW_TO_OLD[i]] = sign[i] * new[i]
    y = [Fraction(0, 1) for _ in range(8)]
    for i in range(8):
        y[NEW_TO_OLD[i]] = Fraction(SIGN[i], 1) * x_new[i]
    return (y[0], y[1], y[2], y[3], y[4], y[5], y[6], y[7])


def oct_mul(a: Oct, b: Oct) -> Oct:
    a_old = _new_to_old(a)
    b_old = _new_to_old(b)
    p_old = base.oct_mul(a_old, b_old)
    return _old_to_new(p_old)


def oct_conj(x: Oct) -> Oct:
    return (x[0], -x[1], -x[2], -x[3], -x[4], -x[5], -x[6], -x[7])


def oct_norm_scalar(x: Oct) -> Fraction:
    return oct_mul(x, oct_conj(x))[0]


def oct_norm_residual_zero(x: Oct) -> bool:
    p = oct_mul(x, oct_conj(x))
    return all(p[i] == 0 for i in range(1, 8))


ALPHABET: List[Oct] = [_old_to_new(x) for x in base.ALPHABET]
ALPHABET_SIZE = len(ALPHABET)
if ALPHABET_SIZE != 240:
    raise ValueError(f"Expected 240 alphabet states, got {ALPHABET_SIZE}")
if len(set(ALPHABET)) != 240:
    raise ValueError("Convention transform did not preserve alphabet bijection.")

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
    raise ValueError("Identity element not present in v3 alphabet.")
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
        raise ValueError(f"Product left v3 closed alphabet: a={a_id}, b={b_id}")
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
    convention_id: str = CONVENTION_ID
    tick: int = 0


def assert_convention_id(convention_id: str) -> None:
    if str(convention_id) != CONVENTION_ID:
        raise ValueError(
            f"Convention mismatch: got={convention_id}, expected={CONVENTION_ID}"
        )


def _canonical_node_order(world: World) -> List[str]:
    if world.event_order is not None:
        return world.event_order
    return sorted(world.node_ids)


def step(world: World) -> World:
    assert_convention_id(world.convention_id)
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
        convention_id=world.convention_id,
        tick=world.tick + 1,
    )


def _basis_unit_id(i: int, sign: int = 1) -> int:
    v = [Fraction(0, 1) for _ in range(8)]
    v[int(i)] = Fraction(int(sign), 1)
    return int(ALPHABET_INDEX[tuple(v)])  # type: ignore[index]


def basis_triplet_sign(i: int, j: int, k: int) -> int:
    a = ALPHABET[_basis_unit_id(int(i), +1)]
    b = ALPHABET[_basis_unit_id(int(j), +1)]
    p = oct_mul(a, b)
    nz = [idx for idx, c in enumerate(p) if c != 0]
    if len(nz) != 1:
        raise ValueError(f"Basis product not monomial for ({i}, {j}).")
    out_idx = int(nz[0])
    coeff = p[out_idx]
    if out_idx != int(k):
        raise ValueError(f"Triplet mismatch: got {out_idx}, expected {k}.")
    return 1 if coeff > 0 else -1


TARGET_POSITIVE_TRIPLETS: Tuple[Tuple[int, int, int], ...] = (
    (6, 7, 1),  # e110*e111=+e001
    (4, 7, 3),  # e100*e111=+e011
    (2, 7, 5),  # e010*e111=+e101
)
