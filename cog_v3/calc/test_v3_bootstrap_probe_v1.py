from __future__ import annotations

import json
from pathlib import Path

from cog_v3.calc.build_v3_bootstrap_probe_v1 import (
    OUT_JSON,
    OUT_MD,
    build_payload,
    write_artifacts,
)
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


def test_payload_deterministic() -> None:
    a = build_payload(ticks=36, thin_output_step=3)
    b = build_payload(ticks=36, thin_output_step=3)
    assert a["replay_hash"] == b["replay_hash"]


def test_v3_core_checks() -> None:
    payload = build_payload(ticks=16, thin_output_step=2)
    assert payload["checks"]["alphabet_size_240"] is True
    assert payload["checks"]["alphabet_norm_one_all"] is True
    assert payload["checks"]["closure_pair_scan_ok"] is True
    assert payload["checks"]["target_triplets_all_positive"] is True
    assert payload["triplet_checks"]["inconsistent_requested_triplet"]["satisfiable"] is False
    assert payload["convention_id"] == k.CONVENTION_ID
    assert payload["kernel_profile"] == k.KERNEL_PROFILE


def test_convention_id_guard() -> None:
    world = k.World(
        node_ids=["n0"],
        parents={"n0": []},
        states={"n0": int(k.IDENTITY_ID)},
        convention_id="wrong_convention",
        tick=0,
    )
    try:
        _ = k.step(world)
        assert False, "Expected convention mismatch error"
    except ValueError as exc:
        assert "Convention mismatch" in str(exc)


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
    assert "COG v3 Bootstrap Probe (v1)" in md
