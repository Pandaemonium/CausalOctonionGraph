"""calc/test_furey_electron_orbit.py

25 tests for the Full Furey Electron State and Universal C_e = 4 Theorem.

Key findings under test:
  1. Universal C_e = 4: L_{e7}^2 = -id (left-alternative law) => period 4 for ALL states.
  2. Witt basis: alpha_j annihilates omega; alpha_j_dag * omega = alpha_j_dag.
  3. Furey electron state: alpha1_dag*(alpha2_dag*(alpha3_dag*omega)) = -i*omega_dag.
  4. Dual sector:  alpha1*(alpha2*(alpha3*omega_dag)) = -i*omega.
  5. Consequence: C_mu/C_e = 1 by the universal theorem; mass ratio needs topology.
"""

import numpy as np
import pytest

from calc.furey_electron_orbit import (
    ALPHA1, ALPHA2, ALPHA3,
    ALPHA1_DAG, ALPHA2_DAG, ALPHA3_DAG,
    OMEGA_DAG,
    compute_full_orbit,
    compute_orbit_period,
    furey_dual_electron_state,
    furey_electron_state,
    quark_state,
)
from calc.qed_ee_sim import E7, OMEGA, oct_mul_full

TOL = 1e-10
E1 = np.zeros(8, dtype=complex); E1[1] = 1.0
E0 = np.zeros(8, dtype=complex); E0[0] = 1.0


# ================================================================
# 1. Universal C_e = 4 Theorem (left-alternative law)
# ================================================================

class TestAlternativeLaw:

    def test_left_alt_e7_e1(self):
        """e7*(e7*e1) = -e1 (left-alternative law for a=e7)."""
        result = oct_mul_full(E7, oct_mul_full(E7, E1))
        assert np.allclose(result, -E1, atol=TOL)

    def test_left_alt_e7_omega(self):
        """e7*(e7*omega) = -omega."""
        result = oct_mul_full(E7, oct_mul_full(E7, OMEGA))
        assert np.allclose(result, -OMEGA, atol=TOL)

    def test_left_alt_all_basis(self):
        """L_{e7}^2(e_k) = -e_k for every basis vector k=0..7."""
        for k in range(8):
            ek = np.zeros(8, dtype=complex); ek[k] = 1.0
            result = oct_mul_full(E7, oct_mul_full(E7, ek))
            assert np.allclose(result, -ek, atol=TOL), f"Failed for k={k}"

    def test_l_e7_squared_neg_id_general(self):
        """L_{e7}^2(x) = -x for a generic linear combination."""
        x = np.array([1+2j, -3j, 0.5, 1j, -1, 0, 2-1j, 0.25j], dtype=complex)
        result = oct_mul_full(E7, oct_mul_full(E7, x))
        assert np.allclose(result, -x, atol=TOL)

    def test_l_e7_fourth_is_identity(self):
        """L_{e7}^4 = id for a generic state (follows from L_{e7}^2 = -id)."""
        x = np.array([0.7, 1+1j, -2j, 3, 0, 1-0.5j, -1, 0.3j], dtype=complex)
        s = x.copy()
        for _ in range(4):
            s = oct_mul_full(E7, s)
        assert np.allclose(s, x, atol=TOL)


# ================================================================
# 2. Witt Basis Properties
# ================================================================

