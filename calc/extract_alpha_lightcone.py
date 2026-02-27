"""
Extract ALPHA-001 estimates from deterministic lightcone simulation payload.

Inputs:
  - calc/alpha_lightcone_conditions.json (frozen policy)
  - sources/alpha_lightcone_simulation.json (deterministic run dataset)

Method:
  - build per-depth discrete acceleration from distance traces,
  - subtract matched control-channel acceleration,
  - compute alpha_hat(depth) = mu_eff * |a_em(depth)| * d(depth)^2,
  - aggregate over a predeclared plateau window.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    from calc.simulate_alpha_lightcone import DEFAULT_CONDITIONS, load_conditions, validate_conditions
except ModuleNotFoundError:  # direct script execution fallback
    from simulate_alpha_lightcone import DEFAULT_CONDITIONS, load_conditions, validate_conditions


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SIMULATION_DATASET = ROOT / "sources" / "alpha_lightcone_simulation.json"
OUT_JSON = ROOT / "sources" / "alpha_lightcone_extraction.json"
OUT_MD = ROOT / "sources" / "alpha_lightcone_report.md"


def _sha(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def load_simulation_dataset(path: Path | None = None) -> dict[str, Any]:
    p = path or DEFAULT_SIMULATION_DATASET
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def _distance_series(run: dict[str, Any]) -> List[Tuple[int, int]]:
    trace = run["monitor"]["trace"]
    return [(int(row["depth"]), int(row["distance_future"])) for row in trace]


def _discrete_acceleration(depth_distance: List[Tuple[int, int]]) -> Dict[int, int]:
    if len(depth_distance) < 3:
        return {}
    acc: Dict[int, int] = {}
    for i in range(1, len(depth_distance) - 1):
        d_prev = depth_distance[i - 1][1]
        depth = depth_distance[i][0]
        d_cur = depth_distance[i][1]
        d_next = depth_distance[i + 1][1]
        acc[depth] = d_next - 2 * d_cur + d_prev
    return acc


def _median(values: List[float]) -> float | None:
    if not values:
        return None
    return float(statistics.median(values))


def _mad(values: List[float], center: float) -> float | None:
    if not values:
        return None
    return float(statistics.median([abs(v - center) for v in values]))


def _build_control_index(runs: List[dict[str, Any]]) -> Dict[Tuple[str, int], dict[str, Any]]:
    idx: Dict[Tuple[str, int], dict[str, Any]] = {}
    for run in runs:
        if run["role"] != "control":
            continue
        key = (run["phase_id"], int(run["initial_edge_distance"]))
        idx[key] = run
    return idx


def _eligible_depth(
    depth: int,
    distance: int,
    depth_horizon: int,
    plateau: dict[str, Any],
) -> bool:
    min_depth = int(plateau["min_depth"])
    max_depth = int(plateau["max_depth"])
    interior_margin = int(plateau["interior_margin"])
    min_distance = int(plateau["min_distance"])
    max_distance = int(plateau["max_distance"])
    if depth < min_depth or depth > max_depth:
        return False
    if depth < interior_margin or depth > (depth_horizon - interior_margin):
        return False
    if distance < min_distance or distance > max_distance:
        return False
    return True


def extract_alpha_from_dataset(
    simulation: dict[str, Any],
    conditions: dict[str, Any],
) -> dict[str, Any]:
    validate_conditions(conditions)
    if simulation.get("schema_version") != "alpha_lightcone_simulation_v1":
        raise ValueError("unsupported simulation schema_version")

    if simulation.get("conditions_checksum") != _sha(conditions):
        raise ValueError("simulation conditions checksum mismatch")

    mu_eff = float(conditions["mass_normalization"]["mu_eff"])
    target_alpha = float(conditions["target"]["alpha"])
    plateau = conditions["plateau_rule"]
    require_nonzero_a_em = bool(plateau.get("require_nonzero_a_em", False))
    depth_horizon = int(conditions["depth_horizon"])

    runs = simulation["runs"]
    control_idx = _build_control_index(runs)
    if not control_idx:
        raise ValueError("no control runs found in simulation dataset")

    per_run_rows: List[dict[str, Any]] = []
    pooled_signal_samples: List[float] = []
    per_channel_samples: Dict[str, List[float]] = {}

    for run in runs:
        if run["role"] != "signal":
            continue
        key = (run["phase_id"], int(run["initial_edge_distance"]))
        if key not in control_idx:
            raise ValueError(f"missing matched control for signal run {run['run_id']}")
        ctrl = control_idx[key]

        sig_series = _distance_series(run)
        ctl_series = _distance_series(ctrl)
        sig_acc = _discrete_acceleration(sig_series)
        ctl_acc = _discrete_acceleration(ctl_series)
        sig_dist = {depth: dist for depth, dist in sig_series}

        alpha_samples: List[float] = []
        sample_rows: List[dict[str, Any]] = []
        for depth in sorted(sig_acc.keys()):
            if depth not in ctl_acc or depth not in sig_dist:
                continue
            d = int(sig_dist[depth])
            if not _eligible_depth(depth, d, depth_horizon, plateau):
                continue
            a_signal = int(sig_acc[depth])
            a_control = int(ctl_acc[depth])
            a_em = a_signal - a_control
            if require_nonzero_a_em and a_em == 0:
                continue
            alpha_hat = mu_eff * abs(float(a_em)) * float(d * d)
            alpha_samples.append(alpha_hat)
            sample_rows.append(
                {
                    "depth": depth,
                    "distance": d,
                    "a_signal": a_signal,
                    "a_control": a_control,
                    "a_em": a_em,
                    "alpha_hat": alpha_hat,
                }
            )

        alpha_median = _median(alpha_samples)
        alpha_mad = _mad(alpha_samples, alpha_median) if alpha_median is not None else None
        rel_gap = (
            abs(alpha_median - target_alpha) / target_alpha
            if alpha_median is not None and target_alpha != 0.0
            else None
        )

        row = {
            "run_id": run["run_id"],
            "channel_id": run["channel_id"],
            "phase_id": run["phase_id"],
            "initial_edge_distance": run["initial_edge_distance"],
            "matched_control_run_id": ctrl["run_id"],
            "sample_count": len(alpha_samples),
            "alpha_hat_median": alpha_median,
            "alpha_hat_mad": alpha_mad,
            "relative_gap_to_target": rel_gap,
            "samples": sample_rows,
        }
        per_run_rows.append(row)

        pooled_signal_samples.extend(alpha_samples)
        per_channel_samples.setdefault(run["channel_id"], []).extend(alpha_samples)

    per_channel_summary: Dict[str, dict[str, Any]] = {}
    for channel_id, vals in sorted(per_channel_samples.items()):
        med = _median(vals)
        mad = _mad(vals, med) if med is not None else None
        rel_gap = abs(med - target_alpha) / target_alpha if med is not None and target_alpha != 0.0 else None
        per_channel_summary[channel_id] = {
            "sample_count": len(vals),
            "alpha_hat_median": med,
            "alpha_hat_mad": mad,
            "relative_gap_to_target": rel_gap,
        }

    pooled_median = _median(pooled_signal_samples)
    pooled_mad = _mad(pooled_signal_samples, pooled_median) if pooled_median is not None else None
    pooled_rel_gap = (
        abs(pooled_median - target_alpha) / target_alpha
        if pooled_median is not None and target_alpha != 0.0
        else None
    )

    deterministic_payload = {
        "schema_version": "alpha_lightcone_extraction_v1",
        "simulation_replay_hash": simulation["replay_hash"],
        "conditions_checksum": simulation["conditions_checksum"],
        "mu_eff": mu_eff,
        "target_alpha": target_alpha,
        "per_run": per_run_rows,
        "per_channel": per_channel_summary,
        "pooled": {
            "sample_count": len(pooled_signal_samples),
            "alpha_hat_median": pooled_median,
            "alpha_hat_mad": pooled_mad,
            "relative_gap_to_target": pooled_rel_gap,
        },
    }
    deterministic_payload["replay_hash"] = _sha(deterministic_payload)
    return deterministic_payload


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# ALPHA Lightcone Extraction Report",
        "",
        f"- Simulation replay hash: `{payload['simulation_replay_hash'][:16]}...`",
        f"- Extraction replay hash: `{payload['replay_hash'][:16]}...`",
        f"- Conditions checksum: `{payload['conditions_checksum'][:16]}...`",
        f"- Mass normalization (mu_eff): {payload['mu_eff']}",
        f"- Target alpha: {payload['target_alpha']:.13f}",
        "",
        "## Per-Channel Summary",
        "",
        "| Channel | Samples | alpha_hat median | MAD | Relative gap |",
        "|---|---:|---:|---:|---:|",
    ]

    for channel_id, row in payload["per_channel"].items():
        lines.append(
            "| {cid} | {n} | {m:.12f} | {mad:.12f} | {gap:.2%} |".format(
                cid=channel_id,
                n=row["sample_count"],
                m=row["alpha_hat_median"] if row["alpha_hat_median"] is not None else float("nan"),
                mad=row["alpha_hat_mad"] if row["alpha_hat_mad"] is not None else float("nan"),
                gap=row["relative_gap_to_target"] if row["relative_gap_to_target"] is not None else float("nan"),
            )
        )

    pooled = payload["pooled"]
    lines.extend(
        [
            "",
            "## Pooled Signal Summary",
            f"- Samples: {pooled['sample_count']}",
            f"- alpha_hat median: {pooled['alpha_hat_median']}",
            f"- MAD: {pooled['alpha_hat_mad']}",
            f"- Relative gap to target: {pooled['relative_gap_to_target']}",
            "",
            "## Governance",
            "- Full predetermined lightcone policy enforced by frozen condition file.",
            "- Channel/phase/distance grid is predeclared; no output-driven selection.",
            "- Control subtraction is mandatory (matched by phase_id + initial_edge_distance).",
            "- No fitted attenuation parameter is used in extraction.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_extraction_artifacts(
    payload: dict[str, Any],
    json_paths: List[Path] | None = None,
    md_paths: List[Path] | None = None,
) -> None:
    if json_paths is None:
        json_paths = [OUT_JSON]
    if md_paths is None:
        md_paths = [OUT_MD]

    for p in json_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = _render_markdown(payload)
    for p in md_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(md, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract alpha_hat from deterministic lightcone simulation data")
    parser.add_argument("--simulation-json", type=Path, default=DEFAULT_SIMULATION_DATASET)
    parser.add_argument("--conditions-file", type=Path, default=DEFAULT_CONDITIONS)
    parser.add_argument("--json", action="store_true", help="Print JSON extraction payload")
    parser.add_argument("--write-sources", action="store_true", help="Write extraction artifacts to sources/")
    args = parser.parse_args()

    sim = load_simulation_dataset(args.simulation_json)
    conditions = load_conditions(args.conditions_file)
    payload = extract_alpha_from_dataset(simulation=sim, conditions=conditions)

    if args.write_sources:
        write_extraction_artifacts(payload)
        print(f"Wrote {OUT_JSON}")
        print(f"Wrote {OUT_MD}")
        return

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return

    pooled = payload["pooled"]
    print(
        f"alpha_lightcone_extraction: samples={pooled['sample_count']}, "
        f"median={pooled['alpha_hat_median']}, "
        f"rel_gap={pooled['relative_gap_to_target']}, "
        f"replay_hash={payload['replay_hash'][:16]}..."
    )


if __name__ == "__main__":
    main()
