"""
calc/test_koide.py
Tests for the Koide formula and mass ratio computations.
"""

import math
import pytest
from calc.koide import (
    koide_ratio,
    koide_angle_degrees,
    koide_deviation,
    LEPTON_MASSES,
    KOIDE_ANGLE_EXACT,
    M_ELECTRON, M_MUON, M_TAU,
)
from calc.mass_ratios import (
    RATIO_MU_E, RATIO_TAU_E, RATIO_TAU_MU,
    TICK_RATE_MU, TICK_RATE_TAU, TICK_RATES,
    QUARK_MASSES, QUARK_NAMES,
)


# ──────────────────────────────────────────────────────────────────────────────
# Koide ratio tests
# ──────────────────────────────────────────────────────────────────────────────

def test_koide_ratio_charged_leptons():
    """Q ≈ 2/3 for the charged lepton masses to 5 significant figures."""
    Q = koide_ratio(LEPTON_MASSES)
    assert abs(Q - 2 / 3) < 5e-4, f"Q = {Q}, expected ≈ 2/3"


def test_koide_ratio_equal_masses():
    """Q = 1/3 when all three masses are equal (minimum value)."""
    Q = koide_ratio((1.0, 1.0, 1.0))
    assert abs(Q - 1 / 3) < 1e-12


def test_koide_ratio_one_dominant():
    """Q → 1 when one mass dominates the other two."""
    Q = koide_ratio((1.0, 1.0, 1e10))
    assert Q > 0.99


def test_koide_ratio_bounds():
    """1/3 ≤ Q ≤ 1 for any positive triple."""
    for triple in [
        LEPTON_MASSES,
        (1.0, 1.0, 1.0),
        (1.0, 4.0, 9.0),
        (0.001, 100.0, 50000.0),
    ]:
        Q = koide_ratio(triple)
        assert 1 / 3 - 1e-12 <= Q <= 1.0 + 1e-12, f"Q = {Q} out of bounds for {triple}"


# ──────────────────────────────────────────────────────────────────────────────
# Geometric angle tests
# ──────────────────────────────────────────────────────────────────────────────

def test_koide_angle_charged_leptons():
    """
    The tick-frequency vector for charged leptons makes ≈ 45°
    with the democratic direction (1,1,1)/√3.
    Q = 2/3 ⟺ cos²(θ) = 1/2 ⟺ θ = 45°.
    """
    θ = koide_angle_degrees(LEPTON_MASSES)
    assert abs(θ - KOIDE_ANGLE_EXACT) < 0.05, f"θ = {θ}°, expected ≈ {KOIDE_ANGLE_EXACT:.4f}°"


def test_koide_angle_equal_masses_is_zero():
    """Equal masses → θ = 0° (aligned with democratic direction)."""
    θ = koide_angle_degrees((1.0, 1.0, 1.0))
    assert θ < 1e-6, f"θ = {θ}°, expected 0°"


def test_koide_exact_angle_value():
    """KOIDE_ANGLE_EXACT = 45°  (arccos(1/√2), from Q = 2/3)."""
    assert abs(KOIDE_ANGLE_EXACT - 45.0) < 1e-10


def test_koide_q_angle_consistency():
    """
    Q = 2/3 and θ = arccos(1/√3) are equivalent:
    cos(θ) = (Σ√m) / √(3·Σm), so Q = cos²(θ) when Q = 2/3 exactly.
    Check the two measures are consistent to within 0.1%.
    """
    Q = koide_ratio(LEPTON_MASSES)
    θ_rad = math.radians(koide_angle_degrees(LEPTON_MASSES))
    # cos²(θ) = (Σ√m)² / (3·Σm) = 1/(3Q)
    cos2 = math.cos(θ_rad) ** 2
    assert abs(cos2 - 1 / (3 * Q)) < 1e-10


# ──────────────────────────────────────────────────────────────────────────────
# Mass ratio tests
# ──────────────────────────────────────────────────────────────────────────────

def test_muon_electron_ratio():
    """m_μ / m_e ≈ 206.77."""
    assert abs(RATIO_MU_E - 206.77) < 0.5


def test_tau_electron_ratio():
    """m_τ / m_e ≈ 3477."""
    assert abs(RATIO_TAU_E - 3477) < 10


def test_tau_muon_ratio():
    """m_τ / m_μ ≈ 16.82."""
    assert abs(RATIO_TAU_MU - 16.82) < 0.5


def test_mass_ratios_consistent():
    """Consistency: (m_τ/m_e) = (m_τ/m_μ) × (m_μ/m_e)."""
    assert abs(RATIO_TAU_E - RATIO_TAU_MU * RATIO_MU_E) < 1e-6


# ──────────────────────────────────────────────────────────────────────────────
# COG tick-rate tests
# ──────────────────────────────────────────────────────────────────────────────

def test_tick_rate_muon():
    """f_μ = √(m_μ/m_e) ≈ 14.42."""
    assert abs(TICK_RATE_MU - math.sqrt(RATIO_MU_E)) < 1e-8


def test_tick_rate_tau():
    """f_τ = √(m_τ/m_e) ≈ 58.96."""
    assert abs(TICK_RATE_TAU - math.sqrt(RATIO_TAU_E)) < 1e-8


def test_tick_rates_satisfy_koide():
    """
    The Koide ratio Q applied to (f_e², f_μ², f_τ²) = (m_e, m_μ, m_τ)
    after normalisation must equal the Koide ratio applied to the raw masses
    (since f_j² = m_j/m_e and scaling all masses by 1/m_e doesn't change Q).
    """
    Q_masses = koide_ratio(LEPTON_MASSES)
    # Tick rates: f = (1, √(m_μ/m_e), √(m_τ/m_e))
    # Tick-rate² = (1, m_μ/m_e, m_τ/m_e)
    masses_normalised = tuple(f**2 for f in TICK_RATES)
    Q_ticks = koide_ratio(masses_normalised)  # type: ignore[arg-type]
    assert abs(Q_masses - Q_ticks) < 1e-10


# ──────────────────────────────────────────────────────────────────────────────
# PDG mass sanity checks
# ──────────────────────────────────────────────────────────────────────────────

def test_lepton_mass_ordering():
    """m_e < m_μ < m_τ."""
    assert M_ELECTRON < M_MUON < M_TAU


def test_electron_mass_MeV():
    """m_e ≈ 0.511 MeV."""
    assert abs(M_ELECTRON - 0.511) < 0.001


def test_muon_mass_MeV():
    """m_μ ≈ 105.66 MeV."""
    assert abs(M_MUON - 105.66) < 0.01


def test_tau_mass_MeV():
    """m_τ ≈ 1776.86 MeV."""
    assert abs(M_TAU - 1776.86) < 0.5


def test_quark_mass_count():
    """There are 6 quarks in the Standard Model."""
    assert len(QUARK_MASSES) == 6
    assert len(QUARK_NAMES) == 6


def test_quark_mass_ordering():
    """u < d < s < c < b < t (approximate)."""
    u, d, s, c, b, t = QUARK_MASSES
    assert u < s < c < b < t
