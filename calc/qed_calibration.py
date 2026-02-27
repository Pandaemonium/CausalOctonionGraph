"""calc/qed_calibration.py
Goal A: Calibrate C_e -- the baseline L1 electron orbit count on a symmetric
periodic vacuum loop.

Physical corrections applied (Gemini, 2026-02-23):

  1. ELECTRON STATE: e1 (L1 associative subalgebra {e1,e2,e3}), NOT e6.
     e6 is the Witt nil-element alpha_1^dag * omega in the color/excited sector.
     The physical electron lives in the quaternionic L1 subalgebra which is
     associative under octonion multiplication (Furey 2019, arXiv:1910.08395).

  2. THE KICK MECHANISM (algebraically forced by the locked Fano convention):
       e1  x  e7  =  +e6    (electron absorbs photon -> excited/color state)
       e6  x  e7  =  -e1    (de-excitation -> back to L1 with phase flip)
     Convention: RIGHT-multiplication (state x operator), verified against
     FANO_CYCLES in rfc/CONVENTIONS.md.

  3. SIGNED STATE: the orbit under repeated e7 absorption has period 4:
       +e1 -> +e6 -> -e1 -> -e6 -> +e1  (exact signed return, 4 absorptions)
       +e1 -> -e1 -> +e1 -> ...         (L1 membership return, 2 absorptions)
     The sign tracks the global phase accumulated from the non-associative
     product. Ignoring signs gives a spurious period-2 orbit.

  4. TOPOLOGY: 1D periodic loop. Both electrons sit at antipodal nodes on a
     ring of 2*(n_vacuum+1) nodes. Photons travel in one direction; by
     symmetry the two exchange photons arrive at the same tick.

  5. INTERACTION: symmetric. Both electrons emit and absorb simultaneously.
     In each exchange cycle: E1 absorbs E2's photon AND E2 absorbs E1's
     photon. Tick cost per cycle = n_vacuum + 1 (vacuum propagation + 1
     absorption, both particles in parallel).

Observables:
  C_e_L1:    Symmetric exchange cycles until both electrons re-enter L1
             (ignoring sign). C_e_L1 = 2 (analytical; period-2 on L1).
  C_e_exact: Symmetric exchange cycles until both electrons return to their
             EXACT initial signed state. C_e_exact = 4 (analytical; period-4).

  These are algebraically computable without running the simulation; the
  simulation verifies them and measures the tick cost per cycle.

References:
  Furey (2019) arXiv:1910.08395 -- L1 subalgebra, electron = generation-1
  rfc/CONVENTIONS.md -- locked Fano triples; FANO_SIGN, FANO_THIRD
  rfc/RFC-012_QED_Scattering_Graph_Simulation.md -- full spec and orbit definition
  Dixon (1994) arXiv:hep-th/9410202 -- octonion X-product orbit periods (method)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import numpy as np

from calc.conftest import FANO_SIGN, FANO_THIRD, VACUUM_AXIS


# ================================================================
# Constants
# ================================================================

PHOTON_OP: int = VACUUM_AXIS + 1   # state index for e7 (= 7)
"""Photon operator: e7 = vacuum axis, U(1)_EM generator (Furey convention).
VACUUM_AXIS (conftest) = 6 is the 0-indexed Fano point; state index = 7.
"""

L1_ELECTRON_STATE: int = 1
"""Initial state for the generation-1 electron: e1 (state index 1).
e1 is the dominant basis element of the L1 = {e1, e2, e3} quaternionic
associative subalgebra. Products within L1 are associative; the
Alternativity Trigger does NOT fire for L1-only interactions.

