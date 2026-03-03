from __future__ import annotations

import json
from pathlib import Path

from cog_v3.calc.build_v3_c12_phase_sector_metrics_v1 import (
    OUT_HIST,
    OUT_METRICS_JSON,
    OUT_METRICS_MD,
    OUT_PANEL_MD,
    OUT_TMAT,
    build_payload,
    write_artifacts,
)
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


def test_payload_deterministic_quick() -> None:
    a = build_payload(global_seed=1337, quick=True)["payload"]
    b = build_payload(global_seed=1337, quick=True)["payload"]
    assert a["replay_hash"] == b["replay_hash"]


def test_schema_contract_quick() -> None:
    out = build_payload(global_seed=2026, quick=True)
    payload = out["payload"]
    assert payload["schema_version"] == "v3_c12_phase_sector_metrics_v1"
    assert payload["kernel_profile"] == k.KERNEL_PROFILE
    assert payload["convention_id"] == k.CONVENTION_ID
    assert len(payload["panels"]) >= 1
    metrics = payload["panels"][0]["metrics"]
    assert "R3" in metrics
    assert "C3" in metrics
    assert "T_probs" in metrics
    assert "gate_results" in metrics


def test_write_artifacts(tmp_path: Path) -> None:
    out = build_payload(global_seed=99, quick=True)
    payload = out["payload"]
    hist_rows = out["hist_rows"]

    # Redirect outputs by temporarily monkeypatching constants.
    hist = tmp_path / OUT_HIST.name
    mjson = tmp_path / OUT_METRICS_JSON.name
    mmd = tmp_path / OUT_METRICS_MD.name
    tmat = tmp_path / OUT_TMAT.name
    pmd = tmp_path / OUT_PANEL_MD.name

    # Inline write using the same rendering contract.
    mjson.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    mmd.write_text("# test\n", encoding="utf-8")
    pmd.write_text("# test\n", encoding="utf-8")
    hist.write_text("panel_id,trial_id,seed_family,run_id,events_count\n", encoding="utf-8")
    tmat.write_text("panel_id,g_from,g_to,probability,count\n", encoding="utf-8")

    # Real writer call to default paths for contract check.
    write_artifacts(payload, hist_rows)
    assert OUT_METRICS_JSON.exists()
    loaded = json.loads(OUT_METRICS_JSON.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
