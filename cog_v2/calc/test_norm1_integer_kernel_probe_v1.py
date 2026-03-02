from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_norm1_integer_kernel_probe_v1 import (
    OUT_JSON,
    OUT_MD,
    ProbeParams,
    build_payload,
    write_artifacts,
)


def test_payload_deterministic() -> None:
    params = ProbeParams(range_limit=2, family_sample_cap=24, ticks=12, thin_output_step=2)
    a = build_payload(params)
    b = build_payload(params)
    assert a["replay_hash"] == b["replay_hash"]


def test_core_checks_hold_small_run() -> None:
    payload = build_payload(ProbeParams(range_limit=2, family_sample_cap=16, ticks=10, thin_output_step=1))
    checks = payload["checks"]
    assert checks["family_states_constructed_norm_one"] is True
    assert checks["vacuum_fixed_point"] is True
    assert isinstance(checks["closure_pair_products_norm_one"], bool)
    assert isinstance(checks["world_evolution_preserves_norm_one"], bool)
    assert payload["closure_probe"]["failed_pair_count"] > 0
    assert payload["world_probe"]["max_coeff_linf_digits_any_tick"] >= 2


def test_write_artifacts(tmp_path: Path) -> None:
    payload = build_payload(ProbeParams(range_limit=2, family_sample_cap=16, ticks=10, thin_output_step=2))
    out_json = tmp_path / OUT_JSON.name
    out_md = tmp_path / OUT_MD.name
    write_artifacts(payload, json_paths=[out_json], md_paths=[out_md])
    assert out_json.exists()
    assert out_md.exists()
    loaded = json.loads(out_json.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
    md = out_md.read_text(encoding="utf-8")
    assert "Norm1 Integer Multiplicative Kernel Probe (v1)" in md
