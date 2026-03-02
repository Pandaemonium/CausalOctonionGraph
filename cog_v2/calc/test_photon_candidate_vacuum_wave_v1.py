from __future__ import annotations

import json
from pathlib import Path

from cog_v2.calc.build_photon_candidate_vacuum_wave_v1 import (
    OUT_JSON,
    OUT_MD,
    PhotonWaveParams,
    build_payload,
    write_artifacts,
)


def test_payload_deterministic() -> None:
    params = PhotonWaveParams(
        ticks=16,
        width=65,
        packet_width=5,
        thin_output_step=2,
        motif_ids=("su_vacuum_omega", "sd_vacuum_omega_dag"),
    )
    a = build_payload(params)
    b = build_payload(params)
    assert a["replay_hash"] == b["replay_hash"]


def test_front_speed_checks_hold_small_run() -> None:
    payload = build_payload(
        PhotonWaveParams(
            ticks=20,
            width=81,
            packet_width=5,
            thin_output_step=1,
            motif_ids=("su_vacuum_omega",),
        )
    )
    lane = payload["lanes"][0]["summary"]
    assert lane["causal_bound_front_speed_le_1"] is True
    assert lane["lightcone_saturated_front_speed_eq_1"] is True
    assert lane["left_front_speed_mean_abs"] >= 0.99
    assert lane["right_front_speed_mean_abs"] >= 0.99


def test_write_artifacts(tmp_path: Path) -> None:
    payload = build_payload(
        PhotonWaveParams(
            ticks=12,
            width=65,
            packet_width=3,
            thin_output_step=3,
            motif_ids=("su_vacuum_omega",),
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
    assert "Photon-Candidate Vacuum Wave (v1)" in md
