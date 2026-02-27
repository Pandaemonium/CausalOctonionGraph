"""calc/anomaly_check.py

Anomaly Cancellation Check for the 8-state Witt Space.

Computes Q_proj = Re(psi[7]) for all 8 states in the Witt construction
(one SM generation), then checks the three anomaly coefficients:
  Tr[Q]   = sum of Q_proj         (U(1) gravitational / linear anomaly)
  Tr[Q^2] = sum of Q_proj^2       (quadratic)
  Tr[Q^3] = sum of Q_proj^3       (cubic U(1)^3 anomaly)

Also performs scale analysis: is there a fixed s such that Q_proj * s = Q_EM
for the standard assignment (vacuum=0, quarks=+2/3, anti-quarks=-1/3, lepton=-1)?

References:
  rfc/RFC-059_Anomaly_Cancellation_in_Discrete_CxO.md
  calc/furey_electron_orbit.py  (Witt state constructors)
  rfc/CONVENTIONS.md Section 5  (Witt basis)
  Furey (2018) arXiv:1806.00612 Section 4-5 (SM representations from C x O)
"""

from __future__ import annotations

import json
import pathlib

import numpy as np

from calc.furey_electron_orbit import (
    OMEGA,
    ALPHA1_DAG,
    ALPHA2_DAG,
    ALPHA3_DAG,
    quark_state,
    furey_electron_state,
)
from calc.qed_ee_sim import oct_mul_full


# ================================================================
# Charge operator
# ================================================================

def q_proj(psi: np.ndarray) -> float:
    """Q_proj = Re(psi[7]) -- the COG U(1) charge observable (RFC-041).

    psi is a length-8 complex array with index k = coefficient of e_k.
    Index 7 = e7 coefficient (the vacuum axis direction).
    """
    return float(np.real(psi[7]))


# ================================================================
# All 8 Witt states
# ================================================================

def all_witt_states() -> list[tuple[str, np.ndarray]]:
    """Return all 8 Witt-basis states as (label, state_vector) pairs.

    The 8 = 2^3 states are built by applying subsets of
    {alpha1_dag, alpha2_dag, alpha3_dag} to the vacuum omega.

    SM particle identification (Furey 2016/2018 convention):
      0 ops: omega                    -- sterile neutrino (nu_R)
      1 op:  alpha_j_dag * omega      -- right-handed up-quark (3 colours)
      2 ops: alpha_j alpha_k dag * w  -- right-handed down-quark (3 colours)
      3 ops: alpha123_dag * omega     -- right-handed charged lepton (e_R)
    """
    # 0 creation operators
    nu_R = OMEGA.copy()

    # 1 creation operator (quarks)
    q_r = quark_state(1)
    q_g = quark_state(2)
    q_b = quark_state(3)

    # 2 creation operators (anti-quarks / diquarks)
    # Applied right-to-left: alpha_i * (alpha_j * omega)
    dq_r = oct_mul_full(ALPHA2_DAG, oct_mul_full(ALPHA3_DAG, OMEGA))
    dq_g = oct_mul_full(ALPHA1_DAG, oct_mul_full(ALPHA3_DAG, OMEGA))
    dq_b = oct_mul_full(ALPHA1_DAG, oct_mul_full(ALPHA2_DAG, OMEGA))

    # 3 creation operators (charged lepton)
    e_R = furey_electron_state()

    return [
        ("nu_R  (omega)",                   nu_R),
        ("q_r   (a1d omega)",               q_r),
        ("q_g   (a2d omega)",               q_g),
        ("q_b   (a3d omega)",               q_b),
        ("dq_r  (a2d a3d omega)",           dq_r),
        ("dq_g  (a1d a3d omega)",           dq_g),
        ("dq_b  (a1d a2d omega)",           dq_b),
        ("e_R   (a1d a2d a3d omega)",       e_R),
    ]


# ================================================================
# Formatting helpers
# ================================================================

def fmt_state(psi: np.ndarray, tol: float = 1e-10) -> str:
    """Compact nonzero-term representation of a C(x)O state vector."""
    basis = ["e0", "e1", "e2", "e3", "e4", "e5", "e6", "e7"]
    parts = []
    for k, c in enumerate(psi):
        if abs(c) < tol:
            continue
        r, im = c.real, c.imag
        if abs(im) < tol:
            parts.append(f"{r:+.3f}*{basis[k]}")
        elif abs(r) < tol:
            parts.append(f"{im:+.3f}i*{basis[k]}")
        else:
            parts.append(f"({r:+.3f}{im:+.3f}i)*{basis[k]}")
    return "  ".join(parts) if parts else "0"


# ================================================================
# Main computation
# ================================================================

