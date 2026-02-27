"""calc/test_qed_calibration.py
Tests for calc/qed_calibration.py:
  Goal A calibration -- L1 electron orbit under symmetric periodic exchange.

Verifies the kick mechanism, signed orbit, and calibration results:
  - e1 x e7 = +e6    (photon excites electron to Witt partner)
  - e6 x e7 = -e1    (second kick returns to L1 with phase flip)
  - Exact orbit period = 4, L1 membership period = 2
  - C_e_exact = 4 symmetric exchange cycles (vacuum-independent)
  - Witt pair structure: e7 action interconverts each Witt pair
"""

import pytest
import numpy as np

from calc.qed_calibration import (
    PHOTON_OP,
    L1_ELECTRON_STATE,
    L1_STATES,
    SignedState,
    oct_mul_right,
    electron_orbit,
    orbit_period_exact,
    orbit_period_l1,
    symmetric_exchange_step,
    TwoParticleState,
    calibrate_Ce,
    check_vacuum_independence,
    l1_orbit_summary,
)


# ================================================================
# TestSignedState: data structure
# ================================================================

class TestSignedState:
    def test_repr_positive(self):
        assert repr(SignedState(1, +1)) == "+e1"

    def test_repr_negative(self):
        assert repr(SignedState(6, -1)) == "-e6"

    def test_in_l1_true(self):
        for idx in [1, 2, 3]:
            assert SignedState(idx, +1).in_l1()
            assert SignedState(idx, -1).in_l1()

    def test_in_l1_false(self):
        for idx in [0, 4, 5, 6, 7]:
            assert not SignedState(idx, +1).in_l1()

    def test_equality(self):
        assert SignedState(1, +1) == SignedState(1, +1)
        assert SignedState(1, +1) != SignedState(1, -1)
        assert SignedState(1, +1) != SignedState(6, +1)

    def test_frozen(self):
        """SignedState is frozen (hashable, usable as dict key)."""
        s = SignedState(1, +1)
        d = {s: "electron"}
        assert d[SignedState(1, +1)] == "electron"


# ================================================================
# TestKickMechanism: the core algebra
# ================================================================

class TestKickMechanism:
    """Verify Gemini's kick mechanism against the locked Fano convention."""

    def test_e1_absorbs_photon_gives_e6(self):
        """e1 x e7 = +e6  (electron excited to color/Witt-partner state)."""
        result = oct_mul_right(SignedState(1, +1), PHOTON_OP)
        assert result == SignedState(6, +1), f"Got {result}"

    def test_e6_absorbs_photon_gives_minus_e1(self):
        """e6 x e7 = -e1  (de-excitation returns to L1 with phase flip)."""
        result = oct_mul_right(SignedState(6, +1), PHOTON_OP)
        assert result == SignedState(1, -1), f"Got {result}"

    def test_minus_e1_absorbs_photon_gives_minus_e6(self):
        """-e1 x e7 = -e6."""
        result = oct_mul_right(SignedState(1, -1), PHOTON_OP)
        assert result == SignedState(6, -1), f"Got {result}"

    def test_minus_e6_absorbs_photon_gives_plus_e1(self):
        """-e6 x e7 = +e1  (completes the 4-step cycle)."""
        result = oct_mul_right(SignedState(6, -1), PHOTON_OP)
        assert result == SignedState(1, +1), f"Got {result}"

    def test_two_kicks_return_to_l1(self):
        """Two photon absorptions return the state to L1 (with sign flip)."""
        s = SignedState(1, +1)
        s = oct_mul_right(s, PHOTON_OP)
        assert not s.in_l1(), "After 1 kick: should be outside L1"
        s = oct_mul_right(s, PHOTON_OP)
        assert s.in_l1(), "After 2 kicks: should be back in L1"
        assert s == SignedState(1, -1), "Two kicks: +e1 -> -e1"

    def test_four_kicks_exact_return(self):
        """Four photon absorptions give exact signed return."""
        s = SignedState(1, +1)
        for _ in range(4):
            s = oct_mul_right(s, PHOTON_OP)
        assert s == SignedState(1, +1), "After 4 kicks: +e1 -> +e1"

    def test_scalar_e0_identity(self):
        """e0 x anything = that thing (scalar is identity)."""
        for j in range(8):
            result = oct_mul_right(SignedState(0, +1), j)
            assert result.index == j

    def test_self_product_gives_minus_scalar(self):
        """e_k x e_k = -e0 for k != 0."""
        for k in range(1, 8):
            result = oct_mul_right(SignedState(k, +1), k)
            assert result == SignedState(0, -1), f"e{k}^2 should be -e0, got {result}"


# ================================================================
# TestWittPairStructure: e7 interconverts Witt pairs
# ================================================================

