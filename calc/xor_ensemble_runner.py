"""
calc/xor_ensemble_runner.py

Batch ensemble runner for XOR scenario specifications.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from calc.xor_charge_sign_interaction_matrix import interaction_kind_xor, u1_charge
from calc.xor_furey_ideals import StateGI, nonzero_support
from calc.xor_observables import aggregate_ensemble_observables, scenario_observables
from calc.xor_scenario_loader import ScenarioSpec, load_scenario_specs, run_loaded_scenario


def _to_base8(n: int) -> str:
    sign = "-" if n < 0 else ""
    return sign + format(abs(n), "o")


def _detect_period(states: Sequence[StateGI]) -> int | None:
    if not states:
        return None
    initial = states[0]
    for i in range(1, len(states)):
        if states[i] == initial:
            return i
    return None


def _snapshot_row(event_state) -> Dict[str, Any]:
    node_ids = sorted(event_state.nodes.keys())
    charges_base8 = {str(i): _to_base8(u1_charge(event_state.nodes[i].state)) for i in node_ids}
    charge_signs = {
        str(i): (
            1
            if u1_charge(event_state.nodes[i].state) > 0
            else (-1 if u1_charge(event_state.nodes[i].state) < 0 else 0)
        )
        for i in node_ids
    }
    supports = {str(i): nonzero_support(event_state.nodes[i].state) for i in node_ids}
    exact = {
        str(i): [[_to_base8(re), _to_base8(im)] for (re, im) in event_state.nodes[i].state]
        for i in node_ids
    }
    ticks = {str(i): event_state.nodes[i].tick_count for i in node_ids}

    pair_kind = None
    if len(node_ids) == 2:
        a, b = node_ids
        pair_kind = interaction_kind_xor(event_state.nodes[a].state, event_state.nodes[b].state)

    return {
        "step_index": event_state.step_index,
        "charges_base8": charges_base8,
        "charge_signs": charge_signs,
        "supports": supports,
        "ticks": ticks,
        "node_state_exact_base8": exact,
        "pair_interaction_kind": pair_kind,
    }


def run_spec_to_result(spec: ScenarioSpec) -> Dict[str, Any]:
    trace_states = run_loaded_scenario(spec)
    snapshots = [_snapshot_row(s) for s in trace_states]

    node_ids = sorted(trace_states[0].nodes.keys())
    periods: Dict[str, int | None] = {}
    for node_id in node_ids:
        seq = [st.nodes[node_id].state for st in trace_states]
        periods[str(node_id)] = _detect_period(seq)

    pair_kind_counts: Dict[str, int] = {}
    for row in snapshots:
        key = row["pair_interaction_kind"] if row["pair_interaction_kind"] is not None else "none"
        pair_kind_counts[key] = pair_kind_counts.get(key, 0) + 1

    out = {
        "scenario_id": spec.scenario_id,
        "title": spec.title,
        "description": spec.description,
        "steps": spec.steps,
        "node_count": len(trace_states[0].nodes),
        "edge_count": len(trace_states[0].edges),
        "periods": periods,
        "initial_pair_kind": snapshots[0]["pair_interaction_kind"],
        "pair_kind_counts": pair_kind_counts,
        "trace": snapshots,
        "final_step": snapshots[-1],
    }
    out["observables"] = scenario_observables(out)
    return out


def run_ensemble_specs(specs: Sequence[ScenarioSpec]) -> Dict[str, Any]:
    runs = [run_spec_to_result(spec) for spec in specs]
    aggregate = aggregate_ensemble_observables([r["observables"] for r in runs])

    csv_rows: List[Dict[str, Any]] = []
    for row in runs:
        obs = row["observables"]
        csv_rows.append(
            {
                "scenario_id": row["scenario_id"],
                "steps": row["steps"],
                "initial_pair_kind": obs["initial_pair_kind"],
                "final_pair_kind": obs["final_pair_kind"],
                "pair_kind_entropy_bits": obs["pair_kind_entropy_bits"],
                "pair_kind_transition_count": obs["pair_kind_transition_count"],
            }
        )

    return {
        "schema_version": "xor_ensemble_runner_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "run_count": len(runs),
        "runs": runs,
        "aggregate_observables": aggregate,
        "csv_rows": csv_rows,
    }


def run_ensemble_from_yaml(path: str | Path) -> Dict[str, Any]:
    specs = load_scenario_specs(path)
    return run_ensemble_specs(specs)


def write_xor_ensemble_artifacts(
    dataset: Dict[str, Any],
    json_paths: Optional[List[Path]] = None,
    csv_paths: Optional[List[Path]] = None,
) -> None:
    if json_paths is None:
        json_paths = [Path("calc/xor_ensemble_results.json")]
    if csv_paths is None:
        csv_paths = [Path("calc/xor_ensemble_results.csv")]

    for path in json_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(dataset, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "scenario_id",
        "steps",
        "initial_pair_kind",
        "final_pair_kind",
        "pair_kind_entropy_bits",
        "pair_kind_transition_count",
    ]
    for path in csv_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in dataset["csv_rows"]:
                writer.writerow(row)

