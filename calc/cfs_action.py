"""calc/cfs_action.py

Finster discrete causal action for the COG electron-muon system.

Tests whether the CFS Lagrangian (Finster-Jonsson-Kilbertus, arXiv:2201.06382)
produces a mass ratio consistent with m_mu/m_e = 206.768 for the COG
octonionic orbit structure.

CFS LAGRANGIAN (rank-1 projector reduction):
  For hermitian operators x = |psi_x><psi_x|, y = |psi_y><psi_y| on H = C^8:
    xy = <psi_x|psi_y> |psi_x><psi_y|
    ||xy||_F^2 = |<psi_x|psi_y>|^2
    tr(xy) = |<psi_x|psi_y>|^2
    L(x, y) = ||xy||^2 - (1/n)|tr(xy)|^2
             = |c|^2 - |c|^4/n    where c = <psi_x|psi_y>

COG ORBIT STRUCTURE (Universal C_e = 4 theorem):
  Both electron and muon complete 4-step orbits under L_{e7}:
    psi_0, psi_1 = e7*psi_0, psi_2 = -psi_0, psi_3 = -(e7*psi_0)
  Non-zero Lagrangian pairs: (0,2) and (1,3) with |c| = 1.
  Total orbit action per particle: S(n) = 2(1 - 1/n).

KEY FINDING:
  The simple L-ratio S(n_mu)/S(n_e) is bounded above by 2 for any
  n_e >= 2 and n_mu > n_e. This CANNOT produce m_mu/m_e = 206.768.

  The only way to get a large ratio from CFS is via the effective
  point-count scaling S ~ m^2 (Dirac sphere), where m = number of
  spacetime events per orbit:
    m_e = N_abs * V_e = 4 * 1 = 4
    m_mu = N_abs * V_mu = 4 * 15 = 60
    S_mu/S_e = (m_mu/m_e)^2 = 225    (8.8% above 206.768)

  Related models:
    N_TAU^2         = 196  (5.2% below 206.768)
    N_TAU * V_mu    = 210  (1.6% above 206.768)
    V_mu^2          = 225  (8.8% above 206.768)

References:
  Finster, Jonsson, Kilbertus (2022): arXiv:2201.06382
  Finster, Gmeineder (2025): arXiv:2503.00526
  claims/causal_action_discrete.yml (CFS-001)
  calc/emu_dag_sim.py (N_TAU, VERTEX_COST_MUON)
"""

from __future__ import annotations

import numpy as np

from calc.qed_ee_sim import oct_mul_full, E1, E7
from calc.emu_dag_sim import (
    N_TAU,
    VERTEX_COST_ELECTRON,
    VERTEX_COST_MUON,
    EXPERIMENTAL_MASS_RATIO,
)


# ================================================================
# Core CFS Lagrangian
# ================================================================

def cfs_lagrangian(c: complex, n: float) -> float:
    """CFS Lagrangian for rank-1 projectors.

    Args:
      c:  Complex overlap <psi_i|psi_j>.
      n:  Spin dimension of the Hilbert space (must be > 0).

    Returns:
      L = |c|^2 - |c|^4 / n.
      For |c| = 0: L = 0 (orthogonal states, causally unrelated).
      For |c| = 1: L = 1 - 1/n  (antiparallel basis states).
    """
    c2 = abs(c) ** 2
    return float(c2 - c2 ** 2 / n)


# ================================================================
# Orbit states
# ================================================================

def orbit_states(initial: np.ndarray, n_steps: int = 4) -> list[np.ndarray]:
    """Compute L_{e7}^k(psi_0) for k = 0, 1, ..., n_steps-1.

    By the left-alternative law: e7*(e7*x) = (e7^2)*x = -x, so
    the orbit has period 4 regardless of the initial state.

    Args:
      initial:  Starting state (complex numpy array, shape (8,)).
      n_steps:  Number of orbit steps; default 4 (one full cycle).

    Returns:
      List of n_steps complex arrays, each of shape (8,).
    """
    state = np.array(initial, dtype=complex)
    states: list[np.ndarray] = [state.copy()]
    for _ in range(n_steps - 1):
        state = oct_mul_full(E7, state)
        states.append(state.copy())
    return states


# ================================================================
# Orbit causal action
# ================================================================

