"""Tests for RFC-053 many-body reduction ladder baseline."""

from __future__ import annotations

import json
from pathlib import Path

from calc.many_body_reduction_ladder import (
    Node,
    conditioned_score,
    ladder_scenarios,
    run_ladder,
    run_scenario,
    write_artifacts,
)


def test_n2_and_n3_inert_are_exact_reductions():
    scenarios = {s["scenario"]: s for s in ladder_scenarios()}
    assert scenarios["N2_baseline"]["reduction_mode"] == "exact"
    assert scenarios["N2_baseline"]["error_max"] == 0
    assert scenarios["N3_inert_spectator"]["reduction_mode"] == "exact"
    assert scenarios["N3_inert_spectator"]["error_max"] == 0


def test_active_background_produces_nonzero_reduction_error():
    scenarios = {s["scenario"]: s for s in ladder_scenarios()}
    n3_active = scenarios["N3_active_spectator"]
    assert n3_active["reduction_mode"] == "approx"
    assert n3_active["error_max"] > 0
    assert n3_active["divergence_tick"] == 0


def test_conditioned_score_is_permutation_invariant_over_externals():
    s1 = conditioned_score(-0.5, -0.5, [+0.5, -0.5, 0.0])
    s2 = conditioned_score(-0.5, -0.5, [0.0, +0.5, -0.5])
    s3 = conditioned_score(-0.5, -0.5, [-0.5, 0.0, +0.5])
    assert s1 == s2 == s3


def test_run_scenario_rejects_non_positive_horizon():
    try:
        run_scenario("bad", [Node("a", -0.5), Node("b", -0.5)], ("a", "b"), horizon=0)
    except ValueError as exc:
        assert "horizon" in str(exc)
    else:
        raise AssertionError("expected ValueError for non-positive horizon")


def test_run_ladder_replay_hash_is_deterministic():
    a = run_ladder()
    b = run_ladder()
    assert a["replay_hash"] == b["replay_hash"]
    assert a["scenarios"] == b["scenarios"]


def test_write_artifacts_writes_json_and_markdown(tmp_path: Path):
    result = run_ladder()
    json_path = tmp_path / "many_body_reduction_ladder.json"
    md_path = tmp_path / "many_body_reduction_ladder.md"
    write_artifacts(result, str(json_path), str(md_path))

    assert json_path.exists()
    assert md_path.exists()

    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == result["replay_hash"]
    md = md_path.read_text(encoding="utf-8")
    assert "Many-Body Reduction Ladder Results" in md
    assert "N2_baseline" in md

