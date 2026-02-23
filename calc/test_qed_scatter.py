"""calc/test_qed_scatter.py
Tests for RFC-012 QED scattering simulation (calc/qed_scatter.py).

Test groups:
  1. McRae H matrix: algebraic properties (H^3=I, H^T H=I).
  2. oct_mul_idx: Fano-convention octonion basis multiplication.
  3. apply_triality_h: placeholder G2 mapping, fixed points, domain.
  4. update_step: tick costs for V, Sp, and Vac nodes.
  5. propagate_photon: sequential routing, vacuum tick counting.
  6. run_scattering: ee and emu system outputs (key observables from RFC-012).
  7. orbit_return_time: V-rep electron orbit, Sp-rep muon placeholder orbit.
  8. vertex_cost_ratio: 15.0 for N_TAU=14.
  9. Node/Edge dataclasses: construction and field access.
"""

import numpy as np
import pytest

from calc.qed_scatter import (
    N_TAU,
    MCRAE_H,
    PHOTON_OP,
    ELECTRON_STATE,
    MUON_STATE,
    Node,
    Edge,
    oct_mul_idx,
    apply_triality_h,
    update_step,
    propagate_photon,
    run_scattering,
    orbit_return_time,
    vertex_cost_ratio,
    verify_mcrae_h,
)
from calc.conftest import VACUUM_AXIS


# ================================================================
# 1. McRae H matrix
# ================================================================

class TestMcRaeH:
    """Verify properties of the McRae triality quartet matrix."""

    def test_h_is_order_3(self):
        """H^3 = I_4 (order-3 matrix)."""
        H = MCRAE_H
        I4 = np.eye(4)
        assert np.allclose(H @ H @ H, I4, atol=1e-10), (
            "H^3 != I_4; McRae H matrix is not order 3"
        )

    def test_h_is_orthogonal(self):
        """H^T H = I_4 (orthogonal matrix)."""
        H = MCRAE_H
        I4 = np.eye(4)
        assert np.allclose(H.T @ H, I4, atol=1e-10), (
            "H^T H != I_4; McRae H matrix is not orthogonal"
        )

    def test_h_has_half_entries(self):
        """McRae H has entries +-1/2 only (no zeros, no unit entries)."""
        H = MCRAE_H
        for i in range(4):
            for j in range(4):
                assert abs(abs(H[i, j]) - 0.5) < 1e-10, (
                    f"H[{i},{j}] = {H[i,j]} is not +-1/2"
                )

    def test_h_shape(self):
        """H is 4x4."""
        assert MCRAE_H.shape == (4, 4)

    def test_verify_mcrae_h_all_ok(self):
        """verify_mcrae_h() reports all_ok=True."""
        result = verify_mcrae_h()
        assert result['all_ok'], f"verify_mcrae_h failed: {result}"
        assert result['order_3']
        assert result['orthogonal']

    def test_n_tau_value(self):
        """N_TAU = 14 = dim(G_2) as proved by count_circuit_depth_greedy(H)."""
        assert N_TAU == 14

    def test_photon_op_is_e7(self):
        """PHOTON_OP = 7 = state index for e_7 = VACUUM_AXIS + 1."""
        assert PHOTON_OP == 7
        assert PHOTON_OP == VACUUM_AXIS + 1


# ================================================================
# 2. oct_mul_idx: octonion basis multiplication
# ================================================================