def orbit_action(states: list[np.ndarray], n: float) -> float:
    """Sum Lagrangians over all distinct pairs in the orbit.

    S = sum_{i < j} L(psi_i, psi_j, n).

    Args:
      states:  List of orbit state vectors.
      n:       Spin dimension.

    Returns:
      Total orbit causal action (float).
    """
    total = 0.0
    m = len(states)
    for i in range(m):
        for j in range(i + 1, m):
            c = np.vdot(states[i], states[j])  # complex inner product
            total += cfs_lagrangian(c, n)
    return total


# ================================================================
# Simple L-ratio model
# ================================================================

def simple_lagrangian_ratio(n_e: float, n_mu: float,
                             initial: np.ndarray | None = None) -> dict:
    """Compute S_mu/S_e using the per-orbit Lagrangian sum.

    Both particles have the same orbit structure (Universal C_e = 4),
    so the ratio reduces to:
      S(n) = 2(1 - 1/n)    [from the two antiparallel pairs (0,2) and (1,3)]
      S_mu/S_e = (1 - 1/n_mu) / (1 - 1/n_e)

    This is bounded above by ~2 for any reasonable n_e, n_mu.

    Args:
      n_e, n_mu:  Spin dimensions for electron and muon.
      initial:    Initial state (default: E1).

    Returns:
      Dict with S_e, S_mu, ratio, and gap to experimental value.
    """
    psi0 = E1.astype(complex) if initial is None else np.array(initial, dtype=complex)
    states = orbit_states(psi0)
    S_e = orbit_action(states, n_e)
    S_mu = orbit_action(states, n_mu)
    ratio = S_mu / S_e if S_e > 1e-15 else float('inf')
    return {
        'model': 'simple_lagrangian_ratio',
        'n_e': n_e,
        'n_mu': n_mu,
        'S_e': S_e,
        'S_mu': S_mu,
        'ratio': ratio,
        'gap_to_experimental': abs(ratio - EXPERIMENTAL_MASS_RATIO),
        'note': 'Bounded above by ~2; cannot reach 206.768.',
    }


# ================================================================
# Effective point-count model (S ~ m^2 Dirac sphere scaling)
# ================================================================

def effective_point_model(
    v_e: int = VERTEX_COST_ELECTRON,
    v_mu: int = VERTEX_COST_MUON,
    n_absorptions: int = 4,
) -> dict:
    """Effective spacetime point count model.

    In the Finster (2022) discrete Dirac sphere, S ~ m^2 for m spacetime
    points.  If each absorption event creates v_p 'effective spacetime
    points' (ticks), then:
      m_e = n_absorptions * v_e = 4 * 1 = 4
      m_mu = n_absorptions * v_mu = 4 * 15 = 60
      S_mu/S_e = (m_mu / m_e)^2 = (v_mu / v_e)^2 = 225

    Also reports related integer products from N_TAU and V_mu.

    Returns:
      Dict of predictions and their deviations from 206.768.
    """
    m_e = n_absorptions * v_e
    m_mu = n_absorptions * v_mu
    ratio_squared = (m_mu / m_e) ** 2
    ratio_linear = m_mu / m_e

    models = {
        'effective_m_squared': ratio_squared,           # (V_mu/V_e)^2 = 225
        'effective_m_linear': ratio_linear,             # V_mu/V_e = 15
        'N_TAU_squared': float(N_TAU ** 2),             # 196
        'N_TAU_times_V_mu': float(N_TAU * v_mu),        # 210
        'V_mu_squared': float(v_mu ** 2),               # 225
        'sqrt_experimental': float(EXPERIMENTAL_MASS_RATIO ** 0.5),  # ~14.379
    }

    return {
        'model': 'effective_point_count',
        'm_e': m_e,
        'm_mu': m_mu,
        'experimental': EXPERIMENTAL_MASS_RATIO,
        'predictions': models,
        'gaps': {k: abs(v - EXPERIMENTAL_MASS_RATIO) / EXPERIMENTAL_MASS_RATIO
                 for k, v in models.items()},
        'note': (
            f'Best: N_TAU * V_mu = {N_TAU * v_mu} '
            f'({abs(N_TAU * v_mu - EXPERIMENTAL_MASS_RATIO) / EXPERIMENTAL_MASS_RATIO:.1%} off). '
            f'sqrt(m_mu/m_e) = {EXPERIMENTAL_MASS_RATIO**0.5:.4f} ≈ {N_TAU} + 0.38.'
        ),
    }


