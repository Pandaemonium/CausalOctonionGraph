"""
calc/xor_charge_sign_interaction_matrix.py

XCALC-101 scaffold: XOR-basis charge-sign interaction matrix.

Design goals:
1) Stay entirely in the XOR octonion execution path (no legacy oct_mul_full).
2) Mirror D1-D3 semantics used by TwoNodeSystem:
   - D1 combine: multiplicative
   - D2 trace: Markov fold over current messages
   - D3 energy exchange: msgs non-empty and interaction fold != identity
3) Produce stable artifacts (JSON + CSV) for claims/dashboard workflows.

This file is intentionally "guided scaffold":
1) core functions are implemented for immediate use,
2) TODO markers identify where to extend benchmark states/policies.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from calc.xor_furey_ideals import (
    StateGI,
    furey_dual_electron_doubled,
    furey_electron_doubled,
    oct_mul_xor,
    state_basis,
    vacuum_doubled,
)
from calc.xor_vector_spinor_phase_cycles import vector_motif_state


def identity_state() -> StateGI:
    """Multiplicative identity e0."""
    return state_basis(0, (1, 0))


def u1_charge(state: StateGI) -> int:
    """
    Mirror Lean u1Charge in integer form:
      real part of e7 coefficient.
    """
    return int(state[7][0])


def temporal_commit(state: StateGI) -> StateGI:
    """T(state) = e7 * state (left multiplication)."""
    return oct_mul_xor(state_basis(7, (1, 0)), state)


def interaction_fold(msgs: list[StateGI]) -> StateGI:
    """
    D2 Markov fold with identity accumulator.
    """
    acc = identity_state()
    for msg in msgs:
        acc = oct_mul_xor(acc, msg)
    return acc


def next_state_v2_xor(state: StateGI, msgs: list[StateGI]) -> StateGI:
    """
    D1+D2 update:
      base = temporal_commit(state)
      interaction = interaction_fold(msgs)
      combine = base * interaction
    """
    base = temporal_commit(state)
    interaction = interaction_fold(msgs)
    return oct_mul_xor(base, interaction)


def two_node_round_xor(state1: StateGI, state2: StateGI) -> tuple[StateGI, StateGI]:
    """
    Deterministic one-round two-node update:
      node1 sees [state2]
      node2 sees [state1]
    """
    return next_state_v2_xor(state1, [state2]), next_state_v2_xor(state2, [state1])


def is_energy_exchange_locked_xor(msgs: list[StateGI]) -> bool:
    """D3 predicate in XOR representation."""
    if not msgs:
        return False
    return interaction_fold(msgs) != identity_state()


def same_u1_charge_sign_xor(state1: StateGI, state2: StateGI) -> bool:
    """Both charges non-zero and same sign."""
    c1 = u1_charge(state1)
    c2 = u1_charge(state2)
    if c1 == 0 or c2 == 0:
        return False
    return (c1 > 0) == (c2 > 0)


def opposite_u1_charge_sign_xor(state1: StateGI, state2: StateGI) -> bool:
    """Both charges non-zero and opposite sign."""
    c1 = u1_charge(state1)
    c2 = u1_charge(state2)
    if c1 == 0 or c2 == 0:
        return False
    return (c1 > 0) != (c2 > 0)


def interaction_kind_xor(state1: StateGI, state2: StateGI) -> str:
    """
    Polarity classifier:
      - repulsive: energy exchange + same-sign non-zero U(1)
      - attractive: energy exchange + opposite-sign non-zero U(1)
      - neutral: otherwise
    """
    if not is_energy_exchange_locked_xor([state2]):
        return "neutral"
    if same_u1_charge_sign_xor(state1, state2):
        return "repulsive"
    if opposite_u1_charge_sign_xor(state1, state2):
        return "attractive"
    return "neutral"


def benchmark_states_xor() -> dict[str, StateGI]:
    """
    Baseline state set for XCALC-101.

    TODO(XCALC-101-ext):
    1) add more motif families (muon/tau proxies, quark-like seeds),
    2) add policy-tag metadata to each state for downstream filters.
    """
    return {
        "vector_electron_favored": vector_motif_state((1, 2, 3), coeff=1),
        "left_spinor_electron_ideal": furey_electron_doubled(),
        "right_spinor_electron_ideal": furey_dual_electron_doubled(),
        "vacuum_doubled": vacuum_doubled(),
    }


def build_charge_sign_matrix_xor() -> dict[str, dict[str, str]]:
    states = benchmark_states_xor()
    labels = list(states.keys())
    matrix: dict[str, dict[str, str]] = {}
    for row in labels:
        matrix[row] = {}
        for col in labels:
            matrix[row][col] = interaction_kind_xor(states[row], states[col])
    return matrix


def summarize_xor() -> dict[str, Any]:
    states = benchmark_states_xor()
    charges = {k: u1_charge(v) for k, v in states.items()}
    matrix = build_charge_sign_matrix_xor()
    return {
        "schema_version": "xor_charge_sign_interaction_matrix_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "charges": charges,
        "matrix": matrix,
        "notes": [
            "XOR-basis polarity classifier using D1-D3 semantics.",
            "No spatial trajectory or force magnitude model in this artifact.",
        ],
    }


def write_xor_charge_sign_artifacts(
    summary: dict[str, Any],
    json_paths: list[Path] | None = None,
    csv_paths: list[Path] | None = None,
) -> None:
    if json_paths is None:
        json_paths = [Path("calc/xor_charge_sign_interaction_matrix.json")]
    if csv_paths is None:
        csv_paths = [Path("calc/xor_charge_sign_interaction_matrix.csv")]

    for p in json_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    rows: list[dict[str, Any]] = []
    charges = summary["charges"]
    matrix = summary["matrix"]
    for row_label, cols in matrix.items():
        for col_label, kind in cols.items():
            rows.append(
                {
                    "row_label": row_label,
                    "col_label": col_label,
                    "kind": kind,
                    "row_charge": charges[row_label],
                    "col_charge": charges[col_label],
                }
            )

    fieldnames = ["row_label", "col_label", "kind", "row_charge", "col_charge"]
    for p in csv_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for row in rows:
                w.writerow(row)


def main() -> int:
    summary = summarize_xor()
    write_xor_charge_sign_artifacts(
        summary,
        json_paths=[
            Path("calc/xor_charge_sign_interaction_matrix.json"),
            Path("website/data/xor_charge_sign_interaction_matrix.json"),
        ],
        csv_paths=[
            Path("calc/xor_charge_sign_interaction_matrix.csv"),
            Path("website/data/xor_charge_sign_interaction_matrix.csv"),
        ],
    )
    print("Wrote calc/xor_charge_sign_interaction_matrix.json")
    print("Wrote calc/xor_charge_sign_interaction_matrix.csv")
    print("Wrote website/data/xor_charge_sign_interaction_matrix.json")
    print("Wrote website/data/xor_charge_sign_interaction_matrix.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

