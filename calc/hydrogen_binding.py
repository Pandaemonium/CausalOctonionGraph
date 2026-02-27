"""HYDROGEN-001 Gate 1 structural scaffold.

This module is intentionally structural-only:
1. motif overlap and line-incidence logic on the locked Fano cycles,
2. a minimal rational binding proxy based on shared-line count,
3. no physical calibration or spectroscopy claims.
"""

from __future__ import annotations

from fractions import Fraction

from calc.conftest import FANO_CYCLES

ELECTRON_MOTIF = frozenset({1, 2, 3})
PROTON_PROTO_MOTIF = frozenset({1, 2, 4})


def _one_index_cycles(fano_cycles: list[tuple[int, int, int]]) -> list[tuple[int, int, int]]:
    """Convert 0-indexed conftest cycles to 1-indexed motif labels."""
    return [(a + 1, b + 1, c + 1) for (a, b, c) in fano_cycles]


def motif_overlap(m1: frozenset[int], m2: frozenset[int]) -> int:
    """Number of shared motif labels."""
    return len(m1.intersection(m2))


def is_collinear_triad(motif: frozenset[int], fano_cycles: list[tuple[int, int, int]]) -> bool:
    """True iff motif is exactly one Fano line (up to cyclic order)."""
    if len(motif) != 3:
        return False
    cycle_sets = {frozenset(c) for c in _one_index_cycles(fano_cycles)}
    return motif in cycle_sets


def shared_pair(m1: frozenset[int], m2: frozenset[int]) -> frozenset[int]:
    """Shared two-point pair for motif intersections."""
    return frozenset(m1.intersection(m2))


def line_through_pair(
    pair: frozenset[int], fano_cycles: list[tuple[int, int, int]]
) -> tuple[int, int, int] | None:
    """Return the unique 1-indexed Fano line containing both pair points, if present."""
    if len(pair) != 2:
        return None
    for line in _one_index_cycles(fano_cycles):
        if pair.issubset(set(line)):
            return line
    return None


def binding_proxy(shared_line_count: int) -> Fraction:
    """Structural proxy: shared lines as a fraction of 7 total Fano lines."""
    if shared_line_count < 0:
        raise ValueError("shared_line_count must be non-negative")
    return Fraction(shared_line_count, 7)


def classify_motif(motif: frozenset[int], fano_cycles: list[tuple[int, int, int]]) -> str:
    """Classify a 3-point motif as collinear (associative line) or non-collinear triad."""
    if len(motif) != 3:
        raise ValueError("motif must have exactly 3 points")
    return "associative_line" if is_collinear_triad(motif, fano_cycles) else "noncollinear_triad"


def _shared_line_count(m1: frozenset[int], m2: frozenset[int], fano_cycles: list[tuple[int, int, int]]) -> int:
    """Count Fano lines that contain at least one point from each motif."""
    count = 0
    for line in _one_index_cycles(fano_cycles):
        line_set = set(line)
        if line_set.intersection(m1) and line_set.intersection(m2):
            count += 1
    return count


def hydrogen_binding_proxy() -> Fraction:
    """Convenience wrapper for the current electron/proton-proto motifs."""
    shared_lines = _shared_line_count(ELECTRON_MOTIF, PROTON_PROTO_MOTIF, FANO_CYCLES)
    return binding_proxy(shared_lines)

