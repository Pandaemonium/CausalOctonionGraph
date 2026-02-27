"""
calc/xor_scenario_loader.py

Scenario specification loader for XOR event-engine runs.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import yaml

from calc.xor_event_engine import (
    XEdgeOperator,
    XEventState,
    XNodeState,
    run_event_steps,
)
from calc.xor_furey_ideals import (
    StateGI,
    ideal_sd_basis_doubled,
    ideal_su_basis_doubled,
)
from calc.xor_observables import decode_base8_int
from calc.xor_vector_spinor_phase_cycles import vector_motif_state


@dataclass(frozen=True)
class ScenarioSpec:
    scenario_id: str
    title: str
    description: str
    steps: int
    nodes: Tuple[Dict[str, Any], ...]
    edges: Tuple[Dict[str, Any], ...]


def canonical_motif_state_map() -> Dict[str, StateGI]:
    out: Dict[str, StateGI] = {}

    vector_triads = [
        (1, 2, 3),
        (1, 4, 5),
        (1, 7, 6),
        (2, 4, 6),
        (2, 5, 7),
        (3, 4, 7),
        (3, 6, 5),
    ]
    for idx, triad in enumerate(vector_triads, start=1):
        out[f"vector_fano_line_l{idx}"] = vector_motif_state(triad, coeff=1)

    out["vector_electron_favored"] = vector_motif_state((1, 2, 3), coeff=1)
    out["vector_proton_proto_t124"] = vector_motif_state((1, 2, 4), coeff=1)

    su = ideal_su_basis_doubled()
    sd = ideal_sd_basis_doubled()
    out.update(su)
    out.update(sd)
    out["left_spinor_electron_ideal"] = su["su_triple_electron"]
    out["right_spinor_electron_ideal"] = sd["sd_triple_dual_electron"]
    return out


def _state_from_base8(spec: Sequence[Sequence[str]]) -> StateGI:
    if len(spec) != 8:
        raise ValueError("state_base8 must have length 8")
    out: List[tuple[int, int]] = []
    for pair in spec:
        if len(pair) != 2:
            raise ValueError("each state_base8 row must have [re, im]")
        out.append((decode_base8_int(pair[0]), decode_base8_int(pair[1])))
    return tuple(out)  # type: ignore[return-value]


def _parse_spec_dict(raw: Dict[str, Any]) -> ScenarioSpec:
    scenario_id = str(raw.get("scenario_id", "")).strip()
    if not scenario_id:
        raise ValueError("scenario_id is required")
    title = str(raw.get("title", scenario_id))
    description = str(raw.get("description", ""))
    steps = int(raw.get("steps", 12))
    nodes = tuple(raw.get("nodes", []))
    edges = tuple(raw.get("edges", []))
    if not nodes:
        raise ValueError("nodes list is required")
    return ScenarioSpec(
        scenario_id=scenario_id,
        title=title,
        description=description,
        steps=steps,
        nodes=nodes,
        edges=edges,
    )


def load_scenario_specs(path: str | Path) -> List[ScenarioSpec]:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if raw is None:
        raise ValueError("empty scenario spec file")
    if isinstance(raw, dict) and "scenarios" in raw:
        items = raw["scenarios"]
    elif isinstance(raw, list):
        items = raw
    elif isinstance(raw, dict):
        items = [raw]
    else:
        raise ValueError("unsupported scenario spec layout")
    return [_parse_spec_dict(dict(item)) for item in items]


def build_event_state_from_spec(spec: ScenarioSpec) -> XEventState:
    motif_map = canonical_motif_state_map()
    nodes: Dict[int, XNodeState] = {}

    for row in spec.nodes:
        node_id = int(row["node_id"])
        if node_id in nodes:
            raise ValueError(f"duplicate node_id: {node_id}")
        tick = int(row.get("tick_count", 0))
        depth = int(row.get("topo_depth", 0))

        if "motif_id" in row:
            motif_id = str(row["motif_id"])
            if motif_id not in motif_map:
                raise KeyError(f"unknown motif_id: {motif_id}")
            state = motif_map[motif_id]
        elif "state_base8" in row:
            state = _state_from_base8(row["state_base8"])
        else:
            raise ValueError(f"node {node_id} requires motif_id or state_base8")

        nodes[node_id] = XNodeState(
            node_id=node_id,
            state=state,
            tick_count=tick,
            topo_depth=depth,
        )

    edges: List[XEdgeOperator] = []
    for i, row in enumerate(spec.edges):
        src = int(row["src_node_id"])
        dst = int(row["dst_node_id"])
        if src not in nodes or dst not in nodes:
            raise ValueError(f"edge references missing node: {src}->{dst}")
        edges.append(
            XEdgeOperator(
                edge_id=str(row.get("edge_id", f"e{i}")),
                src_node_id=src,
                dst_node_id=dst,
                op_idx=int(row.get("op_idx", 7)),
                hand=str(row.get("hand", "left")),
                payload_mode=str(row.get("payload_mode", "src_state")),
                order=int(row.get("order", i)),
            )
        )

    return XEventState(
        nodes=nodes,
        edges=tuple(edges),
        pending_messages=tuple(),
        step_index=0,
        event_log=tuple(),
    )


def run_loaded_scenario(spec: ScenarioSpec) -> List[XEventState]:
    initial = build_event_state_from_spec(spec)
    return run_event_steps(initial, steps=spec.steps)

