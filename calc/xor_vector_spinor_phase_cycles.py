"""
calc/xor_vector_spinor_phase_cycles.py

Phase-cycle traces for vector motifs and spinor motifs in one shared XOR basis.

Focus:
  - vector electron motif in favored integer-count orientation,
  - repeated XOR product traces under identical operator sequences,
  - same-basis comparison for left/right spinor evolution.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from calc.conftest import FANO_CYCLES
from calc.xor_furey_ideals import (
    StateGI,
    furey_dual_electron_doubled,
    furey_electron_doubled,
    nonzero_support,
    oct_mul_xor,
    state_basis,
    state_sparse,
)


def vector_motif_state(triad: tuple[int, int, int], coeff: int = 1) -> StateGI:
    """
    Integer-count vector motif state:
      sum(coeff * e_i) for i in triad (one-indexed imaginary basis labels).
    """
    if coeff == 0:
        raise ValueError("coeff must be non-zero")
    if len(set(triad)) != 3:
        raise ValueError(f"triad must be distinct, got {triad}")
    if any(not (1 <= x <= 7) for x in triad):
        raise ValueError(f"triad entries must be in [1,7], got {triad}")

    cur = state_basis(0, (0, 0))
    for i in triad:
        cur = tuple(
            (cur[k][0] + (coeff if k == i else 0), cur[k][1])
            for k in range(8)
        )  # type: ignore[return-value]
    return cur


def apply_operator(state: StateGI, op_idx: int, hand: str) -> StateGI:
    if not (1 <= op_idx <= 7):
        raise ValueError(f"op_idx must be in [1,7], got {op_idx}")
    op = state_basis(op_idx, (1, 0))
    if hand == "left":
        return oct_mul_xor(op, state)
    if hand == "right":
        return oct_mul_xor(state, op)
    raise ValueError(f"hand must be 'left' or 'right', got {hand}")


def _state_key(state: StateGI) -> StateGI:
    return state


def run_cycle_trace(
    initial: StateGI,
    op_cycle: Iterable[int],
    hand: str,
    max_steps: int = 64,
) -> dict[str, Any]:
    """
    Repeated XOR product trace under a cyclical operator sequence.
    """
    ops = list(op_cycle)
    if not ops:
        raise ValueError("op_cycle must be non-empty")

    seen: dict[StateGI, int] = {}
    trace: list[dict[str, Any]] = []
    cur = initial
    seen[_state_key(cur)] = 0
    trace.append(
        {
            "step": 0,
            "state_sparse": state_sparse(cur),
            "support": nonzero_support(cur),
            "op_idx": None,
            "hand": hand,
        }
    )

    cycle_start: int | None = None
    period: int | None = None
    cycle_found = False

    for step in range(1, max_steps + 1):
        op = ops[(step - 1) % len(ops)]
        cur = apply_operator(cur, op, hand)
        trace.append(
            {
                "step": step,
                "state_sparse": state_sparse(cur),
                "support": nonzero_support(cur),
                "op_idx": op,
                "hand": hand,
            }
        )
        key = _state_key(cur)
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
        "steps_recorded": len(trace),
        "trace": trace,
    }


def _electron_operator_sequences() -> dict[str, list[int]]:
    # Same sequences are applied to vector and spinor motifs.
    return {
        "vacuum_pass_e7": [7],
        "interaction_pass_123": [1, 2, 3],
    }


def _fano_line_motifs() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for idx, cyc in enumerate(FANO_CYCLES, start=1):
        triad = (cyc[0] + 1, cyc[1] + 1, cyc[2] + 1)  # preserve favored orientation
        state = vector_motif_state(triad, coeff=1)
        out.append(
            {
                "motif_id": f"vector_fano_line_l{idx}",
                "triad_oriented": list(triad),
                "state_sparse": state_sparse(state),
                "state": state,
            }
        )
    return out


def build_vector_spinor_phase_cycle_dataset(max_steps: int = 64) -> dict[str, Any]:
    sequences = _electron_operator_sequences()

    # Vector family: integer-count stable line motifs.
    vector_rows: list[dict[str, Any]] = []
    for m in _fano_line_motifs():
        motif_state: StateGI = m["state"]
        hands_out: dict[str, Any] = {}
        for hand in ("left", "right"):
            seq_out: dict[str, Any] = {}
            for seq_id, ops in sequences.items():
                seq_out[seq_id] = run_cycle_trace(
                    motif_state,
                    op_cycle=ops,
                    hand=hand,
                    max_steps=max_steps,
                )
            hands_out[hand] = seq_out
        vector_rows.append(
            {
                "motif_id": m["motif_id"],
                "triad_oriented": m["triad_oriented"],
                "state_sparse": m["state_sparse"],
                "traces": hands_out,
            }
        )

    # Electron-focused exact same basis and exact same op sequences.
    vector_electron = vector_motif_state((1, 2, 3), coeff=1)
    spinor_left = furey_electron_doubled()
    spinor_right = furey_dual_electron_doubled()

    comparison_states = {
        "vector_electron_favored": vector_electron,
        "left_spinor_electron_ideal": spinor_left,
        "right_spinor_electron_ideal": spinor_right,
    }

    comparison_payload: dict[str, Any] = {}
    csv_rows: list[dict[str, Any]] = []
    for label, state in comparison_states.items():
        hands_out: dict[str, Any] = {}
        for hand in ("left", "right"):
            seq_out: dict[str, Any] = {}
            for seq_id, ops in sequences.items():
                sim = run_cycle_trace(state, op_cycle=ops, hand=hand, max_steps=max_steps)
                seq_out[seq_id] = sim
                csv_rows.append(
                    {
                        "label": label,
                        "hand": hand,
                        "sequence_id": seq_id,
                        "cycle_found": sim["cycle_found"],
                        "cycle_start": sim["cycle_start"],
                        "period": sim["period"],
                        "steps_recorded": sim["steps_recorded"],
                    }
                )
            hands_out[hand] = seq_out
        comparison_payload[label] = {
            "state_sparse": state_sparse(state),
            "support": nonzero_support(state),
            "traces": hands_out,
        }

    return {
        "schema_version": "xor_vector_spinor_phase_cycles_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "basis": {
            "channels": ["e0", "e1", "e2", "e3", "e4", "e5", "e6", "e7"],
            "notation": "same basis for vector and spinor motifs",
            "mul_rule": "distinct imaginaries use XOR index + Fano sign; handed by left/right multiplication order",
        },
        "operator_sequences": sequences,
        "vector_motifs": vector_rows,
        "electron_comparison": comparison_payload,
        "csv_rows": csv_rows,
    }


def write_vector_spinor_phase_cycle_artifacts(
    dataset: dict[str, Any],
    json_paths: list[Path] | None = None,
    csv_paths: list[Path] | None = None,
) -> None:
    if json_paths is None:
        json_paths = [Path("calc/xor_vector_spinor_phase_cycles.json")]
    if csv_paths is None:
        csv_paths = [Path("calc/xor_vector_spinor_phase_cycles.csv")]

    for path in json_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(dataset, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "label",
        "hand",
        "sequence_id",
        "cycle_found",
        "cycle_start",
        "period",
        "steps_recorded",
    ]
    for path in csv_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in dataset["csv_rows"]:
                writer.writerow(row)


def main() -> int:
    dataset = build_vector_spinor_phase_cycle_dataset(max_steps=64)
    write_vector_spinor_phase_cycle_artifacts(
        dataset,
        json_paths=[
            Path("calc/xor_vector_spinor_phase_cycles.json"),
            Path("website/data/xor_vector_spinor_phase_cycles.json"),
        ],
        csv_paths=[
            Path("calc/xor_vector_spinor_phase_cycles.csv"),
            Path("website/data/xor_vector_spinor_phase_cycles.csv"),
        ],
    )
    print("Wrote calc/xor_vector_spinor_phase_cycles.json")
    print("Wrote calc/xor_vector_spinor_phase_cycles.csv")
    print("Wrote website/data/xor_vector_spinor_phase_cycles.json")
    print("Wrote website/data/xor_vector_spinor_phase_cycles.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