class TestOctMulIdx:
    """Verify octonion basis multiplication (locked Furey/Fano convention)."""

    def test_identity_left(self):
        """e_0 * e_j = e_j for all j."""
        for j in range(8):
            result_idx, sign = oct_mul_idx(0, j)
            assert result_idx == j, f"e_0 * e_{j}: expected index {j}, got {result_idx}"
            assert sign == +1

    def test_identity_right(self):
        """e_k * e_0 = e_k for all k."""
        for k in range(8):
            result_idx, sign = oct_mul_idx(k, 0)
            assert result_idx == k, f"e_{k} * e_0: expected index {k}, got {result_idx}"
            assert sign == +1

    def test_imaginary_square_to_neg_e0(self):
        """e_k * e_k = -e_0 for all imaginary units k = 1..7."""
        for k in range(1, 8):
            result_idx, sign = oct_mul_idx(k, k)
            assert result_idx == 0, f"e_{k}^2: expected result e_0 (idx 0), got {result_idx}"
            assert sign == -1, f"e_{k}^2: expected sign -1, got {sign}"

    def test_e7_times_e6_eq_plus_e1(self):
        """e_7 * e_6 = +e_1 (from Fano line (0,6,5): b*c = +a means e7*e6 = +e1).

        Fano line (0,6,5) [0-indexed Fano pts] = (e1, e7, e6) [physics].
        Cyclic rule b*c = +a: e7*e6 = +e1.
        State indices: k=7 (e_7), j=6 (e_6), result=1 (e_1).
        """
        result_idx, sign = oct_mul_idx(7, 6)
        assert result_idx == 1, f"e_7 * e_6: expected e_1 (idx 1), got e_{result_idx}"
        assert sign == +1, f"e_7 * e_6: expected sign +1, got {sign}"

    def test_e7_times_e1_eq_minus_e6(self):
        """e_7 * e_1 = -e_6 (anti-cyclic from Fano line (0,6,5): b*a = -c).

        Anti-cyclic rule b*a = -c: e7*e1 = -e6.
        State indices: k=7 (e_7), j=1 (e_1), result=6 (e_6), sign=-1.
        """
        result_idx, sign = oct_mul_idx(7, 1)
        assert result_idx == 6, f"e_7 * e_1: expected e_6 (idx 6), got e_{result_idx}"
        assert sign == -1, f"e_7 * e_1: expected sign -1, got {sign}"

    def test_e7_times_e5_eq_minus_e2(self):
        """e_7 * e_5 = -e_2 (anti-cyclic from Fano line (1,4,6): c*b = -a).

        Fano line (1,4,6) = (e2, e5, e7). Anti-cyclic c*b = -a: e7*e5 = -e2.
        """
        result_idx, sign = oct_mul_idx(7, 5)
        assert result_idx == 2, f"e_7 * e_5: expected e_2 (idx 2), got e_{result_idx}"
        assert sign == -1

    def test_e7_times_e2_eq_plus_e5(self):
        """e_7 * e_2 = +e_5 (from Fano line (1,4,6): c*a = +b means e7*e2 = +e5)."""
        result_idx, sign = oct_mul_idx(7, 2)
        assert result_idx == 5, f"e_7 * e_2: expected e_5 (idx 5), got e_{result_idx}"
        assert sign == +1

    def test_result_index_in_range(self):
        """All products return result indices in 0..7."""
        for k in range(8):
            for j in range(8):
                result_idx, sign = oct_mul_idx(k, j)
                assert 0 <= result_idx <= 7, (
                    f"oct_mul_idx({k}, {j}) = ({result_idx}, {sign}): "
                    f"result index out of range"
                )

    def test_sign_is_plus_or_minus_one(self):
        """All products return sign in {-1, +1}."""
        for k in range(8):
            for j in range(8):
                _, sign = oct_mul_idx(k, j)
                assert sign in (-1, +1), (
                    f"oct_mul_idx({k}, {j}) sign = {sign}, expected -1 or +1"
                )


# ================================================================
# 3. apply_triality_h
# ================================================================

