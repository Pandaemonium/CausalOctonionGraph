"""Tests for calc/estimate_weinberg_angle_weighted.py."""

import pytest

from calc.estimate_weinberg_angle_weighted import build_payload, render_markdown


def test_build_payload_h2_only() -> None:
    payload = build_payload(include_bridge=False)
    assert payload["rfc"] == "RFC-029"
    assert payload["target_scale"] == "M_Z"
    assert payload["h1_enabled"] is False
    assert len(payload["h2_rows"]) == 3
    assert payload["h1_rows"] == []
    assert payload["h2_best_by_abs_gap"]["policy_id"] == "h2_exclusive_u1_quarter"


def test_build_payload_with_bridge() -> None:
    payload = build_payload(include_bridge=True)
    assert payload["h1_enabled"] is True
    assert len(payload["h2_rows"]) == 3
    assert len(payload["h1_rows"]) == 9
    best = payload["h1_best_by_abs_gap"]
    assert best["uv_policy_id"] in {
        "h2_baseline_half",
        "h2_exclusive_u1_quarter",
        "h2_weak_boost_third",
    }
    assert best["bridge_policy_id"] in {
        "h1_no_running",
        "h1_mild_running_4x0p95",
        "h1_strong_running_8x0p90",
    }
    assert abs(best["gap_from_target"]) <= abs(payload["h2_best_by_abs_gap"]["gap_from_target"])


def test_render_markdown_contains_tables() -> None:
    payload = build_payload(include_bridge=True)
    md = render_markdown(payload)
    assert "## H2 Results" in md
    assert "## H1 Bridge Results" in md
    assert "h2_exclusive_u1_quarter" in md
    assert "h1_no_running" in md