# ================================================================
# Comprehensive model scan
# ================================================================

def run_cfs_models() -> dict:
    """Run all CFS action models and return summary table.

    Returns:
      Dict with keys 'simple_scan', 'effective_model', and 'summary'.
    """
    # 1. Simple L-ratio scan over spin dimension pairs
    simple_scan = []
    for n_e in [2, 4, 8]:
        for n_mu in [n_e, n_e * 2, n_e * 7, n_e * N_TAU, n_e * VERTEX_COST_MUON,
                     n_e * N_TAU * VERTEX_COST_MUON]:
            r = simple_lagrangian_ratio(float(n_e), float(n_mu))
            simple_scan.append({
                'n_e': n_e, 'n_mu': n_mu,
                'S_e': round(r['S_e'], 6),
                'S_mu': round(r['S_mu'], 6),
                'ratio': round(r['ratio'], 4),
            })

    # 2. Effective point count model
    eff = effective_point_model()

    # 3. Orbit states for verification
    states_e = orbit_states(E1.astype(complex))
    overlaps = {}
    for i in range(4):
        for j in range(i + 1, 4):
            c = np.vdot(states_e[i], states_e[j])
            overlaps[f'({i},{j})'] = round(float(abs(c)), 6)

    return {
        'orbit_overlaps': overlaps,
        'simple_scan': simple_scan,
        'effective_model': eff,
        'summary': {
            'simple_ratio_max': max(r['ratio'] for r in simple_scan
                                    if r['ratio'] < 1e8),
            'simple_ratio_cannot_reach_206': True,
            'effective_m_squared_ratio': eff['predictions']['effective_m_squared'],
            'closest_integer_model': f"N_TAU * V_mu = {N_TAU * VERTEX_COST_MUON}",
            'closest_gap_percent': round(
                abs(N_TAU * VERTEX_COST_MUON - EXPERIMENTAL_MASS_RATIO)
                / EXPERIMENTAL_MASS_RATIO * 100, 2
            ),
        },
    }


# ================================================================
# Entry point
# ================================================================

if __name__ == '__main__':
    print('=' * 65)
    print('CFS Causal Action: COG Electron-Muon Mass Ratio Models')
    print('=' * 65)

    print(f'\nN_TAU = {N_TAU}  V_e = {VERTEX_COST_ELECTRON}  '
          f'V_mu = {VERTEX_COST_MUON}  m_mu/m_e(exp) = {EXPERIMENTAL_MASS_RATIO}')

    # Orbit structure
    states = orbit_states(E1.astype(complex))
    print('\nElectron orbit states (via L_{e7}^k(e1)):')
    for k, s in enumerate(states):
        nz = [(i, s[i]) for i in range(8) if abs(s[i]) > 1e-10]
        print(f'  psi_{k}: {nz}')

    print('\nPairwise overlaps <psi_i|psi_j>:')
    for i in range(4):
        for j in range(i + 1, 4):
            c = np.vdot(states[i], states[j])
            if abs(c) > 1e-10:
                print(f'  ({i},{j}): c = {c:.4f}  L(n=8) = {cfs_lagrangian(c, 8):.4f}')

    print('\n--- Simple L-ratio model ---')
    print('(S(n_e)/S(n_mu) is bounded by ~2; cannot reach 206.768)')
    for n_e, n_mu in [(2, 28), (2, 30), (8, 112), (8, 120)]:
        r = simple_lagrangian_ratio(float(n_e), float(n_mu))
        print(f'  n_e={n_e:3d} n_mu={n_mu:4d}: ratio = {r["ratio"]:.4f}')

    print('\n--- Effective point-count model (S ~ m^2) ---')
    eff = effective_point_model()
    for name, val in eff['predictions'].items():
        gap_pct = eff['gaps'][name] * 100
        print(f'  {name:30s} = {val:.3f}  ({gap_pct:.1f}% from 206.768)')

    results = run_cfs_models()
    print(f'\nConclusion: simple ratio max = {results["summary"]["simple_ratio_max"]:.2f}')
    print(f'Closest integer model: {results["summary"]["closest_integer_model"]} '
          f'({results["summary"]["closest_gap_percent"]}% off)')
    print(f'Full m_mu/m_e mechanism remains open.')
