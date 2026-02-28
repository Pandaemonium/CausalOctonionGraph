"""Deterministic THETA-001 structure-first witnesses for COG v2."""

from __future__ import annotations

from typing import Dict, Iterable, List, Sequence, Tuple

State8 = Tuple[int, int, int, int, int, int, int, int]
Triple = Tuple[int, int, int]
SignTable = Dict[Tuple[int, int], int]
STRONG_SECTOR_WEIGHTS: Tuple[int, int, int, int, int, int, int, int] = (0, 1, 1, 1, 1, 1, 1, 0)

# 0-indexed Fano lines over binary channels e001..e111 (XOR-closed orientation).
FANO_CYCLES: Tuple[Tuple[int, int, int], ...] = (
    (0, 1, 2),
    (0, 3, 4),
    (0, 5, 6),
    (1, 3, 5),
    (1, 4, 6),
    (2, 3, 6),
    (2, 4, 5),
)

# 1-indexed directed triples for readability in docs/artifacts.
FANO_TRIPLES: Tuple[Triple, ...] = tuple((a + 1, b + 1, c + 1) for (a, b, c) in FANO_CYCLES)

FANO_SIGN: SignTable = {}
for a, b, c in FANO_CYCLES:
    FANO_SIGN[(a, b)] = +1
    FANO_SIGN[(b, c)] = +1
    FANO_SIGN[(c, a)] = +1
    FANO_SIGN[(b, a)] = -1
    FANO_SIGN[(c, b)] = -1
    FANO_SIGN[(a, c)] = -1


def cp_map(state: State8) -> State8:
    """CP action used in this witness lane: keep scalar, flip imaginary channels."""
    return (
        state[0],
        -state[1],
        -state[2],
        -state[3],
        -state[4],
        -state[5],
        -state[6],
        -state[7],
    )


def orientation_flip(triple: Triple) -> Triple:
    a, b, c = triple
    return (a, c, b)


def cp_is_involution(state: State8) -> bool:
    return cp_map(cp_map(state)) == state


def orientation_reversal_closed_on_fano_lines(triples: Sequence[Triple]) -> bool:
    line_sets = {frozenset(t) for t in triples}
    return all(frozenset(orientation_flip(t)) in line_sets for t in triples)


def fano_sign_balance_counts() -> Tuple[int, int, int]:
    """Expected exact structural result: 21 positive, 21 negative, signed sum 0."""
    pos_count = 0
    neg_count = 0
    for a, b, c in FANO_CYCLES:
        for i, j in ((a, b), (b, c), (c, a)):
            if FANO_SIGN[(i, j)] > 0:
                pos_count += 1
        for i, j in ((b, a), (c, b), (a, c)):
            if FANO_SIGN[(i, j)] < 0:
                neg_count += 1
    return pos_count, neg_count, pos_count - neg_count


def _basis_mul(i: int, j: int, sign_table: SignTable) -> Tuple[int, int]:
    if i == 0:
        return 1, j
    if j == 0:
        return 1, i
    if i == j:
        return -1, 0
    return sign_table[(i - 1, j - 1)], (i ^ j)


def left_mul_basis(op_idx: int, state: State8, sign_table: SignTable) -> State8:
    out = [0] * 8
    for j, coeff in enumerate(state):
        if coeff == 0:
            continue
        sign, k = _basis_mul(op_idx, j, sign_table)
        out[k] += sign * coeff
    return tuple(out)  # type: ignore[return-value]


def run_update_trace(initial: State8, op_sequence: Sequence[int], sign_table: SignTable) -> List[State8]:
    cur = initial
    trace = [cur]
    for op_idx in op_sequence:
        cur = left_mul_basis(op_idx, cur, sign_table)
        trace.append(cur)
    return trace


def ckm_like_transport(state: State8, *, phase: int, step: int) -> State8:
    out = list(state)
    a, b, c = out[1], out[2], out[3]

    mode = int(step) % 3
    forward = int(phase) >= 0
    if forward:
        if mode == 0:
            out[1], out[2], out[3] = b, c, a
        elif mode == 1:
            out[1], out[2], out[3] = c, a, b
    else:
        if mode == 0:
            out[1], out[2], out[3] = c, a, b
        elif mode == 1:
            out[1], out[2], out[3] = b, c, a

    if abs(int(phase)) % 2 == 1:
        out[1] = -out[1]
        out[3] = -out[3]
        out[7] = -out[7]
    if abs(int(phase)) % 3 == 2:
        out[2] = -out[2]
        out[7] = -out[7]

    return tuple(out)  # type: ignore[return-value]


