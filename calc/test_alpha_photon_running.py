"""Tests for calc/derive_alpha_photon_running.py."""

from __future__ import annotations

import json
from pathlib import Path

from calc.derive_alpha_photon_running import (
    load_conditions,
    run_alpha_photon_running,
    validate_conditions,
)


def _small_conditions() -> dict:
    base = load_conditions()
    base["initial_edge_distances"] = [1, 3, 5]
    base["depth_horizon_rule"]["slope"] = 2
    base["depth_horizon_rule"]["intercept"] = 8
    base["depth_horizon_rule"]["min_depth"] = 10
    base["phase_offsets"] = [0, 1]
    return base


def test_default_conditions_file_exists_and_validates() -> None:
    data = load_conditions()
    validate_conditions(data)
    assert data["kernel"]["interaction_scope"] == "full_past_lightcone_all_contributors"


def test_small_run_is_deterministic(tmp_path: Path) -> None:
    cond = _small_conditions()
    p = tmp_path / "cond.json"
    p.write_text(json.dumps(cond, indent=2), encoding="utf-8")

    a = run_alpha_photon_running(p)
    b = run_alpha_photon_running(p)
    assert a["replay_hash"] == b["replay_hash"]
    assert len(a["rows"]) == 3


def test_rows_sorted_by_distance_and_have_uv_ir_summary(tmp_path: Path) -> None:
    cond = _small_conditions()
    p = tmp_path / "cond.json"
    p.write_text(json.dumps(cond, indent=2), encoding="utf-8")
    out = run_alpha_photon_running(p)

    d0s = [int(r["initial_edge_distance"]) for r in out["rows"]]
    assert d0s == sorted(d0s)
    assert out["summary"]["uv_distance"] == d0s[0]
    assert out["summary"]["ir_distance"] == d0s[-1]


def test_signal_event_counts_present(tmp_path: Path) -> None:
    cond = _small_conditions()
    p = tmp_path / "cond.json"
    p.write_text(json.dumps(cond, indent=2), encoding="utf-8")
    out = run_alpha_photon_running(p)
    assert all(int(r["phase_valid_count"]) >= 0 for r in out["rows"])


def test_alpha_observable_is_bounded_unit_interval(tmp_path: Path) -> None:
    cond = _small_conditions()
    p = tmp_path / "cond.json"
    p.write_text(json.dumps(cond, indent=2), encoding="utf-8")
    out = run_alpha_photon_running(p)

    for row in out["rows"]:
        for phase_row in row["phase_results"]:
            alpha_em = phase_row["alpha_em"]
            if alpha_em is None:
                continue
            assert 0.0 <= float(alpha_em) < 1.0
