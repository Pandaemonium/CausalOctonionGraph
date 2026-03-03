"""Smoke test for build_v3_order6_psl27_action_probe_v1."""

from __future__ import annotations

import json
from pathlib import Path

from cog_v3.calc import build_v3_order6_psl27_action_probe_v1 as probe
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_order6_psl27_action_probe_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_order6_psl27_action_probe_v1.md"
OUT_ORBITS = ROOT / "cog_v3" / "sources" / "v3_order6_psl27_orbits_v1.csv"


def main() -> None:
    payload = probe.build_payload(random_trials=4, random_seed=1337)
    req = [
        "convention_id",
        "order6_set_size",
        "candidate_action_size",
        "closure_ok",
        "faithful_ok",
        "orbit_partition",
        "stabilizer_histogram",
        "random_control_comparison",
    ]
    for key in req:
        if key not in payload:
            raise AssertionError(f"missing key: {key}")
    if payload["convention_id"] != k.CONVENTION_ID:
        raise AssertionError("convention_id mismatch")
    if int(payload["order6_set_size"]) != 168:
        raise AssertionError("expected S960 order-6 size 168")
    for p in (OUT_JSON, OUT_MD, OUT_ORBITS):
        if not p.exists():
            raise AssertionError(f"missing artifact: {p}")
    loaded = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    if "replay_hash" not in loaded:
        raise AssertionError("missing replay_hash")
    print("ok: test_v3_order6_psl27_action_probe_v1")


if __name__ == "__main__":
    main()

