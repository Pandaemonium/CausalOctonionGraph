"""Projective-unity kernel: deterministic DAG evolution in C x O over unity.

Axiom profile:
1) Universe is a directed acyclic graph (DAG),
2) Node states live in C x O over a discrete unity alphabet,
3) Update rule is projection on the incoming light cone.

This file is intentionally small and executable:
1) load a full predetermined lightcone state,
2) evolve by a deterministic projected update rule,
3) write final state.
"""

from __future__ import annotations

from dataclasses import dataclass
import argparse
import json
from typing import Dict, List, Tuple


# Canonical directed Fano cycles (CONVENTIONS.md ordering).
FANO_CYCLES: Tuple[Tuple[int, int, int], ...] = (
    (1, 2, 4),
    (2, 3, 5),
    (3, 4, 6),
    (4, 5, 7),
    (5, 6, 1),
    (6, 7, 2),
    (7, 1, 3),
)


@dataclass(frozen=True)
class GInt:
    re: int
    im: int


ZERO_G = GInt(0, 0)
ONE_G = GInt(1, 0)
MINUS_ONE_G = GInt(-1, 0)
I_G = GInt(0, 1)
MINUS_I_G = GInt(0, -1)

# Unity alphabet for this kernel profile.
UNITY_ALPHABET: Tuple[GInt, GInt, GInt, GInt, GInt] = (
    ZERO_G,
    ONE_G,
    MINUS_ONE_G,
    I_G,
    MINUS_I_G,
)

PROJECTOR_ID = "pi_unity_axis_dominance_v1"
KERNEL_PROFILE = "projective_unity_v1"

# CxO state: 8 octonion slots with Gaussian-integer coefficients.
CxO = Tuple[GInt, GInt, GInt, GInt, GInt, GInt, GInt, GInt]


def g_add(a: GInt, b: GInt) -> GInt:
    return GInt(a.re + b.re, a.im + b.im)


def g_neg(a: GInt) -> GInt:
    return GInt(-a.re, -a.im)


def g_mul(a: GInt, b: GInt) -> GInt:
    return GInt(a.re * b.re - a.im * b.im, a.re * b.im + a.im * b.re)


def g_is_zero(a: GInt) -> bool:
    return a.re == 0 and a.im == 0


def is_unity_coeff(a: GInt) -> bool:
    return any(a == v for v in UNITY_ALPHABET)


def project_g_to_unity(a: GInt) -> GInt:
    """Deterministic projection from Z[i] to {0, +1, -1, +i, -i}.

    Policy:
    1) zero remains zero,
    2) choose dominant axis by |re| vs |im|,
    3) ties resolve to the real axis for deterministic replay.
    """
    if g_is_zero(a):
        return ZERO_G
    ar = abs(a.re)
    ai = abs(a.im)
    if ar >= ai:
        return ONE_G if a.re >= 0 else MINUS_ONE_G
    return I_G if a.im >= 0 else MINUS_I_G


def cxo_one() -> CxO:
    return (ONE_G, ZERO_G, ZERO_G, ZERO_G, ZERO_G, ZERO_G, ZERO_G, ZERO_G)


def cxo_is_unity(state: CxO) -> bool:
    return all(is_unity_coeff(z) for z in state)


def project_cxo_to_unity(state: CxO) -> CxO:
    vals = [project_g_to_unity(z) for z in state]
    return (
        vals[0],
        vals[1],
        vals[2],
        vals[3],
        vals[4],
        vals[5],
        vals[6],
        vals[7],
    )


def _pair_table() -> Dict[Tuple[int, int], Tuple[int, int]]:
    """Map basis pair (i,j) -> (sign, k) for e_i * e_j = sign * e_k."""
    table: Dict[Tuple[int, int], Tuple[int, int]] = {}
    for a, b, c in FANO_CYCLES:
        # Cyclic orientation is positive.
        table[(a, b)] = (1, c)
        table[(b, c)] = (1, a)
        table[(c, a)] = (1, b)
        # Anti-cyclic orientation is negative.
        table[(b, a)] = (-1, c)
        table[(c, b)] = (-1, a)
        table[(a, c)] = (-1, b)
    return table


PAIR_TABLE = _pair_table()


def basis_mul(i: int, j: int) -> Tuple[int, int]:
    """Multiply basis units e_i * e_j for i,j in [0,7]."""
    if i == 0:
        return 1, j
    if j == 0:
        return 1, i
    if i == j:
        return -1, 0
    try:
        return PAIR_TABLE[(i, j)]
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
    return (
        out[0],
        out[1],
        out[2],
        out[3],
        out[4],
        out[5],
        out[6],
        out[7],
    )