class TestApplyTrialityH:
    """Verify the placeholder G2 triality translation."""

    def test_e0_is_fixed(self):
        """e_0 is fixed by the G2 automorphism."""
        assert apply_triality_h(0) == 0

    def test_e7_is_fixed(self):
        """e_7 (vacuum axis / photon op) is fixed: apply_triality_h(7) = 7."""
        assert apply_triality_h(7) == 7

    def test_e1_maps_to_e2(self):
        """G2 cycle: e_1 -> e_2."""
        assert apply_triality_h(1) == 2

    def test_e2_maps_to_e4(self):
        """G2 cycle: e_2 -> e_4."""
        assert apply_triality_h(2) == 4

    def test_e4_maps_to_e1(self):
        """G2 cycle: e_4 -> e_1 (closes (1,2,4) 3-cycle)."""
        assert apply_triality_h(4) == 1

    def test_e3_maps_to_e6(self):
        """G2 cycle: e_3 -> e_6."""
        assert apply_triality_h(3) == 6

    def test_e6_maps_to_e5(self):
        """G2 cycle: e_6 -> e_5."""
        assert apply_triality_h(6) == 5

    def test_e5_maps_to_e3(self):
        """G2 cycle: e_5 -> e_3 (closes (3,6,5) 3-cycle)."""
        assert apply_triality_h(5) == 3

    def test_is_bijection_on_0_to_7(self):
        """The G2 mapping is a bijection (permutation) on 0..7."""
        images = [apply_triality_h(i) for i in range(8)]
        assert sorted(images) == list(range(8)), (
            "apply_triality_h is not a bijection: images are not a permutation of 0..7"
        )

    def test_order_3_on_imaginaries(self):
        """Applying the map three times returns to the original for all inputs."""
        for i in range(8):
            assert apply_triality_h(apply_triality_h(apply_triality_h(i))) == i, (
                f"G2 map is not order 3 at index {i}"
            )


# ================================================================
# 4. update_step: core conflict resolver
# ================================================================

