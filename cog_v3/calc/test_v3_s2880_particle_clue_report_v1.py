"""Smoke test for build_v3_s2880_particle_clue_report_v1."""

from __future__ import annotations

import json
from pathlib import Path

from cog_v3.calc import build_v3_s2880_action_fingerprints_v1 as fp
from cog_v3.calc import build_v3_s2880_invariants_v1 as inv
from cog_v3.calc import build_v3_s2880_particle_clue_report_v1 as mod
from cog_v3.calc import build_v3_s2880_particle_interaction_catalog_v1 as cat
from cog_v3.calc import build_v3_s2880_structural_classes_v1 as cls


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_s2880_particle_clue_report_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_s2880_particle_clue_report_v1.md"
OUT_PRIOR_CSV = ROOT / "cog_v3" / "sources" / "v3_s2880_seed_priors_v1.csv"


def main() -> None:
    inv.build_payload()
    fp.build_payload()
    cls.build_payload()
    cat.build_payload()
    payload = mod.build_payload()
    if payload["schema_version"] != "v3_s2880_particle_clue_report_v1":
        raise AssertionError("schema mismatch")
    if int(payload["summary"]["element_count"]) != 2880:
        raise AssertionError("expected 2880 elements")
    if int(payload["summary"]["seed_prior_rows"]) <= 0:
        raise AssertionError("seed priors should be nonempty")
    for p in (OUT_JSON, OUT_MD, OUT_PRIOR_CSV):
        if not p.exists():
            raise AssertionError(f"missing artifact: {p}")
    loaded = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    if "replay_hash" not in loaded:
        raise AssertionError("missing replay_hash")
    if not loaded["checks"]["element_count_ok"]:
        raise AssertionError("element_count check failed")
    print("ok: test_v3_s2880_particle_clue_report_v1")


if __name__ == "__main__":
    main()

