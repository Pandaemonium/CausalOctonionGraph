"""Canonical COG v2 kernel: DAG + CxO(unity) + projective lightcone update.

Basis channels are indexed in binary order:
e000, e001, e010, e011, e100, e101, e110, e111.
Runtime multiplication uses XOR index-channel with oriented-sign lookup.
"""

from __future__ import annotations

import argparse
import json
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

# Oriented Fano triples in one-indexed imaginary basis {1..7}.
# They are locked to XOR-channel closure: for each (a,b,c), c = a xor b.
XOR_ORIENTED_TRIPLES: Tuple[Tuple[int, int, int], ...] = (
    (1, 2, 3),
    (1, 4, 5),
    (1, 6, 7),
    (2, 4, 6),
    (2, 5, 7),
    (3, 4, 7),
    (3, 5, 6),
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

UNITY_ALPHABET: Tuple[GInt, GInt, GInt, GInt, GInt] = (
    ZERO_G,
    ONE_G,
    MINUS_ONE_G,
    I_G,
    MINUS_I_G,
)

PROJECTOR_ID = "pi_unity_axis_dominance_v1"
KERNEL_PROFILE = "cog_v2_projective_unity_v1"

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
    """Deterministic projection from Z[i] onto unity alphabet.

    Policy:
    1) zero stays zero,
    2) dominant axis by absolute component,
    3) axis ties resolved to real axis.
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
    return (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7])


def _xor_sign_table() -> Dict[Tuple[int, int], int]:
    table: Dict[Tuple[int, int], int] = {}
    for a, b, c in XOR_ORIENTED_TRIPLES:
        if (a ^ b) != c:
            raise ValueError(
                f"Invalid XOR oriented triple {(a, b, c)}: expected c == (a xor b)"
            )
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


@dataclass
class World:
    node_ids: List[str]
    parents: Dict[str, List[str]]
    states: Dict[str, CxO]
    event_order: List[str] | None = None
    tick: int = 0


def _interaction_fold_raw(messages: List[CxO]) -> CxO:
    acc = cxo_one()
    for msg in messages:
        acc = cxo_mul(acc, msg)
    return acc


def interaction_fold(messages: List[CxO]) -> CxO:
    return project_cxo_to_unity(_interaction_fold_raw(messages))


def update_rule(current: CxO, parent_messages: List[CxO]) -> CxO:
    payload = interaction_fold(parent_messages)
    return project_cxo_to_unity(cxo_mul(payload, current))


def _canonical_node_order(world: World) -> List[str]:
    if world.event_order is not None:
        return world.event_order
    return sorted(world.node_ids)


def step(world: World) -> World:
    old_states = world.states
    new_states: Dict[str, CxO] = {}
    for nid in _canonical_node_order(world):
        pids = sorted(world.parents.get(nid, []))
        msgs = [old_states[pid] for pid in pids]
        new_states[nid] = update_rule(old_states[nid], msgs)
    return World(
        node_ids=world.node_ids,
        parents=world.parents,
        states=new_states,
        event_order=world.event_order,
        tick=world.tick + 1,
    )


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
    return (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7])


def _serialize_cxo(state: CxO) -> List[List[int]]:
    return [[z.re, z.im] for z in state]


def _validate_graph(node_ids: List[str], parents: Dict[str, List[str]]) -> None:
    if len(set(node_ids)) != len(node_ids):
        raise ValueError("node_ids must be unique.")
    node_set = set(node_ids)
    unknown_parent_refs = []
    for nid in node_ids:
        for pid in parents.get(nid, []):
            if pid not in node_set:
                unknown_parent_refs.append((nid, pid))
    if unknown_parent_refs:
        raise ValueError(f"Unknown parent references found: {unknown_parent_refs}")


def _validate_event_order(node_ids: List[str], event_order: List[str] | None) -> None:
    if event_order is None:
        return
    if len(set(event_order)) != len(event_order):
        raise ValueError("event_order must contain unique node IDs.")
    if set(event_order) != set(node_ids):
        raise ValueError("event_order must be a permutation of node_ids.")


def load_world(path: str, *, enforce_unity_input: bool = True) -> World:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    node_ids = [str(x) for x in raw["node_ids"]]
    parents = {str(k): [str(x) for x in v] for k, v in raw.get("parents", {}).items()}
    event_order = None
    if "event_order" in raw and raw["event_order"] is not None:
        event_order = [str(x) for x in raw["event_order"]]

    for nid in node_ids:
        parents.setdefault(nid, [])
    _validate_graph(node_ids, parents)
    _validate_event_order(node_ids, event_order)

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

    return World(
        node_ids=node_ids,
        parents=parents,
        states=init_state,
        event_order=event_order,
        tick=0,
    )


def save_world(path: str, world: World) -> None:
    out = {
        "tick": world.tick,
        "node_ids": world.node_ids,
        "parents": world.parents,
        "state": {nid: _serialize_cxo(world.states[nid]) for nid in world.node_ids},
        "kernel_profile": KERNEL_PROFILE,
        "projector_id": PROJECTOR_ID,
        "unity_alphabet": [[z.re, z.im] for z in UNITY_ALPHABET],
        "basis_labels": list(BASIS_LABELS),
        "index_channel": "xor",
        "sign_table_profile": "fano_oriented_triples_xor_v1",
        "event_order": world.event_order,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="COG v2 projective-unity kernel runner.")
    parser.add_argument("--input", required=True, help="Path to initial lightcone JSON.")
    parser.add_argument(
        "--steps", required=True, type=int, help="Number of deterministic ticks to run."
    )
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
