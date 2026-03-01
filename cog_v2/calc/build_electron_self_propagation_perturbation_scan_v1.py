"""3D perturbation scan for coherent self-propagation of an electron motif.

Goal:
1) start from a stable electron motif in vacuum background,
2) apply one-shot perturbations at tick 0,
3) identify perturbations that produce directional, coherent propagation.

No explicit kinetic-energy variable is introduced. "Excitation" is purely a
microstate perturbation under canonical projector dynamics.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from calc.xor_scenario_loader import canonical_motif_state_map
from cog_v2.python import kernel_projective_unity as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "electron_self_propagation_perturbation_scan_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "electron_self_propagation_perturbation_scan_v1.md"
SCRIPT_REPO_PATH = "cog_v2/calc/build_electron_self_propagation_perturbation_scan_v1.py"
KERNEL_REPO_PATH = "cog_v2/python/kernel_projective_unity.py"
MOTIF_SOURCE_REPO_PATH = "calc/xor_scenario_loader.py::canonical_motif_state_map"


@dataclass(frozen=True)
class ScanParams:
    ticks: int = 24
    size_xyz: int = 15
    warmup_ticks: int = 2
    directionality_threshold: float = 0.60
    net_displacement_threshold: float = 1.0
    min_speed_threshold: float = 0.08


@dataclass(frozen=True)
class PerturbCase:
    case_id: str
    center_op_idx: int | None
    neighbor_seed_op_idx: int | None
    hand: str


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _abs2(z: k.GInt) -> int:
    return int(z.re * z.re + z.im * z.im)


def _to_cxo(state_gi: Sequence[Tuple[int, int]]) -> k.CxO:
    vals = [k.GInt(int(re), int(im)) for re, im in state_gi]
    return k.project_cxo_to_unity((vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7]))


def _basis_state(op_idx: int) -> k.CxO:
    vals = [k.ZERO_G] * 8
    vals[int(op_idx)] = k.ONE_G
    return (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7])


def _left_mul_projected(op_idx: int, state: k.CxO) -> k.CxO:
    return k.project_cxo_to_unity(k.cxo_mul(_basis_state(int(op_idx)), state))


def _right_mul_projected(op_idx: int, state: k.CxO) -> k.CxO:
    return k.project_cxo_to_unity(k.cxo_mul(state, _basis_state(int(op_idx))))


def _neighbors_3d(size_xyz: int) -> Tuple[List[Tuple[int, int, int]], Dict[Tuple[int, int, int], List[Tuple[int, int, int]]]]:
    n = int(size_xyz)
    nodes = [tuple(int(x) for x in p) for p in itertools.product(range(n), repeat=3)]
    out: Dict[Tuple[int, int, int], List[Tuple[int, int, int]]] = {}
    for x, y, z in nodes:
        row: List[Tuple[int, int, int]] = []
        if x - 1 >= 0:
            row.append((x - 1, y, z))
        if x + 1 < n:
            row.append((x + 1, y, z))
        if y - 1 >= 0:
            row.append((x, y - 1, z))
        if y + 1 < n:
            row.append((x, y + 1, z))
        if z - 1 >= 0:
            row.append((x, y, z - 1))
        if z + 1 < n:
            row.append((x, y, z + 1))
        out[(x, y, z)] = row
    return nodes, out


def _build_cases() -> List[PerturbCase]:
    cases: List[PerturbCase] = [PerturbCase("control_none", None, None, "left")]
    for op_idx in range(1, 8):
        cases.append(PerturbCase(f"center_left_e{op_idx:03b}", op_idx, None, "left"))
    for op_idx in range(1, 8):
        cases.append(PerturbCase(f"center_neighbor_px_left_e{op_idx:03b}", op_idx, op_idx, "left"))
    return cases


def _simulate_case(
    *,
    case: PerturbCase,
    params: ScanParams,
    electron_state: k.CxO,
    nodes: List[Tuple[int, int, int]],
    neighbors: Dict[Tuple[int, int, int], List[Tuple[int, int, int]]],
) -> Dict[str, Any]:
    n = int(params.size_xyz)
    center = (n // 2, n // 2, n // 2)
    neighbor_px = (min(n - 1, center[0] + 1), center[1], center[2])
    node_to_idx = {node: i for i, node in enumerate(nodes)}

    world: List[k.CxO] = [k.cxo_one() for _ in nodes]
    world[node_to_idx[center]] = electron_state

    if case.neighbor_seed_op_idx is not None:
        world[node_to_idx[neighbor_px]] = _basis_state(int(case.neighbor_seed_op_idx))

    rows: List[Dict[str, float]] = []
    path_len = 0.0
    prev_centroid: Tuple[float, float, float] | None = None
    start_centroid: Tuple[float, float, float] | None = None
    prev_non_e000 = 0.0

    for tick in range(int(params.ticks)):
        if tick == 0 and case.center_op_idx is not None:
            cidx = node_to_idx[center]
            if case.hand == "left":
                world[cidx] = _left_mul_projected(int(case.center_op_idx), world[cidx])
            else:
                world[cidx] = _right_mul_projected(int(case.center_op_idx), world[cidx])

        old = list(world)
        nxt: List[k.CxO] = [k.cxo_one() for _ in nodes]
        for node in nodes:
            i = node_to_idx[node]
            msgs = [old[node_to_idx[q]] for q in neighbors[node]]
            nxt[i] = k.update_rule(old[i], msgs)

        rho_non_e000: List[float] = []
        e000 = 0.0
        non = 0.0
        for s in nxt:
            nv = float(sum(_abs2(s[j]) for j in range(1, 8)))
            rho_non_e000.append(nv)
            non += nv
            e000 += float(_abs2(s[0]))
        den = float(sum(rho_non_e000))
        if den <= 0.0:
            centroid = (0.0, 0.0, 0.0)
        else:
            centroid = (
                float(sum(float(node[0]) * rho_non_e000[node_to_idx[node]] for node in nodes) / den),
                float(sum(float(node[1]) * rho_non_e000[node_to_idx[node]] for node in nodes) / den),
                float(sum(float(node[2]) * rho_non_e000[node_to_idx[node]] for node in nodes) / den),
            )
        if start_centroid is None:
            start_centroid = centroid
        step_norm = 0.0
        if prev_centroid is not None:
            dx = centroid[0] - prev_centroid[0]
            dy = centroid[1] - prev_centroid[1]
            dz = centroid[2] - prev_centroid[2]
            step_norm = float(math.sqrt(dx * dx + dy * dy + dz * dz))
            path_len += step_norm
        prev_centroid = centroid

        total = e000 + non
        e000_share = 0.0 if total <= 0.0 else float(e000 / total)
        delta_non = float(non - prev_non_e000) if tick > 0 else 0.0
        prev_non_e000 = non
        rows.append(
            {
                "tick": float(tick),
                "centroid_x": float(centroid[0]),
                "centroid_y": float(centroid[1]),
                "centroid_z": float(centroid[2]),
                "step_displacement": float(step_norm),
                "global_e000_share": float(e000_share),
                "global_non_e000_power": float(non),
                "delta_non_e000_power": float(delta_non),
            }
        )
        world = nxt

    if start_centroid is None or prev_centroid is None:
        net = 0.0
        directionality = 0.0
    else:
        ndx = prev_centroid[0] - start_centroid[0]
        ndy = prev_centroid[1] - start_centroid[1]
        ndz = prev_centroid[2] - start_centroid[2]
        net = float(math.sqrt(ndx * ndx + ndy * ndy + ndz * ndz))
        directionality = 0.0 if path_len <= 1e-12 else float(net / path_len)
    mean_speed = float(path_len / max(1, int(params.ticks) - 1))
    warm = max(0, min(int(params.warmup_ticks), int(params.ticks) - 1))
    tail = rows[warm:] if rows else []
    mean_delta_non_tail = float(sum(float(r["delta_non_e000_power"]) for r in tail) / len(tail)) if tail else 0.0
    mean_e000_tail = float(sum(float(r["global_e000_share"]) for r in tail) / len(tail)) if tail else 0.0
    coherent = bool(
        directionality >= float(params.directionality_threshold)
        and net >= float(params.net_displacement_threshold)
        and mean_speed >= float(params.min_speed_threshold)
    )
    coherence_score = float(directionality * net)

    return {
        "case_id": case.case_id,
        "center_op_idx": case.center_op_idx,
        "neighbor_seed_op_idx": case.neighbor_seed_op_idx,
        "hand": case.hand,
        "summary": {
            "net_displacement": float(net),
            "path_length": float(path_len),
            "directionality": float(directionality),
            "mean_speed": float(mean_speed),
            "coherence_score": float(coherence_score),
            "mean_e000_share_tail": float(mean_e000_tail),
            "mean_delta_non_e000_power_tail": float(mean_delta_non_tail),
            "self_propagating_coherent": coherent,
            "rows_recorded": int(len(rows)),
        },
        "rows": rows,
    }


def build_payload(params: ScanParams | None = None) -> Dict[str, Any]:
    p = params if params is not None else ScanParams()
    if int(p.size_xyz) < 7:
        raise ValueError("size_xyz must be >= 7")
    if int(p.ticks) < 4:
        raise ValueError("ticks must be >= 4")

    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH
    motifs = canonical_motif_state_map()
    electron = _to_cxo(motifs["left_spinor_electron_ideal"])

    nodes, neighbors = _neighbors_3d(int(p.size_xyz))
    cases = _build_cases()
    case_rows = [_simulate_case(case=c, params=p, electron_state=electron, nodes=nodes, neighbors=neighbors) for c in cases]

    ranked = sorted(case_rows, key=lambda r: float(r["summary"]["coherence_score"]), reverse=True)
    coherent_ids = [r["case_id"] for r in ranked if bool(r["summary"]["self_propagating_coherent"])]
    control = next(r for r in ranked if r["case_id"] == "control_none")
    best = ranked[0]
    case_map = {r["case_id"]: r for r in case_rows}

    directional_core_ids = [f"center_left_e{op:03b}" for op in range(1, 7)]
    core_scores = [float(case_map[cid]["summary"]["coherence_score"]) for cid in directional_core_ids if cid in case_map]
    core_end = [
        (
            float(case_map[cid]["rows"][-1]["centroid_x"]),
            float(case_map[cid]["rows"][-1]["centroid_y"]),
            float(case_map[cid]["rows"][-1]["centroid_z"]),
        )
        for cid in directional_core_ids
        if cid in case_map and case_map[cid]["rows"]
    ]
    core_score_span = (max(core_scores) - min(core_scores)) if core_scores else 0.0
    all_to_origin = all(abs(x) < 1e-9 and abs(y) < 1e-9 and abs(z) < 1e-9 for x, y, z in core_end) if core_end else False
    likely_fold_order_anisotropy = bool(core_score_span < 1e-9 and all_to_origin and len(core_end) >= 4)

    payload: Dict[str, Any] = {
        "schema_version": "electron_self_propagation_perturbation_scan_v1",
        "claim_id": "ELECTRON-PROP-001",
        "mode": "simulation_first_structure_first",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(kernel_path),
        "kernel_profile": k.KERNEL_PROFILE,
        "projector_id": k.PROJECTOR_ID,
        "motif_source": MOTIF_SOURCE_REPO_PATH,
        "motif_id": "left_spinor_electron_ideal",
        "params": {
            "ticks": int(p.ticks),
            "size_xyz": int(p.size_xyz),
            "warmup_ticks": int(p.warmup_ticks),
            "directionality_threshold": float(p.directionality_threshold),
            "net_displacement_threshold": float(p.net_displacement_threshold),
            "min_speed_threshold": float(p.min_speed_threshold),
        },
        "cases": case_rows,
        "ranked_case_ids": [r["case_id"] for r in ranked],
        "coherent_case_ids": coherent_ids,
        "checks": {
            "has_control_case": True,
            "best_case_beats_control_coherence": bool(
                float(best["summary"]["coherence_score"]) >= float(control["summary"]["coherence_score"])
            ),
            "rows_match_ticks_all_cases": bool(
                all(int(r["summary"]["rows_recorded"]) == int(p.ticks) for r in case_rows)
            ),
            "likely_fold_order_anisotropy": likely_fold_order_anisotropy,
        },
        "diagnostics": {
            "core_directional_case_ids": directional_core_ids,
            "core_directional_score_span": float(core_score_span),
            "core_directional_all_end_at_origin": bool(all_to_origin),
            "interpretation": (
                "If true, coherent drift may be dominated by non-commutative parent-fold order bias "
                "instead of physically distinct perturbation content."
            ),
        },
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def _render_md(payload: Dict[str, Any]) -> str:
    p = payload["params"]
    lines = [
        "# Electron Self-Propagation Perturbation Scan (v1)",
        "",
        "## Goal",
        "",
        "Determine which one-shot perturbations of a stable electron motif produce coherent self-propagation in 3D vacuum background.",
        "",
        "## Params",
        "",
        f"- ticks: `{p['ticks']}`",
        f"- size_xyz: `{p['size_xyz']}`",
        f"- warmup_ticks: `{p['warmup_ticks']}`",
        f"- directionality_threshold: `{p['directionality_threshold']}`",
        f"- net_displacement_threshold: `{p['net_displacement_threshold']}`",
        f"- min_speed_threshold: `{p['min_speed_threshold']}`",
        "",
        "## Ranked Cases (Top 12)",
        "",
        "| rank | case_id | coherence_score | directionality | net_displacement | mean_speed | coherent |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    cases = {r["case_id"]: r for r in payload["cases"]}
    for rank, cid in enumerate(payload["ranked_case_ids"][:12], start=1):
        s = cases[cid]["summary"]
        lines.append(
            f"| {rank} | `{cid}` | {s['coherence_score']:.6f} | {s['directionality']:.6f} | {s['net_displacement']:.6f} | {s['mean_speed']:.6f} | {s['self_propagating_coherent']} |"
        )
    lines.extend(["", "## Coherent Cases", ""])
    coherent_ids = list(payload["coherent_case_ids"])
    if coherent_ids:
        lines.extend([f"- `{cid}`" for cid in coherent_ids])
    else:
        lines.append("- none")
    lines.extend(["", "## Checks", ""])
    lines.extend([f"- {k}: `{v}`" for k, v in payload["checks"].items()])
    d = payload.get("diagnostics", {})
    lines.extend(
        [
            "",
            "## Diagnostics",
            "",
            f"- core_directional_score_span: `{d.get('core_directional_score_span')}`",
            f"- core_directional_all_end_at_origin: `{d.get('core_directional_all_end_at_origin')}`",
            f"- interpretation: {d.get('interpretation', '')}",
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
    parser.add_argument("--ticks", type=int, default=ScanParams.ticks)
    parser.add_argument("--size", type=int, default=ScanParams.size_xyz)
    parser.add_argument("--warmup", type=int, default=ScanParams.warmup_ticks)
    parser.add_argument("--dir-threshold", type=float, default=ScanParams.directionality_threshold)
    parser.add_argument("--disp-threshold", type=float, default=ScanParams.net_displacement_threshold)
    parser.add_argument("--speed-threshold", type=float, default=ScanParams.min_speed_threshold)
    args = parser.parse_args()

    params = ScanParams(
        ticks=int(args.ticks),
        size_xyz=int(args.size),
        warmup_ticks=int(args.warmup),
        directionality_threshold=float(args.dir_threshold),
        net_displacement_threshold=float(args.disp_threshold),
        min_speed_threshold=float(args.speed_threshold),
    )
    payload = build_payload(params)
    write_artifacts(payload)
    best = payload["ranked_case_ids"][0]
    cases = {r["case_id"]: r for r in payload["cases"]}
    bs = cases[best]["summary"]
    print(
        "electron_self_propagation_perturbation_scan_v1: "
        f"best={best}, score={bs['coherence_score']:.6f}, "
        f"dir={bs['directionality']:.6f}, net_disp={bs['net_displacement']:.6f}, "
        f"coherent_count={len(payload['coherent_case_ids'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
