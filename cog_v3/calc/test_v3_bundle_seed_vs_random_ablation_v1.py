"""Smoke test for build_v3_bundle_seed_vs_random_ablation_v1."""

from __future__ import annotations

import json
from pathlib import Path

from cog_v3.calc import build_v3_bundle_seed_vs_random_ablation_v1 as ab
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_bundle_seed_vs_random_ablation_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_bundle_seed_vs_random_ablation_v1.md"


def main() -> None:
    payload = ab.build_payload(
        ab.AblationParams(
            seed_budget=40,
            ticks=36,
            warmup_ticks=8,
            size_x=15,
            size_y=7,
            size_z=7,
            global_seed=1337,
        )
    )
    req = [
        "strategy_summary",
        "effect_size_vs_control",
        "gate_results",
        "panel_id",
        "convention_id",
    ]
    for key in req:
        if key not in payload:
            raise AssertionError(f"missing key: {key}")
    if payload["convention_id"] != k.CONVENTION_ID:
        raise AssertionError("convention mismatch")
    if len(payload["strategy_summary"]) < 4:
        raise AssertionError("expected 4 strategies")
    for p in (OUT_JSON, OUT_MD):
        if not p.exists():
            raise AssertionError(f"missing artifact: {p}")
    loaded = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    if "replay_hash" not in loaded:
        raise AssertionError("missing replay_hash")
    print("ok: test_v3_bundle_seed_vs_random_ablation_v1")


if __name__ == "__main__":
    main()