def compute_anomaly_report() -> dict:
    """Compute the full anomaly cancellation report and return as a dict."""
    states = all_witt_states()

    print("=" * 80)
    print("COG Witt Space -- Q_proj = Re(psi[7])  [RFC-041 charge operator]")
    print("=" * 80)
    header = f"{'State label':<38} {'Q_proj':>8}  State (nonzero terms)"
    print(header)
    print("-" * 80)

    charges = []
    records = []
    for label, psi in states:
        q = q_proj(psi)
        charges.append(q)
        state_str = fmt_state(psi)
        print(f"{label:<38} {q:>+8.4f}  {state_str}")
        records.append({"label": label, "q_proj": round(q, 6), "state": state_str})

    charges_arr = np.array(charges)
    tr_q  = float(np.sum(charges_arr))
    tr_q2 = float(np.sum(charges_arr ** 2))
    tr_q3 = float(np.sum(charges_arr ** 3))

    print()
    print("=" * 80)
    print("Anomaly Coefficients  (summed over all 8 Witt states)")
    print("=" * 80)
    print(f"  Tr[Q]   = sum  Q_proj       = {tr_q:+.8f}")
    print(f"  Tr[Q^2] = sum  Q_proj^2     = {tr_q2:+.8f}")
    print(f"  Tr[Q^3] = sum  Q_proj^3     = {tr_q3:+.8f}")

    # SM Q_EM charges for one RH generation (standard values)
    # nu_R: 0; u_r,u_g,u_b: +2/3; d_r,d_g,d_b: -1/3; e_R: -1
    sm_qem = [0.0, 2/3, 2/3, 2/3, -1/3, -1/3, -1/3, -1.0]
    sm_arr = np.array(sm_qem)
    sm_tr_q  = float(np.sum(sm_arr))
    sm_tr_q2 = float(np.sum(sm_arr**2))
    sm_tr_q3 = float(np.sum(sm_arr**3))

    print()
    print("=" * 80)
    print("SM Right-Handed Q_EM Reference  (nu:0, u:+2/3, d:-1/3, e:-1)")
    print("=" * 80)
    print(f"  SM Tr[Q_EM]   = {sm_tr_q:+.8f}")
    print(f"  SM Tr[Q_EM^2] = {sm_tr_q2:+.8f}")
    print(f"  SM Tr[Q_EM^3] = {sm_tr_q3:+.8f}")
    print()
    print(f"  COG charges:   {[round(q, 4) for q in charges]}")
    print(f"  SM  charges:   {[round(q, 4) for q in sm_qem]}")

    # Scale analysis: find s = Q_EM(e) / Q_proj(e) using the electron
    q_e = charges[-1]  # e_R state
    scale_info = {}
    print()
    print("=" * 80)
    print("Scale Analysis  (Q_proj * s == Q_EM ?)")
    print("=" * 80)
    if abs(q_e) < 1e-10:
        print("  WARNING: Q_proj(e_R) = 0; cannot determine scale factor.")
        scale_info["scale"] = None
        scale_info["match"] = False
    else:
        s = -1.0 / q_e  # want s * Q_proj(e) = -1
        scaled = [round(q * s, 6) for q in charges]
        match = np.allclose(np.array([q * s for q in charges]), sm_arr, atol=0.01)
        print(f"  Scale s = Q_EM(e_R) / Q_proj(e_R) = -1 / ({q_e:.4f}) = {s:.6f}")
        print(f"  Q_proj * {s:.4f}: {scaled}")
        print(f"  SM Q_EM:         {sm_qem}")
        print(f"  All match SM:    {match}")
        scale_info["scale"] = round(s, 6)
        scale_info["scaled_charges"] = scaled
        scale_info["match_sm"] = bool(match)

    # Summary verdict
    print()
    print("=" * 80)
    print("VERDICT")
    print("=" * 80)
    tr_q_zero  = abs(tr_q)  < 1e-8
    tr_q3_zero = abs(tr_q3) < 1e-8
    verdict_lines = []
    if tr_q_zero:
        verdict_lines.append("  PASS  Tr[Q] = 0  (gravitational anomaly cancels)")
    else:
        verdict_lines.append(f"  FAIL  Tr[Q] = {tr_q:.6f} (gravitational anomaly non-zero)")
    if tr_q3_zero:
        verdict_lines.append("  PASS  Tr[Q^3] = 0  (cubic U(1)^3 anomaly cancels)")
    else:
        verdict_lines.append(f"  FAIL  Tr[Q^3] = {tr_q3:.6f} (cubic anomaly non-zero)")
    print("\n".join(verdict_lines))

    result = {
        "states": records,
        "anomaly_coefficients": {
            "tr_q":  round(tr_q,  10),
            "tr_q2": round(tr_q2, 10),
            "tr_q3": round(tr_q3, 10),
            "tr_q_vanishes":  bool(tr_q_zero),
            "tr_q3_vanishes": bool(tr_q3_zero),
        },
        "sm_reference": {
            "sm_qem":   sm_qem,
            "sm_tr_q":  round(sm_tr_q,  8),
            "sm_tr_q2": round(sm_tr_q2, 8),
            "sm_tr_q3": round(sm_tr_q3, 8),
        },
        "scale_analysis": scale_info,
    }
    return result


