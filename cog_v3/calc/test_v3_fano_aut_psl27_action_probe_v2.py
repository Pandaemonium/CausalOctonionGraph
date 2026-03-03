"""Smoke test for build_v3_fano_aut_psl27_action_probe_v2."""

from __future__ import annotations

import json
from pathlib import Path

from cog_v3.calc import build_v3_fano_aut_psl27_action_probe_v2 as probe
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_fano_aut_psl27_action_probe_v2.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_fano_aut_psl27_action_probe_v2.md"
OUT_CSV = ROOT / "cog_v3" / "sources" / "v3_fano_aut_psl27_orbits_v2.csv"


def main() -> None:
    payload = probe.build_payload()
    if payload["convention_id"] != k.CONVENTION_ID:
        raise AssertionError("convention mismatch")
    if int(payload["meta"]["automorphism_count_unoriented"]) != 168:
        raise AssertionError("expected 168 signfree automorphisms")
    if int(payload["meta"]["automorphism_count_oriented"]) != 21:
        raise AssertionError("expected 21 oriented automorphisms")
    if len(payload["variants"]) < 2:
        raise AssertionError("missing variants")
    for p in (OUT_JSON, OUT_MD, OUT_CSV):
        if not p.exists():
            raise AssertionError(f"missing artifact: {p}")
    loaded = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    if "replay_hash" not in loaded:
        raise AssertionError("missing replay_hash")
    print("ok: test_v3_fano_aut_psl27_action_probe_v2")


if __name__ == "__main__":
    main()

