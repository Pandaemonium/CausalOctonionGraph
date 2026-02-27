"""
calc/xor_e7_muon_ablation_scan.py

Pre-model preparation for e7-muon interaction studies.

Runs predeclared full-lightcone cases and computes:
1) per-depth e7 projection load,
2) per-depth scalar (e0) load,
3) projected ablation along e7 vs baseline case.
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from calc.xor_full_lightcone_engine import simulate_full_lightcone
from calc.xor_observables import decode_base8_int

GI = Tuple[int, int]
StateGI = Tuple[GI, GI, GI, GI, GI, GI, GI, GI]


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


def _l1(c: GI) -> int:
    return abs(int(c[0])) + abs(int(c[1]))


def _group_rows_by_depth(rows: Sequence[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
    out: Dict[int, List[Dict[str, Any]]] = {}
    for row in rows:
        out.setdefault(int(row["depth"]), []).append(row)
    return out


def _projection_profile(csv_rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped = _group_rows_by_depth(csv_rows)
    profile: List[Dict[str, Any]] = []
    for depth in sorted(grouped.keys()):
        rows = grouped[depth]
        e7_load = 0
        e0_load = 0
        for row in rows:
            st = _decode_state_base8(str(row["state_base8"]))
            e0_load += _l1(st[0])
            e7_load += _l1(st[7])
        node_count = len(rows)
        profile.append(
            {
                "depth": depth,
                "node_count": node_count,
                "e7_projection_load": e7_load,
                "e0_scalar_load": e0_load,
                "e7_projection_avg": (e7_load / node_count) if node_count > 0 else 0.0,
                "e0_scalar_avg": (e0_load / node_count) if node_count > 0 else 0.0,
            }
        )
    return profile


def _series_variation(values: Sequence[int]) -> int:
    if len(values) <= 1:
        return 0
    total = 0
    for i in range(1, len(values)):
        total += abs(int(values[i]) - int(values[i - 1]))
    return total


def run_case_projection(
    *,
    case_id: str,
    left_motif_id: str,
    right_motif_id: str,
    depth_horizon: int,
    initial_edge_distance: int,
    background_id: str,
) -> Dict[str, Any]:
    depth_horizon = _require_int("depth_horizon", depth_horizon)
    initial_edge_distance = _require_int("initial_edge_distance", initial_edge_distance)
    sim = simulate_full_lightcone(
        channel_id=f"e7_ablation_{case_id}",
        depth_horizon=depth_horizon,
        initial_edge_distance=initial_edge_distance,
        left_motif_id=left_motif_id,
        right_motif_id=right_motif_id,
        background_id=background_id,
    )
    profile = _projection_profile(sim["csv_rows"])
    e7_series = [int(r["e7_projection_load"]) for r in profile]
    e0_series = [int(r["e0_scalar_load"]) for r in profile]
    return {
        "case_id": case_id,
        "left_motif_id": left_motif_id,
        "right_motif_id": right_motif_id,
        "simulation_replay_hash": sim["replay_hash"],
        "projection_profile": profile,
        "summary": {
            "initial_e7_projection_load": e7_series[0] if e7_series else 0,
            "final_e7_projection_load": e7_series[-1] if e7_series else 0,
            "net_e7_projection_delta": (e7_series[-1] - e7_series[0]) if e7_series else 0,
            "e7_projection_total_variation": _series_variation(e7_series),
            "initial_e0_scalar_load": e0_series[0] if e0_series else 0,
            "final_e0_scalar_load": e0_series[-1] if e0_series else 0,
            "net_e0_scalar_delta": (e0_series[-1] - e0_series[0]) if e0_series else 0,
        },
    }


def run_e7_muon_ablation_suite(
    *,
    conditions_path: str | Path = "calc/e7_muon_ablation_conditions.json",
) -> Dict[str, Any]:
    cfg = _load_json(conditions_path)
    baseline_case_id = str(cfg["baseline_case_id"])
    depth_horizon = _require_int("depth_horizon", cfg["depth_horizon"])
    initial_edge_distance = _require_int("initial_edge_distance", cfg["initial_edge_distance"])
    background_id = str(cfg.get("background_id", "vacuum_doubled"))
    cases_spec = list(cfg.get("cases", []))
    if not cases_spec:
        raise ValueError("conditions cases must be non-empty")

    cases: List[Dict[str, Any]] = []
    for row in cases_spec:
        cases.append(
            run_case_projection(
                case_id=str(row["case_id"]),
                left_motif_id=str(row["left_motif_id"]),
                right_motif_id=str(row["right_motif_id"]),
                depth_horizon=depth_horizon,
                initial_edge_distance=initial_edge_distance,
                background_id=background_id,
            )
        )

    by_case = {c["case_id"]: c for c in cases}
    if baseline_case_id not in by_case:
        raise ValueError(f"baseline_case_id not present in cases: {baseline_case_id}")

    baseline_profile = by_case[baseline_case_id]["projection_profile"]
    baseline_by_depth = {int(r["depth"]): int(r["e7_projection_load"]) for r in baseline_profile}

    for case in cases:
        projected_rows: List[Dict[str, Any]] = []
        cumulative_ablation = 0
        for row in case["projection_profile"]:
            d = int(row["depth"])
            base = int(baseline_by_depth[d])
            cur = int(row["e7_projection_load"])
            proj = max(0, base - cur)
            cumulative_ablation += proj
            projected_rows.append(
                {
                    "depth": d,
                    "baseline_e7_projection_load": base,
                    "case_e7_projection_load": cur,
                    "projected_ablation_vs_baseline": proj,
                }
            )
        case["projected_e7_ablation"] = projected_rows
        case["summary"]["cumulative_projected_ablation_vs_baseline"] = cumulative_ablation

    deterministic_payload = {
        "conditions_hash": _sha(cfg),
        "cases": [
            {
                "case_id": c["case_id"],
                "simulation_replay_hash": c["simulation_replay_hash"],
                "summary": c["summary"],
                "projection_profile": c["projection_profile"],
                "projected_e7_ablation": c["projected_e7_ablation"],
            }
            for c in cases
        ],
    }

    return {
        "schema_version": "xor_e7_muon_ablation_scan_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "rfc_scope": "RFC-068 pre-model preparation",
        "conditions_path": str(conditions_path),
        "conditions_hash": _sha(cfg),
        "baseline_case_id": baseline_case_id,
        "config": {
            "depth_horizon": depth_horizon,
            "initial_edge_distance": initial_edge_distance,
            "background_id": background_id,
        },
        "cases": cases,
        "suite_replay_hash": _sha(deterministic_payload),
    }


def write_e7_muon_ablation_artifacts(
    dataset: Dict[str, Any],
    *,
    json_paths: Iterable[Path] | None = None,
    csv_paths: Iterable[Path] | None = None,
) -> None:
    if json_paths is None:
        json_paths = [Path("calc/xor_e7_muon_ablation_scan.json")]
    if csv_paths is None:
        csv_paths = [Path("calc/xor_e7_muon_ablation_scan.csv")]

    for p in json_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(dataset, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "case_id",
        "left_motif_id",
        "right_motif_id",
        "simulation_replay_hash",
        "depth",
        "node_count",
        "e7_projection_load",
        "e0_scalar_load",
        "e7_projection_avg",
        "e0_scalar_avg",
        "baseline_e7_projection_load",
        "projected_ablation_vs_baseline",
    ]

    rows: List[Dict[str, Any]] = []
    for case in dataset["cases"]:
        by_depth = {
            int(r["depth"]): int(r["projected_ablation_vs_baseline"])
            for r in case["projected_e7_ablation"]
        }
        baseline_depth = {
            int(r["depth"]): int(r["baseline_e7_projection_load"])
            for r in case["projected_e7_ablation"]
        }
        for row in case["projection_profile"]:
            depth = int(row["depth"])
            rows.append(
                {
                    "case_id": case["case_id"],
                    "left_motif_id": case["left_motif_id"],
                    "right_motif_id": case["right_motif_id"],
                    "simulation_replay_hash": case["simulation_replay_hash"],
                    "depth": depth,
                    "node_count": row["node_count"],
                    "e7_projection_load": row["e7_projection_load"],
                    "e0_scalar_load": row["e0_scalar_load"],
                    "e7_projection_avg": row["e7_projection_avg"],
                    "e0_scalar_avg": row["e0_scalar_avg"],
                    "baseline_e7_projection_load": baseline_depth[depth],
                    "projected_ablation_vs_baseline": by_depth[depth],
                }
            )

    for p in csv_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for row in rows:
                w.writerow(row)


def main() -> int:
    ds = run_e7_muon_ablation_suite(conditions_path="calc/e7_muon_ablation_conditions.json")
    write_e7_muon_ablation_artifacts(
        ds,
        json_paths=[
            Path("calc/xor_e7_muon_ablation_scan.json"),
            Path("website/data/xor_e7_muon_ablation_scan.json"),
        ],
        csv_paths=[
            Path("calc/xor_e7_muon_ablation_scan.csv"),
            Path("website/data/xor_e7_muon_ablation_scan.csv"),
        ],
    )
    print("Wrote calc/xor_e7_muon_ablation_scan.json")
    print("Wrote calc/xor_e7_muon_ablation_scan.csv")
    print("Wrote website/data/xor_e7_muon_ablation_scan.json")
    print("Wrote website/data/xor_e7_muon_ablation_scan.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
