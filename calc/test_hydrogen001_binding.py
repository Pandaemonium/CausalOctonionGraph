"""Tests for HYDROGEN-001 Gate 1 structural scaffold."""

from __future__ import annotations

from fractions import Fraction

import yaml

from calc.conftest import FANO_CYCLES
from calc.hydrogen_binding import (
    ELECTRON_MOTIF,
    PROTON_PROTO_MOTIF,
    binding_proxy,
    classify_motif,
    is_collinear_triad,
    line_through_pair,
    motif_overlap,
    shared_pair,
)


def test_fano_cycles_match_locked_conventions():
    expected = {
        (0, 1, 2),
        (0, 3, 4),
        (0, 6, 5),
        (1, 3, 5),
        (1, 4, 6),
        (2, 3, 6),
        (2, 5, 4),
    }
    assert set(FANO_CYCLES) == expected


def test_electron_motif_is_collinear_associative():
    assert is_collinear_triad(ELECTRON_MOTIF, FANO_CYCLES) is True
    assert classify_motif(ELECTRON_MOTIF, FANO_CYCLES) == "associative_line"


def test_proton_proto_motif_is_noncollinear():
    assert is_collinear_triad(PROTON_PROTO_MOTIF, FANO_CYCLES) is False
    assert classify_motif(PROTON_PROTO_MOTIF, FANO_CYCLES) == "noncollinear_triad"


def test_motif_overlap_is_two_points():
    assert motif_overlap(ELECTRON_MOTIF, PROTON_PROTO_MOTIF) == 2
    assert shared_pair(ELECTRON_MOTIF, PROTON_PROTO_MOTIF) == frozenset({1, 2})


def test_unique_line_through_shared_pair_is_l1():
    pair = shared_pair(ELECTRON_MOTIF, PROTON_PROTO_MOTIF)
    line = line_through_pair(pair, FANO_CYCLES)
    assert line is not None
    assert set(line) == {1, 2, 3}


def test_binding_proxy_positive_and_less_than_one():
    pair = shared_pair(ELECTRON_MOTIF, PROTON_PROTO_MOTIF)
    shared_line_count = 1 if line_through_pair(pair, FANO_CYCLES) is not None else 0
    val = binding_proxy(shared_line_count)
    assert isinstance(val, Fraction)
    assert val == Fraction(1, 7)
    assert Fraction(0, 1) < val < Fraction(1, 1)


def test_motif_classification_is_deterministic():
    results = [classify_motif(ELECTRON_MOTIF, FANO_CYCLES) for _ in range(5)]
    assert all(r == "associative_line" for r in results)

    results_proto = [classify_motif(PROTON_PROTO_MOTIF, FANO_CYCLES) for _ in range(5)]
    assert all(r == "noncollinear_triad" for r in results_proto)


def test_hydrogen_claim_yaml_exists_and_partial():
    with open("claims/HYDROGEN-001.yml", "r", encoding="utf-8") as f:
        claim = yaml.safe_load(f)
    assert claim["id"] == "HYDROGEN-001"
    assert claim["status"] == "partial"
    assert claim["python_test"] == "calc/test_hydrogen001_binding.py"

