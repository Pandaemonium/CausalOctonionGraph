"""Smoke test for build_v3_fixed_manifest_kernel_gate_stack_seed_sweep_v1."""

from __future__ import annotations

import json
from pathlib import Path

from cog_v3.calc import build_v3_fixed_manifest_kernel_gate_stack_seed_sweep_v1 as sweep
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_fixed_manifest_kernel_gate_stack_seed_sweep_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_fixed_manifest_kernel_gate_stack_seed_sweep_v1.md"
OUT_CSV = ROOT / "cog_v3" / "sources" / "v3_fixed_manifest_kernel_gate_stack_seed_sweep_v1.csv"


def main() -> None:
    payload = sweep.build_payload(backend="numba_cpu", seed_count=2, global_seed=1337, quick=True)
    if payload["convention_id"] != k.CONVENTION_ID:
        raise AssertionError("convention_id mismatch")
    if int(payload["seed_count"]) != 2:
        raise AssertionError("seed count mismatch")
    if "candidate_summary" not in payload:
        raise AssertionError("missing candidate_summary")
    for p in (OUT_JSON, OUT_MD, OUT_CSV):
        if not p.exists():
            raise AssertionError(f"missing artifact: {p}")
    loaded = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    if "replay_hash" not in loaded:
        raise AssertionError("missing replay_hash")
    print("ok: test_v3_fixed_manifest_kernel_gate_stack_seed_sweep_v1")


if __name__ == "__main__":
    main()

