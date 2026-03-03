from __future__ import annotations

import json

from cog_v3.calc.build_v3_generation_aligned_equivalence_panel_v1 import (
    OUT_JSON,
    build_payload,
    write_artifacts,
)
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


def test_payload_deterministic_quick() -> None:
    a = build_payload(global_seed=1337, quick=True)
    b = build_payload(global_seed=1337, quick=True)
    assert a["replay_hash"] == b["replay_hash"]


def test_schema_contract_quick() -> None:
    payload = build_payload(global_seed=42, quick=True)
    assert payload["schema_version"] == "v3_generation_aligned_equivalence_panel_v1"
    assert payload["kernel_profile"] == k.KERNEL_PROFILE
    assert payload["convention_id"] == k.CONVENTION_ID
    assert len(payload["systems"]) == 4
    assert len(payload["pair_defs"]) == 2
    assert len(payload["pair_rows"]) >= 1
    assert "median_Delta_max" in payload["pair_summary"][0]


def test_write_artifacts() -> None:
    payload = build_payload(global_seed=77, quick=True)
    write_artifacts(payload)
    assert OUT_JSON.exists()
    loaded = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
