from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_photon_chirality_direction_probe_v1 import (
    ChiralityProbeParams,
    OUT_JSON,
    OUT_MD,
    build_payload,
    write_artifacts,
)


def test_payload_deterministic() -> None:
    params = ChiralityProbeParams(
        ticks=32,
        width=129,
        packet_width=9,
        warmup_ticks=8,
        thin_output_step=2,
    )
    a = build_payload(params)
    b = build_payload(params)
    assert a["replay_hash"] == b["replay_hash"]


def test_fronts_saturate_lightcone() -> None:
    payload = build_payload(
        ChiralityProbeParams(
            ticks=24,
            width=129,
            packet_width=9,
            warmup_ticks=8,
            thin_output_step=1,
        )
    )
    assert payload["checks"]["all_cases_lightcone_saturated_fronts"] is True


def test_write_artifacts(tmp_path: Path) -> None:
    payload = build_payload(
        ChiralityProbeParams(
            ticks=24,
            width=129,
            packet_width=9,
            warmup_ticks=8,
            thin_output_step=3,
        )
    )
    out_json = tmp_path / OUT_JSON.name
    out_md = tmp_path / OUT_MD.name
    write_artifacts(payload, json_paths=[out_json], md_paths=[out_md])
    assert out_json.exists()
    assert out_md.exists()
    loaded = json.loads(out_json.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
    md = out_md.read_text(encoding="utf-8")
    assert "Photon Chirality-Direction Probe (v1)" in md
