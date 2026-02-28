"""Tests for S3 Witt-pair covariance of minimal update dynamics."""

from calc.witt_s3_update_covariance import (
    left_mul_basis,
    multistep_covariant,
    one_step_covariant,
    permute_basis_index,
    permute_state,
)


def _basis_state(idx: int) -> tuple[int, int, int, int, int, int, int, int]:
    out = [0] * 8
    out[idx] = 1
    return tuple(out)  # type: ignore[return-value]


def test_permutation_keeps_scalar_fixed() -> None:
    assert permute_basis_index(0) == 0
    assert permute_state((5, 1, 2, 3, 4, 5, 6, 7))[0] == 5


def test_one_step_covariance_on_basis_states() -> None:
    for op_idx in range(1, 8):
        for st_idx in range(0, 8):
            assert one_step_covariant(_basis_state(st_idx), op_idx)


def test_one_step_covariance_on_dense_state() -> None:
    state = (2, -1, 3, 0, -2, 1, 4, -3)
    for op_idx in (1, 2, 3, 4, 5, 6, 7):
        assert one_step_covariant(state, op_idx)


def test_multistep_covariance_fixed_sequence() -> None:
    initial = (1, 2, -1, 0, 3, -2, 1, 4)
    ops = (1, 7, 3, 5, 2, 6, 4, 1, 2, 3)
    assert multistep_covariant(initial, ops)


def test_multistep_covariance_alternate_sequence() -> None:
    initial = (0, 1, 1, 2, -1, 3, -2, 1)
    ops = (7, 6, 5, 4, 3, 2, 1, 7, 7, 1, 1)
    assert multistep_covariant(initial, ops)
