"""
Tests for strong_coupling_scale.py (Attack Vector 1 — Inverse Beta Scale Calibrator)
Run: pytest calc/test_strong_coupling_scale.py -v
"""
import numpy as np
import pytest
from calc.strong_coupling_scale import find_cog_scale, run_alpha_s_down, MZ, ALPHA_S_MZ, M_BOT


def test_integration_direction_alpha_increases_downward():
    """alpha_s should increase as energy decreases (asymptotic freedom)."""
    alpha_low, _ = run_alpha_s_down(MZ, ALPHA_S_MZ, 10.0, nf=5)
    assert alpha_low > ALPHA_S_MZ, (
        f"alpha_s({10:.0f} GeV)={alpha_low:.4f} should be > alpha_s(M_Z)={ALPHA_S_MZ}"
    )


def test_alpha_s_near_mZ_stable():
    """Integrating a tiny step from M_Z should change alpha_s by < 0.001."""
    alpha_end, _ = run_alpha_s_down(MZ, ALPHA_S_MZ, MZ * 0.999, nf=5, n_steps=100)
    assert abs(alpha_end - ALPHA_S_MZ) < 0.001


def test_alpha_s_at_mbot_in_range():
    """alpha_s(m_b) from 3-loop RGE should be ~ 0.22-0.24."""
    alpha_bot, _ = run_alpha_s_down(MZ, ALPHA_S_MZ, M_BOT, nf=5)
    assert 0.20 < alpha_bot < 0.28, f"alpha_s(m_b) = {alpha_bot:.4f} out of expected range"


def test_cog_scale_1_over_7_found():
    """alpha_s = 1/7 should be found at a scale between M_BOT and M_Z."""
    result = find_cog_scale(target=1.0 / 7.0, verbose=False)
    assert result.get("mu_COG") is not None, "Scale not found"
    mu = result["mu_COG"]
    assert M_BOT < mu < MZ, f"mu_COG={mu:.2f} GeV not in expected range [{M_BOT},{MZ}]"


def test_cog_scale_residual_tight():
    """The integrated alpha_s at mu_COG should match target to < 1e-4."""
    result = find_cog_scale(target=1.0 / 7.0, verbose=False)
    assert result["residual"] < 1e-4, f"Residual {result['residual']:.2e} too large"


def test_cog_scale_nf_is_5():
    """At mu_COG ~ 29 GeV, we should be in the n_f=5 window."""
    result = find_cog_scale(target=1.0 / 7.0, verbose=False)
    assert result["nf_at_scale"] == 5, f"Expected n_f=5, got {result['nf_at_scale']}"


def test_cog_scale_coincidence_mz_sqrt10():
    """
    Key result: mu_COG = alpha_s^{-1}(1/7) should match M_Z / sqrt(10) within 0.1%.
    This is the Fano-to-EW scale bridge identity.
    """
    result = find_cog_scale(target=1.0 / 7.0, verbose=False)
    mu_cog = result["mu_COG"]
    mu_ref = MZ / np.sqrt(10)
    deviation_pct = abs(mu_cog - mu_ref) / mu_ref * 100
    assert deviation_pct < 0.1, (
        f"mu_COG={mu_cog:.4f} GeV deviates {deviation_pct:.3f}% from M_Z/sqrt(10)={mu_ref:.4f} GeV"
    )


def test_cog_scale_coincidence_mt_over_6():
    """
    Secondary coincidence: mu_COG ~ m_top / 6 within 0.1%.
    """
    from calc.strong_coupling_scale import M_TOP
    result = find_cog_scale(target=1.0 / 7.0, verbose=False)
    mu_cog = result["mu_COG"]
    mu_ref = M_TOP / 6.0
    deviation_pct = abs(mu_cog - mu_ref) / mu_ref * 100
    assert deviation_pct < 0.1, (
        f"mu_COG={mu_cog:.4f} GeV deviates {deviation_pct:.3f}% from m_t/6={mu_ref:.4f} GeV"
    )


def test_beta_function_correct_sign():
    """The beta function must be negative (alpha_s decreases with increasing energy)."""
    from calc.strong_coupling_scale import _dalpha_dt
    for alpha in [0.1, 0.15, 0.2, 0.3]:
        for nf in [3, 4, 5]:
            assert _dalpha_dt(alpha, nf) < 0, (
                f"beta(alpha={alpha}, nf={nf}) should be < 0 (asymptotic freedom)"
            )


def test_alpha_1_over_8_higher_energy_than_1_over_7():
    """alpha_s = 1/8 < 1/7, so the scale where alpha_s = 1/8 is HIGHER than where it is 1/7."""
    r7 = find_cog_scale(target=1.0 / 7.0, verbose=False)
    r8 = find_cog_scale(target=1.0 / 8.0, verbose=False)
    assert r8["mu_COG"] > r7["mu_COG"], (
        f"mu(1/8)={r8['mu_COG']:.2f} should be > mu(1/7)={r7['mu_COG']:.2f}"
    )
