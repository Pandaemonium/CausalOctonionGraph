"""Tests for calc/gauge_scale_bridge.py."""

import pytest

from calc.gauge_scale_bridge import (
    apply_discrete_running,
    predeclared_bridge_policy_ids,
    required_attenuation_for_target,
    run_bridge_for_value,
)


def test_apply_discrete_running_identity() -> None:
    assert apply_discrete_running(0.25, 0, 1.0) == pytest.approx(0.25, rel=1e-12)


def test_apply_discrete_running_monotone_decrease() -> None:
    uv = 0.25
    mild = apply_discrete_running(uv, 4, 0.95)
    strong = apply_discrete_running(uv, 8, 0.90)
    assert strong < mild < uv


def test_required_attenuation_for_target() -> None:
    uv = 0.25
    target = 0.23122
    attn = required_attenuation_for_target(uv, target, 4)
    bridged = apply_discrete_running(uv, 4, attn)
    assert bridged == pytest.approx(target, rel=1e-12)


def test_predeclared_bridge_policy_ids() -> None:
    assert predeclared_bridge_policy_ids() == [
        "h1_no_running",
        "h1_mild_running_4x0p95",
        "h1_strong_running_8x0p90",
    ]


def test_run_bridge_for_value() -> None:
    rows = run_bridge_for_value(0.25, "h2_exclusive_u1_quarter")
    assert len(rows) == 3
    assert rows[0]["bridge_policy_id"] == "h1_no_running"
    assert rows[0]["sin2_theta_w_bridged"] == pytest.approx(0.25, rel=1e-12)

