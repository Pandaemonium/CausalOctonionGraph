"""Shared pytest fixtures and convention constants for HACG.

This file is the Python source of truth for the Furey convention.
All values MUST match rfc/CONVENTIONS.md exactly.
"""

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Section 2 of CONVENTIONS.md: The 7 directed cyclic triples
# (i, j, k) means e_i * e_j = +e_k (cyclic), e_j * e_i = -e_k (anti-cyclic)
# ---------------------------------------------------------------------------
FANO_CYCLES: list[tuple[int, int, int]] = [
    (1, 2, 3),
    (1, 4, 5),
    (1, 7, 6),
    (2, 4, 6),
    (2, 5, 7),
    (3, 4, 7),
    (3, 6, 5),
]

# ---------------------------------------------------------------------------
# Generated from FANO_CYCLES: the sign tensor ε(i,j) and third-index k
# fano_sign[i][j] = +1 or -1 for i,j in {1..7}, i ≠ j
# fano_third[i][j] = k such that e_i * e_j = fano_sign[i][j] * e_k
# ---------------------------------------------------------------------------

def _build_tables() -> tuple[np.ndarray, np.ndarray]:
    """Generate the 7x7 sign and third-index tables from FANO_CYCLES."""
    sign = np.zeros((8, 8), dtype=int)   # index 0 unused for imaginary part
    third = np.zeros((8, 8), dtype=int)
    for i, j, k in FANO_CYCLES:
        # Cyclic: (i,j)->+k, (j,k)->+i, (k,i)->+j
        sign[i, j] = +1; third[i, j] = k
        sign[j, k] = +1; third[j, k] = i
        sign[k, i] = +1; third[k, i] = j
        # Anti-cyclic: (j,i)->-k, (k,j)->-i, (i,k)->-j
        sign[j, i] = -1; third[j, i] = k
        sign[k, j] = -1; third[k, j] = i
        sign[i, k] = -1; third[i, k] = j
    return sign, third

FANO_SIGN, FANO_THIRD = _build_tables()

# ---------------------------------------------------------------------------
# Section 5 of CONVENTIONS.md: Witt basis pairings
# Color index j -> (e_{a}, e_{b}) where α_j = ½(e_a + i·e_b)
# ---------------------------------------------------------------------------
WITT_PAIRS: list[tuple[int, int]] = [
    (1, 4),  # α_1 = ½(e_1 + i·e_4)
    (2, 5),  # α_2 = ½(e_2 + i·e_5)
    (3, 6),  # α_3 = ½(e_3 + i·e_6)
]

# Section 5.1: Symmetry-breaking axis
VACUUM_AXIS: int = 7  # e_7


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def fano_cycles():
    """The 7 directed Fano triples (Furey convention)."""
    return FANO_CYCLES

@pytest.fixture
def fano_sign():
    """8x8 sign table (indices 1-7 are imaginary units)."""
    return FANO_SIGN

@pytest.fixture
def fano_third():
    """8x8 third-index table."""
    return FANO_THIRD

@pytest.fixture
def witt_pairs():
    """The 3 Witt basis pairings [(1,4), (2,5), (3,6)]."""
    return WITT_PAIRS
