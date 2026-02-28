"""
S3 covariance checks for Witt-pair cyclic permutation under a minimal update rule.

This module encodes the known Fano automorphism used in Lean:
  wittPairCyclicPerm = [4,2,5,0,3,1,6]   (0-indexed points for e1..e7)
and checks covariance of left-multiplication update dynamics.
"""

from __future__ import annotations

from typing import Dict, Sequence, Tuple

from calc.conftest import FANO_SIGN, FANO_THIRD

State8 = Tuple[int, int, int, int, int, int, int, int]
SignTable = Dict[Tuple[int, int], int]

# 0-indexed map on imaginary basis points (e1..e7).
WITT_PAIR_CYCLIC_PERM_0: Tuple[int, ...] = (4, 2, 5, 0, 3, 1, 6)


def permute_basis_index(idx: int) -> int:
    """Permute basis index in 0..7; scalar e0 remains fixed."""
    if idx == 0:
        return 0
    return WITT_PAIR_CYCLIC_PERM_0[idx - 1] + 1


def permute_state(state: State8) -> State8:
    """Apply Witt-pair cyclic permutation to imaginary slots of state."""
    out = [0] * 8
    out[0] = state[0]
    for idx in range(1, 8):
        out[permute_basis_index(idx)] = state[idx]
    return tuple(out)  # type: ignore[return-value]


def _basis_mul(i: int, j: int, sign_table: SignTable) -> Tuple[int, int]:
    if i == 0:
        return 1, j
    if j == 0:
        return 1, i
    if i == j:
        return -1, 0
    return sign_table[(i - 1, j - 1)], FANO_THIRD[(i - 1, j - 1)] + 1


def left_mul_basis(op_idx: int, state: State8, sign_table: SignTable = FANO_SIGN) -> State8:
    out = [0] * 8
    for j, coeff in enumerate(state):
        if coeff == 0:
            continue
        sign, k = _basis_mul(op_idx, j, sign_table)
        out[k] += sign * coeff
    return tuple(out)  # type: ignore[return-value]


def one_step_covariant(state: State8, op_idx: int) -> bool:
    """
    Check:
      sigma(op * state) = sigma(op) * sigma(state)
    """
    lhs = permute_state(left_mul_basis(op_idx, state, FANO_SIGN))
    rhs = left_mul_basis(permute_basis_index(op_idx), permute_state(state), FANO_SIGN)
    return lhs == rhs


def run_trace(initial: State8, op_sequence: Sequence[int]) -> Tuple[State8, ...]:
    cur = initial
    trace = [cur]
    for op_idx in op_sequence:
        cur = left_mul_basis(op_idx, cur, FANO_SIGN)
        trace.append(cur)
    return tuple(trace)


def multistep_covariant(initial: State8, op_sequence: Sequence[int]) -> bool:
    """
    Check full-trace covariance under permutation transport:
      sigma(trace(initial, ops)[t]) == trace(sigma(initial), sigma(ops))[t]
    """
    lhs = tuple(permute_state(s) for s in run_trace(initial, op_sequence))
    perm_ops = tuple(permute_basis_index(op) for op in op_sequence)
    rhs = run_trace(permute_state(initial), perm_ops)
    return lhs == rhs
