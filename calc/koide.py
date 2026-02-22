"""
calc/koide.py
Phase 4.3: Koide lepton mass formula

The Koide formula
    Q = (m_e + m_μ + m_τ) / (√m_e + √m_μ + √m_τ)²  ≈  2/3
is verified from PDG 2023 charged-lepton masses.

COG geometric interpretation
──────────────────────────────
Define tick-frequency coordinates f_j = √m_j (j = 1,2,3).
The Koide ratio is then:
    Q = Σf_j² / (Σf_j)²

Q = 2/3 is equivalent to the unit vector f̂ = (f₁, f₂, f₃)/‖f‖
making exactly 45° with the democratic axis d̂ = (1,1,1)/√3
(since cos²(θ) = 1/(3Q) = 1/2 ⟹ θ = arccos(1/√2) = 45°).

In the COG framework, each f_j is the tick rate of one of the three
Witt color planes (CONVENTIONS.md §5.2).

Brannen parametrization (arXiv:0706.2534-adjacent):
    Write f_k = A + B·cos(φ + 2πk/3)  (k = 0, 1, 2).
    Z3-symmetry (equal phase spacing 2π/3) forces Σf_k = 3A
    and Σf_j·f_k (j≠k) = 3A² − (3/4)B².
    The Koide ratio becomes:
        Q = (3A² + (3/2)B²) / (3A)² = 1/3 + B²/(6A²)
    Q = 2/3  requires  B²/(6A²) = 1/3  ⟺  B = A√2.

OPEN QUESTION (KOIDE-001):
    Z3 symmetry (which SL(2,3) does supply) forces equal phase
    spacing, but does NOT force B/A = √2.  No paper in the
    literature derives the B/A = √2 constraint from a discrete group.
    The COG mechanism that selects this ratio is unknown.

    The purely algebraic identity is:
        Q = 2/3  ⟺  f₀²+f₁²+f₂² = 4(f₀f₁+f₁f₂+f₂f₀)
    This can be proved in Lean by `ring` without any real analysis.
    The open task is to show the COG update rules force exactly this
    algebraic relation — see claims/koide_exactness.yml.
"""

import math

# ──────────────────────────────────────────────────────────────────────────────
# PDG 2023 charged lepton masses (MeV/c²)
# Source: Particle Data Group 2023, https://pdg.lbl.gov
# ──────────────────────────────────────────────────────────────────────────────
M_ELECTRON: float = 0.51099895000   # ± 0.000000001 MeV
M_MUON:     float = 105.6583755     # ± 0.0000023   MeV
M_TAU:      float = 1776.86         # ± 0.12        MeV

LEPTON_MASSES: tuple[float, float, float] = (M_ELECTRON, M_MUON, M_TAU)
LEPTON_NAMES:  tuple[str, str, str]       = ("e", "μ", "τ")


# ──────────────────────────────────────────────────────────────────────────────
# Core functions
# ──────────────────────────────────────────────────────────────────────────────

def koide_ratio(masses: tuple[float, float, float]) -> float:
    """
    Compute Q = Σm / (Σ√m)² for a triple of positive masses.

    Bounds: 1/3 ≤ Q ≤ 1
      Q = 1/3  if all masses equal (Cauchy-Schwarz equality).
      Q = 2/3  Koide's prediction for charged leptons.
      Q → 1    if one mass dominates.
    """
    sum_m    = sum(masses)
    sum_sqrt = sum(math.sqrt(m) for m in masses)
    return sum_m / (sum_sqrt ** 2)


def koide_angle_degrees(masses: tuple[float, float, float]) -> float:
    """
    Angle θ between the tick-frequency unit vector f̂ = (√m₁,√m₂,√m₃)/‖f‖
    and the democratic unit vector d̂ = (1,1,1)/√3.

    cos(θ) = (Σ√m) / √(3 · Σm)

    The relationship to Q:
        cos²(θ) = (Σ√m)² / (3·Σm) = 1 / (3Q)
    So Q = 2/3 ⟺ cos²(θ) = 1/2 ⟺ θ = 45°.
    """
    sum_sqrt = sum(math.sqrt(m) for m in masses)
    sum_m    = sum(masses)
    cos_theta = sum_sqrt / math.sqrt(3.0 * sum_m)
    # Clamp to [-1, 1] to guard against tiny floating-point overflows
    theta_rad = math.acos(max(-1.0, min(1.0, cos_theta)))
    return math.degrees(theta_rad)


def koide_deviation(masses: tuple[float, float, float]) -> float:
    """Absolute deviation |Q - 2/3| from the Koide prediction."""
    return abs(koide_ratio(masses) - 2.0 / 3.0)


# ──────────────────────────────────────────────────────────────────────────────
# The "magic angle" from group theory
# ──────────────────────────────────────────────────────────────────────────────

KOIDE_ANGLE_EXACT: float = 45.0
"""
45.0°  The angle predicted by Q = 2/3.
cos²(θ) = 1/(3Q) = 1/2  ⟹  θ = arccos(1/√2) = 45°.
This is the angle between the tick-frequency unit vector and the democratic
axis (1,1,1)/√3 for a Koide-exact lepton triplet.
"""


# ──────────────────────────────────────────────────────────────────────────────
# Diagnostic summary (run as script)
# ──────────────────────────────────────────────────────────────────────────────

def summary() -> None:
    Q = koide_ratio(LEPTON_MASSES)
    θ = koide_angle_degrees(LEPTON_MASSES)
    δ = koide_deviation(LEPTON_MASSES)

    print("Koide formula — charged leptons (PDG 2023)")
    print("=" * 50)
    for name, m in zip(LEPTON_NAMES, LEPTON_MASSES):
        print(f"  m_{name:1s} = {m:>14.8f} MeV   √m_{name} = {math.sqrt(m):.8f}")
    print()
    print(f"  Q             = {Q:.10f}")
    print(f"  2/3           = {2/3:.10f}")
    print(f"  |Q - 2/3|     = {δ:.2e}")
    print()
    print(f"  θ (measured)  = {θ:.6f}°")
    print(f"  θ (predicted) = {KOIDE_ANGLE_EXACT:.6f}°  [arccos(1/√2), from Q=2/3]")
    print(f"  |Δθ|          = {abs(θ - KOIDE_ANGLE_EXACT):.4f}°")
    print()
    print("COG status (KOIDE-001):")
    print("  Q = 2/3 is equivalent to f₀²+f₁²+f₂² = 4(f₀f₁+f₁f₂+f₂f₀).")
    print("  Z3 symmetry forces equal phase spacing (2π/3) but NOT B/A = √2.")
    print("  The COG mechanism that selects B/A = √2 is an open research question.")
    print("  See claims/koide_exactness.yml.")


if __name__ == "__main__":
    summary()
