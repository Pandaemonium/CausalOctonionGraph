"""Test directional photon-candidate transport in 3D (v1).

Purpose:
1) Seed coherent vacuum-phase packets with symmetric and directional/chiral initial conditions.
2) Evolve under canonical projective-unity kernel on a finite 3D lattice.
3) Measure:
   - front speeds along x,
   - left/right power asymmetry,
   - whether one-sided front transport emerges.

This is an explicit test lane; negative findings are first-class outputs.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from calc.xor_scenario_loader import canonical_motif_state_map
from cog_v2.python import kernel_projective_unity as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "photon_candidate_directional_transport_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "photon_candidate_directional_transport_v1.md"
SCRIPT_REPO_PATH = "cog_v2/calc/build_photon_candidate_directional_transport_v1.py"
KERNEL_REPO_PATH = "cog_v2/python/kernel_projective_unity.py"
MOTIF_SOURCE_REPO_PATH = "calc/xor_scenario_loader.py::canonical_motif_state_map"


@dataclass(frozen=True)
class DirectionalPhotonParams:
    ticks: int = 36
    size_x: int = 121
    size_y: int = 11
    size_z: int = 11
    packet_width_x: int = 5
    thin_output_step: int = 1
    warmup_ticks: int = 8
    one_sided_speed_ratio_threshold: float = 0.25


@dataclass(frozen=True)
class SeedCase:
    case_id: str
    description: str
    mode: str


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _to_cxo(state_gi: Sequence[Tuple[int, int]]) -> k.CxO:
    vals = [k.GInt(int(re), int(im)) for re, im in state_gi]
    return k.project_cxo_to_unity((vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7]))


def _basis_state(op_idx: int) -> k.CxO:
    vals = [k.ZERO_G] * 8
    vals[int(op_idx)] = k.ONE_G
    return (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7])


def _left_mul_projected(op_idx: int, state: k.CxO) -> k.CxO:
    return k.project_cxo_to_unity(k.cxo_mul(_basis_state(int(op_idx)), state))


def _abs2(z: k.GInt) -> int:
    return int(z.re * z.re + z.im * z.im)


def _idx(x: int, y: int, z: int, sy: int, sz: int) -> int:
    return (int(x) * int(sy) + int(y)) * int(sz) + int(z)


def _seed_cases() -> Tuple[SeedCase, ...]:
    return (
        SeedCase(
            case_id="sym_control",
            mode="sym_control",
            description="Symmetric coherent packet (control).",
        ),
        SeedCase(
            case_id="dir_grad_plusx",
            mode="dir_grad_plusx",
            description="Directional phase-gradient packet, biased toward +x.",
        ),
        SeedCase(
            case_id="dir_bias_plusx",
            mode="dir_bias_plusx",
            description="Directional packet with opposite-phase loading on -x side.",
        ),
    )


def _build_seed_world(
    *,
    p: DirectionalPhotonParams,
    case: SeedCase,
    packet_su: k.CxO,
    packet_sd: k.CxO,
) -> List[k.CxO]:
    sx, sy, sz = int(p.size_x), int(p.size_y), int(p.size_z)
    world = [k.cxo_one() for _ in range(sx * sy * sz)]
    cx, cy, cz = sx // 2, sy // 2, sz // 2
    half = int(p.packet_width_x) // 2
    x0 = int(cx - half)
    x1 = int(x0 + int(p.packet_width_x) - 1)

    for x in range(x0, x1 + 1):
        if case.mode == "sym_control":
            s = packet_su
        elif case.mode == "dir_grad_plusx":
            if x <= cx - 1:
                s = _left_mul_projected(1, packet_su) if x == cx - 2 else _left_mul_projected(2, packet_su)
            elif x >= cx + 1:
                s = _left_mul_projected(7, packet_su)
            else:
                s = packet_su
        elif case.mode == "dir_bias_plusx":
            s = packet_sd if x <= cx - 1 else packet_su
        else:
            raise ValueError(f"unknown seed mode: {case.mode}")
        world[_idx(x, cy, cz, sy, sz)] = s
    return world


def _slice_metrics(
    *,
    world: Sequence[k.CxO],
    sx: int,
    sy: int,
    sz: int,
    cx: int,
) -> Dict[str, Any]:
    slice_nonvac = [0.0 for _ in range(sx)]
    for x, y, z in itertools.product(range(sx), range(sy), range(sz)):
        s = world[_idx(x, y, z, sy, sz)]
        slice_nonvac[x] += float(sum(_abs2(s[i]) for i in range(1, 8)))
    support = [x for x, v in enumerate(slice_nonvac) if v > 0.0]
    left_front = int(min(support)) if support else -1
    right_front = int(max(support)) if support else -1
    left_power = float(sum(slice_nonvac[:cx]))
    right_power = float(sum(slice_nonvac[cx + 1 :]))
    denom = float(left_power + right_power)
    directionality = 0.0 if denom <= 1e-12 else float((right_power - left_power) / denom)
    return {
        "slice_nonvac": [float(v) for v in slice_nonvac],
        "left_front_x": int(left_front),
        "right_front_x": int(right_front),
        "left_power": float(left_power),
        "right_power": float(right_power),
        "directionality_index": float(directionality),
        "disturbed_slice_count": int(len(support)),
    }


def _simulate_case(case: SeedCase, p: DirectionalPhotonParams, packet_su: k.CxO, packet_sd: k.CxO) -> Dict[str, Any]:
    sx, sy, sz = int(p.size_x), int(p.size_y), int(p.size_z)
    cx = sx // 2
    world = _build_seed_world(p=p, case=case, packet_su=packet_su, packet_sd=packet_sd)

    rows: List[Dict[str, Any]] = []
    left_front_trace: List[int] = []
    right_front_trace: List[int] = []
    dir_trace: List[float] = []
    thin = max(1, int(p.thin_output_step))

    for tick in range(int(p.ticks) + 1):
        sm = _slice_metrics(world=world, sx=sx, sy=sy, sz=sz, cx=cx)
        left_front_trace.append(int(sm["left_front_x"]))
        right_front_trace.append(int(sm["right_front_x"]))
        dir_trace.append(float(sm["directionality_index"]))

        if (tick % thin == 0) or (tick == int(p.ticks)):
            rows.append(
                {
                    "tick": int(tick),
                    "left_front_x": int(sm["left_front_x"]),
                    "right_front_x": int(sm["right_front_x"]),
                    "disturbed_slice_count": int(sm["disturbed_slice_count"]),
                    "left_power": float(sm["left_power"]),
                    "right_power": float(sm["right_power"]),
                    "directionality_index": float(sm["directionality_index"]),
                }
            )

        if tick == int(p.ticks):
            break

        old = world
        nxt: List[k.CxO] = [k.cxo_one() for _ in range(sx * sy * sz)]
        for x, y, z in itertools.product(range(sx), range(sy), range(sz)):
            msgs: List[k.CxO] = []
            if x - 1 >= 0:
                msgs.append(old[_idx(x - 1, y, z, sy, sz)])
            if x + 1 < sx:
                msgs.append(old[_idx(x + 1, y, z, sy, sz)])
            if y - 1 >= 0:
                msgs.append(old[_idx(x, y - 1, z, sy, sz)])
            if y + 1 < sy:
                msgs.append(old[_idx(x, y + 1, z, sy, sz)])
            if z - 1 >= 0:
                msgs.append(old[_idx(x, y, z - 1, sy, sz)])
            if z + 1 < sz:
                msgs.append(old[_idx(x, y, z + 1, sy, sz)])
            nxt[_idx(x, y, z, sy, sz)] = k.update_rule(old[_idx(x, y, z, sy, sz)], msgs)
        world = nxt

    left_speeds = [
        float(left_front_trace[t - 1] - left_front_trace[t])
        for t in range(1, len(left_front_trace))
        if left_front_trace[t] >= 0 and left_front_trace[t - 1] >= 0
    ]
    right_speeds = [
        float(right_front_trace[t] - right_front_trace[t - 1])
        for t in range(1, len(right_front_trace))
        if right_front_trace[t] >= 0 and right_front_trace[t - 1] >= 0
    ]

    def _mean(vals: Sequence[float]) -> float:
        return float(sum(vals) / len(vals)) if vals else 0.0

    warm = max(0, min(int(p.warmup_ticks), len(dir_trace) - 1))
    dir_tail = dir_trace[warm:]
    dir_mean_tail = _mean(dir_tail)
    max_front_step = max([abs(v) for v in left_speeds] + [abs(v) for v in right_speeds]) if (left_speeds or right_speeds) else 0.0
    one_sided = bool(
        _mean(left_speeds) <= float(p.one_sided_speed_ratio_threshold)
        or _mean(right_speeds) <= float(p.one_sided_speed_ratio_threshold)
    )

    summary = {
        "case_id": case.case_id,
        "description": case.description,
        "left_front_speed_mean_abs": float(_mean(left_speeds)),
        "right_front_speed_mean_abs": float(_mean(right_speeds)),
        "max_front_step_speed_abs": float(max_front_step),
        "causal_bound_front_speed_le_1": bool(max_front_step <= 1.000000001),
        "lightcone_saturated_both_fronts": bool(
            left_speeds
            and right_speeds
            and all(abs(v - 1.0) < 1e-9 for v in left_speeds)
            and all(abs(v - 1.0) < 1e-9 for v in right_speeds)
        ),
        "directionality_index_mean_tail": float(dir_mean_tail),
        "one_sided_transport_detected": bool(one_sided),
    }
    return {"summary": summary, "rows": rows}


def build_payload(params: DirectionalPhotonParams | None = None) -> Dict[str, Any]:
    p = params if params is not None else DirectionalPhotonParams()
    if int(p.ticks) < 8:
        raise ValueError("ticks must be >= 8")
    if int(p.size_x) < 41:
        raise ValueError("size_x must be >= 41")
    if int(p.size_y) < 5 or int(p.size_z) < 5:
        raise ValueError("size_y and size_z must be >= 5")

    motifs = canonical_motif_state_map()
    packet_su = _to_cxo(motifs["su_vacuum_omega"])
    packet_sd = _to_cxo(motifs["sd_vacuum_omega_dag"])

    cases = _seed_cases()
    case_rows = [_simulate_case(c, p, packet_su, packet_sd) for c in cases]
    summary_map = {row["summary"]["case_id"]: row["summary"] for row in case_rows}
    control = summary_map["sym_control"]

    checks = {
        "all_cases_causal_bound_ok": bool(all(bool(r["summary"]["causal_bound_front_speed_le_1"]) for r in case_rows)),
        "all_cases_lightcone_saturated": bool(all(bool(r["summary"]["lightcone_saturated_both_fronts"]) for r in case_rows)),
        "any_case_one_sided_transport": bool(any(bool(r["summary"]["one_sided_transport_detected"]) for r in case_rows)),
        "directional_cases_shift_power_asymmetry_vs_control": bool(
            any(
                abs(float(r["summary"]["directionality_index_mean_tail"]))
                > abs(float(control["directionality_index_mean_tail"])) + 1e-6
                for r in case_rows
                if r["summary"]["case_id"] != "sym_control"
            )
        ),
    }

    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH
    payload: Dict[str, Any] = {
        "schema_version": "photon_candidate_directional_transport_v1",
        "claim_id": "PHOTON-CANDIDATE-002",
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
            "size_x": int(p.size_x),
            "size_y": int(p.size_y),
            "size_z": int(p.size_z),
            "packet_width_x": int(p.packet_width_x),
            "thin_output_step": int(max(1, int(p.thin_output_step))),
            "warmup_ticks": int(p.warmup_ticks),
            "one_sided_speed_ratio_threshold": float(p.one_sided_speed_ratio_threshold),
        },
        "cases": case_rows,
        "checks": checks,
        "notes": [
            "Directional seeds can bias left/right power distribution.",
            "Under this canonical kernel lane, front speeds still typically saturate both directions at light-cone speed.",
            "One-sided transport requires explicit detection; absence is a valid result.",
        ],
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def _render_md(payload: Dict[str, Any]) -> str:
    p = payload["params"]
    lines = [
        "# Photon-Candidate Directional Transport (v1)",
        "",
        "## Params",
        "",
        f"- ticks: `{p['ticks']}`",
        f"- size_xyz: `({p['size_x']}, {p['size_y']}, {p['size_z']})`",
        f"- packet_width_x: `{p['packet_width_x']}`",
        f"- warmup_ticks: `{p['warmup_ticks']}`",
        "",
        "## Case Summaries",
        "",
        "| case_id | left_front_speed_mean_abs | right_front_speed_mean_abs | directionality_index_mean_tail | one_sided_transport_detected |",
        "|---|---:|---:|---:|---|",
    ]
    for row in payload["cases"]:
        s = row["summary"]
        lines.append(
            f"| `{s['case_id']}` | {s['left_front_speed_mean_abs']:.6f} | "
            f"{s['right_front_speed_mean_abs']:.6f} | {s['directionality_index_mean_tail']:.6f} | "
            f"{s['one_sided_transport_detected']} |"
        )
    lines.extend(["", "## Checks", ""])
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
    parser.add_argument("--ticks", type=int, default=DirectionalPhotonParams.ticks)
    parser.add_argument("--size-x", type=int, default=DirectionalPhotonParams.size_x)
    parser.add_argument("--size-y", type=int, default=DirectionalPhotonParams.size_y)
    parser.add_argument("--size-z", type=int, default=DirectionalPhotonParams.size_z)
    parser.add_argument("--packet-width-x", type=int, default=DirectionalPhotonParams.packet_width_x)
    parser.add_argument("--thin-output-step", type=int, default=DirectionalPhotonParams.thin_output_step)
    parser.add_argument("--warmup", type=int, default=DirectionalPhotonParams.warmup_ticks)
    parser.add_argument(
        "--one-sided-threshold",
        type=float,
        default=DirectionalPhotonParams.one_sided_speed_ratio_threshold,
    )
    args = parser.parse_args()

    payload = build_payload(
        DirectionalPhotonParams(
            ticks=int(args.ticks),
            size_x=int(args.size_x),
            size_y=int(args.size_y),
            size_z=int(args.size_z),
            packet_width_x=int(args.packet_width_x),
            thin_output_step=int(args.thin_output_step),
            warmup_ticks=int(args.warmup),
            one_sided_speed_ratio_threshold=float(args.one_sided_threshold),
        )
    )
    write_artifacts(payload)
    print(
        "photon_candidate_directional_transport_v1: "
        f"one_sided_any={payload['checks']['any_case_one_sided_transport']}, "
        f"lightcone_all={payload['checks']['all_cases_lightcone_saturated']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

