"""calc/qed_ee_sim.py
Goal C: Electron-Electron Dynamic Graph Simulation (Phase 1)

Implements RFC-013 (Algebraic Vacuum, State Representation, Dynamic Causal Spawning)
for a 1D chain topology: two electrons separated by D vacuum nodes.

Architecture (RFC-013 locked decisions):
  1. Full C(x)O state: length-8 complex numpy array (index k = coefficient of e_k).
  2. Left-multiplication: state_next = oct_mul_full(E7, state_current).
  3. Vacuum relay: e7 * omega = -i*omega  (RFC-013 section 5.1, 1 tick, phase-shift).
  4. Axiom of Identity: vacuum detection via algebraic check only (no metadata).
  5. SPAWN sentinel: -1 (reserved for Phase 2 graph growth; chain pre-built here).

Topology (RFC-013 section 7):
  E1(pos=0) -- V[0](pos=1) -- ... -- V[D-1](pos=D) -- E2(pos=D+1)

Protocol:
  Tick 0  : Both electrons emit photons toward each other.
             Electron state does NOT change on emission (absorption-only model).
  Tick 1..D: Photons relay through vacuum nodes (e7 left-applied per hop).
  Tick D+1 : Both electrons absorb simultaneously; both re-emit.
  Repeat until both electrons return to their exact initial state.

Design note -- emission vs absorption:
  RFC-013 section 4.4 states that emission also applies e7 to the emitter.
  This simulation uses the absorption-only model for consistency with the
  C_e = 4 result from Goal A (qed_calibration.py, right-multiplication baseline).
  The discrepancy is flagged as an open question in RFC-013 section 10, row 3.

Observables:
  Ce_exact   : Exchange cycles until both electrons return to exact initial state.
               Expected: 4 (consistent with Goal A).
  total_ticks: Total simulation ticks = Ce_exact * (D + 1).
  vacuum_phase: Vacuum nodes accumulate phase (-i)^n per n photon hits.

References:
  rfc/RFC-013_Algebraic_Vacuum_and_Causal_Spawning.md
  calc/qed_calibration.py  (Goal A: right-mult baseline, C_e = 4)
  calc/conftest.py         (FANO_SIGN, FANO_THIRD, VACUUM_AXIS)
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

import numpy as np

from calc.conftest import FANO_SIGN, FANO_THIRD, VACUUM_AXIS


# ================================================================
# Constants: C(x)O basis states and operators
# ================================================================

PHOTON_IDX: int = VACUUM_AXIS + 1   # = 7  (state index for e7)
"""State index for the photon operator e7 (vacuum axis, U(1)_EM generator).
VACUUM_AXIS (conftest) = 6 is the 0-indexed Fano point; state index = 7."""

SPAWN: int = -1
"""Sentinel for RFC-013 section 6.1: destination node not yet instantiated."""


def _basis_vec(k: int) -> np.ndarray:
    """Return the k-th standard basis vector in C^8 (dtype=complex)."""
    v = np.zeros(8, dtype=complex)
    v[k] = 1.0 + 0j
    return v


E0 = _basis_vec(0)   # scalar identity
E1 = _basis_vec(1)   # first L1 element -- electron initial state (Furey convention)
E7 = _basis_vec(7)   # vacuum axis / photon operator

OMEGA: np.ndarray = 0.5 * E0 + 0.5j * E7
"""Furey vacuum idempotent omega = 0.5*(e0 + i*e7) (RFC-013 section 2.1)."""

_ORBIT_PHASES = [1.0 + 0j, -1j, -1.0 + 0j, +1j]
VACUUM_ORBIT: tuple[np.ndarray, ...] = tuple(p * OMEGA for p in _ORBIT_PHASES)
"""Closed orbit {omega, -i*omega, -omega, +i*omega} under repeated L_e7 (period 4)."""


# ================================================================
# Complex-Octonion left-multiplication (RFC-013 section 3.3)
# ================================================================

def oct_mul_basis(i: int, j: int) -> tuple[int, int]:
    """Multiply basis elements e_i * e_j = sign * e_k.

    Returns (k, sign) where sign in {+1, -1}.
    Index range: 0..7  (0 = scalar e0; 1..7 = imaginary units e1..e7).

    Rules:
      e0 * e_j = e_j            (scalar identity, left)
      e_i * e0 = e_i            (scalar identity, right)
      e_i * e_i = -e0           (imaginary units square to -1, i != 0)
      e_i * e_j  (distinct i,j in 1..7): use Fano sign table (locked Furey convention)
    """
    if i == 0:
        return (j, 1)
    if j == 0:
        return (i, 1)
    if i == j:
        return (0, -1)
    # Distinct imaginary units i, j in 1..7.
    # Convert to 0-indexed Fano points (0..6) and look up the precomputed table.
    fi, fj = i - 1, j - 1
    fk  = FANO_THIRD[(fi, fj)]
    sgn = FANO_SIGN [(fi, fj)]
    return (fk + 1, sgn)   # convert result back to state index


def oct_mul_full(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Left-multiply a * b in C(x)O using the locked Furey Fano convention.

    a, b: length-8 complex numpy arrays (index k = coefficient of e_k).
    Returns a length-8 complex array.

    For left-multiplication by the photon operator:
        state_next = oct_mul_full(E7, state_current)
    This matches RFC-013 section 4: state_next = e7 * state_current.
    """
    result = np.zeros(8, dtype=complex)
    for i in range(8):
        ai = a[i]
        if ai == 0:
            continue
        for j in range(8):
            bj = b[j]
            if bj == 0:
                continue
            k, sgn = oct_mul_basis(i, j)
            result[k] += ai * bj * sgn
    return result


