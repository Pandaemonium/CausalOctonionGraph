"""Model a photon-candidate as a coherent vacuum-phase wave packet (v1).

Operational definition in this artifact:
1) Seed a compact packet of coherent vacuum phase in 1D vacuum background.
2) Evolve under the canonical projective-unity kernel with nearest-neighbor causal updates.
3) Measure front propagation speed and phase-orientation coherence.

This is a structure-first simulation lane. It does not claim full SM photon closure.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from calc.xor_scenario_loader import canonical_motif_state_map
from cog_v2.python import kernel_projective_unity as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "photon_candidate_vacuum_wave_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "photon_candidate_vacuum_wave_v1.md"
SCRIPT_REPO_PATH = "cog_v2/calc/build_photon_candidate_vacuum_wave_v1.py"
KERNEL_REPO_PATH = "cog_v2/python/kernel_projective_unity.py"
MOTIF_SOURCE_REPO_PATH = "calc/xor_scenario_loader.py::canonical_motif_state_map"


@dataclass(frozen=True)
class PhotonWaveParams:
    ticks: int = 64
    width: int = 257
    packet_width: int = 5
    thin_output_step: int = 1
    motif_ids: Tuple[str, ...] = ("su_vacuum_omega", "sd_vacuum_omega_dag")


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _to_cxo(state_gi: Sequence[Tuple[int, int]]) -> k.CxO:
    if len(state_gi) != 8:
        raise ValueError("motif state must have 8 coefficients")
    vals = [k.GInt(int(re), int(im)) for re, im in state_gi]
    return k.project_cxo_to_unity((vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7]))


def _serialize_state(state: k.CxO) -> List[List[int]]:
    return [[int(z.re), int(z.im)] for z in state]


def _disturbed_support(world: Sequence[k.CxO], vacuum: k.CxO) -> List[int]:
    return [i for i, s in enumerate(world) if s != vacuum]


def _phase_alignment(world: Sequence[k.CxO], vacuum: k.CxO) -> Dict[str, Any]:
    disturbed = [s for s in world if s != vacuum]
    if not disturbed:
        return {
            "disturbed_count": 0,
            "e111_unique": [],
            "dominant_e111": [0, 0],
            "dominant_share": 0.0,
        }
    e7_vals = [(int(s[7].re), int(s[7].im)) for s in disturbed]
    counts: Dict[Tuple[int, int], int] = {}
    for v in e7_vals:
        counts[v] = counts.get(v, 0) + 1
    dominant = max(counts.items(), key=lambda kv: kv[1])
    return {
        "disturbed_count": int(len(disturbed)),
        "e111_unique": [[int(a), int(b)] for a, b in sorted(counts.keys())],
        "dominant_e111": [int(dominant[0][0]), int(dominant[0][1])],
        "dominant_share": float(dominant[1] / max(1, len(disturbed))),
    }


def _simulate_lane(motif_id: str, packet_state: k.CxO, p: PhotonWaveParams) -> Dict[str, Any]:
    n = int(p.width)
    vac = k.cxo_one()
    if n < 33:
        raise ValueError("width must be >= 33")
    if int(p.packet_width) < 1 or int(p.packet_width) > (n // 3):
        raise ValueError("packet_width must be in [1, width//3]")

    c = n // 2
    half = int(p.packet_width) // 2
    seed_left = int(c - half)
    seed_right = int(seed_left + int(p.packet_width) - 1)

    world: List[k.CxO] = [vac for _ in range(n)]
    for x in range(seed_left, seed_right + 1):
        world[x] = packet_state

    rows: List[Dict[str, Any]] = []
    left_fronts: List[int] = []
    right_fronts: List[int] = []

    thin = max(1, int(p.thin_output_step))
    for tick in range(int(p.ticks) + 1):
        sup = _disturbed_support(world, vac)
        if sup:
            lf = int(min(sup))
            rf = int(max(sup))
        else:
            lf = -1
            rf = -1
        left_fronts.append(lf)
        right_fronts.append(rf)
        ph = _phase_alignment(world, vac)

        keep = (tick % thin == 0) or (tick == int(p.ticks))
        if keep:
            rows.append(
                {
                    "tick": int(tick),
                    "left_front_x": int(lf),
                    "right_front_x": int(rf),
                    "disturbed_count": int(ph["disturbed_count"]),
                    "e111_unique": ph["e111_unique"],
                    "dominant_e111": ph["dominant_e111"],
                    "dominant_share": float(ph["dominant_share"]),
                }
            )

        if tick == int(p.ticks):
            break

        old = world
        nxt: List[k.CxO] = [vac for _ in range(n)]
        for x in range(n):
            msgs: List[k.CxO] = []
            if x - 1 >= 0:
                msgs.append(old[x - 1])
            if x + 1 < n:
                msgs.append(old[x + 1])
            nxt[x] = k.update_rule(old[x], msgs)
        world = nxt

    left_step_speeds: List[float] = []
    right_step_speeds: List[float] = []
    for t in range(1, len(left_fronts)):
        if left_fronts[t] >= 0 and left_fronts[t - 1] >= 0:
            left_step_speeds.append(float(left_fronts[t - 1] - left_fronts[t]))
        if right_fronts[t] >= 0 and right_fronts[t - 1] >= 0:
            right_step_speeds.append(float(right_fronts[t] - right_fronts[t - 1]))

    def mean(xs: Sequence[float]) -> float:
        return float(sum(xs) / len(xs)) if xs else 0.0

    left_mean = mean(left_step_speeds)
    right_mean = mean(right_step_speeds)
    all_speed_samples = [abs(x) for x in left_step_speeds] + [abs(x) for x in right_step_speeds]
    max_front_step = float(max(all_speed_samples) if all_speed_samples else 0.0)
    causal_bound_ok = bool(max_front_step <= 1.000000001)
    lightcone_saturated = bool(
        left_step_speeds
        and right_step_speeds
        and all(abs(v - 1.0) < 1e-9 for v in left_step_speeds)
        and all(abs(v - 1.0) < 1e-9 for v in right_step_speeds)
    )

    final_phase = _phase_alignment(world, vac)
    summary = {
        "motif_id": motif_id,
        "seed_interval_x": [int(seed_left), int(seed_right)],
        "seed_state_vector": _serialize_state(packet_state),
        "left_front_speed_mean_abs": float(left_mean),
        "right_front_speed_mean_abs": float(right_mean),
        "max_front_step_speed_abs": float(max_front_step),
        "causal_bound_front_speed_le_1": bool(causal_bound_ok),
        "lightcone_saturated_front_speed_eq_1": bool(lightcone_saturated),
        "final_disturbed_count": int(final_phase["disturbed_count"]),
        "final_dominant_e111": final_phase["dominant_e111"],
        "final_dominant_e111_share": float(final_phase["dominant_share"]),
    }
    return {"summary": summary, "rows": rows}


def build_payload(params: PhotonWaveParams | None = None) -> Dict[str, Any]:
    p = params if params is not None else PhotonWaveParams()
    if int(p.ticks) < 8:
        raise ValueError("ticks must be >= 8")
    if int(p.width) < 33:
        raise ValueError("width must be >= 33")

    motifs = canonical_motif_state_map()
    lanes: List[Dict[str, Any]] = []
    for motif_id in p.motif_ids:
        if motif_id not in motifs:
            raise KeyError(f"unknown motif_id: {motif_id}")
        state = _to_cxo(motifs[motif_id])
        lanes.append(_simulate_lane(motif_id, state, p))

    checks = {
        "all_lanes_causal_bound_ok": bool(all(bool(l["summary"]["causal_bound_front_speed_le_1"]) for l in lanes)),
        "all_lanes_lightcone_saturated": bool(all(bool(l["summary"]["lightcone_saturated_front_speed_eq_1"]) for l in lanes)),
        "all_lanes_high_phase_alignment": bool(all(float(l["summary"]["final_dominant_e111_share"]) >= 0.95 for l in lanes)),
    }

    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH
    payload: Dict[str, Any] = {
        "schema_version": "photon_candidate_vacuum_wave_v1",
        "claim_id": "PHOTON-CANDIDATE-001",
        "mode": "simulation_first_structure_first",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(kernel_path),
        "kernel_profile": k.KERNEL_PROFILE,
        "projector_id": k.PROJECTOR_ID,
        "motif_source": MOTIF_SOURCE_REPO_PATH,
        "params": {
            "ticks": int(p.ticks),
            "width": int(p.width),
            "packet_width": int(p.packet_width),
            "thin_output_step": int(max(1, int(p.thin_output_step))),
            "motif_ids": [str(x) for x in p.motif_ids],
        },
        "lanes": lanes,
        "checks": checks,
        "notes": [
            "This lane models a photon-candidate as coherent vacuum-phase packet propagation.",
            "Speed metric is front propagation (disturbance support edge) in 1D nearest-neighbor causal updates.",
            "Orientation proxy is dominant e111 phase sign (+i vs -i).",
        ],
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def _render_md(payload: Dict[str, Any]) -> str:
    p = payload["params"]
    lines = [
        "# Photon-Candidate Vacuum Wave (v1)",
        "",
        "## Scope",
        "",
        "- Model: coherent vacuum-phase packet in 1D canonical kernel lane",
        "- Not a full electrodynamic closure claim",
        "",
        "## Params",
        "",
        f"- ticks: `{p['ticks']}`",
        f"- width: `{p['width']}`",
        f"- packet_width: `{p['packet_width']}`",
        f"- thin_output_step: `{p['thin_output_step']}`",
        f"- motif_ids: `{p['motif_ids']}`",
        "",
        "## Lane Summaries",
        "",
        "| motif_id | left_front_speed_mean_abs | right_front_speed_mean_abs | max_front_step_speed_abs | causal_bound_front_speed_le_1 | lightcone_saturated_front_speed_eq_1 | final_dominant_e111 | final_dominant_e111_share |",
        "|---|---:|---:|---:|---|---|---|---:|",
    ]
    for lane in payload["lanes"]:
        s = lane["summary"]
        lines.append(
            f"| `{s['motif_id']}` | {s['left_front_speed_mean_abs']:.6f} | {s['right_front_speed_mean_abs']:.6f} | "
            f"{s['max_front_step_speed_abs']:.6f} | {s['causal_bound_front_speed_le_1']} | "
            f"{s['lightcone_saturated_front_speed_eq_1']} | `{s['final_dominant_e111']}` | "
            f"{s['final_dominant_e111_share']:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Checks",
            "",
        ]
    )
    for kx, vx in payload["checks"].items():
        lines.append(f"- {kx}: `{vx}`")
    lines.append("")
    return "\n".join(lines)


def write_artifacts(
    payload: Dict[str, Any],
    json_paths: Sequence[Path] = (OUT_JSON,),
    md_paths: Sequence[Path] = (OUT_MD,),
) -> None:
    for path in json_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = _render_md(payload)
    for path in md_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(md, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticks", type=int, default=PhotonWaveParams.ticks)
    parser.add_argument("--width", type=int, default=PhotonWaveParams.width)
    parser.add_argument("--packet-width", type=int, default=PhotonWaveParams.packet_width)
    parser.add_argument("--thin-output-step", type=int, default=PhotonWaveParams.thin_output_step)
    parser.add_argument(
        "--motif-ids",
        nargs="*",
        default=list(PhotonWaveParams.motif_ids),
        help="motif ids to test as coherent vacuum-phase packet seeds",
    )
    args = parser.parse_args()
    mids = tuple(str(x) for x in args.motif_ids)
    if not mids:
        raise ValueError("motif-ids must be non-empty")
    payload = build_payload(
        PhotonWaveParams(
            ticks=int(args.ticks),
            width=int(args.width),
            packet_width=int(args.packet_width),
            thin_output_step=int(args.thin_output_step),
            motif_ids=mids,
        )
    )
    write_artifacts(payload)
    print(
        "photon_candidate_vacuum_wave_v1: "
        f"lanes={len(payload['lanes'])}, "
        f"lightcone_saturated={payload['checks']['all_lanes_lightcone_saturated']}, "
        f"causal_bound_ok={payload['checks']['all_lanes_causal_bound_ok']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

