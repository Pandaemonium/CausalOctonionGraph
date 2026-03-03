"""Smoke test for build_v3_associator_field_probe_v1."""

from __future__ import annotations

import json
from pathlib import Path

from cog_v3.calc import build_v3_associator_field_probe_v1 as probe
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_associator_field_probe_v1.json"
OUT_RADIAL_CSV = ROOT / "cog_v3" / "sources" / "v3_associator_radial_profiles_v1.csv"
OUT_FAMILY_CSV = ROOT / "cog_v3" / "sources" / "v3_associator_family_activity_v1.csv"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_associator_field_probe_v1.md"


def main() -> None:
    payload = probe.build_payload(
        ticks=20,
        warmup_ticks=6,
        size_x=11,
        size_y=7,
        size_z=7,
        stencil_id="cube26",
        boundary_mode="fixed_vacuum",
    )
    req = [
        "kernel_profile",
        "convention_id",
        "stencil_id",
        "seed_id",
        "A_bg",
        "A_shell_profile",
        "A_var_profile",
        "fit_scores",
        "family_activity_summary",
        "gate_results",
    ]
    for key in req:
        if key not in payload:
            raise AssertionError(f"missing key: {key}")

    if payload["kernel_profile"] != k.KERNEL_PROFILE:
        raise AssertionError("kernel_profile mismatch")
    if payload["convention_id"] != k.CONVENTION_ID:
        raise AssertionError("convention_id mismatch")

    for p in (OUT_JSON, OUT_RADIAL_CSV, OUT_FAMILY_CSV, OUT_MD):
        if not p.exists():
            raise AssertionError(f"missing artifact: {p}")

    loaded = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    if "replay_hash" not in loaded:
        raise AssertionError("missing replay_hash")

    print("ok: test_v3_associator_field_probe_v1")


if __name__ == "__main__":
    main()

