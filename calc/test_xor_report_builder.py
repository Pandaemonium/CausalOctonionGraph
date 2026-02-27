"""
Tests for calc/xor_report_builder.py
"""

from __future__ import annotations

import json
from pathlib import Path

from calc.xor_report_builder import (
    build_ensemble_report,
    build_report_from_dataset_path,
    render_markdown_report,
    write_xor_report_artifacts,
)


def _fake_dataset():
    return {
        "schema_version": "xor_ensemble_runner_v1",
        "run_count": 2,
        "aggregate_observables": {
            "avg_pair_kind_entropy_bits": 0.5,
            "avg_pair_kind_transition_count": 1.5,
            "pair_kind_counts_total": {"neutral": 3, "repulsive": 1},
        },
        "runs": [
            {
                "scenario_id": "a",
                "title": "A",
                "steps": 3,
                "observables": {
                    "initial_pair_kind": "repulsive",
                    "final_pair_kind": "neutral",
                    "pair_kind_entropy_bits": 0.9,
                    "pair_kind_transition_count": 2,
                },
            },
            {
                "scenario_id": "b",
                "title": "B",
                "steps": 4,
                "observables": {
                    "initial_pair_kind": "none",
                    "final_pair_kind": "none",
                    "pair_kind_entropy_bits": 0.1,
                    "pair_kind_transition_count": 0,
                },
            },
        ],
    }


def test_build_ensemble_report_shape():
    report = build_ensemble_report(_fake_dataset())
    assert report["schema_version"] == "xor_ensemble_report_v1"
    assert report["headline"]["run_count"] == 2
    assert len(report["scenario_cards"]) == 2
    # sorted by entropy desc
    assert report["scenario_cards"][0]["scenario_id"] == "a"


def test_render_markdown_report_contains_sections():
    report = build_ensemble_report(_fake_dataset())
    md = render_markdown_report(report)
    assert "# XOR Ensemble Report" in md
    assert "## Headline" in md
    assert "## Scenario Cards" in md
    assert "`a` (A)" in md


def test_write_report_artifacts(tmp_path: Path):
    report = build_ensemble_report(_fake_dataset())
    json_path = tmp_path / "rep.json"
    md_path = tmp_path / "rep.md"
    write_xor_report_artifacts(report, json_paths=[json_path], md_paths=[md_path])
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "xor_ensemble_report_v1"
    assert md_path.read_text(encoding="utf-8").startswith("# XOR Ensemble Report")


def test_build_report_from_dataset_path(tmp_path: Path):
    ds_path = tmp_path / "ds.json"
    ds_path.write_text(json.dumps(_fake_dataset()), encoding="utf-8")
    report = build_report_from_dataset_path(ds_path)
    assert report["headline"]["run_count"] == 2

