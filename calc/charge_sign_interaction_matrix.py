"""
calc/charge_sign_interaction_matrix.py

Charge-sign interaction matrix for the current two-node kernel semantics.

Purpose:
  1) Provide a falsifiable polarity check now (repulsive/attractive/neutral)
     before distance/trajectory layers are added.
  2) Mirror the locked D1-D3 contracts used by TwoNodeSystem.lean:
       - D1 combine: multiplicative
       - D2 trace: Markov (fold over current messages only)
       - D3 energy exchange: k > 0 and interactionFold(msgs) != 1

Notes:
  - This script classifies interaction kind only.
  - It does not model spatial scattering trajectories.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import numpy as np

from calc.furey_electron_orbit import furey_dual_electron_state, furey_electron_state
from calc.qed_ee_sim import E0, E7, OMEGA, oct_mul_full

TOL = 1e-10


def u1_charge(psi: np.ndarray) -> float:
    """Mirror Lean u1Charge: real part of e7 component."""
    return float(np.real(psi[7]))


def temporal_commit(psi: np.ndarray) -> np.ndarray:
    """T(psi) = e7 * psi (left multiplication)."""
    return oct_mul_full(E7, psi)


def interaction_fold(msgs: list[np.ndarray]) -> np.ndarray:
    """D2 Markov fold: left fold over octonion multiplication with identity e0."""
    acc = E0.copy()
    for msg in msgs:
        acc = oct_mul_full(acc, msg)
    return acc


def next_state_v2(psi: np.ndarray, msgs: list[np.ndarray]) -> np.ndarray:
    """D1+D2 update: combine(temporal_commit(psi), interactionFold(msgs)) with combine=*."""
    base = temporal_commit(psi)
    interaction = interaction_fold(msgs)
    return oct_mul_full(base, interaction)


def two_node_round(psi1: np.ndarray, psi2: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    One deterministic two-node round:
      node1 sees [psi2]
      node2 sees [psi1]
    """
    return next_state_v2(psi1, [psi2]), next_state_v2(psi2, [psi1])


def is_energy_exchange_locked(msgs: list[np.ndarray]) -> bool:
    """D3 predicate: non-empty boundary and non-identity folded interaction."""
    if not msgs:
        return False
    return not np.allclose(interaction_fold(msgs), E0, atol=TOL)


def same_u1_charge_sign(psi1: np.ndarray, psi2: np.ndarray) -> bool:
    """Both charges non-zero and same sign."""
    c1 = u1_charge(psi1)
    c2 = u1_charge(psi2)
    if abs(c1) <= TOL or abs(c2) <= TOL:
        return False
    return float(np.sign(c1)) == float(np.sign(c2))


def opposite_u1_charge_sign(psi1: np.ndarray, psi2: np.ndarray) -> bool:
    """Both charges non-zero and opposite sign."""
    c1 = u1_charge(psi1)
    c2 = u1_charge(psi2)
    if abs(c1) <= TOL or abs(c2) <= TOL:
        return False
    return float(np.sign(c1)) != float(np.sign(c2))


def interaction_kind(psi1: np.ndarray, psi2: np.ndarray) -> str:
    """
    Classify pair interaction polarity using current two-node semantics:
      - "repulsive": energy exchange and same-sign non-zero U(1) charge
      - "attractive": energy exchange and opposite-sign non-zero U(1) charge
      - "neutral": otherwise
    """
    if not is_energy_exchange_locked([psi2]):
        return "neutral"
    if same_u1_charge_sign(psi1, psi2):
        return "repulsive"
    if opposite_u1_charge_sign(psi1, psi2):
        return "attractive"
    return "neutral"


def benchmark_states() -> Dict[str, np.ndarray]:
    """
    Benchmark state set for polarity matrix:
      - electron: Furey charged lepton state (negative U(1) sign in this scaling)
      - positron_like: dual-sector opposite-sign benchmark
      - vacuum: neutral baseline
    """
    return {
        "electron": furey_electron_state(),
        "positron_like": furey_dual_electron_state(),
        "vacuum": OMEGA.copy(),
    }


def build_charge_sign_matrix() -> dict[str, dict[str, str]]:
    """Build a nested dict matrix[row_state][col_state] -> interaction kind."""
    states = benchmark_states()
    labels = list(states.keys())
    matrix: dict[str, dict[str, str]] = {}
    for row in labels:
        matrix[row] = {}
        for col in labels:
            matrix[row][col] = interaction_kind(states[row], states[col])
    return matrix


def summarize() -> dict:
    """Structured summary for CI and dashboards."""
    states = benchmark_states()
    charges = {k: u1_charge(v) for k, v in states.items()}
    matrix = build_charge_sign_matrix()
    return {
        "charges": charges,
        "matrix": matrix,
    }


def _print_table(summary: dict) -> None:
    charges = summary["charges"]
    matrix = summary["matrix"]
    labels = list(matrix.keys())

    print("Charge-sign interaction matrix (D1-D3 semantics)")
    print("=" * 64)
    print("Charges (real part of e7 component):")
    for label in labels:
        print(f"  {label:14s}: {charges[label]: .6f}")

    print("\nMatrix rows=source, cols=boundary payload:")
    header = " " * 16 + "".join(f"{c:>16s}" for c in labels)
    print(header)
    for r in labels:
        row = f"{r:>16s}"
        for c in labels:
            row += f"{matrix[r][c]:>16s}"
        print(row)


def main() -> None:
    summary = summarize()
    _print_table(summary)

    out_path = Path(__file__).with_name("charge_sign_interaction_matrix.json")
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nWrote summary JSON: {out_path}")


if __name__ == "__main__":
    main()

