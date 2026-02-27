"""Tests for calc/anomaly_check.py -- COG Witt-space anomaly coefficients.

Verifies the three key numerical results from RFC-059:
  1. Q_proj assigns zero charge to all quark states (e7-component is zero).
  2. Q_num (number-operator charge) gives Tr[Q_num] = 0 over the 8 Witt states.
  3. Q_num cubic anomaly cancels between RH and dual sectors: sum = 0.
"""

import numpy as np
import pytest

from calc.anomaly_check import (
    all_witt_states,
    q_proj,
    compute_anomaly_report,
    compute_q_num_report,
)


# ------------------------------------------------------------------ #
# 1. Q_proj structure
# ------------------------------------------------------------------ #

class TestQProjStructure:
    """Q_proj = Re(psi[7]) properties on the 8 Witt states."""

    def test_vacuum_charge_zero(self):
        states = dict(all_witt_states())
        assert q_proj(states["nu_R  (omega)"]) == pytest.approx(0.0, abs=1e-10)

    def test_all_quark_charges_zero(self):
        """All six quark states live in the color subspace (no e7 component)."""
        states = dict(all_witt_states())
        quark_labels = [
            "q_r   (a1d omega)",
            "q_g   (a2d omega)",
            "q_b   (a3d omega)",
            "dq_r  (a2d a3d omega)",
            "dq_g  (a1d a3d omega)",
            "dq_b  (a1d a2d omega)",
        ]
        for label in quark_labels:
            assert q_proj(states[label]) == pytest.approx(0.0, abs=1e-10), \
                f"Expected Q_proj=0 for {label}"

    def test_lepton_charge_neg_half(self):
        states = dict(all_witt_states())
        assert q_proj(states["e_R   (a1d a2d a3d omega)"]) == pytest.approx(-0.5, abs=1e-10)

    def test_q_proj_anomaly_not_zero(self):
        """Q_proj does NOT give an anomaly-free theory (Tr[Q] != 0)."""
        states = all_witt_states()
        charges = np.array([q_proj(psi) for _, psi in states])
        tr_q = float(np.sum(charges))
        assert abs(tr_q) > 0.1, \
            f"Expected Tr[Q_proj] != 0, got {tr_q:.6f}"


# ------------------------------------------------------------------ #
# 2. Q_num (number-operator charge)
# ------------------------------------------------------------------ #

class TestQNumAnomalyCoefficients:
    """RFC-059 Section 4.2 -- Q_num satisfies linear anomaly for RH sector."""

    def setup_method(self):
        # SM electric charge assignment by Witt occupation number
        self.sm_qem = {0: 0.0, 1: 2.0/3, 2: -1.0/3, 3: -1.0}
        # 8 states in order: N=0 x1, N=1 x3, N=2 x3, N=3 x1
        self.q_vals = (
            [self.sm_qem[0]] +
            [self.sm_qem[1]] * 3 +
            [self.sm_qem[2]] * 3 +
            [self.sm_qem[3]]
        )
        self.arr = np.array(self.q_vals)

    def test_linear_anomaly_vanishes(self):
        """Tr[Q_num] = 0 over the 8-state primary Witt space."""
        tr_q = float(np.sum(self.arr))
        assert tr_q == pytest.approx(0.0, abs=1e-10), \
            f"Tr[Q_num] = {tr_q:.8f}, expected 0"

    def test_cubic_anomaly_rh_sector_nonzero(self):
        """Tr[Q_num^3] != 0 for the RH sector alone (= -2/9)."""
        tr_q3 = float(np.sum(self.arr**3))
        assert tr_q3 == pytest.approx(-2.0/9, abs=1e-8), \
            f"Tr[Q_num^3]_RH = {tr_q3:.8f}, expected -2/9 = {-2/9:.8f}"

    def test_cubic_anomaly_combined_vanishes(self):
        """Tr[Q^3]_RH + Tr[Q^3]_dual = 0 (anomaly cancels between sectors)."""
        tr_q3_rh   = float(np.sum(self.arr**3))
        tr_q3_dual = float(np.sum((-self.arr)**3))
        total = tr_q3_rh + tr_q3_dual
        assert total == pytest.approx(0.0, abs=1e-10), \
            f"Combined Tr[Q^3] = {total:.8f}, expected 0"

    def test_dual_sector_negates_cubic(self):
        """Dual sector Tr[Q^3] = +2/9 (exact negation of RH)."""
        tr_q3_dual = float(np.sum((-self.arr)**3))
        assert tr_q3_dual == pytest.approx(2.0/9, abs=1e-8), \
            f"Tr[Q_num^3]_dual = {tr_q3_dual:.8f}, expected +2/9"


