"""Octavian-240 candidate alphabet over canonical XOR/Fano multiplication.

Alphabet construction (240 states):
1) ±e_i, i=0..7  (16 states)
2) (±e0 ± ea ± eb ± ec)/2 for each Fano line (a,b,c) (112 states)
3) (±ea ±eb ±ec ±ed)/2 for each complement-of-line quadruple (112 states)

Runtime update is multiplication-only. Under canonical multiplication in this
basis, this 240-state set is not closed; diagnostics are exposed explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
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

KERNEL_PROFILE = "cog_v2_octavian240_candidate_v1"

Oct = Tuple[Fraction, Fraction, Fraction, Fraction, Fraction, Fraction, Fraction, Fraction]


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
    p = oct_mul(x, oct_conj(x))
    return p[0]


def oct_norm_residual_zero(x: Oct) -> bool:
    p = oct_mul(x, oct_conj(x))
    return all(p[i] == 0 for i in range(1, 8))


def _build_alphabet() -> List[Oct]:
    vals: List[Oct] = []

    # 1) ±e_i
    for i in range(8):
        v = [Fraction(0, 1) for _ in range(8)]
        v[i] = Fraction(1, 1)
        vals.append((v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7]))
        v = [Fraction(0, 1) for _ in range(8)]
        v[i] = Fraction(-1, 1)
        vals.append((v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7]))

    # 2) (±e0 ±ea ±eb ±ec)/2 for each line.
    for a, b, c in XOR_ORIENTED_TRIPLES:
        for s0 in (1, -1):
            for s1 in (1, -1):
                for s2 in (1, -1):
                    for s3 in (1, -1):
                        v = [Fraction(0, 1) for _ in range(8)]
                        v[0] = Fraction(s0, 2)
                        v[a] = Fraction(s1, 2)
                        v[b] = Fraction(s2, 2)
                        v[c] = Fraction(s3, 2)
                        vals.append((v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7]))

    # 3) (±ea ±eb ±ec ±ed)/2 for complement quadruple of each line.
    imag = set(range(1, 8))
    for a, b, c in XOR_ORIENTED_TRIPLES:
        comp = sorted(imag - {a, b, c})
        for s1 in (1, -1):
            for s2 in (1, -1):
                for s3 in (1, -1):
                    for s4 in (1, -1):
                        v = [Fraction(0, 1) for _ in range(8)]
                        for idx, s in zip(comp, (s1, s2, s3, s4)):
                            v[idx] = Fraction(s, 2)
                        vals.append((v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7]))

    # de-duplicate deterministically while preserving order
    seen = set()
    out: List[Oct] = []
    for x in vals:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


ALPHABET: List[Oct] = _build_alphabet()
ALPHABET_SIZE = len(ALPHABET)
if ALPHABET_SIZE != 240:
    raise ValueError(f"Expected 240 alphabet states, got {ALPHABET_SIZE}")

ALPHABET_INDEX: Dict[Oct, int] = {x: i for i, x in enumerate(ALPHABET)}


def in_alphabet(x: Oct) -> bool:
    return x in ALPHABET_INDEX


def elem_label(elem_id: int) -> str:
    x = ALPHABET[int(elem_id)]
    pieces = [f"{x[i]}*{BASIS_LABELS[i]}" for i in range(8) if x[i] != 0]
    return " + ".join(pieces) if pieces else "0"


def multiply_ids(a_id: int, b_id: int) -> int | None:
    prod = oct_mul(ALPHABET[int(a_id)], ALPHABET[int(b_id)])
    return ALPHABET_INDEX.get(prod)


def multiply_ids_strict(a_id: int, b_id: int) -> int:
    out = multiply_ids(int(a_id), int(b_id))
    if out is None:
        raise ValueError(f"Product leaves 240 alphabet: a={a_id}, b={b_id}")
    return int(out)


def fold_product(messages: List[int], strict: bool = True) -> int | None:
    acc = 0  # +e000
    for msg in messages:
        nxt = multiply_ids(acc, int(msg))
        if nxt is None:
            if strict:
                raise ValueError(f"Fold left alphabet: acc={acc}, msg={msg}")
            return None
        acc = int(nxt)
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


def step(world: World, strict: bool = True) -> World | None:
    old = world.states
    nxt: Dict[str, int] = {}
    for nid in _canonical_node_order(world):
        pids = sorted(world.parents.get(nid, []))
        payload = fold_product([old[pid] for pid in pids], strict=strict)
        if payload is None:
            if strict:
                raise ValueError(f"Payload left alphabet at node={nid}")
            return None
        out = multiply_ids(int(payload), int(old[nid]))
        if out is None:
            if strict:
                raise ValueError(f"Update left alphabet at node={nid}")
            return None
        nxt[nid] = int(out)
    return World(
        node_ids=world.node_ids,
        parents=world.parents,
        states=nxt,
        event_order=world.event_order,
        tick=world.tick + 1,
    )

