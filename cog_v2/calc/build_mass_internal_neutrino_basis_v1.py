"""Build internal neutrino-basis mass artifact (v1).

This lane uses an internal normalization policy:
    m_nu := 1
and computes electron mass in neutrino units from a preregistered v2 metric:
    m_eff = <R_t + lambda * V_t> / <Y_t>

Where:
  - R_t: non-e000 rephasing load (normalized L1 state delta),
  - V_t: global e000 share,
  - Y_t: non-e000 centroid displacement per tick.
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
OUT_JSON = ROOT / "cog_v2" / "sources" / "mass_internal_neutrino_basis_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "mass_internal_neutrino_basis_v1.md"
SCRIPT_REPO_PATH = "cog_v2/calc/build_mass_internal_neutrino_basis_v1.py"
KERNEL_REPO_PATH = "cog_v2/python/kernel_projective_unity.py"
MOTIF_SOURCE_REPO_PATH = "calc/xor_scenario_loader.py::canonical_motif_state_map"


@dataclass(frozen=True)
class MassBasisParams:
    ticks: int = 160
    warmup_ticks: int = 80
    width: int = 96
    lambda_vacuum_drag: float = 1.0
    source_op_cycle: Tuple[int, ...] = (7, 7, 7, 7)


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _abs2(z: k.GInt) -> int:
    return int(z.re * z.re + z.im * z.im)


def _to_cxo(state_gi: Sequence[Tuple[int, int]]) -> k.CxO:
    if len(state_gi) != 8:
        raise ValueError("motif state must have 8 coefficients")
    vals = [k.GInt(int(re), int(im)) for re, im in state_gi]
    return k.project_cxo_to_unity((vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7]))


def _basis_state(op_idx: int) -> k.CxO:
    vals = [k.ZERO_G] * 8
    vals[int(op_idx)] = k.ONE_G
    return (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7])


def _left_mul_projected(op_idx: int, state: k.CxO) -> k.CxO:
    return k.project_cxo_to_unity(k.cxo_mul(_basis_state(int(op_idx)), state))


def _simulate_lane(motif_id: str, params: MassBasisParams) -> Dict[str, Any]:
    motifs = canonical_motif_state_map()
    if motif_id not in motifs:
        raise KeyError(f"unknown motif_id: {motif_id}")
    if int(params.width) < 8:
        raise ValueError("width must be >= 8")
    if int(params.ticks) < 4:
        raise ValueError("ticks must be >= 4")

    source_state = _to_cxo(motifs[motif_id])
    states: List[k.CxO] = [k.cxo_one() for _ in range(int(params.width))]
    states[0] = source_state

    rows: List[Dict[str, float]] = []
    prev_centroid: float | None = None
    max_non_e000_delta_per_node = 14.0  # 7 channels * max per-channel L1 delta (2)
    eps = 1e-12
    op_cycle = tuple(int(x) for x in params.source_op_cycle)
    if not op_cycle:
        raise ValueError("source_op_cycle must be non-empty")

    for tick in range(int(params.ticks)):
        op = int(op_cycle[tick % len(op_cycle)])
        source_state = _left_mul_projected(op, source_state)

        old = list(states)
        old[0] = source_state
        nxt: List[k.CxO] = [k.cxo_one() for _ in range(int(params.width))]
        nxt[0] = source_state
        for x in range(1, int(params.width)):
            nxt[x] = k.update_rule(old[x], [old[x - 1]])

        rho_non_e000: List[float] = []
        e000_power = 0.0
        non_e000_power = 0.0
        rephase_l1_total = 0.0
        for x in range(int(params.width)):
            s_old = old[x]
            s_new = nxt[x]
            nv = float(sum(_abs2(s_new[i]) for i in range(1, 8)))
            rho_non_e000.append(nv)
            e000_power += float(_abs2(s_new[0]))
            non_e000_power += nv
            rephase_l1_total += float(
                sum(abs(s_new[i].re - s_old[i].re) + abs(s_new[i].im - s_old[i].im) for i in range(1, 8))
            )

        rho_den = float(sum(rho_non_e000))
        centroid = 0.0 if rho_den <= eps else float(sum(float(i) * rho_non_e000[i] for i in range(int(params.width))) / rho_den)
        transport_yield = 0.0 if prev_centroid is None else float(abs(centroid - prev_centroid))
        prev_centroid = centroid

        total_power = e000_power + non_e000_power
        vacuum_drag = 0.0 if total_power <= eps else float(e000_power / total_power)
        rephase_load = float(rephase_l1_total / (max_non_e000_delta_per_node * float(params.width)))

        rows.append(
            {
                "tick": float(tick),
                "centroid_non_e000": float(centroid),
                "Y_t_transport_yield": float(transport_yield),
                "V_t_vacuum_drag": float(vacuum_drag),
                "R_t_rephasing_load": float(rephase_load),
            }
        )
        states = nxt

    warm = max(0, min(int(params.warmup_ticks), int(params.ticks) - 1))
    tail = rows[warm:]
    if not tail:
        tail = rows[-1:]
    mean_y = float(sum(float(r["Y_t_transport_yield"]) for r in tail) / float(len(tail)))
    mean_v = float(sum(float(r["V_t_vacuum_drag"]) for r in tail) / float(len(tail)))
    mean_r = float(sum(float(r["R_t_rephasing_load"]) for r in tail) / float(len(tail)))
    denom = max(mean_y, eps)
    m_eff = float((mean_r + float(params.lambda_vacuum_drag) * mean_v) / denom)

    return {
        "motif_id": motif_id,
        "summary": {
            "mean_Y_t_transport_yield_tail": mean_y,
            "mean_V_t_vacuum_drag_tail": mean_v,
            "mean_R_t_rephasing_load_tail": mean_r,
            "m_eff": m_eff,
            "rows_recorded": int(len(rows)),
            "warmup_ticks": int(warm),
        },
        "rows": rows,
    }


def build_payload(params: MassBasisParams | None = None) -> Dict[str, Any]:
    p = params if params is not None else MassBasisParams()
    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH

    neutrino_lane = _simulate_lane("su_vacuum_omega", p)
    electron_lane = _simulate_lane("left_spinor_electron_ideal", p)

    m_nu = float(neutrino_lane["summary"]["m_eff"])
    m_e = float(electron_lane["summary"]["m_eff"])
    eps = 1e-12
    m_e_in_nu_units = float(m_e / max(m_nu, eps))

    payload: Dict[str, Any] = {
        "schema_version": "mass_internal_neutrino_basis_v1",
        "claim_id": "MASS-BASIS-001",
        "mode": "simulation_first_structure_first",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(kernel_path),
        "kernel_profile": k.KERNEL_PROFILE,
        "projector_id": k.PROJECTOR_ID,
        "motif_source": MOTIF_SOURCE_REPO_PATH,
        "internal_basis_policy": {
            "basis_motif_id": "su_vacuum_omega",
            "basis_mass_unit": 1.0,
            "notes": [
                "This artifact defines an internal mass unit from the neutrino/vacuum motif lane.",
                "It is not an absolute physical-unit calibration claim.",
            ],
        },
        "params": {
            "ticks": int(p.ticks),
            "warmup_ticks": int(p.warmup_ticks),
            "width": int(p.width),
            "lambda_vacuum_drag": float(p.lambda_vacuum_drag),
            "source_op_cycle": [int(x) for x in p.source_op_cycle],
        },
        "lanes": {
            "neutrino_basis_lane": neutrino_lane,
            "electron_lane": electron_lane,
        },
        "derived": {
            "m_eff_neutrino_basis_raw": m_nu,
            "m_eff_electron_raw": m_e,
            "m_electron_in_neutrino_units": m_e_in_nu_units,
        },
        "checks": {
            "m_eff_neutrino_positive": bool(m_nu > 0.0),
            "m_eff_electron_positive": bool(m_e > 0.0),
            "electron_heavier_than_neutrino_internal": bool(m_e_in_nu_units > 1.0),
            "rows_match_ticks": bool(
                int(neutrino_lane["summary"]["rows_recorded"]) == int(p.ticks)
                and int(electron_lane["summary"]["rows_recorded"]) == int(p.ticks)
            ),
        },
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def _render_md(payload: Dict[str, Any]) -> str:
    p = payload["params"]
    d = payload["derived"]
    chk = payload["checks"]
    lines = [
        "# Mass Internal Neutrino Basis (v1)",
        "",
        "## Basis Policy",
        "",
        "- basis_motif_id: `su_vacuum_omega`",
        "- basis_mass_unit: `1.0`",
        "- scope: internal normalization only (no physical-unit calibration in this artifact)",
        "",
        "## Params",
        "",
        f"- ticks: `{p['ticks']}`",
        f"- warmup_ticks: `{p['warmup_ticks']}`",
        f"- width: `{p['width']}`",
        f"- lambda_vacuum_drag: `{p['lambda_vacuum_drag']}`",
        f"- source_op_cycle: `{p['source_op_cycle']}`",
        "",
        "## Derived Values",
        "",
        f"- m_eff_neutrino_basis_raw: `{d['m_eff_neutrino_basis_raw']}`",
        f"- m_eff_electron_raw: `{d['m_eff_electron_raw']}`",
        f"- m_electron_in_neutrino_units: `{d['m_electron_in_neutrino_units']}`",
        "",
        "## Checks",
        "",
    ]
    lines.extend([f"- {k}: `{v}`" for k, v in chk.items()])
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- This artifact is a structure-first internal-basis lane.",
            "- External mass calibration and SM closure require a separate anchor contract.",
        ]
    )
    return "\n".join(lines) + "\n"


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
    parser.add_argument("--ticks", type=int, default=MassBasisParams.ticks)
    parser.add_argument("--warmup", type=int, default=MassBasisParams.warmup_ticks)
    parser.add_argument("--width", type=int, default=MassBasisParams.width)
    parser.add_argument("--lambda-drag", type=float, default=MassBasisParams.lambda_vacuum_drag)
    parser.add_argument(
        "--source-op-cycle",
        type=int,
        nargs="*",
        default=list(MassBasisParams.source_op_cycle),
        help="source internal left-multiply op indices per tick cycle",
    )
    args = parser.parse_args()
    if int(args.ticks) < 4:
        raise ValueError("ticks must be >= 4")
    if int(args.width) < 8:
        raise ValueError("width must be >= 8")
    cycle = tuple(int(x) for x in args.source_op_cycle)
    if not cycle:
        raise ValueError("source-op-cycle must be non-empty")

    params = MassBasisParams(
        ticks=int(args.ticks),
        warmup_ticks=int(args.warmup),
        width=int(args.width),
        lambda_vacuum_drag=float(args.lambda_drag),
        source_op_cycle=cycle,
    )
    payload = build_payload(params)
    write_artifacts(payload)
    print(
        "mass_internal_neutrino_basis_v1: "
        f"m_e_over_m_nu={payload['derived']['m_electron_in_neutrino_units']:.10f}, "
        f"m_nu_raw={payload['derived']['m_eff_neutrino_basis_raw']:.10f}, "
        f"m_e_raw={payload['derived']['m_eff_electron_raw']:.10f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