class TestWittPairStructure:
    """The photon e7 exactly interconverts the three Witt pairs.

    Witt pairs (from rfc/CONVENTIONS.md): (e1,e6), (e2,e5), (e3,e4).
    Under right-mult by e7:
      e1 -> +e6,  e6 -> -e1  (pair 1)
      e2 -> -e5,  e5 -> +e2? -- let's verify
      e3 -> -e4,  e4 -> +e3? -- let's verify
    """

    def test_e1_maps_to_witt_partner_e6(self):
        assert oct_mul_right(SignedState(1, +1), PHOTON_OP).index == 6

    def test_e6_maps_to_witt_partner_e1(self):
        assert oct_mul_right(SignedState(6, +1), PHOTON_OP).index == 1

    def test_e2_maps_to_witt_partner_e5(self):
        assert oct_mul_right(SignedState(2, +1), PHOTON_OP).index == 5

    def test_e5_maps_to_witt_partner_e2(self):
        assert oct_mul_right(SignedState(5, +1), PHOTON_OP).index == 2

    def test_e3_maps_to_witt_partner_e4(self):
        assert oct_mul_right(SignedState(3, +1), PHOTON_OP).index == 4

    def test_e4_maps_to_witt_partner_e3(self):
        assert oct_mul_right(SignedState(4, +1), PHOTON_OP).index == 3

    def test_e7_maps_to_e0(self):
        """e7 x e7 = -e0 (vacuum axis squares to negative scalar)."""
        result = oct_mul_right(SignedState(7, +1), PHOTON_OP)
        assert result == SignedState(0, -1)

    def test_all_witt_pairs_have_period_4(self):
        """All states in all three Witt pairs have exact orbit period 4."""
        for idx in [1, 2, 3, 4, 5, 6]:
            period = orbit_period_exact(SignedState(idx, +1))
            assert period == 4, f"e{idx} period = {period}, expected 4"


# ================================================================
# TestElectronOrbit: single-particle orbit
# ================================================================

class TestElectronOrbit:
    def test_orbit_length_5(self):
        """electron_orbit returns 5 elements (period-4 plus return)."""
        traj = electron_orbit(SignedState(L1_ELECTRON_STATE, +1))
        assert len(traj) == 5

    def test_orbit_returns_to_initial(self):
        """Last element of orbit == first."""
        initial = SignedState(L1_ELECTRON_STATE, +1)
        traj = electron_orbit(initial)
        assert traj[-1] == initial

    def test_orbit_trajectory_e1(self):
        """Full trajectory for e1: +e1 -> +e6 -> -e1 -> -e6 -> +e1."""
        traj = electron_orbit(SignedState(1, +1))
        expected = [
            SignedState(1, +1),
            SignedState(6, +1),
            SignedState(1, -1),
            SignedState(6, -1),
            SignedState(1, +1),
        ]
        assert traj == expected

    def test_orbit_trajectory_e2(self):
        """Full trajectory for e2: +e2 -> -e5 -> -e2 -> +e5 -> +e2."""
        traj = electron_orbit(SignedState(2, +1))
        expected = [
            SignedState(2, +1),
            SignedState(5, -1),
            SignedState(2, -1),
            SignedState(5, +1),
            SignedState(2, +1),
        ]
        assert traj == expected

    def test_orbit_trajectory_e3(self):
        """Full trajectory for e3: +e3 -> -e4 -> -e3 -> +e4 -> +e3."""
        traj = electron_orbit(SignedState(3, +1))
        expected = [
            SignedState(3, +1),
            SignedState(4, -1),
            SignedState(3, -1),
            SignedState(4, +1),
            SignedState(3, +1),
        ]
        assert traj == expected

    def test_period_exact_is_4(self):
        for idx in L1_STATES:
            assert orbit_period_exact(SignedState(idx, +1)) == 4

    def test_period_l1_is_2(self):
        for idx in L1_STATES:
            assert orbit_period_l1(SignedState(idx, +1)) == 2

    def test_l1_orbit_summary_all_period_4(self):
        summary = l1_orbit_summary()
        for idx, info in summary.items():
            assert info['period_exact'] == 4
            assert info['period_l1'] == 2

    def test_l1_orbit_interleaves_l1_and_witt_partner(self):
        """Orbit alternates between L1 states and non-L1 Witt partners."""
        for idx in L1_STATES:
            traj = electron_orbit(SignedState(idx, +1))[:-1]  # drop return
            for step, state in enumerate(traj):
                if step % 2 == 0:
                    assert state.in_l1(), f"e{idx} step {step} should be in L1"
                else:
                    assert not state.in_l1(), f"e{idx} step {step} should be outside L1"


# ================================================================
# TestSymmetricExchange: two-particle step
# ================================================================

