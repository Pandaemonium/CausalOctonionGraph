"""Smoke test for build_v3_koide_c12_verification_v1."""

from __future__ import annotations

import json
from pathlib import Path

from cog_v3.calc import build_v3_koide_c12_verification_v1 as koide
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_koide_c12_verification_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_koide_c12_verification_v1.md"
OUT_CSV = ROOT / "cog_v3" / "sources" / "v3_koide_c12_verification_v1.csv"


def main() -> None:
    payload = koide.build_payload(delta_step_deg=30.0)
    if payload["convention_id"] != k.CONVENTION_ID:
        raise AssertionError("convention mismatch")
    err = float(payload["equilateral_orbit"]["max_abs_error_signed_vs_2over3"])
    if err > 1e-9:
        raise AssertionError(f"Koide identity error too large: {err}")
    for p in (OUT_JSON, OUT_MD, OUT_CSV):
        if not p.exists():
            raise AssertionError(f"missing artifact: {p}")
    loaded = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    if "replay_hash" not in loaded:
        raise AssertionError("missing replay_hash")
    print("ok: test_v3_koide_c12_verification_v1")


if __name__ == "__main__":
    main()
