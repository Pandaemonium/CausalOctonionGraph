"""Smoke test for build_v3_phase_boundary_kernel_sweep_v1."""

from __future__ import annotations

import json
from pathlib import Path

from cog_v3.calc import build_v3_phase_boundary_kernel_sweep_v1 as sweep
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_phase_boundary_sweep_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_phase_boundary_sweep_v1.md"
OUT_CSV = ROOT / "cog_v3" / "sources" / "v3_phase_boundary_sweep_v1.csv"


def main() -> None:
    payload = sweep.build_payload(
        global_seed=1337,
        seed_count=2,
        ticks=40,
        warmup_ticks=8,
        size_x=11,
        size_y=7,
        size_z=7,
        w3_values=[1.0, 4.0],
        p_mem_values=[0.0, 0.5],
    )
    if payload["convention_id"] != k.CONVENTION_ID:
        raise AssertionError("convention mismatch")
    if len(payload["rows"]) != 4:
        raise AssertionError("unexpected sweep row count")
    sweep.write_artifacts(payload)
    for p in (OUT_JSON, OUT_MD, OUT_CSV):
        if not p.exists():
            raise AssertionError(f"missing artifact: {p}")
    loaded = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    if "replay_hash" not in loaded:
        raise AssertionError("missing replay_hash")
    print("ok: test_v3_phase_boundary_kernel_sweep_v1")


if __name__ == "__main__":
    main()

