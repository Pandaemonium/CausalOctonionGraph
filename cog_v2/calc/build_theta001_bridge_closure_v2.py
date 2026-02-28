"""Build deterministic THETA-001 bridge closure artifacts for COG v2."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from cog_v2.calc.theta001_cp_invariant_v2 import (
    FANO_TRIPLES,
    cp_dual_trace_relation_holds,
    cp_weighted_trace_delta,
    fano_sign_balance_counts,
    orientation_reversal_closed_on_fano_lines,
    weak_leakage_ckm_like_strong_residual,
    weak_leakage_strong_residual,
)

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "cog_v2" / "sources" / "theta001_bridge_closure_v2.json"
OUT_MD = ROOT / "cog_v2" / "sources" / "theta001_bridge_closure_v2.md"

SCRIPT_REPO_PATH = "cog_v2/calc/build_theta001_bridge_closure_v2.py"
WITNESS_MODULE_REPO_PATH = "cog_v2/calc/theta001_cp_invariant_v2.py"
LEAN_BRIDGE_REPO_PATH = "cog_v2/lean/CausalGraphV2/ThetaEFTBridge.lean"

DEFAULT_WEIGHTS: Tuple[int, ...] = (1, 2, 3, 4, 5, 6, 7, 8)
CASE_DEFINITIONS: Tuple[Dict[str, Any], ...] = (
    {
        "case_id": "base_lane_v2",
        "initial_state": (1, -2, 3, -4, 5, -6, 7, -1),
        "op_sequence": (
            7, 1, 7, 2, 7, 3, 7, 4, 7, 5, 7, 6, 7, 1, 2, 3, 4, 5,
            7, 1, 7, 2, 7, 3, 7, 4, 7, 5, 7, 6, 7, 1, 2, 3, 4, 5,
            7, 1, 7, 2, 7, 3, 7, 4, 7, 5, 7, 6, 7, 1, 2, 3, 4, 5,
            7, 1, 7, 2, 7, 3, 7, 4, 7, 5, 7, 6, 7, 1, 2, 3, 4, 5,
        ),
    },
    {
        "case_id": "alt_lane_a_v2",
        "initial_state": (2, 1, -3, 4, -5, 6, -7, 2),
        "op_sequence": (
            1, 7, 2, 7, 3, 7, 4, 7, 5, 7, 6, 7, 1, 2, 3, 4, 5, 6,
            1, 7, 2, 7, 3, 7, 4, 7, 5, 7, 6, 7, 1, 2, 3, 4, 5, 6,
            1, 7, 2, 7, 3, 7, 4, 7, 5, 7, 6, 7, 1, 2, 3, 4, 5, 6,
            1, 7, 2, 7, 3, 7, 4, 7, 5, 7, 6, 7, 1, 2, 3, 4, 5, 6,
        ),
    },
    {
        "case_id": "alt_lane_b_v2",
        "initial_state": (-3, 5, -7, 9, -11, 13, -15, 4),
        "op_sequence": (
            7, 6, 7, 5, 7, 4, 7, 3, 7, 2, 7, 1, 6, 5, 4, 3, 2, 1,
            7, 6, 7, 5, 7, 4, 7, 3, 7, 2, 7, 1, 6, 5, 4, 3, 2, 1,
            7, 6, 7, 5, 7, 4, 7, 3, 7, 2, 7, 1, 6, 5, 4, 3, 2, 1,
            7, 6, 7, 5, 7, 4, 7, 3, 7, 2, 7, 1, 6, 5, 4, 3, 2, 1,
        ),
    },
)
WEAK_KICKS: Tuple[int, ...] = (-11, -9, -7, -5, -3, -1, 1, 3, 5, 7, 9, 11)
PHASE_SHIFTS: Tuple[int, ...] = (1, 2, 3, 4, 5, 6, 7, 8, 9)
CKM_PHASES: Tuple[int, ...] = (-7, -5, -3, -1, 1, 3, 5, 7)
CKM_TRANSPORT_PERIODS: Tuple[int, ...] = (2, 3, 4, 5, 6)
PERIODIC_PROBE_RESIDUALS: Tuple[int, ...] = (-3, -1, 0, 1, 3)
LINEAR_PROBE_RESIDUALS: Tuple[int, ...] = (-7, -3, -1, 0, 1, 3, 7)
LINEAR_PROBE_SCALES: Tuple[int, ...] = (-2, -1, 1, 2)


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


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


def _to_repo_path(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def _trace_suite(weights: Sequence[int]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for case_id, initial_state, op_sequence in _iter_cases():
        cp_dual_ok = cp_dual_trace_relation_holds(initial_state, op_sequence)
        weighted_delta = cp_weighted_trace_delta(initial_state, op_sequence, weights)
        rows.append(
            {
                "case_id": case_id,
                "cp_dual_relation_holds": bool(cp_dual_ok),
                "weighted_trace_delta": int(weighted_delta),
            }
        )
    return rows


def _weak_leakage_grid() -> List[Dict[str, int]]:
    rows: List[Dict[str, int]] = []
    for case_id, initial_state, op_sequence in _iter_cases():
        for weak_kick in WEAK_KICKS:
            for phase_shift in PHASE_SHIFTS:
                residual = weak_leakage_strong_residual(
                    initial_state,
                    op_sequence,
                    weak_kick=weak_kick,
                    phase_shift=phase_shift,
                )
                rows.append(
                    {
                        "case_id": case_id,
                        "weak_kick": int(weak_kick),
                        "phase_shift": int(phase_shift),
                        "strong_residual": int(residual),
                    }
                )
    return rows


def _ckm_like_grid() -> List[Dict[str, int]]:
    rows: List[Dict[str, int]] = []
    for case_id, initial_state, op_sequence in _iter_cases():
        for weak_kick in WEAK_KICKS:
            for ckm_phase in CKM_PHASES:
                for period in CKM_TRANSPORT_PERIODS:
                    residual = weak_leakage_ckm_like_strong_residual(
                        initial_state,
                        op_sequence,
                        weak_kick=weak_kick,
                        ckm_phase=ckm_phase,
                        transport_period=period,
                    )
                    rows.append(
                        {
                            "case_id": case_id,
                            "weak_kick": int(weak_kick),
                            "ckm_phase": int(ckm_phase),
                            "transport_period": int(period),
                            "strong_residual": int(residual),
                        }
                    )
    return rows


def _periodic_angle_stub() -> Dict[str, Any]:
    k = 1.0

    def wrap(theta: float) -> float:
        two_pi = 2.0 * math.pi
        return ((theta + math.pi) % two_pi) - math.pi

    rows = []
    for residual in PERIODIC_PROBE_RESIDUALS:
        theta = wrap(k * float(residual))
        theta_dual = wrap(k * float(-residual))
        rows.append(
            {
                "residual": float(residual),
                "theta_wrapped": float(theta),
                "theta_dual_wrapped": float(theta_dual),
                "odd_mod_2pi_holds": abs(theta + theta_dual) < 1e-12,
            }
        )
    return {
        "status": "stub_non_blocking",
        "promotion_blocking": False,
        "cp_odd_mod_2pi_all_hold": all(bool(r["odd_mod_2pi_holds"]) for r in rows),
        "rows": rows,
    }


def _linear_map_lane() -> Dict[str, Any]:
    rows: List[Dict[str, int | bool]] = []
    for scale in LINEAR_PROBE_SCALES:
        for residual in LINEAR_PROBE_RESIDUALS:
            theta = int(scale * residual)
            theta_dual = int(scale * (-residual))
            rows.append(
                {
                    "scale": int(scale),
                    "residual": int(residual),
                    "theta": int(theta),
                    "theta_dual": int(theta_dual),
                    "cp_odd_holds": int(theta + theta_dual) == 0,
                    "zero_anchor_holds": (int(residual) != 0) or (int(theta) == 0 and int(theta_dual) == 0),
                }
            )
    return {
        "status": "primary_blocking",
        "promotion_blocking": True,
        "cp_odd_all_hold": all(bool(r["cp_odd_holds"]) for r in rows),
        "zero_anchor_all_hold": all(bool(r["zero_anchor_holds"]) for r in rows),
        "rows": rows,
    }


def build_bridge_closure_payload() -> Dict[str, Any]:
    script_path = ROOT / SCRIPT_REPO_PATH
    witness_module_path = ROOT / WITNESS_MODULE_REPO_PATH
    lean_bridge_path = ROOT / LEAN_BRIDGE_REPO_PATH
    pos_count, neg_count, signed_sum = fano_sign_balance_counts()
    orientation_closed = orientation_reversal_closed_on_fano_lines(FANO_TRIPLES)
    trace_suite = _trace_suite(weights=DEFAULT_WEIGHTS)
    weak_grid = _weak_leakage_grid()
    ckm_grid = _ckm_like_grid()
    case_depths = [len(op_sequence) for (_, _, op_sequence) in _iter_cases()]
    weak_max = max(abs(int(row["strong_residual"])) for row in weak_grid)
    ckm_max = max(abs(int(row["strong_residual"])) for row in ckm_grid)
    linear_lane = _linear_map_lane()
    periodic_lane = _periodic_angle_stub()

    payload: Dict[str, Any] = {
        "schema_version": "theta001_bridge_closure_v2",
        "claim_id": "THETA-001",
        "closure_scope": "structure_first",
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "witness_module": WITNESS_MODULE_REPO_PATH,
        "witness_module_sha256": _sha_file(witness_module_path),
        "lean_bridge_file": LEAN_BRIDGE_REPO_PATH,
        "lean_bridge_file_sha256": _sha_file(lean_bridge_path),
        "trace_suite": trace_suite,
        "fano_sign_balance": {
            "positive_count": int(pos_count),
            "negative_count": int(neg_count),
            "signed_sum": int(signed_sum),
        },
        "orientation_reversal_closed_on_fano_lines": bool(orientation_closed),
        "stress_lane_profile": {
            "case_count": len(CASE_DEFINITIONS),
            "op_depth_min": int(min(case_depths)),
            "op_depth_max": int(max(case_depths)),
            "weak_kicks": list(WEAK_KICKS),
            "phase_shifts": list(PHASE_SHIFTS),
            "ckm_phases": list(CKM_PHASES),
            "ckm_transport_periods": list(CKM_TRANSPORT_PERIODS),
            "weak_grid_size": int(len(weak_grid)),
            "ckm_grid_size": int(len(ckm_grid)),
        },
        "weak_leakage_suite": {
            "case_count": len(CASE_DEFINITIONS),
            "rows": weak_grid,
            "max_abs_residual": int(weak_max),
            "all_zero": int(weak_max) == 0,
        },
        "ckm_like_weak_leakage_suite": {
            "case_count": len(CASE_DEFINITIONS),
            "rows": ckm_grid,
            "max_abs_residual": int(ckm_max),
            "all_zero": int(ckm_max) == 0,
        },
        "continuum_bridge_contract": {
            "bridge_mode": "conditional_linear_map_v1",
            "linear_map_lane": linear_lane,
            "conditional_conclusion_theta_zero": True,
            "lean_theorems": [
                "CausalGraphV2.discreteCpResidual_zero",
                "CausalGraphV2.theta_zero_if_direct_bridge",
                "CausalGraphV2.theta_zero_if_linear_bridge",
                "CausalGraphV2.theta_zero_if_affine_bridge",
                "CausalGraphV2.theta_zero_if_zero_anchored_bridge",
            ],
        },
        "periodic_angle_lane": periodic_lane,
    }
    payload["bridge_ready_supported_bridge"] = bool(
        payload["fano_sign_balance"]["signed_sum"] == 0
        and payload["weak_leakage_suite"]["all_zero"]
        and payload["ckm_like_weak_leakage_suite"]["all_zero"]
        and linear_lane["cp_odd_all_hold"]
        and linear_lane["zero_anchor_all_hold"]
    )
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def render_markdown(payload: Dict[str, Any]) -> str:
    lines = [
        "# THETA-001 Bridge Closure Artifact (v2)",
        "",
        f"- Claim: `{payload['claim_id']}`",
        f"- Replay hash: `{payload['replay_hash']}`",
        f"- Source script: `{payload['source_script']}`",
        "",
        "## Structural Residual",
        f"- Sign balance: +{payload['fano_sign_balance']['positive_count']} / -{payload['fano_sign_balance']['negative_count']}",
        f"- Signed sum: `{payload['fano_sign_balance']['signed_sum']}`",
        f"- Orientation closed: `{payload['orientation_reversal_closed_on_fano_lines']}`",
        "",
        "## Weak Leakage",
        f"- Stress profile depth: min {payload['stress_lane_profile']['op_depth_min']} / max {payload['stress_lane_profile']['op_depth_max']}",
        f"- Weak grid size: {payload['stress_lane_profile']['weak_grid_size']}",
        f"- CKM-like grid size: {payload['stress_lane_profile']['ckm_grid_size']}",
        f"- Weak lane all zero: `{payload['weak_leakage_suite']['all_zero']}` (max abs {payload['weak_leakage_suite']['max_abs_residual']})",
        f"- CKM-like lane all zero: `{payload['ckm_like_weak_leakage_suite']['all_zero']}` (max abs {payload['ckm_like_weak_leakage_suite']['max_abs_residual']})",
        "",
        "## Bridge Lanes",
        f"- Linear lane status: `{payload['continuum_bridge_contract']['linear_map_lane']['status']}`",
        f"- Linear cp odd all hold: `{payload['continuum_bridge_contract']['linear_map_lane']['cp_odd_all_hold']}`",
        f"- Linear zero anchor all hold: `{payload['continuum_bridge_contract']['linear_map_lane']['zero_anchor_all_hold']}`",
        f"- Periodic lane status: `{payload['periodic_angle_lane']['status']}`",
        "",
        "## Promotion Readiness",
        f"- bridge_ready_supported_bridge: `{payload['bridge_ready_supported_bridge']}`",
        "",
        "## Replay",
        "Run `python -m cog_v2.calc.build_theta001_bridge_closure_v2 --write-sources` and verify the replay hash is unchanged.",
    ]
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
    parser = argparse.ArgumentParser(description="Build THETA-001 bridge closure artifact for COG v2")
    parser.add_argument("--json", action="store_true", help="Print JSON payload")
    parser.add_argument("--write-sources", action="store_true", help="Write artifacts to cog_v2/sources")
    args = parser.parse_args()

    payload = build_bridge_closure_payload()
    if args.write_sources:
        write_artifacts(payload)
        print(f"Wrote {_to_repo_path(OUT_JSON)}")
        print(f"Wrote {_to_repo_path(OUT_MD)}")
        return
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(
        "theta001_bridge_closure_v2: "
        f"bridge_ready_supported_bridge={payload['bridge_ready_supported_bridge']}, "
        f"replay_hash={payload['replay_hash'][:16]}..."
    )


if __name__ == "__main__":
    main()
