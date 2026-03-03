"""COG Pseudo-Lorentzian Kernel (v1).

Kernel contract (geometry-independent):
    INPUT  : complete causal past of the target -- any finite sequence of v4
             States from earlier causal ticks.
    RULE   : deterministic canonical-ordered fold under State.__mul__.
    PHYSICS: path-independence of fold product (coherence gate C3).

Pseudo-Lorentzian causal structure:
    Time  : causal tick tau in Z>=0  (separate from State.e)
    Space : C12 phase  p = canonical_phase(g, a) in {0,...,11}
    Past cone of (p_target, tau_target) at depth d:
        { (p_source, tau_source) : tau_source < tau_target
                                   AND d_C12(p_source, p_target) <= tau_target - tau_source }
    where d_C12 = circular distance on Z12  (min(|Dp|, 12-|Dp|)).

    Timelike  : delta_tau >  d_C12   (inside cone)
    Null      : delta_tau == d_C12   (on cone / light-like)
    Spacelike : delta_tau <  d_C12   (outside cone, excluded from past)

Symmetries (gates C1, C2 from KOIDE-KERNEL-CONSTRAINTS-001):
    T3: g -> (g+1)%3   <=>  p -> (p+4)%12   (Z3 generation, 120 deg)
    T4: a -> (a+1)%4   <=>  p -> (p+3)%12   (Z4 energy-phase, 90 deg)
    gcd(4,3) = 1, so T3 and T4 together generate all of Z12.

Phase embedding (gate C2):
    p = (4*g + 3*a) % 12

Equivariance resonance (algebraic):
    State.__mul__ accumulates g and a additively (mod 3 and mod 4).
    Fold of n events shifts g by n*mean_g and a by n*mean_a.
    For uniform shift (T3 or T4 on all inputs):
        T3: fold(T3(past)) == T3(fold(past))  iff  n == 1 (mod 3)
        T4: fold(T4(past)) == T4(fold(past))  iff  n == 1 (mod 4)
        Both: iff  n == 1 (mod 12)  [C12 resonance]
    Physically resonant sizes: 1, 13, 25, 37, ...

Note on geometry:
    This module defines WHAT the kernel computes given a complete past.
    HOW that past is collected (F2^3 cube, Lorentzian cone, oracle)
    is a supplementary concern -- see causal_past_contract_v1.py.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from cog_v3.python.kernel_cog_v4_coherence import State

# ---------------------------------------------------------------------------
# Gate C2: canonical phase embedding
# ---------------------------------------------------------------------------


def canonical_phase(g: int, a: int) -> int:
    """Gate C2: p = (4*g + 3*a) % 12.

    Encodes Z3 generation (120 deg steps) and Z4 energy-phase (90 deg steps)
    into a single C12 phase index.  gcd(4,3)=1 so (g,a) <-> p is surjective.
    """
    return (4 * int(g) + 3 * int(a)) % 12


def phase_of(state: State) -> int:
    """C12 phase of a v4 State under the canonical embedding."""
    return canonical_phase(state.g, state.a)


# ---------------------------------------------------------------------------
# Pseudo-Lorentzian metric on C12
# ---------------------------------------------------------------------------


def d_c12(p1: int, p2: int) -> int:
    """Circular distance on Z12: min(|p1-p2|, 12-|p1-p2|).

    This is the 'spatial distance' in the pseudo-Lorentzian model.
    Range: 0..6.
    """
    diff = abs(int(p1) - int(p2)) % 12
    return min(diff, 12 - diff)


# ---------------------------------------------------------------------------
# Causal event: v4 State + causal time coordinate
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CausalEvent:
    """A v4 State paired with a causal time coordinate tau.

    Attributes
    ----------
    state : v4 State -- carries (g, a, basis, sign, e)
    tau   : causal tick in Z>=0 -- external time, separate from State.e
    """

    state: State
    tau: int

    def __post_init__(self) -> None:
        if int(self.tau) < 0:
            raise ValueError(f"tau must be >= 0, got {self.tau}")
        object.__setattr__(self, "tau", int(self.tau))

    @property
    def phase(self) -> int:
        """C12 phase under canonical embedding."""
        return phase_of(self.state)


# ---------------------------------------------------------------------------
# Pseudo-Lorentzian causal filter
# ---------------------------------------------------------------------------


def is_in_past_cone(source: CausalEvent, target: CausalEvent) -> bool:
    """Return True iff source is inside or on the past light cone of target.

    Lorentzian condition:
        delta_tau > 0                         (strict past)
        d_C12(source.phase, target.phase) <= delta_tau   (inside cone)
    """
    delta_tau = target.tau - source.tau
    if delta_tau <= 0:
        return False
    return d_c12(source.phase, target.phase) <= delta_tau


def causal_separation(source: CausalEvent, target: CausalEvent) -> str:
    """Classify the causal relation of source to target.

    Returns one of: 'timelike', 'null', 'spacelike', 'simultaneous', 'future'
    """
    delta_tau = target.tau - source.tau
    if delta_tau == 0:
        return "simultaneous"
    if delta_tau < 0:
        return "future"
    dp = d_c12(source.phase, target.phase)
    if dp < delta_tau:
        return "timelike"
    if dp == delta_tau:
        return "null"
    return "spacelike"


def causal_past(
    target: CausalEvent,
    pool: Sequence[CausalEvent],
    *,
    max_depth: Optional[int] = None,
) -> List[CausalEvent]:
    """Filter pool to events in the causal past (timelike or null) of target.

    Contract: caller must supply a COMPLETE pool.  This function only filters.

    Args:
        target    : the event whose past we want
        pool      : all candidate past events (caller's responsibility)
        max_depth : if set, restrict to tau in [target.tau - max_depth, target.tau)
    """
    result = []
    for ev in pool:
        if max_depth is not None and (target.tau - ev.tau) > max_depth:
            continue
        if is_in_past_cone(ev, target):
            result.append(ev)
    return result


# ---------------------------------------------------------------------------
# Fold product
# ---------------------------------------------------------------------------

_IDENTITY_STATE = State(g=0, a=0, sign=1, basis=0, e=0)


def canonical_order(events: Sequence[CausalEvent]) -> List[CausalEvent]:
    """Canonical deterministic ordering for the fold.

    Sort key (ascending): (tau, phase, basis, g, a, sign)
    Earlier events fold first; ties broken by internal state lexicographic order.
    """
    return sorted(
        events,
        key=lambda ev: (
            ev.tau, ev.phase, ev.state.basis, ev.state.g, ev.state.a, ev.state.sign
        ),
    )


def fold_product(ordered_events: Sequence[CausalEvent]) -> State:
    """Ordered fold product: identity * state_0 * state_1 * ... * state_{n-1}.

    Returns IDENTITY state (g=0, a=0, basis=0, sign=+1, e=0) for empty input.
    Note: State.e accumulates during the fold; it is NOT reset.
    """
    result = _IDENTITY_STATE
    for ev in ordered_events:
        result = result * ev.state
    return result


# ---------------------------------------------------------------------------
# Core kernel
# ---------------------------------------------------------------------------


def kernel_evolve(
    past: Sequence[CausalEvent],
    target: CausalEvent,
) -> State:
    """Compute the evolved state from the complete causal past.

    Steps:
    1. Apply pseudo-Lorentzian filter (causal_past) to restrict to past cone.
    2. Sort in canonical order.
    3. Compute fold product.

    Contract: caller must supply a COMPLETE past.  The Lorentzian filter
    only excludes events outside the light cone; it does not add missing ones.

    Args:
        past   : all available past events (caller's responsibility for completeness)
        target : the event being evolved (used only for tau and phase filtering)

    Returns:
        evolved State
    """
    cone = causal_past(target, past)
    return fold_product(canonical_order(cone))


# ---------------------------------------------------------------------------
# Gate C3: path independence (coherence check)
# ---------------------------------------------------------------------------


def _state_key(s: State) -> Tuple[int, int, int, int]:
    """Comparison key for States; ignores accumulated energy e."""
    return (s.g, s.a, s.basis, s.sign)


def check_path_independence(
    past: Sequence[CausalEvent],
    *,
    n_permutations: int = 8,
    rng_seed: int = 42,
) -> Tuple[bool, Optional[Tuple[State, State]]]:
    """Gate C3: verify fold product is path-independent.

    Tests canonical order, reverse order, and up to n_permutations random
    orderings.  Returns (True, None) if all agree, (False, (a, b)) on first
    disagreement.

    Note: ignores accumulated State.e in the comparison.
    """
    events = list(past)
    if len(events) <= 1:
        return True, None

    rng = random.Random(rng_seed)

    orderings: List[List[CausalEvent]] = [canonical_order(events)]
    for _ in range(n_permutations - 1):
        shuffled = events[:]
        rng.shuffle(shuffled)
        orderings.append(shuffled)
    orderings.append(list(reversed(canonical_order(events))))

    reference = _state_key(fold_product(orderings[0]))
    for ordering in orderings[1:]:
        result = _state_key(fold_product(ordering))
        if result != reference:
            return False, (fold_product(orderings[0]), fold_product(ordering))

    return True, None


# ---------------------------------------------------------------------------
# Gates C1: T3 and T4 equivariance
# ---------------------------------------------------------------------------


def t3(state: State) -> State:
    """T3: g -> (g+1)%3.  Phase effect: p -> (p+4)%12 (120 deg)."""
    return State(
        g=(state.g + 1) % 3,
        a=state.a,
        sign=state.sign,
        basis=state.basis,
        e=state.e,
    )


def t4(state: State) -> State:
    """T4: a -> (a+1)%4.  Phase effect: p -> (p+3)%12 (90 deg)."""
    return State(
        g=state.g,
        a=(state.a + 1) % 4,
        sign=state.sign,
        basis=state.basis,
        e=state.e,
    )


def _apply_sym(
    sym_fn, events: Sequence[CausalEvent]
) -> List[CausalEvent]:
    """Apply a State-level symmetry to every event, preserving tau."""
    return [CausalEvent(state=sym_fn(ev.state), tau=ev.tau) for ev in events]


def check_t3_equivariance(past: Sequence[CausalEvent]) -> bool:
    """Gate C1: K(T3(past)) == T3(K(past)).

    Compares (g, a, basis, sign); ignores accumulated e.
    Algebraically: holds iff len(past) == 1 (mod 3).
    """
    r_orig = fold_product(canonical_order(past))
    r_t3_in = fold_product(canonical_order(_apply_sym(t3, past)))
    r_t3_out = t3(r_orig)
    return _state_key(r_t3_in) == _state_key(r_t3_out)


def check_t4_equivariance(past: Sequence[CausalEvent]) -> bool:
    """Gate C1: K(T4(past)) == T4(K(past)).

    Algebraically: holds iff len(past) == 1 (mod 4).
    """
    r_orig = fold_product(canonical_order(past))
    r_t4_in = fold_product(canonical_order(_apply_sym(t4, past)))
    r_t4_out = t4(r_orig)
    return _state_key(r_t4_in) == _state_key(r_t4_out)


def equivariance_resonance(n: int) -> Dict[str, bool]:
    """Algebraic equivariance prediction for a past of size n.

    Returns dict with keys: 't3', 't4', 'c12_full'.

    Derivation:
        Fold of n events all shifted by T3 shifts g sum by n.
        T3(fold) shifts g sum by 1.
        Equal iff n == 1 (mod 3).
        Analogously for T4 and a (mod 4), and for both (mod 12).
    """
    return {
        "t3": n % 3 == 1,
        "t4": n % 4 == 1,
        "c12_full": n % 12 == 1,
    }


# ---------------------------------------------------------------------------
# Lorentzian kernel class (main entry point)
# ---------------------------------------------------------------------------


class LorentzianKernel:
    """Pseudo-Lorentzian kernel for the COG model.

    Contract:
        - Geometry/collection of causal past: caller's responsibility.
        - Kernel computes: filter to cone -> canonical fold -> return State.
        - Physicality: path-independence of fold (C3).
        - Symmetry: T3 and T4 equivariance at C12-resonant past sizes (C1).

    Profile ID: 'cog_lorentzian_v1'
    """

    PROFILE = "cog_lorentzian_v1"

    def evolve(
        self,
        past: Sequence[CausalEvent],
        target: CausalEvent,
    ) -> State:
        """Compute next state from complete causal past."""
        return kernel_evolve(past, target)

    def is_coherent(
        self,
        past: Sequence[CausalEvent],
        *,
        n_permutations: int = 8,
    ) -> bool:
        """Gate C3: fold is path-independent."""
        ok, _ = check_path_independence(past, n_permutations=n_permutations)
        return ok

    def gate_status(self, past: Sequence[CausalEvent]) -> Dict[str, object]:
        """Return all gate statuses for the given causal past.

        Keys:
            profile        : kernel profile ID
            past_size      : len(past)
            C1_t3_alg      : T3 equivariance (algebraic prediction)
            C1_t4_alg      : T4 equivariance (algebraic prediction)
            C1_c12_alg     : full C12 equivariance (algebraic)
            C1_t3_empirical: T3 equivariance (computed on this past)
            C1_t4_empirical: T4 equivariance (computed on this past)
            C3_coherent    : path independence (computed on this past)
        """
        n = len(past)
        alg = equivariance_resonance(n)
        return {
            "profile": self.PROFILE,
            "past_size": n,
            "C1_t3_alg": alg["t3"],
            "C1_t4_alg": alg["t4"],
            "C1_c12_alg": alg["c12_full"],
            "C1_t3_empirical": check_t3_equivariance(past),
            "C1_t4_empirical": check_t4_equivariance(past),
            "C3_coherent": self.is_coherent(past),
        }
