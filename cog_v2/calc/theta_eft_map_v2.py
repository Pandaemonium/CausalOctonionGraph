"""Continuum-EFT bridge scaffolding for THETA-001 in COG v2.

This module does not claim full EFT closure. It provides:
1) deterministic map-form probes from discrete CP residual to continuum theta,
2) CP-odd / zero-anchor consistency checks over probe grids,
3) a coarse-grained CP-odd topological-charge proxy lane for trace diagnostics.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Sequence, Tuple

from cog_v2.calc.theta001_cp_invariant_v2 import FANO_SIGN, cp_map, run_update_trace


ROOT = Path(__file__).resolve().parents[2]
MODULE_REPO_PATH = "cog_v2/calc/theta_eft_map_v2.py"

TraceCase = Tuple[str, Tuple[int, ...], Tuple[int, ...]]

TRACE_CASES: Tuple[TraceCase, ...] = (
    (
        "eft_case_001",
        (1, -2, 3, -4, 5, -6, 7, -1),
        (7, 1, 7, 2, 7, 3, 7, 4, 7, 5, 7, 6, 7, 1, 2, 3),
    ),
    (
        "eft_case_002",
        (2, 1, -3, 4, -5, 6, -7, 2),
        (1, 7, 2, 7, 3, 7, 4, 7, 5, 7, 6, 7, 1, 2, 3, 4),
    ),
    (
        "eft_case_003",
        (-3, 5, -7, 9, -11, 13, -15, 4),
        (7, 6, 7, 5, 7, 4, 7, 3, 7, 2, 7, 1, 6, 5, 4, 3),
    ),
)

RESIDUAL_PROBES: Tuple[int, ...] = (-21, -13, -7, -3, -1, 0, 1, 3, 7, 13, 21)
LINEAR_SCALES: Tuple[float, ...] = (-2.0, -1.0, 1.0, 2.0)
AFFINE_OFFSETS: Tuple[float, ...] = (0.0, 0.25)
ZERO_ANCHORED_CUBIC_SCALES: Tuple[float, ...] = (0.0, 0.01, 0.05)
MAP_IDENTIFICATION_POLICY_ID = "theta_map_identification_linear_unit_v1"


@dataclass(frozen=True)
class MapSpec:
    map_id: str
    mode: str
    scale: float
    offset: float = 0.0
    cubic_scale: float = 0.0


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def theta_map_direct(residual: int) -> float:
    return float(residual)


def theta_map_linear(residual: int, *, scale: float) -> float:
    return float(scale * float(residual))


def theta_map_affine(residual: int, *, scale: float, offset: float) -> float:
    return float(scale * float(residual) + offset)


def theta_map_zero_anchored_poly(residual: int, *, scale: float, cubic_scale: float) -> float:
    r = float(residual)
    return float(scale * r + cubic_scale * (r**3))


def _build_map_fn(spec: MapSpec) -> Callable[[int], float]:
    if spec.mode == "direct":
        return theta_map_direct
    if spec.mode == "linear":
        return lambda r: theta_map_linear(r, scale=spec.scale)
    if spec.mode == "affine":
        return lambda r: theta_map_affine(r, scale=spec.scale, offset=spec.offset)
    if spec.mode == "zero_anchored_poly":
        return lambda r: theta_map_zero_anchored_poly(r, scale=spec.scale, cubic_scale=spec.cubic_scale)
    raise ValueError(f"Unknown map mode: {spec.mode}")


def evaluate_map_symmetry(
    residuals: Sequence[int],
    map_fn: Callable[[int], float],
    *,
    tol: float = 1e-12,
) -> Dict[str, Any]:
    rows = []
    for r in residuals:
        theta = float(map_fn(int(r)))
        theta_dual = float(map_fn(int(-r)))
        cp_odd_holds = abs(theta + theta_dual) <= tol
        zero_anchor_holds = (int(r) != 0) or (abs(theta) <= tol and abs(theta_dual) <= tol)
        rows.append(
            {
                "residual": int(r),
                "theta": theta,
                "theta_dual": theta_dual,
                "cp_odd_holds": bool(cp_odd_holds),
                "zero_anchor_holds": bool(zero_anchor_holds),
            }
        )
    return {
        "rows": rows,
        "cp_odd_all_hold": all(bool(row["cp_odd_holds"]) for row in rows),
        "zero_anchor_all_hold": all(bool(row["zero_anchor_holds"]) for row in rows),
        "max_cp_odd_violation": max(abs(float(row["theta"]) + float(row["theta_dual"])) for row in rows),
    }


def q_density_proxy(state: Sequence[int]) -> int:
    """Coarse CP-odd density proxy.

    Uses e111 sign channel times quadratic strong-sector activity:
      q ~ e111 * sum_i i * channel_i^2  for i in {e001..e110}
    Under cp_map: e111 -> -e111, channel_i^2 invariant => q -> -q.
    """
    e111 = int(state[7])
    strong_quad = sum((idx + 1) * (int(state[idx]) ** 2) for idx in range(1, 7))
    return int(e111 * strong_quad)


def q_top_proxy(trace: Iterable[Sequence[int]]) -> int:
    return int(sum(q_density_proxy(state) for state in trace))


def run_qtop_proxy_suite(cases: Sequence[TraceCase]) -> Dict[str, Any]:
    rows = []
    for case_id, initial_state, op_sequence in cases:
        trace = run_update_trace(tuple(initial_state), tuple(op_sequence), FANO_SIGN)
        cp_trace = [cp_map(tuple(s)) for s in trace]
        q = q_top_proxy(trace)
        q_cp = q_top_proxy(cp_trace)
        rows.append(
            {
                "case_id": case_id,
                "q_top_proxy": int(q),
                "q_top_proxy_cp_dual": int(q_cp),
                "cp_odd_holds": int(q + q_cp) == 0,
                "trace_len": len(trace),
            }
        )
    return {
        "rows": rows,
        "cp_odd_all_hold": all(bool(r["cp_odd_holds"]) for r in rows),
        "max_abs_q_top_proxy": max(abs(int(r["q_top_proxy"])) for r in rows),
    }


def build_theta_eft_bridge_payload() -> Dict[str, Any]:
    module_path = ROOT / MODULE_REPO_PATH
    map_specs: List[MapSpec] = [
        MapSpec(map_id="direct_v1", mode="direct", scale=1.0),
    ]
    map_specs.extend(
        MapSpec(map_id=f"linear_scale_{scale:g}_v1", mode="linear", scale=float(scale))
        for scale in LINEAR_SCALES
    )
    map_specs.extend(
        MapSpec(map_id=f"affine_scale_1_offset_{offset:g}_v1", mode="affine", scale=1.0, offset=float(offset))
        for offset in AFFINE_OFFSETS
    )
    map_specs.extend(
        MapSpec(
            map_id=f"zero_anchored_poly_scale_1_cubic_{cubic:g}_v1",
            mode="zero_anchored_poly",
            scale=1.0,
            cubic_scale=float(cubic),
        )
        for cubic in ZERO_ANCHORED_CUBIC_SCALES
    )

    map_rows = []
    for spec in map_specs:
        map_fn = _build_map_fn(spec)
        result = evaluate_map_symmetry(RESIDUAL_PROBES, _build_map_fn(spec))
        map_rows.append(
            {
                "map_id": spec.map_id,
                "mode": spec.mode,
                "scale": float(spec.scale),
                "offset": float(spec.offset),
                "cubic_scale": float(spec.cubic_scale),
                "theta_at_plus_one": float(map_fn(1)),
                "theta_at_minus_one": float(map_fn(-1)),
                "cp_odd_all_hold": bool(result["cp_odd_all_hold"]),
                "zero_anchor_all_hold": bool(result["zero_anchor_all_hold"]),
                "max_cp_odd_violation": float(result["max_cp_odd_violation"]),
                "rows": result["rows"],
            }
        )

    qtop_suite = run_qtop_proxy_suite(TRACE_CASES)

    eligible_map_ids: List[str] = []
    for row in map_rows:
        if row["mode"] != "linear":
            continue
        if row["cp_odd_all_hold"] is not True:
            continue
        if row["zero_anchor_all_hold"] is not True:
            continue
        if abs(float(row["theta_at_plus_one"]) - 1.0) > 1e-12:
            continue
        if abs(float(row["theta_at_minus_one"]) + 1.0) > 1e-12:
            continue
        eligible_map_ids.append(str(row["map_id"]))
    eligible_map_ids = sorted(set(eligible_map_ids))
    selected_map_id = eligible_map_ids[0] if len(eligible_map_ids) == 1 else ""

    payload: Dict[str, Any] = {
        "schema_version": "theta001_eft_bridge_v2",
        "claim_id": "THETA-001",
        "closure_scope": "structure_first",
        "source_module": MODULE_REPO_PATH,
        "source_module_sha256": _sha_file(module_path),
        "probe_residuals": list(RESIDUAL_PROBES),
        "map_suite": {
            "rows": map_rows,
            "cp_odd_all_hold": all(bool(r["cp_odd_all_hold"]) for r in map_rows),
            "zero_anchor_all_hold": all(bool(r["zero_anchor_all_hold"]) for r in map_rows),
            "notes": [
                "Map-form consistency probe with an operational identification policy.",
                "Affine non-zero offset probes intentionally test zero-anchor failure behavior.",
            ],
        },
        "map_identification": {
            "policy_id": MAP_IDENTIFICATION_POLICY_ID,
            "constraints": [
                "mode == linear",
                "cp_odd_all_hold == true",
                "zero_anchor_all_hold == true",
                "theta_at_plus_one == +1",
                "theta_at_minus_one == -1",
            ],
            "eligible_map_ids": eligible_map_ids,
            "selected_map_id": selected_map_id,
            "selected_unique": len(eligible_map_ids) == 1,
            "selection_ready": bool(selected_map_id),
        },
        "q_top_proxy_suite": qtop_suite,
        "continuum_eft_bridge_readiness": {
            "cp_odd_proxy_consistent": bool(qtop_suite["cp_odd_all_hold"]),
            "map_suite_has_cp_odd_candidate": any(
                bool(r["cp_odd_all_hold"]) and bool(r["zero_anchor_all_hold"]) for r in map_rows
            ),
            "map_identification_locked": bool(selected_map_id == "linear_scale_1_v1"),
            "full_value_closure_ready": False,
        },
        "lean_bridge_theorems": [
            "CausalGraphV2.discreteCpResidual_zero",
            "CausalGraphV2.theta_zero_if_direct_bridge",
            "CausalGraphV2.theta_zero_if_linear_bridge",
            "CausalGraphV2.theta_zero_if_affine_bridge",
            "CausalGraphV2.theta_zero_if_zero_anchored_bridge",
        ],
    }
    payload["replay_hash"] = _sha_payload(payload)
    return payload
