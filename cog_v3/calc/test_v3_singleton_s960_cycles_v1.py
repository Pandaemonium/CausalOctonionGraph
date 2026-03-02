from __future__ import annotations

import json
from pathlib import Path

from cog_v3.calc.build_v3_singleton_s960_cycles_v1 import (
    OUT_JSON,
    OUT_MD,
    S960_SIZE,
    build_payload,
    write_artifacts,
)
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


def test_payload_deterministic() -> None:
    a = build_payload(example_ticks=8, top_n=10)
    b = build_payload(example_ticks=8, top_n=10)
    assert a["replay_hash"] == b["replay_hash"]


def test_contract_checks() -> None:
    payload = build_payload(example_ticks=8, top_n=8)
    assert payload["schema_version"] == "v3_singleton_s960_cycles_v1"
    assert payload["kernel_profile"] == k.KERNEL_PROFILE
    assert payload["convention_id"] == k.CONVENTION_ID
    assert payload["alphabet_id"] == "s960_shared_phase_v1"
    assert payload["summary"]["seed_count"] == int(S960_SIZE)
    assert payload["checks"]["seed_count_ok"] is True
    assert payload["checks"]["all_periods_positive"] is True
    assert payload["checks"]["all_periods_within_bound"] is True
    assert payload["checks"]["no_scan_errors"] is True


def test_write_artifacts(tmp_path: Path) -> None:
    payload = build_payload(example_ticks=8, top_n=6)
    out_json = tmp_path / OUT_JSON.name
    out_md = tmp_path / OUT_MD.name
    write_artifacts(payload, json_paths=[out_json], md_paths=[out_md])
    assert out_json.exists()
    assert out_md.exists()
    loaded = json.loads(out_json.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
    md = out_md.read_text(encoding="utf-8")
    assert "COG v3 Singleton S960 Cycle Census (v1)" in md