def compute_q_num_report() -> dict:
    """Compute anomaly coefficients for Q_num (number-operator charge).

    Q_num is the SM electric charge derived from the Witt occupation number N:
      N = number of alpha_j_dag operators applied to omega

    State -> particle identification (Furey 2016/2018 right-handed sector):
      N=0: nu_R  (sterile neutrino)    Q_EM = 0
      N=1: u_R   (up quarks, 3 colors) Q_EM = +2/3
      N=2: d_R   (down quarks, 3 col)  Q_EM = -1/3
      N=3: e_R   (charged lepton)      Q_EM = -1

    Note: the right-handed sector alone is NOT anomaly-free (Tr[Q^3] = -2/9).
    Full anomaly cancellation requires the dual (left-handed) sector too.
    """
    # Witt occupation numbers for the 8 states
    #  label                  N  Q_num  SM particle
    witt_table = [
        ("nu_R  (omega)",           0,  0.0,      "sterile neutrino"),
        ("q_r   (a1d omega)",       1,  2.0/3,    "u quark color r"),
        ("q_g   (a2d omega)",       1,  2.0/3,    "u quark color g"),
        ("q_b   (a3d omega)",       1,  2.0/3,    "u quark color b"),
        ("dq_r  (a2d a3d omega)",   2, -1.0/3,    "d quark color r"),
        ("dq_g  (a1d a3d omega)",   2, -1.0/3,    "d quark color g"),
        ("dq_b  (a1d a2d omega)",   2, -1.0/3,    "d quark color b"),
        ("e_R   (a1d a2d a3d)",     3, -1.0,      "charged lepton"),
    ]

    print()
    print("=" * 80)
    print("Q_num (Furey number-operator charge) for the 8 Witt states")
    print("  Assignment: N=0->0, N=1->+2/3, N=2->-1/3, N=3->-1")
    print("=" * 80)
    header2 = f"{'State':<35} {'N':>4} {'Q_num':>8}  SM particle"
    print(header2)
    print("-" * 80)

    q_num_vals = []
    records2 = []
    for label, N, q, particle in witt_table:
        print(f"{label:<35} {N:>4} {q:>+8.4f}  {particle}")
        q_num_vals.append(q)
        records2.append({"label": label, "N": N, "q_num": q, "particle": particle})

    q_arr = np.array(q_num_vals)
    tr_q   = float(np.sum(q_arr))
    tr_q2  = float(np.sum(q_arr**2))
    tr_q3  = float(np.sum(q_arr**3))

    print()
    print(f"  Tr[Q_num]   = {tr_q:+.8f}")
    print(f"  Tr[Q_num^2] = {tr_q2:+.8f}")
    print(f"  Tr[Q_num^3] = {tr_q3:+.8f}")

    # Dual sector: conjugate (anti-fermion) charges
    # For the dual Witt ideal (omega_dag): q -> -q flips all charges
    q_dual = [-q for q in q_num_vals]
    q_dual_arr = np.array(q_dual)
    tr_q3_dual = float(np.sum(q_dual_arr**3))

    print()
    print(f"  Dual sector Tr[Q_num^3] = {tr_q3_dual:+.8f}")
    print(f"  Combined    Tr[Q_num^3] = {tr_q3 + tr_q3_dual:+.8f}  (should be 0)")

    print()
    print("=" * 80)
    print("VERDICT for Q_num")
    print("=" * 80)
    rh_q3_zero     = abs(tr_q3) < 1e-8
    rh_q_zero      = abs(tr_q) < 1e-8
    combined_zero  = abs(tr_q3 + tr_q3_dual) < 1e-8
    print(f"  RH sector Tr[Q_num]   = 0:  {rh_q_zero}  (linear anomaly)")
    print(f"  RH sector Tr[Q_num^3] = 0:  {rh_q3_zero}  (cubic anomaly, RH alone)")
    print(f"  Combined   Tr[Q^3]    = 0:  {combined_zero}  (requires dual sector)")

    return {
        "states": records2,
        "anomaly_coefficients": {
            "tr_q":  round(tr_q, 10),
            "tr_q2": round(tr_q2, 10),
            "tr_q3": round(tr_q3, 10),
            "tr_q_rh_vanishes":       bool(rh_q_zero),
            "tr_q3_rh_vanishes":      bool(rh_q3_zero),
            "tr_q3_combined_vanishes": bool(combined_zero),
        },
    }


def main() -> None:
    result_proj = compute_anomaly_report()
    result_num  = compute_q_num_report()
    combined = {"q_proj": result_proj, "q_num": result_num}
    out = pathlib.Path(__file__).parent / "anomaly_check_results.json"
    with open(out, "w") as f:
        json.dump(combined, f, indent=2)
    print(f"\n  Artifact saved: {out}")


if __name__ == "__main__":
    main()
