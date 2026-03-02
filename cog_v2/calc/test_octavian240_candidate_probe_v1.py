from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_octavian240_candidate_probe_v1 import (
    OUT_JSON,
    OUT_MD,
    build_payload,
    write_artifacts,
)


def test_payload_deterministic() -> None:
    a = build_payload(ticks=24, thin_output_step=2)
    b = build_payload(ticks=24, thin_output_step=2)
    assert a["replay_hash"] == b["replay_hash"]


def test_full_240_alphabet_loaded() -> None:
    payload = build_payload(ticks=8, thin_output_step=1)
    assert payload["checks"]["alphabet_size_240"] is True
    assert payload["alphabet_norm_checks"]["all_norm_one"] is True
    assert payload["closure_checks"]["pair_count"] == 240 * 240


def test_closure_is_explicitly_measured() -> None:
    payload = build_payload(ticks=8, thin_output_step=1)
    assert payload["closure_checks"]["counterexample_count"] >= 0
    assert "closed_under_multiplication" in payload["closure_checks"]
    assert len(payload["scenarios"]) == 2


def test_write_artifacts(tmp_path: Path) -> None:
    payload = build_payload(ticks=12, thin_output_step=3)
    out_json = tmp_path / OUT_JSON.name
    out_md = tmp_path / OUT_MD.name
    write_artifacts(payload, json_paths=[out_json], md_paths=[out_md])
    assert out_json.exists()
    assert out_md.exists()
    loaded = json.loads(out_json.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
    md = out_md.read_text(encoding="utf-8")
    assert "Octavian-240 Candidate Probe (v1)" in md

