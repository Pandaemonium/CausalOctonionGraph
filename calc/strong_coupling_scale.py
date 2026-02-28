"""
strong_coupling_scale.py  -- Attack Vector 1: Inverse Beta Scale Calibrator
Find the energy scale mu where alpha_s(mu) = 1/7 (the COG Fano proxy).

Uses the standard 3-loop QCD beta function with n_f flavor thresholds:
  m_b = 4.18 GeV (MS-bar), m_c = 1.28 GeV (MS-bar), m_t = 172.9 GeV
Starting point: alpha_s(M_Z) = 0.1179 at M_Z = 91.1876 GeV (PDG 2024)
Target:         alpha_s(mu)  = 1/7   ~ 0.14286

Run pytest calc/test_strong_coupling_scale.py to verify.
"""

import numpy as np
from scipy.integrate import solve_ivp

# ── Physical constants (PDG 2024) ─────────────────────────────────────────────
ALPHA_S_MZ = 0.1179     # alpha_s at M_Z in MS-bar, n_f=5 scheme
MZ         = 91.1876    # GeV
M_TOP      = 172.9      # GeV  (approx; n_f threshold)
M_BOT      = 4.18       # GeV  (MS-bar mass)
M_CHM      = 1.28       # GeV  (MS-bar mass)

# ── Beta function coefficients ─────────────────────────────────────────────────
def _beta_coeffs(nf):
    """3-loop beta function coefficients for n_f active flavors."""
    b0 = 11.0 - 2.0 * nf / 3.0
    b1 = 102.0 - 38.0 * nf / 3.0
    b2 = 2857.0 / 2.0 - 5033.0 * nf / 18.0 + 325.0 * nf ** 2 / 54.0
    return b0, b1, b2


def _dalpha_dt(alpha_s, nf):
    """
    d(alpha_s) / d(t)  where t = ln(mu / 1 GeV)
    3-loop: dalpha/dt = -(b0/(2pi)) alpha^2 [1 + (b1/(4pi b0)) alpha + (b2/(16pi^2 b0)) alpha^2]
    """
    pi = np.pi
    b0, b1, b2 = _beta_coeffs(nf)
    a = alpha_s
    return -(b0 / (2 * pi)) * a ** 2 * (
        1.0
        + (b1 / (4.0 * pi * b0)) * a
        + (b2 / (16.0 * pi ** 2 * b0)) * a ** 2
    )


def run_alpha_s_down(mu_start, alpha_start, mu_end, nf=5, n_steps=50000):
    """
    Integrate alpha_s from mu_start down to mu_end using n_f active flavors.
    Returns (alpha_s at mu_end, array of (mu, alpha_s) pairs).
    """
    t_start = np.log(mu_start)
    t_end   = np.log(mu_end)
    t_eval  = np.linspace(t_start, t_end, n_steps)

    sol = solve_ivp(
        lambda t, y: [_dalpha_dt(y[0], nf)],
        (t_start, t_end),
        [alpha_start],
        t_eval=t_eval,
        method="RK45",
        rtol=1e-10,
        atol=1e-12,
    )
    mus    = np.exp(sol.t)
    alphas = sol.y[0]
    return alphas[-1], list(zip(mus, alphas))


