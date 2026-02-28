from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_theta001_nonzero_robust_casebook_v1 import (
    OUT_JSON,
    OUT_MD,
    build_payload,
    write_artifacts,
)


def test_payload_deterministic() -> None:
    a = build_payload()
    b = build_payload()
    assert a["replay_hash"] == b["replay_hash"]
    assert a["summary"] == b["summary"]


def test_payload_expected_properties() -> None:
    payload = build_payload()
    assert payload["schema_version"] == "theta001_nonzero_robust_casebook_v1"
    assert payload["claim_id"] == "THETA-002"
    summary = payload["summary"]
    assert summary["developed_count"] == 24
    assert summary["all_squared_zero_rate_one"] is True
    assert summary["robust_total_count"] >= 1
    for row in payload["developed_candidates"]:
        assert float(row["squared_zero_rate"]) == 1.0
        assert float(row["nonzero_rate_excluding_t0"]) > 0.0


def test_write_artifacts(tmp_path: Path) -> None:
    payload = build_payload()
    json_path = tmp_path / OUT_JSON.name
    md_path = tmp_path / OUT_MD.name
    write_artifacts(payload, json_paths=[json_path], md_paths=[md_path])
    assert json_path.exists()
    assert md_path.exists()
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
    md = md_path.read_text(encoding="utf-8")
    assert "THETA-002 Nonzero Robust Casebook (v1)" in md
    assert "Candidate Scores" in md

