from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_phase_shared_unit_loop_probe_v1 import (
    OUT_JSON,
    OUT_MD,
    build_payload,
    write_artifacts,
)


def test_payload_deterministic() -> None:
    a = build_payload(ticks=48, thin_output_step=2)
    b = build_payload(ticks=48, thin_output_step=2)
    assert a["replay_hash"] == b["replay_hash"]


def test_closure_and_alphabet_membership() -> None:
    payload = build_payload(ticks=32, thin_output_step=1)
    assert payload["checks"]["closure_pair_scan_ok"] is True
    assert payload["checks"]["all_states_always_in_alphabet"] is True
    assert payload["closure_checks"]["counterexample_count"] == 0


def test_write_artifacts(tmp_path: Path) -> None:
    payload = build_payload(ticks=24, thin_output_step=4)
    out_json = tmp_path / OUT_JSON.name
    out_md = tmp_path / OUT_MD.name
    write_artifacts(payload, json_paths=[out_json], md_paths=[out_md])
    assert out_json.exists()
    assert out_md.exists()
    loaded = json.loads(out_json.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
    md = out_md.read_text(encoding="utf-8")
    assert "Phase-Shared Unit Loop Probe (v1)" in md

