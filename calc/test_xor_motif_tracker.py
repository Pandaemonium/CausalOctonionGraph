"""Tests for calc/xor_motif_tracker.py."""

from __future__ import annotations

from calc.xor_furey_ideals import furey_electron_doubled
from calc.xor_full_lightcone_engine import simulate_full_lightcone
from calc.xor_motif_tracker import (
    _to_base8,
    best_motif_position,
    edge_distance_series,
    motif_l1_distance,
    run_builtin_motif_tracking,
    track_motif_path,
)


def _enc(state):
    return [[_to_base8(re), _to_base8(im)] for (re, im) in state]


def test_motif_l1_distance_zero_for_exact_match() -> None:
    e = furey_electron_doubled()
    assert motif_l1_distance(e, e) == 0


def test_best_motif_position_tiebreak_uses_smaller_position() -> None:
    e = furey_electron_doubled()
    depth_slice = {
        "-1": _enc(e),
        "1": _enc(e),
    }
    best = best_motif_position(depth_slice=depth_slice, motif=e)
    assert best["exact_match"] is True
    assert best["pos"] == -1


def test_best_motif_position_tiebreak_right_prefers_larger_position() -> None:
    e = furey_electron_doubled()
    depth_slice = {
        "-1": _enc(e),
        "1": _enc(e),
    }
    best = best_motif_position(depth_slice=depth_slice, motif=e, side_preference="right")
    assert best["exact_match"] is True
    assert best["pos"] == 1


def test_track_motif_path_len_matches_depth_horizon_plus_one() -> None:
    run = simulate_full_lightcone(
        channel_id="electron_electron",
        depth_horizon=10,
        initial_edge_distance=5,
        left_motif_id="furey_electron_doubled",
        right_motif_id="furey_electron_doubled",
    )
    path = track_motif_path(
        run_payload=run,
        motif_id="furey_electron_doubled",
        track_id="e_path",
    )
    assert len(path) == 11
    assert path[0]["depth"] == 0
    assert path[-1]["depth"] == 10


def test_edge_distance_series_nonnegative() -> None:
    run = simulate_full_lightcone(
        channel_id="electron_positron",
        depth_horizon=8,
        initial_edge_distance=5,
        left_motif_id="furey_electron_doubled",
        right_motif_id="furey_dual_electron_doubled",
    )
    pa = track_motif_path(run_payload=run, motif_id="furey_electron_doubled", track_id="a")
    pb = track_motif_path(run_payload=run, motif_id="furey_dual_electron_doubled", track_id="b")
    ds = edge_distance_series(pa, pb)
    assert len(ds) == 9
    assert all(int(r["edge_distance"]) >= 0 for r in ds)


def test_builtin_motif_tracking_shape() -> None:
    data = run_builtin_motif_tracking(depth_horizon=12, initial_edge_distance=5)
    assert data["schema_version"] == "xor_motif_tracker_v1"
    assert set(data["cases"].keys()) == {"electron_electron", "electron_positron"}
    ee_dist = data["cases"]["electron_electron"]["distance"]
    ep_dist = data["cases"]["electron_positron"]["distance"]
    assert len(ee_dist) == 13
    assert len(ep_dist) == 13
    # At depth 0, left/right anchored electron tracks must be separated by initial distance.
    assert int(ee_dist[0]["edge_distance"]) == 5
