"""
test_strong_alpha.py - STRONG-001 numeric verification
Pytest verifying that the COG Fano-plane alpha_s proxy is within 25% of
the PDG value and is an overestimate.

RFC-026 §7: honesty requirement -- gap must be documented, not hidden.
"""

# PDG value of alpha_s at M_Z (2022 PDG review)
alpha_s_phys = 0.1179


def test_alpha_s_fano_estimate():
    """
    Verify the COG leading-order Fano estimate for the strong coupling constant.

    alpha_s_COG = |Stab(e7)| / |Aut(PG(2,2))| = 24 / 168 = 1/7 ~ 0.14286

    The estimate must:
    1. Be within 25% of the PDG value (20% gap is documented in RFC-026).
    2. Be an overestimate (proxy > physical).
    """
    # COG leading-order estimate from Fano geometry
    alpha_s_COG = 1 / 7  # = 24 / 168

    # 1. Within 25% of physical value
    relative_gap = abs(alpha_s_COG - alpha_s_phys) / alpha_s_phys
    assert relative_gap < 0.25, (
        f"COG estimate {alpha_s_COG:.6f} is more than 25% from "
        f"PDG value {alpha_s_phys} (gap = {relative_gap:.1%})"
    )

    # 2. Proxy overestimates physical value
    assert alpha_s_COG > alpha_s_phys, (
        f"COG estimate {alpha_s_COG:.6f} should exceed "
        f"PDG value {alpha_s_phys} (overestimate expected)"
    )