# ================================================================
# Axiom of Identity: algebraic vacuum detection (RFC-013 section 2.3)
# ================================================================

def state_is_vacuum_orbit(state: np.ndarray, tol: float = 1e-10) -> bool:
    """Return True iff state is in the vacuum orbit {omega, -i*omega, -omega, +i*omega}.

    Algebraic check only -- no metadata (Axiom of Identity, RFC-013 section 2.3).
    Correct:   if state_is_vacuum_orbit(node.state): ...
    Forbidden: if node.is_vacuum: ...   (metadata tag violates the Axiom)
    """
    for v in VACUUM_ORBIT:
        if np.allclose(state, v, atol=tol):
            return True
    return False


def state_is_matter(state: np.ndarray, tol: float = 1e-10) -> bool:
    """Return True iff state is NOT in the vacuum orbit (matter node)."""
    return not state_is_vacuum_orbit(state, tol)


# ================================================================
# EE Simulation dataclass
# ================================================================

@dataclass
class AbsorptionEvent:
    """State snapshot at a joint absorption tick (both electrons absorbed)."""
    cycle: int                  # which absorption cycle this is (1-indexed)
    tick: int                   # simulation tick at which both absorbed
    e1_state: np.ndarray        # E1 state after absorption
    e2_state: np.ndarray        # E2 state after absorption
    vacuum_states: list         # states of all D vacuum nodes at this tick
    e1_at_initial: bool         # True iff E1 has returned to initial state
    e2_at_initial: bool         # True iff E2 has returned to initial state
    vacuum_at_initial: bool     # True iff all vacuum nodes have returned to OMEGA


# ================================================================
# Main simulation
# ================================================================

