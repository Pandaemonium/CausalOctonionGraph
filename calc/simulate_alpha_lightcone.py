"""
Deterministic ALPHA-001 simulation over fully predetermined lightcones.

Protocol:
1) load frozen conditions from calc/alpha_lightcone_conditions.json,
2) construct only predeclared channel x phase-class x initial-distance runs,
3) run XOR/Furey predetermined-lightcone monitor for each run
   (current backend is reduced two-body monitor; canonical interaction-scope policy
   is enforced in conditions and must be satisfied by the next full-cone engine),
4) write deterministic artifacts for downstream alpha extraction.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

try:
    from calc.xor_charge_sign_interaction_matrix import temporal_commit
    from calc.xor_furey_ideals import (
        StateGI,
        furey_dual_electron_doubled,
        furey_electron_doubled,
        state_basis,
    )
    from calc.xor_furey_lightcone_monitor import run_pair_on_predetermined_lightcone
except ModuleNotFoundError:  # direct script execution fallback
    from xor_charge_sign_interaction_matrix import temporal_commit
    from xor_furey_ideals import (
        StateGI,
        furey_dual_electron_doubled,
        furey_electron_doubled,
        state_basis,
    )
    from xor_furey_lightcone_monitor import run_pair_on_predetermined_lightcone


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONDITIONS = Path(__file__).with_name("alpha_lightcone_conditions.json")
OUT_JSON = ROOT / "sources" / "alpha_lightcone_simulation.json"
OUT_CSV = ROOT / "sources" / "alpha_lightcone_simulation_runs.csv"


def _sha(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def load_conditions(path: Path | None = None) -> dict[str, Any]:
    p = path or DEFAULT_CONDITIONS
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def _assert_no_forbidden_keys(obj: Any) -> None:
    forbidden = {"attenuation", "fit_param", "fitted_param", "tuned_param"}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in forbidden:
                raise ValueError(f"Forbidden key in conditions: {k}")
            _assert_no_forbidden_keys(v)
        return
    if isinstance(obj, list):
        for v in obj:
            _assert_no_forbidden_keys(v)


def validate_conditions(data: dict[str, Any]) -> None:
    if data.get("mode") != "deterministic_full_cone_preconditioned":
        raise ValueError("conditions.mode must be deterministic_full_cone_preconditioned")
    if "target" not in data or "alpha" not in data["target"]:
        raise ValueError("conditions.target.alpha is required")
    if "kernel" not in data or not isinstance(data["kernel"], dict):
        raise ValueError("conditions.kernel must be provided")
    if "channels" not in data or not isinstance(data["channels"], list) or not data["channels"]:
        raise ValueError("conditions.channels must be a non-empty list")
    if "phase_classes" not in data or not isinstance(data["phase_classes"], list) or not data["phase_classes"]:
        raise ValueError("conditions.phase_classes must be a non-empty list")
    if "initial_edge_distances" not in data or not isinstance(data["initial_edge_distances"], list):
        raise ValueError("conditions.initial_edge_distances must be a list")

    _assert_no_forbidden_keys(data)

    kernel = data["kernel"]
    if kernel.get("distance_semantics") != "edge_separation_count":
        raise ValueError("kernel.distance_semantics must be edge_separation_count")
    if kernel.get("time_semantics") != "topological_depth":
        raise ValueError("kernel.time_semantics must be topological_depth")
    if kernel.get("no_spawn") is not True:
        raise ValueError("kernel.no_spawn must be true")
    if kernel.get("full_lightcone_preconditioned") is not True:
        raise ValueError("kernel.full_lightcone_preconditioned must be true")
    if kernel.get("interaction_scope") != "full_past_lightcone_all_contributors":
        raise ValueError("kernel.interaction_scope must be full_past_lightcone_all_contributors")
    if kernel.get("interaction_scope_canonical") is not True:
        raise ValueError("kernel.interaction_scope_canonical must be true")

    seen_channels: set[str] = set()
    control_count = 0
    signal_count = 0
    for row in data["channels"]:
        cid = row.get("channel_id")
        if not cid:
            raise ValueError("each channel requires channel_id")
        if cid in seen_channels:
            raise ValueError(f"duplicate channel_id: {cid}")
        seen_channels.add(cid)
        role = row.get("role")
        if role == "control":
            control_count += 1
        elif role == "signal":
            signal_count += 1
        else:
            raise ValueError(f"channel {cid}: role must be signal/control")
        if "left_motif_id" not in row or "right_motif_id" not in row:
            raise ValueError(f"channel {cid}: motif ids required")

    if control_count != 1:
        raise ValueError("exactly one control channel is required")
    if signal_count < 1:
        raise ValueError("at least one signal channel is required")

    seen_phase: set[str] = set()
    for row in data["phase_classes"]:
        pid = row.get("phase_id")
        if not pid:
            raise ValueError("phase class missing phase_id")
        if pid in seen_phase:
            raise ValueError(f"duplicate phase_id: {pid}")
        seen_phase.add(pid)
        if int(row.get("left_precommit_ticks", -1)) < 0:
            raise ValueError(f"{pid}: left_precommit_ticks must be >= 0")
        if int(row.get("right_precommit_ticks", -1)) < 0:
            raise ValueError(f"{pid}: right_precommit_ticks must be >= 0")

    for d0 in data["initial_edge_distances"]:
        if int(d0) < 1:
            raise ValueError("all initial_edge_distances must be >= 1")

    if int(data.get("depth_horizon", -1)) < 2:
        raise ValueError("depth_horizon must be >= 2")


def _motif_by_id(motif_id: str) -> StateGI:
    if motif_id == "furey_electron_doubled":
        return furey_electron_doubled()
    if motif_id == "furey_dual_electron_doubled":
        return furey_dual_electron_doubled()
    if motif_id == "identity_e0":
        return state_basis(0, (1, 0))
    raise KeyError(f"unknown motif_id: {motif_id}")


def _apply_precommit_ticks(state: StateGI, n_ticks: int) -> StateGI:
    out = state
    for _ in range(n_ticks):
        out = temporal_commit(out)
    return out


def _sanitize_monitor_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Drop non-deterministic timestamp fields from run payload."""
    out = dict(payload)
    out.pop("generated_at_utc", None)
    return out


