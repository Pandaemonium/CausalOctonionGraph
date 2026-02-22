"""
calc/test_constants.py
RFC-007: Tests for the fundamental constants derivation framework

These tests serve two purposes:
  1. Verify the Fano group data that feeds the derivations (cross-checks GAUGE-001).
  2. Document the current accuracy gap between COG candidates and experiment,
     so any unintentional regression (or improvement) is immediately visible.

A FAILING test here means either:
  (a) A bug was introduced in the group-theoretic calculations, or
  (b) A new derivation candidate was added and needs review.

A test called test_*_gap documents the CURRENT GAP.  When a derivation
is completed, replace the gap test with a precision test.
"""

import math
import pytest

from calc.fundamental_constants import (
    # Experimental values
    ALPHA_EXP,
    ALPHA_INVERSE_EXP,
    ALPHA_S_EXP,
    ALPHA_S_UNCERTAINTY,
    SIN2_THETA_W_EXP,
    SIN2_THETA_W_UNCERTAINTY,
    MU_EXP,
    MU_UNCERTAINTY,
    # Fano data
    FANO_AUT_ORDER,
    VACUUM_STAB_ORDER,
    FANO_ORBIT_SIZE,
    WITT_PAIRS,
    # Candidates
    ALPHA_S_CANDIDATE,
    ALPHA_CANDIDATE,
    WEINBERG_CANDIDATE_3_13,
    WEINBERG_CANDIDATE_NAIVE,
    MU_6PI5,
    # Helpers
    compute_gap,
    alpha_s_running_2loop,
    find_alpha_s_matching_scale,
)


# ──────────────────────────────────────────────────────────────────────────────
# Fano group data (cross-check GAUGE-001)
# ──────────────────────────────────────────────────────────────────────────────

class TestFanoGroupData:
    """
    Cross-check the group-theoretic constants from GAUGE-001.

    These are all proved by native_decide in GaugeGroup.lean;
    we verify the same numbers appear in the Python derivation.
    """

    def test_fano_aut_order(self) -> None:
        """|GL(3,2)| = 168."""
        assert FANO_AUT_ORDER == 168

    def test_vacuum_stab_order(self) -> None:
        """|SL(2,3)| = |Stab(e₇)| = 24."""
        assert VACUUM_STAB_ORDER == 24

    def test_fano_orbit_size(self) -> None:
        """Fano plane has 7 points (orbit of any point under GL(3,2) is 7)."""
        assert FANO_ORBIT_SIZE == 7

    def test_witt_lines(self) -> None:
        """Exactly 3 Witt lines pass through the vacuum axis."""
        assert WITT_PAIRS == 3

    def test_orbit_stabilizer(self) -> None:
        """Orbit-stabilizer theorem: 168 = 7 × 24."""
        assert FANO_AUT_ORDER == FANO_ORBIT_SIZE * VACUUM_STAB_ORDER

    def test_stab_ratio_exact(self) -> None:
        """Vacuum stabilizer ratio = 24/168 = 1/7 exactly."""
        ratio = VACUUM_STAB_ORDER / FANO_AUT_ORDER
        assert ratio == pytest.approx(1.0 / 7.0, rel=1e-12)


# ──────────────────────────────────────────────────────────────────────────────
# ALPHA-001: Fine-structure constant
# ──────────────────────────────────────────────────────────────────────────────

class TestAlphaFineStructure:
    """ALPHA-001: α ≈ 1/137.036."""

    def test_alpha_target_value(self) -> None:
        """Verify the CODATA 2022 experimental target."""
        assert ALPHA_EXP == pytest.approx(7.2973525693e-3, rel=1e-10)
        assert ALPHA_INVERSE_EXP == pytest.approx(137.035999, rel=1e-6)

    def test_alpha_no_candidate(self) -> None:
        """
        ALPHA-001 has no valid candidate formula yet.
        This test documents the placeholder state.
        When a real formula is found, replace with a precision test.
        """
        assert ALPHA_CANDIDATE == 0.0, (
            "ALPHA_CANDIDATE was changed from the 'no formula' placeholder (0.0). "
            "If you've identified a genuine derivation, update this test to check "
            "precision; document the formula in claims/alpha_fine_structure.yml."
        )

    def test_simple_fano_ratios_are_wrong(self) -> None:
        """
        Confirm that naive Fano ratios are NOT close to α.
        This guards against premature numerological 'derivations'.
        """
        naive_candidates = {
            "stab/total": VACUUM_STAB_ORDER / FANO_AUT_ORDER,          # 1/7 ≈ 0.143
            "1/total": 1.0 / FANO_AUT_ORDER,                           # ≈ 0.006
            "orbit/total": FANO_ORBIT_SIZE / FANO_AUT_ORDER,           # ≈ 0.042
            "1/(orbit*stab)": 1.0 / (FANO_ORBIT_SIZE * VACUUM_STAB_ORDER),  # ≈ 0.006
        }
        for name, value in naive_candidates.items():
            gap = compute_gap(value, ALPHA_EXP)
            assert gap > 0.1, (
                f"Fano ratio '{name}' = {value:.6f} is suspiciously close to "
                f"α = {ALPHA_EXP:.6f} (gap {gap:.1%}). "
                "Verify this is a genuine derivation, not numerology."
            )