class TestUpdateStep:
    """Verify tick costs and state updates in the Conflict Resolver."""

    # --- V node ---

    def test_v_node_absorbs_photon_costs_1_tick(self):
        """V node + photon edge: +1 tick (native XOR, no triality)."""
        node = Node(id=0, rep='V', state=ELECTRON_STATE, tick_cost=0)
        edge = Edge(src=-1, dst=0, op=PHOTON_OP)
        successor = update_step(node, [edge])
        assert successor.tick_cost == 1, (
            f"V node photon absorption: expected 1 tick, got {successor.tick_cost}"
        )

    def test_v_node_photon_updates_state(self):
        """V node (state e_6) absorbs e_7: state -> e_1 (oct_mul_idx(7,6) = (1,+1))."""
        node = Node(id=0, rep='V', state=6, tick_cost=0)
        edge = Edge(src=-1, dst=0, op=7)
        successor = update_step(node, [edge])
        assert successor.state == 1, (
            f"V node e_7 * e_6: expected state 1 (e_1), got {successor.state}"
        )

    def test_v_node_prop_edge_costs_1_tick(self):
        """V node + propagation edge: +1 tick, state unchanged."""
        node = Node(id=0, rep='V', state=3, tick_cost=5)
        prop_edge = Edge(src=-1, dst=0, op=None)
        successor = update_step(node, [prop_edge])
        assert successor.tick_cost == 6
        assert successor.state == 3

    def test_v_node_no_edges(self):
        """V node with no incoming edges: tick_cost unchanged, state unchanged."""
        node = Node(id=0, rep='V', state=2, tick_cost=7)
        successor = update_step(node, [])
        assert successor.tick_cost == 7
        assert successor.state == 2

    # --- Sp node ---

    def test_sp_node_absorbs_photon_costs_15_ticks(self):
        """Sp node + photon edge: +N_TAU+1 = 15 ticks (triality emulation + XOR)."""
        node = Node(id=0, rep='Sp', state=MUON_STATE, tick_cost=0)
        edge = Edge(src=-1, dst=0, op=PHOTON_OP)
        successor = update_step(node, [edge])
        assert successor.tick_cost == N_TAU + 1, (
            f"Sp node photon absorption: expected {N_TAU+1} ticks, "
            f"got {successor.tick_cost}"
        )

    def test_sp_node_absorbs_photon_costs_ntau_plus_1(self):
        """Sp node + photon edge: +n_tau+1 for arbitrary n_tau."""
        node = Node(id=0, rep='Sp', state=MUON_STATE, tick_cost=0)
        edge = Edge(src=-1, dst=0, op=PHOTON_OP)
        for n in (1, 7, 14, 100):
            s = update_step(node, [edge], n_tau=n)
            assert s.tick_cost == n + 1, (
                f"Sp node n_tau={n}: expected {n+1} ticks, got {s.tick_cost}"
            )

    def test_sp_node_photon_updates_state(self):
        """Sp node (state e_5) absorbs e_7 via G2 placeholder: state -> e_2.

        apply_triality_h(7) = 7 (e_7 fixed).
        oct_mul_idx(7, 5) = (2, -1) [e_7*e_5 = -e_2].
        State: 5 -> 2.
        """
        node = Node(id=0, rep='Sp', state=5, tick_cost=0)
        edge = Edge(src=-1, dst=0, op=7)
        successor = update_step(node, [edge])
        assert successor.state == 2, (
            f"Sp node e_7*e_5 (via G2 placeholder): expected state 2, "
            f"got {successor.state}"
        )

    def test_sp_node_prop_edge_costs_1_tick(self):
        """Sp node + propagation edge: +1 tick, state unchanged."""
        node = Node(id=0, rep='Sp', state=5, tick_cost=0)
        prop_edge = Edge(src=-1, dst=0, op=None)
        successor = update_step(node, [prop_edge])
        assert successor.tick_cost == 1
        assert successor.state == 5

    # --- Vac node ---

    def test_vac_node_absorbs_photon_costs_1_tick(self):
        """Vac node + photon edge: +1 tick (e_7 * omega associative; defines c=1)."""
        node = Node(id=0, rep='Vac', state=0, tick_cost=0)
        edge = Edge(src=-1, dst=0, op=PHOTON_OP)
        successor = update_step(node, [edge])
        assert successor.tick_cost == 1, (
            f"Vac node photon absorption: expected 1 tick, got {successor.tick_cost}"
        )

    def test_vac_node_photon_updates_state(self):
        """Vac node (state e_0=0) absorbs e_7: state -> e_7 (oct_mul_idx(7,0)=(7,+1))."""
        node = Node(id=0, rep='Vac', state=0, tick_cost=0)
        edge = Edge(src=-1, dst=0, op=7)
        successor = update_step(node, [edge])
        assert successor.state == 7, (
            f"Vac node e_7*e_0: expected state 7 (e_7), got {successor.state}"
        )

    # --- ID increment ---

    def test_successor_id_incremented(self):
        """Successor node has id = node.id + 1."""
        node = Node(id=5, rep='V', state=1, tick_cost=0)
        edge = Edge(src=4, dst=5, op=PHOTON_OP)
        successor = update_step(node, [edge])
        assert successor.id == 6

    # --- Rep preserved ---

    def test_rep_is_preserved(self):
        """Rep type is unchanged after update."""
        for rep in ('V', 'Sp', 'Vac'):
            node = Node(id=0, rep=rep, state=0, tick_cost=0)
            successor = update_step(node, [])
            assert successor.rep == rep

    # --- Photon before propagation ---

    def test_photon_processed_before_propagation(self):
        """Photon edges are processed before propagation edges.

        A V node (state 6) receiving photon e_7 (state -> 1) and then
        a propagation edge (state unchanged): final state = 1, ticks = 2.
        """
        node = Node(id=0, rep='V', state=6, tick_cost=0)
        photon = Edge(src=-1, dst=0, op=7)
        prop   = Edge(src=-1, dst=0, op=None)
        successor = update_step(node, [prop, photon])   # note: wrong order in list
        assert successor.state == 1, "Photon should be applied before propagation"
        assert successor.tick_cost == 2, "1 (photon) + 1 (prop) = 2 ticks"


# ================================================================
# 5. propagate_photon: sequential routing
# ================================================================

