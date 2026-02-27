"""
calc/xor_octonion_gate.py

Bitwise XOR interaction kernel for octonion basis-unit products with explicit handedness.

Conventions:
  - Basis indices are 0..7 where:
      0 -> e0 (real identity)
      1..7 -> e1..e7 (imaginary units)
  - For distinct imaginary units e_i, e_j (i,j in 1..7, i != j):
      output index channel: k = i xor j
      sign channel: lookup from locked Fano orientation table
  - Handedness:
      LEFT  means operator hits from left:  e_op * e_state
      RIGHT means operator hits from right: e_state * e_op

This module is a fast basis-unit gate. It intentionally does not replace the
full Octonion implementation; it is an execution kernel with strict parity tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from calc.conftest import FANO_SIGN, FANO_THIRD


class Handedness(str, Enum):
    LEFT = "left"
    RIGHT = "right"


@dataclass(frozen=True)
class BasisMulResult:
    out_idx: int   # 0..7 (0 is e0)
    sign: int      # +/-1 (for basis-unit multiplication path)


def _check_basis_idx(idx: int) -> None:
    if not (0 <= idx <= 7):
        raise ValueError(f"Basis index must be in [0,7], got {idx}")


def _check_imag_idx(idx: int) -> None:
    if not (1 <= idx <= 7):
        raise ValueError(f"Imaginary basis index must be in [1,7], got {idx}")


def xor_channel(i: int, j: int) -> int:
    """
    XOR output channel for one-indexed imaginary basis labels.
    Only valid for i,j in [1,7].
    """
    _check_imag_idx(i)
    _check_imag_idx(j)
    return i ^ j


def mul_basis_fast(i: int, j: int) -> BasisMulResult:
    """
    Basis multiplication gate for e_i * e_j in index form (0..7).

    Special cases:
      - i == 0: e0 * ej = ej
      - j == 0: ei * e0 = ei
      - i == j != 0: ei * ei = -e0

    Distinct imaginary case (i,j in 1..7, i != j):
      - out_idx = i xor j
      - sign from locked Fano orientation table
    """
    _check_basis_idx(i)
    _check_basis_idx(j)

    if i == 0:
        return BasisMulResult(out_idx=j, sign=1)
    if j == 0:
        return BasisMulResult(out_idx=i, sign=1)
    if i == j:
        return BasisMulResult(out_idx=0, sign=-1)

    # Distinct imaginary units: use XOR index channel + Fano sign channel.
    fi = i - 1  # map e1..e7 -> Fano points 0..6
    fj = j - 1
    sign = int(FANO_SIGN[(fi, fj)])
    out_idx = int(FANO_THIRD[(fi, fj)] + 1)

    # Defensive contract check: canonical table must match XOR index channel.
    xor_idx = i ^ j
    if out_idx != xor_idx:
        raise RuntimeError(
            f"Fano/XOR mismatch for ({i},{j}): table={out_idx}, xor={xor_idx}"
        )
    return BasisMulResult(out_idx=out_idx, sign=sign)


def apply_handed_operator(state_idx: int, op_idx: int, hand: Handedness) -> BasisMulResult:
    """
    Apply a basis operator to a basis state with explicit handedness.

    LEFT:  e_op * e_state
    RIGHT: e_state * e_op
    """
    _check_basis_idx(state_idx)
    _check_basis_idx(op_idx)

    if hand is Handedness.LEFT:
        return mul_basis_fast(op_idx, state_idx)
    if hand is Handedness.RIGHT:
        return mul_basis_fast(state_idx, op_idx)
    raise ValueError(f"Unsupported handedness: {hand}")


def handed_sign_flip_distinct_imag(state_idx: int, op_idx: int) -> bool:
    """
    Contract check for distinct imaginary units:
      RIGHT sign = -LEFT sign, output index identical.
    """
    _check_imag_idx(state_idx)
    _check_imag_idx(op_idx)
    if state_idx == op_idx:
        raise ValueError("Requires distinct imaginary indices")

    left = apply_handed_operator(state_idx, op_idx, Handedness.LEFT)
    right = apply_handed_operator(state_idx, op_idx, Handedness.RIGHT)
    return left.out_idx == right.out_idx and right.sign == -left.sign