# ──────────────────────────────────────────────────────────────────────────────
# STRONG-001: Strong coupling constant
# ──────────────────────────────────────────────────────────────────────────────

class TestAlphaStrong:
    """STRONG-001: α_s(M_Z) ≈ 0.1181."""

    def test_alpha_s_target_value(self) -> None:
        """Verify the PDG 2023 experimental target."""
        assert ALPHA_S_EXP == pytest.approx(0.1180, rel=1e-4)

    def test_alpha_strong_candidate_is_stab_ratio(self) -> None:
        """The leading-order candidate is 24/168 = 1/7."""
        assert ALPHA_S_CANDIDATE == pytest.approx(1.0 / 7.0, rel=1e-12)

    def test_alpha_strong_gap_is_documented(self) -> None:
        """
        The 24/168 candidate has a ~21% gap from experiment.

        This test will FAIL if the gap unexpectedly changes — which means
        either the formula was updated (good) or the experimental value
        was changed (check the PDG source).
        """
        gap = compute_gap(ALPHA_S_CANDIDATE, ALPHA_S_EXP)
        # Gap is between 15% and 30% (the ~21% documented in STRONG-001)
        assert 0.15 < gap < 0.30, (
            f"Expected gap ~21% between 1/7 ≈ 0.143 and α_s ≈ 0.118."
            f"Got {gap:.1%}.  Update claims/alpha_strong.yml if formula changed."
        )

    def test_alpha_strong_candidate_order_of_magnitude(self) -> None:
        """The candidate is in the right ballpark (not off by a factor of 10)."""
        # 0.05 < candidate < 0.30
        assert 0.05 < ALPHA_S_CANDIDATE < 0.30

    def test_alpha_s_running_is_monotone_decreasing(self) -> None:
        """α_s decreases with energy (asymptotic freedom)."""
        scales = [10.0, 91.2, 1000.0, 10000.0]
        values = [alpha_s_running_2loop(Q) for Q in scales]
        for i in range(len(values) - 1):
            assert values[i] > values[i + 1], (
                f"α_s should decrease with Q: α_s({scales[i]}) = {values[i]:.5f} "
                f"but α_s({scales[i+1]}) = {values[i+1]:.5f}"
            )

    def test_alpha_s_at_mz(self) -> None:
        """1-loop running gives α_s(M_Z) in the right order of magnitude.

        The 1-loop (leading-log) formula with Lambda_QCD = 217 MeV and Nf=5
        is a rough approximation only.  At M_Z ≈ 91 GeV it gives ~0.14,
        compared to the PDG value 0.118.  We require the result is in (0.05, 0.50)
        — correct order of magnitude, not a precision test.
        """
        a_mz = alpha_s_running_2loop(91.2)
        assert 0.05 < a_mz < 0.50, (
            f"1-loop α_s(M_Z) = {a_mz:.4f} is outside the expected range (0.05, 0.50)"
        )

    def test_alpha_s_matching_scale_is_physical(self) -> None:
        """
        Find the scale Q* where the running α_s(Q*) = 1/7 (the COG candidate).

        Since 1/7 ≈ 0.143 > α_s(M_Z) ≈ 0.118, and α_s increases as Q decreases
        (confinement), the match occurs at Q* < M_Z — somewhere between 1 GeV
        and 91 GeV (the electroweak / QCD transition region).

        If the COG formula represents α_s at the discrete Fano scale (rather
        than at M_Z), then Q* is the natural energy at which the graph
        description is valid.
        """
        Q_star = find_alpha_s_matching_scale(ALPHA_S_CANDIDATE)
        # Should be in the physical range 1 GeV to 10^6 GeV
        assert 1.0 < Q_star < 1e6, (
            f"Matching scale Q* = {Q_star:.1f} GeV is outside (1, 1e6) GeV range"
        )


