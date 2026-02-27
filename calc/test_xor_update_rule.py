"""
Tests for calc/xor_update_rule.py
"""

from calc.xor_octonion_gate import Handedness
from calc.xor_stable_motif_scan import (
    apply_basis_handed,
    motif_schedule,
    run_round,
    triad_seed_state,
)
from calc.xor_update_rule import (
    coupled_pair_round,
    dominant_nonzero_idx,
    interaction_fold,
    motif_round_update,
    temporal_commit,
)


def test_temporal_commit_matches_direct_basis_hit():
    state = triad_seed_state((1, 2, 3))
    got = temporal_commit(state, op_idx=7, hand=Handedness.LEFT)
    expected = apply_basis_handed(state, 7, Handedness.LEFT)
    assert got == expected


def test_interaction_fold_matches_manual_sequence():
    state = triad_seed_state((1, 2, 3))
    msgs = [(7, Handedness.LEFT), (2, Handedness.RIGHT), (5, Handedness.LEFT)]
    got = interaction_fold(state, msgs)
    cur = state
    for op_idx, hand in msgs:
        cur = apply_basis_handed(cur, op_idx, hand)
    assert got == cur


def test_motif_round_update_temporal_first_and_last():
    triad = (1, 2, 3)
    state = triad_seed_state(triad)

    got_first = motif_round_update(
        state,
        triad=triad,
        temporal_first=True,
        temporal_op_idx=7,
        temporal_hand=Handedness.LEFT,
        internal_mode="alternating",
    )
    expected_first = run_round(
        apply_basis_handed(state, 7, Handedness.LEFT),
        motif_schedule(triad, mode="alternating"),
    )
    assert got_first == expected_first

    got_last = motif_round_update(
        state,
        triad=triad,
        temporal_first=False,
        temporal_op_idx=7,
        temporal_hand=Handedness.LEFT,
        internal_mode="alternating",
    )
    expected_last = apply_basis_handed(
        run_round(state, motif_schedule(triad, mode="alternating")),
        7,
        Handedness.LEFT,
    )
    assert got_last == expected_last


def test_dominant_nonzero_idx_tie_break_and_fallback():
    # Tie on absolute coefficient at e2 and e5 -> pick smallest index e2.
    state = (0, 0, 3, 0, 0, -3, 0, 0)
    assert dominant_nonzero_idx(state) == 2

    # Pure scalar state -> fallback e7.
    scalar_only = (4, 0, 0, 0, 0, 0, 0, 0)
    assert dominant_nonzero_idx(scalar_only) == 7


def test_coupled_pair_round_shape_and_determinism():
    a0 = triad_seed_state((1, 2, 3))
    b0 = triad_seed_state((2, 5, 7))

    a1, b1 = coupled_pair_round(a0, b0, triad_a=(1, 2, 3), triad_b=(2, 5, 7))
    a2, b2 = coupled_pair_round(a0, b0, triad_a=(1, 2, 3), triad_b=(2, 5, 7))

    assert a1 == a2
    assert b1 == b2
    assert len(a1) == 8
    assert len(b1) == 8

