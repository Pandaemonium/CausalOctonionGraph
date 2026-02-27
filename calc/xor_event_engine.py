"""
calc/xor_event_engine.py

MVP event engine for XOR octonion simulations.

Implements:
1) typed event-state container (nodes, edges, pending messages, event log),
2) deterministic scheduler (canonical node/edge/message ordering),
3) explicit message/edge operator layer,
4) built-in simple scenarios for particle/event runs.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

from calc.xor_charge_sign_interaction_matrix import (
    interaction_kind_xor,
    temporal_commit,
    u1_charge,
)
from calc.xor_furey_ideals import (
    GI,
    StateGI,
    furey_dual_electron_doubled,
    furey_electron_doubled,
    nonzero_support,
    oct_mul_xor,
    state_basis,
)
from calc.xor_vector_spinor_phase_cycles import vector_motif_state


def _to_base8(n: int) -> str:
    sign = "-" if n < 0 else ""
    return sign + format(abs(n), "o")


@dataclass(frozen=True)
class XNodeState:
    node_id: int
    state: StateGI
    tick_count: int
    topo_depth: int


@dataclass(frozen=True)
class XEdgeOperator:
    edge_id: str
    src_node_id: int
    dst_node_id: int
    op_idx: int
    hand: str  # "left" | "right"
    payload_mode: str  # "src_state" | "identity"
    order: int


@dataclass(frozen=True)
class XMessage:
    message_id: str
    src_node_id: int
    dst_node_id: int
    op_idx: int
    hand: str  # "left" | "right"
    payload_state: StateGI
    edge_id: str
    order: int


@dataclass(frozen=True)
class XEventState:
    nodes: Dict[int, XNodeState]
    edges: Tuple[XEdgeOperator, ...]
    pending_messages: Tuple[XMessage, ...]
    step_index: int
    event_log: Tuple[Dict[str, Any], ...]


@dataclass(frozen=True)
class XScenarioSpec:
    scenario_id: str
    title: str
    description: str
    builder: Callable[[], XEventState]


def _identity_state() -> StateGI:
    return state_basis(0, (1, 0))


def _apply_basis_hit(state: StateGI, op_idx: int, hand: str) -> StateGI:
    if not (1 <= op_idx <= 7):
        raise ValueError(f"op_idx must be in [1,7], got {op_idx}")
    op = state_basis(op_idx, (1, 0))
    if hand == "left":
        return oct_mul_xor(op, state)
    if hand == "right":
        return oct_mul_xor(state, op)
    raise ValueError(f"hand must be 'left' or 'right', got {hand}")


def _validate_event_state(state: XEventState) -> None:
    node_ids = set(state.nodes.keys())
    for n in state.nodes.values():
        if n.node_id not in node_ids:
            raise ValueError(f"Node dict mismatch for node_id={n.node_id}")
    for e in state.edges:
        if e.src_node_id not in node_ids:
            raise ValueError(f"Edge src not found: {e.src_node_id}")
        if e.dst_node_id not in node_ids:
            raise ValueError(f"Edge dst not found: {e.dst_node_id}")
        if e.hand not in ("left", "right"):
            raise ValueError(f"Unsupported edge hand: {e.hand}")
        if e.payload_mode not in ("src_state", "identity"):
            raise ValueError(f"Unsupported payload_mode: {e.payload_mode}")


def canonical_node_ids(state: XEventState) -> List[int]:
    return sorted(state.nodes.keys())


def canonical_edge_order(edges: Sequence[XEdgeOperator]) -> List[XEdgeOperator]:
    return sorted(
        edges,
        key=lambda e: (e.order, e.dst_node_id, e.src_node_id, e.op_idx, e.hand, e.edge_id),
    )


def build_pending_messages(state: XEventState) -> Tuple[XMessage, ...]:
    _validate_event_state(state)
    out: List[XMessage] = []
    for edge in canonical_edge_order(state.edges):
        src_state = state.nodes[edge.src_node_id].state
        payload = src_state if edge.payload_mode == "src_state" else _identity_state()
        out.append(
            XMessage(
                message_id=f"s{state.step_index}_e{edge.edge_id}",
                src_node_id=edge.src_node_id,
                dst_node_id=edge.dst_node_id,
                op_idx=edge.op_idx,
                hand=edge.hand,
                payload_state=payload,
                edge_id=edge.edge_id,
                order=edge.order,
            )
        )
    return tuple(out)


def _messages_for_dst(messages: Sequence[XMessage], dst_node_id: int) -> List[XMessage]:
    return sorted(
        [m for m in messages if m.dst_node_id == dst_node_id],
        key=lambda m: (m.order, m.src_node_id, m.op_idx, m.hand, m.message_id),
    )


def apply_message_fold(state: StateGI, messages: Sequence[XMessage]) -> StateGI:
    cur = state
    for msg in messages:
        cur = _apply_basis_hit(cur, msg.op_idx, msg.hand)
        cur = oct_mul_xor(cur, msg.payload_state)
    return cur


def step_event(state: XEventState) -> XEventState:
    _validate_event_state(state)
    messages = build_pending_messages(state)

    new_nodes: Dict[int, XNodeState] = {}
    node_updates: List[Dict[str, Any]] = []

    for node_id in canonical_node_ids(state):
        old = state.nodes[node_id]
        local_msgs = _messages_for_dst(messages, node_id)

        cur = temporal_commit(old.state)
        cur = apply_message_fold(cur, local_msgs)

        updated = XNodeState(
            node_id=node_id,
            state=cur,
            tick_count=old.tick_count + 1,
            topo_depth=old.topo_depth + 1,
        )
        new_nodes[node_id] = updated
        node_updates.append(
            {
                "node_id": node_id,
                "message_count": len(local_msgs),
                "u1_before": u1_charge(old.state),
                "u1_after": u1_charge(updated.state),
            }
        )

    step_log = {
        "step_index_before": state.step_index,
        "step_index_after": state.step_index + 1,
        "message_count": len(messages),
        "node_updates": node_updates,
    }
    return XEventState(
        nodes=new_nodes,
        edges=state.edges,
        pending_messages=messages,
        step_index=state.step_index + 1,
        event_log=state.event_log + (step_log,),
    )


def run_event_steps(initial: XEventState, steps: int) -> List[XEventState]:
    if steps < 0:
        raise ValueError("steps must be >= 0")
    out = [initial]
    cur = initial
    for _ in range(steps):
        cur = step_event(cur)
        out.append(cur)
    return out


def _detect_period_from_trace(states: Sequence[StateGI]) -> Optional[int]:
    if not states:
        return None
    initial = states[0]
    for i in range(1, len(states)):
        if states[i] == initial:
            return i
    return None


def _mk_node(node_id: int, state: StateGI) -> XNodeState:
    return XNodeState(node_id=node_id, state=state, tick_count=0, topo_depth=0)


def _mk_event_state(nodes: Sequence[XNodeState], edges: Sequence[XEdgeOperator]) -> XEventState:
    return XEventState(
        nodes={n.node_id: n for n in nodes},
        edges=tuple(edges),
        pending_messages=tuple(),
        step_index=0,
        event_log=tuple(),
    )


def scenario_single_motif_vacuum_drive() -> XEventState:
    nodes = [_mk_node(0, vector_motif_state((1, 2, 3), coeff=1))]
    edges: List[XEdgeOperator] = []
    return _mk_event_state(nodes, edges)


def scenario_two_node_opposite_sign() -> XEventState:
    nodes = [
        _mk_node(0, furey_electron_doubled()),
        _mk_node(1, furey_dual_electron_doubled()),
    ]
    edges = [
        XEdgeOperator(
            edge_id="0_to_1",
            src_node_id=0,
            dst_node_id=1,
            op_idx=7,
            hand="left",
            payload_mode="src_state",
            order=0,
        ),
        XEdgeOperator(
            edge_id="1_to_0",
            src_node_id=1,
            dst_node_id=0,
            op_idx=7,
            hand="left",
            payload_mode="src_state",
            order=1,
        ),
    ]
    return _mk_event_state(nodes, edges)


def scenario_two_node_same_sign() -> XEventState:
    nodes = [
        _mk_node(0, furey_electron_doubled()),
        _mk_node(1, furey_electron_doubled()),
    ]
    edges = [
        XEdgeOperator(
            edge_id="0_to_1",
            src_node_id=0,
            dst_node_id=1,
            op_idx=7,
            hand="left",
            payload_mode="src_state",
            order=0,
        ),
        XEdgeOperator(
            edge_id="1_to_0",
            src_node_id=1,
            dst_node_id=0,
            op_idx=7,
            hand="left",
            payload_mode="src_state",
            order=1,
        ),
    ]
    return _mk_event_state(nodes, edges)


def builtin_scenarios() -> Dict[str, XScenarioSpec]:
    return {
        "single_motif_vacuum_drive": XScenarioSpec(
            scenario_id="single_motif_vacuum_drive",
            title="Single Motif + Vacuum Drive",
            description="One vector motif with temporal vacuum commit and no cross-edge messages.",
            builder=scenario_single_motif_vacuum_drive,
        ),
        "two_node_opposite_sign_pair": XScenarioSpec(
            scenario_id="two_node_opposite_sign_pair",
            title="Two Node Opposite Sign Pair",
            description="Two-node exchange with opposite-sign spinor motifs.",
            builder=scenario_two_node_opposite_sign,
        ),
        "two_node_same_sign_pair": XScenarioSpec(
            scenario_id="two_node_same_sign_pair",
            title="Two Node Same Sign Pair",
            description="Two-node exchange with same-sign spinor motifs.",
            builder=scenario_two_node_same_sign,
        ),
    }


def _snapshot_row(state: XEventState) -> Dict[str, Any]:
    node_ids = canonical_node_ids(state)
    charges_base8 = {str(i): _to_base8(u1_charge(state.nodes[i].state)) for i in node_ids}
    charge_signs = {
        str(i): (
            1
            if u1_charge(state.nodes[i].state) > 0
            else (-1 if u1_charge(state.nodes[i].state) < 0 else 0)
        )
        for i in node_ids
    }
    ticks = {str(i): state.nodes[i].tick_count for i in node_ids}
    supports = {str(i): nonzero_support(state.nodes[i].state) for i in node_ids}
    exact_state_base8 = {
        str(i): [[_to_base8(re), _to_base8(im)] for (re, im) in state.nodes[i].state]
        for i in node_ids
    }

    pair_kind: Optional[str] = None
    if len(node_ids) == 2:
        a, b = node_ids
        pair_kind = interaction_kind_xor(state.nodes[a].state, state.nodes[b].state)

    return {
        "step_index": state.step_index,
        "charges_base8": charges_base8,
        "charge_signs": charge_signs,
        "ticks": ticks,
        "supports": supports,
        "node_state_exact_base8": exact_state_base8,
        "pair_interaction_kind": pair_kind,
    }


def run_scenario(scenario_id: str, steps: int = 12) -> Dict[str, Any]:
    scenarios = builtin_scenarios()
    if scenario_id not in scenarios:
        raise KeyError(f"Unknown scenario_id: {scenario_id}")
    spec = scenarios[scenario_id]
    initial = spec.builder()
    trace_states = run_event_steps(initial, steps=steps)
    snapshots = [_snapshot_row(s) for s in trace_states]

    node_ids = canonical_node_ids(trace_states[0])
    periods: Dict[str, Optional[int]] = {}
    for node_id in node_ids:
        seq = [s.nodes[node_id].state for s in trace_states]
        periods[str(node_id)] = _detect_period_from_trace(seq)

    pair_kind_counts: Dict[str, int] = {}
    for snap in snapshots:
        key = snap["pair_interaction_kind"] if snap["pair_interaction_kind"] is not None else "none"
        pair_kind_counts[key] = pair_kind_counts.get(key, 0) + 1

    return {
        "scenario_id": spec.scenario_id,
        "title": spec.title,
        "description": spec.description,
        "steps": steps,
        "node_count": len(trace_states[0].nodes),
        "edge_count": len(trace_states[0].edges),
        "periods": periods,
        "initial_pair_kind": snapshots[0]["pair_interaction_kind"],
        "pair_kind_counts": pair_kind_counts,
        "trace": snapshots,
        "final_step": snapshots[-1],
    }


def build_event_engine_dataset(steps: int = 12) -> Dict[str, Any]:
    scenarios = builtin_scenarios()
    scenario_payload: List[Dict[str, Any]] = []
    csv_rows: List[Dict[str, Any]] = []

    for scenario_id in sorted(scenarios.keys()):
        row = run_scenario(scenario_id, steps=steps)
        scenario_payload.append(row)
        for snap in row["trace"]:
            csv_rows.append(
                {
                    "scenario_id": scenario_id,
                    "step_index": snap["step_index"],
                    "pair_interaction_kind": snap["pair_interaction_kind"],
                    "charges_base8": json.dumps(snap["charges_base8"], sort_keys=True),
                    "ticks": json.dumps(snap["ticks"], sort_keys=True),
                }
            )

    return {
        "schema_version": "xor_event_engine_scenarios_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "steps_per_scenario": steps,
        "scenario_count": len(scenario_payload),
        "scenarios": scenario_payload,
        "csv_rows": csv_rows,
    }


def write_event_engine_artifacts(
    dataset: Dict[str, Any],
    json_paths: Optional[List[Path]] = None,
    csv_paths: Optional[List[Path]] = None,
) -> None:
    if json_paths is None:
        json_paths = [Path("calc/xor_event_engine_scenarios.json")]
    if csv_paths is None:
        csv_paths = [Path("calc/xor_event_engine_scenarios.csv")]

    for path in json_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(dataset, indent=2) + "\n", encoding="utf-8")

    fieldnames = ["scenario_id", "step_index", "pair_interaction_kind", "charges_base8", "ticks"]
    for path in csv_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in dataset["csv_rows"]:
                writer.writerow(row)


def main() -> int:
    dataset = build_event_engine_dataset(steps=12)
    write_event_engine_artifacts(
        dataset,
        json_paths=[
            Path("calc/xor_event_engine_scenarios.json"),
            Path("website/data/xor_event_engine_scenarios.json"),
        ],
        csv_paths=[
            Path("calc/xor_event_engine_scenarios.csv"),
            Path("website/data/xor_event_engine_scenarios.csv"),
        ],
    )
    print("Wrote calc/xor_event_engine_scenarios.json")
    print("Wrote calc/xor_event_engine_scenarios.csv")
    print("Wrote website/data/xor_event_engine_scenarios.json")
    print("Wrote website/data/xor_event_engine_scenarios.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