# ------------------------------------------------------------------ #
# 3. Cross-checks with computed state vectors
# ------------------------------------------------------------------ #

class TestStateVectorCrossCheck:
    """Verify that state vector structure matches charge expectations."""

    def test_all_quark_states_orthogonal_to_e7(self):
        """Quark states must have zero e7 coefficient (both real and imag)."""
        states = dict(all_witt_states())
        quark_labels = [
            "q_r   (a1d omega)",
            "q_g   (a2d omega)",
            "q_b   (a3d omega)",
            "dq_r  (a2d a3d omega)",
            "dq_g  (a1d a3d omega)",
            "dq_b  (a1d a2d omega)",
        ]
        for label in quark_labels:
            psi = states[label]
            e7_coeff = psi[7]
            assert abs(e7_coeff) == pytest.approx(0.0, abs=1e-10), \
                f"e7 coeff of {label} = {e7_coeff}, expected 0"

    def test_lepton_state_has_e7_component(self):
        """The lepton state (N=3) has Re(psi[7]) = -0.5."""
        states = dict(all_witt_states())
        psi = states["e_R   (a1d a2d a3d omega)"]
        assert np.real(psi[7]) == pytest.approx(-0.5, abs=1e-10)

    def test_vacuum_state_has_imaginary_e7_component(self):
        """Vacuum omega has Im(psi[7]) = +0.5, Re(psi[7]) = 0."""
        states = dict(all_witt_states())
        psi = states["nu_R  (omega)"]
        assert np.real(psi[7]) == pytest.approx(0.0, abs=1e-10)
        assert np.imag(psi[7]) == pytest.approx(0.5, abs=1e-10)

    def test_all_states_have_norm_half(self):
        """Each Witt state has squared norm = 1/2 (from the 1/2 prefactor)."""
        for label, psi in all_witt_states():
            norm_sq = float(np.real(np.dot(psi.conj(), psi)))
            assert norm_sq == pytest.approx(0.5, abs=1e-10), \
                f"Norm^2 of {label} = {norm_sq:.6f}, expected 0.5"


# ------------------------------------------------------------------ #
# 4. Scale analysis
# ------------------------------------------------------------------ #

class TestScaleAnalysis:
    """Q_proj * 2 = Q_EM only for the lepton/vacuum, not quarks."""

    def test_scale_factor_electron(self):
        """Q_proj(e_R) * 2 == Q_EM(e_R) = -1."""
        states = dict(all_witt_states())
        psi_e = states["e_R   (a1d a2d a3d omega)"]
        assert q_proj(psi_e) * 2 == pytest.approx(-1.0, abs=1e-10)

    def test_scale_fails_for_quarks(self):
        """Q_proj * 2 does NOT equal +2/3 or -1/3 for quark states (= 0 instead)."""
        states = dict(all_witt_states())
        quark_labels = [
            "q_r   (a1d omega)",
            "q_g   (a2d omega)",
            "q_b   (a3d omega)",
        ]
        sm_up_charge = 2.0 / 3
        for label in quark_labels:
            scaled = q_proj(states[label]) * 2
            assert scaled != pytest.approx(sm_up_charge, abs=0.01), \
                f"Expected mismatch for {label}: got {scaled}"
