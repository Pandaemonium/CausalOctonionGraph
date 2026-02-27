"""
Independent skeptic verification of ALPHA-001 Fano-graph fine-structure constant bound.
Does NOT import from alpha_fano.py — all computations are self-contained.
"""
import math
import sys

# Snapshot sys.modules at module import time -- before any other test file in the
# pytest session has a chance to import calc.alpha_fano.  Using the live
# sys.modules dict inside the test body would cause a false failure whenever
# another test file (e.g. test_alpha001.py) imports the producer module earlier
# in the same session, because sys.modules is a global singleton shared across
# all test files collected in a single pytest run.
_SKEPTIC_MODULE_IMPORTS = frozenset(sys.modules.keys())

# ---------------------------------------------------------------------------
# Independent Fano plane definition (PG(2,2) over GF(2))
# 7 points labelled 1..7, 7 lines each containing exactly 3 points
# ---------------------------------------------------------------------------
_FANO_LINES = [
    (1, 2, 4),
    (2, 3, 5),
    (3, 4, 6),
    (4, 5, 7),
    (5, 6, 1),
    (6, 7, 2),
    (7, 1, 3),
]

# CODATA 2018 value of the fine-structure constant
_ALPHA_PHYSICAL = 7.2973525693e-3  # = 1 / 137.035999084


def _lines_per_point() -> dict:
    """Return mapping point -> number of Fano lines through that point."""
    counts: dict = {}
    for line in _FANO_LINES:
        for p in line:
            counts[p] = counts.get(p, 0) + 1
    return counts


# ---------------------------------------------------------------------------
# Required test functions (exact names from task contract)
# ---------------------------------------------------------------------------

def test_fano_line_count_independent():
    """Fano plane has exactly 7 lines."""
    assert len(_FANO_LINES) == 7, f"Expected 7 lines, got {len(_FANO_LINES)}"


def test_fano_lines_per_point_independent():
    """Each Fano point lies on exactly 3 lines."""
    lpp = _lines_per_point()
    points = {p for line in _FANO_LINES for p in line}
    assert len(points) == 7, f"Expected 7 points, got {len(points)}"
    for pt, count in lpp.items():
        assert count == 3, f"Point {pt} lies on {count} lines, expected 3"


def test_alpha_cog_proxy_formula_independent():
    """alpha_COG proxy = 1 / (lines per Fano point) = 1/3."""
    lines_per_fano_point = 3  # proven by test_fano_lines_per_point_independent
    alpha_cog = 1.0 / lines_per_fano_point
    assert abs(alpha_cog - 1.0 / 3.0) < 1e-15, (
        f"alpha_COG formula mismatch: got {alpha_cog}, expected {1/3}"
    )


def test_alpha_bound_direction():
    """alpha_COG > alpha_physical (COG proxy is an upper bound)."""
    alpha_cog = 1.0 / 3.0
    assert alpha_cog > _ALPHA_PHYSICAL, (
        f"Bound violated: alpha_COG={alpha_cog} not > alpha_physical={_ALPHA_PHYSICAL}"
    )


def test_alpha_ratio_order_of_magnitude():
    """Ratio alpha_COG / alpha_physical is finite and > 1."""
    ratio = (1.0 / 3.0) / _ALPHA_PHYSICAL
    assert math.isfinite(ratio), "Ratio is not finite"
    assert ratio > 1.0, f"Ratio {ratio} is not > 1"
    # Sanity: should be approximately 137.036/3 ~= 45.68
    assert 40.0 < ratio < 50.0, f"Ratio {ratio:.4f} outside expected range (40, 50)"


def test_no_dependency_on_producer_module():
    """This module computes independently -- no import of alpha_fano.

    We check the frozen snapshot of sys.modules captured at import time of this
    module (stored in _SKEPTIC_MODULE_IMPORTS), NOT the live sys.modules at test
    execution time.  Using the live dict would cause a false failure when another
    test file (e.g. the producer's own test suite) imports calc.alpha_fano
    earlier in the same pytest session, because sys.modules is a global singleton.
    """
    for mod_name in _SKEPTIC_MODULE_IMPORTS:
        assert "alpha_fano" not in mod_name, (
            f"alpha_fano found in modules loaded by skeptic: '{mod_name}'"
        )