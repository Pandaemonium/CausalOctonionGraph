"""Probe a neutrino-style seeded volume in the S2880 pair-conservative kernel.

Configurable seed components:
  g (Z3 domain)          = user-provided
  q (oct spin mixor)     = [1,0,0,0,0,0,0,0]  ( +e000 )
  E (Z energy)           = user-provided (metadata only in this kernel lane)
  a (Z4 energy phase)    = user-provided

Scope note:
- Active S2880 pair-conservative kernel evolves sid = (phase_idx in Z12, q_id in Q240).
- Integer Z-energy E is not yet evolved dynamically in this lane.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

from cog_v3.calc import build_v3_c12_singlet_doublet_clock_shift_sparse_v1 as c12
from cog_v3.python import kernel_octavian240_multiplicative_v1 as k
from cog_v3.python import kernel_s2880_pair_conservative_v1 as kpair


ROOT = Path(__file__).resolve().parents[2]

SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_enu_volume_probe_v1.py"
PAIR_KERNEL_REPO_PATH = "cog_v3/python/kernel_s2880_pair_conservative_v1.py"
OCT_KERNEL_REPO_PATH = "cog_v3/python/kernel_octavian240_multiplicative_v1.py"

OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_enu_volume_probe_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_enu_volume_probe_v1.md"

PHASE_COUNT = 12


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _idx(x: int, y: int, z: int, ny: int, nz: int) -> int:
    return (x * ny + y) * nz + z


def _xyz(i: np.ndarray, ny: int, nz: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    x = i // (ny * nz)
    rem = i % (ny * nz)
    y = rem // nz
    z = rem % nz
    return x.astype(np.float64), y.astype(np.float64), z.astype(np.float64)


def _sid_from_components(*, g: int, a: int, q_coeffs: List[int], qn: int) -> Tuple[int, int, int]:
    # C12 decomposition in this lane: phase_idx = 4*g + 3*a (mod 12)
    phase_idx = int(kpair.phase_idx_from_domain_energy_phase(int(g), int(a), phase_count=PHASE_COUNT))
    q_tuple = tuple(k.Fraction(int(c), 1) for c in q_coeffs)
    q_id = int(k.ALPHABET_INDEX[q_tuple])  # type: ignore[index]
    sid = int(phase_idx * int(qn) + int(q_id))
    return sid, phase_idx, q_id


def _seed_sphere(
    world: np.ndarray,
    *,
    sid_seed: int,
    nx: int,
    ny: int,
    nz: int,
    radius: int,
) -> int:
    cx, cy, cz = nx // 2, ny // 2, nz // 2
    r2 = int(radius) * int(radius)
    n = 0
    for x in range(nx):
        dx2 = (x - cx) * (x - cx)
        for y in range(ny):
            dy2 = (y - cy) * (y - cy)
            for z in range(nz):
                dz2 = (z - cz) * (z - cz)
                if dx2 + dy2 + dz2 <= r2:
                    world[_idx(x, y, z, ny, nz)] = np.uint16(int(sid_seed))
                    n += 1
    return int(n)


def _metrics(world: np.ndarray, vac_sid: int, ny: int, nz: int) -> Dict[str, float]:
    active = np.where(world.astype(np.int32) != int(vac_sid))[0].astype(np.int64)
    if active.size == 0:
        return {"active_count": 0.0, "com_x": float("nan"), "com_y": float("nan"), "com_z": float("nan")}
    x, y, z = _xyz(active, int(ny), int(nz))
    return {
        "active_count": float(active.size),
        "com_x": float(np.mean(x)),
        "com_y": float(np.mean(y)),
        "com_z": float(np.mean(z)),
    }


def _run_one_case(
    *,
    ticks: int,
    nx: int,
    ny: int,
    nz: int,
    radius: int,
    g: int,
    a: int,
    e: int,
    qmul: np.ndarray,
    pair_rounds: kpair.PairRounds,
) -> Dict[str, Any]:
    qn = int(qmul.shape[0])
    vac_sid = int(c12.s_identity_id())
    q_coeffs = [1, 0, 0, 0, 0, 0, 0, 0]
    sid_seed, phase_idx, q_id = _sid_from_components(g=int(g), a=int(a), q_coeffs=q_coeffs, qn=qn)

    world = np.full((int(nx * ny * nz),), np.uint16(vac_sid), dtype=np.uint16)
    seeded_cells = _seed_sphere(world, sid_seed=sid_seed, nx=nx, ny=ny, nz=nz, radius=radius)

    series: List[Dict[str, float]] = []
    series.append({"tick": 0.0, **_metrics(world, vac_sid, ny, nz)})

    for t in range(1, int(ticks) + 1):
        world = kpair.step_pair_conservative(
            world,
            pair_rounds,
            qmul=qmul,
            phase_count=PHASE_COUNT,
            global_seed=20260303,
            tick=int(t),
            shuffle_round_order=False,
            use_all_rounds_per_tick=False,
        )
        series.append({"tick": float(t), **_metrics(world, vac_sid, ny, nz)})

    x0, y0, z0 = float(series[0]["com_x"]), float(series[0]["com_y"]), float(series[0]["com_z"])
    finite_rows = [r for r in series if math.isfinite(float(r["com_x"]))]
    displacements = [
        math.sqrt(
            (float(r["com_x"]) - x0) ** 2 + (float(r["com_y"]) - y0) ** 2 + (float(r["com_z"]) - z0) ** 2
        )
        for r in finite_rows
    ]

    return {
        "seed_request": {
            "g_domain_z3": int(g),
            "q_oct_spin_coeffs": q_coeffs,
            "E_z_energy_recorded": int(e),
            "a_z4_energy_phase": int(a),
        },
        "resolved_seed": {
            "phase_idx_z12": int(phase_idx),
            "q_id_q240": int(q_id),
            "q_label": str(k.elem_label(int(q_id))),
            "sid_s2880": int(sid_seed),
            "sid_label": f"zeta12^{phase_idx}*({k.elem_label(int(q_id))})" if phase_idx != 0 else k.elem_label(int(q_id)),
        },
        "seeded_cells": int(seeded_cells),
        "series": series,
        "summary": {
            "initial_active_count": float(series[0]["active_count"]),
            "final_active_count": float(series[-1]["active_count"]),
            "max_com_displacement": float(max(displacements) if displacements else 0.0),
            "final_com_displacement": float(displacements[-1] if displacements else 0.0),
        },
    }


def build_payload(
    *,
    ticks: int,
    nx: int,
    ny: int,
    nz: int,
    radius: int,
    g: int,
    a: int,
    e: int,
    sweep_c4: bool,
) -> Dict[str, Any]:
    qmul = c12.build_qmul_table()
    pair_rounds = kpair.build_pair_rounds(nx, ny, nz, stencil_id="cube26", boundary_mode="fixed_vacuum")

    a_values = list(range(4)) if bool(sweep_c4) else [int(a)]
    cases = [
        _run_one_case(
            ticks=int(ticks),
            nx=int(nx),
            ny=int(ny),
            nz=int(nz),
            radius=int(radius),
            g=int(g),
            a=int(aa),
            e=int(e),
            qmul=qmul,
            pair_rounds=pair_rounds,
        )
        for aa in a_values
    ]

    payload: Dict[str, Any] = {
        "schema_version": "v3_enu_volume_probe_v1",
        "kernel_profile": str(kpair.KERNEL_PROFILE),
        "convention_id": str(k.CONVENTION_ID),
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(ROOT / SCRIPT_REPO_PATH),
        "pair_kernel_module": PAIR_KERNEL_REPO_PATH,
        "pair_kernel_module_sha256": _sha_file(ROOT / PAIR_KERNEL_REPO_PATH),
        "oct_module": OCT_KERNEL_REPO_PATH,
        "oct_module_sha256": _sha_file(ROOT / OCT_KERNEL_REPO_PATH),
        "grid": [int(nx), int(ny), int(nz)],
        "ticks": int(ticks),
        "radius": int(radius),
        "requested_g": int(g),
        "requested_a": int(a),
        "requested_E": int(e),
        "sweep_c4": bool(sweep_c4),
        "notes": [
            "This run uses S2880 pair-conservative kernel (sid = phase_idx x q_id).",
            "Integer Z energy E is not yet a dynamical state lane here; E is metadata only.",
            "Movement is measured by center-of-mass drift of non-vacuum support.",
        ],
        "cases": cases,
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# v3 e-neutrino Volume Probe (v1)",
        "",
        f"- kernel_profile: `{payload['kernel_profile']}`",
        f"- convention_id: `{payload['convention_id']}`",
        f"- grid: `{payload['grid']}`",
        f"- ticks: `{payload['ticks']}`",
        f"- radius: `{payload['radius']}`",
        f"- sweep_c4: `{payload['sweep_c4']}`",
        "",
        "## Requested Seed Components",
        "",
        f"- g (Z3): `{payload['requested_g']}`",
        "- q coeffs: `[1, 0, 0, 0, 0, 0, 0, 0]`",
        f"- E (Z): `{payload['requested_E']}` (recorded; non-dynamical in this lane)",
        f"- a (Z4): `{payload['requested_a']}`",
        "",
        "## Case Summary",
        "",
        "| a (Z4) | phase_idx (Z12) | sid | sid_label | max_com_displacement | final_com_displacement | final_active_count |",
        "|---:|---:|---:|---|---:|---:|---:|",
    ]
    for c in payload["cases"]:
        req = c["seed_request"]
        rs = c["resolved_seed"]
        s = c["summary"]
        lines.append(
            f"| {int(req['a_z4_energy_phase'])} | {int(rs['phase_idx_z12'])} | {int(rs['sid_s2880'])} | "
            f"`{rs['sid_label']}` | {float(s['max_com_displacement']):.6f} | "
            f"{float(s['final_com_displacement']):.6f} | {float(s['final_active_count']):.1f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Nonzero COM displacement means net propagation/drift of the seeded volume.",
            "- If displacement is ~0 at final tick, the seeded volume is approximately stationary overall.",
            "- To test true E-driven kinetics, E must be upgraded to a dynamical kernel field.",
        ]
    )
    return "\n".join(lines)


def write_artifacts(payload: Dict[str, Any]) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    OUT_MD.write_text(_render_md(payload), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Run neutrino-style seeded volume drift probe.")
    ap.add_argument("--ticks", type=int, default=64)
    ap.add_argument("--size-x", type=int, default=25)
    ap.add_argument("--size-y", type=int, default=25)
    ap.add_argument("--size-z", type=int, default=25)
    ap.add_argument("--radius", type=int, default=5)
    ap.add_argument("--g", type=int, default=0, help="Z3 domain index in {0,1,2}")
    ap.add_argument("--a", type=int, default=1, help="Z4 phase index in {0,1,2,3}")
    ap.add_argument("--energy-z", type=int, default=4, help="Recorded Z energy metadata for seed")
    ap.add_argument("--sweep-c4", action="store_true", help="Run a in {0,1,2,3} at fixed g")
    args = ap.parse_args()

    payload = build_payload(
        ticks=int(args.ticks),
        nx=int(args.size_x),
        ny=int(args.size_y),
        nz=int(args.size_z),
        radius=int(args.radius),
        g=int(args.g) % 3,
        a=int(args.a) % 4,
        e=int(args.energy_z),
        sweep_c4=bool(args.sweep_c4),
    )
    write_artifacts(payload)
    print("v3_enu_volume_probe_v1: wrote JSON+MD")


if __name__ == "__main__":
    main()
