"""
calc/fundamental_constants.py
RFC-007: Numerical framework for deriving fundamental constants

Provides:
  - CODATA 2022 experimental values for each target constant
  - Fano group-theoretic data (from GAUGE-001)
  - Leading-order COG candidates and their accuracy gaps
  - Helper functions for the eventual Monte Carlo derivations

COG derivation targets
──────────────────────
  ALPHA-001   Fine-structure constant   α ≈ 1/137.036
  STRONG-001  Strong coupling           α_s(M_Z) ≈ 0.1181
  WEINBERG-001 Weinberg angle           sin²θ_W ≈ 0.2312
  MU-001      Proton/electron mass      μ ≈ 1836.15

All group-theoretic constants come from GAUGE-001 (proved):
  |GL(3,2)| = 168,  |SL(2,3)| = 24,  orbit = 7,  Witt lines = 3.
"""

import math
from dataclasses import dataclass

# ──────────────────────────────────────────────────────────────────────────────
# CODATA 2022 experimental values
# ──────────────────────────────────────────────────────────────────────────────

# Fine-structure constant (CODATA 2022)
ALPHA_EXP: float = 7.2973525693e-3           # dimensionless
ALPHA_INVERSE_EXP: float = 1.0 / ALPHA_EXP  # ≈ 137.035999084

# Strong coupling at the Z-boson mass scale (PDG 2023)
ALPHA_S_EXP: float = 0.1180            # at M_Z = 91.1876 GeV
ALPHA_S_UNCERTAINTY: float = 0.0009

# Weinberg angle, sin²θ_W, MS-bar at M_Z (PDG 2023)
SIN2_THETA_W_EXP: float = 0.23122
SIN2_THETA_W_UNCERTAINTY: float = 0.00003

# Proton-to-electron mass ratio (CODATA 2022)
MU_EXP: float = 1836.15267343           # m_p / m_e
MU_UNCERTAINTY: float = 0.00000011

# ──────────────────────────────────────────────────────────────────────────────
# Fano group data (GAUGE-001, proved in GaugeGroup.lean)
# ──────────────────────────────────────────────────────────────────────────────

FANO_AUT_ORDER: int = 168        # |GL(3,2)| = |Aut(PG(2,2))|
VACUUM_STAB_ORDER: int = 24      # |SL(2,3)| = |Stab(e₇)|
FANO_ORBIT_SIZE: int = 7         # orbit of any point under GL(3,2)
WITT_PAIRS: int = 3              # lines through the vacuum axis

assert FANO_AUT_ORDER == FANO_ORBIT_SIZE * VACUUM_STAB_ORDER, (
    "Orbit-stabilizer consistency check failed"
)

# ──────────────────────────────────────────────────────────────────────────────
# Candidate formulas
# ──────────────────────────────────────────────────────────────────────────────

# STRONG-001 leading-order candidate: trapped fraction = Stab / GL(3,2)
ALPHA_S_CANDIDATE: float = VACUUM_STAB_ORDER / FANO_AUT_ORDER  # = 1/7 ≈ 0.14286

# ALPHA-001 placeholder (no formula yet)
ALPHA_CANDIDATE: float = 0.0   # research target

# WEINBERG-001 tentative candidates
# 3/13 ≈ 0.2308 is numerically suggestive (3 = Witt lines, 13 = ?)
# 3/(3+10) where 10 = dim(SU(3)) is too ad hoc; not claimed.
WEINBERG_CANDIDATE_3_13: float = 3.0 / 13.0    # ≈ 0.2308
WEINBERG_CANDIDATE_NAIVE: float = 2.0 / 4.0    # dim(C)/dim(H) = 0.5 (wrong)

# MU-001 known numerical coincidences (not derivations)
MU_6PI5: float = 6.0 * math.pi ** 5             # ≈ 1836.118

