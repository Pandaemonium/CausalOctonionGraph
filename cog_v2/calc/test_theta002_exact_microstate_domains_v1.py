from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_theta002_exact_microstate_domains_v1 import (
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
    assert payload["schema_version"] == "theta002_exact_microstate_domains_v1"
    assert payload["claim_id"] == "THETA-002"
    assert payload["summary"]["scenario_count"] == 4
    assert payload["summary"]["all_squared_totals_zero"] is True
    assert payload["summary"]["domain_signs_satisfied"] is True

    expected_domains = {"weak_positive", "weak_negative", "ckm_positive", "ckm_negative"}
    got_domains = {str(s["domain_id"]) for s in payload["scenarios"]}
    assert got_domains == expected_domains

    for s in payload["scenarios"]:
        domain_id = str(s["domain_id"])
        total_ex_t0 = int(s["expected_totals"]["oriented_cubic_residual_total_excluding_t0"])
        sq_total = int(s["expected_totals"]["squared_residual_total"])
        assert sq_total == 0
        assert total_ex_t0 != 0
        if domain_id.endswith("_positive"):
            assert total_ex_t0 > 0
        elif domain_id.endswith("_negative"):
            assert total_ex_t0 < 0
        else:
            raise AssertionError(f"Unknown domain id {domain_id}")

        ticks = list(s["tick_rows"])
        assert len(ticks) == len(s["input"]["op_sequence"]) + 1
        for row in ticks:
            assert len(row["orig_state_vector"]) == 8
            assert len(row["dual_state_vector"]) == 8


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
    assert "THETA-002 Exact Microstate Domains (v1)" in md
    assert "weak_positive" in md
    assert "ckm_negative" in md