class TestSymmetricExchange:
    def test_both_states_updated(self):
        s = TwoParticleState(SignedState(1, +1), SignedState(1, +1))
        s2 = symmetric_exchange_step(s)
        assert s2.p1 == SignedState(6, +1)
        assert s2.p2 == SignedState(6, +1)

    def test_exchange_count_increments(self):
        s = TwoParticleState(SignedState(1, +1), SignedState(1, +1))
        s2 = symmetric_exchange_step(s)
        assert s2.n_exchanges == 1

    def test_tick_cost_n_vacuum_0(self):
        s = TwoParticleState(SignedState(1, +1), SignedState(1, +1))
        s2 = symmetric_exchange_step(s, n_vacuum=0)
        assert s2.tick_cost == 1

    def test_tick_cost_n_vacuum_4(self):
        s = TwoParticleState(SignedState(1, +1), SignedState(1, +1))
        s2 = symmetric_exchange_step(s, n_vacuum=4)
        assert s2.tick_cost == 5   # n_vacuum + 1 = 5

    def test_independent_initial_states(self):
        """Particles with different initial states evolve independently."""
        s = TwoParticleState(SignedState(1, +1), SignedState(2, +1))
        s2 = symmetric_exchange_step(s)
        assert s2.p1 == SignedState(6, +1)   # e1 -> +e6
        assert s2.p2 == SignedState(5, -1)   # e2 -> -e5


# ================================================================
# TestCalibrateCe: Goal A result
# ================================================================

class TestCalibrateCe:
    def test_Ce_exact_is_4(self):
        result = calibrate_Ce()
        assert result['Ce_exact'] == 4

    def test_Ce_L1_is_2(self):
        result = calibrate_Ce()
        assert result['Ce_L1'] == 2

    def test_Ce_ticks_exact_n_vacuum_0(self):
        """C_e_ticks_exact = 4 * (0+1) = 4 for n_vacuum=0."""
        result = calibrate_Ce(n_vacuum=0)
        assert result['Ce_ticks_exact'] == 4

    def test_Ce_ticks_exact_n_vacuum_4(self):
        """C_e_ticks_exact = 4 * (4+1) = 20 for n_vacuum=4."""
        result = calibrate_Ce(n_vacuum=4)
        assert result['Ce_ticks_exact'] == 20

    def test_trajectory_length(self):
        """Trajectory has Ce_exact + 1 entries (steps 0..Ce_exact)."""
        result = calibrate_Ce()
        assert len(result['trajectory']) == result['Ce_exact'] + 1

    def test_trajectory_final_state_equals_initial(self):
        result = calibrate_Ce()
        traj = result['trajectory']
        assert traj[-1].p1 == result['initial_p1']
        assert traj[-1].p2 == result['initial_p2']

    def test_trajectory_step1_both_at_e6(self):
        """After 1 exchange: both particles at +e6."""
        result = calibrate_Ce()
        step1 = result['trajectory'][1]
        assert step1.p1 == SignedState(6, +1)
        assert step1.p2 == SignedState(6, +1)

    def test_trajectory_step2_both_at_minus_e1(self):
        """After 2 exchanges: both particles at -e1 (in L1, sign flipped)."""
        result = calibrate_Ce()
        step2 = result['trajectory'][2]
        assert step2.p1 == SignedState(1, -1)
        assert step2.p2 == SignedState(1, -1)
        assert step2.p1.in_l1() and step2.p2.in_l1()

    def test_Ce_same_for_all_l1_initial_states(self):
        """C_e_exact = 4 regardless of which L1 state is the initial."""
        for idx in L1_STATES:
            initial = SignedState(idx, +1)
            result = calibrate_Ce(initial_p1=initial, initial_p2=initial)
            assert result['Ce_exact'] == 4, f"e{idx} gave C_e = {result['Ce_exact']}"

    def test_Ce_same_for_mixed_initial_l1_states(self):
        """Two electrons starting at different L1 states still give C_e = 4."""
        result = calibrate_Ce(
            initial_p1=SignedState(1, +1),
            initial_p2=SignedState(2, +1),
        )
        assert result['Ce_exact'] == 4


# ================================================================
# TestVacuumIndependence: C_e is independent of n_vacuum
# ================================================================

class TestVacuumIndependence:
    def test_Ce_exact_independent_of_n_vacuum(self):
        check = check_vacuum_independence()
        assert check['all_equal'], \
            f"C_e_exact varies with n_vacuum: {check}"

    def test_Ce_exact_is_4_across_all_n_vacuum(self):
        check = check_vacuum_independence()
        assert check['Ce_exact'] == 4

    def test_tick_cost_scales_linearly_with_n_vacuum(self):
        """Tick cost = Ce_exact * (n_vacuum + 1): linear in n_vacuum."""
        for n in [0, 1, 2, 4, 8]:
            result = calibrate_Ce(n_vacuum=n)
            expected_ticks = 4 * (n + 1)
            assert result['Ce_ticks_exact'] == expected_ticks, \
                f"n_vacuum={n}: expected {expected_ticks}, got {result['Ce_ticks_exact']}"

    def test_ratio_ce_ticks_n1_over_n0(self):
        """Ratio Ce_ticks(n_vac=1) / Ce_ticks(n_vac=0) = 2 (linear scaling)."""
        r0 = calibrate_Ce(n_vacuum=0)
        r1 = calibrate_Ce(n_vacuum=1)
        assert r1['Ce_ticks_exact'] == 2 * r0['Ce_ticks_exact']
