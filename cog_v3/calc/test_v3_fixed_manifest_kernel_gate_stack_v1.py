from __future__ import annotations

import json

from cog_v3.calc.build_v3_fixed_manifest_kernel_gate_stack_v1 import (
    OUT_JSON,
    build_payload,
    write_artifacts,
)
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


def test_payload_quick_contract() -> None:
    payload = build_payload(backend="numba_cpu", global_seed=1337, quick=True)
    assert payload["schema_version"] == "v3_fixed_manifest_kernel_gate_stack_v1"
    assert payload["kernel_profile"] == k.KERNEL_PROFILE
    assert payload["convention_id"] == k.CONVENTION_ID
    assert len(payload["rows"]) == 3
    for r in payload["rows"]:
        assert "gate_results" in r
        assert "lorentz_metrics" in r
        assert "clock_metrics" in r


def test_payload_deterministic_quick() -> None:
    a = build_payload(backend="numba_cpu", global_seed=2026, quick=True)
    b = build_payload(backend="numba_cpu", global_seed=2026, quick=True)
    assert a["replay_hash"] == b["replay_hash"]


def test_write_artifacts() -> None:
    payload = build_payload(backend="numba_cpu", global_seed=77, quick=True)
    write_artifacts(payload)
    assert OUT_JSON.exists()
    loaded = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert loaded["replay_hash"] == payload["replay_hash"]
