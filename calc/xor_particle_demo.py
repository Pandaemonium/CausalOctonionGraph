"""
calc/xor_particle_demo.py

Minimal signed-basis simulation helpers using the XOR octonion gate.
This is intentionally a toy layer for simple motif/phase experiments.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from calc.xor_octonion_gate import Handedness, apply_handed_operator, mul_basis_fast


@dataclass(frozen=True)
class SignedBasis:
    """
    Signed basis unit:
      sign * e_idx, with idx in 0..7 and sign in {+1, -1}.
    """
    idx: int
    sign: int = 1

    def __post_init__(self) -> None:
        if not (0 <= self.idx <= 7):
            raise ValueError(f"idx must be in [0,7], got {self.idx}")
        if self.sign not in (-1, 1):
            raise ValueError(f"sign must be +/-1, got {self.sign}")


def mul_signed_basis(lhs: SignedBasis, rhs: SignedBasis) -> SignedBasis:
    """
    Multiply two signed basis units exactly:
      (s1 * e_i) * (s2 * e_j) = (s1*s2*s3) * e_k
    where (k, s3) is the unsigned basis multiplication result from the XOR gate.
    """
    core = mul_basis_fast(lhs.idx, rhs.idx)
    return SignedBasis(idx=core.out_idx, sign=lhs.sign * rhs.sign * core.sign)


def apply_handed_signed(state: SignedBasis, op_idx: int, hand: Handedness) -> SignedBasis:
    """
    Apply unsigned operator basis unit to a signed state with handedness:
      LEFT : e_op * state
      RIGHT: state * e_op
    """
    if hand is Handedness.LEFT:
        return mul_signed_basis(SignedBasis(op_idx, 1), state)
    if hand is Handedness.RIGHT:
        return mul_signed_basis(state, SignedBasis(op_idx, 1))
    raise ValueError(f"Unsupported handedness: {hand}")


def run_handed_sequence(
    state: SignedBasis,
    ops: Iterable[tuple[int, Handedness]],
) -> SignedBasis:
    """
    Run a sequence of handed operator hits.
    Each op is a tuple (op_idx, hand).
    """
    cur = state
    for op_idx, hand in ops:
        # parity check: ensure handed operator helper agrees with lower-level gate.
        _ = apply_handed_operator(cur.idx, op_idx, hand)
        cur = apply_handed_signed(cur, op_idx, hand)
    return cur


def e7_vacuum_cycle(step_count: int, hand: Handedness = Handedness.LEFT) -> list[SignedBasis]:
    """
    Return the sequence obtained by repeatedly applying e7 for step_count steps,
    starting from +e7.
    """
    out: list[SignedBasis] = []
    cur = SignedBasis(idx=7, sign=1)
    for _ in range(step_count):
        out.append(cur)
        cur = apply_handed_signed(cur, 7, hand)
    return out

