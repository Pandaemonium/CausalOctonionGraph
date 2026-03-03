"""Tests for the pseudo-Lorentzian kernel (v1).

Covers:
    Gate C2  -- canonical phase embedding
    Causal   -- d_c12 metric, is_in_past_cone, causal_separation
    Fold     -- identity, associativity, canonical order
    Gate C3  -- path independence (coherence)
    Gate C1  -- T3/T4 equivariance (algebraic resonance + empirical)
    Kernel   -- end-to-end LorentzianKernel.evolve and gate_status
"""

import pytest

from cog_v3.python.kernel_cog_v4_coherence import State
from cog_v3.python.kernel_pseudo_lorentzian_v1 import (
    CausalEvent,
    LorentzianKernel,
    _IDENTITY_STATE,
    _state_key,
    canonical_order,
    canonical_phase,
    causal_past,
    causal_separation,
    check_path_independence,
    check_t3_equivariance,
    check_t4_equivariance,
    d_c12,
    equivariance_resonance,
    fold_product,
    is_in_past_cone,
    kernel_evolve,
    phase_of,
    t3,
    t4,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def s(g: int, a: int, basis: int = 0, sign: int = 1, e: int = 0) -> State:
    """Shorthand State constructor."""
    return State(g=g, a=a, sign=sign, basis=basis, e=e)


def ev(g: int, a: int, tau: int, basis: int = 0, sign: int = 1) -> CausalEvent:
    """Shorthand CausalEvent constructor."""
    return CausalEvent(state=s(g, a, basis=basis, sign=sign), tau=tau)


# ---------------------------------------------------------------------------
# Gate C2: canonical phase embedding
# ---------------------------------------------------------------------------


def test_canonical_phase_vacuum():
    assert canonical_phase(0, 0) == 0


def test_canonical_phase_all_12():
    """All 12 distinct (g,a) combinations hit distinct phases in Z12."""
    phases = set()
    for g in range(3):
        for a in range(4):
            phases.add(canonical_phase(g, a))
    assert phases == set(range(12)), "canonical embedding must cover all 12 phases"


def test_canonical_phase_t3_shift():
    """T3: g -> g+1 shifts phase by +4 mod 12."""
    for g in range(3):
        for a in range(4):
            p0 = canonical_phase(g, a)
            p1 = canonical_phase((g + 1) % 3, a)
            assert (p1 - p0) % 12 == 4


def test_canonical_phase_t4_shift():
    """T4: a -> a+1 shifts phase by +3 mod 12."""
    for g in range(3):
        for a in range(4):
            p0 = canonical_phase(g, a)
            p1 = canonical_phase(g, (a + 1) % 4)
            assert (p1 - p0) % 12 == 3


def test_phase_of_state():
    st = s(1, 2)
    assert phase_of(st) == canonical_phase(1, 2)


# ---------------------------------------------------------------------------
# Pseudo-Lorentzian metric d_C12
# ---------------------------------------------------------------------------


def test_d_c12_zero():
    assert d_c12(0, 0) == 0
    assert d_c12(7, 7) == 0


def test_d_c12_opposite():
    assert d_c12(0, 6) == 6
    assert d_c12(6, 0) == 6


def test_d_c12_adjacent():
    assert d_c12(0, 1) == 1
    assert d_c12(11, 0) == 1


def test_d_c12_half():
    assert d_c12(0, 4) == 4
    assert d_c12(4, 8) == 4
    assert d_c12(8, 0) == 4


def test_d_c12_symmetric():
    for p in range(12):
        for q in range(12):
            assert d_c12(p, q) == d_c12(q, p)


def test_d_c12_triangle_inequality():
    """Circular metric satisfies triangle inequality."""
    for p in range(12):
        for q in range(12):
            for r in range(12):
                assert d_c12(p, r) <= d_c12(p, q) + d_c12(q, r)


# ---------------------------------------------------------------------------
# Causal filter
# ---------------------------------------------------------------------------


def test_is_in_past_cone_direct():
    src = ev(0, 0, tau=0)
    tgt = ev(0, 0, tau=1)
    assert is_in_past_cone(src, tgt)


def test_is_in_past_cone_same_tau_excluded():
    src = ev(0, 0, tau=5)
    tgt = ev(0, 0, tau=5)
    assert not is_in_past_cone(src, tgt)


def test_is_in_past_cone_future_excluded():
    src = ev(0, 0, tau=10)
    tgt = ev(0, 0, tau=5)
    assert not is_in_past_cone(src, tgt)


def test_is_in_past_cone_null():
    """Phase 0 -> phase 4 (d=4) at delta_tau=4 is exactly on the light cone."""
    src = CausalEvent(state=s(0, 0), tau=0)     # phase=0
    tgt = CausalEvent(state=s(1, 0), tau=4)     # phase=4, d_c12(0,4)=4
    assert is_in_past_cone(src, tgt)             # null = on cone, included


def test_is_in_past_cone_spacelike():
    """Phase 0 -> phase 4 (d=4) at delta_tau=3 is spacelike, excluded."""
    src = CausalEvent(state=s(0, 0), tau=0)     # phase=0
    tgt = CausalEvent(state=s(1, 0), tau=3)     # phase=4, d_c12(0,4)=4 > 3
    assert not is_in_past_cone(src, tgt)


def test_causal_separation_types():
    base = CausalEvent(state=s(0, 0), tau=5)
    future = CausalEvent(state=s(0, 0), tau=10)   # delta_tau=5, d=0
    assert causal_separation(future, base) == "future"
    assert causal_separation(base, base) == "simultaneous"
    assert causal_separation(base, future) == "timelike"


def test_causal_past_filters_spacelike():
    target = CausalEvent(state=s(0, 0), tau=5)
    past_ok = CausalEvent(state=s(0, 0), tau=4)        # phase=0, d=0 <= 1: OK
    past_spacelike = CausalEvent(state=s(1, 0), tau=4)  # phase=4, d=4 > 1: excluded
    pool = [past_ok, past_spacelike]
    result = causal_past(target, pool)
    assert past_ok in result
    assert past_spacelike not in result


def test_causal_past_max_depth():
    target = CausalEvent(state=s(0, 0), tau=10)
    deep = CausalEvent(state=s(0, 0), tau=0)    # delta_tau=10
    near = CausalEvent(state=s(0, 0), tau=9)    # delta_tau=1
    pool = [deep, near]
    result = causal_past(target, pool, max_depth=2)
    assert near in result
    assert deep not in result


# ---------------------------------------------------------------------------
# Fold product
# ---------------------------------------------------------------------------


def test_fold_empty():
    result = fold_product([])
    assert _state_key(result) == _state_key(_IDENTITY_STATE)


def test_fold_single():
    ev0 = ev(1, 2, tau=0, basis=3, sign=1)
    result = fold_product([ev0])
    assert _state_key(result) == _state_key(ev0.state)


def test_fold_identity_left():
    """fold([identity, s]) == identity * s == s."""
    ev_id = CausalEvent(state=_IDENTITY_STATE, tau=0)
    ev_s = ev(1, 1, tau=1, basis=2, sign=1)
    result = fold_product([ev_id, ev_s])
    assert _state_key(result) == _state_key(_IDENTITY_STATE * ev_s.state)


def test_fold_two_states():
    e1 = ev(0, 0, tau=0, basis=1, sign=1)
    e2 = ev(0, 0, tau=1, basis=2, sign=1)
    r = fold_product([e1, e2])
    expected = _IDENTITY_STATE * e1.state * e2.state
    assert _state_key(r) == _state_key(expected)


def test_canonical_order_sort():
    """Canonical order is ascending by (tau, phase, basis, g, a, sign)."""
    evts = [
        ev(0, 0, tau=3, basis=0),
        ev(0, 0, tau=1, basis=0),
        ev(0, 0, tau=2, basis=0),
    ]
    ordered = canonical_order(evts)
    taus = [e.tau for e in ordered]
    assert taus == sorted(taus)


# ---------------------------------------------------------------------------
# Gate C3: path independence
# ---------------------------------------------------------------------------


def test_path_independence_empty():
    ok, _ = check_path_independence([])
    assert ok


def test_path_independence_single():
    ok, _ = check_path_independence([ev(0, 0, tau=0)])
    assert ok


def test_path_independence_uniform_seed():
    """Uniform state (all same): fold is independent of order."""
    evts = [ev(1, 1, tau=i, basis=0) for i in range(4)]
    ok, _ = check_path_independence(evts)
    # g accumulates additively, basis=e0 means oct_mul is trivial -> coherent
    # g=1 four times -> g_sum=4%3=1; all orderings give same result
    assert ok


def test_path_independence_identity_seed():
    """All-identity states: fold always returns identity."""
    evts = [CausalEvent(state=_IDENTITY_STATE, tau=i) for i in range(5)]
    ok, _ = check_path_independence(evts)
    assert ok


def test_path_independence_octonion_noncommutative():
    """e1*e2 != e2*e1 for octonions: fold is ORDER-DEPENDENT for basis states."""
    e1 = CausalEvent(state=s(0, 0, basis=1), tau=0)
    e2 = CausalEvent(state=s(0, 0, basis=2), tau=1)
    # With 2 events and different bases, different orderings give different results
    result_12 = fold_product([e1, e2])
    result_21 = fold_product([e2, e1])
    # e1*e2: oct_mul(1,2) = (1,3) -> basis=3; e2*e1: oct_mul(2,1) = (-1,3) -> sign=-1
    # So they differ in sign; path_independence should FAIL
    # (canonical order will pick [e1,e2] by tau, reverse picks [e2,e1])
    assert _state_key(result_12) != _state_key(result_21)
    ok, disagreement = check_path_independence([e1, e2])
    assert not ok
    assert disagreement is not None


# ---------------------------------------------------------------------------
# Gate C1: T3/T4 equivariance
# ---------------------------------------------------------------------------


def test_t3_state():
    st = s(0, 0)
    st3 = t3(st)
    assert st3.g == 1
    assert st3.a == st.a
    assert st3.basis == st.basis


def test_t4_state():
    st = s(0, 0)
    st4 = t4(st)
    assert st4.a == 1
    assert st4.g == st.g
    assert st4.basis == st.basis


def test_t3_orbit():
    """T3 applied three times returns the original state."""
    st = s(1, 2, basis=3, sign=-1)
    assert _state_key(t3(t3(t3(st)))) == _state_key(st)


def test_t4_orbit():
    """T4 applied four times returns the original state."""
    st = s(1, 2, basis=3, sign=-1)
    assert _state_key(t4(t4(t4(t4(st))))) == _state_key(st)


def test_equivariance_resonance_n1():
    """n=1: T3, T4, and C12 full equivariance all hold."""
    r = equivariance_resonance(1)
    assert r["t3"] is True
    assert r["t4"] is True
    assert r["c12_full"] is True


def test_equivariance_resonance_n2():
    r = equivariance_resonance(2)
    assert r["t3"] is False   # 2 != 1 mod 3
    assert r["t4"] is False   # 2 != 1 mod 4
    assert r["c12_full"] is False


def test_equivariance_resonance_n4():
    """n=4: T3 holds (4==1 mod 3), T4 does not (4==0 mod 4)."""
    r = equivariance_resonance(4)
    assert r["t3"] is True
    assert r["t4"] is False


def test_equivariance_resonance_n13():
    """n=13=12+1: both T3 and T4 hold (C12 resonance)."""
    r = equivariance_resonance(13)
    assert r["t3"] is True
    assert r["t4"] is True
    assert r["c12_full"] is True


def test_t3_equivariance_n1_empirical():
    """Single-element past: T3 equivariance always holds."""
    past = [ev(0, 0, tau=0, basis=1)]
    assert check_t3_equivariance(past)


def test_t3_equivariance_n4_empirical():
    """n=4 (1 mod 3): T3 equivariance holds empirically for uniform past."""
    past = [ev(0, 0, tau=i, basis=0) for i in range(4)]
    assert check_t3_equivariance(past)


def test_t3_equivariance_n2_fails():
    """n=2 (2 mod 3): T3 equivariance fails."""
    past = [ev(0, 0, tau=0, basis=0), ev(0, 0, tau=1, basis=0)]
    assert not check_t3_equivariance(past)


def test_t4_equivariance_n1_empirical():
    past = [ev(0, 0, tau=0, basis=0)]
    assert check_t4_equivariance(past)


def test_t4_equivariance_n5_empirical():
    """n=5 (1 mod 4): T4 equivariance holds for uniform past."""
    past = [ev(0, 0, tau=i, basis=0) for i in range(5)]
    assert check_t4_equivariance(past)


def test_t4_equivariance_n2_fails():
    """n=2 (2 mod 4): T4 equivariance fails."""
    past = [ev(0, 0, tau=0, basis=0), ev(0, 0, tau=1, basis=0)]
    assert not check_t4_equivariance(past)


def test_c12_resonance_n13_empirical():
    """n=13: both T3 and T4 equivariance hold empirically (uniform past)."""
    past = [ev(0, 0, tau=i, basis=0) for i in range(13)]
    assert check_t3_equivariance(past)
    assert check_t4_equivariance(past)


# ---------------------------------------------------------------------------
# Lorentzian kernel integration
# ---------------------------------------------------------------------------


def test_kernel_evolve_single_past():
    """Kernel with one past event returns that event's state (times identity)."""
    src = ev(0, 0, tau=0, basis=1)
    tgt = CausalEvent(state=s(0, 0), tau=1)
    result = kernel_evolve([src], tgt)
    assert _state_key(result) == _state_key(src.state)


def test_kernel_evolve_empty_past():
    """Kernel with no past events (none in cone) returns identity."""
    src = CausalEvent(state=s(1, 0), tau=0)    # phase=4
    tgt = CausalEvent(state=s(0, 0), tau=1)    # phase=0, d_c12(4,0)=4 > 1: excluded
    result = kernel_evolve([src], tgt)
    assert _state_key(result) == _state_key(_IDENTITY_STATE)


def test_kernel_evolve_causal_filter():
    """Only events inside the light cone contribute."""
    in_cone = CausalEvent(state=s(0, 0), tau=0)     # phase=0, tgt phase=0, d=0: in cone
    out_cone = CausalEvent(state=s(1, 0), tau=4)     # phase=4, tgt tau=5, d=4=delta_tau: null (in)
    spacelike = CausalEvent(state=s(1, 0), tau=4)    # same but if delta=3 it would be out
    tgt = CausalEvent(state=s(0, 0), tau=5)

    result_all = kernel_evolve([in_cone, spacelike], tgt)
    result_only_in = kernel_evolve([in_cone], tgt)
    # Both spacelike (phase=4, tau=4, tgt_tau=5: d=4 > 1) -> spacelike = excluded
    # So result_all == result_only_in
    spacelike2 = CausalEvent(state=s(1, 0), tau=3)   # d=4 > 2: excluded
    result_with_spacelike = kernel_evolve([in_cone, spacelike2], tgt)
    assert _state_key(result_with_spacelike) == _state_key(result_only_in)


def test_lorentzian_kernel_class():
    kernel = LorentzianKernel()
    assert kernel.PROFILE == "cog_lorentzian_v1"


def test_gate_status_n1():
    kernel = LorentzianKernel()
    past = [ev(0, 0, tau=0)]
    status = kernel.gate_status(past)
    assert status["past_size"] == 1
    assert status["C1_t3_alg"] is True
    assert status["C1_t4_alg"] is True
    assert status["C1_c12_alg"] is True
    assert status["C3_coherent"] is True


def test_gate_status_n13_resonant():
    kernel = LorentzianKernel()
    past = [ev(0, 0, tau=i) for i in range(13)]
    status = kernel.gate_status(past)
    assert status["past_size"] == 13
    assert status["C1_c12_alg"] is True
    assert status["C1_t3_empirical"] is True
    assert status["C1_t4_empirical"] is True


def test_gate_status_coherent_uniform():
    """Uniform-state past is always coherent."""
    kernel = LorentzianKernel()
    past = [ev(0, 0, tau=i, basis=0) for i in range(6)]
    status = kernel.gate_status(past)
    assert status["C3_coherent"] is True


# ---------------------------------------------------------------------------
# Koide orbit phases
# ---------------------------------------------------------------------------


def test_koide_orbit_phases():
    """Z3 orbit {0,4,8} corresponds to g=0,1,2 at a=0."""
    assert canonical_phase(0, 0) == 0
    assert canonical_phase(1, 0) == 4
    assert canonical_phase(2, 0) == 8


def test_koide_orbit_sum_zero():
    """The three Koide orbit phases sum to 0 mod 12."""
    phases = [canonical_phase(g, 0) for g in range(3)]
    assert sum(phases) % 12 == 0


def test_t3_generates_koide_orbit():
    """T3 cycles through the Koide orbit: 0->4->8->0."""
    p0 = canonical_phase(0, 0)   # 0
    p1 = canonical_phase(1, 0)   # 4
    p2 = canonical_phase(2, 0)   # 8
    assert p1 == (p0 + 4) % 12
    assert p2 == (p1 + 4) % 12
    assert p0 == (p2 + 4) % 12