class TestWittBasisProperties:

    def test_alpha1_annihilates_omega(self):
        """alpha1 * omega = 0  (CONVENTIONS.md §6: lowering operators annihilate vacuum)."""
        assert np.allclose(oct_mul_full(ALPHA1, OMEGA), np.zeros(8), atol=TOL)

    def test_alpha2_annihilates_omega(self):
        """alpha2 * omega = 0."""
        assert np.allclose(oct_mul_full(ALPHA2, OMEGA), np.zeros(8), atol=TOL)

    def test_alpha3_annihilates_omega(self):
        """alpha3 * omega = 0."""
        assert np.allclose(oct_mul_full(ALPHA3, OMEGA), np.zeros(8), atol=TOL)

    def test_omega_idempotent(self):
        """omega * omega = omega  (CONVENTIONS.md §6, property 1)."""
        assert np.allclose(oct_mul_full(OMEGA, OMEGA), OMEGA, atol=TOL)

    def test_omega_dag_idempotent(self):
        """omega_dag * omega_dag = omega_dag."""
        assert np.allclose(oct_mul_full(OMEGA_DAG, OMEGA_DAG), OMEGA_DAG, atol=TOL)

    def test_raising_operator_times_vacuum_is_itself(self):
        """alpha1_dag * omega = alpha1_dag.

        Every raising operator is an element of the minimal left ideal
        S = C(x)O * omega; omega acts as a right identity on S.
        """
        assert np.allclose(oct_mul_full(ALPHA1_DAG, OMEGA), ALPHA1_DAG, atol=TOL)
        assert np.allclose(oct_mul_full(ALPHA2_DAG, OMEGA), ALPHA2_DAG, atol=TOL)
        assert np.allclose(oct_mul_full(ALPHA3_DAG, OMEGA), ALPHA3_DAG, atol=TOL)

    def test_raise_then_lower_returns_vacuum(self):
        """alpha1 * (alpha1_dag * omega) = omega.

        Applying one creation then one annihilation returns the vacuum.
        This verifies the Clifford-type action: {alpha_j, alpha_j_dag} acts as
        the identity on the vacuum (in the ideal action sense).
        """
        s = oct_mul_full(ALPHA1_DAG, OMEGA)   # = alpha1_dag
        result = oct_mul_full(ALPHA1, s)       # alpha1 * alpha1_dag
        assert np.allclose(result, OMEGA, atol=TOL)


# ================================================================
# 3. Furey Electron State
# ================================================================

class TestFureyElectronState:

    def test_furey_electron_is_nonzero(self):
        """The full Furey electron state is non-zero."""
        psi_e = furey_electron_state()
        assert not np.allclose(psi_e, np.zeros(8), atol=TOL)

    def test_furey_electron_equals_neg_i_omega_dag(self):
        """alpha1_dag*(alpha2_dag*(alpha3_dag*omega)) = -i * omega_dag.

        Algebraic proof (CONVENTIONS.md Fano triples):
            alpha3_dag * omega = alpha3_dag                  (right identity on S)
            alpha2_dag * alpha3_dag = 0.5*(e1 - i*e6)
            alpha1_dag * 0.5*(e1 - i*e6) = -i * omega_dag
        """
        psi_e = furey_electron_state()
        expected = -1j * OMEGA_DAG
        assert np.allclose(psi_e, expected, atol=TOL)

    def test_furey_electron_orbit_period_4(self):
        """The Furey electron state has orbit period 4 under L_{e7}."""
        psi_e = furey_electron_state()
        assert compute_orbit_period(psi_e) == 4

    def test_furey_electron_orbit_visits_omega_dag(self):
        """After one L_{e7} kick, the Furey electron state maps to omega_dag.

        Orbit: -i*omega_dag -> omega_dag -> i*omega_dag -> -omega_dag -> -i*omega_dag.
        """
        psi_e = furey_electron_state()
        step1 = oct_mul_full(E7, psi_e)
        assert np.allclose(step1, OMEGA_DAG, atol=TOL)

    def test_furey_electron_full_orbit_structure(self):
        """The 4-step orbit of psi_e is exactly {-i*w†, w†, i*w†, -w†}."""
        psi_e = furey_electron_state()
        orbit = compute_full_orbit(psi_e)
        expected = [-1j * OMEGA_DAG, OMEGA_DAG, 1j * OMEGA_DAG, -OMEGA_DAG]
        for k, (got, exp) in enumerate(zip(orbit, expected)):
            assert np.allclose(got, exp, atol=TOL), f"Orbit step {k} mismatch"

    def test_intermediate_product_alpha2dag_alpha3dag(self):
        """alpha2_dag * alpha3_dag = 0.5*(e1 - i*e6).

        Intermediate step in the Furey electron state derivation.
        Verifies the non-associative product chain is computed correctly.
        """
        product = oct_mul_full(ALPHA2_DAG, ALPHA3_DAG)
        E6 = np.zeros(8, dtype=complex); E6[6] = 1.0
        expected = 0.5 * (E1 - 1j * E6)
        assert np.allclose(product, expected, atol=TOL)

    def test_quark_state_is_alpha_dag(self):
        """quark_state(j) = alpha_j_dag * omega = alpha_j_dag for j=1,2,3."""
        assert np.allclose(quark_state(1), ALPHA1_DAG, atol=TOL)
        assert np.allclose(quark_state(2), ALPHA2_DAG, atol=TOL)
        assert np.allclose(quark_state(3), ALPHA3_DAG, atol=TOL)

    def test_quark_state_orbit_period_4(self):
        """All one-particle (quark) states have orbit period 4 under L_{e7}."""
        for j in range(1, 4):
            qs = quark_state(j)
            assert compute_orbit_period(qs) == 4, f"Quark j={j} period != 4"


