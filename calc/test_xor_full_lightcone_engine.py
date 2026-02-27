"""Tests for calc/xor_full_lightcone_engine.py."""

from __future__ import annotations

from calc.xor_full_lightcone_engine import (
    run_builtin_full_lightcone_cases,
    simulate_full_lightcone,
)


def test_simulate_full_lightcone_deterministic_replay_hash() -> None:
    a = simulate_full_lightcone(
        channel_id="electron_electron",
        depth_horizon=12,
        initial_edge_distance=5,
        left_motif_id="furey_electron_doubled",
        right_motif_id="furey_electron_doubled",
    )
    b = simulate_full_lightcone(
        channel_id="electron_electron",
        depth_horizon=12,
        initial_edge_distance=5,
        left_motif_id="furey_electron_doubled",
        right_motif_id="furey_electron_doubled",
    )
    assert a["replay_hash"] == b["replay_hash"]


def test_kernel_flags_are_canonical_full_cone() -> None:
    data = simulate_full_lightcone(
        channel_id="electron_positron",
        depth_horizon=10,
        initial_edge_distance=5,
        left_motif_id="furey_electron_doubled",
        right_motif_id="furey_dual_electron_doubled",
    )
    k = data["kernel"]
    assert k["interaction_scope"] == "full_past_lightcone_all_contributors"
    assert k["ordering"] == "topoDepth_then_position"
    assert k["no_spawn"] is True
    assert k["full_lightcone_preconditioned"] is True


def test_contributor_count_exceeds_parent_only_interior() -> None:
    data = simulate_full_lightcone(
        channel_id="electron_electron",
        depth_horizon=8,
        initial_edge_distance=5,
        left_motif_id="furey_electron_doubled",
        right_motif_id="furey_electron_doubled",
    )
    rows = data["csv_rows"]
    # Interior node at depth 5 near center; parent-only would be 2.
    sample = [r for r in rows if int(r["depth"]) == 5 and int(r["pos"]) == 2]
    assert len(sample) == 1
    assert int(sample[0]["contributor_count"]) > 2


def test_depth_summary_matches_predetermined_cone_growth() -> None:
    data = simulate_full_lightcone(
        channel_id="electron_electron",
        depth_horizon=9,
        initial_edge_distance=5,
        left_motif_id="furey_electron_doubled",
        right_motif_id="furey_electron_doubled",
    )
    base = 6  # initial nodes from [0..5]
    for row in data["depth_summary"]:
        d = int(row["depth"])
        expected = base + 2 * d
        assert int(row["node_count"]) == expected


def test_builtin_case_keys() -> None:
    ds = run_builtin_full_lightcone_cases(depth_horizon=8, initial_edge_distance=5)
    assert ds["schema_version"] == "xor_full_lightcone_cases_v1"
    assert set(ds["cases"].keys()) == {"electron_electron", "electron_positron"}

