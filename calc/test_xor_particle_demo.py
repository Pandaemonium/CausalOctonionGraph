"""
Tests for calc/xor_particle_demo.py
"""

from calc.xor_octonion_gate import Handedness
from calc.xor_particle_demo import (
    SignedBasis,
    apply_handed_signed,
    e7_vacuum_cycle,
    mul_signed_basis,
    run_handed_sequence,
)


def test_mul_signed_basis_identity_and_square():
    s = SignedBasis(idx=3, sign=1)
    assert mul_signed_basis(SignedBasis(0, 1), s) == s
    assert mul_signed_basis(s, SignedBasis(0, 1)) == s
    assert mul_signed_basis(SignedBasis(4, 1), SignedBasis(4, 1)) == SignedBasis(0, -1)


def test_apply_handed_signed_left_right_distinct_imag():
    state = SignedBasis(idx=2, sign=1)
    left = apply_handed_signed(state, 5, Handedness.LEFT)   # e5 * e2
    right = apply_handed_signed(state, 5, Handedness.RIGHT) # e2 * e5
    assert left.idx == right.idx
    assert left.sign == -right.sign


def test_e7_vacuum_cycle_left():
    # Expected basis-sign orbit: +e7, -e0, -e7, +e0, +e7 ...
    seq = e7_vacuum_cycle(5, Handedness.LEFT)
    expected = [
        SignedBasis(7, 1),
        SignedBasis(0, -1),
        SignedBasis(7, -1),
        SignedBasis(0, 1),
        SignedBasis(7, 1),
    ]
    assert seq == expected


def test_run_handed_sequence_smoke():
    # Start at +e1, apply [L:e2, R:e2, L:e7]
    # This just checks determinism and valid signed-basis output.
    start = SignedBasis(1, 1)
    end = run_handed_sequence(start, [
        (2, Handedness.LEFT),
        (2, Handedness.RIGHT),
        (7, Handedness.LEFT),
    ])
    assert isinstance(end, SignedBasis)
    assert 0 <= end.idx <= 7
    assert end.sign in (-1, 1)

