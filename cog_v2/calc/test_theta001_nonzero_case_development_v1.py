from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_theta001_nonzero_case_development_v1 import (
    OUT_JSON,
    OUT_MD,
    build_payload,
    write_artifacts,
)


def test_payload_deterministic() -> None:
    a = build_payload()
    b = build_payload()
    assert a["replay_hash"] == b["replay_hash"]
    assert a["aggregate"] == b["aggregate"]


def test_payload_expected_properties() -> None:
    payload = build_payload()
    assert payload["schema_version"] == "theta001_nonzero_case_development_v1"
    assert payload["claim_id"] == "THETA-001"
    assert payload["developed_case_count"] == 12
    assert payload["aggregate"]["all_sq_totals_zero"] is True
    assert payload["aggregate"]["all_cubic_totals_nonzero"] is True
    assert payload["aggregate"]["cases_with_nonzero_cubic_total_excluding_t0"] >= 1
    assert payload["aggregate"]["weak_cases_with_nonzero_cubic_total_excluding_t0"] == 0
    assert payload["aggregate"]["ckm_cases_with_nonzero_cubic_total_excluding_t0"] >= 1

    cases = payload["developed_cases"]
    assert len(cases) == 12
    for c in cases:
        assert int(c["sq_total"]) == 0
        assert int(c["cubic_total"]) != 0
        assert "cubic_total_excluding_t0" in c
        assert "first_nonzero_cubic_tick_excluding_t0" in c
        assert isinstance(c["tick_rows"], list)
        assert len(c["tick_rows"]) == int(c["op_depth"]) + 1
        for row in c["tick_rows"]:
            assert "sq_delta" in row
            assert "cubic_delta" in row
            assert "cp_map_matches_dual" in row
            assert "cp_map_matches_neg_dual" in row


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
    assert "THETA-001 Nonzero Candidate Case Development (v1)" in md
    assert "Developed Cases (summary)" in md
