"""EE-SCAT-001: Electron-electron scattering kinematics scaffold (Gate 1).

Implements discrete momentum-exchange combinatorics for two-electron
repulsion in the COG causal graph framework.

Octonion index convention: 7 Fano lines per CONVENTIONS.md Section 2.
Electron motif: (1, 2, 3) — indices of e1, e2, e3.
"""

from __future__ import annotations

# Fano lines per CONVENTIONS.md Section 2
_FANO_LINES: list[tuple[int, int, int]] = [
    (1, 2, 3),
    (1, 4, 5),
    (1, 7, 6),
    (2, 4, 6),
    (2, 5, 7),
    (3, 4, 7),
    (3, 6, 5),
]

# Electron motif: indices of e1, e2, e3
_ELECTRON_MOTIF: tuple[int, int, int] = (1, 2, 3)


def momentum_transfer(p1: tuple, p2: tuple) -> tuple:
    """Return component-wise difference p1 - p2 in Z^3."""
    return tuple(a - b for a, b in zip(p1, p2))


def is_fano_collinear(a: int, b: int, c: int) -> bool:
    """Return True if indices a, b, c form a Fano line per CONVENTIONS.md Section 2."""
    triple = frozenset({a, b, c})
    return any(frozenset(line) == triple for line in _FANO_LINES)


def scattering_channel(motif1: tuple, motif2: tuple) -> str:
    """Return 't', 'u', or 's' depending on shared Fano structure.

    - 't': motifs share 2 indices (t-channel, momentum exchange)
    - 'u': motifs share 1 index (u-channel, exchange diagram)
    - 's': motifs share 0 indices (s-channel, annihilation)
    """
    shared = len(frozenset(motif1) & frozenset(motif2))
    if shared >= 2:
        return "t"
    elif shared == 1:
        return "u"
    else:
        return "s"


def mandelstam_proxy_t(p_in: tuple, p_out: tuple) -> int:
    """Return sum of squares of momentum transfer components (discrete Mandelstam t).

    t_proxy = sum_i (p_in_i - p_out_i)^2  >= 0
    """
    transfer = momentum_transfer(p_in, p_out)
    return sum(x * x for x in transfer)


def ee_scattering_is_repulsive(motif1: tuple, motif2: tuple) -> bool:
    """Return True when both motifs are electron-type {1, 2, 3}.

    Both particles must match the electron motif (1, 2, 3) per
    CONVENTIONS.md Section 2 (indices of e1, e2, e3).
    """
    return tuple(motif1) == _ELECTRON_MOTIF and tuple(motif2) == _ELECTRON_MOTIF


# Gauss