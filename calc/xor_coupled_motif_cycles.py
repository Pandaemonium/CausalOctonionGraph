"""
calc/xor_coupled_motif_cycles.py

Deterministic coupled two-motif cycle analysis on top of the XOR gate kernel.

Goal:
  - capture higher-order periods that do not appear in isolated one-motif scans,
  - persist replayable pair-cycle traces for analysis and website display.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any

from calc.xor_stable_motif_scan import (
    StateVec,
    scan_triad_stability,
    stable_rows,
    triad_seed_state,
)
from calc.xor_update_rule import coupled_pair_round, dominant_nonzero_idx


def pair_step(
    state_a: StateVec,
    state_b: StateVec,
    triad_a: tuple[int, int, int],
    triad_b: tuple[int, int, int],
) -> tuple[StateVec, StateVec]:
    """
    One deterministic coupled round:
      1) each motif applies internal alternating triad update,
      2) each receives a cross-message operator from the partner's dominant channel.
    """
    return coupled_pair_round(
        state_a,
        state_b,
        triad_a=triad_a,
        triad_b=triad_b,
        internal_mode="alternating",
    )


def _pair_state_key(a: StateVec, b: StateVec) -> tuple[StateVec, StateVec]:
    return (a, b)


def detect_pair_cycle(
    triad_a: tuple[int, int, int],
    triad_b: tuple[int, int, int],
    max_steps: int = 512,
) -> dict[str, Any]:
    """
    Simulate coupled dynamics until first repeated pair-state.
    """
    a = triad_seed_state(tuple(sorted(triad_a)))
    b = triad_seed_state(tuple(sorted(triad_b)))

    seen: dict[tuple[StateVec, StateVec], int] = {}
    trace: list[dict[str, Any]] = []
    key = _pair_state_key(a, b)
    seen[key] = 0

    # Record initial state
    trace.append(
        {
            "step": 0,
            "a_vector": list(a),
            "b_vector": list(b),
            "a_dominant_idx": dominant_nonzero_idx(a),
            "b_dominant_idx": dominant_nonzero_idx(b),
        }
    )

    for step in range(1, max_steps + 1):
        a, b = pair_step(a, b, triad_a=triad_a, triad_b=triad_b)
        trace.append(
            {
                "step": step,
                "a_vector": list(a),
                "b_vector": list(b),
                "a_dominant_idx": dominant_nonzero_idx(a),
                "b_dominant_idx": dominant_nonzero_idx(b),
            }
        )
        key = _pair_state_key(a, b)
        if key in seen:
            cycle_start = seen[key]
            return {
                "cycle_found": True,
                "cycle_start": cycle_start,
                "period": step - cycle_start,
                "steps_recorded": len(trace),
                "trace": trace,
            }
        seen[key] = step

    return {
        "cycle_found": False,
        "cycle_start": None,
        "period": None,
        "steps_recorded": len(trace),
        "trace": trace,
    }


def stable_triad_set() -> list[tuple[int, int, int]]:
    """
    Canonical support-stable triads under isolated alternating schedule.
    """
    rows = scan_triad_stability(schedule_mode="alternating")
    return [r.triad for r in stable_rows(rows)]


def build_coupled_cycle_dataset(max_steps: int = 512) -> dict[str, Any]:
    triads = stable_triad_set()
    pairs_payload: list[dict[str, Any]] = []
    csv_rows: list[dict[str, Any]] = []

    for ta, tb in combinations(triads, 2):
        sim = detect_pair_cycle(ta, tb, max_steps=max_steps)
        pair_id = f"{ta}-{tb}"
        pairs_payload.append(
            {
                "pair_id": pair_id,
                "triad_a": list(ta),
                "triad_b": list(tb),
                "cycle_found": sim["cycle_found"],
                "cycle_start": sim["cycle_start"],
                "period": sim["period"],
                "steps_recorded": sim["steps_recorded"],
                "trace": sim["trace"],
            }
        )
        csv_rows.append(
            {
                "pair_id": pair_id,
                "triad_a": str(ta),
                "triad_b": str(tb),
                "cycle_found": sim["cycle_found"],
                "cycle_start": sim["cycle_start"],
                "period": sim["period"],
                "steps_recorded": sim["steps_recorded"],
                "period_gt_4": (sim["period"] is not None and sim["period"] > 4),
            }
        )

    period_hist: dict[str, int] = {}
    for row in csv_rows:
        p = row["period"]
        key = "None" if p is None else str(p)
        period_hist[key] = period_hist.get(key, 0) + 1

    return {
        "schema_version": "xor_coupled_motif_cycles_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "notes": [
            "Coupled dynamics are deterministic and purely structural.",
            "Higher periods are expected from motif coupling even when isolated motifs are period <= 4.",
        ],
        "triads": [list(t) for t in triads],
        "pair_count": len(csv_rows),
        "period_histogram": period_hist,
        "pairs": pairs_payload,
        "csv_rows": csv_rows,
    }


def write_coupled_cycle_artifacts(
    dataset: dict[str, Any],
    json_paths: list[Path] | None = None,
    csv_paths: list[Path] | None = None,
) -> None:
    if json_paths is None:
        json_paths = [Path("calc/xor_coupled_motif_cycles.json")]
    if csv_paths is None:
        csv_paths = [Path("calc/xor_coupled_motif_cycles.csv")]

    for path in json_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(dataset, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "pair_id",
        "triad_a",
        "triad_b",
        "cycle_found",
        "cycle_start",
        "period",
        "steps_recorded",
        "period_gt_4",
    ]
    for path in csv_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in dataset["csv_rows"]:
                writer.writerow(row)


def main() -> int:
    dataset = build_coupled_cycle_dataset(max_steps=512)
    write_coupled_cycle_artifacts(
        dataset,
        json_paths=[
            Path("calc/xor_coupled_motif_cycles.json"),
            Path("website/data/xor_coupled_motif_cycles.json"),
        ],
        csv_paths=[
            Path("calc/xor_coupled_motif_cycles.csv"),
            Path("website/data/xor_coupled_motif_cycles.csv"),
        ],
    )
    print("Wrote calc/xor_coupled_motif_cycles.json")
    print("Wrote calc/xor_coupled_motif_cycles.csv")
    print("Wrote website/data/xor_coupled_motif_cycles.json")
    print("Wrote website/data/xor_coupled_motif_cycles.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