# ──────────────────────────────────────────────────────────────────────────────
# Accuracy diagnostics
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class DerivationStatus:
    """Summary of current derivation status for one constant."""
    claim_id: str
    name: str
    experimental: float
    candidate: float
    fractional_gap: float        # |candidate - exp| / |exp|
    status: str                  # 'no candidate' | 'gap ~X%' | 'proved'
    comment: str


def compute_gap(candidate: float, experimental: float) -> float:
    """Fractional gap |candidate - exp| / |exp|. Returns inf if exp = 0."""
    if experimental == 0.0:
        return math.inf
    return abs(candidate - experimental) / abs(experimental)


def build_status_table() -> list[DerivationStatus]:
    return [
        DerivationStatus(
            claim_id="ALPHA-001",
            name="Fine-structure constant α",
            experimental=ALPHA_EXP,
            candidate=ALPHA_CANDIDATE,
            fractional_gap=compute_gap(ALPHA_CANDIDATE, ALPHA_EXP),
            status="no candidate",
            comment=(
                "No formula yet.  Simple Fano ratios are all O(10x) off."
                "  Must come from U(1) phase-space volume in C⊗O."
            ),
        ),
        DerivationStatus(
            claim_id="STRONG-001",
            name="Strong coupling α_s(M_Z)",
            experimental=ALPHA_S_EXP,
            candidate=ALPHA_S_CANDIDATE,
            fractional_gap=compute_gap(ALPHA_S_CANDIDATE, ALPHA_S_EXP),
            status=f"gap ~{compute_gap(ALPHA_S_CANDIDATE, ALPHA_S_EXP):.0%}",
            comment=(
                "Leading-order: 24/168 = 1/7 ≈ 0.1429."
                "  Experimental 0.1180.  ~21% gap."
                "  May close with finite-density / running corrections."
            ),
        ),
        DerivationStatus(
            claim_id="WEINBERG-001",
            name="Weinberg angle sin²θ_W",
            experimental=SIN2_THETA_W_EXP,
            candidate=WEINBERG_CANDIDATE_3_13,
            fractional_gap=compute_gap(WEINBERG_CANDIDATE_3_13, SIN2_THETA_W_EXP),
            status=f"tentative, gap ~{compute_gap(WEINBERG_CANDIDATE_3_13, SIN2_THETA_W_EXP):.1%}",
            comment=(
                "3/13 ≈ 0.2308 is numerically suggestive but not derived."
                "  Naive dim(C)/dim(H) = 0.5 is wrong."
                "  No formula yet from first principles."
            ),
        ),
        DerivationStatus(
            claim_id="MU-001",
            name="Proton/electron mass ratio μ",
            experimental=MU_EXP,
            candidate=MU_6PI5,
            fractional_gap=compute_gap(MU_6PI5, MU_EXP),
            status="numerological coincidence, not derived",
            comment=(
                f"6π⁵ ≈ {MU_6PI5:.4f} matches to 0.002% but is NOT a COG"
                " derivation.  Awaits proton motif implementation (MU-001)."
            ),
        ),
    ]


# ──────────────────────────────────────────────────────────────────────────────
# Running of α_s (qualitative)
# ──────────────────────────────────────────────────────────────────────────────

def alpha_s_running_2loop(Q_gev: float,
                           n_flavours: int = 5,
                           lambda_qcd_gev: float = 0.217) -> float:
    """
    1-loop (leading-log) running of α_s(Q).

    α_s(Q) ≈ 1 / (b0 * ln(Q²/Λ²))  =  1 / (b0 * 2*ln(Q/Λ))
    where b0 = (33 - 2*Nf) / (12*pi).

    Note: the factor 2 comes from ln(Q²/Λ²) = 2*ln(Q/Λ).  Omitting it
    gives a formula that is 2× too large (a common typo).

    This is a rough approximation only — good to ~30-50% for Q ≈ M_Z.
    Lambda_QCD ≈ 217 MeV (5-flavour MS-bar, PDG 2023).
    """
    b0 = (33 - 2 * n_flavours) / (12 * math.pi)
    ratio = Q_gev / lambda_qcd_gev
    if ratio <= 1.0:
        return float('inf')   # confinement regime
    return 1.0 / (b0 * 2.0 * math.log(ratio))