class TestPropagatePhoton:
    """Verify photon routing through a vacuum chain."""

    def _make_chain(self, n_vac: int, p2_rep: str = 'V') -> list[Node]:
        """Build [emitter(V), vac*n, absorber(p2_rep)] with tick_cost=0."""
        chain = [Node(id=0, rep='V', state=ELECTRON_STATE, tick_cost=0)]
        for i in range(n_vac):
            chain.append(Node(id=i + 1, rep='Vac', state=0, tick_cost=0))
        chain.append(Node(id=n_vac + 1, rep=p2_rep, state=ELECTRON_STATE, tick_cost=0))
        return chain

    def test_emitter_is_unchanged(self):
        """The emitter (chain[0]) is not modified by propagate_photon."""
        chain = self._make_chain(2)
        original_state = chain[0].state
        original_ticks = chain[0].tick_cost
        updated, _ = propagate_photon(chain)
        assert updated[0].state == original_state
        assert updated[0].tick_cost == original_ticks

    def test_vacuum_tick_count_equals_n_vac(self):
        """vacuum_tick_cost = number of vacuum nodes in the chain."""
        for n in (0, 1, 2, 4, 8):
            chain = self._make_chain(n)
            _, vac_ticks = propagate_photon(chain)
            assert vac_ticks == n, (
                f"n_vac={n}: expected vacuum_tick_cost={n}, got {vac_ticks}"
            )

    def test_v_absorber_tick_cost_is_1(self):
        """V absorber (chain[-1]) accumulates 1 tick for photon absorption."""
        chain = self._make_chain(3, p2_rep='V')
        updated, _ = propagate_photon(chain)
        absorber = updated[-1]
        assert absorber.tick_cost == 1, (
            f"V absorber: expected 1 tick, got {absorber.tick_cost}"
        )

    def test_sp_absorber_tick_cost_is_n_tau_plus_1(self):
        """Sp absorber accumulates N_TAU+1 ticks for photon absorption."""
        chain = self._make_chain(3, p2_rep='Sp')
        chain[-1] = Node(id=chain[-1].id, rep='Sp', state=MUON_STATE, tick_cost=0)
        updated, _ = propagate_photon(chain)
        absorber = updated[-1]
        assert absorber.tick_cost == N_TAU + 1, (
            f"Sp absorber: expected {N_TAU+1} ticks, got {absorber.tick_cost}"
        )

    def test_updated_chain_length_preserved(self):
        """updated_chain has the same length as the input chain."""
        for n in (0, 1, 3):
            chain = self._make_chain(n)
            updated, _ = propagate_photon(chain)
            assert len(updated) == len(chain)

    def test_zero_vacuum_nodes(self):
        """Chain with no vacuum nodes: photon goes directly from emitter to absorber."""
        chain = self._make_chain(0, p2_rep='V')
        updated, vac_ticks = propagate_photon(chain)
        assert vac_ticks == 0
        assert updated[-1].tick_cost == 1   # absorber: 1 tick

    def test_photon_op_relayed_unchanged(self):
        """The photon operator (e_7) is relayed unchanged through the chain."""
        # Each vacuum node absorbs e_7 and transitions, but the RELAYED op
        # is always photon_op (e_7), not the result of oct_mul.
        chain = self._make_chain(2, p2_rep='V')
        # propagate_photon always passes photon_op=7 to each node -- this is
        # verified implicitly: if each vac costs 1 and absorber costs 1, the
        # op is never altered.
        updated, vac_ticks = propagate_photon(chain, photon_op=7)
        assert vac_ticks == 2
        assert updated[-1].tick_cost == 1


# ================================================================
# 6. run_scattering: key observables (RFC-012 sec 6.5)
# ================================================================

