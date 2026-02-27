"""
calc/mass_ratios.py
Phase 4.3: Lepton mass ratios and COG tick-count targets

Tabulates:
  - Experimental lepton mass ratios (PDG 2023)
  - The Koide-predicted tick frequency ratios
  - COG tick-count estimates (mass ∝ tick_rate²)

In the COG framework, a particle's rest mass is proportional to the
squared tick rate: m ∝ f² where f = (# forced Tick evaluations per
causal time step).  The Koide formula constrains the three charged-lepton
tick rates to satisfy the geometric angle condition Q = 2/3.

The tick rate ratios are exactly √(m_μ/m_e), √(m_τ/m_e), etc.
If we normalise to the electron tick rate f_e = 1, the predicted rates:
    f_μ = √(m_μ / m_e)   ≈  14.42
    f_τ = √(m_τ / m_e)   ≈  58.96
must satisfy the Koide angle condition (verified by koide.py).
"""

import math
from calc.koide import LEPTON_MASSES, LEPTON_NAMES, M_ELECTRON, M_MUON, M_TAU


# ──────────────────────────────────────────────────────────────────────────────
# Mass ratios
# ──────────────────────────────────────────────────────────────────────────────

def mass_ratio(m_num: float, m_den: float) -> float:
    """Return m_num / m_den."""
    return m_num / m_den


RATIO_MU_E:  float = mass_ratio(M_MUON, M_ELECTRON)   # ≈ 206.77
RATIO_TAU_E: float = mass_ratio(M_TAU,  M_ELECTRON)   # ≈ 3477.15
RATIO_TAU_MU: float = mass_ratio(M_TAU, M_MUON)       # ≈ 16.82


# ──────────────────────────────────────────────────────────────────────────────
# Tick-rate ratios  (normalised to electron = 1)
# ──────────────────────────────────────────────────────────────────────────────

TICK_RATE_E:  float = 1.0
TICK_RATE_MU: float = math.sqrt(RATIO_MU_E)    # ≈ 14.42
TICK_RATE_TAU: float = math.sqrt(RATIO_TAU_E)  # ≈ 58.96

TICK_RATES: tuple[float, float, float] = (TICK_RATE_E, TICK_RATE_MU, TICK_RATE_TAU)


# ──────────────────────────────────────────────────────────────────────────────
# Quark masses (PDG 2023, MS-bar scheme at 2 GeV, MeV/c²)
# ──────────────────────────────────────────────────────────────────────────────
# These are included for comparison but not yet used in Lean proofs.
M_UP:      float = 2.16    # ± 0.49 MeV
M_DOWN:    float = 4.70    # ± 0.20 MeV
M_STRANGE: float = 93.4    # ± 8.6  MeV
M_CHARM:   float = 1270.0  # ± 20   MeV
M_BOTTOM:  float = 4180.0  # ± 30   MeV
M_TOP:     float = 172_690.0  # ± 300 MeV (pole mass)

QUARK_NAMES  = ("u", "d", "s", "c", "b", "t")
QUARK_MASSES = (M_UP, M_DOWN, M_STRANGE, M_CHARM, M_BOTTOM, M_TOP)


# ──────────────────────────────────────────────────────────────────────────────
# Diagnostic summary (run as script)
# ──────────────────────────────────────────────────────────────────────────────

def summary() -> None:
    print("Lepton mass ratios and COG tick targets (PDG 2023)")
    print("=" * 55)
    print()
    print("Masses:")
    for name, m in zip(LEPTON_NAMES, LEPTON_MASSES):
        print(f"  m_{name:1s} = {m:>14.8f} MeV")
    print()
    print("Mass ratios:")
    print(f"  m_μ / m_e   = {RATIO_MU_E:.6f}   (≈ 206.77)")
    print(f"  m_τ / m_e   = {RATIO_TAU_E:.4f}  (≈ 3477.15)")
    print(f"  m_τ / m_μ   = {RATIO_TAU_MU:.6f}   (≈ 16.82)")
    print()
    print("COG tick rates (normalised, f_e = 1,  mass ∝ f²):")
    print(f"  f_e  = {TICK_RATE_E:.6f}")
    print(f"  f_μ  = {TICK_RATE_MU:.6f}   (= √(m_μ/m_e))")
    print(f"  f_τ  = {TICK_RATE_TAU:.6f}   (= √(m_τ/m_e))")
    print()
    print("Koide check on tick rates:")
    sum_f2 = sum(f**2 for f in TICK_RATES)
    sum_f  = sum(TICK_RATES)
    Q_ticks = sum_f2 / sum_f**2
    print(f"  Q(f₁²,f₂²,f₃²) = {Q_ticks:.10f}")
    print(f"  2/3              = {2/3:.10f}")
    print(f"  (Should match: Q(m_e,m_μ,m_τ) = Q(f_e²,f_μ²,f_τ²))")
    print()
    print("Quark masses (PDG 2023, for future COG comparison):")
    for name, m in zip(QUARK_NAMES, QUARK_MASSES):
        print(f"  m_{name} = {m:>10.2f} MeV")


if __name__ == "__main__":
    summary()