def find_cog_scale(target=1.0 / 7.0, verbose=True):
    """
    Find the energy scale mu_COG where alpha_s(mu_COG) = target.

    Integration route (top-down, matching at thresholds):
      M_Z (n_f=5)  ->  M_BOT (n_f=5)  ->  M_BOT (n_f=4)  ->  M_CHM (n_f=4)
      If target not reached at M_CHM, continue with n_f=3.

    Returns: dict with mu_COG, alpha_s_check, nf_at_scale, and diagnostic info.
    """
    # Step 1: M_Z -> M_BOT (n_f = 5)
    alpha_bot, trace5 = run_alpha_s_down(MZ, ALPHA_S_MZ, M_BOT, nf=5)

    def _interpolate_crossing(alpha_arr, mu_arr, tgt):
        """Find mu where ascending alpha_arr first reaches tgt; return mu or None."""
        # alpha_arr is ascending (low mu at end); find first index >= tgt
        idx = np.searchsorted(alpha_arr, tgt)
        if idx == 0 or idx >= len(alpha_arr):
            return None
        a0, a1 = alpha_arr[idx - 1], alpha_arr[idx]
        m0, m1 = mu_arr[idx - 1], mu_arr[idx]
        frac    = (tgt - a0) / (a1 - a0)
        return float(np.exp(np.log(m0) + frac * (np.log(m1) - np.log(m0))))

    # Check if target is in the n_f=5 window (M_Z -> M_BOT)
    alpha5_arr = np.array([a for _, a in trace5])
    mu5_arr    = np.array([m for m, _ in trace5])
    mu_cross   = _interpolate_crossing(alpha5_arr, mu5_arr, target)
    if mu_cross is not None:
        nf_at = 5
    else:
        # Step 2: M_BOT -> M_CHM (n_f=4)
        alpha_chm, trace4 = run_alpha_s_down(M_BOT, alpha_bot, M_CHM, nf=4)
        alpha4_arr = np.array([a for _, a in trace4])
        mu4_arr    = np.array([m for m, _ in trace4])
        mu_cross   = _interpolate_crossing(alpha4_arr, mu4_arr, target)
        if mu_cross is not None:
            nf_at = 4
        else:
            # Step 3: below charm (n_f=3) -- perturbation theory unreliable here
            alpha_end, trace3 = run_alpha_s_down(M_CHM, alpha_chm, 0.5, nf=3)
            alpha3_arr = np.array([a for _, a in trace3])
            mu3_arr    = np.array([m for m, _ in trace3])
            mu_cross   = _interpolate_crossing(alpha3_arr, mu3_arr, target)
            if mu_cross is not None:
                nf_at = 3
            else:
                return {"mu_COG": None, "error": "target not reached above 0.5 GeV"}

    # Verify: re-run from M_Z to mu_cross and check
    # Determine n_f for verification run
    if mu_cross > M_BOT:
        alpha_verify, _ = run_alpha_s_down(MZ, ALPHA_S_MZ, mu_cross, nf=5)
    elif mu_cross > M_CHM:
        alpha_at_bot, _ = run_alpha_s_down(MZ, ALPHA_S_MZ, M_BOT, nf=5)
        alpha_verify, _ = run_alpha_s_down(M_BOT, alpha_at_bot, mu_cross, nf=4)
    else:
        alpha_at_bot, _ = run_alpha_s_down(MZ, ALPHA_S_MZ, M_BOT, nf=5)
        alpha_at_chm, _ = run_alpha_s_down(M_BOT, alpha_at_bot, M_CHM, nf=4)
        alpha_verify, _ = run_alpha_s_down(M_CHM, alpha_at_chm, mu_cross, nf=3)

    # Known reference points for sanity check
    known_thresholds = {
        "3 m_b": 3 * M_BOT,
        "2 m_b": 2 * M_BOT,
        "m_b":   M_BOT,
        "sqrt(m_b * m_t)": np.sqrt(M_BOT * M_TOP),
        "m_b + m_c": M_BOT + M_CHM,
        "Upsilon(1S)": 9.46,  # GeV
        "J/psi": 3.097,       # GeV
    }

    result = {
        "mu_COG":        round(float(mu_cross), 4),
        "alpha_s_check": round(float(alpha_verify), 6),
        "target":        round(target, 6),
        "residual":      round(abs(float(alpha_verify) - target), 8),
        "nf_at_scale":   nf_at,
        "nearby_thresholds": {
            k: round(abs(mu_cross - v) / v * 100, 2)
            for k, v in known_thresholds.items()
        },
    }

    if verbose:
        print(f"\n=== COG Native Scale Search: alpha_s = {target:.6f} = 1/7 ===")
        print(f"  Starting: alpha_s(M_Z={MZ} GeV) = {ALPHA_S_MZ}")
        print(f"  Result:   alpha_s({result['mu_COG']:.3f} GeV) = {result['alpha_s_check']:.6f}")
        print(f"  Residual: {result['residual']:.2e}")
        print(f"  Active n_f at this scale: {nf_at}")
        print()
        print("  Distance from known thresholds (% deviation):")
        for thresh, pct in result["nearby_thresholds"].items():
            marker = " <-- closest" if pct == min(result["nearby_thresholds"].values()) else ""
            print(f"    {thresh:25s}: {pct:6.2f}%{marker}")
        print()
        mq = result["mu_COG"]
        print(f"  Interpretation: mu_COG = {mq:.3f} GeV")
        if mq > M_BOT:
            print(f"  -> Above m_b = {M_BOT} GeV (n_f=5 window)")
        else:
            print(f"  -> Below m_b = {M_BOT} GeV (n_f=4 window, pQCD still valid)")
        print()
        # ── COG-specific scale coincidences ───────────────────────────────────
        print("  COG-specific scale coincidences:")
        coincidences = {
            "M_Z / sqrt(10)":      MZ / np.sqrt(10),
            "m_t / 6":             M_TOP / 6,
            "sqrt(m_b * m_t)":     np.sqrt(M_BOT * M_TOP),
            "3 * m_b":             3 * M_BOT,
            "m_Z / pi":            MZ / np.pi,
        }
        for label, val in sorted(coincidences.items(), key=lambda x: abs(x[1] - mq)):
            dev = (mq - val) / val * 100
            print(f"    {label:25s}: {val:.4f} GeV  (dev {dev:+.3f}%)")
        # Summary flag for best coincidence
        best_label, best_val = min(coincidences.items(), key=lambda x: abs(x[1] - mq))
        print(f"\n  ** Best coincidence: mu_COG = {best_label} ({best_val:.4f} GeV,"
              f" deviation {(mq-best_val)/best_val*100:+.3f}%) **")

    return result


if __name__ == "__main__":
    result = find_cog_scale(target=1.0 / 7.0, verbose=True)