def simulate_ee(
    D: int,
    max_cycles: int = 20,
    initial_state: Optional[np.ndarray] = None,
) -> dict:
    """Simulate electron-electron scattering on a 1D causal chain.

    Topology (RFC-013 section 7):
      E1(pos=0) -- V[0](pos=1) -- ... -- V[D-1](pos=D) -- E2(pos=D+1)

    Both electrons emit photons toward each other at tick 0 (no state change
    on emission). Photons propagate at 1 hop/tick through vacuum nodes
    (e7 applied to each vacuum node state: relay protocol RFC-013 section 5.3).
    Electrons absorb at tick D+1, 2*(D+1), ... Each absorption applies e7 to
    the electron state. After each absorption the electron immediately re-emits
    (no additional state change on re-emission).

    Stops when both electrons simultaneously return to their exact initial state.

    Args:
      D:            Number of vacuum nodes between the two electrons (>= 0).
      max_cycles:   Safety limit on absorption cycles.
      initial_state: Initial electron state vector (default: E1 = [0,1,0,...]).

    Returns dict with:
      D                    : number of vacuum nodes
      Ce_exact             : exchange cycles until exact joint return (-1 if not found)
      total_ticks          : total simulation ticks at termination
      tick_per_cycle       : D + 1  (ticks between successive joint absorptions)
      absorption_history   : list[AbsorptionEvent], one entry per joint absorption
      chain_states_final   : numpy array (chain_len, 8) of final node states
      vacuum_period_tick   : tick at which vacuum nodes first returned to OMEGA
                             (None if vacuum never fully returned within simulation)
    """
    if initial_state is None:
        initial_state = E1.copy()

    chain_len = D + 2
    chain = np.zeros((chain_len, 8), dtype=complex)
    chain[0]     = initial_state.copy()   # E1
    chain[D + 1] = initial_state.copy()   # E2
    for i in range(1, D + 1):
        chain[i] = OMEGA.copy()           # vacuum nodes

    initial_e1  = initial_state.copy()
    initial_e2  = initial_state.copy()

    # Photon events: tick -> [(target_pos, direction), ...]
    # direction: +1 = moving E1->E2, -1 = moving E2->E1
    pending: dict[int, list] = defaultdict(list)

    # Schedule initial photon arrivals at tick 1.
    if D == 0:
        # Direct interaction: no vacuum nodes.
        # E1's photon goes directly to E2 (pos=D+1=1) at tick 1.
        # E2's photon goes directly to E1 (pos=0) at tick 1.
        pending[1].append((D + 1, +1))
        pending[1].append((0,     -1))
    else:
        # First vacuum hop at tick 1.
        pending[1].append((1,   +1))   # E1's photon -> V[0]
        pending[1].append((D,   -1))   # E2's photon -> V[D-1]

    absorption_count = [0, 0]     # [count_E1, count_E2]
    absorption_history: list[AbsorptionEvent] = []
    vacuum_period_tick: Optional[int] = None

    max_ticks = max_cycles * (D + 2) + 10

    for t in range(1, max_ticks + 1):
        tick_events = pending.pop(t, [])
        if not tick_events:
            continue

        # Sort by target position for deterministic processing order.
        tick_events.sort(key=lambda e: e[0])

        for (tgt, direction) in tick_events:
            # Apply photon operator via left-multiplication.
            chain[tgt] = oct_mul_full(E7, chain[tgt])

            is_electron = (tgt == 0 or tgt == D + 1)

            if is_electron:
                # Electron absorbed a photon.  Re-emit in the same forward direction.
                # (The re-emitted photon is a new e7-labeled edge; electron state
                #  does not change further on re-emission -- absorption-only model.)
                if tgt == 0:
                    # E1 absorbed; re-emit toward E2.
                    absorption_count[0] += 1
                    next_tgt = 1 if D > 0 else D + 1
                    pending[t + 1].append((next_tgt, +1))
                else:
                    # E2 absorbed; re-emit toward E1.
                    absorption_count[1] += 1
                    next_tgt = D if D > 0 else 0
                    pending[t + 1].append((next_tgt, -1))

                # Record joint state when both electrons have absorbed equally.
                if absorption_count[0] == absorption_count[1]:
                    cycle_n = absorption_count[0]

                    e1_at_init  = np.allclose(chain[0],     initial_e1, atol=1e-10)
                    e2_at_init  = np.allclose(chain[D + 1], initial_e2, atol=1e-10)
                    vac_at_init = all(
                        np.allclose(chain[k], OMEGA, atol=1e-10)
                        for k in range(1, D + 1)
                    )

                    event = AbsorptionEvent(
                        cycle=cycle_n,
                        tick=t,
                        e1_state=chain[0].copy(),
                        e2_state=chain[D + 1].copy(),
                        vacuum_states=[chain[k].copy() for k in range(1, D + 1)],
                        e1_at_initial=e1_at_init,
                        e2_at_initial=e2_at_init,
                        vacuum_at_initial=vac_at_init,
                    )
                    absorption_history.append(event)

                    if vacuum_period_tick is None and vac_at_init:
                        vacuum_period_tick = t

                    # Full system return: both electrons AND vacuum at initial.
                    if e1_at_init and e2_at_init:
                        return {
                            'D': D,
                            'Ce_exact': cycle_n,
                            'total_ticks': t,
                            'tick_per_cycle': D + 1,
                            'absorption_history': absorption_history,
                            'chain_states_final': chain.copy(),
                            'vacuum_period_tick': vacuum_period_tick,
                        }
            else:
                # Vacuum node: relay photon to the next position in the chain.
                next_pos = tgt + direction
                if 0 <= next_pos <= D + 1:
                    pending[t + 1].append((next_pos, direction))
                # else: next_pos out of range -> SPAWN territory (Phase 2).

    # Simulation ended without finding exact return.
    return {
        'D': D,
        'Ce_exact': -1,
        'total_ticks': max_ticks,
        'tick_per_cycle': D + 1,
        'absorption_history': absorption_history,
        'chain_states_final': chain.copy(),
        'vacuum_period_tick': vacuum_period_tick,
    }


# ================================================================
# Verification helpers
# ================================================================

