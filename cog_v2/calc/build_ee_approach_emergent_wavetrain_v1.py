"""Two-electron approach simulation under canonical v2 projection kernel.

Goal:
1) Start with two electron motifs far apart and moving toward each other,
2) Evolve deterministically with kernel-native state updates,
3) Observe whether a coherent imaginary-spin mediator ("photon-like wavetrain")
   and e-e repulsion behavior emerge without forcing outcomes.

This script does not inject an explicit Coulomb term. The only dynamic force
uses a pressure signal derived from the mediator state produced by kernel
interaction folding and phase content.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from cog_v2.python import kernel_projective_unity as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "ee_approach_emergent_wavetrain_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "ee_approach_emergent_wavetrain_v1.md"
SCRIPT_REPO_PATH = "cog_v2/calc/build_ee_approach_emergent_wavetrain_v1.py"
KERNEL_REPO_PATH = "cog_v2/python/kernel_projective_unity.py"

BASIS_LABELS: Tuple[str, ...] = tuple(k.BASIS_LABELS)


@dataclass(frozen=True)
class SimulationParams:
    ticks: int = 180
    x_left_0: float = -12.0
    x_right_0: float = 12.0
    v_left_0: float = 0.35
    v_right_0: float = -0.35
    interaction_radius: float = 12.0
    energy_scale: int = 2
    accel_scale: float = 0.04
    max_speed: float = 1.5
    thin_output_step: int = 1
    left_ops: Tuple[int, ...] = (7, 7, 7, 7)
    right_ops: Tuple[int, ...] = (7, 7, 7, 7)


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _coeff(re: int, im: int = 0) -> k.GInt:
    return k.GInt(int(re), int(im))


def _state_from_sparse(mapping: Dict[int, k.GInt]) -> k.CxO:
    vals = [k.ZERO_G] * 8
    for idx, z in mapping.items():
        vals[int(idx)] = z
    return (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7])


def _serialize_state(state: k.CxO) -> List[List[int]]:
    return [[int(z.re), int(z.im)] for z in state]


def _state_to_map(state: k.CxO) -> Dict[str, List[int]]:
    return {BASIS_LABELS[i]: [int(z.re), int(z.im)] for i, z in enumerate(state)}


def _basis_state(op_idx: int) -> k.CxO:
    vals = [k.ZERO_G] * 8
    vals[int(op_idx)] = k.ONE_G
    return (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7])


def _left_mul_projected(op_idx: int, state: k.CxO) -> k.CxO:
    return k.project_cxo_to_unity(k.cxo_mul(_basis_state(int(op_idx)), state))


def _sign(x: float) -> int:
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def _clip(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _distance_to_multiplicity(distance: float, radius: float, energy_scale: int) -> int:
    if distance > float(radius):
        return 0
    raw = float(radius) - float(distance) + 1.0
    return int(max(0, math.floor(raw * float(energy_scale))))


def _charge_proxy(state: k.CxO) -> int:
    # Locked deterministic proxy from e111 channel sign (re preferred over im).
    z = state[7]
    if z.re != 0:
        return 1 if z.re > 0 else -1
    if z.im != 0:
        return 1 if z.im > 0 else -1
    return 0


def _mediator_metrics(mediator: k.CxO) -> Dict[str, float]:
    imag_by_channel = [abs(float(mediator[i].im)) for i in range(1, 8)]
    real_by_channel = [abs(float(mediator[i].re)) for i in range(1, 8)]
    imag_total = float(sum(imag_by_channel))
    real_total = float(sum(real_by_channel))
    nonvac_total = float(imag_total + real_total)
    imag_share = 0.0 if nonvac_total == 0.0 else float(imag_total / nonvac_total)
    imag_dom = 0.0 if imag_total == 0.0 else float(max(imag_by_channel) / imag_total)
    wavetrain_coherence = float(imag_share * imag_dom)
    return {
        "imag_total_nonvac": float(imag_total),
        "real_total_nonvac": float(real_total),
        "imag_share_nonvac": float(imag_share),
        "imag_dominance": float(imag_dom),
        "wavetrain_coherence": float(wavetrain_coherence),
    }


def _electron_motif_state() -> k.CxO:
    # Canonical electron-like motif in the v2 basis (projected from doubled legacy scale):
    # e000 = -i, e111 = -1.
    s = _state_from_sparse(
        {
            0: _coeff(0, -1),
            7: _coeff(-1, 0),
        }
    )
    return k.project_cxo_to_unity(s)


def _simulate(params: SimulationParams) -> Dict[str, Any]:
    thin_step = max(1, int(params.thin_output_step))

    left = _electron_motif_state()
    right = _electron_motif_state()

    x_left = float(params.x_left_0)
    x_right = float(params.x_right_0)
    v_left = float(params.v_left_0)
    v_right = float(params.v_right_0)

    rows: List[Dict[str, Any]] = []
    first_interaction_tick: int | None = None
    first_wavetrain_tick: int | None = None
    first_separation_tick: int | None = None
    first_left_reverse_tick: int | None = None
    first_right_reverse_tick: int | None = None
    min_distance = float("inf")
    max_pressure_signal = 0.0
    max_wavetrain_coherence = 0.0

    prev_left_toward = True
    prev_right_toward = True
    prev_approach_speed_positive = True

    for tick in range(int(params.ticks)):
        rel = float(x_right - x_left)
        rel_sign = _sign(rel)
        distance = abs(rel)
        min_distance = min(min_distance, distance)

        multiplicity = _distance_to_multiplicity(distance, float(params.interaction_radius), int(params.energy_scale))
        interaction_started_now = bool(multiplicity > 0 and first_interaction_tick is None)
        if interaction_started_now:
            first_interaction_tick = int(tick)

        lop = int(params.left_ops[tick % len(params.left_ops)])
        rop = int(params.right_ops[tick % len(params.right_ops)])

        left_internal = _left_mul_projected(lop, left)
        right_internal = _left_mul_projected(rop, right)

        mediator = k.interaction_fold([left_internal, right_internal]) if multiplicity > 0 else k.cxo_one()
        mm = _mediator_metrics(mediator)
        wavetrain_started_now = bool(mm["wavetrain_coherence"] > 0.0 and first_wavetrain_tick is None)
        if wavetrain_started_now:
            first_wavetrain_tick = int(tick)

        # Kernel-native state updates with distance-gated message multiplicity.
        left_next = k.update_rule(left_internal, [right_internal for _ in range(multiplicity)])
        right_next = k.update_rule(right_internal, [left_internal for _ in range(multiplicity)])

        q_left = _charge_proxy(left_next)
        q_right = _charge_proxy(right_next)
        charge_pair = int(q_left * q_right)

        # Emergent pressure from mediator coherence and distance-gated coupling.
        pressure = float(multiplicity) * float(mm["wavetrain_coherence"])
        max_pressure_signal = max(max_pressure_signal, pressure)
        max_wavetrain_coherence = max(max_wavetrain_coherence, float(mm["wavetrain_coherence"]))

        # Force direction follows charge-pair sign and geometry only.
        force_left = float(-charge_pair * pressure * rel_sign)
        force_right = float(charge_pair * pressure * rel_sign)

        v_left = _clip(float(v_left + float(params.accel_scale) * force_left), -float(params.max_speed), float(params.max_speed))
        v_right = _clip(
            float(v_right + float(params.accel_scale) * force_right), -float(params.max_speed), float(params.max_speed)
        )

        x_left = float(x_left + v_left)
        x_right = float(x_right + v_right)

        left_toward = bool(v_left * rel_sign > 0.0)
        right_toward = bool(v_right * rel_sign < 0.0)
        approach_speed = float((v_left - v_right) * rel_sign)
        approach_speed_positive = bool(approach_speed > 0.0)

        left_reversal_now = bool(prev_left_toward and not left_toward and first_left_reverse_tick is None)
        if left_reversal_now:
            first_left_reverse_tick = int(tick)
        right_reversal_now = bool(prev_right_toward and not right_toward and first_right_reverse_tick is None)
        if right_reversal_now:
            first_right_reverse_tick = int(tick)
        separation_now = bool(prev_approach_speed_positive and (not approach_speed_positive) and first_separation_tick is None)
        if separation_now:
            first_separation_tick = int(tick)

        is_last_tick = bool(tick == int(params.ticks) - 1)
        keep_by_stride = bool(tick % thin_step == 0)
        keep_by_event = bool(
            interaction_started_now
            or wavetrain_started_now
            or left_reversal_now
            or right_reversal_now
            or separation_now
        )
        if thin_step <= 1 or keep_by_stride or keep_by_event or is_last_tick:
            rows.append(
                {
                    "tick": int(tick),
                    "x_left": float(x_left),
                    "x_right": float(x_right),
                    "distance": float(abs(x_right - x_left)),
                    "v_left": float(v_left),
                    "v_right": float(v_right),
                    "approach_speed": float(approach_speed),
                    "interaction_multiplicity": int(multiplicity),
                    "charge_left": int(q_left),
                    "charge_right": int(q_right),
                    "charge_pair_sign": int(charge_pair),
                    "pressure_signal": float(pressure),
                    "wavetrain_coherence": float(mm["wavetrain_coherence"]),
                    "imag_share_nonvac": float(mm["imag_share_nonvac"]),
                    "imag_dominance": float(mm["imag_dominance"]),
                    "mediator_state_vector": _serialize_state(mediator),
                    "left_state_vector": _serialize_state(left_next),
                    "right_state_vector": _serialize_state(right_next),
                    "left_state": _state_to_map(left_next),
                    "right_state": _state_to_map(right_next),
                }
            )

        prev_left_toward = left_toward
        prev_right_toward = right_toward
        prev_approach_speed_positive = approach_speed_positive

        left = left_next
        right = right_next

    summary: Dict[str, Any] = {
        "first_interaction_tick": first_interaction_tick,
        "first_wavetrain_tick": first_wavetrain_tick,
        "first_left_reverse_tick": first_left_reverse_tick,
        "first_right_reverse_tick": first_right_reverse_tick,
        "first_separation_tick": first_separation_tick,
        "min_distance": float(min_distance if min_distance != float("inf") else 0.0),
        "max_pressure_signal": float(max_pressure_signal),
        "max_wavetrain_coherence": float(max_wavetrain_coherence),
        "any_reversal": bool(first_left_reverse_tick is not None or first_right_reverse_tick is not None),
        "any_separation_after_approach": bool(first_separation_tick is not None),
        "final_distance": float(abs(x_right - x_left)),
        "recorded_row_count": int(len(rows)),
        "total_tick_count": int(params.ticks),
    }

    return {
        "params": {
            "ticks": int(params.ticks),
            "x_left_0": float(params.x_left_0),
            "x_right_0": float(params.x_right_0),
            "v_left_0": float(params.v_left_0),
            "v_right_0": float(params.v_right_0),
            "interaction_radius": float(params.interaction_radius),
            "energy_scale": int(params.energy_scale),
            "accel_scale": float(params.accel_scale),
            "max_speed": float(params.max_speed),
            "thin_output_step": int(thin_step),
            "left_ops": [int(x) for x in params.left_ops],
            "right_ops": [int(x) for x in params.right_ops],
        },
        "summary": summary,
        "tick_rows": rows,
    }


def build_payload(params: SimulationParams | None = None) -> Dict[str, Any]:
    p = params if params is not None else SimulationParams()
    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH
    simulation = _simulate(p)
    payload: Dict[str, Any] = {
        "schema_version": "ee_approach_emergent_wavetrain_v1",
        "claim_id": "EE-APPROACH-001",
        "mode": "simulation_first_structure_first",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(kernel_path),
        "kernel_profile": k.KERNEL_PROFILE,
        "projector_id": k.PROJECTOR_ID,
        "basis_labels": list(BASIS_LABELS),
        "simulation": simulation,
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def _render_md(payload: Dict[str, Any]) -> str:
    sim = payload["simulation"]
    params = sim["params"]
    summary = sim["summary"]
    lines = [
        "# Two-Electron Approach Emergent Wavetrain (v1)",
        "",
        "## Setup",
        "",
        "- Two identical electron motifs initialized far apart in 1D.",
        "- Initial velocities point toward each other.",
        "- State updates use only `kernel_projective_unity` update rules.",
        "- Distance gates interaction multiplicity; no explicit Coulomb law term is injected.",
        "",
        "## Parameters",
        "",
        f"- ticks: `{params['ticks']}`",
        f"- x_left_0, x_right_0: `{params['x_left_0']}`, `{params['x_right_0']}`",
        f"- v_left_0, v_right_0: `{params['v_left_0']}`, `{params['v_right_0']}`",
        f"- interaction_radius: `{params['interaction_radius']}`",
        f"- energy_scale: `{params['energy_scale']}`",
        f"- accel_scale: `{params['accel_scale']}`",
        f"- thin_output_step: `{params['thin_output_step']}`",
        "",
        "## Outcome Summary",
        "",
        f"- first_interaction_tick: `{summary['first_interaction_tick']}`",
        f"- first_wavetrain_tick: `{summary['first_wavetrain_tick']}`",
        f"- first_left_reverse_tick: `{summary['first_left_reverse_tick']}`",
        f"- first_right_reverse_tick: `{summary['first_right_reverse_tick']}`",
        f"- first_separation_tick: `{summary['first_separation_tick']}`",
        f"- any_reversal: `{summary['any_reversal']}`",
        f"- any_separation_after_approach: `{summary['any_separation_after_approach']}`",
        f"- min_distance: `{summary['min_distance']}`",
        f"- final_distance: `{summary['final_distance']}`",
        f"- recorded_row_count / total_tick_count: `{summary['recorded_row_count']}` / `{summary['total_tick_count']}`",
        "",
        "## Notes",
        "",
        "- `wavetrain_coherence` is a mediator diagnostic from imaginary-spin content of the folded mediator state.",
        "- `pressure_signal` is derived from mediator coherence and interaction multiplicity only.",
        "- `tick_rows` may be thinned by `thin_output_step`; key event ticks are always retained.",
        "- Full exact microstates are recoverable by rerunning with `--thin-output 1`.",
    ]
    return "\n".join(lines) + "\n"


def write_artifacts(payload: Dict[str, Any], json_paths: Sequence[Path] = (OUT_JSON,), md_paths: Sequence[Path] = (OUT_MD,)) -> None:
    for path in json_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_text = _render_md(payload)
    for path in md_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(md_text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticks", type=int, default=SimulationParams.ticks)
    parser.add_argument("--v0", type=float, default=SimulationParams.v_left_0, help="symmetric speed magnitude")
    parser.add_argument("--x0", type=float, default=abs(SimulationParams.x_left_0), help="half-separation at tick 0")
    parser.add_argument("--radius", type=float, default=SimulationParams.interaction_radius)
    parser.add_argument("--energy-scale", type=int, default=SimulationParams.energy_scale)
    parser.add_argument("--accel-scale", type=float, default=SimulationParams.accel_scale)
    parser.add_argument(
        "--thin-output",
        type=int,
        default=SimulationParams.thin_output_step,
        help="record every Nth tick in tick_rows (plus first/last/event ticks). Use 1 for full output.",
    )
    args = parser.parse_args()

    p = SimulationParams(
        ticks=int(args.ticks),
        x_left_0=-abs(float(args.x0)),
        x_right_0=abs(float(args.x0)),
        v_left_0=abs(float(args.v0)),
        v_right_0=-abs(float(args.v0)),
        interaction_radius=float(args.radius),
        energy_scale=int(args.energy_scale),
        accel_scale=float(args.accel_scale),
        thin_output_step=max(1, int(args.thin_output)),
    )
    payload = build_payload(p)
    write_artifacts(payload)
    s = payload["simulation"]["summary"]
    print(
        "ee_approach_emergent_wavetrain_v1: "
        f"reversal={s['any_reversal']}, "
        f"first_interaction_tick={s['first_interaction_tick']}, "
        f"first_separation_tick={s['first_separation_tick']}, "
        f"max_wavetrain_coherence={s['max_wavetrain_coherence']:.4f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
