"""
calc/xor_particle_motif_cycles.py

Persist cycle-structure artifacts for XOR octonion motif simulations.

Outputs:
  - JSON with full state traces and cycle metadata
  - CSV with compact per-motif/per-policy period summaries
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from calc.conftest import FANO_CYCLES
from calc.xor_octonion_gate import Handedness
from calc.xor_stable_motif_scan import (
    StateVec,
    apply_basis_handed,
    fano_lines_one_indexed,
    motif_schedule,
    run_round,
    scan_triad_stability,
    triad_seed_state,
)
from calc.xor_update_rule import motif_round_update


@dataclass(frozen=True)
class TriadMotifSpec:
    motif_id: str
    title: str
    triad: tuple[int, int, int]
    tags: tuple[str, ...]


def _state_sparse(state: StateVec) -> dict[str, int]:
    out: dict[str, int] = {}
    for idx, coeff in enumerate(state):
        if coeff != 0:
            out[f"e{idx}"] = int(coeff)
    return out


def _simulate_cycle(
    initial: StateVec,
    step_fn: Callable[[StateVec], StateVec],
    max_steps: int = 128,
) -> dict[str, Any]:
    """
    Simulate until the first repeated state is observed or max_steps is reached.
    """
    seen: dict[StateVec, int] = {}
    trace: list[dict[str, Any]] = []
    cur = initial

    for step in range(max_steps + 1):
        trace.append(
            {
                "step": step,
                "vector": list(cur),
                "sparse": _state_sparse(cur),
            }
        )
        if cur in seen:
            cycle_start = seen[cur]
            period = step - cycle_start
            return {
                "cycle_found": True,
                "cycle_start": cycle_start,
                "period": period,
                "steps_recorded": step + 1,
                "trace": trace,
            }
        seen[cur] = step
        cur = step_fn(cur)

    return {
        "cycle_found": False,
        "cycle_start": None,
        "period": None,
        "steps_recorded": len(trace),
        "trace": trace,
    }


def _support_closure_from_trace(
    trace: list[dict[str, Any]],
    motif_support_sorted: tuple[int, int, int],
) -> bool:
    allowed = set(motif_support_sorted) | {0}
    for row in trace:
        vec = row.get("vector", [])
        for idx, coeff in enumerate(vec):
            if coeff != 0 and idx not in allowed:
                return False
    return True


def _triad_specs() -> list[TriadMotifSpec]:
    """
    Build named motif set:
      - all 7 stable Fano-line triads (candidate single-particle motifs)
      - explicit electron scaffold alias
      - explicit proton-proto non-collinear scaffold
    """
    out: list[TriadMotifSpec] = []
    for idx, (a, b, c) in enumerate(FANO_CYCLES, start=1):
        triad = (a + 1, b + 1, c + 1)
        out.append(
            TriadMotifSpec(
                motif_id=f"fano_line_l{idx}",
                title=f"Fano line L{idx}",
                triad=triad,
                tags=("stable_candidate", "fano_line"),
            )
        )

    out.append(
        TriadMotifSpec(
            motif_id="electron_line_l1",
            title="Electron scaffold line",
            triad=(1, 2, 3),
            tags=("electron_scaffold", "stable_candidate"),
        )
    )
    out.append(
        TriadMotifSpec(
            motif_id="proton_proto_t124",
            title="Proton-proto triad",
            triad=(1, 2, 4),
            tags=("proton_proto_scaffold", "noncollinear"),
        )
    )
    return out


def _policy_definitions(
    triad: tuple[int, int, int],
) -> dict[str, Callable[[StateVec], StateVec]]:
    oriented = triad
    return {
        "internal_oriented_alternating": lambda s: run_round(
            s, motif_schedule(oriented, mode="alternating")
        ),
        "internal_oriented_left_only": lambda s: run_round(
            s, motif_schedule(oriented, mode="left_only")
        ),
        "internal_oriented_right_only": lambda s: run_round(
            s, motif_schedule(oriented, mode="right_only")
        ),
        "vacuum_left_e7": lambda s: apply_basis_handed(s, 7, Handedness.LEFT),
        "vacuum_right_e7": lambda s: apply_basis_handed(s, 7, Handedness.RIGHT),
        "temporal_first_internal_alternating_left": lambda s: motif_round_update(
            s,
            triad=oriented,
            temporal_first=True,
            temporal_op_idx=7,
            temporal_hand=Handedness.LEFT,
            internal_mode="alternating",
        ),
        "internal_alternating_then_temporal_left": lambda s: motif_round_update(
            s,
            triad=oriented,
            temporal_first=False,
            temporal_op_idx=7,
            temporal_hand=Handedness.LEFT,
            internal_mode="alternating",
        ),
    }


def build_particle_motif_cycle_dataset(max_steps: int = 128) -> dict[str, Any]:
    lines = fano_lines_one_indexed()
    stable_set = {row.triad for row in scan_triad_stability(schedule_mode="alternating") if row.support_stable}

    motifs_payload: list[dict[str, Any]] = []
    csv_rows: list[dict[str, Any]] = []

    for spec in _triad_specs():
        triad_sorted = tuple(sorted(spec.triad))
        seed = triad_seed_state(triad_sorted)
        policies = _policy_definitions(spec.triad)

        policy_out: dict[str, Any] = {}
        for policy_id, step_fn in policies.items():
            sim = _simulate_cycle(seed, step_fn=step_fn, max_steps=max_steps)
            sim["support_closure_within_motif_plus_e0"] = _support_closure_from_trace(
                sim["trace"],
                motif_support_sorted=triad_sorted,
            )
            policy_out[policy_id] = sim
            csv_rows.append(
                {
                    "motif_id": spec.motif_id,
                    "triad": str(spec.triad),
                    "policy_id": policy_id,
                    "cycle_found": sim["cycle_found"],
                    "cycle_start": sim["cycle_start"],
                    "period": sim["period"],
                    "steps_recorded": sim["steps_recorded"],
                    "support_closure_within_motif_plus_e0": sim[
                        "support_closure_within_motif_plus_e0"
                    ],
                    "is_fano_line": triad_sorted in lines,
                    "is_stable_candidate": triad_sorted in stable_set,
                }
            )

        motifs_payload.append(
            {
                "motif_id": spec.motif_id,
                "title": spec.title,
                "triad_oriented": list(spec.triad),
                "triad_support_sorted": list(triad_sorted),
                "seed_vector": list(seed),
                "seed_sparse": _state_sparse(seed),
                "is_fano_line": triad_sorted in lines,
                "is_stable_candidate": triad_sorted in stable_set,
                "tags": list(spec.tags),
                "policies": policy_out,
            }
        )

    return {
        "schema_version": "xor_particle_motif_cycles_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "basis_index_map": {str(i): f"e{i}" for i in range(8)},
        "notes": [
            "Cycle data is purely structural under XOR-gate dynamics.",
            "No physical calibration constants are used.",
        ],
        "stable_motif_definition": "support-closure under internal alternating schedule",
        "motifs": motifs_payload,
        "csv_rows": csv_rows,
    }


def write_particle_motif_cycle_artifacts(
    dataset: dict[str, Any],
    json_paths: list[Path] | None = None,
    csv_paths: list[Path] | None = None,
) -> None:
    if json_paths is None:
        json_paths = [Path("calc/xor_particle_motif_cycles.json")]
    if csv_paths is None:
        csv_paths = [Path("calc/xor_particle_motif_cycles.csv")]

    for path in json_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(dataset, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "motif_id",
        "triad",
        "policy_id",
        "cycle_found",
        "cycle_start",
        "period",
        "steps_recorded",
        "support_closure_within_motif_plus_e0",
        "is_fano_line",
        "is_stable_candidate",
    ]
    for path in csv_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in dataset["csv_rows"]:
                writer.writerow(row)


def main() -> int:
    dataset = build_particle_motif_cycle_dataset(max_steps=128)
    write_particle_motif_cycle_artifacts(
        dataset,
        json_paths=[
            Path("calc/xor_particle_motif_cycles.json"),
            Path("website/data/xor_particle_motif_cycles.json"),
        ],
        csv_paths=[
            Path("calc/xor_particle_motif_cycles.csv"),
            Path("website/data/xor_particle_motif_cycles.csv"),
        ],
    )
    print("Wrote calc/xor_particle_motif_cycles.json")
    print("Wrote calc/xor_particle_motif_cycles.csv")
    print("Wrote website/data/xor_particle_motif_cycles.json")
    print("Wrote website/data/xor_particle_motif_cycles.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
