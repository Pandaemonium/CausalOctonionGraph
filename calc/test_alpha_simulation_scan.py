"""Tests for deterministic ALPHA simulation scan."""

from __future__ import annotations

from calc.simulate_alpha_em_scan import (
    DEFAULT_CONDITIONS,
    load_conditions,
    run_scan,
    validate_conditions,
)


def test_conditions_file_exists() -> None:
    assert DEFAULT_CONDITIONS.exists()
    assert DEFAULT_CONDITIONS.name == "alpha_simulation_conditions.json"


def test_conditions_validate() -> None:
    data = load_conditions()
    validate_conditions(data)
    assert data["mode"] == "deterministic_full_cone_preconditioned"
    assert len(data["conditions"]) >= 1


def test_scan_is_deterministic() -> None:
    rows1 = run_scan()
    rows2 = run_scan()
    assert rows1 == rows2


def test_proxy_monotonicity_for_sites_and_ticks() -> None:
    rows = run_scan()
    rows = sorted(rows, key=lambda r: r["cone_depth"])
    site_proxies = [r["proxies"]["alpha_proxy_cone_sites"] for r in rows]
    tick_proxies = [r["proxies"]["alpha_proxy_cycle_ticks"] for r in rows]

    for i in range(len(site_proxies) - 1):
        assert site_proxies[i] > site_proxies[i + 1]
        assert tick_proxies[i] > tick_proxies[i + 1]


def test_scan_row_shape() -> None:
    row = run_scan()[0]
    required = {
        "condition_id",
        "cone_depth",
        "full_cone_sites",
        "ce_exact",
        "ce_l1",
        "ce_ticks_exact",
        "proxies",
        "relative_gaps",
        "best_proxy_id",
        "best_proxy_value",
        "best_proxy_relative_gap",
        "replay_hash",
    }
    assert required.issubset(set(row.keys()))