def run_update_trace_ckm_transport(
    initial: State8,
    op_sequence: Sequence[int],
    sign_table: SignTable,
    *,
    ckm_phase: int,
    transport_period: int,
) -> List[State8]:
    if int(transport_period) <= 0:
        raise ValueError("transport_period must be > 0")
    cur = initial
    trace = [cur]
    period = int(transport_period)
    for step, op_idx in enumerate(op_sequence, start=1):
        if step % period == 0:
            cur = ckm_like_transport(cur, phase=int(ckm_phase), step=step)
        cur = left_mul_basis(op_idx, cur, sign_table)
        trace.append(cur)
    return trace


def flipped_sign_table() -> SignTable:
    return {(i, j): -s for (i, j), s in FANO_SIGN.items()}


def cp_dual_trace_relation_holds(initial: State8, op_sequence: Sequence[int]) -> bool:
    orig_trace = run_update_trace(initial, op_sequence, FANO_SIGN)
    dual_trace = run_update_trace(cp_map(initial), op_sequence, flipped_sign_table())
    for t, (s_orig, s_dual) in enumerate(zip(orig_trace, dual_trace)):
        lhs = cp_map(s_orig)
        rhs = s_dual if (t % 2 == 0) else tuple(-x for x in s_dual)
        if lhs != rhs:
            return False
    return True


def _weighted_action(state: State8, weights: Sequence[int]) -> int:
    return int(sum(w * (x * x) for w, x in zip(weights, state)))


def cp_weighted_trace_delta(
    initial: State8,
    op_sequence: Sequence[int],
    weights: Sequence[int],
) -> int:
    orig_trace = run_update_trace(initial, op_sequence, FANO_SIGN)
    dual_trace = run_update_trace(cp_map(initial), op_sequence, flipped_sign_table())
    delta = 0
    for s1, s2 in zip(orig_trace, dual_trace):
        delta += _weighted_action(s1, weights) - _weighted_action(s2, weights)
    return delta


def cp_trace_delta(trace: Iterable[State8]) -> int:
    weights = (1, 2, 3, 4, 5, 6, 7, 8)
    delta = 0
    for s in trace:
        delta += _weighted_action(s, weights) - _weighted_action(cp_map(s), weights)
    return delta


def rotate_ops(op_sequence: Sequence[int], shift: int) -> Tuple[int, ...]:
    n = len(op_sequence)
    if n == 0:
        return tuple()
    k = shift % n
    if k == 0:
        return tuple(op_sequence)
    return tuple(op_sequence[k:]) + tuple(op_sequence[:k])


def weak_leakage_strong_residual(
    initial: State8,
    op_sequence: Sequence[int],
    *,
    weak_kick: int,
    phase_shift: int,
    strong_weights: Sequence[int] = STRONG_SECTOR_WEIGHTS,
) -> int:
    if len(op_sequence) <= 10:
        raise ValueError("weak-leakage stress requires deep cone: len(op_sequence) > 10")
    perturbed = list(initial)
    perturbed[7] += int(weak_kick)
    ops_shifted = rotate_ops(op_sequence, int(phase_shift))
    return cp_weighted_trace_delta(tuple(perturbed), ops_shifted, strong_weights)


def weak_leakage_ckm_like_strong_residual(
    initial: State8,
    op_sequence: Sequence[int],
    *,
    weak_kick: int,
    ckm_phase: int,
    transport_period: int = 3,
    strong_weights: Sequence[int] = STRONG_SECTOR_WEIGHTS,
) -> int:
    if len(op_sequence) <= 10:
        raise ValueError("weak-leakage stress requires deep cone: len(op_sequence) > 10")
    if int(transport_period) <= 0:
        raise ValueError("transport_period must be > 0")

    perturbed = list(initial)
    perturbed[7] += int(weak_kick)
    init = tuple(perturbed)

    orig_trace = run_update_trace_ckm_transport(
        init,
        op_sequence,
        FANO_SIGN,
        ckm_phase=int(ckm_phase),
        transport_period=int(transport_period),
    )
    dual_trace = run_update_trace_ckm_transport(
        cp_map(init),
        op_sequence,
        flipped_sign_table(),
        ckm_phase=int(ckm_phase),
        transport_period=int(transport_period),
    )

    delta = 0
    for s1, s2 in zip(orig_trace, dual_trace):
        delta += _weighted_action(s1, strong_weights) - _weighted_action(s2, strong_weights)
    return delta
