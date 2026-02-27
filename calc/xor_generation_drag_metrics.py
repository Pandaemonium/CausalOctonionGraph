"""
calc/xor_generation_drag_metrics.py

RFC-068 Phase A instrumentation:
1) run deterministic full-lightcone simulations for predeclared motif cases,
2) compute per-depth drag observables (S_t, V_t, M_t, C_t, A_t, D_t),
3) compute DragScore and MuEff relative to electron baseline.
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from calc.xor_furey_ideals import (
    GI,
    StateGI,
    furey_dual_electron_doubled,
    furey_electron_doubled,
    ideal_sd_basis_doubled,
    ideal_su_basis_doubled,
    nonzero_support,
    state_basis,
)
from calc.xor_full_lightcone_engine import simulate_full_lightcone
from calc.xor_observables import decode_base8_int


def _require_int(name: str, value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer")
    return int(value)


def _sha(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _load_json(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _motif_state_map() -> Dict[str, StateGI]:
    motifs: Dict[str, StateGI] = {
        "furey_electron_doubled": furey_electron_doubled(),
        "furey_dual_electron_doubled": furey_dual_electron_doubled(),
        "identity_e0": state_basis(0, (1, 0)),
    }
    motifs.update(ideal_su_basis_doubled())
    motifs.update(ideal_sd_basis_doubled())
    return motifs


def _decode_state_base8(payload: str) -> StateGI:
    raw = json.loads(payload)
    if not isinstance(raw, list) or len(raw) != 8:
        raise ValueError("state_base8 must decode to length-8 list")
    out: List[GI] = []
    for item in raw:
        if not isinstance(item, list) or len(item) != 2:
            raise ValueError("state_base8 row must be [re, im]")
        out.append((decode_base8_int(str(item[0])), decode_base8_int(str(item[1]))))
    return tuple(out)  # type: ignore[return-value]


def _coeff_l1(c: GI) -> int:
    return abs(int(c[0])) + abs(int(c[1]))


def _support_outside_allowed(state: StateGI, allowed: set[int]) -> bool:
    for idx in nonzero_support(state):
        if idx not in allowed:
            return True
    return False


def _group_rows_by_depth(rows: Sequence[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
    out: Dict[int, List[Dict[str, Any]]] = {}
    for row in rows:
        depth = int(row["depth"])
        out.setdefault(depth, []).append(row)
    return out


def _compute_depth_metrics(
    *,
    csv_rows: Sequence[Dict[str, Any]],
    allowed_support: set[int],
) -> Tuple[List[Dict[str, Any]], float]:
    grouped = _group_rows_by_depth(csv_rows)
    depth_metrics: List[Dict[str, Any]] = []
    drag_sum = 0

    for depth in sorted(grouped.keys()):
        rows = grouped[depth]
        scalar_load = 0
        vacuum_load = 0
        misalignment_load = 0
        associator_exposure = 0

        for row in rows:
            state = _decode_state_base8(str(row["state_base8"]))
            scalar_load += _coeff_l1(state[0])
            vacuum_load += _coeff_l1(state[7])
            if _support_outside_allowed(state, allowed_support):
                misalignment_load += 1
            contributors = int(row["contributor_count"])
            associator_exposure += max(0, contributors - 2)

        # Phase A: stabilization work is estimated as required ideal repairs.
        stabilization_work = misalignment_load
        drag_proxy = scalar_load + misalignment_load + stabilization_work + associator_exposure
        drag_sum += drag_proxy

        depth_metrics.append(
            {
                "depth": depth,
                "node_count": len(rows),
                "S_t": scalar_load,
                "V_t": vacuum_load,
                "M_t": misalignment_load,
                "C_t": stabilization_work,
                "A_t": associator_exposure,
                "D_t": drag_proxy,
            }
        )

    if not depth_metrics:
        return [], 0.0
    return depth_metrics, (drag_sum / len(depth_metrics))


def run_generation_drag_case(
    *,
    label: str,
    motif_id: str,
    depth_horizon: int,
    initial_edge_distance: int,
    background_id: str = "vacuum_doubled",
) -> Dict[str, Any]:
    depth_horizon = _require_int("depth_horizon", depth_horizon)
    initial_edge_distance = _require_int("initial_edge_distance", initial_edge_distance)
    motifs = _motif_state_map()
    if motif_id not in motifs:
        raise KeyError(f"unknown motif_id: {motif_id}")
    support = set(nonzero_support(motifs[motif_id]))
    # Keep scalar/vacuum channels observable but not automatically treated as leakage.
    support.update({0, 7})

    sim = simulate_full_lightcone(
        channel_id=f"generation_drag_{label}",
        depth_horizon=depth_horizon,
        initial_edge_distance=initial_edge_distance,
        left_motif_id=motif_id,
        right_motif_id=motif_id,
        background_id=background_id,
    )

    depth_metrics, drag_score = _compute_depth_metrics(
        csv_rows=sim["csv_rows"],
        allowed_support=support,
    )

    return {
        "label": label,
        "motif_id": motif_id,
        "allowed_support": sorted(int(x) for x in support),
        "drag_score": drag_score,
        "simulation_replay_hash": sim["replay_hash"],
        "depth_metrics": depth_metrics,
    }


def run_generation_drag_suite(
    *,
    mapping_path: str | Path = "calc/generation_drag_motif_mapping.json",
    depth_horizon: int = 12,
    initial_edge_distance: int = 5,
    background_id: str = "vacuum_doubled",
) -> Dict[str, Any]:
    depth_horizon = _require_int("depth_horizon", depth_horizon)
    initial_edge_distance = _require_int("initial_edge_distance", initial_edge_distance)
    mapping = _load_json(mapping_path)
    baseline_label = str(mapping["baseline_label"])
    motifs: List[Dict[str, Any]] = list(mapping.get("motifs", []))
    if not motifs:
        raise ValueError("mapping motifs must be non-empty")
    if baseline_label not in {str(m["label"]) for m in motifs}:
        raise ValueError(f"baseline_label not present in motifs: {baseline_label}")

    cases: List[Dict[str, Any]] = []
    for row in motifs:
        cases.append(
            run_generation_drag_case(
                label=str(row["label"]),
                motif_id=str(row["motif_id"]),
                depth_horizon=depth_horizon,
                initial_edge_distance=initial_edge_distance,
                background_id=background_id,
            )
        )

    by_label = {c["label"]: c for c in cases}
    baseline_drag = float(by_label[baseline_label]["drag_score"])
    if baseline_drag <= 0:
        raise ValueError("baseline drag score must be > 0")

    for c in cases:
        c["mu_eff"] = float(c["drag_score"]) / baseline_drag

    deterministic_payload = {
        "mapping_hash": _sha(mapping),
        "depth_horizon": depth_horizon,
        "initial_edge_distance": initial_edge_distance,
        "background_id": background_id,
        "cases": [
            {
                "label": c["label"],
                "motif_id": c["motif_id"],
                "drag_score": c["drag_score"],
                "mu_eff": c["mu_eff"],
                "simulation_replay_hash": c["simulation_replay_hash"],
                "depth_metrics": c["depth_metrics"],
            }
            for c in cases
        ],
    }

    return {
        "schema_version": "xor_generation_drag_metrics_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "rfc": "RFC-068",
        "mapping_path": str(mapping_path),
        "mapping_hash": _sha(mapping),
        "baseline_label": baseline_label,
        "config": {
            "depth_horizon": depth_horizon,
            "initial_edge_distance": initial_edge_distance,
            "background_id": background_id,
        },
        "cases": cases,
        "suite_replay_hash": _sha(deterministic_payload),
    }


def write_generation_drag_artifacts(
    dataset: Dict[str, Any],
    *,
    json_paths: Iterable[Path] | None = None,
    csv_paths: Iterable[Path] | None = None,
) -> None:
    if json_paths is None:
        json_paths = [Path("calc/xor_generation_drag_metrics.json")]
    if csv_paths is None:
        csv_paths = [Path("calc/xor_generation_drag_metrics.csv")]

    for path in json_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(dataset, indent=2) + "\n", encoding="utf-8")

    rows: List[Dict[str, Any]] = []
    for case in dataset["cases"]:
        for depth_row in case["depth_metrics"]:
            rows.append(
                {
                    "label": case["label"],
                    "motif_id": case["motif_id"],
                    "drag_score": case["drag_score"],
                    "mu_eff": case["mu_eff"],
                    "simulation_replay_hash": case["simulation_replay_hash"],
                    **depth_row,
                }
            )

    fieldnames = [
        "label",
        "motif_id",
        "drag_score",
        "mu_eff",
        "simulation_replay_hash",
        "depth",
        "node_count",
        "S_t",
        "V_t",
        "M_t",
        "C_t",
        "A_t",
        "D_t",
    ]

    for path in csv_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)


def main() -> int:
    dataset = run_generation_drag_suite(
        mapping_path="calc/generation_drag_motif_mapping.json",
        depth_horizon=12,
        initial_edge_distance=5,
        background_id="vacuum_doubled",
    )
    write_generation_drag_artifacts(
        dataset,
        json_paths=[
            Path("calc/xor_generation_drag_metrics.json"),
            Path("website/data/xor_generation_drag_metrics.json"),
        ],
        csv_paths=[
            Path("calc/xor_generation_drag_metrics.csv"),
            Path("website/data/xor_generation_drag_metrics.csv"),
        ],
    )
    print("Wrote calc/xor_generation_drag_metrics.json")
    print("Wrote calc/xor_generation_drag_metrics.csv")
    print("Wrote website/data/xor_generation_drag_metrics.json")
    print("Wrote website/data/xor_generation_drag_metrics.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
