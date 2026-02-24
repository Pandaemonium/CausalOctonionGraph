"""calc/furey_electron_orbit.py

Full Furey Electron State and Universal C_e = 4 Theorem.

Computes the full Furey electron state
    psi_e = alpha1_dag * (alpha2_dag * (alpha3_dag * omega))
as defined in rfc/CONVENTIONS.md §6 and measures its orbit period under L_{e7}.

KEY RESULT — UNIVERSAL C_e THEOREM (proved algebraically, verified numerically):
    By the left-alternative law of octonions (which holds in C(x)O):
        e7 * (e7 * x) = (e7 * e7) * x = -x    for ALL x in C(x)O.
    Therefore L_{e7}^2 = -id, and L_{e7}^4 = id.
    The orbit period of ANY non-zero x under L_{e7} is exactly 4.

    Proof:  Apply the left-alternative law with a = e7:
            L_{e7}^2(x) = e7 * (e7 * x) = (e7 * e7) * x = -1 * x = -x.
            Period 1 would require L_{e7}(x) = x => e7*x = x, but then -x = x => x=0.
            Period 2 would require L_{e7}^2(x) = x => -x = x => x=0.
            Hence any non-zero x has period exactly 4.

COMPUTED RESULT:
    psi_e = alpha1_dag * (alpha2_dag * (alpha3_dag * omega)) = -i * omega_dag
    The Furey electron state is (up to a pure phase) the conjugate vacuum omega_dag.
    Its orbit under L_{e7}: {-i*omega_dag, omega_dag, i*omega_dag, -omega_dag}.
    Orbit period = 4.  Consistent with C_e = 4 from qed_calibration.py (e1 component).

CONSEQUENCE FOR MUON MASS:
    C_e = C_mu = 4 for ANY non-zero state under repeated L_{e7} kicks.
    The mass ratio m_mu/m_e CANNOT arise from state-orbit period alone.
    The mechanism must involve triality overhead (N_tau = 14 per S+ vertex,
    RFC-012) or DAG topology, not the algebraic orbit period.
    This closes gap_1_electron_state in claims/muon_mass.yml.

References:
    rfc/CONVENTIONS.md §5 (Witt basis), §6 (fermion state construction)
    claims/muon_mass.yml (gap_1_electron_state, literature_gaps_found_2026_02_23)
    calc/qed_ee_sim.py (oct_mul_full, OMEGA, E7)
    calc/qed_calibration.py (C_e = 4 from e1 component, Goal A)
"""

from __future__ import annotations

import numpy as np

from calc.qed_ee_sim import OMEGA, E7, oct_mul_full


# ================================================================
# Basis vectors (state index k = coefficient of e_k in C(x)O)
# ================================================================

def _bv(k: int) -> np.ndarray:
    v = np.zeros(8, dtype=complex)
    v[k] = 1.0
    return v


E0 = _bv(0)
E1 = _bv(1)
E2 = _bv(2)
E3 = _bv(3)
E4 = _bv(4)
E5 = _bv(5)
E6 = _bv(6)
# E7 imported from qed_ee_sim

# Conjugate vacuum: omega_dag = 0.5*(e0 - i*e7)   (rfc/CONVENTIONS.md §6)
OMEGA_DAG: np.ndarray = 0.5 * E0 - 0.5j * E7

# ================================================================
# Witt basis operators (rfc/CONVENTIONS.md §5.3-5.4)
# Pairs: color j=1 -> (e6,e1), j=2 -> (e2,e5), j=3 -> (e3,e4)
# ================================================================

# Lowering (annihilation) operators: alpha_j = 0.5*(e_a + i*e_b)
ALPHA1: np.ndarray = 0.5 * (E6 + 1j * E1)   # color 1: (e6, e1)
ALPHA2: np.ndarray = 0.5 * (E2 + 1j * E5)   # color 2: (e2, e5)
ALPHA3: np.ndarray = 0.5 * (E3 + 1j * E4)   # color 3: (e3, e4)

# Raising (creation) operators: alpha_j_dag = 0.5*(-e_a + i*e_b)
# Sign correction (CONVENTIONS.md §5.4): Hermitian adjoint includes octonion
# conjugation (e_a -> -e_a), yielding the negative sign for {alpha_j, alpha_j†}=1.
ALPHA1_DAG: np.ndarray = 0.5 * (-E6 + 1j * E1)   # color 1
ALPHA2_DAG: np.ndarray = 0.5 * (-E2 + 1j * E5)   # color 2
ALPHA3_DAG: np.ndarray = 0.5 * (-E3 + 1j * E4)   # color 3


# ================================================================
# Orbit computation
# ================================================================

def compute_orbit_period(initial_state: np.ndarray, max_steps: int = 20) -> int:
    """Return the smallest k >= 1 s.t. L_{e7}^k(initial_state) = initial_state.

    Returns -1 if no return within max_steps.  For any non-zero state this
    should always return 4 (Universal C_e Theorem).
    """
    tol = 1e-10
    state = initial_state.copy()
    for k in range(1, max_steps + 1):
        state = oct_mul_full(E7, state)
        if np.allclose(state, initial_state, atol=tol):
            return k
    return -1


def compute_full_orbit(initial_state: np.ndarray) -> list[np.ndarray]:
    """Return the 4-element orbit list [x, L(x), L^2(x), L^3(x)] under L_{e7}."""
    orbit = [initial_state.copy()]
    state = initial_state.copy()
    for _ in range(3):
        state = oct_mul_full(E7, state)
        orbit.append(state.copy())
    return orbit


# ================================================================
# Furey fermion states (rfc/CONVENTIONS.md §6)
# ================================================================

def quark_state(j: int) -> np.ndarray:
    """One-particle (quark) state: alpha_j_dag * omega, j in {1,2,3}."""
    alphas = [ALPHA1_DAG, ALPHA2_DAG, ALPHA3_DAG]
    return oct_mul_full(alphas[j - 1], OMEGA)


def furey_electron_state() -> np.ndarray:
    """Full Furey charged-lepton state (CONVENTIONS.md §6).

    Returns alpha1_dag * (alpha2_dag * (alpha3_dag * omega)).
    Operators applied right-to-left (standard QM convention).
    Algebraic result: -i * omega_dag.
    """
    s = OMEGA.copy()
    s = oct_mul_full(ALPHA3_DAG, s)   # alpha3_dag * omega  = alpha3_dag
    s = oct_mul_full(ALPHA2_DAG, s)   # alpha2_dag * alpha3_dag
    s = oct_mul_full(ALPHA1_DAG, s)   # alpha1_dag * (alpha2_dag * alpha3_dag)
    return s


def furey_dual_electron_state() -> np.ndarray:
    """Dual-sector charged-lepton state.

    Returns alpha1 * (alpha2 * (alpha3 * omega_dag)).
    In the S^d minimal LEFT ideal (generated by omega_dag).
    Algebraic result: -i * omega.
    """
    s = OMEGA_DAG.copy()
    s = oct_mul_full(ALPHA3, s)
    s = oct_mul_full(ALPHA2, s)
    s = oct_mul_full(ALPHA1, s)
    return s
