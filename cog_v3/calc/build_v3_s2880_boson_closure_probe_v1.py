"""Short-horizon dynamic closure probe for S2880 boson candidate lanes.

This probe treats bosons as motifs/process lanes rather than single immutable symbols.
It runs seeded-vs-baseline worlds under the pair-conservative kernel and tracks whether
the induced perturbation remains inside the intended structural role lane.

Inputs:
- cog_v3/sources/v3_s2880_boson_candidate_scan_v1.json
- cog_v3/sources/v3_s2880_particle_interaction_catalog_v1.csv

Outputs:
- cog_v3/sources/v3_s2880_boson_closure_probe_v1.json
- cog_v3/sources/v3_s2880_boson_closure_probe_v1.md
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set

import numpy as np

from cog_v3.python import kernel_octavian240_multiplicative_v1 as k
from cog_v3.python import kernel_s2880_pair_conservative_v1 as kp


ROOT = Path(__file__).resolve().parents[2]

IN_SCAN = ROOT / "cog_v3" / "sources" / "v3_s2880_boson_candidate_scan_v1.json"
IN_ROLE = ROOT / "cog_v3" / "sources" / "v3_s2880_particle_interaction_catalog_v1.csv"

OUT_JSON = ROOT / "cog_v3" / "sources" / "v3_s2880_boson_closure_probe_v1.json"
OUT_MD = ROOT / "cog_v3" / "sources" / "v3_s2880_boson_closure_probe_v1.md"

SCRIPT_REPO_PATH = "cog_v3/calc/build_v3_s2880_boson_closure_probe_v1.py"
KERNEL_REPO_PATH = "cog_v3/python/kernel_s2880_pair_conservative_v1.py"


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _read_scan(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_role_rows(path: Path) -> Dict[int, Dict[str, Any]]:
    by_sid: Dict[int, Dict[str, Any]] = {}
    with path.open("r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            sid = int(row["s_id"])
            by_sid[sid] = {
                "top_role_1": str(row["top_role_1"]),
                "score_photon_like": float(row["score_photon_like"]),
                "score_mediator_w_like": float(row["score_mediator_w_like"]),
                "score_unstable_crossmix_like": float(row["score_unstable_crossmix_like"]),
                "score_quark_core_like": float(row["score_quark_core_like"]),
                "score_neutrino_like": float(row["score_neutrino_like"]),
                "label": str(row["label"]),
                "q_id": int(row["q_id"]),
                "phase_idx": int(row["phase_idx"]),
            }
    return by_sid


@dataclass(frozen=True)
class LaneSpec:
    lane_id: str
    candidate_key: str
    primary_role: str
    primary_score_key: str
    allowed_roles: Set[str]


LANES: Sequence[LaneSpec] = (
    LaneSpec(
        lane_id="photon_lane",
        candidate_key="photon_like_top",
        primary_role="photon_like",
        primary_score_key="score_photon_like",
        allowed_roles={"photon_like", "neutrino_like"},
    ),
    LaneSpec(
        lane_id="weak_lane",
        candidate_key="mediator_w_like_top",
        primary_role="mediator_w_like",
        primary_score_key="score_mediator_w_like",
        allowed_roles={"mediator_w_like", "unstable_crossmix_like"},
    ),
    LaneSpec(
        lane_id="gluon_proxy_lane",
        candidate_key="gluon_proxy_top",
        primary_role="unstable_crossmix_like",
        primary_score_key="score_unstable_crossmix_like",
        allowed_roles={"unstable_crossmix_like", "mediator_w_like", "quark_core_like"},
    ),
)


def _center_index(nx: int, ny: int, nz: int) -> int:
    cx, cy, cz = int(nx) // 2, int(ny) // 2, int(nz) // 2
    return (cx * int(ny) + cy) * int(nz) + cz


def _mean(values: List[float]) -> float:
    if not values:
        return 0.0
    return float(sum(values) / float(len(values)))


def _run_seed_probe(
    *,
    seed_sid: int,
    lane: LaneSpec,
    roles_by_sid: Dict[int, Dict[str, Any]],
    pair_rounds: kp.PairRounds,
    qmul: np.ndarray,
    ticks: int,
    nx: int,
    ny: int,
    nz: int,
    global_seed: int,
    vacuum_sid: int,
) -> Dict[str, Any]:
    n = int(nx) * int(ny) * int(nz)
    world_base = np.full(n, int(vacuum_sid), dtype=np.uint16)
    world_seed = np.full(n, int(vacuum_sid), dtype=np.uint16)
    cidx = _center_index(int(nx), int(ny), int(nz))
    world_seed[int(cidx)] = np.uint16(int(seed_sid))

    tick_rows: List[Dict[str, Any]] = []
    active_ticks = 0
    first_extinct_tick: Optional[int] = None

    for t in range(int(ticks)):
        world_base = kp.step_pair_conservative(
            world_base,
            pair_rounds,
            qmul=qmul,
            phase_count=12,
            global_seed=int(global_seed),
            tick=int(t),
            shuffle_round_order=False,
            use_all_rounds_per_tick=False,
        )
        world_seed = kp.step_pair_conservative(
            world_seed,
            pair_rounds,
            qmul=qmul,
            phase_count=12,
            global_seed=int(global_seed),
            tick=int(t),
            shuffle_round_order=False,
            use_all_rounds_per_tick=False,
        )

        mask = world_seed != world_base
        diff_count = int(np.count_nonzero(mask))
        lane_frac = 0.0
        primary_frac = 0.0
        primary_score_mean = 0.0

        if diff_count > 0:
            active_ticks += 1
            sid_vals = world_seed[mask].astype(np.int32)
            allowed = 0
            primary = 0
            pscore: List[float] = []
            for sid in sid_vals.tolist():
                row = roles_by_sid.get(int(sid))
                if row is None:
                    continue
                role = str(row["top_role_1"])
                if role in lane.allowed_roles:
                    allowed += 1
                if role == lane.primary_role:
                    primary += 1
                pscore.append(float(row.get(lane.primary_score_key, 0.0)))
            denom = float(len(sid_vals))
            if denom > 0.0:
                lane_frac = float(allowed) / denom
                primary_frac = float(primary) / denom
            primary_score_mean = _mean(pscore)
        elif first_extinct_tick is None:
            first_extinct_tick = int(t + 1)

        tick_rows.append(
            {
                "tick": int(t + 1),
                "diff_count": int(diff_count),
                "lane_fraction": float(lane_frac),
                "primary_fraction": float(primary_frac),
                "primary_score_mean": float(primary_score_mean),
            }
        )

    lane_fracs = [float(r["lane_fraction"]) for r in tick_rows if int(r["diff_count"]) > 0]
    primary_scores = [float(r["primary_score_mean"]) for r in tick_rows if int(r["diff_count"]) > 0]
    peak_diff = max((int(r["diff_count"]) for r in tick_rows), default=0)
    final_diff = int(tick_rows[-1]["diff_count"]) if tick_rows else 0
    survival_ratio = float(active_ticks) / max(1.0, float(ticks))
    lane_mean = _mean(lane_fracs)
    score_mean = _mean(primary_scores)
    closure_score = float(0.5 * lane_mean + 0.3 * survival_ratio + 0.2 * score_mean)

    return {
        "seed_sid": int(seed_sid),
        "seed_label": str(roles_by_sid.get(int(seed_sid), {}).get("label", f"s{seed_sid}")),
        "active_ticks": int(active_ticks),
        "ticks": int(ticks),
        "survival_ratio": float(survival_ratio),
        "first_extinct_tick": None if first_extinct_tick is None else int(first_extinct_tick),
        "peak_diff_count": int(peak_diff),
        "final_diff_count": int(final_diff),
        "lane_fraction_mean_active": float(lane_mean),
        "primary_score_mean_active": float(score_mean),
        "closure_score": float(closure_score),
        "tick_trace": tick_rows,
    }


def _render_md(payload: Dict[str, Any]) -> str:
    cfg = payload["config"]
    lines: List[str] = [
        "# v3 S2880 Boson Closure Probe (v1)",
        "",
        f"- schema_version: `{payload['schema_version']}`",
        f"- kernel_profile: `{payload['kernel_profile']}`",
        f"- ticks: `{cfg['ticks']}`",
        f"- grid: `{cfg['nx']}x{cfg['ny']}x{cfg['nz']}`",
        f"- stencil: `{cfg['stencil_id']}`",
        f"- boundary: `{cfg['boundary_mode']}`",
        "",
        "## Lane Summary",
        "",
        "| lane | n_seeds | mean closure | mean lane fraction | mean survival |",
        "|---|---:|---:|---:|---:|",
    ]

    for lane_id, lane in payload["lane_results"].items():
        lines.append(
            f"| `{lane_id}` | {int(lane['n_seeds'])} | "
            f"{float(lane['closure_score_mean']):.4f} | "
            f"{float(lane['lane_fraction_mean']):.4f} | "
            f"{float(lane['survival_ratio_mean']):.4f} |"
        )

    for lane_id, lane in payload["lane_results"].items():
        lines.extend(
            [
                "",
                f"## Top Seeds: {lane_id}",
                "",
                "| seed_sid | closure | lane frac | survival | peak diff | final diff | label |",
                "|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for r in lane["top_seeds"]:
            lines.append(
                f"| {int(r['seed_sid'])} | {float(r['closure_score']):.4f} | "
                f"{float(r['lane_fraction_mean_active']):.4f} | {float(r['survival_ratio']):.4f} | "
                f"{int(r['peak_diff_count'])} | {int(r['final_diff_count'])} | `{str(r['seed_label'])}` |"
            )
    return "\n".join(lines)


def build_payload(
    *,
    top_n: int,
    ticks: int,
    nx: int,
    ny: int,
    nz: int,
    stencil_id: str,
    boundary_mode: str,
    global_seed: int,
    vacuum_phase: int,
) -> Dict[str, Any]:
    scan = _read_scan(IN_SCAN)
    roles_by_sid = _read_role_rows(IN_ROLE)
    qmul = kp.default_qmul_table()
    qn = int(qmul.shape[0])
    vacuum_sid = int((int(vacuum_phase) % 12) * int(qn) + int(k.IDENTITY_ID))
    pair_rounds = kp.build_pair_rounds(
        int(nx),
        int(ny),
        int(nz),
        stencil_id=str(stencil_id),
        boundary_mode=str(boundary_mode),
    )

    lane_results: Dict[str, Any] = {}
    all_seed_metrics: Dict[str, List[Dict[str, Any]]] = {}

    for lane in LANES:
        seed_rows = list(scan["candidates"].get(lane.candidate_key, []))[: int(top_n)]
        seed_sids = [int(r["s_id"]) for r in seed_rows]
        metrics: List[Dict[str, Any]] = []
        for sid in seed_sids:
            metrics.append(
                _run_seed_probe(
                    seed_sid=int(sid),
                    lane=lane,
                    roles_by_sid=roles_by_sid,
                    pair_rounds=pair_rounds,
                    qmul=qmul,
                    ticks=int(ticks),
                    nx=int(nx),
                    ny=int(ny),
                    nz=int(nz),
                    global_seed=int(global_seed),
                    vacuum_sid=int(vacuum_sid),
                )
            )
        metrics.sort(key=lambda x: (float(x["closure_score"]), float(x["survival_ratio"]), float(x["lane_fraction_mean_active"])), reverse=True)
        all_seed_metrics[lane.lane_id] = metrics
        lane_results[lane.lane_id] = {
            "n_seeds": int(len(metrics)),
            "closure_score_mean": _mean([float(m["closure_score"]) for m in metrics]),
            "lane_fraction_mean": _mean([float(m["lane_fraction_mean_active"]) for m in metrics]),
            "survival_ratio_mean": _mean([float(m["survival_ratio"]) for m in metrics]),
            "top_seeds": metrics[: min(12, len(metrics))],
        }

    payload: Dict[str, Any] = {
        "schema_version": "v3_s2880_boson_closure_probe_v1",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(ROOT / SCRIPT_REPO_PATH),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(ROOT / KERNEL_REPO_PATH),
        "kernel_profile": kp.KERNEL_PROFILE,
        "inputs": {
            "scan_json": str(IN_SCAN.relative_to(ROOT)).replace("\\", "/"),
            "scan_json_sha256": _sha_file(IN_SCAN),
            "role_csv": str(IN_ROLE.relative_to(ROOT)).replace("\\", "/"),
            "role_csv_sha256": _sha_file(IN_ROLE),
        },
        "config": {
            "top_n": int(top_n),
            "ticks": int(ticks),
            "nx": int(nx),
            "ny": int(ny),
            "nz": int(nz),
            "stencil_id": str(stencil_id),
            "boundary_mode": str(boundary_mode),
            "global_seed": int(global_seed),
            "vacuum_phase": int(vacuum_phase),
            "vacuum_sid": int(vacuum_sid),
            "pair_round_count": int(len(pair_rounds.rounds)),
        },
        "lane_results": lane_results,
        "seed_metrics": all_seed_metrics,
        "notes": [
            "Closure here means short-horizon lane retention of perturbation states under seeded-vs-baseline differencing.",
            "This is a motif/process probe, not a proof that a boson is a single S2880 symbol.",
        ],
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def write_artifacts(payload: Dict[str, Any]) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_render_md(payload), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--top-n", type=int, default=16)
    ap.add_argument("--ticks", type=int, default=8)
    ap.add_argument("--nx", type=int, default=9)
    ap.add_argument("--ny", type=int, default=9)
    ap.add_argument("--nz", type=int, default=9)
    ap.add_argument("--stencil-id", choices=["axial6", "cube26"], default="axial6")
    ap.add_argument("--boundary-mode", choices=["fixed_vacuum", "periodic"], default="fixed_vacuum")
    ap.add_argument("--global-seed", type=int, default=20260303)
    ap.add_argument("--vacuum-phase", type=int, default=0)
    args = ap.parse_args()

    payload = build_payload(
        top_n=int(args.top_n),
        ticks=int(args.ticks),
        nx=int(args.nx),
        ny=int(args.ny),
        nz=int(args.nz),
        stencil_id=str(args.stencil_id),
        boundary_mode=str(args.boundary_mode),
        global_seed=int(args.global_seed),
        vacuum_phase=int(args.vacuum_phase),
    )
    write_artifacts(payload)
    lanes = payload["lane_results"]
    print(
        "v3_s2880_boson_closure_probe_v1: "
        + ", ".join(
            f"{lid}=closure:{float(v['closure_score_mean']):.4f},survival:{float(v['survival_ratio_mean']):.4f}"
            for lid, v in lanes.items()
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