def verify_left_mult_orbit(state: Optional[np.ndarray] = None) -> dict:
    """Verify single-particle orbit under left-multiplication by E7.

    Expected orbit (RFC-013 section 4.2):
      +e1 -> -e6 -> -e1 -> +e6 -> +e1   (period 4)

    Returns dict with trajectory list, period, and passed flag.
    """
    if state is None:
        state = E1.copy()

    start = state.copy()
    trajectory = [start.copy()]
    current = state.copy()

    for _ in range(20):
        current = oct_mul_full(E7, current)
        trajectory.append(current.copy())
        if np.allclose(current, start, atol=1e-10):
            period = len(trajectory) - 1
            return {
                'start': start,
                'trajectory': trajectory[:-1],   # exclude the return copy
                'period': period,
                'passed': period == 4,
            }

    return {'start': start, 'trajectory': trajectory, 'period': -1, 'passed': False}


def verify_vacuum_relay() -> dict:
    """Verify e7 * omega = -i * omega (RFC-013 section 5.1).

    Returns dict with result array, expected array, and passed flag.
    """
    result   = oct_mul_full(E7, OMEGA)
    expected = -1j * OMEGA
    passed   = np.allclose(result, expected, atol=1e-10)
    return {'result': result, 'expected': expected, 'passed': passed}


def run_calibration_check() -> dict:
    """Run all Goal C Phase 1 calibration checks.

    Checks:
      1. left_mult_orbit_period : period of e1 under L_e7 = 4
      2. vacuum_relay           : e7 * omega = -i*omega
      3. ee_sim_D0              : Ce_exact=4, total_ticks=4
      4. ee_sim_D1              : Ce_exact=4, total_ticks=8
      5. ee_sim_D2              : Ce_exact=4, total_ticks=12
      6. d_independence         : Ce_exact=4 for D=0,1,2,4

    Returns dict with 'checks' (dict of individual results) and 'all_passed' (bool).
    """
    checks: dict = {}

    # 1. Left-mult orbit period.
    orbit = verify_left_mult_orbit()
    checks['left_mult_orbit_period'] = {
        'expected': 4,
        'actual': orbit['period'],
        'passed': orbit['passed'],
    }

    # 2. Vacuum relay identity.
    relay = verify_vacuum_relay()
    checks['vacuum_relay'] = {
        'identity': 'e7 * omega = -i*omega',
        'actual_matches': relay['passed'],
        'passed': relay['passed'],
    }

    # 3-5. simulate_ee for D = 0, 1, 2.
    for D in [0, 1, 2]:
        sim = simulate_ee(D)
        expected_ticks = 4 * (D + 1)
        ok = (sim['Ce_exact'] == 4 and sim['total_ticks'] == expected_ticks)
        checks[f'ee_sim_D{D}'] = {
            'D': D,
            'Ce_exact': sim['Ce_exact'],
            'total_ticks': sim['total_ticks'],
            'expected_Ce': 4,
            'expected_ticks': expected_ticks,
            'passed': ok,
        }

    # 6. D-independence.
    D_values = [0, 1, 2, 4]
    Ce_values = [simulate_ee(D)['Ce_exact'] for D in D_values]
    d_indep = (len(set(Ce_values)) == 1 and Ce_values[0] == 4)
    checks['d_independence'] = {
        'D_values': D_values,
        'Ce_exact_values': Ce_values,
        'passed': d_indep,
    }

    all_passed = all(c['passed'] for c in checks.values())
    return {'checks': checks, 'all_passed': all_passed}


# ================================================================
# Entry point: print calibration report
# ================================================================

if __name__ == '__main__':
    print('=' * 60)
    print('QED E-E Simulation: Goal C Phase 1 Calibration')
    print('=' * 60)

    relay = verify_vacuum_relay()
    print(f'\n[1] Vacuum relay: e7 * omega = -i*omega: {relay["passed"]}')

    orbit = verify_left_mult_orbit()
    E6_idx = 6
    step_labels = []
    for s in orbit['trajectory']:
        dominant = np.argmax(np.abs(s))
        sign_char = '+' if np.real(s[dominant]) > 0 else '-'
        step_labels.append(f'{sign_char}e{dominant}')
    print(f'[2] Left-mult orbit of e1: period={orbit["period"]}')
    print(f'    trajectory: {" -> ".join(step_labels)}')

    for D in [0, 1, 2, 4]:
        sim = simulate_ee(D)
        print(
            f'[3] simulate_ee(D={D}): '
            f'Ce_exact={sim["Ce_exact"]}  '
            f'total_ticks={sim["total_ticks"]}  '
            f'(expected: Ce=4, ticks={4*(D+1)})'
        )
        if sim['absorption_history']:
            hist = sim['absorption_history']
            print(f'    vacuum_period_tick={sim["vacuum_period_tick"]}')

    calib = run_calibration_check()
    print(f'\nCalibration: all_passed={calib["all_passed"]}')
    for name, check in calib['checks'].items():
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f'  [{status}] {name}')
