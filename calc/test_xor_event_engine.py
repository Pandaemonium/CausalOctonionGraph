"""
Tests for calc/xor_event_engine.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from calc.xor_event_engine import (
    build_event_engine_dataset,
    builtin_scenarios,
    run_event_steps,
    run_scenario,
    scenario_single_motif_vacuum_drive,
    step_event,
    write_event_engine_artifacts,
)


def test_builtin_scenario_ids_present():
    scenarios = builtin_scenarios()
    assert set(scenarios.keys()) == {
        "single_motif_vacuum_drive",
        "two_node_opposite_sign_pair",
        "two_node_same_sign_pair",
    }


def test_step_event_deterministic():
    s0 = scenario_single_motif_vacuum_drive()
    a = step_event(s0)
    b = step_event(s0)
    assert a == b
    assert a.step_index == 1
    assert len(a.nodes) == 1


def test_single_motif_period4_under_vacuum_drive():
    s0 = scenario_single_motif_vacuum_drive()
    trace = run_event_steps(s0, steps=8)
    # Node 0 returns to initial by step 4 under repeated e7 temporal commit.
    assert trace[4].nodes[0].state == trace[0].nodes[0].state


def test_two_node_pair_kinds_match_sign_expectation():
    opp = run_scenario("two_node_opposite_sign_pair", steps=0)
    same = run_scenario("two_node_same_sign_pair", steps=0)
    assert opp["final_step"]["pair_interaction_kind"] == "attractive"
    assert same["final_step"]["pair_interaction_kind"] == "repulsive"


def test_event_dataset_shape():
    data = build_event_engine_dataset(steps=6)
    assert data["schema_version"] == "xor_event_engine_scenarios_v1"
    assert data["scenario_count"] == 3
    assert len(data["scenarios"]) == 3
    assert len(data["csv_rows"]) == 3 * (6 + 1)
    sample_trace = data["scenarios"][0]["trace"][0]
    assert "node_state_exact_base8" in sample_trace
    assert "charges_base8" in sample_trace
    # base-8 encoding sanity
    for v in sample_trace["charges_base8"].values():
        assert isinstance(v, str)


def test_write_event_engine_artifacts(tmp_path: Path):
    data = build_event_engine_dataset(steps=4)
    json_path = tmp_path / "xor_event_engine_scenarios.json"
    csv_path = tmp_path / "xor_event_engine_scenarios.csv"
    write_event_engine_artifacts(data, json_paths=[json_path], csv_paths=[csv_path])

    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "xor_event_engine_scenarios_v1"

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == len(data["csv_rows"])
    assert "scenario_id" in rows[0]
    assert "step_index" in rows[0]
    assert "pair_interaction_kind" in rows[0]
    assert "charges_base8" in rows[0]
