"""Protocol tests for ALPHA deterministic lightcone simulation/extraction pack."""

from __future__ import annotations

from calc.extract_alpha_lightcone import extract_alpha_from_dataset
from calc.simulate_alpha_lightcone import (
    DEFAULT_CONDITIONS,
    load_conditions,
    run_simulation_dataset,
    validate_conditions,
)


def test_conditions_file_exists_and_validates() -> None:
    assert DEFAULT_CONDITIONS.exists()
    data = load_conditions()
    validate_conditions(data)
    assert data["mode"] == "deterministic_full_cone_preconditioned"
    assert data["kernel"]["interaction_scope"] == "full_past_lightcone_all_contributors"
    assert data["kernel"]["interaction_scope_canonical"] is True


def test_simulation_is_deterministic() -> None:
    d1 = run_simulation_dataset()
    d2 = run_simulation_dataset()
    assert d1["conditions_checksum"] == d2["conditions_checksum"]
    assert d1["replay_hash"] == d2["replay_hash"]
    assert d1["run_count"] == d2["run_count"]


def test_required_channel_grid_coverage() -> None:
    dataset = run_simulation_dataset()
    runs = dataset["runs"]
    keys = {(r["phase_id"], int(r["initial_edge_distance"])) for r in runs}
    for phase_id, d0 in keys:
        control = [r for r in runs if r["role"] == "control" and r["phase_id"] == phase_id and int(r["initial_edge_distance"]) == d0]
        signal = [r for r in runs if r["role"] == "signal" and r["phase_id"] == phase_id and int(r["initial_edge_distance"]) == d0]
        assert len(control) == 1
        assert len(signal) >= 1


def test_extraction_is_deterministic() -> None:
    dataset = run_simulation_dataset()
    conditions = load_conditions()
    p1 = extract_alpha_from_dataset(dataset, conditions)
    p2 = extract_alpha_from_dataset(dataset, conditions)
    assert p1["replay_hash"] == p2["replay_hash"]
    assert p1["simulation_replay_hash"] == dataset["replay_hash"]
    assert p1["pooled"]["sample_count"] >= 1
