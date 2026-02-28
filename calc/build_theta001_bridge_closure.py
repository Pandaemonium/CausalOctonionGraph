"""Build THETA-001 bridge-closure artifacts (weak leakage + EFT bridge contract)."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from calc.theta001_cp_invariant import (
    fano_sign_balance_counts,
    weak_leakage_ckm_conjugate_strong_residual,
    weak_leakage_ckm_conjugate_diagnostics,
    weak_leakage_ckm_like_strong_residual,
    weak_leakage_strong_residual,
)

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "sources" / "theta001_bridge_closure.json"
OUT_MD = ROOT / "sources" / "theta001_bridge_closure.md"

SCRIPT_REPO_PATH = "calc/build_theta001_bridge_closure.py"
WITNESS_MODULE_REPO_PATH = "calc/theta001_cp_invariant.py"
LEAN_BRIDGE_REPO_PATH = "CausalGraphTheory/ThetaEFTBridge.lean"

CASE_DEFINITIONS: Tuple[Dict[str, Any], ...] = (
    {
        "case_id": "base_lane_v1",
        "initial_state": (1, -2, 3, -4, 5, -6, 7, -1),
        "op_sequence": (7, 1, 7, 2, 7, 3, 7, 4, 7, 5, 7, 6, 7, 1, 2, 3, 4, 5),
    },
    {
        "case_id": "alt_lane_a_v1",
        "initial_state": (2, 1, -3, 4, -5, 6, -7, 2),
        "op_sequence": (1, 7, 2, 7, 3, 7, 4, 7, 5, 7, 6, 7, 1, 2, 3, 4, 5, 6),
    },
    {
        "case_id": "alt_lane_b_v1",
        "initial_state": (-3, 5, -7, 9, -11, 13, -15, 4),
        "op_sequence": (7, 6, 7, 5, 7, 4, 7, 3, 7, 2, 7, 1, 6, 5, 4, 3, 2, 1),
    },
)
WEAK_KICKS: Tuple[int, ...] = (-7, -5, -3, -1, 1, 3, 5, 7)
PHASE_SHIFTS: Tuple[int, ...] = (1, 2, 3, 4, 5)
CKM_PHASES: Tuple[int, ...] = (-5, -3, -1, 1, 3, 5)
CKM_TRANSPORT_PERIODS: Tuple[int, ...] = (2, 3, 4)
PERIODIC_PROBE_RESIDUALS: Tuple[int, ...] = (-3, -1, 0, 1, 3)
PERIODIC_PROBE_K: float = 1.0
LINEAR_PROBE_RESIDUALS: Tuple[int, ...] = (-7, -3, -1, 0, 1, 3, 7)
LINEAR_PROBE_SCALES: Tuple[int, ...] = (-2, -1, 1, 2)


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _to_repo_path(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def _iter_cases() -> List[Tuple[str, Tuple[int, ...], Tuple[int, ...]]]:
    cases: List[Tuple[str, Tuple[int, ...], Tuple[int, ...]]] = []
    for row in CASE_DEFINITIONS:
        case_id = str(row["case_id"])
        init = tuple(int(x) for x in row["initial_state"])
        ops = tuple(int(x) for x in row["op_sequence"])
        cases.append((case_id, init, ops))
    return cases


def _case_lookup() -> Dict[str, Tuple[Tuple[int, ...], Tuple[int, ...]]]:
    return {case_id: (init, ops) for case_id, init, ops in _iter_cases()}


def _by_case_max_abs(rows: Sequence[Dict[str, int]]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for row in rows:
        case_id = str(row["case_id"])
        out[case_id] = max(out.get(case_id, 0), abs(int(row["strong_residual"])))
    return out


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


def _ckm_like_weak_leakage_grid() -> List[Dict[str, int]]:
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


def _ckm_conjugate_falsifier_grid() -> List[Dict[str, int]]:
    rows: List[Dict[str, int]] = []
    for case_id, initial_state, op_sequence in _iter_cases():
        for weak_kick in WEAK_KICKS:
            for ckm_phase in CKM_PHASES:
                for period in CKM_TRANSPORT_PERIODS:
                    residual = weak_leakage_ckm_conjugate_strong_residual(
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


def _max_abs_residual_row(rows: Sequence[Dict[str, int]]) -> Dict[str, int]:
    if not rows:
        return {"weak_kick": 0, "ckm_phase": 0, "transport_period": 0, "strong_residual": 0}
    return max(rows, key=lambda r: abs(int(r["strong_residual"])))


def _wrap_angle(theta: float) -> float:
    """Wrap to (-pi, pi]."""
    two_pi = 2.0 * math.pi
    return ((theta + math.pi) % two_pi) - math.pi


def _periodic_angle_stub() -> Dict[str, Any]:
    """
    Non-blocking periodic-angle map lane.

    This is intentionally a governance stub:
    - keeps angle-map evaluation visible in parallel,
    - does not gate promotion while linear map remains primary.
    """
    k = float(PERIODIC_PROBE_K)
    samples: List[Dict[str, float]] = []
    for r in PERIODIC_PROBE_RESIDUALS:
        theta = _wrap_angle(k * float(r))
        theta_dual = _wrap_angle(k * float(-r))
        samples.append(
            {
                "residual": float(r),
                "theta_wrapped": theta,
                "theta_dual_wrapped": theta_dual,
                "odd_mod_2pi_holds": abs(theta + theta_dual) < 1e-12,
            }
        )

    all_odd = all(bool(row["odd_mod_2pi_holds"]) for row in samples)
    return {
        "status": "stub_non_blocking",
        "promotion_blocking": False,
        "policy_id": "theta001_periodic_angle_stub_v1",
        "map_form": "theta = wrap(k * discrete_cp_residual)",
        "k_probe": k,
        "probe_residuals": list(PERIODIC_PROBE_RESIDUALS),
        "cp_odd_mod_2pi_all_hold": bool(all_odd),
        "rows": samples,
        "notes": [
            "Parallel lane only; linear map remains the promotion contract.",
            "No fitted k, no branch-policy tuning, no value-claim semantics.",
        ],
    }


def _linear_map_lane() -> Dict[str, Any]:
    """
    Primary continuum-bridge map lane.

    Deterministic probe checks for theta = scale * residual:
    - CP oddness: theta(-r) = -theta(r),
    - zero anchor: theta(0) = 0 for all scales.
    """
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

    cp_odd_all_hold = all(bool(r["cp_odd_holds"]) for r in rows)
    zero_anchor_all_hold = all(bool(r["zero_anchor_holds"]) for r in rows)
    return {
        "status": "primary_blocking",
        "promotion_blocking": True,
        "policy_id": "theta001_linear_bridge_probe_v1",
        "map_form": "theta = scale * discrete_cp_residual",
        "scales": list(LINEAR_PROBE_SCALES),
        "probe_residuals": list(LINEAR_PROBE_RESIDUALS),
        "rows": rows,
        "cp_odd_all_hold": bool(cp_odd_all_hold),
        "zero_anchor_all_hold": bool(zero_anchor_all_hold),
        "notes": [
            "Primary bridge lane for structure_first promotion governance.",
            "No fitted scale selected; this is a map-form consistency probe only.",
        ],
    }


def build_bridge_closure_payload(
    *,
    policy_id: str = "theta001_bridge_closure_v1",
) -> Dict[str, Any]:
    script_path = ROOT / SCRIPT_REPO_PATH
    witness_module_path = ROOT / WITNESS_MODULE_REPO_PATH
    lean_bridge_path = ROOT / LEAN_BRIDGE_REPO_PATH

    pos_count, neg_count, signed_sum = fano_sign_balance_counts()
    case_lookup = _case_lookup()
    case_ids = [case_id for case_id, _, _ in _iter_cases()]
    weak_grid = _weak_leakage_grid()
    weak_by_case = _by_case_max_abs(weak_grid)
    max_abs_residual = max(abs(int(row["strong_residual"])) for row in weak_grid)
    ckm_grid = _ckm_like_weak_leakage_grid()
    ckm_by_case = _by_case_max_abs(ckm_grid)
    ckm_max_abs_residual = max(abs(int(row["strong_residual"])) for row in ckm_grid)
    ckm_conj_grid = _ckm_conjugate_falsifier_grid()
    ckm_conj_by_case = _by_case_max_abs(ckm_conj_grid)
    ckm_conj_max_abs_residual = max(abs(int(row["strong_residual"])) for row in ckm_conj_grid)
    ckm_conj_any_nonzero = any(int(row["strong_residual"]) != 0 for row in ckm_conj_grid)
    ckm_conj_max_row = _max_abs_residual_row(ckm_conj_grid)
    max_case_id = str(ckm_conj_max_row["case_id"])
    max_case_initial, max_case_ops = case_lookup[max_case_id]
    ckm_conj_diag = weak_leakage_ckm_conjugate_diagnostics(
        max_case_initial,
        max_case_ops,
        weak_kick=int(ckm_conj_max_row["weak_kick"]),
        ckm_phase=int(ckm_conj_max_row["ckm_phase"]),
        transport_period=int(ckm_conj_max_row["transport_period"]),
    )
    ckm_conj_diag["case_id"] = max_case_id
    linear_lane = _linear_map_lane()
    periodic_lane = _periodic_angle_stub()

    payload: Dict[str, Any] = {
        "schema_version": "theta001_bridge_closure_v1",
        "claim_id": "THETA-001",
        "policy_id": policy_id,
        "source_script": SCRIPT_REPO_PATH,
        "source_script_sha256": _sha_file(script_path),
        "witness_module": WITNESS_MODULE_REPO_PATH,
        "witness_module_sha256": _sha_file(witness_module_path),
        "lean_bridge_file": LEAN_BRIDGE_REPO_PATH,
        "lean_bridge_file_sha256": _sha_file(lean_bridge_path),
        "discrete_cp_residual": {
            "positive_count": int(pos_count),
            "negative_count": int(neg_count),
            "signed_sum": int(signed_sum),
            "is_zero": int(signed_sum) == 0,
        },
        "weak_leakage_suite": {
            "cases": case_ids,
            "case_count": len(case_ids),
            "weak_kicks": list(WEAK_KICKS),
            "phase_shifts": list(PHASE_SHIFTS),
            "rows": weak_grid,
            "by_case_max_abs_residual": weak_by_case,
            "max_abs_residual": int(max_abs_residual),
            "all_zero": int(max_abs_residual) == 0,
        },
        "ckm_like_weak_leakage_suite": {
            "cases": case_ids,
            "case_count": len(case_ids),
            "weak_kicks": list(WEAK_KICKS),
            "ckm_phases": list(CKM_PHASES),
            "transport_periods": list(CKM_TRANSPORT_PERIODS),
            "rows": ckm_grid,
            "by_case_max_abs_residual": ckm_by_case,
            "max_abs_residual": int(ckm_max_abs_residual),
            "all_zero": int(ckm_max_abs_residual) == 0,
        },
        "ckm_conjugate_falsifier_lane": {
            "status": "exploratory_non_blocking",
            "promotion_blocking": False,
            "cases": case_ids,
            "case_count": len(case_ids),
            "weak_kicks": list(WEAK_KICKS),
            "ckm_phases": list(CKM_PHASES),
            "transport_periods": list(CKM_TRANSPORT_PERIODS),
            "rows": ckm_conj_grid,
            "by_case_max_abs_residual": ckm_conj_by_case,
            "max_abs_residual": int(ckm_conj_max_abs_residual),
            "any_nonzero": bool(ckm_conj_any_nonzero),
            "max_case": ckm_conj_max_row,
            "max_case_diagnostics": ckm_conj_diag,
            "notes": [
                "This lane uses explicit CP-conjugate CKM phase in dual run.",
                "Non-zero residuals are expected as falsifier signals under stronger assumptions.",
                "Lane is non-blocking for THETA-001 structure_first promotion.",
            ],
        },
        "continuum_bridge_contract": {
            "bridge_mode": "conditional_linear_map_v1",
            "map_form": "theta_continuum = scale * discrete_cp_residual",
            "linear_map_lane": linear_lane,
            "assumptions": [
                "Discrete CP map corresponds to continuum CP transformation under locked group-theoretic identification.",
                "Continuum theta coefficient is linear in the discrete CP residual at bridge scale.",
            ],
            "lean_theorems": [
                "CausalGraph.discreteCpResidual_zero",
                "CausalGraph.theta_zero_if_direct_bridge",
                "CausalGraph.theta_zero_if_linear_bridge",
                "CausalGraph.theta_zero_if_affine_bridge",
            ],
            "conditional_conclusion_theta_zero": True,
        },
        "periodic_angle_lane": periodic_lane,
    }
    payload["bridge_ready_supported_bridge"] = bool(
        payload["discrete_cp_residual"]["is_zero"]
        and payload["weak_leakage_suite"]["all_zero"]
        and payload["ckm_like_weak_leakage_suite"]["all_zero"]
    )
    payload["replay_hash"] = _sha_payload(payload)
    return payload


def render_markdown(payload: Dict[str, Any]) -> str:
    disc = payload["discrete_cp_residual"]
    wl = payload["weak_leakage_suite"]
    ckm = payload["ckm_like_weak_leakage_suite"]
    ckm_conj = payload["ckm_conjugate_falsifier_lane"]
    bridge = payload["continuum_bridge_contract"]
    periodic = payload["periodic_angle_lane"]
    lines = [
        "# THETA-001 Bridge Closure Artifact",
        "",
        f"- Claim: `{payload['claim_id']}`",
        f"- Policy: `{payload['policy_id']}`",
        f"- Replay hash: `{payload['replay_hash']}`",
        "",
        "## Discrete Residual",
        f"- Positive count: {disc['positive_count']}",
        f"- Negative count: {disc['negative_count']}",
        f"- Signed sum: {disc['signed_sum']}",
        f"- Residual zero: `{disc['is_zero']}`",
        "",
        "## Weak Leakage Suite",
        f"- Cases: {wl['case_count']}",
        f"- Grid rows: {len(wl['rows'])}",
        f"- Max abs strong residual: {wl['max_abs_residual']}",
        f"- All zero: `{wl['all_zero']}`",
        "",
        "## CKM-Like Weak Leakage Suite",
        f"- Cases: {ckm['case_count']}",
        f"- Grid rows: {len(ckm['rows'])}",
        f"- Max abs strong residual: {ckm['max_abs_residual']}",
        f"- All zero: `{ckm['all_zero']}`",
        "",
        "## CKM-Conjugate Falsifier Lane (Non-Blocking)",
        f"- Status: `{ckm_conj['status']}`",
        f"- Promotion blocking: `{ckm_conj['promotion_blocking']}`",
        f"- Cases: {len(ckm_conj['rows'])}",
        f"- Max abs strong residual: {ckm_conj['max_abs_residual']}",
        f"- Any nonzero residual detected: `{ckm_conj['any_nonzero']}`",
        f"- First nonzero tick (max case): `{ckm_conj['max_case_diagnostics']['first_nonzero_tick']}`",
        f"- Max abs tick delta (max case): `{ckm_conj['max_case_diagnostics']['max_abs_tick_delta']}`",
        "",
        "## Continuum Bridge Contract",
        f"- Mode: `{bridge['bridge_mode']}`",
        f"- Map form: `{bridge['map_form']}`",
        f"- Conditional conclusion theta=0: `{bridge['conditional_conclusion_theta_zero']}`",
        "",
        "### Lean Theorems",
    ]
    for thm in bridge["lean_theorems"]:
        lines.append(f"- `{thm}`")
    lines.extend(
        [
            "",
            "## Periodic Angle Lane (Parallel Stub)",
            f"- Status: `{periodic['status']}`",
            f"- Promotion blocking: `{periodic['promotion_blocking']}`",
            f"- Map form: `{periodic['map_form']}`",
            f"- Probe k: `{periodic['k_probe']}`",
            f"- CP oddness mod 2pi all hold: `{periodic['cp_odd_mod_2pi_all_hold']}`",
            "",
            "## Linear Map Lane (Primary Blocking)",
            f"- Status: `{bridge['linear_map_lane']['status']}`",
            f"- Promotion blocking: `{bridge['linear_map_lane']['promotion_blocking']}`",
            f"- Map form: `{bridge['linear_map_lane']['map_form']}`",
            f"- CP oddness all hold: `{bridge['linear_map_lane']['cp_odd_all_hold']}`",
            f"- Zero anchor all hold: `{bridge['linear_map_lane']['zero_anchor_all_hold']}`",
            "",
            "## Promotion Signal",
            f"- bridge_ready_supported_bridge: `{payload['bridge_ready_supported_bridge']}`",
        ]
    )
    return "\n".join(lines) + "\n"


def write_artifacts(
    payload: Dict[str, Any],
    *,
    json_paths: Sequence[Path] | None = None,
    md_paths: Sequence[Path] | None = None,
) -> None:
    json_out = list(json_paths) if json_paths is not None else [OUT_JSON]
    md_out = list(md_paths) if md_paths is not None else [OUT_MD]

    for path in json_out:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = render_markdown(payload)
    for path in md_out:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(md, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build THETA-001 bridge closure artifacts")
    parser.add_argument("--json", action="store_true", help="Print JSON payload")
    parser.add_argument("--write-sources", action="store_true", help="Write sources artifacts")
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
        "theta001_bridge_closure: "
        f"all_zero={payload['weak_leakage_suite']['all_zero']}, "
        f"bridge_ready={payload['bridge_ready_supported_bridge']}, "
        f"replay_hash={payload['replay_hash'][:16]}..."
    )


if __name__ == "__main__":
    main()
