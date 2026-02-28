from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_theta001_nonzero_candidate_probe_v1 import (
    OUT_JSON,
    OUT_MD,
    build_payload,
    write_artifacts,
)


def test_probe_payload_deterministic() -> None:
    a = build_payload()
    b = build_payload()
    assert a["replay_hash"] == b["replay_hash"]
    assert a["weak_leakage_summary"] == b["weak_leakage_summary"]
    assert a["ckm_like_summary"] == b["ckm_like_summary"]


def test_probe_detects_nonzero_candidate() -> None:
    payload = build_payload()
    assert payload["schema_version"] == "theta001_nonzero_candidate_probe_v1"
    assert payload["falsification_candidate"]["candidate_observable_id"] == "oriented_fano_cubic_cp_odd_v1"
    assert payload["weak_leakage_summary"]["squared_all_zero"] is True
    assert payload["ckm_like_summary"]["squared_all_zero"] is True
    assert payload["weak_leakage_summary"]["oriented_cubic_nonzero_count"] > 0
    assert payload["ckm_like_summary"]["oriented_cubic_nonzero_count"] > 0
    assert payload["falsification_candidate"]["has_nonzero_cases"] is True


def test_probe_write_artifacts(tmp_path: Path) -> None:
    payload = build_payload()
    json_path = tmp_path / OUT_JSON.name
    md_path = tmp_path / OUT_MD.name
    write_artifacts(payload, json_paths=[json_path], md_paths=[md_path])
    assert json_path.exists()
    assert md_path.exists()
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
    md = md_path.read_text(encoding="utf-8")
    assert "THETA-001 Nonzero Candidate Probe (v1)" in md
    assert "Candidate Conclusion" in md

