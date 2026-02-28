"""THETA-001 deterministic CP-invariance witness tests."""

from calc.theta001_cp_invariant import (
    FANO_TRIPLES,
    cp_dual_trace_relation_holds,
    cp_is_involution,
    cp_trace_delta,
    cp_weighted_trace_delta,
    fano_sign_balance_counts,
    orientation_reversal_closed_on_fano_lines,
    weak_leakage_ckm_like_strong_residual,
    weak_leakage_strong_residual,
)


def test_cp_involution_true() -> None:
    state = (3, -1, 2, 0, -5, 8, 13, -21)
    assert cp_is_involution(state)


def test_orientation_reversal_closed_on_fano_triples() -> None:
    assert orientation_reversal_closed_on_fano_lines(FANO_TRIPLES)


def test_fano_sign_balance_is_exactly_21_21() -> None:
    pos_count, neg_count, signed_sum = fano_sign_balance_counts()
    assert pos_count == 21
    assert neg_count == 21
    assert signed_sum == 0


def test_cp_dual_trace_relation_holds() -> None:
    initial = (1, 2, -1, 0, 3, -2, 1, 4)
    ops = (1, 7, 3, 5, 2, 6, 4, 1, 2, 3)
    assert cp_dual_trace_relation_holds(initial, ops)


def test_cp_weighted_trace_delta_zero() -> None:
    initial = (2, -1, 0, 3, -2, 1, 4, -3)
    ops = (7, 1, 4, 2, 6, 3, 5, 7)
    weights = (1, 2, 3, 4, 5, 6, 7, 8)
    assert cp_weighted_trace_delta(initial, ops, weights) == 0


def test_cp_invariant_trace_delta_zero() -> None:
    trace = [
        (1, 0, 0, 0, 0, 0, 0, 0),
        (1, 2, -3, 5, -7, 11, -13, 17),
        (0, 1, 1, 1, 1, 1, 1, 1),
    ]
    assert cp_trace_delta(trace) == 0


def test_weak_leakage_strong_residual_zero_deep_cone() -> None:
    initial = (1, -2, 3, -4, 5, -6, 7, -1)
    ops = (7, 1, 7, 2, 7, 3, 7, 4, 7, 5, 7, 6, 7, 1, 2, 3)
    residual = weak_leakage_strong_residual(
        initial,
        ops,
        weak_kick=5,
        phase_shift=3,
    )
    assert residual == 0


def test_weak_leakage_ckm_like_strong_residual_zero_deep_cone() -> None:
    initial = (1, -2, 3, -4, 5, -6, 7, -1)
    ops = (7, 1, 7, 2, 7, 3, 7, 4, 7, 5, 7, 6, 7, 1, 2, 3, 4, 5)
    residual = weak_leakage_ckm_like_strong_residual(
        initial,
        ops,
        weak_kick=5,
        ckm_phase=3,
        transport_period=3,
    )
    assert residual == 0
