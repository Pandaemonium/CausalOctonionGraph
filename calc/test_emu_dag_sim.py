"""calc/test_emu_dag_sim.py

25 tests for the E-Mu DAG timing simulation (calc/emu_dag_sim.py).

Test plan:
  1-4  : Module constants (N_TAU, VERTEX_COST_ELECTRON, VERTEX_COST_MUON, relationship)
  5-7  : Vertex cost ratio and gap to experimental mass ratio
  8-10 : Algebraic orbit periods (Universal C_e = 4 theorem)
  11-19: simulate_emu(D=0) — absorption ticks, orbit times, state returns
  20-22: simulate_emu(D=1) — absorption ticks, counts, state returns
  23-24: Custom initial states (full Furey electron and dual-sector muon states)
  25   : e-e baseline reference (Ce_exact = 4 from qed_ee_sim)

Key verified values (D=0, both initial states = E1):
  E absorption ticks:  [1, 17, 32, 47]
  Mu absorption ticks: [1, 16, 31, 46]
  vertex_cost_ratio = 15   (lower bound on m_mu/m_e)
  gap_to_experimental ~ 13.8x
"""

import numpy as np
import pytest

from calc.emu_dag_sim import (
    N_TAU,
    VERTEX_COST_ELECTRON,
    VERTEX_COST_MUON,
    EXPERIMENTAL_MASS_RATIO,
    simulate_emu,
)
from calc.furey_electron_orbit import (
    compute_orbit_period,
    furey_electron_state,
    furey_dual_electron_state,
    OMEGA_DAG,
)
from calc.qed_ee_sim import E1, OMEGA, simulate_ee

TOL = 1e-10


# ================================================================
# 1. Module constants
# ================================================================

class TestConstants:

    def test_n_tau_equals_14(self):
        """N_TAU = 14 = dim(G_2), proved by triality circuit depth."""
        assert N_TAU == 14

    def test_vertex_cost_electron_equals_1(self):
        """VERTEX_COST_ELECTRON = 1 tick (native V-rep photon absorption)."""
        assert VERTEX_COST_ELECTRON == 1

    def test_vertex_cost_muon_equals_15(self):
        """VERTEX_COST_MUON = 15 ticks (N_TAU + 1)."""
        assert VERTEX_COST_MUON == 15

    def test_muon_cost_equals_n_tau_plus_1(self):
        """VERTEX_COST_MUON = N_TAU + 1: one absorption tick plus triality overhead."""
        assert VERTEX_COST_MUON == N_TAU + 1


# ================================================================
# 2. Vertex cost ratio and gap to experimental
# ================================================================

class TestVertexCostRatio:

    def test_vertex_cost_ratio_equals_15(self):
        """Muon-to-electron vertex cost ratio = 15."""
        r = simulate_emu(D=0)
        assert r['vertex_cost_ratio'] == 15.0

    def test_vertex_cost_ratio_lt_experimental(self):
        """vertex_cost_ratio = 15 < 206.768: lower bound on m_mu/m_e confirmed."""
        r = simulate_emu(D=0)
        assert r['vertex_cost_ratio'] < EXPERIMENTAL_MASS_RATIO

    def test_gap_to_experimental_approx_13_8(self):
        """Gap factor = 206.768 / 15 ~ 13.8 (mechanism partially open)."""
        r = simulate_emu(D=0)
        gap = r['gap_to_experimental']
        assert abs(gap - EXPERIMENTAL_MASS_RATIO / 15.0) < 1e-6
        assert 13.0 < gap < 15.0   # approximately 13.78


# ================================================================
# 3. Algebraic orbit periods (Universal C_e = 4 theorem)
# ================================================================

class TestAlgebraicOrbits:

    def test_electron_state_orbit_period_4(self):
        """L_{e7}^4(e1) = e1: electron algebraic period = 4."""
        assert compute_orbit_period(E1) == 4

    def test_muon_state_orbit_period_4(self):
        """L_{e7}^4(omega_dag) = omega_dag: dual-sector state also period 4."""
        assert compute_orbit_period(OMEGA_DAG) == 4

    def test_various_states_period_4(self):
        """Universal C_e = 4: period is 4 for all non-zero states tested."""
        states = [
            E1,
            OMEGA,
            OMEGA_DAG,
            furey_electron_state(),
            furey_dual_electron_state(),
        ]
        for i, s in enumerate(states):
            assert compute_orbit_period(s) == 4, f"State {i} has period != 4"


# ================================================================
# 4. simulate_emu(D=0): absorption ticks
# ================================================================

class TestSimulateEmuD0AbsTicks:

    def setup_method(self):
        self.r = simulate_emu(D=0)

    def test_e_abs_count_equals_4(self):
        """Electron makes exactly 4 absorptions in D=0 e-mu simulation."""
        assert self.r['e_abs_count'] == 4

    def test_mu_abs_count_equals_4(self):
        """Muon makes exactly 4 absorptions in D=0 e-mu simulation."""
        assert self.r['mu_abs_count'] == 4

    def test_e_abs_ticks_D0(self):
        """Electron absorption ticks for D=0: [1, 17, 32, 47].

        Inter-absorption gaps: first gap = D+16 = 16; subsequent = 15 (= V_mu).
        """
        assert self.r['e_abs_ticks'] == [1, 17, 32, 47]

    def test_mu_abs_ticks_D0(self):
        """Muon absorption ticks for D=0: [1, 16, 31, 46].

        Muon absorbs every V_mu = 15 ticks after the first absorption.
        Queued-photon model: each re-emitted photon is absorbed as soon as
        the muon finishes the previous vertex.
        """
        assert self.r['mu_abs_ticks'] == [1, 16, 31, 46]


