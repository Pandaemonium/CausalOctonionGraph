"""
calc/xor_update_rule.py

Deterministic XOR update-rule helpers for motif and coupled-motif simulations.

This module mirrors the COG update skeleton at a structural level:
  1) temporal commit,
  2) ordered local interaction fold,
  3) deterministic cross-message application.
"""

from __future__ import annotations

from typing import Iterable

from calc.xor_octonion_gate import Handedness
from calc.xor_stable_motif_scan import (
    StateVec,
    apply_basis_handed,
    motif_schedule,
    run_round,
)


def interaction_fold(
    state: StateVec,
    messages: Iterable[tuple[int, Handedness]],
) -> StateVec:
    """
    Deterministic ordered fold of handed basis-operator messages.
    """
    cur = state
    for op_idx, hand in messages:
        cur = apply_basis_handed(cur, op_idx, hand)
    return cur


def temporal_commit(
    state: StateVec,
    op_idx: int = 7,
    hand: Handedness = Handedness.LEFT,
) -> StateVec:
    """
    One-step temporal commit (default: left hit by e7).
    """
    return apply_basis_handed(state, op_idx, hand)


def motif_round_update(
    state: StateVec,
    triad: tuple[int, int, int],
    boundary_messages: Iterable[tuple[int, Handedness]] = (),
    *,
    temporal_first: bool = True,
    temporal_op_idx: int = 7,
    temporal_hand: Handedness = Handedness.LEFT,
    internal_mode: str = "alternating",
) -> StateVec:
    """
    Deterministic motif round:
      - optional temporal commit,
      - one internal triad round,
      - ordered boundary interaction fold.
    """
    cur = state
    if temporal_first:
        cur = temporal_commit(cur, op_idx=temporal_op_idx, hand=temporal_hand)
    cur = run_round(cur, motif_schedule(triad, mode=internal_mode))
    cur = interaction_fold(cur, boundary_messages)
    if not temporal_first:
        cur = temporal_commit(cur, op_idx=temporal_op_idx, hand=temporal_hand)
    return cur


def dominant_nonzero_idx(state: StateVec) -> int:
    """
    Deterministic message operator selection:
      - pick nonzero basis index with max |coeff|,
      - tie-break by smallest basis index,
      - fallback to e7 when all imaginary coefficients are zero.
    """
    best_idx: int | None = None
    best_abs = -1
    for idx, coeff in enumerate(state):
        if idx == 0:
            continue
        if coeff == 0:
            continue
        a = abs(coeff)
        if a > best_abs or (a == best_abs and best_idx is not None and idx < best_idx):
            best_abs = a
            best_idx = idx
    return best_idx if best_idx is not None else 7


def coupled_pair_round(
    state_a: StateVec,
    state_b: StateVec,
    *,
    triad_a: tuple[int, int, int],
    triad_b: tuple[int, int, int],
    internal_mode: str = "alternating",
) -> tuple[StateVec, StateVec]:
    """
    Deterministic coupled update with fixed handed cross messages.

    This intentionally preserves the existing structural policy:
      - each motif applies one internal round first,
      - each then receives one partner-derived cross message.
    """
    next_a = run_round(state_a, motif_schedule(triad_a, mode=internal_mode))
    next_b = run_round(state_b, motif_schedule(triad_b, mode=internal_mode))

    op_for_a = dominant_nonzero_idx(next_b)
    op_for_b = dominant_nonzero_idx(next_a)
    next_a = apply_basis_handed(next_a, op_for_a, Handedness.LEFT)
    next_b = apply_basis_handed(next_b, op_for_b, Handedness.RIGHT)
    return next_a, next_b