def find_alpha_s_matching_scale(target: float = ALPHA_S_CANDIDATE) -> float:
    """
    Find the scale Q* (in GeV) where the running α_s(Q*) equals the
    COG leading-order candidate (1/7).  This is the 'matching scale'.

    If the COG formula gives α_s at some natural high-energy scale
    rather than at M_Z, this tells us what that scale is.
    """
    # Binary search in [1 GeV, 1e6 GeV]
    lo, hi = 1.0, 1e6
    for _ in range(60):
        mid = (lo + hi) / 2.0
        if alpha_s_running_2loop(mid) > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


# ──────────────────────────────────────────────────────────────────────────────
# Diagnostics
# ──────────────────────────────────────────────────────────────────────────────

def summary() -> None:
    print("RFC-007 Fundamental Constants — COG Derivation Status")
    print("=" * 65)

    print("\nFano group data (GAUGE-001, proved):")
    print(f"  |GL(3,2)| = {FANO_AUT_ORDER}")
    print(f"  |SL(2,3)| = {VACUUM_STAB_ORDER}   (vacuum stabilizer)")
    print(f"  orbit     = {FANO_ORBIT_SIZE}   (transitive on Fano points)")
    print(f"  Witt lines = {WITT_PAIRS}   (through vacuum axis e₇)")
    print(f"  stabRatio = {VACUUM_STAB_ORDER}/{FANO_AUT_ORDER} = 1/7 "
          f"≈ {VACUUM_STAB_ORDER/FANO_AUT_ORDER:.6f}")

    print("\nDerivation status:")
    table = build_status_table()
    for s in table:
        print(f"\n  [{s.claim_id}]  {s.name}")
        print(f"    Experimental: {s.experimental:.8g}")
        print(f"    Candidate:    {s.candidate:.8g}")
        print(f"    Gap:          {s.fractional_gap:.1%}")
        print(f"    Status:       {s.status}")
        print(f"    Note: {s.comment}")

    print("\nStrong coupling running (1-loop approximation):")
    for Q in [1.0, 2.0, 5.0, 91.2, 1000.0]:
        a = alpha_s_running_2loop(Q)
        print(f"  α_s({Q:7.1f} GeV) ≈ {a:.5f}")

    Q_star = find_alpha_s_matching_scale(ALPHA_S_CANDIDATE)
    print(f"\n  COG matching scale (α_s(Q*) = 1/7 ≈ 0.1429): Q* ≈ {Q_star:.1f} GeV")
    print(f"  (This is the energy scale at which the COG leading-order estimate")
    print(f"   matches experiment; ~{Q_star:.0f} GeV is near the top-quark / LHC scale.)")

    print("\n6π⁵ coincidence (not a COG derivation):")
    print(f"  6π⁵ = {MU_6PI5:.8f}")
    print(f"  μ   = {MU_EXP:.8f}")
    print(f"  gap = {compute_gap(MU_6PI5, MU_EXP):.2e}")

    print("\nWeinberg angle candidates:")
    print(f"  3/13          = {WEINBERG_CANDIDATE_3_13:.6f}  "
          f"(gap {compute_gap(WEINBERG_CANDIDATE_3_13, SIN2_THETA_W_EXP):.1%})")
    print(f"  dim(C)/dim(H) = {WEINBERG_CANDIDATE_NAIVE:.6f}  "
          f"(gap {compute_gap(WEINBERG_CANDIDATE_NAIVE, SIN2_THETA_W_EXP):.1%})")
    print(f"  Experiment    = {SIN2_THETA_W_EXP:.6f}")


if __name__ == "__main__":
    summary()
