"""
calc/xor_furey_lightcone_monitor.py

Deterministic Furey-motif evolution on a predetermined lightcone.

Intent:
1) Seed two tracked Furey motifs on a precomputed cone envelope.
2) Advance depth deterministically (no spawn / no RNG).
3) Monitor interaction events and edge-separation distance changes over depth.

This module reuses the locked two-body kinematics semantics in
calc/xor_two_body_kinematics.py and wraps them in an explicit predetermined
lightcone scaffold for per-depth observability.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from calc.xor_charge_sign_interaction_matrix import u1_charge
from calc.xor_furey_ideals import StateGI, furey_dual_electron_doubled, furey_electron_doubled
from calc.xor_two_body_kinematics import (
    TwoBodyKinematicsState,
    initial_two_body_state,
    step_two_body,
)


def _require_int(name: str, value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer")
    return int(value)


def _to_base8(n: int) -> str:
    sign = "-" if n < 0 else ""
    return sign + format(abs(n), "o")


@dataclass(frozen=True)
class PredeterminedLightconeSpec:
    depth_horizon: int
    initial_edge_distance: int
    min_position_depth0: int
    max_position_depth0: int
    description: str = "full_cone_preconditioned_no_spawn"


def build_predetermined_lightcone(spec: PredeterminedLightconeSpec) -> Dict[str, Any]:
    """
    Build a deterministic 1+1D cone envelope from depth 0..depth_horizon.

    Nodes at depth d are integer positions in:
      [min_position_depth0 - d, max_position_depth0 + d]
    which is the future cone of the initial interval.
    """
    depth_horizon = _require_int("depth_horizon", spec.depth_horizon)
    initial_edge_distance = _require_int("initial_edge_distance", spec.initial_edge_distance)
    min_position_depth0 = _require_int("min_position_depth0", spec.min_position_depth0)
    max_position_depth0 = _require_int("max_position_depth0", spec.max_position_depth0)

    if depth_horizon < 0:
        raise ValueError("depth_horizon must be >= 0")
    if initial_edge_distance < 1:
        raise ValueError("initial_edge_distance must be >= 1")
    if min_position_depth0 > max_position_depth0:
        raise ValueError("min_position_depth0 must be <= max_position_depth0")

    depths: List[Dict[str, int]] = []
    total_nodes = 0
    total_edges = 0

    for depth in range(depth_horizon + 1):
        min_pos = min_position_depth0 - depth
        max_pos = max_position_depth0 + depth
        node_count = max_pos - min_pos + 1
        # Two outgoing causal edges per node except at final depth.
        edge_count = 0 if depth == depth_horizon else 2 * node_count
        total_nodes += node_count
        total_edges += edge_count
        depths.append(
            {
                "depth": depth,
                "min_pos": min_pos,
                "max_pos": max_pos,
                "node_count": node_count,
                "edge_count_to_next_depth": edge_count,
            }
        )

    return {
        "schema_version": "predetermined_lightcone_v1",
        "description": spec.description,
        "depth_horizon": depth_horizon,
        "initial_edge_distance": initial_edge_distance,
        "min_position_depth0": min_position_depth0,
        "max_position_depth0": max_position_depth0,
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "depths": depths,
    }


def _snapshot_row(
    depth: int,
    st: TwoBodyKinematicsState,
    last_interaction_depth: Optional[int],
    interaction_count: int,
) -> Dict[str, Any]:
    has_interaction = st.last_pair_kind_on_arrival is not None

    if has_interaction:
        edge_since_last = depth if last_interaction_depth is None else (depth - last_interaction_depth)
        next_last_interaction_depth = depth
        next_interaction_count = interaction_count + 1
    else:
        edge_since_last = None if last_interaction_depth is None else (depth - last_interaction_depth)
        next_last_interaction_depth = last_interaction_depth
        next_interaction_count = interaction_count

    row = {
        "depth": depth,
        "distance_past": st.edge_distance_past,
        "distance_future": st.edge_distance_future,
        "distance_delta": st.last_distance_delta,
        "distance_changed": st.last_distance_delta != 0,
        "ticks_until_next_interaction": st.ticks_until_next_interaction,
        "interaction_occurred": has_interaction,
        "interaction_kind": st.last_pair_kind_on_arrival,
        "edge_depth_since_last_interaction": edge_since_last,
        "edge_depth_until_next_interaction": st.ticks_until_next_interaction,
        "interaction_count": next_interaction_count,
        "left_u1_charge_base8": _to_base8(u1_charge(st.left_state)),
        "right_u1_charge_base8": _to_base8(u1_charge(st.right_state)),
    }
    return row, next_last_interaction_depth, next_interaction_count


def run_pair_on_predetermined_lightcone(
    left_state: StateGI,
    right_state: StateGI,
    depth_horizon: int,
    initial_edge_distance: int,
) -> Dict[str, Any]:
    depth_horizon = _require_int("depth_horizon", depth_horizon)
    initial_edge_distance = _require_int("initial_edge_distance", initial_edge_distance)
    if depth_horizon < 0:
        raise ValueError("depth_horizon must be >= 0")
    if initial_edge_distance < 1:
        raise ValueError("initial_edge_distance must be >= 1")

    spec = PredeterminedLightconeSpec(
        depth_horizon=depth_horizon,
        initial_edge_distance=initial_edge_distance,
        min_position_depth0=0,
        max_position_depth0=initial_edge_distance,
    )
    cone = build_predetermined_lightcone(spec)

    st = initial_two_body_state(
        left_state=left_state,
        right_state=right_state,
        edge_distance=initial_edge_distance,
    )

    trace: List[Dict[str, Any]] = []
    interaction_events: List[Dict[str, Any]] = []
    last_interaction_depth: Optional[int] = None
    interaction_count = 0

    for depth in range(depth_horizon + 1):
        row, last_interaction_depth, interaction_count = _snapshot_row(
            depth=depth,
            st=st,
            last_interaction_depth=last_interaction_depth,
            interaction_count=interaction_count,
        )
        trace.append(row)
        if row["interaction_occurred"]:
            interaction_events.append(
                {
                    "depth": depth,
                    "kind": row["interaction_kind"],
                    "edge_depth_since_last_interaction": row["edge_depth_since_last_interaction"],
                    "distance_before": row["distance_past"],
                    "distance_after": row["distance_future"],
                    "distance_delta": row["distance_delta"],
                }
            )

        if depth < depth_horizon:
            st = step_two_body(st)

    return {
        "schema_version": "xor_furey_lightcone_monitor_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "lightcone": cone,
        "trace": trace,
        "interaction_events": interaction_events,
        "summary": {
            "depth_horizon": depth_horizon,
            "initial_edge_distance": initial_edge_distance,
            "interaction_event_count": len(interaction_events),
            "final_distance_future": trace[-1]["distance_future"],
            "distance_delta_total": sum(int(r["distance_delta"]) for r in trace),
            "distance_change_depths": [int(r["depth"]) for r in trace if bool(r["distance_changed"])],
        },
    }


def run_builtin_furey_lightcone_cases(depth_horizon: int = 40, initial_edge_distance: int = 5) -> Dict[str, Any]:
    depth_horizon = _require_int("depth_horizon", depth_horizon)
    initial_edge_distance = _require_int("initial_edge_distance", initial_edge_distance)
    same = run_pair_on_predetermined_lightcone(
        left_state=furey_electron_doubled(),
        right_state=furey_electron_doubled(),
        depth_horizon=depth_horizon,
        initial_edge_distance=initial_edge_distance,
    )
    opp = run_pair_on_predetermined_lightcone(
        left_state=furey_electron_doubled(),
        right_state=furey_dual_electron_doubled(),
        depth_horizon=depth_horizon,
        initial_edge_distance=initial_edge_distance,
    )
    return {
        "schema_version": "xor_furey_lightcone_cases_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "depth_horizon": depth_horizon,
        "initial_edge_distance": initial_edge_distance,
        "cases": {
            "electron_electron": same,
            "electron_positron": opp,
        },
    }


def write_furey_lightcone_artifacts(
    dataset: Dict[str, Any],
    json_paths: Optional[List[Path]] = None,
    csv_paths: Optional[List[Path]] = None,
) -> None:
    if json_paths is None:
        json_paths = [Path("calc/xor_furey_lightcone_monitor.json")]
    if csv_paths is None:
        csv_paths = [Path("calc/xor_furey_lightcone_monitor.csv")]

    for path in json_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(dataset, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "case_id",
        "depth",
        "distance_past",
        "distance_future",
        "distance_delta",
        "distance_changed",
        "ticks_until_next_interaction",
        "interaction_occurred",
        "interaction_kind",
        "edge_depth_since_last_interaction",
        "edge_depth_until_next_interaction",
        "interaction_count",
        "left_u1_charge_base8",
        "right_u1_charge_base8",
    ]
    rows: List[Dict[str, Any]] = []
    for case_id, payload in dataset["cases"].items():
        for row in payload["trace"]:
            rows.append({"case_id": case_id, **row})

    for path in csv_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)


def main() -> int:
    data = run_builtin_furey_lightcone_cases(depth_horizon=40, initial_edge_distance=5)
    write_furey_lightcone_artifacts(
        data,
        json_paths=[
            Path("calc/xor_furey_lightcone_monitor.json"),
            Path("website/data/xor_furey_lightcone_monitor.json"),
        ],
        csv_paths=[
            Path("calc/xor_furey_lightcone_monitor.csv"),
            Path("website/data/xor_furey_lightcone_monitor.csv"),
        ],
    )
    print("Wrote calc/xor_furey_lightcone_monitor.json")
    print("Wrote calc/xor_furey_lightcone_monitor.csv")
    print("Wrote website/data/xor_furey_lightcone_monitor.json")
    print("Wrote website/data/xor_furey_lightcone_monitor.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
