"""
Tests for calc/xor_furey_lightcone_monitor.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from calc.xor_furey_lightcone_monitor import (
    PredeterminedLightconeSpec,
    build_predetermined_lightcone,
    run_builtin_furey_lightcone_cases,
    run_pair_on_predetermined_lightcone,
    write_furey_lightcone_artifacts,
)
from calc.xor_furey_ideals import furey_dual_electron_doubled, furey_electron_doubled


def test_build_predetermined_lightcone_depth_shape():
    spec = PredeterminedLightconeSpec(
        depth_horizon=12,
        initial_edge_distance=5,
        min_position_depth0=0,
        max_position_depth0=5,
    )
    cone = build_predetermined_lightcone(spec)
    assert cone["schema_version"] == "predetermined_lightcone_v1"
    assert len(cone["depths"]) == 13
    assert cone["depths"][0]["node_count"] == 6
    assert cone["depths"][1]["node_count"] == 8


def test_run_pair_trace_len_is_horizon_plus_one():
    data = run_pair_on_predetermined_lightcone(
        left_state=furey_electron_doubled(),
        right_state=furey_electron_doubled(),
        depth_horizon=20,
        initial_edge_distance=4,
    )
    assert len(data["trace"]) == 21
    assert data["summary"]["depth_horizon"] == 20


def test_interaction_events_have_edge_depth_since_last():
    data = run_pair_on_predetermined_lightcone(
        left_state=furey_electron_doubled(),
        right_state=furey_dual_electron_doubled(),
        depth_horizon=30,
        initial_edge_distance=3,
    )
    events = data["interaction_events"]
    assert len(events) >= 1
    for ev in events:
        assert ev["edge_depth_since_last_interaction"] is not None
        assert int(ev["edge_depth_since_last_interaction"]) >= 1


def test_builtin_cases_include_same_and_opposite_sign():
    data = run_builtin_furey_lightcone_cases(depth_horizon=24, initial_edge_distance=5)
    assert data["schema_version"] == "xor_furey_lightcone_cases_v1"
    assert set(data["cases"].keys()) == {"electron_electron", "electron_positron"}
    ee = data["cases"]["electron_electron"]["interaction_events"]
    ep = data["cases"]["electron_positron"]["interaction_events"]
    assert any(ev["kind"] == "repulsive" for ev in ee)
    assert any(ev["kind"] == "attractive" for ev in ep)


def test_distance_changes_are_detected_for_odd_initial_separation():
    data = run_builtin_furey_lightcone_cases(depth_horizon=24, initial_edge_distance=5)
    ee = data["cases"]["electron_electron"]["summary"]["distance_change_depths"]
    ep = data["cases"]["electron_positron"]["summary"]["distance_change_depths"]
    assert len(ee) > 0
    assert len(ep) > 0


def test_write_artifacts(tmp_path: Path):
    data = run_builtin_furey_lightcone_cases(depth_horizon=16, initial_edge_distance=4)
    json_path = tmp_path / "lightcone.json"
    csv_path = tmp_path / "lightcone.csv"
    write_furey_lightcone_artifacts(data, json_paths=[json_path], csv_paths=[csv_path])

    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "xor_furey_lightcone_cases_v1"

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) > 0
    assert "distance_future" in rows[0]
    assert "interaction_occurred" in rows[0]


def test_non_integer_initial_edge_distance_rejected() -> None:
    with pytest.raises(TypeError, match="initial_edge_distance must be an integer"):
        run_pair_on_predetermined_lightcone(
            left_state=furey_electron_doubled(),
            right_state=furey_electron_doubled(),
            depth_horizon=8,
            initial_edge_distance=3.25,  # type: ignore[arg-type]
        )