def run_simulation_dataset(path: Path | None = None) -> dict[str, Any]:
    conditions = load_conditions(path)
    validate_conditions(conditions)

    depth_horizon = int(conditions["depth_horizon"])
    runs: List[Dict[str, Any]] = []

    for channel in conditions["channels"]:
        for phase in conditions["phase_classes"]:
            for d0 in conditions["initial_edge_distances"]:
                left = _motif_by_id(channel["left_motif_id"])
                right = _motif_by_id(channel["right_motif_id"])
                left = _apply_precommit_ticks(left, int(phase["left_precommit_ticks"]))
                right = _apply_precommit_ticks(right, int(phase["right_precommit_ticks"]))

                monitor = run_pair_on_predetermined_lightcone(
                    left_state=left,
                    right_state=right,
                    depth_horizon=depth_horizon,
                    initial_edge_distance=int(d0),
                )
                monitor = _sanitize_monitor_payload(monitor)

                run_id = (
                    f"{channel['channel_id']}__{phase['phase_id']}__d{int(d0)}"
                )
                run_record = {
                    "run_id": run_id,
                    "channel_id": channel["channel_id"],
                    "role": channel["role"],
                    "expected_polarity": channel["expected_polarity"],
                    "phase_id": phase["phase_id"],
                    "left_precommit_ticks": int(phase["left_precommit_ticks"]),
                    "right_precommit_ticks": int(phase["right_precommit_ticks"]),
                    "initial_edge_distance": int(d0),
                    "depth_horizon": depth_horizon,
                    "left_motif_id": channel["left_motif_id"],
                    "right_motif_id": channel["right_motif_id"],
                    "monitor": monitor,
                }
                run_record["run_checksum"] = _sha(
                    {
                        "run_id": run_id,
                        "channel_id": run_record["channel_id"],
                        "phase_id": run_record["phase_id"],
                        "initial_edge_distance": run_record["initial_edge_distance"],
                        "monitor": monitor,
                    }
                )
                runs.append(run_record)

    runs_sorted = sorted(runs, key=lambda r: r["run_id"])
    conditions_checksum = _sha(conditions)
    deterministic_payload = {
        "schema_version": "alpha_lightcone_simulation_v1",
        "conditions_checksum": conditions_checksum,
        "run_count": len(runs_sorted),
        "runs": runs_sorted,
    }
    replay_hash = _sha(deterministic_payload)

    return {
        "schema_version": "alpha_lightcone_simulation_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "conditions_checksum": conditions_checksum,
        "run_count": len(runs_sorted),
        "runs": runs_sorted,
        "replay_hash": replay_hash,
    }


def write_simulation_artifacts(
    dataset: dict[str, Any],
    json_paths: list[Path] | None = None,
    csv_paths: list[Path] | None = None,
) -> None:
    if json_paths is None:
        json_paths = [OUT_JSON]
    if csv_paths is None:
        csv_paths = [OUT_CSV]

    for p in json_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(dataset, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    fieldnames = [
        "run_id",
        "channel_id",
        "role",
        "phase_id",
        "initial_edge_distance",
        "depth_horizon",
        "interaction_event_count",
        "final_distance_future",
        "distance_delta_total",
        "distance_change_depth_count",
        "run_checksum",
    ]
    rows: List[Dict[str, Any]] = []
    for run in dataset["runs"]:
        summary = run["monitor"]["summary"]
        rows.append(
            {
                "run_id": run["run_id"],
                "channel_id": run["channel_id"],
                "role": run["role"],
                "phase_id": run["phase_id"],
                "initial_edge_distance": run["initial_edge_distance"],
                "depth_horizon": run["depth_horizon"],
                "interaction_event_count": summary["interaction_event_count"],
                "final_distance_future": summary["final_distance_future"],
                "distance_delta_total": summary["distance_delta_total"],
                "distance_change_depth_count": len(summary["distance_change_depths"]),
                "run_checksum": run["run_checksum"],
            }
        )

    for p in csv_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for row in rows:
                w.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic ALPHA lightcone simulation dataset")
    parser.add_argument("--conditions-file", type=Path, default=DEFAULT_CONDITIONS)
    parser.add_argument("--json", action="store_true", help="Print full JSON payload")
    parser.add_argument("--write-sources", action="store_true", help="Write sources artifacts")
    args = parser.parse_args()

    dataset = run_simulation_dataset(args.conditions_file)
    if args.write_sources:
        write_simulation_artifacts(dataset)
        print(f"Wrote {OUT_JSON}")
        print(f"Wrote {OUT_CSV}")
        return

    if args.json:
        print(json.dumps(dataset, indent=2, sort_keys=True))
        return

    print(
        f"alpha_lightcone_simulation: runs={dataset['run_count']}, "
        f"replay_hash={dataset['replay_hash'][:16]}..."
    )


if __name__ == "__main__":
    main()
