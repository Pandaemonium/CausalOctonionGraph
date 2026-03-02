"""Probe chirality-to-direction coupling for photon-candidate phase ramps (v1).

Test question:
- Do chirality/phase-ramp seeds produce signed one-way transport,
  or only symmetric light-cone front splitting?

Method:
1) Build 1D packet seeds from su/sd vacuum motifs.
2) Apply phase ramps using e111 left-multiply cycle.
3) Evolve with canonical kernel update_rule and nearest-neighbor messages.
4) Measure centroid drift, directionality index, and front speeds.
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
OUT_JSON = ROOT / "cog_v2" / "sources" / "photon_chirality_direction_probe_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "photon_chirality_direction_probe_v1.md"
SCRIPT_REPO_PATH = "cog_v2/calc/build_photon_chirality_direction_probe_v1.py"
KERNEL_REPO_PATH = "cog_v2/python/kernel_projective_unity.py"
MOTIF_SOURCE_REPO_PATH = "calc/xor_scenario_loader.py::canonical_motif_state_map"


@dataclass(frozen=True)
class ChiralityProbeParams:
    ticks: int = 96
    width: int = 257
    packet_width: int = 9
    warmup_ticks: int = 24
    thin_output_step: int = 4
    drift_sign_tol: float = 1e-6


@dataclass(frozen=True)
class SeedCase:
    case_id: str
    mode: str
    description: str


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


def _phase_cycle_e111(seed: k.CxO) -> Tuple[k.CxO, k.CxO, k.CxO, k.CxO]:
    s0 = seed
    s1 = _left_mul_projected(7, s0)
    s2 = _left_mul_projected(7, s1)
    s3 = _left_mul_projected(7, s2)
    return (s0, s1, s2, s3)


def _seed_cases() -> Tuple[SeedCase, ...]:
    return (
        SeedCase("flat_su", "flat_su", "Symmetric flat packet from su_vacuum_omega."),
        SeedCase("ramp_plus_su", "ramp_plus_su", "Phase ramp +k from su_vacuum_omega."),
        SeedCase("ramp_minus_su", "ramp_minus_su", "Phase ramp -k from su_vacuum_omega."),
        SeedCase("ramp_plus_sd", "ramp_plus_sd", "Phase ramp +k from sd_vacuum_omega_dag."),
        SeedCase("ramp_minus_sd", "ramp_minus_sd", "Phase ramp -k from sd_vacuum_omega_dag."),
    )


def _build_seed_world(case: SeedCase, p: ChiralityProbeParams, su: k.CxO, sd: k.CxO) -> List[k.CxO]:
    n = int(p.width)
    w = int(p.packet_width)
    if w < 3 or w % 2 == 0:
        raise ValueError("packet_width must be odd and >= 3")
    c = n // 2
    h = w // 2
    x0 = c - h
    x1 = c + h
    world = [k.cxo_one() for _ in range(n)]

    cyc_su = _phase_cycle_e111(su)
    cyc_sd = _phase_cycle_e111(sd)
    for x in range(x0, x1 + 1):
        r = int(x - x0)
        if case.mode == "flat_su":
            state = su
        elif case.mode == "ramp_plus_su":
            state = cyc_su[r % 4]
        elif case.mode == "ramp_minus_su":
            state = cyc_su[(-r) % 4]
        elif case.mode == "ramp_plus_sd":
            state = cyc_sd[r % 4]
        elif case.mode == "ramp_minus_sd":
            state = cyc_sd[(-r) % 4]
        else:
            raise ValueError(f"unknown mode: {case.mode}")
        world[x] = state
    return world


def _nonvac_power_1d(world: Sequence[k.CxO]) -> List[float]:
    out: List[float] = []
    for s in world:
        out.append(float(sum(int(z.re * z.re + z.im * z.im) for z in s[1:])))
    return out


def _centroid_x(power: Sequence[float]) -> float:
    den = float(sum(power))
    if den <= 1e-12:
        return 0.0
    return float(sum(float(i) * float(power[i]) for i in range(len(power))) / den)


def _support_bounds(power: Sequence[float]) -> Tuple[int, int]:
    idx = [i for i, v in enumerate(power) if float(v) > 0.0]
    if not idx:
        return -1, -1
    return int(min(idx)), int(max(idx))


def _simulate_case(case: SeedCase, p: ChiralityProbeParams, su: k.CxO, sd: k.CxO) -> Dict[str, Any]:
    n = int(p.width)
    c = n // 2
    world = _build_seed_world(case, p, su, sd)
    rows: List[Dict[str, Any]] = []
    centroid_trace: List[float] = []
    dir_index_trace: List[float] = []
    left_front: List[int] = []
    right_front: List[int] = []
    thin = max(1, int(p.thin_output_step))

    for tick in range(int(p.ticks) + 1):
        power = _nonvac_power_1d(world)
        cx = _centroid_x(power)
        lf, rf = _support_bounds(power)
        lp = float(sum(power[:c]))
        rp = float(sum(power[c + 1 :]))
        denom = lp + rp
        di = 0.0 if denom <= 1e-12 else float((rp - lp) / denom)

        centroid_trace.append(float(cx))
        dir_index_trace.append(float(di))
        left_front.append(int(lf))
        right_front.append(int(rf))

        if tick % thin == 0 or tick == int(p.ticks):
            rows.append(
                {
                    "tick": int(tick),
                    "centroid_x": float(cx),
                    "left_front_x": int(lf),
                    "right_front_x": int(rf),
                    "left_power": float(lp),
                    "right_power": float(rp),
                    "directionality_index": float(di),
                }
            )

        if tick == int(p.ticks):
            break

        old = world
        nxt: List[k.CxO] = [k.cxo_one() for _ in range(n)]
        for x in range(n):
            msgs: List[k.CxO] = []
            if x - 1 >= 0:
                msgs.append(old[x - 1])
            if x + 1 < n:
                msgs.append(old[x + 1])
            nxt[x] = k.update_rule(old[x], msgs)
        world = nxt

    warm = max(0, min(int(p.warmup_ticks), len(centroid_trace) - 2))
    vel = [float(centroid_trace[t + 1] - centroid_trace[t]) for t in range(warm, len(centroid_trace) - 1)]
    mean_v = float(sum(vel) / len(vel)) if vel else 0.0

    ls = [
        float(left_front[t - 1] - left_front[t])
        for t in range(1, len(left_front))
        if left_front[t] >= 0 and left_front[t - 1] >= 0
    ]
    rs = [
        float(right_front[t] - right_front[t - 1])
        for t in range(1, len(right_front))
        if right_front[t] >= 0 and right_front[t - 1] >= 0
    ]
    mean_ls = float(sum(ls) / len(ls)) if ls else 0.0
    mean_rs = float(sum(rs) / len(rs)) if rs else 0.0
    max_front_step = max([abs(v) for v in ls] + [abs(v) for v in rs]) if (ls or rs) else 0.0
    mean_dir = float(sum(dir_index_trace[warm:]) / max(1, len(dir_index_trace[warm:])))

    summary = {
        "case_id": case.case_id,
        "description": case.description,
        "mean_centroid_velocity_x_tail": float(mean_v),
        "mean_directionality_index_tail": float(mean_dir),
        "left_front_speed_mean_abs": float(mean_ls),
        "right_front_speed_mean_abs": float(mean_rs),
        "max_front_step_speed_abs": float(max_front_step),
        "lightcone_saturated_both_fronts": bool(
            ls and rs and all(abs(v - 1.0) < 1e-9 for v in ls) and all(abs(v - 1.0) < 1e-9 for v in rs)
        ),
    }
    return {"summary": summary, "rows": rows}


def build_payload(params: ChiralityProbeParams | None = None) -> Dict[str, Any]:
    p = params if params is not None else ChiralityProbeParams()
    if int(p.width) < 65:
        raise ValueError("width must be >= 65")
    if int(p.ticks) < 16:
        raise ValueError("ticks must be >= 16")

    motifs = canonical_motif_state_map()
    su = _to_cxo(motifs["su_vacuum_omega"])
    sd = _to_cxo(motifs["sd_vacuum_omega_dag"])

    cases = _seed_cases()
    lanes = [_simulate_case(c, p, su, sd) for c in cases]
    sm = {row["summary"]["case_id"]: row["summary"] for row in lanes}
    tol = float(p.drift_sign_tol)
    vpp = float(sm["ramp_plus_su"]["mean_centroid_velocity_x_tail"])
    vpn = float(sm["ramp_minus_su"]["mean_centroid_velocity_x_tail"])
    vdp = float(sm["ramp_plus_sd"]["mean_centroid_velocity_x_tail"])
    vdn = float(sm["ramp_minus_sd"]["mean_centroid_velocity_x_tail"])

    checks = {
        "all_cases_lightcone_saturated_fronts": bool(all(bool(r["summary"]["lightcone_saturated_both_fronts"]) for r in lanes)),
        "su_ramp_has_signed_opposite_drift": bool(vpp * vpn < -tol),
        "sd_ramp_has_signed_opposite_drift": bool(vdp * vdn < -tol),
        "any_nonzero_group_drift": bool(max(abs(vpp), abs(vpn), abs(vdp), abs(vdn)) > tol),
    }

    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH
    payload: Dict[str, Any] = {
        "schema_version": "photon_chirality_direction_probe_v1",
        "claim_id": "PHOTON-CANDIDATE-003",
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
            "warmup_ticks": int(p.warmup_ticks),
            "thin_output_step": int(max(1, int(p.thin_output_step))),
            "drift_sign_tol": float(p.drift_sign_tol),
        },
        "cases": lanes,
        "checks": checks,
        "notes": [
            "Phase ramps are built from repeated left-multiply by e111 over su/sd vacuum seeds.",
            "Front propagation and group drift are measured separately.",
            "If chirality-direction coupling is strong, +k and -k ramps should produce opposite signed centroid drifts.",
        ],
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def _render_md(payload: Dict[str, Any]) -> str:
    p = payload["params"]
    lines = [
        "# Photon Chirality-Direction Probe (v1)",
        "",
        "## Params",
        "",
        f"- ticks: `{p['ticks']}`",
        f"- width: `{p['width']}`",
        f"- packet_width: `{p['packet_width']}`",
        f"- warmup_ticks: `{p['warmup_ticks']}`",
        "",
        "## Case Summaries",
        "",
        "| case_id | mean_centroid_velocity_x_tail | mean_directionality_index_tail | left_front_speed_mean_abs | right_front_speed_mean_abs |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in payload["cases"]:
        s = row["summary"]
        lines.append(
            f"| `{s['case_id']}` | {s['mean_centroid_velocity_x_tail']:.6f} | {s['mean_directionality_index_tail']:.6f} | "
            f"{s['left_front_speed_mean_abs']:.6f} | {s['right_front_speed_mean_abs']:.6f} |"
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
    parser.add_argument("--ticks", type=int, default=ChiralityProbeParams.ticks)
    parser.add_argument("--width", type=int, default=ChiralityProbeParams.width)
    parser.add_argument("--packet-width", type=int, default=ChiralityProbeParams.packet_width)
    parser.add_argument("--warmup", type=int, default=ChiralityProbeParams.warmup_ticks)
    parser.add_argument("--thin-output-step", type=int, default=ChiralityProbeParams.thin_output_step)
    parser.add_argument("--drift-sign-tol", type=float, default=ChiralityProbeParams.drift_sign_tol)
    args = parser.parse_args()

    payload = build_payload(
        ChiralityProbeParams(
            ticks=int(args.ticks),
            width=int(args.width),
            packet_width=int(args.packet_width),
            warmup_ticks=int(args.warmup),
            thin_output_step=int(args.thin_output_step),
            drift_sign_tol=float(args.drift_sign_tol),
        )
    )
    write_artifacts(payload)
    print(
        "photon_chirality_direction_probe_v1: "
        f"any_nonzero_group_drift={payload['checks']['any_nonzero_group_drift']}, "
        f"su_opposite_drift={payload['checks']['su_ramp_has_signed_opposite_drift']}, "
        f"sd_opposite_drift={payload['checks']['sd_ramp_has_signed_opposite_drift']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

