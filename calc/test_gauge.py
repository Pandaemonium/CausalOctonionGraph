"""
Claim-level tests for GAUGE-001 using calc/gauge_check.py helpers.
"""

from itertools import permutations

import pytest

from calc.gauge_check import (
    all_fano_auts,
    color_permutation_group,
    orbit_of,
    vacuum_lines,
    vacuum_stabilizer,
)


@pytest.fixture(scope="module")
def group_data() -> tuple[list[list[int]], list[list[int]]]:
    auts = all_fano_auts()
    return auts, vacuum_stabilizer(auts)


def test_fano_automorphism_count(group_data: tuple[list[list[int]], list[list[int]]]) -> None:
    auts, _ = group_data
    assert len(auts) == 168


def test_vacuum_stabilizer_count(group_data: tuple[list[list[int]], list[list[int]]]) -> None:
    _, stab = group_data
    assert len(stab) == 24


def test_vacuum_lines_count() -> None:
    assert len(vacuum_lines()) == 3


def test_orbit_stabilizer_identity(group_data: tuple[list[list[int]], list[list[int]]]) -> None:
    auts, stab = group_data
    orbit_size = len(orbit_of(auts, 0))
    assert orbit_size * len(stab) == len(auts) == 168


def test_color_permutation_action_is_s3(group_data: tuple[list[list[int]], list[list[int]]]) -> None:
    _, stab = group_data
    induced = color_permutation_group(stab)
    assert induced == set(permutations((0, 1, 2)))
