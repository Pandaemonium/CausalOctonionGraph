"""
calc/xor_hydrogen_binding_scan.py

XCALC-103 scaffold: bridge structural hydrogen motif scaffold to XOR dynamics.

This module intentionally keeps scope structural:
1) motif overlap and line-incidence summary (Gate-1 compatible),
2) XOR cycle traces for electron/proton-proto motifs,
3) deterministic coupled two-motif period probe.

Not claimed here:
1) full proton closure,
2) physical hydrogen spectrum,
3) calibrated binding energies.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

from calc.conftest import FANO_CYCLES
from calc.hydrogen_binding import (
    ELECTRON_MOTIF,
    PROTON_PROTO_MOTIF,
    binding_proxy,
    classify_motif,
    line_through_pair,
    motif_overlap,
    shared_pair,
)
from calc.xor_furey_ideals import StateGI
from calc.xor_vector_spinor_phase_cycles import apply_operator, run_cycle_trace, vector_motif_state


def _one_index_cycles() -> list[tuple[int, int, int]]:
    return [(a + 1, b + 1, c + 1) for (a, b, c) in FANO_CYCLES]


def shared_line_count(m1: frozenset[int], m2: frozenset[int]) -> int:
    """
    Count Fano lines that touch both motifs (at least one point from each).
    """
    count = 0
    for line in _one_index_cycles():
        s = set(line)
        if s.intersection(m1) and s.intersection(m2):
            count += 1
    return count


def build_hydrogen_structural_summary() -> dict[str, Any]:
    pair = shared_pair(ELECTRON_MOTIF, PROTON_PROTO_MOTIF)
    line = line_through_pair(pair, FANO_CYCLES)
    sl_count = shared_line_count(ELECTRON_MOTIF, PROTON_PROTO_MOTIF)
    return {
        "electron_motif": sorted(ELECTRON_MOTIF),
        "proton_proto_motif": sorted(PROTON_PROTO_MOTIF),
        "electron_class": classify_motif(ELECTRON_MOTIF, FANO_CYCLES),
        "proton_proto_class": classify_motif(PROTON_PROTO_MOTIF, FANO_CYCLES),
        "overlap_count": motif_overlap(ELECTRON_MOTIF, PROTON_PROTO_MOTIF),
        "shared_pair": sorted(pair),
        "line_through_shared_pair": None if line is None else sorted(line),
        "shared_line_count": sl_count,
        "binding_proxy": {
            "numerator": binding_proxy(sl_count).numerator,
            "denominator": binding_proxy(sl_count).denominator,
            "value_float": float(binding_proxy(sl_count)),
        },
    }


def _operator_sequences() -> dict[str, list[int]]:
    return {
        "vacuum_pass_e7": [7],
        "interaction_pass_123": [1, 2, 3],
    }


def build_hydrogen_xor_cycle_summary(max_steps: int = 64) -> dict[str, Any]:
    seqs = _operator_sequences()
    motifs = {
        "electron_favored_vector": vector_motif_state((1, 2, 3), coeff=1),
        "proton_proto_vector": vector_motif_state((1, 2, 4), coeff=1),
    }

    out: dict[str, Any] = {}
    for name, state in motifs.items():
        hand_map: dict[str, Any] = {}
        for hand in ("left", "right"):
            seq_map: dict[str, Any] = {}
            for seq_id, ops in seqs.items():
                seq_map[seq_id] = run_cycle_trace(state, op_cycle=ops, hand=hand, max_steps=max_steps)
            hand_map[hand] = seq_map
        out[name] = hand_map
    return out


def _dominant_nonzero_idx_gi(state: StateGI) -> int:
    """
    Deterministic cross-message selector for StateGI.
    """
    best_idx: int | None = None
    best_mag = -1
    for idx, c in enumerate(state):
        if idx == 0:
            continue
        re, im = c
        mag = abs(re) + abs(im)
        if mag == 0:
            continue
        if mag > best_mag or (mag == best_mag and best_idx is not None and idx < best_idx):
            best_mag = mag
            best_idx = idx
    return best_idx if best_idx is not None else 7


def _coupled_step_hydrogen(a: StateGI, b: StateGI) -> tuple[StateGI, StateGI]:
    # Internal "interaction pass" stage (same for both motifs).
    for op in (1, 2, 3):
        a = apply_operator(a, op, "left")
        b = apply_operator(b, op, "left")

    # Cross-message stage (directional handedness).
    op_for_a = _dominant_nonzero_idx_gi(b)
    op_for_b = _dominant_nonzero_idx_gi(a)
    a = apply_operator(a, op_for_a, "left")
    b = apply_operator(b, op_for_b, "right")
    return a, b


def _detect_coupled_period_hydrogen(max_steps: int = 256) -> dict[str, Any]:
    a = vector_motif_state((1, 2, 3), coeff=1)
    b = vector_motif_state((1, 2, 4), coeff=1)
    seen: dict[tuple[StateGI, StateGI], int] = {(a, b): 0}
    trace: list[dict[str, Any]] = [{"step": 0}]
    cycle_start = None
    period = None
    cycle_found = False

    for step in range(1, max_steps + 1):
        a, b = _coupled_step_hydrogen(a, b)
        trace.append({"step": step})
        key = (a, b)
        if key in seen:
            cycle_start = seen[key]
            period = step - cycle_start
            cycle_found = True
            break
        seen[key] = step

    return {
        "cycle_found": cycle_found,
        "cycle_start": cycle_start,
        "period": period,
        "period_gt_4": (period is not None and period > 4),
        "steps_recorded": len(trace),
    }


def build_hydrogen_coupled_summary(max_steps: int = 256) -> dict[str, Any]:
    # TODO(XCALC-103-ext): add replay hash field once hash utility is standardized.
    return _detect_coupled_period_hydrogen(max_steps=max_steps)


def build_hydrogen_scan_dataset(max_steps: int = 64) -> dict[str, Any]:
    structural = build_hydrogen_structural_summary()
    dynamic = build_hydrogen_xor_cycle_summary(max_steps=max_steps)
    coupled = build_hydrogen_coupled_summary(max_steps=max_steps * 4)

    csv_rows: list[dict[str, Any]] = []
    for motif, hand_map in dynamic.items():
        for hand, seq_map in hand_map.items():
            for seq_id, sim in seq_map.items():
                csv_rows.append(
                    {
                        "section": "dynamic",
                        "label": motif,
                        "hand": hand,
                        "sequence_id": seq_id,
                        "cycle_found": sim["cycle_found"],
                        "cycle_start": sim["cycle_start"],
                        "period": sim["period"],
                        "steps_recorded": sim["steps_recorded"],
                    }
                )
    csv_rows.append(
        {
            "section": "coupled",
            "label": "electron_vs_proton_proto",
            "hand": "mixed",
            "sequence_id": "coupled_internal123_plus_cross",
            "cycle_found": coupled["cycle_found"],
            "cycle_start": coupled["cycle_start"],
            "period": coupled["period"],
            "steps_recorded": coupled["steps_recorded"],
        }
    )

    return {
        "schema_version": "xor_hydrogen_binding_scan_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "notes": [
            "Structural + XOR dynamic scan for HYDROGEN-001 bridge.",
            "No spectroscopic or SI-calibrated claim in this artifact.",
        ],
        "structural": structural,
        "dynamic": dynamic,
        "coupled": coupled,
        "csv_rows": csv_rows,
    }


def write_hydrogen_scan_artifacts(
    dataset: dict[str, Any],
    json_paths: list[Path] | None = None,
    csv_paths: list[Path] | None = None,
) -> None:
    if json_paths is None:
        json_paths = [Path("calc/xor_hydrogen_binding_scan.json")]
    if csv_paths is None:
        csv_paths = [Path("calc/xor_hydrogen_binding_scan.csv")]

    for p in json_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(dataset, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "section",
        "label",
        "hand",
        "sequence_id",
        "cycle_found",
        "cycle_start",
        "period",
        "steps_recorded",
    ]
    for p in csv_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for row in dataset["csv_rows"]:
                w.writerow(row)


def main() -> int:
    dataset = build_hydrogen_scan_dataset(max_steps=64)
    write_hydrogen_scan_artifacts(
        dataset,
        json_paths=[
            Path("calc/xor_hydrogen_binding_scan.json"),
            Path("website/data/xor_hydrogen_binding_scan.json"),
        ],
        csv_paths=[
            Path("calc/xor_hydrogen_binding_scan.csv"),
            Path("website/data/xor_hydrogen_binding_scan.csv"),
        ],
    )
    print("Wrote calc/xor_hydrogen_binding_scan.json")
    print("Wrote calc/xor_hydrogen_binding_scan.csv")
    print("Wrote website/data/xor_hydrogen_binding_scan.json")
    print("Wrote website/data/xor_hydrogen_binding_scan.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