class TestRunScattering:
    """Verify the two-system scattering simulation outputs."""

    # --- System A: ee ---

    def test_ee_vertex_tick_cost_is_1(self):
        """System 'ee': vertex_tick_cost = 1 (V-rep native XOR)."""
        r = run_scattering('ee')
        assert r['vertex_tick_cost'] == 1, (
            f"ee vertex_tick_cost: expected 1, got {r['vertex_tick_cost']}"
        )

    def test_ee_vacuum_tick_cost_equals_n_vacuum(self):
        """System 'ee': vacuum_tick_cost = n_vacuum."""
        for n in (0, 1, 4, 7):
            r = run_scattering('ee', n_vacuum=n)
            assert r['vacuum_tick_cost'] == n, (
                f"ee n_vacuum={n}: expected vacuum_tick_cost={n}, "
                f"got {r['vacuum_tick_cost']}"
            )

    def test_ee_total_tick_cost(self):
        """System 'ee': total_tick_cost = vertex + vacuum = 1 + n."""
        for n in (0, 4):
            r = run_scattering('ee', n_vacuum=n)
            assert r['total_tick_cost'] == 1 + n, (
                f"ee n_vacuum={n}: expected total={1+n}, got {r['total_tick_cost']}"
            )

    def test_ee_particle_reps(self):
        """System 'ee': both particles are V-rep."""
        r = run_scattering('ee')
        assert r['particle1_rep'] == 'V'
        assert r['particle2_rep'] == 'V'

    def test_ee_n_tau_field(self):
        """System 'ee': n_tau field equals N_TAU."""
        r = run_scattering('ee')
        assert r['n_tau'] == N_TAU

    # --- System B: emu ---

    def test_emu_vertex_tick_cost_is_15(self):
        """System 'emu': vertex_tick_cost = N_TAU + 1 = 15 (triality + XOR)."""
        r = run_scattering('emu')
        assert r['vertex_tick_cost'] == N_TAU + 1, (
            f"emu vertex_tick_cost: expected {N_TAU+1}, got {r['vertex_tick_cost']}"
        )

    def test_emu_vertex_tick_cost_is_exactly_15(self):
        """vertex_tick_cost for emu is exactly 15 for N_TAU=14."""
        r = run_scattering('emu', n_tau=14)
        assert r['vertex_tick_cost'] == 15

    def test_emu_vacuum_tick_cost_equals_n_vacuum(self):
        """System 'emu': vacuum_tick_cost = n_vacuum."""
        for n in (0, 1, 4, 10):
            r = run_scattering('emu', n_vacuum=n)
            assert r['vacuum_tick_cost'] == n

    def test_emu_total_tick_cost(self):
        """System 'emu': total_tick_cost = 15 + n_vacuum."""
        for n in (0, 4):
            r = run_scattering('emu', n_vacuum=n)
            assert r['total_tick_cost'] == 15 + n

    def test_emu_particle_reps(self):
        """System 'emu': particle 1 is V-rep, particle 2 is Sp-rep."""
        r = run_scattering('emu')
        assert r['particle1_rep'] == 'V'
        assert r['particle2_rep'] == 'Sp'

    # --- Ratio ---

    def test_vertex_cost_ratio_is_15(self):
        """vertex_tick_cost('emu') / vertex_tick_cost('ee') = 15."""
        r_ee  = run_scattering('ee',  n_vacuum=0)
        r_emu = run_scattering('emu', n_vacuum=0)
        ratio = r_emu['vertex_tick_cost'] / r_ee['vertex_tick_cost']
        assert ratio == pytest.approx(15.0), (
            f"emu/ee vertex cost ratio: expected 15.0, got {ratio}"
        )

    def test_ratio_independent_of_n_vacuum(self):
        """The vertex_tick_cost ratio is independent of n_vacuum.

        Vacuum hops add equally to both systems; they cancel in the ratio
        of VERTEX costs (not total costs).
        """
        for n in (0, 4, 8):
            r_ee  = run_scattering('ee',  n_vacuum=n)
            r_emu = run_scattering('emu', n_vacuum=n)
            ratio = r_emu['vertex_tick_cost'] / r_ee['vertex_tick_cost']
            assert ratio == pytest.approx(15.0), (
                f"n_vacuum={n}: vertex ratio should be 15.0, got {ratio}"
            )

    # --- Return dict structure ---

    def test_run_scattering_returns_dict(self):
        """run_scattering returns a dict with all required keys."""
        required_keys = {
            'system', 'particle1_rep', 'particle2_rep', 'n_vacuum',
            'vertex_tick_cost', 'n_tau', 'vacuum_tick_cost', 'total_tick_cost',
            'particle1_state', 'particle2_state',
        }
        for sys in ('ee', 'emu'):
            r = run_scattering(sys)
            missing = required_keys - set(r.keys())
            assert not missing, f"run_scattering('{sys}') missing keys: {missing}"

    def test_run_scattering_invalid_system_raises(self):
        """run_scattering raises ValueError for unknown system strings."""
        with pytest.raises(ValueError, match="Unknown system"):
            run_scattering('ee-mu')

    # --- State changes ---

    def test_ee_absorber_state_changes_after_photon(self):
        """System 'ee': particle 2 state changes after absorbing e_7.

        Initial state = ELECTRON_STATE = 6 (e_6).
        e_7 * e_6 = +e_1 (state index 1).
        """
        r = run_scattering('ee', n_vacuum=0)
        assert r['particle2_state'] == 1, (
            f"ee absorber: e_7*e_6 should give state 1 (e_1), got {r['particle2_state']}"
        )

    def test_emu_absorber_state_changes_after_photon(self):
        """System 'emu': particle 2 (muon) state changes after photon via placeholder.

        Initial state = MUON_STATE = 5 (e_5).
        apply_triality_h(7) = 7 (e_7 fixed by G2 automorphism).
        e_7 * e_5 = -e_2 (state index 2).
        """
        r = run_scattering('emu', n_vacuum=0)
        assert r['particle2_state'] == 2, (
            f"emu absorber: expected state 2 (e_2), got {r['particle2_state']}"
        )

    def test_emitter_state_is_unchanged(self):
        """Particle 1 (emitter) state is not modified by propagate_photon."""
        r = run_scattering('ee', n_vacuum=4)
        # Emitter (p1) is chain[0] in propagate_photon, which is passed through
        # unchanged. Its state remains ELECTRON_STATE = 6.
        assert r['particle1_state'] == ELECTRON_STATE, (
            f"Emitter state should remain {ELECTRON_STATE}, got {r['particle1_state']}"
        )


