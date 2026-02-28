from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_theta001_nonzero_search_v1 import (
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
    assert payload["schema_version"] == "theta001_nonzero_search_v1"
    assert payload["claim_id"] == "THETA-001"
    summary = payload["summary"]
    assert summary["weak_squared_all_zero"] is True
    assert summary["ckm_squared_all_zero"] is True
    assert summary["weak_nonzero_excluding_t0_count"] > 0
    assert summary["ckm_nonzero_excluding_t0_count"] > 0
    assert summary["weak_nonzero_excluding_t0_rate"] > 0.5
    assert summary["ckm_nonzero_excluding_t0_rate"] > 0.5
    assert len(payload["top_weak_nonzero_excluding_t0"]) > 0
    assert len(payload["top_ckm_nonzero_excluding_t0"]) > 0


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
    assert "THETA-001 Nonzero Search (v1)" in md
    assert "Top CKM Nonzero Cases" in md

