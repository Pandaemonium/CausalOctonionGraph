"""Smoke test for build_v3_s2880_action_fingerprints_v1."""

from __future__ import annotations

import json
from pathlib import Path

from cog_v3.calc import build_v3_s2880_action_fingerprints_v1 as mod
from cog_v3.calc import build_v3_s2880_invariants_v1 as inv


ROOT = Path(__file__).resolve().parents[2]
OUT_CSV = ROOT / "cog_v3" / "sources" / "v3_s2880_action_fingerprints_v1.csv"
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_s2880_action_fingerprints_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_s2880_action_fingerprints_v1.md"


def main() -> None:
    inv.build_payload()
    payload = mod.build_payload()
    if payload["schema_version"] != "v3_s2880_action_fingerprints_v1":
        raise AssertionError("schema mismatch")
    if int(payload["summary"]["element_count"]) != 2880:
        raise AssertionError("expected 2880 fingerprint rows")
    if int(payload["summary"]["probe_count"]) <= 0:
        raise AssertionError("probe_count must be positive")
    for p in (OUT_CSV, OUT_JSON, OUT_MD):
        if not p.exists():
            raise AssertionError(f"missing artifact: {p}")
    loaded = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    if "replay_hash" not in loaded:
        raise AssertionError("missing replay_hash")
    if not loaded["checks"]["row_count_ok"]:
        raise AssertionError("row_count check failed")
    print("ok: test_v3_s2880_action_fingerprints_v1")


if __name__ == "__main__":
    main()

