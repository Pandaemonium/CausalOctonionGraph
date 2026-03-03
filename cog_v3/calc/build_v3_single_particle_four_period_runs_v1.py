"""Simulate one particle 4 times, each run for at least 4 periods.

Default particle:
  domain=1, octavian_id=239 (+e000), energy_n=4, energy_phase=1

Kernel:
  cog_v3_s2880_pair_conservative_v1
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from cog_v3.calc import build_v3_c12_singlet_doublet_clock_shift_sparse_v1 as c12
from cog_v3.python import kernel_s2880_pair_conservative_v1 as kp


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_single_particle_four_period_runs_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_s2880_pair_conservative_v1.py"
OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_single_particle_four_period_runs_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_single_particle_four_period_runs_v1.md"


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _center_idx(nx: int, ny: int, nz: int) -> int:
    cx, cy, cz = nx // 2, ny // 2, nz // 2
    return (cx * ny + cy) * nz + cz


def _find_period(
    *,
    world0: np.ndarray,
    pair_rounds: kp.PairRounds,
    qmul: np.ndarray,
    period_search_max: int,
    full_round_sweep: bool,
) -> int | None:
    w = world0.copy()
    for t in range(1, int(period_search_max) + 1):
        w = kp.step_pair_conservative(
            w,
            pair_rounds,
            qmul=qmul,
            phase_count=12,
            tick=int(t),
            shuffle_round_order=False,
            use_all_rounds_per_tick=bool(full_round_sweep),
        )
        if np.array_equal(w, world0):
            return int(t)
    return None


def _run_once(
    *,
    nx: int,
    ny: int,
    nz: int,
    seed: kp.SiteSeed,
    qmul: np.ndarray,
    pair_rounds: kp.PairRounds,
    period_search_max: int,
    full_round_sweep: bool,
) -> Dict[str, Any]:
    qn = int(qmul.shape[0])
    vac = int(c12.s_identity_id())
    sid = int(kp.sid_from_site_seed(seed, qn=qn))

    world0 = np.full((int(nx * ny * nz),), np.uint16(vac), dtype=np.uint16)
    world0[_center_idx(nx, ny, nz)] = np.uint16(int(sid))
    period = _find_period(
        world0=world0,
        pair_rounds=pair_rounds,
        qmul=qmul,
        period_search_max=int(period_search_max),
        full_round_sweep=bool(full_round_sweep),
    )
    if period is None:
        return {
            "period_found": False,
            "period": None,
            "ticks_run": int(period_search_max),
            "checkpoints": [],
            "all_four_period_checks_pass": False,
        }

    horizon = int(4 * period)
    w = world0.copy()
    checkpoints: List[Dict[str, Any]] = []
    for t in range(1, horizon + 1):
        w = kp.step_pair_conservative(
            w,
            pair_rounds,
            qmul=qmul,
            phase_count=12,
            tick=int(t),
            shuffle_round_order=False,
            use_all_rounds_per_tick=bool(full_round_sweep),
        )
        if t % period == 0:
            checkpoints.append(
                {
                    "tick": int(t),
                    "cycle_k": int(t // period),
                    "matches_initial": bool(np.array_equal(w, world0)),
                }
            )

    return {
        "period_found": True,
        "period": int(period),
        "ticks_run": int(horizon),
        "checkpoints": checkpoints,
        "all_four_period_checks_pass": bool(all(bool(c["matches_initial"]) for c in checkpoints)),
    }


def build_payload(
    *,
    nx: int,
    ny: int,
    nz: int,
    period_search_max: int,
    runs: int,
    domain: int,
    octavian_id: int,
    energy_n: int,
    energy_phase: int,
    full_round_sweep: bool,
) -> Dict[str, Any]:
    qmul = c12.build_qmul_table()
    pair_rounds = kp.build_pair_rounds(nx, ny, nz, stencil_id="cube26", boundary_mode="fixed_vacuum")
    seed = kp.SiteSeed(
        domain=int(domain) % 3,
        octavian_id=int(octavian_id),
        energy_n=int(energy_n),
        energy_phase=int(energy_phase) % 4,
    )

    run_rows: List[Dict[str, Any]] = []
    for rid in range(1, int(runs) + 1):
        row = _run_once(
            nx=int(nx),
            ny=int(ny),
            nz=int(nz),
            seed=seed,
            qmul=qmul,
            pair_rounds=pair_rounds,
            period_search_max=int(period_search_max),
            full_round_sweep=bool(full_round_sweep),
        )
        row["run_id"] = int(rid)
        run_rows.append(row)

    payload: Dict[str, Any] = {
        "schema_version": "v3_single_particle_four_period_runs_v1",
        "kernel_profile": str(kp.KERNEL_PROFILE),
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(ROOT / SCRIPT_REPO_PATH),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(ROOT / KERNEL_REPO_PATH),
        "grid": [int(nx), int(ny), int(nz)],
        "seed": {
            "domain": int(seed.domain),
            "octavian_id": int(seed.octavian_id),
            "energy_n": int(seed.energy_n),
            "energy_phase": int(seed.energy_phase),
            "sid": int(kp.sid_from_site_seed(seed, qn=int(qmul.shape[0]))),
        },
        "notes": [
            "One particle seeded at center, all other sites vacuum.",
            "Each run is deterministic in this configuration.",
            "energy_n is metadata only in current kernel lane (non-dynamical).",
        ],
        "period_search_max": int(period_search_max),
        "full_round_sweep": bool(full_round_sweep),
        "runs_requested": int(runs),
        "runs": run_rows,
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def _render_md(payload: Dict[str, Any]) -> str:
    lines = [
        "# v3 Single-Particle Four-Period Runs (v1)",
        "",
        f"- kernel_profile: `{payload['kernel_profile']}`",
        f"- grid: `{payload['grid']}`",
        f"- seed: `{payload['seed']}`",
        f"- period_search_max: `{payload['period_search_max']}`",
        f"- full_round_sweep: `{payload['full_round_sweep']}`",
        "",
        "| run_id | period_found | period | ticks_run | all_four_period_checks_pass |",
        "|---:|---:|---:|---:|---:|",
    ]
    for r in payload["runs"]:
        lines.append(
            f"| {int(r['run_id'])} | {bool(r['period_found'])} | "
            f"{'NA' if r['period'] is None else int(r['period'])} | {int(r['ticks_run'])} | "
            f"{bool(r['all_four_period_checks_pass'])} |"
        )
    lines.append("")
    lines.append("## Checkpoints")
    lines.append("")
    for r in payload["runs"]:
        lines.append(f"### Run {int(r['run_id'])}")
        cps = r["checkpoints"]
        if not cps:
            lines.append("- no checkpoints (period not found)")
            lines.append("")
            continue
        lines.append("| cycle_k | tick | matches_initial |")
        lines.append("|---:|---:|---:|")
        for c in cps:
            lines.append(
                f"| {int(c['cycle_k'])} | {int(c['tick'])} | {bool(c['matches_initial'])} |"
            )
        lines.append("")
    return "\n".join(lines)


def write_artifacts(payload: Dict[str, Any]) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    OUT_MD.write_text(_render_md(payload), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Run one-particle simulation 4 times over >=4 periods.")
    ap.add_argument("--size-x", type=int, default=7)
    ap.add_argument("--size-y", type=int, default=7)
    ap.add_argument("--size-z", type=int, default=7)
    ap.add_argument("--period-search-max", type=int, default=600)
    ap.add_argument("--runs", type=int, default=4)
    ap.add_argument("--domain", type=int, default=1)
    ap.add_argument("--octavian-id", type=int, default=239)
    ap.add_argument("--energy-n", type=int, default=4)
    ap.add_argument("--energy-phase", type=int, default=1)
    ap.add_argument("--strict-lightcone-round", action="store_true", help="Use one disjoint round per tick")
    args = ap.parse_args()

    payload = build_payload(
        nx=int(args.size_x),
        ny=int(args.size_y),
        nz=int(args.size_z),
        period_search_max=int(args.period_search_max),
        runs=int(args.runs),
        domain=int(args.domain),
        octavian_id=int(args.octavian_id),
        energy_n=int(args.energy_n),
        energy_phase=int(args.energy_phase),
        full_round_sweep=not bool(args.strict_lightcone_round),
    )
    write_artifacts(payload)
    print("v3_single_particle_four_period_runs_v1: wrote JSON+MD")


if __name__ == "__main__":
    main()
