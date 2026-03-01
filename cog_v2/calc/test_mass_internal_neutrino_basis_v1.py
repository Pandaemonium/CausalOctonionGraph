from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_mass_internal_neutrino_basis_v1 import (
    OUT_JSON,
    OUT_MD,
    MassBasisParams,
    build_payload,
    write_artifacts,
)


def test_payload_deterministic() -> None:
    params = MassBasisParams(
        ticks=80,
        warmup_ticks=40,
        width=48,
        lambda_vacuum_drag=1.0,
        source_op_cycle=(7, 7, 7, 7),
    )
    a = build_payload(params)
    b = build_payload(params)
    assert a["replay_hash"] == b["replay_hash"]
    assert a["derived"] == b["derived"]


def test_neutrino_basis_mass_positive_and_ratio_finite() -> None:
    payload = build_payload(
        MassBasisParams(
            ticks=80,
            warmup_ticks=40,
            width=48,
            lambda_vacuum_drag=1.0,
            source_op_cycle=(7, 7, 7, 7),
        )
    )
    assert payload["schema_version"] == "mass_internal_neutrino_basis_v1"
    checks = payload["checks"]
    assert checks["m_eff_neutrino_positive"] is True
    assert checks["m_eff_electron_positive"] is True
    assert checks["rows_match_ticks"] is True
    ratio = float(payload["derived"]["m_electron_in_neutrino_units"])
    assert ratio > 0.0
    assert ratio < 1e6


def test_write_artifacts(tmp_path: Path) -> None:
    payload = build_payload(
        MassBasisParams(
            ticks=40,
            warmup_ticks=20,
            width=32,
            lambda_vacuum_drag=1.0,
            source_op_cycle=(7, 7),
        )
    )
    out_json = tmp_path / OUT_JSON.name
    out_md = tmp_path / OUT_MD.name
    write_artifacts(payload, json_paths=[out_json], md_paths=[out_md])
    assert out_json.exists()
    assert out_md.exists()
    loaded = json.loads(out_json.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
    md = out_md.read_text(encoding="utf-8")
    assert "Mass Internal Neutrino Basis (v1)" in md
    assert "m_electron_in_neutrino_units" in md

