"""Governance tests for ALPHA-001 policy-locked estimator."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from calc.estimate_alpha_from_policy import (
    POLICY_FILE_DEFAULT,
    load_policy_bundle,
    predeclared_policy_ids,
    run_ablation,
    run_policy,
    validate_policy_bundle,
)


def test_policy_file_exists() -> None:
    assert POLICY_FILE_DEFAULT.exists()
    assert POLICY_FILE_DEFAULT.name == "alpha_policies.json"
    assert POLICY_FILE_DEFAULT.parent.name == "calc"


def test_predeclared_policy_ids_are_frozen() -> None:
    assert predeclared_policy_ids() == [
        "alpha_proxy_v1_area",
        "alpha_proxy_v2_stabilizer_gap",
        "alpha_proxy_v3_cubic_fano",
    ]


def test_unknown_policy_fails() -> None:
    with pytest.raises(KeyError):
        run_policy("unknown_policy")


def test_requires_no_fitted_attenuation(tmp_path: Path) -> None:
    bundle = load_policy_bundle()
    bundle["policies"][0]["no_fitted_attenuation"] = False
    tmp = tmp_path / "alpha_policies_bad.json"
    tmp.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    with pytest.raises(ValueError):
        validate_policy_bundle(load_policy_bundle(tmp))


def test_expected_proxy_values() -> None:
    v1 = run_policy("alpha_proxy_v1_area")
    v2 = run_policy("alpha_proxy_v2_stabilizer_gap")
    v3 = run_policy("alpha_proxy_v3_cubic_fano")

    assert v1["candidate"]["value"] == pytest.approx(1.0 / 49.0, rel=1e-12)
    assert v2["candidate"]["value"] == pytest.approx(1.0 / 153.0, rel=1e-12)
    assert v3["candidate"]["value"] == pytest.approx(1.0 / 145.0, rel=1e-12)


def test_replay_hash_is_stable() -> None:
    r1 = run_policy("alpha_proxy_v3_cubic_fano")
    r2 = run_policy("alpha_proxy_v3_cubic_fano")
    assert r1["replay_hash"] == r2["replay_hash"]


def test_ablation_runs_all_declared_rows_once() -> None:
    rows = run_ablation()
    assert [r["policy_id"] for r in rows] == predeclared_policy_ids()
    assert len({r["policy_checksum"] for r in rows}) == len(rows)
    assert len({r["replay_hash"] for r in rows}) == len(rows)


def test_best_declared_row_is_v3() -> None:
    rows = run_ablation()
    best = min(rows, key=lambda row: row["relative_gap"]["value"])
    assert best["policy_id"] == "alpha_proxy_v3_cubic_fano"

