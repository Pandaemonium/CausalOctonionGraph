"""Preregistered-order unity-projection kernel for CxO lightcone evolution.

Purpose:
1) enforce superdeterministic event ordering from initial-state metadata,
2) run deterministic CxO updates under that immutable plan,
3) project coefficients to unit CxO values via a declared projector policy.

This profile is exploratory/non-canonical unless explicitly promoted by policy.
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

# CxO state: 8 octonion slots with Gaussian-integer coefficients.
CxO = Tuple[GInt, GInt, GInt, GInt, GInt, GInt, GInt, GInt]

# Allowed projection policies for this profile.
PROJECTION_POLICIES = {"fold_and_update", "fold_only", "update_only"}


def g_add(a: GInt, b: GInt) -> GInt:
    return GInt(a.re + b.re, a.im + b.im)


def g_neg(a: GInt) -> GInt:
    return GInt(-a.re, -a.im)


def g_mul(a: GInt, b: GInt) -> GInt:
    return GInt(a.re * b.re - a.im * b.im, a.re * b.im + a.im * b.re)


def g_is_zero(a: GInt) -> bool:
    return a.re == 0 and a.im == 0


def project_g_to_unity(a: GInt) -> GInt:
    """
    Deterministic projection from Z[i] to {0, +1, -1, +i, -i}.

    Rule:
    1) zero remains zero,
    2) choose dominant axis by |re| vs |im|,
    3) ties resolve to real axis.
    """
    if g_is_zero(a):
        return ZERO_G
    ar = abs(a.re)
    ai = abs(a.im)
    if ar >= ai:
        return ONE_G if a.re >= 0 else MINUS_ONE_G
    return I_G if a.im >= 0 else MINUS_I_G


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


def cxo_one() -> CxO:
    return (ONE_G, ZERO_G, ZERO_G, ZERO_G, ZERO_G, ZERO_G, ZERO_G, ZERO_G)


def _pair_table() -> Dict[Tuple[int, int], Tuple[int, int]]:
    table: Dict[Tuple[int, int], Tuple[int, int]] = {}
    for a, b, c in FANO_CYCLES:
        table[(a, b)] = (1, c)
        table[(b, c)] = (1, a)
        table[(c, a)] = (1, b)
        table[(b, a)] = (-1, c)
        table[(c, b)] = (-1, a)
        table[(a, c)] = (-1, b)
    return table


PAIR_TABLE = _pair_table()


def basis_mul(i: int, j: int) -> Tuple[int, int]:
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


@dataclass(frozen=True)
class EvalPlan:
    round_order: List[str]
    parent_order: Dict[str, List[str]]
    projection_policy: str = "fold_and_update"


@dataclass
class World:
    node_ids: List[str]
    parents: Dict[str, List[str]]
    states: Dict[str, CxO]
    eval_plan: EvalPlan
    tick: int = 0


def _should_project_after_fold(policy: str) -> bool:
    return policy in {"fold_and_update", "fold_only"}


def _should_project_after_update(policy: str) -> bool:
    return policy in {"fold_and_update", "update_only"}


def interaction_fold(messages: List[CxO], projection_policy: str) -> CxO:
    acc = cxo_one()
    for msg in messages:
        acc = cxo_mul(acc, msg)
        if _should_project_after_fold(projection_policy):
            acc = project_cxo_to_unity(acc)
    return acc


def update_rule(current: CxO, parent_messages: List[CxO], projection_policy: str) -> CxO:
    payload = interaction_fold(parent_messages, projection_policy=projection_policy)
    out = cxo_mul(payload, current)
    if _should_project_after_update(projection_policy):
        out = project_cxo_to_unity(out)
    return out


def _validate_eval_plan(node_ids: List[str], parents: Dict[str, List[str]], plan: EvalPlan) -> None:
    if plan.projection_policy not in PROJECTION_POLICIES:
        raise ValueError(
            f"Invalid eval_plan.projection_policy={plan.projection_policy!r}. "
            f"Allowed: {sorted(PROJECTION_POLICIES)}"
        )

    node_set = set(node_ids)
    round_set = set(plan.round_order)
    if round_set != node_set or len(plan.round_order) != len(node_ids):
        raise ValueError("eval_plan.round_order must be a permutation of node_ids.")
    if len(set(plan.round_order)) != len(plan.round_order):
        raise ValueError("eval_plan.round_order contains duplicate node ids.")

    if set(plan.parent_order.keys()) != node_set:
        raise ValueError("eval_plan.parent_order keys must exactly match node_ids.")

    for nid in node_ids:
        declared = plan.parent_order[nid]
        if len(declared) != len(set(declared)):
            raise ValueError(f"eval_plan.parent_order[{nid!r}] contains duplicates.")
        declared_set = set(declared)
        actual_set = set(parents.get(nid, []))
        if declared_set != actual_set:
            raise ValueError(
                f"eval_plan.parent_order[{nid!r}] must match parents[{nid!r}] as a set; "
                f"declared={sorted(declared_set)}, parents={sorted(actual_set)}"
            )


def step(world: World) -> World:
    old_states = world.states
    new_states: Dict[str, CxO] = {}
    for nid in world.eval_plan.round_order:
        pids = world.eval_plan.parent_order[nid]
        msgs = [old_states[pid] for pid in pids]
        new_states[nid] = update_rule(
            old_states[nid],
            msgs,
            projection_policy=world.eval_plan.projection_policy,
        )
    return World(
        node_ids=world.node_ids,
        parents=world.parents,
        states=new_states,
        eval_plan=world.eval_plan,
        tick=world.tick + 1,
    )


def run(world: World, steps: int) -> World:
    cur = world
    for _ in range(steps):
        cur = step(cur)
    return cur


def _parse_int_coeff(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer literal (no decimal point), got {value!r}.")
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


def load_world(path: str) -> World:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    node_ids = [str(x) for x in raw["node_ids"]]
    parents = {str(k): [str(x) for x in v] for k, v in raw["parents"].items()}
    init_state = {str(k): project_cxo_to_unity(_parse_cxo(v)) for k, v in raw["init_state"].items()}

    missing = [nid for nid in node_ids if nid not in init_state]
    if missing:
        raise ValueError(f"Missing init_state entries for node_ids: {missing}")

    if "eval_plan" not in raw:
        raise ValueError("Missing required field: eval_plan")
    eval_plan_raw = raw["eval_plan"]
    round_order = [str(x) for x in eval_plan_raw["round_order"]]
    parent_order = {
        str(k): [str(x) for x in v]
        for k, v in eval_plan_raw["parent_order"].items()
    }
    projection_policy = str(eval_plan_raw.get("projection_policy", "fold_and_update"))
    plan = EvalPlan(
        round_order=round_order,
        parent_order=parent_order,
        projection_policy=projection_policy,
    )
    _validate_eval_plan(node_ids=node_ids, parents=parents, plan=plan)

    return World(
        node_ids=node_ids,
        parents=parents,
        states=init_state,
        eval_plan=plan,
        tick=0,
    )


def save_world(path: str, world: World) -> None:
    out = {
        "tick": world.tick,
        "node_ids": world.node_ids,
        "parents": world.parents,
        "eval_plan": {
            "round_order": world.eval_plan.round_order,
            "parent_order": world.eval_plan.parent_order,
            "projection_policy": world.eval_plan.projection_policy,
        },
        "state": {nid: _serialize_cxo(world.states[nid]) for nid in world.node_ids},
        "kernel_profile": "preregistered_unity",
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Preregistered-order unity-projection CxO kernel runner.")
    parser.add_argument("--input", required=True, help="Path to initial lightcone JSON.")
    parser.add_argument("--steps", required=True, type=int, help="Number of deterministic ticks to run.")
    parser.add_argument("--output", required=True, help="Path to output JSON.")
    args = parser.parse_args()

    if args.steps < 0:
        raise ValueError("--steps must be >= 0")

    world0 = load_world(args.input)
    worldN = run(world0, args.steps)
    save_world(args.output, worldN)


if __name__ == "__main__":
    main()