# ================================================================
# 7. orbit_return_time
# ================================================================

class TestOrbitReturnTime:
    """Verify orbit return times for V-rep and Sp-rep particles."""

    def test_v_electron_orbit_is_2_ticks(self):
        """V-rep electron (state e_6): orbit return time = 2 ticks.

        Orbit under e_7 photon absorptions:
          e_6 --e_7--> e_1 (1 tick)
          e_1 --e_7--> e_6 (1 tick, returns to start)
        Total: 2 ticks.  C_e = 2.
        """
        C_e = orbit_return_time('V', ELECTRON_STATE)
        assert C_e == 2, f"V-rep electron orbit: expected 2 ticks, got {C_e}"

    def test_sp_muon_orbit_placeholder_is_30_ticks(self):
        """Sp-rep muon (state e_5): orbit return time = 30 ticks (placeholder).

        With G2 placeholder (apply_triality_h(7)=7, fixed):
          e_5 --e_7 via G2--> e_2 (15 ticks: 14 triality + 1 XOR)
          e_2 --e_7 via G2--> e_5 (15 ticks, returns to start)
        Total: 30 ticks.  C_mu (placeholder) = 30.

        NOTE: True C_mu requires 8x8 SO(8) intertwiner (RFC-010 Phase D).
        Target: C_mu/C_e ~ 206.768.  Placeholder gives 30/2 = 15.
        """
        C_mu = orbit_return_time('Sp', MUON_STATE)
        assert C_mu == 30, f"Sp-rep muon orbit (placeholder): expected 30 ticks, got {C_mu}"

    def test_placeholder_orbit_ratio_equals_vertex_cost_ratio(self):
        """Placeholder orbit ratio C_mu/C_e = 15 = vertex_cost_ratio().

        With the G2 placeholder, e_7 is fixed (apply_triality_h(7)=7),
        so the orbit structure is identical for V and Sp; only the tick
        cost per step differs.  True ratio requires the SO(8) intertwiner.
        """
        C_e  = orbit_return_time('V',  ELECTRON_STATE)
        C_mu = orbit_return_time('Sp', MUON_STATE)
        ratio = C_mu / C_e
        expected = vertex_cost_ratio()
        assert ratio == pytest.approx(expected), (
            f"Placeholder C_mu/C_e = {ratio:.3f}, expected {expected:.3f}"
        )

    def test_orbit_returns_positive_integer(self):
        """orbit_return_time returns a positive integer for known orbits."""
        for rep, state in [('V', ELECTRON_STATE), ('Sp', MUON_STATE)]:
            t = orbit_return_time(rep, state)
            assert isinstance(t, int)
            assert t > 0, f"orbit_return_time('{rep}', {state}) = {t}, expected > 0"

    def test_v_orbit_state_6_returns_within_max_steps(self):
        """V-rep electron orbit found within 100 steps (period = 2)."""
        C = orbit_return_time('V', ELECTRON_STATE, max_steps=100)
        assert C != -1, "orbit not found within max_steps"

    def test_orbit_not_found_returns_minus_1(self):
        """orbit_return_time returns -1 if orbit not found within max_steps.

        Use max_steps=1 for a state that needs at least 2 steps.
        """
        C = orbit_return_time('V', ELECTRON_STATE, max_steps=1)
        assert C == -1, (
            f"Expected -1 (orbit not found in 1 step), got {C}"
        )

    def test_v_orbit_alternative_starting_state(self):
        """V-rep particle starting at e_1 also has orbit period 2 under e_7.

        e_1 --e_7--> e_6 (oct_mul_idx(7,1) = (6,-1))
        e_6 --e_7--> e_1 (oct_mul_idx(7,6) = (1,+1))
        """
        C = orbit_return_time('V', initial_state=1)
        assert C == 2


