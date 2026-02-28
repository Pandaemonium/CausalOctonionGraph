"""Build continuum-bridge diagnostics for THETA-001 in COG v2.

This artifact is a bridge diagnostic, not full value-closure proof.
It quantifies finite-size behavior of the discrete CP-odd residual lanes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from cog_v2.calc.build_theta001_bridge_closure_v2 import (
    CASE_DEFINITIONS,
    CKM_PHASES,
    CKM_TRANSPORT_PERIODS,
    PHASE_SHIFTS,
    WEAK_KICKS,
)
from cog_v2.calc.build_triplet_coherence_e000_leakage_v1 import (
    build_payload as build_triplet_payload,
)
from cog_v2.calc.build_triplet_coherence_e000_robustness_v1 import (
    build_payload as build_triplet_robustness_payload,
)
from cog_v2.calc.theta001_cp_invariant_v2 import (
    weak_leakage_ckm_like_strong_residual,
    weak_leakage_strong_residual,
)

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "theta001_continuum_bridge_v2.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "theta001_continuum_bridge_v2.md"

SCRIPT_REPO_PATH = "cog_v2/calc/build_theta001_continuum_bridge_v2.py"
BRIDGE_ARTIFACT_REPO_PATH = "cog_v2/sources/theta001_bridge_closure_v2.json"
TRIPLET_ARTIFACT_REPO_PATH = "cog_v2/sources/triplet_coherence_e000_leakage_v1.json"
TRIPLET_ROBUSTNESS_ARTIFACT_REPO_PATH = "cog_v2/sources/triplet_coherence_e000_robustness_v1.json"


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _to_repo_path(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def _iter_cases() -> List[Tuple[str, Tuple[int, ...], Tuple[int, ...]]]:
    rows: List[Tuple[str, Tuple[int, ...], Tuple[int, ...]]] = []
    for row in CASE_DEFINITIONS:
        rows.append(
            (
                str(row["case_id"]),
                tuple(int(x) for x in row["initial_state"]),
                tuple(int(x) for x in row["op_sequence"]),
            )
        )
    return rows


def _build_discrete_correction_envelope(
    triplet_payload: Dict[str, Any],
    triplet_robustness_payload: Dict[str, Any],
) -> Dict[str, Any]:
    dtf = triplet_payload.get("discrete_transfer_function", {}) if isinstance(triplet_payload, dict) else {}
    coherent = dtf.get("coherent_triplet_v1", {}) if isinstance(dtf, dict) else {}
    broken = dtf.get("broken_off_cycle_v1", {}) if isinstance(dtf, dict) else {}
    robust = (
        triplet_robustness_payload.get("discrete_correction_envelope_robustness", {})
        if isinstance(triplet_robustness_payload, dict)
        else {}
    )
    coherent_onset = coherent.get("correction_onset_d_E")
    broken_onset = broken.get("correction_onset_d_E")

    coherent_near_first = float(coherent.get("near_field_first_order_fraction_E", 0.0))
    coherent_near_high = float(coherent.get("near_field_high_order_fraction_E", 0.0))
    coherent_far_high = float(coherent.get("far_field_high_order_fraction_E", 0.0))
    broken_near_high = float(broken.get("near_field_high_order_fraction_E", 0.0))

    near_mode = "first_order_dominant" if coherent_near_first >= 0.6 else "mixed"
    correction_mode = "higher_order_corrections_active" if coherent_far_high > coherent_near_high else "weak_correction_growth"

    robust_lane_ready = bool(robust.get("robustness_lane_ready", False))
    base_lane_ready = (
        coherent_near_first >= 0.6
        and coherent_far_high > coherent_near_high
        and coherent_onset is not None
        and broken_onset is not None
    )

    return {
        "envelope_id": "theta_discrete_correction_envelope_v1",
        "distance_axis_id": "graph_distance_tick_index_v1",
        "domain": "nonnegative_integers",
        "source_model_id": str(dtf.get("model_id", "")),
        "near_field_mode": near_mode,
        "correction_mode": correction_mode,
        "coherent_near_first_order_fraction_E": coherent_near_first,
        "coherent_near_high_order_fraction_E": coherent_near_high,
        "coherent_far_high_order_fraction_E": coherent_far_high,
        "broken_near_high_order_fraction_E": broken_near_high,
        "coherent_correction_onset_d_E": coherent_onset,
        "broken_correction_onset_d_E": broken_onset,
        "correction_onset_defined": coherent_onset is not None and broken_onset is not None,
        "base_correction_lane_ready": bool(base_lane_ready),
        "robustness_envelope_id": str(robust.get("envelope_id", "")),
        "robustness_lane_ready": robust_lane_ready,
        "robust_coherent_near_first_order_fraction_mean_E": float(
            robust.get("coherent_near_first_order_fraction_mean_E", 0.0)
        ),
        "robust_coherent_far_high_order_fraction_mean_E": float(
            robust.get("coherent_far_high_order_fraction_mean_E", 0.0)
        ),
        "robust_coherent_near_high_order_fraction_mean_E": float(
            robust.get("coherent_near_high_order_fraction_mean_E", 0.0)
        ),
        "correction_lane_ready": bool(base_lane_ready and robust_lane_ready),
    }


def _depth_schedule(max_depth: int) -> List[int]:
    baseline = [12, 16, 20, 24, 32, 40, 48, 56, 64, 72, 84, 96]
    out = [d for d in baseline if d <= max_depth]
    if max_depth not in out:
        out.append(max_depth)
    return sorted(set(out))


def _metrics(values: Sequence[float]) -> Dict[str, float]:
    n = len(values)
    if n == 0:
        return {
            "n": 0.0,
            "mean": 0.0,
            "mean_abs": 0.0,
            "max_abs": 0.0,
            "rms": 0.0,
            "std": 0.0,
            "stderr": 0.0,
            "ci95_half_width": 0.0,
            "ci95_low": 0.0,
            "ci95_high": 0.0,
        }
    n_f = float(n)
    mean = sum(values) / n_f
    abs_vals = [abs(v) for v in values]
    mean_abs = sum(abs_vals) / n_f
    max_abs = max(abs_vals)
    rms = math.sqrt(sum(v * v for v in values) / n_f)
    if n > 1:
        var = sum((v - mean) ** 2 for v in values) / float(n - 1)
        std = math.sqrt(var)
    else:
        std = 0.0
    stderr = std / math.sqrt(n_f) if n > 0 else 0.0
    ci_half = 1.96 * stderr
    return {
        "n": n_f,
        "mean": float(mean),
        "mean_abs": float(mean_abs),
        "max_abs": float(max_abs),
        "rms": float(rms),
        "std": float(std),
        "stderr": float(stderr),
        "ci95_half_width": float(ci_half),
        "ci95_low": float(mean - ci_half),
        "ci95_high": float(mean + ci_half),
    }


def _linear_fit(xs: Sequence[float], ys: Sequence[float]) -> Dict[str, float]:
    n = len(xs)
    if n == 0 or len(ys) != n:
        return {"slope": 0.0, "intercept": 0.0, "r2": 0.0}
    x_mean = sum(xs) / float(n)
    y_mean = sum(ys) / float(n)
    denom = sum((x - x_mean) ** 2 for x in xs)
    if denom == 0.0:
        slope = 0.0
    else:
        slope = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / denom
    intercept = y_mean - slope * x_mean
    ss_tot = sum((y - y_mean) ** 2 for y in ys)
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
    r2 = 1.0 if ss_tot == 0.0 else max(0.0, 1.0 - (ss_res / ss_tot))
    return {"slope": float(slope), "intercept": float(intercept), "r2": float(r2)}


def _weak_values_for_depth(initial: Tuple[int, ...], ops: Tuple[int, ...]) -> List[int]:
    vals: List[int] = []
    for weak_kick in WEAK_KICKS:
        for phase_shift in PHASE_SHIFTS:
            vals.append(
                int(
                    weak_leakage_strong_residual(
                        initial,
                        ops,
                        weak_kick=int(weak_kick),
                        phase_shift=int(phase_shift),
                    )
                )
            )
    return vals


def _ckm_values_for_depth(initial: Tuple[int, ...], ops: Tuple[int, ...]) -> List[int]:
    vals: List[int] = []
    for weak_kick in WEAK_KICKS:
        for ckm_phase in CKM_PHASES:
            for period in CKM_TRANSPORT_PERIODS:
                vals.append(
                    int(
                        weak_leakage_ckm_like_strong_residual(
                            initial,
                            ops,
                            weak_kick=int(weak_kick),
                            ckm_phase=int(ckm_phase),
                            transport_period=int(period),
                        )
                    )
                )
    return vals


def build_continuum_bridge_payload() -> Dict[str, Any]:
    script_path = ROOT / SCRIPT_REPO_PATH
    bridge_path = ROOT / BRIDGE_ARTIFACT_REPO_PATH
    triplet_path = ROOT / TRIPLET_ARTIFACT_REPO_PATH
    triplet_robustness_path = ROOT / TRIPLET_ROBUSTNESS_ARTIFACT_REPO_PATH
    cases = _iter_cases()
    max_depth = min(len(op_sequence) for (_, _, op_sequence) in cases)
    depths = _depth_schedule(max_depth)

    depth_rows: List[Dict[str, Any]] = []
    for depth in depths:
        weak_vals: List[float] = []
        ckm_vals: List[float] = []
        for _, initial, op_sequence in cases:
            ops = tuple(op_sequence[:depth])
            weak_vals.extend(float(v) for v in _weak_values_for_depth(initial, ops))
            ckm_vals.extend(float(v) for v in _ckm_values_for_depth(initial, ops))
        combined_vals = weak_vals + ckm_vals
        weak_norm = [v / float(depth) for v in weak_vals]
        ckm_norm = [v / float(depth) for v in ckm_vals]
        combined_norm = [v / float(depth) for v in combined_vals]

        depth_rows.append(
            {
                "depth": int(depth),
                "weak": _metrics(weak_vals),
                "ckm_like": _metrics(ckm_vals),
                "combined": _metrics(combined_vals),
                "combined_normalized_by_depth": _metrics(combined_norm),
                "sample_count": {
                    "weak": len(weak_vals),
                    "ckm_like": len(ckm_vals),
                    "combined": len(combined_vals),
                },
                "strong_residual_all_zero": all(v == 0.0 for v in combined_vals),
            }
        )

    max_abs_series = [float(row["combined"]["max_abs"]) for row in depth_rows]
    rms_series = [float(row["combined"]["rms"]) for row in depth_rows]
    mean_abs_series = [float(row["combined"]["mean_abs"]) for row in depth_rows]
    inv_depth_series = [1.0 / float(row["depth"]) for row in depth_rows]

    zero_plateau_depth = None
    for idx, row in enumerate(depth_rows):
        suffix = depth_rows[idx:]
        if all(float(item["combined"]["max_abs"]) == 0.0 for item in suffix):
            zero_plateau_depth = int(row["depth"])
            break

    convergence = {
        "max_abs_nonincreasing": all(b <= a for a, b in zip(max_abs_series, max_abs_series[1:])),
        "rms_nonincreasing": all(b <= a for a, b in zip(rms_series, rms_series[1:])),
        "zero_plateau_depth": zero_plateau_depth,
        "finite_size_fit_mean_abs_vs_inv_depth": _linear_fit(inv_depth_series, mean_abs_series),
    }

    triplet_payload = _load_json(triplet_path) if triplet_path.exists() else {}
    if not isinstance(triplet_payload.get("discrete_transfer_function"), dict):
        triplet_payload = build_triplet_payload()
    triplet_robustness_payload = _load_json(triplet_robustness_path) if triplet_robustness_path.exists() else {}
    if not isinstance(triplet_robustness_payload.get("discrete_correction_envelope_robustness"), dict):
        triplet_robustness_payload = build_triplet_robustness_payload()
    correction_envelope = _build_discrete_correction_envelope(triplet_payload, triplet_robustness_payload)

    payload: Dict[str, Any] = {
        "schema_version": "theta001_continuum_bridge_v2",
        "claim_id": "THETA-001",
        "closure_scope": "structure_first",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "bridge_dependency_artifact": BRIDGE_ARTIFACT_REPO_PATH,
        "bridge_dependency_artifact_sha256": _sha_file(bridge_path) if bridge_path.exists() else "",
        "triplet_dependency_artifact": TRIPLET_ARTIFACT_REPO_PATH,
        "triplet_dependency_artifact_sha256": _sha_file(triplet_path) if triplet_path.exists() else "",
        "triplet_robustness_dependency_artifact": TRIPLET_ROBUSTNESS_ARTIFACT_REPO_PATH,
        "triplet_robustness_dependency_artifact_sha256": _sha_file(triplet_robustness_path)
        if triplet_robustness_path.exists()
        else "",
        "depth_schedule": depths,
        "depth_rows": depth_rows,
        "convergence_diagnostics": convergence,
        "discrete_correction_envelope": correction_envelope,
        "continuum_identification_contract": {
            "rfc_id": "RFC-003",
            "policy_id": "theta_continuum_linear_identification_v1",
            "discrete_observable_id": "theta_cp_odd_residual_v2",
            "continuum_target_operator": "F_tilde_F_coefficient",
            "locked_map_policy": "linear_scale_1_v1",
            "discrete_correction_envelope_id": "theta_discrete_correction_envelope_v1",
            "discrete_correction_robustness_id": "theta_discrete_correction_envelope_robustness_v1",
            "lean_theorem_targets": [
                "CausalGraphV2.discreteTopologicalCharge_v1_zero",
                "CausalGraphV2.thetaContinuumCoeff_linear_v1_zero",
                "CausalGraphV2.fTildeFCoeff_proxy_linear_v1_zero",
                "CausalGraphV2.theta_qcd_zero_under_locked_identification_v1",
            ],
            "status": "diagnostic_not_proved_core",
        },
        "continuum_bridge_readiness": {
            "finite_size_residual_stable_zero": all(bool(row["strong_residual_all_zero"]) for row in depth_rows),
            "normalized_residual_stable_zero": all(
                float(row["combined_normalized_by_depth"]["max_abs"]) == 0.0 for row in depth_rows
            ),
            "discrete_correction_lane_ready": bool(correction_envelope["correction_lane_ready"]),
            "discrete_correction_robustness_ready": bool(correction_envelope["robustness_lane_ready"]),
            "full_value_closure_ready": False,
        },
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def render_markdown(payload: Dict[str, Any]) -> str:
    lines = [
        "# THETA-001 Continuum Bridge Diagnostics (v2)",
        "",
        f"- Claim: `{payload['claim_id']}`",
        f"- Scope: `{payload['closure_scope']}`",
        f"- Replay hash: `{payload['replay_hash']}`",
        "",
        "## Depth Sweep",
        f"- Depth schedule: {payload['depth_schedule']}",
        "",
        "| Depth | Combined n | Max abs residual | RMS residual | Max abs residual / depth | All zero |",
        "|---:|---:|---:|---:|---:|---|",
    ]
    for row in payload["depth_rows"]:
        lines.append(
            f"| {row['depth']} | {row['sample_count']['combined']} | "
            f"{row['combined']['max_abs']} | {row['combined']['rms']} | "
            f"{row['combined_normalized_by_depth']['max_abs']} | {row['strong_residual_all_zero']} |"
        )
    conv = payload["convergence_diagnostics"]
    lines.extend(
        [
            "",
            "## Convergence Diagnostics",
            f"- max_abs_nonincreasing: `{conv['max_abs_nonincreasing']}`",
            f"- rms_nonincreasing: `{conv['rms_nonincreasing']}`",
            f"- zero_plateau_depth: `{conv['zero_plateau_depth']}`",
            f"- finite_size_fit(mean_abs vs 1/depth): `{conv['finite_size_fit_mean_abs_vs_inv_depth']}`",
            "",
            "## Discrete Correction Envelope",
            f"- envelope_id: `{payload['discrete_correction_envelope']['envelope_id']}`",
            f"- near_field_mode: `{payload['discrete_correction_envelope']['near_field_mode']}`",
            f"- correction_mode: `{payload['discrete_correction_envelope']['correction_mode']}`",
            f"- coherent_correction_onset_d_E: `{payload['discrete_correction_envelope']['coherent_correction_onset_d_E']}`",
            f"- broken_correction_onset_d_E: `{payload['discrete_correction_envelope']['broken_correction_onset_d_E']}`",
            f"- robustness_envelope_id: `{payload['discrete_correction_envelope']['robustness_envelope_id']}`",
            f"- base_correction_lane_ready: `{payload['discrete_correction_envelope']['base_correction_lane_ready']}`",
            f"- robustness_lane_ready: `{payload['discrete_correction_envelope']['robustness_lane_ready']}`",
            f"- correction_lane_ready: `{payload['discrete_correction_envelope']['correction_lane_ready']}`",
            "",
            "## Readiness",
            f"- finite_size_residual_stable_zero: `{payload['continuum_bridge_readiness']['finite_size_residual_stable_zero']}`",
            f"- normalized_residual_stable_zero: `{payload['continuum_bridge_readiness']['normalized_residual_stable_zero']}`",
            f"- discrete_correction_lane_ready: `{payload['continuum_bridge_readiness']['discrete_correction_lane_ready']}`",
            f"- discrete_correction_robustness_ready: `{payload['continuum_bridge_readiness']['discrete_correction_robustness_ready']}`",
            f"- full_value_closure_ready: `{payload['continuum_bridge_readiness']['full_value_closure_ready']}`",
            "",
            "## Notes",
            "- This artifact strengthens bridge diagnostics but does not establish proved_core by itself.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_artifacts(
    payload: Dict[str, Any],
    *,
    json_paths: Sequence[Path] | None = None,
    md_paths: Sequence[Path] | None = None,
) -> None:
    j_paths = list(json_paths) if json_paths is not None else [OUT_JSON]
    m_paths = list(md_paths) if md_paths is not None else [OUT_MD]
    for path in j_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = render_markdown(payload)
    for path in m_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(md, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build THETA-001 continuum bridge diagnostics (v2)")
    parser.add_argument("--json", action="store_true", help="Print JSON payload")
    parser.add_argument("--write-sources", action="store_true", help="Write artifacts to cog_v2/sources")
    args = parser.parse_args()

    payload = build_continuum_bridge_payload()
    if args.write_sources:
        write_artifacts(payload)
        print(f"Wrote {_to_repo_path(OUT_JSON)}")
        print(f"Wrote {_to_repo_path(OUT_MD)}")
        return
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(
        "theta001_continuum_bridge_v2: "
        f"stable_zero={payload['continuum_bridge_readiness']['finite_size_residual_stable_zero']}, "
        f"replay_hash={payload['replay_hash'][:16]}..."
    )


if __name__ == "__main__":
    main()
