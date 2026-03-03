"""Smoke run for canonical v5 coherent-lightcone engine."""

from __future__ import annotations

import json
from pathlib import Path

from cog_v3.python import engine_canonical_v5 as eng


OUT_JSON = Path("cog_v3/sources/v5_canonical_engine_smoke_v1.json")
OUT_MD = Path("cog_v3/sources/v5_canonical_engine_smoke_v1.md")


def main() -> None:
    seed = eng.SiteSeed(domain=1, oct_basis=7, energy_n=1, energy_phase=1, sign=1)
    cfg = eng.uniform_seed(seed)
    payload = eng.lightcone_trace(seed_cfg=cfg, horizon=2)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md = [
        "# v5 Canonical Engine Smoke (v1)",
        "",
        f"- engine_profile: `{payload['engine_profile']}`",
        f"- physical: `{payload['physical']}`",
        f"- horizon: `2`",
        f"- violation: `{payload['violation']}`",
        "",
        "Canonical lane:",
        "- coherent lightcone semantics",
        "- deterministic path-product fold",
        "- no Markov state-machine update",
    ]
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
