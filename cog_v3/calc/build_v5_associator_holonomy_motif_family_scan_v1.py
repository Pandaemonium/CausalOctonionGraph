"""Targeted motif-family scan for v5 associator/holonomy observables.

Artifacts:
1) cog_v3/sources/v5_associator_holonomy_motif_family_scan_v1.json
2) cog_v3/sources/v5_associator_holonomy_motif_family_scan_v1.md
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Dict, List, Tuple

from cog_v3.python import kernel_cog_v5_coherence as kv5


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v3" / "sources" / "v5_associator_holonomy_motif_family_scan_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v5_associator_holonomy_motif_family_scan_v1.md"


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
        out[s] = float(assoc_indicator(snap[nbs[0]], snap[nbs[1]], snap[nbs[2]]))
    return out


def shell_profile(field: Dict[Coords, float], center: Coords) -> Dict[int, float]:
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
            spreads.append(max(0, len(set(products)) - 1))
    if not spreads:
        return {"mean": 0.0, "max": 0.0}
    return {"mean": float(mean(spreads)), "max": float(max(spreads))}


def seed_from_sites(sites: Dict[Coords, kv5.State], vacuum: kv5.State) -> kv5.SeedConfig:
    cfg = {s: vacuum for s in kv5.F2_SITES}
    for s, st in sites.items():
        cfg[s] = st
    return cfg


def motif_bank() -> Dict[str, kv5.SeedConfig]:
    vac = kv5.State(g=0, a=0, basis=0, sign=1, e=0)
    ex = kv5.State(g=1, a=1, basis=7, sign=1, e=1)
    ex2 = kv5.State(g=2, a=3, basis=6, sign=-1, e=1)

    # neighbors of (1,1,1): (0,1,1), (1,0,1), (1,1,0)
    return {
        "vacuum": kv5.vacuum_seed(),
        "uniform_nonvac_e7": {s: kv5.State(g=1, a=1, basis=7, sign=1, e=0) for s in kv5.F2_SITES},
        "single_corner_e7": seed_from_sites({(1, 1, 1): ex}, vac),
        "opposite_pair": seed_from_sites({(1, 1, 1): ex, (0, 0, 0): ex}, vac),
        "edge_pair_mixed": seed_from_sites({(1, 1, 1): ex, (0, 1, 1): ex2}, vac),
        "tripod_plus_core": seed_from_sites(
            {
                (1, 1, 1): ex,
                (0, 1, 1): ex,
                (1, 0, 1): ex,
                (1, 1, 0): ex,
            },
            vac,
        ),
        "checkerboard_parity": {
            s: (kv5.State(g=0, a=0, basis=0, sign=1, e=0) if (sum(s) % 2 == 0) else kv5.State(g=1, a=1, basis=7, sign=1, e=0))
            for s in kv5.F2_SITES
        },
        "basis_identity_reference": kv5.basis_identity_seed(),
    }


def analyze_seed(
    name: str,
    seed: kv5.SeedConfig,
    *,
    horizon: int,
    max_paths: int,
    center: Coords = (1, 1, 1),
) -> Dict[str, object]:
    default_state = kv5.State(g=0, a=0, basis=0, sign=1, e=0)
    kernel = kv5.make_kernel(seed)
    physical, viol = kernel.physical(horizon=int(horizon))

    a_t: List[float] = []
    shells: Dict[int, List[float]] = {}
    incoherent_total = 0

    for t in range(1, int(horizon) + 1):
        snap, inc = world_snapshot(kernel, t, default_state=default_state)
        incoherent_total += int(inc)
        field = associator_field(snap)
        a_t.append(float(mean(field.values())))
        sh = shell_profile(field, center)
        for r, v in sh.items():
            shells.setdefault(int(r), []).append(float(v))

    shell_mean = {int(r): float(mean(vs)) for r, vs in sorted(shells.items())}
    vals = [float(v) for _r, v in sorted(shell_mean.items(), key=lambda x: int(x[0]))]
    shell_var = float(mean([(x - mean(vals)) ** 2 for x in vals])) if vals else 0.0
    hsum = holonomy_spread_summary(kernel, horizon=int(horizon), max_paths=int(max_paths))

    return {
        "seed_id": name,
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
        "A_mean": float(mean(a_t)) if a_t else 0.0,
        "A_by_t": [float(x) for x in a_t],
        "A_shell_mean": shell_mean,
        "A_shell_var": shell_var,
        "incoherent_points_count": int(incoherent_total),
        "H_spread_summary": hsum,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Run v5 targeted motif family associator/holonomy scan.")
    ap.add_argument("--horizon", type=int, default=6)
    ap.add_argument("--max-paths", type=int, default=50000)
    ns = ap.parse_args()

    bank = motif_bank()
    rows = [analyze_seed(name, seed, horizon=int(ns.horizon), max_paths=int(ns.max_paths)) for name, seed in bank.items()]
    by_id = {r["seed_id"]: r for r in rows}
    a_bg = float(by_id["vacuum"]["A_mean"])

    promoted = []
    for r in rows:
        delta_a = float(r["A_mean"]) - a_bg
        hmax = float(r["H_spread_summary"]["max"])
        if bool(r["physical"]) and hmax == 0.0 and float(r["A_shell_var"]) > 0.0:
            promoted.append({**r, "DeltaA": delta_a})

    payload = {
        "schema_version": "v5_associator_holonomy_motif_family_scan_v1",
        "kernel_profile": kv5.KERNEL_PROFILE,
        "causal_backend": "F2CubePastProvider",
        "horizon": int(ns.horizon),
        "max_paths": int(ns.max_paths),
        "A_bg_mean": a_bg,
        "rows": rows,
        "promoted_candidates": promoted,
        "promotion_rule": "physical && H_spread.max == 0 && A_shell_var > 0",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md: List[str] = [
        "# v5 Associator-Holonomy Motif Family Scan (v1)",
        "",
        f"- kernel_profile: `{payload['kernel_profile']}`",
        f"- causal_backend: `{payload['causal_backend']}`",
        f"- horizon: `{payload['horizon']}`",
        f"- A_bg_mean (vacuum): `{payload['A_bg_mean']}`",
        f"- promotion_rule: `{payload['promotion_rule']}`",
        f"- promoted_candidates: `{len(promoted)}`",
        "",
        "## Rows",
        "",
        "| seed_id | physical | A_mean | A_shell_var | H_spread.max | incoherent_points |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for r in rows:
        md.append(
            f"| {r['seed_id']} | {r['physical']} | {float(r['A_mean']):.6f} | "
            f"{float(r['A_shell_var']):.6f} | {float(r['H_spread_summary']['max']):.3f} | "
            f"{int(r['incoherent_points_count'])} |"
        )

    if promoted:
        md.append("")
        md.append("## Promoted candidates")
        md.append("")
        for r in promoted:
            md.append(f"- `{r['seed_id']}` (DeltaA={float(r['DeltaA']):.6f})")
    else:
        md.append("")
        md.append("No promoted candidates in this motif bank under current rule.")

    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
