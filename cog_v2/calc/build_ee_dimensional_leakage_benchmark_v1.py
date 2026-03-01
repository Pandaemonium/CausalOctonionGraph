"""Dimensional benchmark for e-e mediator leakage (1D vs 2D vs 3D).

Purpose:
1) quantify off-axis leakage of mediator power,
2) test when a 1D lane is a valid approximation,
3) compare distance-response scaling across dimensional lanes.

All dynamics use canonical `kernel_projective_unity` updates with local-neighbor
message passing and deterministic source oscillators.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from cog_v2.python import kernel_projective_unity as k


ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "ee_dimensional_leakage_benchmark_v1.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "ee_dimensional_leakage_benchmark_v1.md"
OUT_VALIDITY_JSON = ROOT / "cog_v2" / "sources" / "ee_dimensional_1d_validity_report_v1.json"
OUT_VALIDITY_MD = ROOT / "cog_v2" / "sources" / "ee_dimensional_1d_validity_report_v1.md"
SCRIPT_REPO_PATH = "cog_v2/calc/build_ee_dimensional_leakage_benchmark_v1.py"
KERNEL_REPO_PATH = "cog_v2/python/kernel_projective_unity.py"

BASIS_LABELS: Tuple[str, ...] = tuple(k.BASIS_LABELS)
AVAILABLE_LANES: Tuple[str, ...] = ("line_1d", "strip_2d", "full_2d", "full_3d")


@dataclass(frozen=True)
class BenchmarkParams:
    ticks: int = 180
    warmup_ticks: int = 90
    width: int = 31
    strip_height: int = 5
    full_height: int = 15
    full_depth: int = 7
    separations: Tuple[int, ...] = (6, 10, 14, 18)
    thin_output_step: int = 4
    source_ops_left: Tuple[int, ...] = (7, 7, 7, 7)
    source_ops_right: Tuple[int, ...] = (7, 7, 7, 7)


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


def _abs2(z: k.GInt) -> int:
    return int(z.re * z.re + z.im * z.im)


def _basis_state(op_idx: int) -> k.CxO:
    vals = [k.ZERO_G] * 8
    vals[int(op_idx)] = k.ONE_G
    return (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6], vals[7])


def _left_mul_projected(op_idx: int, state: k.CxO) -> k.CxO:
    return k.project_cxo_to_unity(k.cxo_mul(_basis_state(int(op_idx)), state))


def _electron_motif_state() -> k.CxO:
    s = _state_from_sparse(
        {
            0: _coeff(0, -1),
            7: _coeff(-1, 0),
        }
    )
    return k.project_cxo_to_unity(s)


def _lattice_nodes(shape: Sequence[int]) -> List[Tuple[int, ...]]:
    return [tuple(int(x) for x in idx) for idx in itertools.product(*(range(int(d)) for d in shape))]


def _lattice_neighbors(shape: Sequence[int]) -> Dict[Tuple[int, ...], List[Tuple[int, ...]]]:
    dims = len(shape)
    out: Dict[Tuple[int, ...], List[Tuple[int, ...]]] = {}
    for node in _lattice_nodes(shape):
        row: List[Tuple[int, ...]] = []
        for ax in range(dims):
            if node[ax] - 1 >= 0:
                c = list(node)
                c[ax] -= 1
                row.append(tuple(c))
            if node[ax] + 1 < int(shape[ax]):
                c = list(node)
                c[ax] += 1
                row.append(tuple(c))
        out[node] = row
    return out


def _fit_power_law(distances: Sequence[float], responses: Sequence[float]) -> Dict[str, float | None]:
    rows = [(float(d), float(r)) for d, r in zip(distances, responses) if d > 0.0 and r > 0.0]
    if len(rows) < 2:
        return {"slope": None, "intercept": None, "exponent_n": None, "r2": None}
    xs = [math.log(d) for d, _ in rows]
    ys = [math.log(r) for _, r in rows]
    n = len(xs)
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    var_x = sum((x - x_mean) ** 2 for x in xs)
    if var_x == 0.0:
        return {"slope": None, "intercept": None, "exponent_n": None, "r2": None}
    cov = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    slope = cov / var_x
    intercept = y_mean - slope * x_mean
    ss_tot = sum((y - y_mean) ** 2 for y in ys)
    if ss_tot == 0.0:
        r2 = 1.0
    else:
        ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
        r2 = 1.0 - ss_res / ss_tot
    return {
        "slope": float(slope),
        "intercept": float(intercept),
        "exponent_n": float(-slope),
        "r2": float(r2),
    }


def _simulate_lane(
    *,
    lane_id: str,
    shape: Tuple[int, ...],
    separation: int,
    params: BenchmarkParams,
) -> Dict[str, Any]:
    thin_step = max(1, int(params.thin_output_step))
    dims = len(shape)
    if int(separation) % 2 != 0:
        raise ValueError("separation must be even for integer midpoint placement")
    if int(separation) >= int(shape[0]) - 2:
        raise ValueError(f"separation={separation} too large for x-width={shape[0]}")

    center = [int(s // 2) for s in shape]
    x_mid = int(center[0])
    x_left = int(x_mid - int(separation) // 2)
    x_right = int(x_mid + int(separation) // 2)
    left_src = tuple([x_left] + center[1:])
    right_src = tuple([x_right] + center[1:])
    midpoint = tuple([x_mid] + center[1:])
    axis_nodes = {
        tuple([x] + center[1:])
        for x in range(int(shape[0]))
    }

    nodes = _lattice_nodes(shape)
    neighbors = _lattice_neighbors(shape)

    left_state = _electron_motif_state()
    right_state = _electron_motif_state()
    states: Dict[Tuple[int, ...], k.CxO] = {n: k.cxo_one() for n in nodes}
    states[left_src] = left_state
    states[right_src] = right_state

    leakage_trace: List[float] = []
    midpoint_nonvac_trace: List[float] = []
    axis_imag_share_trace: List[float] = []
    rows: List[Dict[str, Any]] = []

    for tick in range(int(params.ticks)):
        lop = int(params.source_ops_left[tick % len(params.source_ops_left)])
        rop = int(params.source_ops_right[tick % len(params.source_ops_right)])
        left_state = _left_mul_projected(lop, left_state)
        right_state = _left_mul_projected(rop, right_state)

        old = dict(states)
        old[left_src] = left_state
        old[right_src] = right_state

        nxt: Dict[Tuple[int, ...], k.CxO] = {}
        for node in nodes:
            if node == left_src:
                nxt[node] = left_state
                continue
            if node == right_src:
                nxt[node] = right_state
                continue
            msgs = [old[nbr] for nbr in neighbors[node]]
            nxt[node] = k.update_rule(old[node], msgs)
        states = nxt

        total_nonvac = 0.0
        axis_nonvac = 0.0
        axis_imag_nonvac = 0.0
        for node in nodes:
            s = states[node]
            nonvac = float(sum(_abs2(s[i]) for i in range(1, 8)))
            total_nonvac += nonvac
            if node in axis_nodes:
                axis_nonvac += nonvac
                axis_imag_nonvac += float(sum((s[i].im * s[i].im) for i in range(1, 8)))
        off_axis_nonvac = float(total_nonvac - axis_nonvac)
        leakage_ratio = 0.0 if total_nonvac == 0.0 else float(off_axis_nonvac / total_nonvac)
        axis_imag_share = 0.0 if axis_nonvac == 0.0 else float(axis_imag_nonvac / axis_nonvac)

        s_mid = states[midpoint]
        midpoint_nonvac = float(sum(_abs2(s_mid[i]) for i in range(1, 8)))

        leakage_trace.append(leakage_ratio)
        midpoint_nonvac_trace.append(midpoint_nonvac)
        axis_imag_share_trace.append(axis_imag_share)

        is_last = bool(tick == int(params.ticks) - 1)
        keep_row = bool(tick % thin_step == 0 or is_last)
        if keep_row:
            rows.append(
                {
                    "tick": int(tick),
                    "leakage_ratio": float(leakage_ratio),
                    "axis_imag_share_nonvac": float(axis_imag_share),
                    "midpoint_nonvac_power": float(midpoint_nonvac),
                    "midpoint_state_vector": _serialize_state(s_mid),
                }
            )

    warm = max(0, min(int(params.warmup_ticks), int(params.ticks) - 1))
    tail_leakage = leakage_trace[warm:]
    tail_mid = midpoint_nonvac_trace[warm:]
    tail_axis_imag = axis_imag_share_trace[warm:]
    summary = {
        "mean_leakage_tail": float(sum(tail_leakage) / len(tail_leakage)) if tail_leakage else 0.0,
        "max_leakage_all": float(max(leakage_trace) if leakage_trace else 0.0),
        "mean_midpoint_nonvac_tail": float(sum(tail_mid) / len(tail_mid)) if tail_mid else 0.0,
        "max_midpoint_nonvac_all": float(max(midpoint_nonvac_trace) if midpoint_nonvac_trace else 0.0),
        "mean_axis_imag_share_tail": float(sum(tail_axis_imag) / len(tail_axis_imag)) if tail_axis_imag else 0.0,
        "recorded_row_count": int(len(rows)),
        "total_tick_count": int(params.ticks),
    }

    return {
        "lane_id": lane_id,
        "shape": [int(x) for x in shape],
        "dimension": int(dims),
        "separation": int(separation),
        "sources": {
            "left": [int(x) for x in left_src],
            "right": [int(x) for x in right_src],
            "midpoint": [int(x) for x in midpoint],
            "axis_center": [int(x) for x in center[1:]],
        },
        "summary": summary,
        "tick_rows": rows,
    }


def _build_validity_report(payload: Dict[str, Any]) -> Dict[str, Any]:
    ls = payload["lane_summary"]
    selected_lanes = set(str(x) for x in payload.get("selected_lanes", []))
    required = {"line_1d", "strip_2d", "full_2d", "full_3d"}
    missing = sorted(required - selected_lanes)

    def lane_leak(lane: str) -> float | None:
        row = ls.get(lane)
        if row is None:
            return None
        return float(row["mean_leakage_across_separations"])

    one_d = lane_leak("line_1d")
    strip = lane_leak("strip_2d")
    full2 = lane_leak("full_2d")
    full3 = lane_leak("full_3d")

    thresholds = {
        "one_d_zero_leakage_eps": 1e-12,
        "max_strip_leak_for_1d_valid": 0.05,
        "max_full2_leak_for_1d_valid": 0.05,
        "max_full3_leak_for_1d_valid": 0.05,
    }
    if missing:
        return {
            "schema_version": "ee_dimensional_1d_validity_report_v1",
            "from_schema": payload["schema_version"],
            "from_replay_hash": payload["replay_hash"],
            "lane_leakage_means": {
                "line_1d": one_d,
                "strip_2d": strip,
                "full_2d": full2,
                "full_3d": full3,
            },
            "thresholds": thresholds,
            "one_d_proxy_valid": None,
            "decision": "NOT_EVALUABLE",
            "missing_lanes": missing,
            "notes": [
                "1D validity requires all four lanes: line_1d, strip_2d, full_2d, full_3d.",
                "Run with full lane set for a PASS/FAIL validity decision.",
            ],
        }

    one_d_valid = bool(
        abs(float(one_d)) <= float(thresholds["one_d_zero_leakage_eps"])
        and float(strip) <= float(thresholds["max_strip_leak_for_1d_valid"])
        and float(full2) <= float(thresholds["max_full2_leak_for_1d_valid"])
        and float(full3) <= float(thresholds["max_full3_leak_for_1d_valid"])
    )

    return {
        "schema_version": "ee_dimensional_1d_validity_report_v1",
        "from_schema": payload["schema_version"],
        "from_replay_hash": payload["replay_hash"],
        "lane_leakage_means": {
            "line_1d": float(one_d),
            "strip_2d": float(strip),
            "full_2d": float(full2),
            "full_3d": float(full3),
        },
        "thresholds": thresholds,
        "one_d_proxy_valid": one_d_valid,
        "decision": "PASS" if one_d_valid else "FAIL",
        "notes": [
            "1D proxy is valid only if higher-dimensional lanes remain near-zero leakage.",
            "If 2D/3D leakage is nontrivial, 1D over-constrains mediator transport.",
        ],
    }


def build_payload(params: BenchmarkParams | None = None, lanes: Sequence[str] | None = None) -> Dict[str, Any]:
    p = params if params is not None else BenchmarkParams()
    script_path = ROOT / SCRIPT_REPO_PATH
    kernel_path = ROOT / KERNEL_REPO_PATH

    lane_shapes_map: Dict[str, Tuple[int, ...]] = {
        "line_1d": (int(p.width),),
        "strip_2d": (int(p.width), int(p.strip_height)),
        "full_2d": (int(p.width), int(p.full_height)),
        "full_3d": (int(p.width), int(p.full_height), int(p.full_depth)),
    }
    selected_lanes = list(lanes) if lanes else list(AVAILABLE_LANES)
    unknown = [x for x in selected_lanes if x not in lane_shapes_map]
    if unknown:
        raise ValueError(f"unknown lanes requested: {unknown}")
    lane_shapes: List[Tuple[str, Tuple[int, ...]]] = [(lid, lane_shapes_map[lid]) for lid in selected_lanes]

    lane_results: List[Dict[str, Any]] = []
    lane_sweep: Dict[str, Dict[str, List[float]]] = {}
    for lane_id, shape in lane_shapes:
        sep_rows: List[Dict[str, Any]] = []
        dvals: List[float] = []
        ivals: List[float] = []
        lvals: List[float] = []
        for d in p.separations:
            row = _simulate_lane(lane_id=lane_id, shape=shape, separation=int(d), params=p)
            sep_rows.append(row)
            dvals.append(float(d))
            ivals.append(float(row["summary"]["mean_midpoint_nonvac_tail"]))
            lvals.append(float(row["summary"]["mean_leakage_tail"]))
        lane_results.extend(sep_rows)
        lane_sweep[lane_id] = {
            "separations": dvals,
            "interaction_tail_mean": ivals,
            "leakage_tail_mean": lvals,
        }

    lane_summary: Dict[str, Any] = {}
    for lane_id, sweep in lane_sweep.items():
        fit = _fit_power_law(sweep["separations"], sweep["interaction_tail_mean"])
        leak_mean = float(sum(sweep["leakage_tail_mean"]) / len(sweep["leakage_tail_mean"]))
        lane_summary[lane_id] = {
            "mean_leakage_across_separations": leak_mean,
            "power_law_fit": fit,
        }

    def _lane_leak(lane: str) -> float | None:
        row = lane_summary.get(lane)
        return None if row is None else float(row["mean_leakage_across_separations"])

    one_d_leak = _lane_leak("line_1d")
    strip_leak = _lane_leak("strip_2d")
    full2_leak = _lane_leak("full_2d")
    full3_leak = _lane_leak("full_3d")

    payload: Dict[str, Any] = {
        "schema_version": "ee_dimensional_leakage_benchmark_v1",
        "claim_id": "EE-DIM-LEAK-001",
        "mode": "simulation_first_structure_first",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "kernel_module": KERNEL_REPO_PATH,
        "kernel_module_sha256": _sha_file(kernel_path),
        "kernel_profile": k.KERNEL_PROFILE,
        "projector_id": k.PROJECTOR_ID,
        "selected_lanes": list(selected_lanes),
        "params": {
            "ticks": int(p.ticks),
            "warmup_ticks": int(p.warmup_ticks),
            "width": int(p.width),
            "strip_height": int(p.strip_height),
            "full_height": int(p.full_height),
            "full_depth": int(p.full_depth),
            "separations": [int(x) for x in p.separations],
            "thin_output_step": int(max(1, int(p.thin_output_step))),
        },
        "lanes": lane_results,
        "lane_summary": lane_summary,
        "checks": {
            "one_d_zero_leakage": None if one_d_leak is None else bool(abs(one_d_leak) < 1e-12),
            "strip_has_nonzero_leakage": None if strip_leak is None else bool(strip_leak > 0.0),
            "full2_has_nonzero_leakage": None if full2_leak is None else bool(full2_leak > 0.0),
            "full3_has_nonzero_leakage": None if full3_leak is None else bool(full3_leak > 0.0),
            "full2_leakage_ge_strip": None if (full2_leak is None or strip_leak is None) else bool(full2_leak >= strip_leak),
            "full3_leakage_ge_full2": None if (full3_leak is None or full2_leak is None) else bool(full3_leak >= full2_leak),
        },
    }
    payload["replay_hash"] = _sha_payload(payload)
    payload["one_d_validity_report"] = _build_validity_report(payload)
    return payload


def _render_md(payload: Dict[str, Any]) -> str:
    p = payload["params"]
    ls = payload["lane_summary"]
    chk = payload["checks"]
    vr = payload["one_d_validity_report"]
    lines = [
        "# EE Dimensional Leakage Benchmark (v1)",
        "",
        "## Purpose",
        "",
        "Compare 1D vs 2D strip vs 2D full vs 3D full lanes for off-axis leakage and distance-response scaling.",
        "",
        "## Params",
        "",
        f"- ticks: `{p['ticks']}`",
        f"- warmup_ticks: `{p['warmup_ticks']}`",
        f"- width: `{p['width']}`",
        f"- strip_height: `{p['strip_height']}`",
        f"- full_height: `{p['full_height']}`",
        f"- full_depth: `{p['full_depth']}`",
        f"- separations: `{p['separations']}`",
        f"- thin_output_step: `{p['thin_output_step']}`",
        "",
        "## Lane Summary",
        "",
    ]
    for lane_id in payload.get("selected_lanes", []):
        row = ls[lane_id]
        fit = row["power_law_fit"]
        lines.extend(
            [
                f"### {lane_id}",
                f"- mean_leakage_across_separations: `{row['mean_leakage_across_separations']}`",
                f"- fitted_exponent_n: `{fit['exponent_n']}`",
                f"- fit_r2: `{fit['r2']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Checks",
            "",
            *(f"- {k}: `{v}`" for k, v in chk.items()),
            "",
            "## 1D Validity Report",
            "",
            f"- decision: `{vr['decision']}`",
            f"- one_d_proxy_valid: `{vr['one_d_proxy_valid']}`",
            f"- lane_leakage_means: `{vr['lane_leakage_means']}`",
            f"- missing_lanes: `{vr.get('missing_lanes', [])}`",
            "",
            "## Interpretation",
            "",
            "- If 2D/3D leakage is nontrivial, strict 1D isolation is not physically generic.",
            "- If 3D leakage >= 2D leakage, surrounding volume materially changes mediator transport.",
        ]
    )
    return "\n".join(lines) + "\n"


def _render_validity_md(report: Dict[str, Any]) -> str:
    lines = [
        "# EE 1D Validity Report (v1)",
        "",
        f"- from_schema: `{report['from_schema']}`",
        f"- from_replay_hash: `{report['from_replay_hash']}`",
        f"- decision: `{report['decision']}`",
        f"- one_d_proxy_valid: `{report['one_d_proxy_valid']}`",
        f"- missing_lanes: `{report.get('missing_lanes', [])}`",
        "",
        "## Leakage Means",
        "",
    ]
    for lane, v in report["lane_leakage_means"].items():
        lines.append(f"- {lane}: `{v}`")
    lines.extend(
        [
            "",
            "## Thresholds",
            "",
            *(f"- {k}: `{v}`" for k, v in report["thresholds"].items()),
            "",
            "## Notes",
            "",
            *(f"- {x}" for x in report["notes"]),
        ]
    )
    return "\n".join(lines) + "\n"


def write_artifacts(
    payload: Dict[str, Any],
    json_paths: Sequence[Path] = (OUT_JSON,),
    md_paths: Sequence[Path] = (OUT_MD,),
    validity_json_paths: Sequence[Path] = (OUT_VALIDITY_JSON,),
    validity_md_paths: Sequence[Path] = (OUT_VALIDITY_MD,),
) -> None:
    for path in json_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = _render_md(payload)
    for path in md_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(md, encoding="utf-8")

    report = payload["one_d_validity_report"]
    for path in validity_json_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_md = _render_validity_md(report)
    for path in validity_md_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report_md, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticks", type=int, default=BenchmarkParams.ticks)
    parser.add_argument("--warmup", type=int, default=BenchmarkParams.warmup_ticks)
    parser.add_argument("--width", type=int, default=BenchmarkParams.width)
    parser.add_argument("--strip-height", type=int, default=BenchmarkParams.strip_height)
    parser.add_argument("--full-height", type=int, default=BenchmarkParams.full_height)
    parser.add_argument("--full-depth", type=int, default=BenchmarkParams.full_depth)
    parser.add_argument("--thin-output", type=int, default=BenchmarkParams.thin_output_step)
    parser.add_argument(
        "--lanes",
        type=str,
        nargs="*",
        default=list(AVAILABLE_LANES),
        help="subset of lanes to run: line_1d strip_2d full_2d full_3d",
    )
    parser.add_argument(
        "--separations",
        type=int,
        nargs="*",
        default=list(BenchmarkParams.separations),
        help="even integer separations",
    )
    args = parser.parse_args()
    seps = tuple(int(x) for x in args.separations)
    if not seps:
        raise ValueError("at least one separation is required")
    if any(int(s) <= 0 or int(s) % 2 != 0 for s in seps):
        raise ValueError("all separations must be positive even integers")
    if int(args.width) < 8:
        raise ValueError("width must be >= 8")
    if int(args.strip_height) < 1 or int(args.full_height) < 1 or int(args.full_depth) < 1:
        raise ValueError("heights/depth must be >= 1")
    lanes = [str(x) for x in args.lanes]
    if not lanes:
        raise ValueError("at least one lane must be selected")
    bad = [x for x in lanes if x not in AVAILABLE_LANES]
    if bad:
        raise ValueError(f"unknown lanes: {bad}")

    params = BenchmarkParams(
        ticks=int(args.ticks),
        warmup_ticks=int(args.warmup),
        width=int(args.width),
        strip_height=int(args.strip_height),
        full_height=int(args.full_height),
        full_depth=int(args.full_depth),
        separations=seps,
        thin_output_step=max(1, int(args.thin_output)),
    )
    payload = build_payload(params, lanes=lanes)
    write_artifacts(payload)
    ls = payload["lane_summary"]
    l1 = ls.get("line_1d", {}).get("mean_leakage_across_separations")
    l2s = ls.get("strip_2d", {}).get("mean_leakage_across_separations")
    l2 = ls.get("full_2d", {}).get("mean_leakage_across_separations")
    l3 = ls.get("full_3d", {}).get("mean_leakage_across_separations")
    print(
        "ee_dimensional_leakage_benchmark_v1: "
        f"lanes={payload['selected_lanes']}, "
        f"1d_leak={l1}, strip_leak={l2s}, full2_leak={l2}, full3_leak={l3}, "
        f"one_d_valid={payload['one_d_validity_report']['one_d_proxy_valid']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
