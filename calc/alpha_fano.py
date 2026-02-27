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


# ---------------------------------------------------------------------------
# Gate-1 contract functions required by ALPHA-001 task specification
# ---------------------------------------------------------------------------

def fano_line_count() -> int:
    """Return the number of lines in the Fano plane PG(2,2).

    Wraps the module-level FANO_LINES constant as a callable so that
    downstream tests and the Lean statement can refer to the same source.
    Standard Fano plane PG(2,2) has exactly 7 lines.
    """
    return int(FANO_LINES)


def alpha_fano_proxy() -> float:
    """Primary Fano-plane proxy for the fine-structure constant alpha.

    Returns 1 / (FANO_LINES * FANO_POINTS) = 1/49 for the standard Fano
    plane.  This equals alpha_proxy_v1() and is the only shipped proxy that
    lies strictly above the physical value alpha ~ 1/137.036
    (CODATA 2018: Mohr et al., Rev. Mod. Phys. 93, 025010, 2021).
    """
    return alpha_proxy_v1()


def alpha_upper_bound() -> float:
    """Upper bound on alpha derived from Fano-plane combinatorics.

    Returns 1/49 ~ 0.02041, which is strictly greater than the CODATA 2018
    value alpha = 1/137.035999084 ~ 0.007297
    (Mohr et al., Rev. Mod. Phys. 93, 025010, 2021).

    NOTE: alpha_proxy_v2 (= 1/153 ~ 0.00654) and alpha_proxy_v3
    (= 1/145 ~ 0.00690) both fall *below* physical alpha and must NOT
    be used as upper bounds on alpha.
    """
    return alpha_proxy_v1()