"""RFC-031 probe: algebra-only gravity observables in v5 kernel.

Outputs:
1) cog_v3/sources/v5_associator_holonomy_probe_v1.json
2) cog_v3/sources/v5_associator_holonomy_probe_v1.md
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Dict, List, Tuple

from cog_v3.python import kernel_cog_v5_coherence as kv5


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v3" / "sources" / "v5_associator_holonomy_probe_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v5_associator_holonomy_probe_v1.md"


Coords = Tuple[int, int, int]


def assoc_indicator(a: kv5.State, b: kv5.State, c: kv5.State) -> int:
    return int(((a * b) * c) != (a * (b * c)))


def world_snapshot(
    kernel: kv5.COGKernelV5,
    t: int,
    *,
    default_state: kv5.State,
) -> Tuple[Dict[Coords, kv5.State], int]:
    snap: Dict[Coords, kv5.State] = {}
    incoherent = 0
    for s in kv5.F2_SITES:
        pt = kernel.future_state_detailed(s, t)
        if pt.status == kv5.COHERENT and pt.state is not None:
            snap[s] = pt.state
        else:
            snap[s] = default_state
            if pt.status == kv5.INCOHERENT:
                incoherent += 1
    return snap, incoherent


def associator_field(
    snap: Dict[Coords, kv5.State],
) -> Dict[Coords, float]:
    out: Dict[Coords, float] = {}
    for s in kv5.F2_SITES:
        nbs = kv5.causal_neighbors(s)
        # F2^3 has exactly three neighbors, one canonical triple.
        out[s] = float(assoc_indicator(snap[nbs[0]], snap[nbs[1]], snap[nbs[2]]))
    return out


def shell_profile(
    field: Dict[Coords, float],
    center: Coords,
) -> Dict[int, float]:
    bins: Dict[int, List[float]] = {}
    for s, v in field.items():
        r = kv5.hamming_distance(s, center)
        bins.setdefault(int(r), []).append(float(v))
    return {int(r): float(mean(vals)) for r, vals in sorted(bins.items())}


def holonomy_spread_summary(
    kernel: kv5.COGKernelV5,
    *,
    horizon: int,
    max_paths: int,
) -> Dict[str, float]:
    spreads: List[int] = []
    for t in range(1, int(horizon) + 1):
        for target in kv5.F2_SITES:
            if not kernel.is_reachable(target, t):
                continue
            paths = kv5.all_paths(kernel.origin, target, t, max_paths=max_paths)
            products = [kv5.path_product(p, kernel.cfg, s_rule=kernel.s_rule) for p in paths]
            distinct = len(set(products))
            spreads.append(max(0, int(distinct - 1)))
    if not spreads:
        return {"mean": 0.0, "max": 0.0}
    return {"mean": float(mean(spreads)), "max": float(max(spreads))}


def seed_single_excitation(
    *,
    g: int,
    a: int,
    basis: int,
    sign: int,
    e: int,
    site: Coords,
) -> kv5.SeedConfig:
    cfg = kv5.vacuum_seed()
    cfg[site] = kv5.State(g=g, a=a, basis=basis, sign=sign, e=e)
    return cfg


def run_probe(
    *,
    horizon: int = 6,
    max_paths: int = 50000,
    excite_site: Coords = (1, 1, 1),
) -> Dict[str, object]:
    default_state = kv5.State(g=0, a=0, basis=0, sign=1, e=0)

    seeds = {
        "vacuum": kv5.vacuum_seed(),
        "motif_single_excitation": seed_single_excitation(
            g=1, a=1, basis=7, sign=1, e=1, site=excite_site
        ),
        "reference_nonphysical": kv5.basis_identity_seed(),
    }

    results: Dict[str, object] = {}
    for name, seed in seeds.items():
        kernel = kv5.make_kernel(seed)
        physical, viol = kernel.physical(horizon=int(horizon))

        a_means: List[float] = []
        shells: Dict[int, List[float]] = {}
        incoherent_total = 0

        for t in range(1, int(horizon) + 1):
            snap, incoherent = world_snapshot(kernel, t, default_state=default_state)
            incoherent_total += int(incoherent)
            f = associator_field(snap)
            a_means.append(float(mean(f.values())))
            sh = shell_profile(f, excite_site)
            for r, v in sh.items():
                shells.setdefault(int(r), []).append(float(v))

        shell_mean = {int(r): float(mean(vs)) for r, vs in sorted(shells.items())}
        hsum = holonomy_spread_summary(kernel, horizon=int(horizon), max_paths=int(max_paths))
        results[name] = {
            "physical": bool(physical),
            "first_violation": None
            if viol is None
            else {
                "coords": tuple(viol.coords),
                "t": int(viol.t),
                "status": str(viol.status),
                "n_paths": int(viol.n_paths),
                "n_disagreeing": int(viol.n_disagreeing),
            },
            "A_mean": float(mean(a_means)) if a_means else 0.0,
            "A_by_t": [float(x) for x in a_means],
            "A_shell_mean": shell_mean,
            "incoherent_points_count": int(incoherent_total),
            "H_spread_summary": hsum,
        }

    a_bg = float(results["vacuum"]["A_mean"])  # type: ignore[index]
    a_motif = float(results["motif_single_excitation"]["A_mean"])  # type: ignore[index]
    delta_a = float(a_motif - a_bg)

    shell_bg = results["vacuum"]["A_shell_mean"]  # type: ignore[index]
    shell_motif = results["motif_single_excitation"]["A_shell_mean"]  # type: ignore[index]
    vals_bg = [float(v) for _k, v in sorted(shell_bg.items(), key=lambda x: int(x[0]))]
    vals_m = [float(v) for _k, v in sorted(shell_motif.items(), key=lambda x: int(x[0]))]
    var_bg = float(mean([(x - mean(vals_bg)) ** 2 for x in vals_bg])) if vals_bg else 0.0
    var_m = float(mean([(x - mean(vals_m)) ** 2 for x in vals_m])) if vals_m else 0.0

    h_motif_max = float(results["motif_single_excitation"]["H_spread_summary"]["max"])  # type: ignore[index]
    h_ref_max = float(results["reference_nonphysical"]["H_spread_summary"]["max"])  # type: ignore[index]

    gates = {
        "G1_deltaA_positive": bool(delta_a > 0.0),
        "G2_shell_nonflat_vs_bg": bool(var_m > var_bg),
        "G3_coherent_requires_zero_hspread": bool(
            bool(results["motif_single_excitation"]["physical"]) and h_motif_max == 0.0  # type: ignore[index]
        ),
        "G4_nonphysical_can_have_hspread": bool(
            (not bool(results["reference_nonphysical"]["physical"])) and h_ref_max > 0.0  # type: ignore[index]
        ),
    }

    return {
        "schema_version": "v5_associator_holonomy_probe_v1",
        "kernel_profile": kv5.KERNEL_PROFILE,
        "causal_backend": "F2CubePastProvider",
        "horizon": int(horizon),
        "max_paths": int(max_paths),
        "A_bg_mean": a_bg,
        "A_motif_mean": a_motif,
        "DeltaA_mean": delta_a,
        "A_shell_bg": shell_bg,
        "A_shell_motif": shell_motif,
        "H_spread_bg_summary": results["vacuum"]["H_spread_summary"],  # type: ignore[index]
        "H_spread_motif_summary": results["motif_single_excitation"]["H_spread_summary"],  # type: ignore[index]
        "H_spread_reference_nonphysical_summary": results["reference_nonphysical"]["H_spread_summary"],  # type: ignore[index]
        "gate_results": gates,
        "seed_results": results,
    }


def render_md(payload: Dict[str, object]) -> str:
    g = payload["gate_results"]  # type: ignore[index]
    lines = [
        "# v5 Associator-Holonomy Probe (v1)",
        "",
        f"- kernel_profile: `{payload['kernel_profile']}`",
        f"- causal_backend: `{payload['causal_backend']}`",
        f"- horizon: `{payload['horizon']}`",
        f"- A_bg_mean: `{payload['A_bg_mean']}`",
        f"- A_motif_mean: `{payload['A_motif_mean']}`",
        f"- DeltaA_mean: `{payload['DeltaA_mean']}`",
        "",
        "## Gate Results",
        "",
        f"- G1_deltaA_positive: `{g['G1_deltaA_positive']}`",
        f"- G2_shell_nonflat_vs_bg: `{g['G2_shell_nonflat_vs_bg']}`",
        f"- G3_coherent_requires_zero_hspread: `{g['G3_coherent_requires_zero_hspread']}`",
        f"- G4_nonphysical_can_have_hspread: `{g['G4_nonphysical_can_have_hspread']}`",
        "",
        "## Holonomy Spread Summary",
        "",
        f"- vacuum: `{payload['H_spread_bg_summary']}`",
        f"- motif_single_excitation: `{payload['H_spread_motif_summary']}`",
        f"- reference_nonphysical: `{payload['H_spread_reference_nonphysical_summary']}`",
    ]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description="Run v5 associator-holonomy gravity probe.")
    ap.add_argument("--horizon", type=int, default=6)
    ap.add_argument("--max-paths", type=int, default=50000)
    ns = ap.parse_args()

    payload = run_probe(horizon=int(ns.horizon), max_paths=int(ns.max_paths))
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_md(payload), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