# ================================================================
# 4. Dual Sector (S^d minimal left ideal)
# ================================================================

class TestDualSector:

    def test_dual_electron_is_nonzero(self):
        """The dual-sector electron state is non-zero."""
        psi_dual = furey_dual_electron_state()
        assert not np.allclose(psi_dual, np.zeros(8), atol=TOL)

    def test_dual_electron_equals_neg_i_omega(self):
        """alpha1*(alpha2*(alpha3*omega_dag)) = -i * omega.

        Mirror image of the primal result:
            alpha3 * omega_dag = alpha3    (right identity on S^d)
            alpha2 * alpha3 = 0.5*(e1 + i*e6)
            alpha1 * 0.5*(e1 + i*e6) = -i * omega
        """
        psi_dual = furey_dual_electron_state()
        expected = -1j * OMEGA
        assert np.allclose(psi_dual, expected, atol=TOL)

    def test_dual_electron_orbit_period_4(self):
        """Dual electron state has orbit period 4."""
        psi_dual = furey_dual_electron_state()
        assert compute_orbit_period(psi_dual) == 4


# ================================================================
# 5. Implications for the Muon Mass Mechanism
# ================================================================

class TestImplications:

    def test_universal_orbit_period_sample(self):
        """C_e = 4 holds for 10 structurally diverse non-zero initial states.

        Direct numerical verification of the Universal C_e Theorem:
        L_{e7}^4 = id for every state in C(x)O.
        """
        test_states = [
            OMEGA,                    # vacuum
            OMEGA_DAG,                # conjugate vacuum
            furey_electron_state(),   # full Furey electron
            furey_dual_electron_state(),  # dual sector
            ALPHA1_DAG,               # quark 1
            ALPHA2_DAG,               # quark 2
            ALPHA3_DAG,               # quark 3
            E1,                       # single basis element
            np.array([1+2j, 0, 3, 0, -1j, 0, 2, 0.5j]),  # generic combo
            OMEGA + ALPHA1_DAG,       # mixed state
        ]
        for i, s in enumerate(test_states):
            p = compute_orbit_period(s)
            assert p == 4, f"State {i} has period {p} != 4"

    def test_muon_orbit_also_period_4(self):
        """The dual electron state (standing for the 'muon') also has period 4.

        C_mu = C_e = 4.  The mass ratio C_mu/C_e = 4/4 = 1, not 206.768.
        This confirms: the orbit-period mechanism under L_{e7} alone CANNOT
        produce m_mu/m_e.  Triality overhead or DAG topology is required.
        """
        c_e = compute_orbit_period(furey_electron_state())
        c_mu = compute_orbit_period(furey_dual_electron_state())
        assert c_e == 4
        assert c_mu == 4
        assert c_e == c_mu  # ratio = 1, not 207

    def test_ce_4_independent_of_initial_state(self):
        """C_e = 4 regardless of which non-zero state represents the electron.

        In particular, C_e(e1 component) = C_e(full Furey state) = 4.
        The gap_1_electron_state concern (claims/muon_mass.yml) is resolved:
        the C_e = 4 result from qed_calibration.py (e1 component) is not
        an artefact of the simplified initial state.
        """
        # e1 component (qed_calibration.py baseline)
        assert compute_orbit_period(E1) == 4
        # Full Furey state (alpha1_dag * alpha2_dag * alpha3_dag * omega)
        assert compute_orbit_period(furey_electron_state()) == 4
        # Any rescaling (phases)
        for phase in [1.0, -1.0, 1j, -1j, (1+1j)/np.sqrt(2)]:
            assert compute_orbit_period(phase * E1) == 4