Contrast: the earlier (incorrect) choice ELECTRON_STATE = 6 used the
Witt nil-element e6 = alpha_1^dag * omega (the excited/color state).
"""

L1_STATES: frozenset[int] = frozenset({1, 2, 3})
"""State indices for the L1 associative subalgebra {e1, e2, e3}."""

N_TAU: int = 14
"""Triality circuit depth: dim(G_2) = 14 (proved 2026-02-22)."""


# ================================================================
# Signed state
# ================================================================

@dataclass(frozen=True, eq=True)
class SignedState:
    """A signed octonion basis element: sign * e_{index}.

    Tracks the full algebraic phase accumulated under non-associative products.
    Ignoring sign gives a spurious period-2 orbit; the true orbit is period-4.

    index: 0..7  (0 = e0 scalar, 1..7 = e1..e7 imaginary units)
    sign:  +1 or -1
    """
    index: int
    sign: int = +1   # +1 or -1

    def __repr__(self) -> str:
        return f"{'+'if self.sign>0 else '-'}e{self.index}"

    def in_l1(self) -> bool:
        """True iff this state is in the L1 subalgebra {e1, e2, e3} (any sign)."""
        return self.index in L1_STATES


# ================================================================
# Octonion right-multiplication
# ================================================================

def oct_mul_right(state: SignedState, op_idx: int) -> SignedState:
    """Right-multiply state by e_{op_idx}: returns (state) x e_{op_idx}.

    Convention: RIGHT-multiplication matches Gemini's kick description:
        e1 x e7 = +e6    (absorb photon: electron -> excited color state)
        e6 x e7 = -e1    (absorb photon: excited state -> recovered electron)

    For left-multiplication (used in qed_scatter.py) swap arguments.

    The underlying oct_mul_idx(k, j) function computes e_k x e_j using the
    FANO_SIGN / FANO_THIRD tables from the locked Furey convention.
    Right-mult: state x op = oct_mul_idx(state.index, op_idx).

    Special cases:
        e0 x anything  = that thing (scalar is the multiplicative identity)
        anything x e0  = that thing
        e_k x e_k      = -e0  (imaginary units square to -1)
    """
    k, j = state.index, op_idx
    if k == 0:                      # e0 * e_j = e_j
        return SignedState(j, state.sign)
    if j == 0:                      # e_k * e0 = e_k
        return SignedState(k, state.sign)
    if k == j:                      # e_k^2 = -e0
        return SignedState(0, -state.sign)
    fano_k, fano_j = k - 1, j - 1
    result_fano = FANO_THIRD[(fano_k, fano_j)]
    mul_sign    = FANO_SIGN [(fano_k, fano_j)]
    return SignedState(result_fano + 1, state.sign * mul_sign)


# ================================================================
# Single electron orbit
# ================================================================

def electron_orbit(
    initial: SignedState,
    photon_idx: int = PHOTON_OP,
    max_steps: int = 100,
) -> list[SignedState]:
    """Trace the single-particle orbit under repeated right-mult by e_{photon_idx}.

    Returns the orbit trajectory [initial, step1, step2, ...] until the
    state returns to *initial* (exact signed return), or until max_steps.

    The orbit for e1 under e7 is: +e1 -> +e6 -> -e1 -> -e6 -> +e1 (period 4).

    Args:
        initial:    Starting SignedState.
        photon_idx: Index of the applied operator (default: PHOTON_OP = 7 = e7).
        max_steps:  Safety limit.

    Returns:
        List of SignedState including initial and all subsequent states up to
        (and including) the return to initial. Length = orbit_period + 1.
        Returns partial trajectory if period not found within max_steps.
    """
    trajectory = [initial]
    state = initial
    for _ in range(max_steps):
        state = oct_mul_right(state, photon_idx)
        trajectory.append(state)
        if state == initial:
            return trajectory
    return trajectory


def orbit_period_exact(initial: SignedState, photon_idx: int = PHOTON_OP) -> int:
    """Return the exact signed orbit period (steps until state == initial).

    For e1 under e7: returns 4.
    For e6 under e7: returns 4.
    """
    traj = electron_orbit(initial, photon_idx)
    return len(traj) - 1   # last element == initial, don't count it


def orbit_period_l1(initial: SignedState, photon_idx: int = PHOTON_OP) -> int:
    """Return the orbit period for L1 re-membership (index in {1,2,3}).

    Counts steps from *initial* until the state re-enters L1.
    For e1 under e7: initial is in L1, so returns 2 (first re-entry after leaving).
    """
    state = initial
    for step in range(1, 100):
        state = oct_mul_right(state, photon_idx)
        if state.in_l1():
            return step
    return -1


# ================================================================
# Symmetric two-particle exchange
# ================================================================

@dataclass
class TwoParticleState:
    """Joint state of two electrons on a periodic loop.

    e1: SignedState of particle 1.
    e2: SignedState of particle 2.
    n_exchanges: number of symmetric exchange cycles completed.
    tick_cost: total ticks accumulated (n_exchanges * tick_per_cycle).
    """
    p1: SignedState
    p2: SignedState
    n_exchanges: int = 0
    tick_cost: int = 0

    def __repr__(self) -> str:
        return (
            f"TwoParticleState(p1={self.p1}, p2={self.p2}, "
            f"n_exch={self.n_exchanges}, ticks={self.tick_cost})"
        )


def symmetric_exchange_step(
    state: TwoParticleState,
    photon_idx: int = PHOTON_OP,
    n_vacuum: int = 0,
    tick_per_absorption: int = 1,
) -> TwoParticleState:
    """Apply one symmetric exchange cycle to both particles.

    Both particles absorb one photon simultaneously. On the periodic loop,
    the photon emitted by P1 travels through n_vacuum vacuum nodes to reach
    P2, and vice versa. Since both paths have equal length, both photons
    arrive at the same tick.

    Tick cost per cycle = n_vacuum + tick_per_absorption.
      - n_vacuum:             vacuum hops (defines c = 1 hop/tick)
      - tick_per_absorption:  1 for V-rep (electron), 15 for S+-rep (muon)

    Args:
        state:               Current TwoParticleState.
        photon_idx:          Operator index (default: e7).
        n_vacuum:            Number of vacuum nodes between particles.
        tick_per_absorption: Ticks to absorb one photon (rep-type overhead).

    Returns:
        New TwoParticleState with updated signed states and accumulated ticks.
    """
    new_p1 = oct_mul_right(state.p1, photon_idx)
    new_p2 = oct_mul_right(state.p2, photon_idx)
    tick_per_cycle = n_vacuum + tick_per_absorption
    return TwoParticleState(
        p1=new_p1,
        p2=new_p2,
        n_exchanges=state.n_exchanges + 1,
        tick_cost=state.tick_cost + tick_per_cycle,
    )


# ================================================================
# Orbit calibration
# ================================================================

def calibrate_Ce(
    initial_p1: Optional[SignedState] = None,
    initial_p2: Optional[SignedState] = None,
    photon_idx: int = PHOTON_OP,
    n_vacuum: int = 0,
    max_exchanges: int = 1000,
) -> dict:
    """Run the Goal A calibration: find C_e for an L1 electron pair.

    Starts both particles at L1_ELECTRON_STATE (e1, +1) by default.
    Runs symmetric exchange cycles until the joint state returns to
    exactly (initial_p1, initial_p2).

    Key results (analytically known, verified by this function):
      C_e_exact = 4 symmetric exchange cycles for exact signed return.
      C_e_L1    = 2 symmetric exchange cycles for L1 membership return.
      Tick cost per cycle = n_vacuum + 1 (for V-rep electrons).

    Args:
        initial_p1:    Initial state of particle 1 (default: +e1).
        initial_p2:    Initial state of particle 2 (default: +e1).
        photon_idx:    Photon operator index (default: e7 = PHOTON_OP).
        n_vacuum:      Vacuum nodes between particles (affects tick cost).
        max_exchanges: Safety limit.

    Returns:
        dict with:
          'initial_p1', 'initial_p2': initial states
          'trajectory': list of TwoParticleState snapshots (exchange 0..C_e_exact)
          'Ce_exact':   exchange count for exact joint return
          'Ce_L1':      exchange count for both particles to re-enter L1
          'Ce_ticks_exact': total tick cost for exact return
          'Ce_ticks_L1':    total tick cost for L1 return
          'tick_per_cycle': n_vacuum + 1
          'n_vacuum':   n_vacuum
          'photon_idx': photon_idx
    """
    if initial_p1 is None:
        initial_p1 = SignedState(L1_ELECTRON_STATE, +1)
    if initial_p2 is None:
        initial_p2 = SignedState(L1_ELECTRON_STATE, +1)

    current = TwoParticleState(p1=initial_p1, p2=initial_p2)
    trajectory = [current]

    Ce_L1 = None
    Ce_exact = None

    for _ in range(max_exchanges):
        current = symmetric_exchange_step(
            current, photon_idx=photon_idx, n_vacuum=n_vacuum
        )
        trajectory.append(current)

        if Ce_L1 is None and current.p1.in_l1() and current.p2.in_l1():
            Ce_L1 = current.n_exchanges

        if Ce_exact is None and current.p1 == initial_p1 and current.p2 == initial_p2:
            Ce_exact = current.n_exchanges
            break

    tick_per_cycle = n_vacuum + 1
    return {
        'initial_p1': initial_p1,
        'initial_p2': initial_p2,
        'trajectory': trajectory,
        'Ce_exact': Ce_exact if Ce_exact is not None else -1,
        'Ce_L1': Ce_L1 if Ce_L1 is not None else -1,
        'Ce_ticks_exact': Ce_exact * tick_per_cycle if Ce_exact else -1,
        'Ce_ticks_L1': Ce_L1 * tick_per_cycle if Ce_L1 else -1,
        'tick_per_cycle': tick_per_cycle,
        'n_vacuum': n_vacuum,
        'photon_idx': photon_idx,
    }


# ================================================================
# Vacuum-independence check
# ================================================================

def check_vacuum_independence(
    n_vacuum_values: list[int] | None = None,
    photon_idx: int = PHOTON_OP,
) -> dict:
    """Verify that C_e_exact is independent of n_vacuum.

    The orbit count C_e_exact must not depend on the number of vacuum
    nodes (the vacuum hops just add a constant offset to tick cost).
    This confirms that the ratio C_mu/C_e will be well-defined.

    Returns:
        dict with 'Ce_exact_values' (list per n_vacuum), 'all_equal' (bool).
    """
    if n_vacuum_values is None:
        n_vacuum_values = [0, 1, 2, 4, 8, 16]

    Ce_values = []
    for n in n_vacuum_values:
        result = calibrate_Ce(n_vacuum=n, photon_idx=photon_idx)
        Ce_values.append(result['Ce_exact'])

    return {
        'n_vacuum_values': n_vacuum_values,
        'Ce_exact_values': Ce_values,
        'all_equal': len(set(Ce_values)) == 1 and Ce_values[0] > 0,
        'Ce_exact': Ce_values[0] if Ce_values else -1,
    }


# ================================================================
# L1 orbit structure summary
# ================================================================

def l1_orbit_summary(photon_idx: int = PHOTON_OP) -> dict:
    """Summarise the L1 electron orbit structure under e_{photon_idx}.

    For each L1 basis state {e1, e2, e3}, compute:
      - The single-particle signed orbit trajectory
      - The exact orbit period
      - The L1 re-membership period

    Returns a dict keyed by state index.
    """
    summary = {}
    for idx in sorted(L1_STATES):
        initial = SignedState(idx, +1)
        traj = electron_orbit(initial, photon_idx)
        period_exact = orbit_period_exact(initial, photon_idx)
        period_l1 = orbit_period_l1(initial, photon_idx)
        summary[idx] = {
            'initial': initial,
            'trajectory': traj[:-1],   # exclude the return copy
            'period_exact': period_exact,
            'period_l1': period_l1,
            'all_in_l1': all(s.in_l1() for s in traj),
        }
    return summary


# ================================================================
# Main: print calibration report
# ================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("QED Calibration: L1 Electron Orbit (Goal A)")
    print("=" * 60)

    print(f"\nPhoton operator: e{PHOTON_OP}")
    print(f"Electron initial state: e{L1_ELECTRON_STATE} (L1 subalgebra {{e1,e2,e3}})")

    print("\n--- Single-particle kick mechanism ---")
    e1 = SignedState(1, +1)
    e1_after = oct_mul_right(e1, PHOTON_OP)
    e6_after = oct_mul_right(e1_after, PHOTON_OP)
    print(f"  e1 x e7 = {e1_after}  (electron -> excited/color state)")
    print(f"  e6 x e7 = {e6_after}  (de-excitation -> back to L1 with phase flip)")

    print("\n--- Single-particle signed orbit ---")
    orbit = electron_orbit(SignedState(L1_ELECTRON_STATE, +1))
    for i, s in enumerate(orbit):
        marker = " <-- EXACT RETURN" if i > 0 and s == orbit[0] else ""
        print(f"  step {i}: {s}  L1={s.in_l1()}{marker}")

    print(f"\n  period_exact = {orbit_period_exact(SignedState(L1_ELECTRON_STATE,+1))}")
    print(f"  period_L1    = {orbit_period_l1(SignedState(L1_ELECTRON_STATE,+1))}")

    print("\n--- L1 orbit structure for all three L1 states ---")
    summary = l1_orbit_summary()
    for idx, info in summary.items():
        traj_str = " -> ".join(str(s) for s in info['trajectory'])
        print(f"  e{idx}: {traj_str}  (period_exact={info['period_exact']}, period_L1={info['period_l1']})")

    print("\n--- Two-particle calibration (symmetric exchange) ---")
    result = calibrate_Ce(n_vacuum=0)
    print(f"  C_e_exact  = {result['Ce_exact']} exchange cycles")
    print(f"  C_e_L1     = {result['Ce_L1']} exchange cycles")
    print(f"  C_e_ticks (n_vac=0) = {result['Ce_ticks_exact']} ticks (no vacuum)")
    for snap in result['trajectory']:
        print(f"    exch {snap.n_exchanges}: p1={snap.p1} p2={snap.p2}  ticks={snap.tick_cost}")

    print("\n--- Vacuum independence check ---")
    vac_check = check_vacuum_independence()
    for n, ce in zip(vac_check['n_vacuum_values'], vac_check['Ce_exact_values']):
        print(f"  n_vacuum={n:2d}: C_e_exact={ce}")
    print(f"  all_equal = {vac_check['all_equal']}")

    print(f"\n--- Tick cost scaling ---")
    for n in [0, 1, 4, 16]:
        r = calibrate_Ce(n_vacuum=n)
        print(f"  n_vacuum={n:2d}: tick_per_cycle={r['tick_per_cycle']:3d}, "
              f"Ce_ticks_exact={r['Ce_ticks_exact']}")

    print("\nCONCLUSION:")
    print(f"  C_e_exact = {result['Ce_exact']} (independent of n_vacuum)")
    print(f"  Tick cost per cycle = n_vacuum + 1")
    print(f"  Baseline for C_mu/C_e ratio: C_e = {result['Ce_exact']}")