# ──────────────────────────────────────────────────────────────────────────────
# WEINBERG-001: Weinberg angle
# ──────────────────────────────────────────────────────────────────────────────

class TestWeinbergAngle:
    """WEINBERG-001: sin²θ_W ≈ 0.2312."""

    def test_weinberg_target_value(self) -> None:
        """Verify the PDG 2023 experimental target."""
        assert SIN2_THETA_W_EXP == pytest.approx(0.23122, rel=1e-4)

    def test_naive_candidate_is_wrong(self) -> None:
        """dim(C)/dim(H) = 2/4 = 0.5 is NOT close to 0.231."""
        gap = compute_gap(WEINBERG_CANDIDATE_NAIVE, SIN2_THETA_W_EXP)
        assert gap > 0.5, (
            f"Naive 0.5 should be badly wrong (gap > 50%), got {gap:.1%}"
        )

    def test_3_over_13_is_numerically_suggestive(self) -> None:
        """
        3/13 ≈ 0.2308 is close to 0.2312 (gap < 0.5%).

        This test documents the numerical suggestiveness of 3/13.
        It is NOT a derivation.  If this test fails, investigate whether
        the candidate was updated or the experimental value changed.
        """
        gap = compute_gap(WEINBERG_CANDIDATE_3_13, SIN2_THETA_W_EXP)
        assert gap < 0.005, (
            f"3/13 ≈ {WEINBERG_CANDIDATE_3_13:.6f} expected within 0.5% of "
            f"sin²θ_W = {SIN2_THETA_W_EXP:.6f}. Got gap {gap:.2%}."
        )

    def test_3_over_13_not_claimed_as_derivation(self) -> None:
        """
        3/13 is documented as a numerical coincidence, not a derivation.
        The constant WEINBERG_CANDIDATE_3_13 must remain equal to 3/13
        until a proper algebraic derivation is found.
        """
        assert WEINBERG_CANDIDATE_3_13 == pytest.approx(3.0 / 13.0, rel=1e-12)


# ──────────────────────────────────────────────────────────────────────────────
# MU-001: Proton-to-electron mass ratio
# ──────────────────────────────────────────────────────────────────────────────

class TestProtonElectronRatio:
    """MU-001: μ = m_p/m_e ≈ 1836.153."""

    def test_mu_target_value(self) -> None:
        """Verify the CODATA 2022 experimental target."""
        assert MU_EXP == pytest.approx(1836.15267343, rel=1e-10)

    def test_6pi5_coincidence_is_close(self) -> None:
        """
        6π⁵ ≈ 1836.118 is within 0.003% of μ.

        This documents the famous coincidence.  It is NOT a COG derivation.
        """
        gap = compute_gap(MU_6PI5, MU_EXP)
        assert gap < 1e-4, (
            f"6π⁵ ≈ {MU_6PI5:.6f} expected within 0.01% of μ = {MU_EXP:.6f}"
        )

    def test_6pi5_is_not_exact(self) -> None:
        """6π⁵ ≠ μ exactly (it's a coincidence, not an identity)."""
        assert MU_6PI5 != pytest.approx(MU_EXP, rel=1e-8), (
            "6π⁵ accidentally equals μ to 8 significant figures?  Check the math."
        )

    def test_proton_motif_target(self) -> None:
        """The Monte Carlo simulation target is μ ≈ 1836 (integer part)."""
        assert int(MU_EXP) == 1836


# ──────────────────────────────────────────────────────────────────────────────
# KOIDE-001 cross-reference
# ──────────────────────────────────────────────────────────────────────────────

class TestKoideCrossReference:
    """Cross-reference: confirm Koide formula holds at Python level (from koide.py)."""

    def test_koide_ratio_from_constants(self) -> None:
        """The Koide ratio for PDG lepton masses ≈ 2/3 (within 2e-5)."""
        from calc.koide import koide_ratio, LEPTON_MASSES
        Q = koide_ratio(LEPTON_MASSES)
        assert abs(Q - 2.0 / 3.0) < 2e-5, (
            f"Koide ratio Q = {Q:.8f}, expected 2/3 ± 2e-5"
        )