# ================================================================
# 5. simulate_emu(D=0): orbit times and ratios
# ================================================================

class TestSimulateEmuD0Timing:

    def setup_method(self):
        self.r = simulate_emu(D=0)

    def test_e_orbit_time_equals_47(self):
        """Electron orbit time for D=0: 47 ticks (4th absorption at t=47)."""
        assert self.r['e_orbit_time'] == 47

    def test_mu_orbit_time_equals_46(self):
        """Muon orbit time for D=0: 46 ticks (4th absorption at t=46)."""
        assert self.r['mu_orbit_time'] == 46

    def test_max_orbit_time_equals_47(self):
        """Joint system orbit time = max(47, 46) = 47 ticks."""
        assert self.r['max_orbit_time'] == 47

    def test_ee_baseline_equals_4(self):
        """e-e baseline for D=0: 4 ticks (Ce_exact=4, tick_per_cycle=1)."""
        assert self.r['ee_baseline_ticks'] == 4

    def test_timing_ratio_e(self):
        """Electron timing ratio for D=0: 47/4 = 11.75."""
        assert abs(self.r['timing_ratio_e'] - 47.0 / 4.0) < 1e-9

    def test_timing_ratio_mu(self):
        """Muon timing ratio for D=0: 46/4 = 11.5."""
        assert abs(self.r['timing_ratio_mu'] - 46.0 / 4.0) < 1e-9


# ================================================================
# 6. simulate_emu(D=0): state returns
# ================================================================

class TestSimulateEmuD0StateReturn:

    def setup_method(self):
        self.r = simulate_emu(D=0)

    def test_electron_returns_to_initial(self):
        """Electron state matches initial state after 4 absorptions."""
        assert self.r['e_at_initial']

    def test_muon_returns_to_initial(self):
        """Muon state matches initial state after 4 absorptions."""
        assert self.r['mu_at_initial']

    def test_hop_equals_1_for_D0(self):
        """hop = D + 1 = 1 for D=0."""
        assert self.r['hop'] == 1


# ================================================================
# 7. simulate_emu(D=1)
# ================================================================

class TestSimulateEmuD1:

    def setup_method(self):
        self.r = simulate_emu(D=1)

    def test_D1_abs_counts_equal_4(self):
        """Both particles make exactly 4 absorptions for D=1."""
        assert self.r['e_abs_count'] == 4
        assert self.r['mu_abs_count'] == 4

    def test_D1_e_abs_ticks(self):
        """Electron absorption ticks for D=1: [2, 19, 34, 49]."""
        assert self.r['e_abs_ticks'] == [2, 19, 34, 49]

    def test_D1_mu_abs_ticks(self):
        """Muon absorption ticks for D=1: [2, 17, 32, 47]."""
        assert self.r['mu_abs_ticks'] == [2, 17, 32, 47]

    def test_D1_both_at_initial(self):
        """Both particles return to their initial states for D=1."""
        assert self.r['e_at_initial']
        assert self.r['mu_at_initial']


# ================================================================
# 8. Custom initial states (Furey electron and muon)
# ================================================================

class TestCustomInitialStates:

    def test_furey_electron_state_returns_to_initial(self):
        """simulate_emu with full Furey electron state (-i*omega_dag) as electron.

        The algebraic orbit still closes in 4 absorptions (Universal C_e = 4).
        """
        psi_e = furey_electron_state()   # = -i * omega_dag
        r = simulate_emu(D=0, electron_state=psi_e)
        assert r['e_abs_count'] == 4
        assert r['e_at_initial']

    def test_furey_dual_electron_state_returns_to_initial(self):
        """simulate_emu with dual-sector state (-i*omega) as muon.

        The muon algebraic orbit also closes in 4 absorptions regardless of
        which non-zero state is chosen (Universal C_e = 4 theorem).
        """
        psi_mu = furey_dual_electron_state()   # = -i * omega
        r = simulate_emu(D=0, muon_state=psi_mu)
        assert r['mu_abs_count'] == 4
        assert r['mu_at_initial']


# ================================================================
# 9. e-e baseline reference
# ================================================================

class TestEEBaseline:

    def test_ee_baseline_Ce_exact_equals_4(self):
        """e-e simulation (qed_ee_sim) gives Ce_exact = 4 for D=0.

        This is the reference against which the e-mu timing ratio is computed.
        Ce_exact = 4 from the e-e baseline is consistent with VERTEX_COST_ELECTRON = 1:
          total_ticks (e-e, D=0) = Ce_exact * (D+1) = 4 * 1 = 4 = ee_baseline_ticks.
        """
        ee = simulate_ee(D=0)
        assert ee['Ce_exact'] == 4
        r_emu = simulate_emu(D=0)
        assert r_emu['ee_baseline_ticks'] == ee['total_ticks']
