"""
calc/koide_heawood.py

Spectral utilities for the Heawood graph (Fano incidence bipartite graph):
  - 7 point vertices + 7 line vertices
  - 3-regular bipartite graph
  - adjacency spectrum expected: {+3, -3, +sqrt(2)x6, -sqrt(2)x6}

This module is used for KOIDE-HEAWOOD-001 scaffolding:
the secondary spectral scale sqrt(2) matches the B/A ratio used in Koide work.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Dict, Tuple

import numpy as np

from calc.conftest import FANO_CYCLES


def build_incidence_matrix() -> np.ndarray:
    """
    Build the 7x7 point-line incidence matrix B for PG(2,2).

    Rows are points (0..6), columns are directed-line IDs (0..6).
    Entry B[p, l] = 1 iff point p lies on line l.
    """
    b = np.zeros((7, 7), dtype=int)
    for l_idx, triple in enumerate(FANO_CYCLES):
        for p in triple:
            b[p, l_idx] = 1
    return b


def build_heawood_adjacency() -> np.ndarray:
    """
    Build 14x14 adjacency of the Heawood graph as [0 B; B^T 0].
    """
    b = build_incidence_matrix()
    z = np.zeros((7, 7), dtype=int)
    return np.block([[z, b], [b.T, z]])


def heawood_spectrum() -> np.ndarray:
    """
    Return sorted real eigenvalues of the Heawood adjacency matrix.
    """
    a = build_heawood_adjacency().astype(float)
    vals = np.linalg.eigvals(a)
    vals = np.real_if_close(vals)
    vals = np.array(sorted(float(v) for v in vals), dtype=float)
    return vals


def rounded_spectrum_counts(decimals: int = 10) -> Dict[float, int]:
    """
    Return multiplicities after rounding eigenvalues for stable reporting.
    """
    vals = heawood_spectrum()
    rounded = [float(np.round(v, decimals)) for v in vals]
    return dict(Counter(rounded))


def secondary_mode_value() -> float:
    """
    Return the nontrivial positive secondary eigenvalue (expected sqrt(2)).
    """
    vals = heawood_spectrum()
    positives = sorted(v for v in vals if v > 1e-12)
    # positives should be [sqrt(2)x6, 3]
    if len(positives) < 2:
        raise ValueError("Unexpected Heawood spectrum shape")
    return positives[0]


def koide_heawood_ratio() -> float:
    """
    Alias used by KOIDE-HEAWOOD-001.
    """
    return secondary_mode_value()


def summary() -> Dict[str, object]:
    """
    Return compact summary payload for scripts/notebooks.
    """
    b = build_incidence_matrix()
    a = build_heawood_adjacency()
    sec = secondary_mode_value()
    return {
        "incidence_shape": tuple(b.shape),
        "heawood_shape": tuple(a.shape),
        "degree_sequence": [int(x) for x in np.sum(a, axis=1)],
        "spectrum_counts": rounded_spectrum_counts(),
        "secondary_mode": sec,
        "sqrt2": math.sqrt(2.0),
        "secondary_gap": sec - math.sqrt(2.0),
    }


if __name__ == "__main__":
    payload = summary()
    print("KOIDE-HEAWOOD summary")
    print(f"  incidence_shape: {payload['incidence_shape']}")
    print(f"  heawood_shape:   {payload['heawood_shape']}")
    print(f"  secondary_mode:  {payload['secondary_mode']:.10f}")
    print(f"  sqrt(2):         {payload['sqrt2']:.10f}")
    print(f"  gap:             {payload['secondary_gap']:+.3e}")
    print(f"  spectrum_counts: {payload['spectrum_counts']}")