# ================================================================
# 8. vertex_cost_ratio
# ================================================================

class TestVertexCostRatio:
    """Verify the single-vertex cost ratio prediction."""

    def test_default_ratio_is_15(self):
        """vertex_cost_ratio() = 15.0 for N_TAU=14."""
        assert vertex_cost_ratio() == pytest.approx(15.0)

    def test_ratio_is_n_tau_plus_1(self):
        """vertex_cost_ratio(n) = n + 1 for any n."""
        for n in (0, 1, 7, 14, 99):
            assert vertex_cost_ratio(n) == pytest.approx(float(n + 1))

    def test_ratio_for_ntau_14(self):
        """For N_TAU=14: vertex_cost_ratio is a lower bound on m_mu/m_e.

        Single-vertex cost: 15 << 206.768.
        The full ratio C_mu/C_e (target ~206.768) includes orbit recovery.
        This test documents that 15.0 is NOT the muon mass ratio.
        """
        ratio = vertex_cost_ratio(14)
        assert ratio == pytest.approx(15.0)
        # Confirm it is strictly below the experimental value
        M_MU_ME_EXPERIMENTAL = 206.768
        assert ratio < M_MU_ME_EXPERIMENTAL, (
            "vertex_cost_ratio should be < 206.768 (orbit recovery cost needed)"
        )


# ================================================================
# 9. Node and Edge dataclasses
# ================================================================

class TestNodeEdge:
    """Verify Node and Edge dataclass construction and field access."""

    def test_node_default_tick_cost(self):
        """Node.tick_cost defaults to 0."""
        n = Node(id=0, rep='V', state=1)
        assert n.tick_cost == 0

    def test_node_fields(self):
        """Node stores all fields correctly."""
        n = Node(id=42, rep='Sp', state=5, tick_cost=99)
        assert n.id == 42
        assert n.rep == 'Sp'
        assert n.state == 5
        assert n.tick_cost == 99

    def test_vac_node_construction(self):
        """Vac node is constructable with state=0."""
        n = Node(id=0, rep='Vac', state=0, tick_cost=0)
        assert n.rep == 'Vac'
        assert n.state == 0

    def test_edge_photon(self):
        """Edge with op=7 is a photon edge."""
        e = Edge(src=0, dst=1, op=7)
        assert e.op == PHOTON_OP
        assert e.op is not None

    def test_edge_propagation(self):
        """Edge with op=None is a propagation (free) edge."""
        e = Edge(src=0, dst=1, op=None)
        assert e.op is None

    def test_edge_fields(self):
        """Edge stores src, dst, op correctly."""
        e = Edge(src=3, dst=7, op=4)
        assert e.src == 3
        assert e.dst == 7
        assert e.op == 4

    def test_electron_state_constant(self):
        """ELECTRON_STATE = 6 (e_6, first Witt nil-element)."""
        assert ELECTRON_STATE == 6

    def test_muon_state_constant(self):
        """MUON_STATE = 5 (e_5, placeholder for muon state)."""
        assert MUON_STATE == 5
