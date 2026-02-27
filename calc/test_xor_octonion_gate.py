"""
Tests for calc/xor_octonion_gate.py.

Validates the bitwise XOR index channel + orientation sign channel and
explicit left/right handed interaction semantics.
"""

import pytest

from calc.conftest import FANO_SIGN, FANO_THIRD
from calc.xor_octonion_gate import (
    BasisMulResult,
    Handedness,
    apply_handed_operator,
    handed_sign_flip_distinct_imag,
    mul_basis_fast,
    xor_channel,
)


def test_xor_channel_distinct_imaginaries():
    """Distinct imaginary products use XOR index channel."""
    for i in range(1, 8):
        for j in range(1, 8):
            if i == j:
                continue
            assert xor_channel(i, j) == (i ^ j)
            out = mul_basis_fast(i, j)
            assert out.out_idx == (i ^ j)


def test_mul_basis_fast_special_cases():
    """Identity and square rules are handled explicitly."""
    for j in range(8):
        out = mul_basis_fast(0, j)
        assert out == BasisMulResult(out_idx=j, sign=1)
    for i in range(1, 8):
        out = mul_basis_fast(i, 0)
        assert out == BasisMulResult(out_idx=i, sign=1)
        sq = mul_basis_fast(i, i)
        assert sq == BasisMulResult(out_idx=0, sign=-1)


def test_mul_basis_fast_matches_canonical_fano_tables():
    """Distinct imaginary pairwise multiplication matches locked canonical tables."""
    for i in range(1, 8):
        for j in range(1, 8):
            if i == j:
                continue
            out = mul_basis_fast(i, j)
            fi, fj = i - 1, j - 1
            assert out.out_idx == FANO_THIRD[(fi, fj)] + 1
            assert out.sign == FANO_SIGN[(fi, fj)]


def test_handed_left_right_sign_flip_distinct_imaginaries():
    """
    For distinct imaginary units, right-handed application is the same output
    index and opposite sign relative to left-handed application.
    """
    for state_idx in range(1, 8):
        for op_idx in range(1, 8):
            if state_idx == op_idx:
                continue
            assert handed_sign_flip_distinct_imag(state_idx, op_idx)


def test_handed_operator_matches_swapped_order():
    """LEFT uses op*state; RIGHT uses state*op."""
    for state_idx in range(8):
        for op_idx in range(8):
            left = apply_handed_operator(state_idx, op_idx, Handedness.LEFT)
            right = apply_handed_operator(state_idx, op_idx, Handedness.RIGHT)
            assert left == mul_basis_fast(op_idx, state_idx)
            assert right == mul_basis_fast(state_idx, op_idx)


def test_handed_sign_flip_only_for_distinct_imaginaries():
    """
    Sign flip is not a universal rule (identity/square are exceptions),
    but should always hold on the distinct-imaginary domain.
    """
    # Distinct imaginary: must flip
    assert handed_sign_flip_distinct_imag(1, 2)
    assert handed_sign_flip_distinct_imag(7, 3)

    # Equal imaginary: domain error
    with pytest.raises(ValueError):
        handed_sign_flip_distinct_imag(2, 2)

