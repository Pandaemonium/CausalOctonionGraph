from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cog_v2.scripts.validate_layered_causality_v1 import ValidationConfig, _demo_graphs, analyze_graph


def test_layered_demo_passes() -> None:
    payload = analyze_graph(_demo_graphs()["layered_ok"], ValidationConfig(max_sources=64))
    summary = payload["summary"]
    assert summary["is_dag"] is True
    assert summary["strict_layering_holds"] is True
    assert summary["max_delta"] == 0
    assert summary["canonical_layered_verdict"] == "pass"


def test_shortcut_demo_fails() -> None:
    payload = analyze_graph(_demo_graphs()["shortcut_defect"], ValidationConfig(max_sources=64))
    summary = payload["summary"]
    assert summary["is_dag"] is True
    assert summary["strict_layering_holds"] is False
    assert summary["layer_violation_count"] >= 1
    assert summary["max_delta"] >= 1
    assert summary["canonical_layered_verdict"] == "fail"
