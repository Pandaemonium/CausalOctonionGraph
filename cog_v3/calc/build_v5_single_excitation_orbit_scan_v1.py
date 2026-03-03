"""Scan coherent loops for single-excitation seeds in v5 kernel."""

from __future__ import annotations

import json
from pathlib import Path

from cog_v3.python import orbit_loops_v5 as ol


OUT_JSON = Path("cog_v3/sources/v5_single_excitation_orbit_scan_v1.json")
OUT_MD = Path("cog_v3/sources/v5_single_excitation_orbit_scan_v1.md")


def main() -> None:
    results = ol.scan_single_excitation_loops(
        g_values=[0, 1, 2],
        a_values=[0, 1, 2, 3],
        basis_values=list(range(8)),
        sign_values=[-1, 1],
        e_values=[0, 1, 2, 4],
        excite_site=(1, 1, 1),
        target=(1, 1, 1),
        horizon=9,
    )

    rows = [
        {
            "seed_g": r.seed_g,
            "seed_a": r.seed_a,
            "seed_basis": r.seed_basis,
            "seed_sign": r.seed_sign,
            "seed_e": r.seed_e,
            "physical": r.physical,
            "period": r.period,
            "first_repeat_at": r.first_repeat_at,
            "coherent_samples": r.coherent_samples,
            "incoherent_samples": r.incoherent_samples,
            "excite_site": r.excite_site,
            "target": r.target,
            "horizon": r.horizon,
        }
        for r in results
    ]

    coherent_periodic = [r for r in rows if r["physical"] and r["period"] is not None]
    coherent_periodic.sort(key=lambda x: (x["period"], x["seed_e"], x["seed_basis"], x["seed_g"], x["seed_a"]))

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "profile": "cog_v5_coherent_lightcone_fold_v1",
        "n_total": len(rows),
        "n_coherent_periodic": len(coherent_periodic),
        "top_coherent_periodic": coherent_periodic[:40],
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md = [
        "# v5 Single-Excitation Orbit Scan (v1)",
        "",
        "- profile: `cog_v5_coherent_lightcone_fold_v1`",
        "- sweep: `g in {0,1,2}, a in {0,1,2,3}, basis in 0..7, sign in {-1,+1}, E in {0,1,2,4}`",
        "- horizon: `9` (exact-path regime under current path cap)",
        f"- total seeds: `{len(rows)}`",
        f"- coherent+periodic: `{len(coherent_periodic)}`",
        "",
        "## Top coherent periodic seeds",
    ]
    if coherent_periodic:
        md.append("")
        md.append("| g | a | basis | sign | E | period | first_repeat_at | coherent_samples |")
        md.append("|---|---|-------|------|---|--------|-----------------|------------------|")
        for r in coherent_periodic[:20]:
            md.append(
                f"| {r['seed_g']} | {r['seed_a']} | {r['seed_basis']} | {r['seed_sign']} | "
                f"{r['seed_e']} | {r['period']} | {r['first_repeat_at']} | {r['coherent_samples']} |"
            )
    else:
        md.append("")
        md.append("No coherent periodic seeds found in this sweep.")

    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
