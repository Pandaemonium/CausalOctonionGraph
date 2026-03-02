from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_norm1_integer_failure_cases_v1 import (
    OUT_JSON,
    OUT_MD,
    build_payload,
    write_artifacts,
)


def test_payload_deterministic_small() -> None:
    a = build_payload(range_limit=2, sample_cap=64, max_failure_records=200)
    b = build_payload(range_limit=2, sample_cap=64, max_failure_records=200)
    assert a["replay_hash"] == b["replay_hash"]


def test_payload_contains_mixed_channels_small() -> None:
    payload = build_payload(range_limit=2, sample_cap=128, max_failure_records=500)
    assert payload["state_count"] == 128
    assert payload["e000_one_state_count"] > 0
    assert payload["e000_zero_state_count"] > 0
    assert payload["e111_nonzero_state_count"] > 0
    assert payload["failure_count"] >= payload["recorded_failure_count"]
    assert payload["recorded_failure_count"] <= 500


def test_write_artifacts(tmp_path: Path) -> None:
    payload = build_payload(range_limit=2, sample_cap=64, max_failure_records=100)
    out_json = tmp_path / OUT_JSON.name
    out_md = tmp_path / OUT_MD.name
    write_artifacts(payload, json_paths=[out_json], md_paths=[out_md])
    assert out_json.exists()
    assert out_md.exists()
    loaded = json.loads(out_json.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
    md = out_md.read_text(encoding="utf-8")
    assert "Norm1 Integer Failure Cases (v1)" in md
