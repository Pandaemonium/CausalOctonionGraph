"""Alpha proxy formulas from Fano combinatorics (ALPHA-001 Gate 1)."""

from __future__ import annotations

from collections import Counter

from calc.conftest import FANO_CYCLES

FANO_LINES = len(FANO_CYCLES)
FANO_POINTS = len({p for triad in FANO_CYCLES for p in triad})
POINTS_PER_LINE = len(FANO_CYCLES[0]) if FANO_CYCLES else 0
_point_hist = Counter(p for triad in FANO_CYCLES for p in triad)
LINES_PER_POINT = _point_hist.most_common(1)[0][1] if _point_hist else 0

G2_ORDER = 14
GL32_ORDER = 168


def alpha_proxy_v1() -> float:
    """1 / (FANO_LINES * FANO_POINTS): naive area-style proxy."""
    return 1.0 / (FANO_LINES * FANO_POINTS)


def alpha_proxy_v2() -> float:
    """1 / (GL32_ORDER - G2_ORDER - 1): stabilizer-gap proxy."""
    return 1.0 / (GL32_ORDER - G2_ORDER - 1)


def alpha_proxy_v3() -> float:
    """1 / (FANO_LINES^2 * POINTS_PER_LINE - 2): cubic Fano proxy."""
    return 1.0 / (FANO_LINES * FANO_LINES * POINTS_PER_LINE - 2)


def alpha_pdg() -> float:
    """PDG/CODATA target value used for current ALPHA-001 comparisons."""
    return 1.0 / 137.036


def best_proxy() -> tuple[str, float, float]:
    """Return the closest proxy as (name, value, relative_error_to_target)."""
    target = alpha_pdg()
    candidates = [
        ("alpha_proxy_v1", alpha_proxy_v1()),
        ("alpha_proxy_v2", alpha_proxy_v2()),
        ("alpha_proxy_v3", alpha_proxy_v3()),
    ]
    scored = [(name, value, abs(value - target) / target) for name, value in candidates]
    return min(scored, key=lambda item: item[2])