@dataclass
class World:
    node_ids: List[str]
    parents: Dict[str, List[str]]
    states: Dict[str, CxO]
    tick: int = 0


def _interaction_fold_raw(messages: List[CxO]) -> CxO:
    acc = cxo_one()
    for msg in messages:
        acc = cxo_mul(acc, msg)
    return acc


def interaction_fold(messages: List[CxO]) -> CxO:
    """Projective lightcone fold: Pi(fold(messages))."""
    return project_cxo_to_unity(_interaction_fold_raw(messages))


def update_rule(current: CxO, parent_messages: List[CxO]) -> CxO:
    """Projective update: Pi(Pi(fold(parents)) * current)."""
    payload = interaction_fold(parent_messages)
    return project_cxo_to_unity(cxo_mul(payload, current))


def step(world: World) -> World:
    old_states = world.states
    new_states: Dict[str, CxO] = {}
    # Canonical deterministic ordering.
    for nid in sorted(world.node_ids):
        pids = sorted(world.parents.get(nid, []))
        msgs = [old_states[pid] for pid in pids]
        new_states[nid] = update_rule(old_states[nid], msgs)
    return World(node_ids=world.node_ids, parents=world.parents, states=new_states, tick=world.tick + 1)


def run(world: World, steps: int) -> World:
    cur = world
    for _ in range(steps):
        cur = step(cur)
    return cur


def _parse_int_coeff(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(
            f"{label} must be an integer literal (no decimal point), got {value!r}."
        )
    return value


def _parse_cxo(raw: List[List[object]]) -> CxO:
    if len(raw) != 8:
        raise ValueError("Each CxO state must have 8 basis coefficients.")
    vals = []
    for basis_idx, pair in enumerate(raw):
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError("Each coefficient must be [re, im].")
        re_part = _parse_int_coeff(pair[0], f"basis[{basis_idx}].re")
        im_part = _parse_int_coeff(pair[1], f"basis[{basis_idx}].im")
        vals.append(GInt(re_part, im_part))
    return (
        vals[0],
        vals[1],
        vals[2],
        vals[3],
        vals[4],
        vals[5],
        vals[6],
        vals[7],
    )


def _serialize_cxo(state: CxO) -> List[List[int]]:
    return [[z.re, z.im] for z in state]


def load_world(path: str, *, enforce_unity_input: bool = True) -> World:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    node_ids = [str(x) for x in raw["node_ids"]]
    parents = {str(k): [str(x) for x in v] for k, v in raw["parents"].items()}

    init_state: Dict[str, CxO] = {}
    for k, v in raw["init_state"].items():
        nid = str(k)
        parsed = _parse_cxo(v)
        if enforce_unity_input:
            if not cxo_is_unity(parsed):
                raise ValueError(
                    f"init_state[{nid!r}] is not in unity alphabet; "
                    f"use --allow-nonunity-input to project inputs."
                )
            init_state[nid] = parsed
        else:
            init_state[nid] = project_cxo_to_unity(parsed)

    missing = [nid for nid in node_ids if nid not in init_state]
    if missing:
        raise ValueError(f"Missing init_state entries for node_ids: {missing}")
    return World(node_ids=node_ids, parents=parents, states=init_state, tick=0)


def save_world(path: str, world: World) -> None:
    out = {
        "tick": world.tick,
        "node_ids": world.node_ids,
        "parents": world.parents,
        "state": {nid: _serialize_cxo(world.states[nid]) for nid in world.node_ids},
        "kernel_profile": KERNEL_PROFILE,
        "projector_id": PROJECTOR_ID,
        "unity_alphabet": [[z.re, z.im] for z in UNITY_ALPHABET],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Projective-unity CxO kernel runner.")
    parser.add_argument("--input", required=True, help="Path to initial lightcone JSON.")
    parser.add_argument("--steps", required=True, type=int, help="Number of deterministic ticks to run.")
    parser.add_argument("--output", required=True, help="Path to output JSON.")
    parser.add_argument(
        "--allow-nonunity-input",
        action="store_true",
        help="Project non-unity inputs onto the unity alphabet before running.",
    )
    args = parser.parse_args()

    if args.steps < 0:
        raise ValueError("--steps must be >= 0")

    world0 = load_world(args.input, enforce_unity_input=not args.allow_nonunity_input)
    worldN = run(world0, args.steps)
    save_world(args.output, worldN)


if __name__ == "__main__":
    main()

