"""
Tests for calc/xor_two_body_kinematics.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from calc.xor_furey_ideals import furey_dual_electron_doubled, furey_electron_doubled
from calc.xor_two_body_kinematics import (
    POLICY_LOCK,
    initial_two_body_state,
    run_builtin_two_body_cases,
    run_two_body_trajectory,
    step_two_body,
    write_two_body_kinematics_artifacts,
)


def test_policy_lock_values():
    assert POLICY_LOCK.distance_semantics == "edge_separation_count"
    assert POLICY_LOCK.propagation_rule == "one_hop_per_tick"
    assert POLICY_LOCK.impulse_source_rule == "charge_sign_relation_at_message_arrival"
    assert POLICY_LOCK.topology_update_cadence == "every_tick"
    assert POLICY_LOCK.boundary_condition == "superdeterministic"
    assert POLICY_LOCK.observable_definition == "distance_delta = future_edge_distance - past_edge_distance"


def test_first_arrival_impulse_sign_same_vs_opposite():
    same = initial_two_body_state(furey_electron_doubled(), furey_electron_doubled(), edge_distance=1)
    opp = initial_two_body_state(furey_electron_doubled(), furey_dual_electron_doubled(), edge_distance=1)

    same1 = step_two_body(same)
    opp1 = step_two_body(opp)

    assert same1.last_pair_kind_on_arrival == "repulsive"
    assert same1.last_impulse_event == 1
    assert opp1.last_pair_kind_on_arrival == "attractive"
    assert opp1.last_impulse_event == -1


def test_distance_delta_matches_future_minus_past():
    st = initial_two_body_state(furey_electron_doubled(), furey_electron_doubled(), edge_distance=1)
    for _ in range(8):
        st = step_two_body(st)
        assert st.last_distance_delta == (st.edge_distance_future - st.edge_distance_past)


def test_propagation_is_one_hop_per_tick_on_nonarrival_ticks():
    st = initial_two_body_state(furey_electron_doubled(), furey_electron_doubled(), edge_distance=3)
    st1 = step_two_body(st)
    assert st1.ticks_until_next_interaction == 2
    assert st1.last_pair_kind_on_arrival is None
    st2 = step_two_body(st1)
    assert st2.ticks_until_next_interaction == 1
    assert st2.last_pair_kind_on_arrival is None


def test_builtin_dataset_shape():
    data = run_builtin_two_body_cases(steps=10, edge_distance=1)
    assert data["schema_version"] == "xor_two_body_kinematics_v1"
    assert set(data["cases"].keys()) == {
        "electron_electron_same_sign",
        "electron_positron_opposite_sign",
    }
    assert len(data["csv_rows"]) == 2 * (10 + 1)


def test_write_artifacts(tmp_path: Path):
    data = run_builtin_two_body_cases(steps=6, edge_distance=1)
    json_path = tmp_path / "two_body.json"
    csv_path = tmp_path / "two_body.csv"
    write_two_body_kinematics_artifacts(data, json_paths=[json_path], csv_paths=[csv_path])

    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "xor_two_body_kinematics_v1"

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == len(data["csv_rows"])
    assert "distance_delta" in rows[0]

