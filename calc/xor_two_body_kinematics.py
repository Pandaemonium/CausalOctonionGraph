"""
calc/xor_two_body_kinematics.py

Deterministic two-body kinematics layer for XOR simulations.

Policy lock implemented from user decisions:
1) Distance = edge separation count.
2) Propagation = one hop per tick.
3) Impulse source = charge-sign relation at message arrival.
4) Topology update cadence = every tick.
5) Boundary condition = superdeterministic (no RNG / no stochastic boundary terms).
6) Observable = distance_delta = future_edge_distance - past_edge_distance.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from calc.xor_charge_sign_interaction_matrix import (
    interaction_kind_xor,
    temporal_commit,
    u1_charge,
)
from calc.xor_furey_ideals import StateGI, furey_dual_electron_doubled, furey_electron_doubled


def _require_int(name: str, value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer")
    return int(value)


def _to_base8(n: int) -> str:
    sign = "-" if n < 0 else ""
    return sign + format(abs(n), "o")


@dataclass(frozen=True)
class DistancePolicyLock:
    distance_semantics: str = "edge_separation_count"
    distance_past_definition: str = "past_edge_count_between_same_two_states"
    distance_future_definition: str = "future_edge_count_before_next_interaction"
    propagation_rule: str = "one_hop_per_tick"
    impulse_source_rule: str = "charge_sign_relation_at_message_arrival"
    topology_update_cadence: str = "every_tick"
    boundary_condition: str = "superdeterministic"
    observable_definition: str = "distance_delta = future_edge_distance - past_edge_distance"


POLICY_LOCK = DistancePolicyLock()


@dataclass(frozen=True)
class TwoBodyKinematicsState:
    left_state: StateGI
    right_state: StateGI
    tick: int
    edge_distance_past: int
    edge_distance_future: int
    ticks_until_next_interaction: int
    accumulated_impulse: int
    last_pair_kind_on_arrival: Optional[str]
    last_impulse_event: int
    last_distance_delta: int


def initial_two_body_state(
    left_state: StateGI,
    right_state: StateGI,
    edge_distance: int,
) -> TwoBodyKinematicsState:
    edge_distance = _require_int("edge_distance", edge_distance)
    if edge_distance < 1:
        raise ValueError("edge_distance must be >= 1")
    return TwoBodyKinematicsState(
        left_state=left_state,
        right_state=right_state,
        tick=0,
        edge_distance_past=edge_distance,
        edge_distance_future=edge_distance,
        ticks_until_next_interaction=edge_distance,
        accumulated_impulse=0,
        last_pair_kind_on_arrival=None,
        last_impulse_event=0,
        last_distance_delta=0,
    )


def _impulse_from_pair_kind(kind: Optional[str]) -> int:
    if kind == "repulsive":
        return 1
    if kind == "attractive":
        return -1
    return 0


def step_two_body(state: TwoBodyKinematicsState) -> TwoBodyKinematicsState:
    """
    One deterministic tick.

    Order:
    1) advance in-flight propagation by one hop,
    2) if arrival happens, sample pair-kind and update impulse accumulator,
    3) temporal commit both states,
    4) update future distance every tick from accumulated impulse,
    5) if arrival, start new interaction horizon with current future distance.
    """
    # 1) one-hop propagation
    countdown = max(0, state.ticks_until_next_interaction - 1)
    arrival = countdown == 0

    # 2) arrival-triggered impulse event
    pair_kind = None
    impulse_event = 0
    accumulated = state.accumulated_impulse
    if arrival:
        pair_kind = interaction_kind_xor(state.left_state, state.right_state)
        impulse_event = _impulse_from_pair_kind(pair_kind)
        accumulated += impulse_event

    # 3) deterministic local state update
    left_next = temporal_commit(state.left_state)
    right_next = temporal_commit(state.right_state)

    # 4) topology/distance update (every tick)
    d_past = state.edge_distance_future
    d_future = max(1, d_past + accumulated)
    d_delta = d_future - d_past

    # 5) next horizon rule
    if arrival:
        next_countdown = d_future
    else:
        next_countdown = countdown

    return TwoBodyKinematicsState(
        left_state=left_next,
        right_state=right_next,
        tick=state.tick + 1,
        edge_distance_past=d_past,
        edge_distance_future=d_future,
        ticks_until_next_interaction=next_countdown,
        accumulated_impulse=accumulated,
        last_pair_kind_on_arrival=pair_kind,
        last_impulse_event=impulse_event,
        last_distance_delta=d_delta,
    )


def run_two_body_trajectory(initial: TwoBodyKinematicsState, steps: int) -> List[TwoBodyKinematicsState]:
    steps = _require_int("steps", steps)
    if steps < 0:
        raise ValueError("steps must be >= 0")
    out = [initial]
    cur = initial
    for _ in range(steps):
        cur = step_two_body(cur)
        out.append(cur)
    return out


def _snapshot_row(st: TwoBodyKinematicsState) -> Dict[str, Any]:
    return {
        "tick": st.tick,
        "distance_past": st.edge_distance_past,
        "distance_future": st.edge_distance_future,
        "distance_delta": st.last_distance_delta,
        "ticks_until_next_interaction": st.ticks_until_next_interaction,
        "pair_kind_on_arrival": st.last_pair_kind_on_arrival,
        "impulse_event": st.last_impulse_event,
        "accumulated_impulse": st.accumulated_impulse,
        "left_u1_charge_base8": _to_base8(u1_charge(st.left_state)),
        "right_u1_charge_base8": _to_base8(u1_charge(st.right_state)),
    }


def run_builtin_two_body_cases(steps: int = 24, edge_distance: int = 1) -> Dict[str, Any]:
    steps = _require_int("steps", steps)
    edge_distance = _require_int("edge_distance", edge_distance)
    same = initial_two_body_state(
        left_state=furey_electron_doubled(),
        right_state=furey_electron_doubled(),
        edge_distance=edge_distance,
    )
    opp = initial_two_body_state(
        left_state=furey_electron_doubled(),
        right_state=furey_dual_electron_doubled(),
        edge_distance=edge_distance,
    )

    cases = {
        "electron_electron_same_sign": run_two_body_trajectory(same, steps=steps),
        "electron_positron_opposite_sign": run_two_body_trajectory(opp, steps=steps),
    }

    payload: Dict[str, Any] = {}
    csv_rows: List[Dict[str, Any]] = []
    for case_id, trace in cases.items():
        snaps = [_snapshot_row(s) for s in trace]
        payload[case_id] = {
            "steps": steps,
            "trace": snaps,
            "initial_pair_kind": snaps[1]["pair_kind_on_arrival"] if len(snaps) > 1 else None,
            "final_distance_future": snaps[-1]["distance_future"],
            "distance_delta_sum": sum(int(r["distance_delta"]) for r in snaps),
        }
        for row in snaps:
            csv_rows.append({"case_id": case_id, **row})

    return {
        "schema_version": "xor_two_body_kinematics_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "policy_lock": POLICY_LOCK.__dict__,
        "steps": steps,
        "edge_distance_initial": edge_distance,
        "cases": payload,
        "csv_rows": csv_rows,
    }


def write_two_body_kinematics_artifacts(
    dataset: Dict[str, Any],
    json_paths: Optional[List[Path]] = None,
    csv_paths: Optional[List[Path]] = None,
) -> None:
    if json_paths is None:
        json_paths = [Path("calc/xor_two_body_kinematics.json")]
    if csv_paths is None:
        csv_paths = [Path("calc/xor_two_body_kinematics.csv")]

    for path in json_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(dataset, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "case_id",
        "tick",
        "distance_past",
        "distance_future",
        "distance_delta",
        "ticks_until_next_interaction",
        "pair_kind_on_arrival",
        "impulse_event",
        "accumulated_impulse",
        "left_u1_charge_base8",
        "right_u1_charge_base8",
    ]
    for path in csv_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in dataset["csv_rows"]:
                writer.writerow(row)


def main() -> int:
    dataset = run_builtin_two_body_cases(steps=24, edge_distance=1)
    write_two_body_kinematics_artifacts(
        dataset,
        json_paths=[
            Path("calc/xor_two_body_kinematics.json"),
            Path("website/data/xor_two_body_kinematics.json"),
        ],
        csv_paths=[
            Path("calc/xor_two_body_kinematics.csv"),
            Path("website/data/xor_two_body_kinematics.csv"),
        ],
    )
    print("Wrote calc/xor_two_body_kinematics.json")
    print("Wrote calc/xor_two_body_kinematics.csv")
    print("Wrote website/data/xor_two_body_kinematics.json")
    print("Wrote website/data/xor_two_body_kinematics.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
