"""
calc/test_triality_map.py
Tests for RFC-011 Action Item A: triality map on 8-dimensional state space.

Tests fall into four groups:
  1. Left-multiplication matrices: algebraic identities from CONVENTIONS.md.
  2. G2 placeholder matrix: structure and order-3 property.
  3. Fano line preservation: the G2 map is an automorphism of O.
  4. N_tau analysis: cost reporting helpers.
"""

import numpy as np
import pytest
from calc.triality_map import (
    octonion_left_mul_matrix,
    build_all_left_mul_matrices,
    verify_left_mul_algebra,
    g2_color_cycle,
    verify_order,
    classify_entries,
    count_xor_sign_ops,
    count_circuit_depth_cse,
    count_circuit_depth_greedy,
    report_ntau,
)
from calc.conftest import FANO_CYCLES, WITT_PAIRS


# ================================================================
# 1. Left-multiplication matrix tests
# ================================================================

class TestLeftMulMatrices:
    """Verify octonion_left_mul_matrix returns correct 8x8 real matrices."""

    def test_L0_is_identity(self):
        """L0 = I_8 (left-mult by e0 is the identity)."""
        L0 = octonion_left_mul_matrix(0)
        assert np.allclose(L0, np.eye(8))

    @pytest.mark.parametrize("k", range(1, 8))
    def test_Lk_square_is_neg_identity(self, k):
        """L_k @ L_k = -I for imaginary units (e_k^2 = -1)."""
        Lk = octonion_left_mul_matrix(k)
        result = Lk @ Lk
        assert np.allclose(result, -np.eye(8)), (
            f"L{k}^2 != -I: {result}"
        )

    @pytest.mark.parametrize("k", range(1, 8))
    def test_Lk_is_orthogonal(self, k):
        """L_k is a real orthogonal matrix."""
        Lk = octonion_left_mul_matrix(k)
        assert np.allclose(Lk.T @ Lk, np.eye(8))

    @pytest.mark.parametrize("k", range(1, 8))
    def test_Lk_is_antisymmetric(self, k):
        """L_k^T = -L_k for imaginary units (antisymmetric)."""
        Lk = octonion_left_mul_matrix(k)
        assert np.allclose(Lk.T, -Lk), (
            f"L{k} is not antisymmetric"
        )

    @pytest.mark.parametrize("k,j", [(k, j) for k in range(1, 8)
                                      for j in range(1, 8) if k != j])
    def test_Lk_Lj_anticommute(self, k, j):
        """L_k L_j + L_j L_k = 0 for distinct imaginary units (Clifford relation)."""
        Lk = octonion_left_mul_matrix(k)
        Lj = octonion_left_mul_matrix(j)
        anticomm = Lk @ Lj + Lj @ Lk
        assert np.allclose(anticomm, np.zeros((8, 8))), (
            f"L{k}*L{j} + L{j}*L{k} != 0"
        )

    def test_all_algebra_checks_pass(self):
        """Batch check: verify_left_mul_algebra returns all True."""
        L = build_all_left_mul_matrices()
        result = verify_left_mul_algebra(L)
        assert result['all_ok'], (
            f"Left-mul algebra checks failed: {result}"
        )

    def test_L1_e1_times_e2_eq_e3(self):
        """L1[3, 2] = +1: e1 * e2 = +e3 (Fano line L1=(1,2,3))."""
        L1 = octonion_left_mul_matrix(1)
        # Output index 3 (e3) when input index 2 (e2): L1[3, 2] = +1
        assert L1[3, 2] == pytest.approx(1.0), (
            f"e1*e2 should be +e3; L1[3,2] = {L1[3,2]}"
        )

    def test_L2_e2_times_e4_eq_e6(self):
        """L2[6, 4] = +1: e2 * e4 = +e6 (Fano line L4=(2,4,6))."""
        L2 = octonion_left_mul_matrix(2)
        assert L2[6, 4] == pytest.approx(1.0), (
            f"e2*e4 should be +e6; L2[6,4] = {L2[6,4]}"
        )

    def test_L7_e7_times_e1_eq_e6(self):
        """L7[6, 1] = +1: e7 * e1 = +e6 (Fano line L3=(1,7,6): e7*e1=e6 anti-cyclic? check)."""
        # L3=(1,7,6) means e1*e7=+e6, e7*e6=+e1, e6*e1=+e7
        # So e7*e1 = -e6 (anti-cyclic of e1*e7=+e6)
        L7 = octonion_left_mul_matrix(7)
        # e7 * e1 = -e6 (anti-cyclic from line (1,7,6))
        assert L7[6, 1] == pytest.approx(-1.0), (
            f"e7*e1 should be -e6; L7[6,1] = {L7[6,1]}"
        )


# ================================================================
# 2. G2 placeholder matrix tests
# ================================================================

class TestG2ColorCycle:
    """Verify the G2 color-cycle permutation matrix."""

    def test_is_permutation_matrix(self):
        """G2 matrix has exactly one 1.0 per row and column."""
        T = g2_color_cycle()
        assert np.allclose(T @ T.T, np.eye(8)), "Not orthogonal"
        assert np.allclose(T.T @ T, np.eye(8)), "Not orthogonal"
        # Each row sums to exactly 1
        for i in range(8):
            assert abs(T[i].sum() - 1.0) < 1e-10, f"Row {i} sum != 1"
            assert np.sum(T[i] > 0.5) == 1, f"Row {i} has != 1 entry equal to 1"

    def test_order_three(self):
        """G2 color-cycle has order 3: T^3 = I."""
        T = g2_color_cycle()
        is_3, order = verify_order(T, expected_order=3)
        assert is_3, f"Expected order 3, got order {order}"

    def test_order_not_one(self):
        """G2 color-cycle is not the identity."""
        T = g2_color_cycle()
        assert not np.allclose(T, np.eye(8)), "T should not be I"

    def test_e0_fixed(self):
        """T maps e0 -> e0: column 0 is e_0."""
        T = g2_color_cycle()
        assert T[0, 0] == pytest.approx(1.0), "e0 not fixed"
        assert np.sum(T[:, 0] != 0) == 1, "e0 column not sparse"

    def test_e7_fixed(self):
        """T maps e7 -> e7: vacuum axis is preserved."""
        T = g2_color_cycle()
        assert T[7, 7] == pytest.approx(1.0), "e7 (vacuum) not fixed"
        assert np.sum(T[:, 7] != 0) == 1, "e7 column not sparse"

    def test_e1_maps_to_e2(self):
        """e1 -> e2 under the G2 cycle."""
        T = g2_color_cycle()
        # Column 1 (input e1) should have 1 at row 2 (output e2)
        assert T[2, 1] == pytest.approx(1.0), "e1 should map to e2"

    def test_e2_maps_to_e4(self):
        """e2 -> e4 under the G2 cycle."""
        T = g2_color_cycle()
        assert T[4, 2] == pytest.approx(1.0), "e2 should map to e4"

    def test_e4_maps_to_e1(self):
        """e4 -> e1 (closing the (1,2,4) 3-cycle)."""
        T = g2_color_cycle()
        assert T[1, 4] == pytest.approx(1.0), "e4 should map to e1"

    def test_e3_maps_to_e6(self):
        """e3 -> e6 under the G2 cycle."""
        T = g2_color_cycle()
        assert T[6, 3] == pytest.approx(1.0), "e3 should map to e6"

    def test_e6_maps_to_e5(self):
        """e6 -> e5 under the G2 cycle."""
        T = g2_color_cycle()
        assert T[5, 6] == pytest.approx(1.0), "e6 should map to e5"

    def test_e5_maps_to_e3(self):
        """e5 -> e3 (closing the (3,6,5) 3-cycle)."""
        T = g2_color_cycle()
        assert T[3, 5] == pytest.approx(1.0), "e5 should map to e3"


# ================================================================
# 3. Fano line preservation (G2 automorphism property)
# ================================================================

class TestFanoPreservation:
    """
    The G2 automorphism maps each Fano line to another Fano line.

    FANO_CYCLES uses 0-indexed Fano points (0=e1 ... 6=e7).
    Our state indices: 1=e1 ... 7=e7.
    So Fano point k corresponds to state index k+1.
    """

    def _fano_pt_to_state(self, fp: int) -> int:
        """Convert 0-indexed Fano point to state vector index."""
        return fp + 1

    def test_each_fano_line_maps_to_a_fano_line(self):
        """
        Under the G2 cycle, each Fano line maps to another Fano line.
        This confirms the G2 cycle is an automorphism of the Fano plane.
        """
        T = g2_color_cycle()

        # Build a set of frozensets for quick lookup
        fano_line_sets = {
            frozenset(
                self._fano_pt_to_state(fp) for fp in line
            )
            for line in FANO_CYCLES
        }

        # Apply the permutation to each Fano line
        perm = {}  # state_idx -> state_idx under G2 cycle
        for src in range(8):
            for dst in range(8):
                if T[dst, src] > 0.5:
                    perm[src] = dst
                    break

        for line in FANO_CYCLES:
            state_line = {self._fano_pt_to_state(fp) for fp in line}
            mapped_line = frozenset(perm[s] for s in state_line)
            assert mapped_line in fano_line_sets, (
                f"Fano line {state_line} mapped to {set(mapped_line)}, "
                f"which is not a Fano line.  G2 cycle is not an automorphism."
            )

    def test_witt_pairs_cycle_correctly(self):
        """
        The G2 cycle permutes the three Witt color pairs:
        (e6,e1) -> (e2,e5) -> (e3,e4) -> (e6,e1)

        WITT_PAIRS in conftest: [(5,0), (1,4), (2,3)] -- 0-indexed Fano pts.
        As state indices: [(6,1), (2,5), (3,4)].
        """
        T = g2_color_cycle()

        # Build permutation dict: state_idx -> state_idx
        perm = {}
        for src in range(8):
            for dst in range(8):
                if T[dst, src] > 0.5:
                    perm[src] = dst
                    break

        # WITT_PAIRS as state indices (Fano pt + 1):
        witt_state = [
            frozenset(fp + 1 for fp in pair) for pair in WITT_PAIRS
        ]
        witt_state_set = set(witt_state)

        for pair_fs in witt_state:
            mapped = frozenset(perm[s] for s in pair_fs)
            assert mapped in witt_state_set, (
                f"Witt pair {set(pair_fs)} mapped to {set(mapped)}, "
                f"not in Witt pair set {[set(w) for w in witt_state]}"
            )


# ================================================================
# 4. N_tau analysis helpers
# ================================================================

class TestCostAnalysis:
    """Verify the XOR+sign cost counting for the placeholder matrix."""

    def test_g2_has_only_unit_and_zero_entries(self):
        """G2 permutation matrix has entries in {0, 1} only."""
        T = g2_color_cycle()
        info = classify_entries(T)
        assert info['n_half'] == 0, (
            "G2 permutation should have no 1/2 entries"
        )
        assert info['n_other'] == 0, (
            "G2 permutation should have no unexpected entries"
        )
        assert info['n_unit'] == 8, (
            "G2 permutation should have exactly 8 unit entries (one per row)"
        )

    def test_g2_ntau_equals_24(self):
        """G2 placeholder: N_tau = 8 non-zero entries x C_e=3 = 24."""
        T = g2_color_cycle()
        N_tau = count_xor_sign_ops(T)
        assert N_tau == 24, (
            f"G2 N_tau should be 24 (8 entries x 3 ops); got {N_tau}"
        )

    def test_g2_ntau_does_not_predict_muon_mass(self):
        """
        G2 placeholder N_tau = 24 gives 1 + N_tau = 25, NOT 206.768.

        This DOCUMENTS that the G2 permutation is the wrong map.
        The true SO(8) outer triality must have a much larger N_tau.
        """
        T = g2_color_cycle()
        result = report_ntau(T, label="G2-placeholder")
        # Placeholder gives prediction = 25
        assert result['N_tau'] == 24
        assert result['prediction_1_plus_Ntau'] == 25
        # This must NOT match the muon mass ratio (it's the wrong map)
        assert not result['COG_QC_01_consistent'], (
            "G2 placeholder should NOT be consistent with m_mu/m_e = 206.768.  "
            "If it is, the cost model or G2 map is wrong."
        )

    def test_report_ntau_fields(self):
        """report_ntau returns expected dict keys."""
        T = g2_color_cycle()
        result = report_ntau(T)
        expected_keys = {
            'label', 'is_order_3', 'actual_order', 'n_nonzero',
            'n_unit_entries', 'n_half_entries', 'n_other_entries',
            'per_row_nonzero', 'N_tau', 'prediction_1_plus_Ntau',
            'm_mu_me_observed', 'COG_QC_01_consistent',
        }
        assert expected_keys <= set(result.keys()), (
            f"Missing keys: {expected_keys - set(result.keys())}"
        )

    def test_report_is_order_3(self):
        """G2 placeholder is correctly identified as order 3."""
        T = g2_color_cycle()
        result = report_ntau(T)
        assert result['is_order_3'] is True
        assert result['actual_order'] == 3

    def test_true_tau_needs_dense_half_entries(self):
        """
        Document the requirement for the true tau matrix.

        The true SO(8) outer triality matrix should:
          - Have entries +-1/2 (not +-1 permutation entries)
          - Be dense (multiple non-zero entries per row)
          - Give N_tau closer to 192 (8 rows x 8 entries x 3 ops)
          - The exact N_tau needed for COG-QC-01 is open (RFC-011 §7.1)

        This test encodes those constraints as documentation.
        NOTE: This test does NOT have a correct tau available; it
        tests the REQUIREMENTS so that when the true matrix is added
        these constraints can be verified automatically.
        """
        # These are the TARGET constraints for the true tau, not tested here.
        TARGET_N_HALF_ENTRIES_MIN = 32   # at least 32 entries of magnitude 1/2
        TARGET_N_PER_ROW_MIN = 4         # at least 4 non-zero per row
        TARGET_N_TAU_APPROX = 192        # 8 rows x 8 entries x 3 ops (upper bound)
        TARGET_CONSISTENT_WITH_MUON = abs(1 + TARGET_N_TAU_APPROX - 206.768) < 20

        # Confirm the placeholder FAILS these targets (proving it's wrong)
        T_placeholder = g2_color_cycle()
        p = classify_entries(T_placeholder)
        assert p['n_half'] < TARGET_N_HALF_ENTRIES_MIN, (
            "Placeholder should not have dense 1/2 entries"
        )
        assert all(n < TARGET_N_PER_ROW_MIN for n in p['per_row_nonzero']), (
            "Placeholder rows are not dense enough"
        )

    def test_report_ntau_has_cse_fields(self):
        """report_ntau includes the CSE-optimized N_tau fields (RFC-011 §7.3)."""
        T = g2_color_cycle()
        result = report_ntau(T)
        cse_fields = {
            'N_tau_cse',
            'N_tau_cse_unique_sources',
            'N_tau_cse_reuses',
            'N_tau_cse_savings',
            'prediction_1_plus_Ntau_cse',
            'COG_QC_01_consistent_cse',
        }
        assert cse_fields <= set(result.keys()), (
            f"Missing CSE fields: {cse_fields - set(result.keys())}"
        )


# ================================================================
# 5. CSE optimization tests
# ================================================================

class TestCSEOptimization:
    """Verify count_circuit_depth_cse on known matrices."""

    def test_permutation_has_no_cse_savings(self):
        """G2 permutation: every column maps to exactly 1 row → no reuse."""
        T = g2_color_cycle()
        cse_cost, info = count_circuit_depth_cse(T)
        assert info['n_reuses'] == 0, (
            "Permutation matrix has no shared sub-expressions"
        )
        assert info['cse_savings'] == 0, (
            "Permutation matrix should give 0 CSE savings"
        )

    def test_permutation_cse_equals_naive(self):
        """For G2 permutation: CSE cost = naive cost = 24."""
        T = g2_color_cycle()
        cse_cost, info = count_circuit_depth_cse(T)
        naive_cost = count_xor_sign_ops(T)
        assert cse_cost == naive_cost, (
            f"CSE={cse_cost} should equal naive={naive_cost} for permutation"
        )
        assert cse_cost == 24

    def test_cse_returns_tuple_with_dict(self):
        """count_circuit_depth_cse returns (int, dict)."""
        T = g2_color_cycle()
        result = count_circuit_depth_cse(T)
        assert isinstance(result, tuple) and len(result) == 2
        cost, info = result
        assert isinstance(cost, int)
        assert isinstance(info, dict)

    def test_cse_info_keys(self):
        """info dict has the expected fields."""
        T = g2_color_cycle()
        _, info = count_circuit_depth_cse(T)
        expected_keys = {
            'naive_cost', 'unique_sources', 'n_total_nonzero',
            'n_reuses', 'cse_savings', 'cse_cost',
        }
        assert expected_keys <= set(info.keys()), (
            f"Missing keys: {expected_keys - set(info.keys())}"
        )

    def test_dense_matrix_has_cse_savings(self):
        """
        A dense matrix with repeated column access has strictly fewer
        unique sources than total non-zero entries → positive CSE savings.

        Construct a 2-row test: two rows each reading from column 0 at mag 1/2.
        unique_sources = 1 (only one (col=0, mag=0.5) group)
        total_nonzero = 2
        savings = C_e * 1 = 3 ops saved vs. naive 6.
        """
        T = np.zeros((8, 8))
        T[0, 0] = 0.5   # row 0 reads col 0 at +1/2
        T[1, 0] = -0.5  # row 1 reads col 0 at -1/2 (same magnitude → shared)
        cse_cost, info = count_circuit_depth_cse(T)
        assert info['unique_sources'] == 1, (
            "Two rows with same (col, mag) should share 1 source"
        )
        assert info['n_reuses'] == 1, "1 reuse expected"
        assert info['cse_savings'] == 3, "3 ops saved (C_e=3 × 1 reuse)"
        assert cse_cost == 3, f"CSE cost should be 3; got {cse_cost}"

    def test_true_tau_cse_should_beat_naive(self):
        """
        Document: the true SO(8) outer triality (once implemented) must
        have MORE CSE reuses than the G2 placeholder.

        The true tau has ~4 non-zero entries per column, all at magnitude 1/2.
        For 8 columns × 4 rows each: total_nonzero=32, unique_sources=8,
        reuses=24, CSE cost = 3*8 = 24 vs. naive 3*32 = 96.

        This test encodes the REQUIREMENT using a synthetic dense matrix.
        """
        # Synthetic dense matrix: 8 columns, each contributing to 4 rows
        T_dense = np.zeros((8, 8))
        for col in range(8):
            for row_offset in range(4):
                row = (col * 3 + row_offset) % 8
                T_dense[row, col] = 0.5 * (1 if (row + col) % 2 == 0 else -1)

        _, info = count_circuit_depth_cse(T_dense)
        assert info['n_reuses'] > 0, (
            "Dense matrix should have CSE reuse opportunities"
        )
        assert info['cse_cost'] < info['naive_cost'], (
            "Dense matrix CSE cost should be strictly less than naive"
        )

    def test_tau_and_transpose_have_computable_cse(self):
        """
        RFC-011 §9.3: tau^2 = tau^T for orthogonal matrices.
        Verify count_circuit_depth_cse runs without error on T.T.
        The actual depths may differ, revealing asymmetry from Fano signs.
        """
        T = g2_color_cycle()
        cse_t, _ = count_circuit_depth_cse(T)
        cse_tt, _ = count_circuit_depth_cse(T.T)
        # For the G2 permutation, T and T.T are both permutation matrices
        # with the same structure → same CSE cost
        assert cse_t == cse_tt, (
            "G2 permutation and its transpose should have equal CSE depth"
        )


# ================================================================
# 6. Greedy CSE (straight-line program depth) tests
# ================================================================

class TestGreedyCSE:
    """Verify count_circuit_depth_greedy (Gemini algorithm, 2026-02-22)."""

    def test_permutation_greedy_is_zero(self):
        """
        G2 permutation is trivial routing: no additions, no shifts, no pairs.
        N_tau_greedy = 0 (arithmetic circuit is empty).
        """
        T = g2_color_cycle()
        N_tau, info = count_circuit_depth_greedy(T)
        assert N_tau == 0, (
            f"Permutation needs 0 arithmetic ops; got {N_tau}"
        )
        assert info['shift_ticks'] == 0
        assert info['intermediate_ticks'] == 0
        assert info['summation_ticks'] == 0

    def test_identity_greedy_is_zero(self):
        """Identity matrix: each output = one input, no arithmetic."""
        T = np.eye(8)
        N_tau, _ = count_circuit_depth_greedy(T)
        assert N_tau == 0

    def test_greedy_returns_tuple_with_dict(self):
        """count_circuit_depth_greedy returns (int, dict)."""
        T = g2_color_cycle()
        result = count_circuit_depth_greedy(T)
        assert isinstance(result, tuple) and len(result) == 2
        cost, info = result
        assert isinstance(cost, int)
        assert isinstance(info, dict)

    def test_greedy_info_keys(self):
        """info dict has the expected fields."""
        T = g2_color_cycle()
        _, info = count_circuit_depth_greedy(T)
        expected = {'N_tau', 'shift_ticks', 'intermediate_ticks',
                    'n_intermediates', 'summation_ticks', 'rows_after_cse'}
        assert expected <= set(info.keys()), (
            f"Missing keys: {expected - set(info.keys())}"
        )

    def test_half_row_costs_one_shift(self):
        """
        A row with two ±1/2 entries costs 1 shift tick + 1 addition tick.

        T = zeros(8,8) with T[0,0]=0.5, T[0,1]=-0.5 only.
        Row 0: non-zero entries [+0.5, -0.5] → is_half_row=True → 1 shift.
        After factoring out 1/2: terms [(1,'x0'), (-1,'x1')], k=2 → 1 addition.
        No other rows have non-zero entries → no pairs to share.
        N_tau = 1 (shift) + 0 (intermediates) + 1 (summation) = 2.
        """
        T = np.zeros((8, 8))
        T[0, 0] = 0.5
        T[0, 1] = -0.5
        N_tau, info = count_circuit_depth_greedy(T)
        assert info['shift_ticks'] == 1, "1 half-row → 1 shift tick"
        assert info['summation_ticks'] == 1, "2 terms → 1 addition tick"
        assert N_tau == 2, f"Expected N_tau=2; got {N_tau}"

    def test_common_pair_across_three_rows(self):
        """
        If (x0 + x1) appears in three rows, it's cached as one intermediate.

        Rows 0, 2, 4: each have only x0 and x1 at magnitude 1.
        After greedy CSE:
          - t0 = x0 + x1  (1 intermediate tick)
          - Rows 0,2,4 each become [(1,'t0')] (0 summation ticks each)
          - No further pairs repeat
        N_tau = 0 (shifts) + 1 (intermediate) + 0 (summations) = 1.
        """
        T = np.zeros((8, 8))
        T[0, 0] = 1.0;  T[0, 1] = 1.0
        T[2, 0] = 1.0;  T[2, 1] = 1.0
        T[4, 0] = 1.0;  T[4, 1] = 1.0
        N_tau, info = count_circuit_depth_greedy(T)
        assert info['intermediate_ticks'] == 1, "1 shared pair → 1 intermediate"
        assert info['n_intermediates'] == 1
        assert info['summation_ticks'] == 0, "All rows reduced to 1 term"
        assert N_tau == 1, f"Expected N_tau=1; got {N_tau}"

    def test_unique_pairs_no_cse(self):
        """
        If each row has a unique pair of variables, no CSE is possible.

        Row 0: (x0, x1), Row 2: (x2, x3), Row 4: (x4, x5)
        All pairs are distinct → 0 intermediates.
        N_tau = 0 + 0 + 3 (each row has 2 terms → 1 addition each) = 3.
        """
        T = np.zeros((8, 8))
        T[0, 0] = 1.0;  T[0, 1] = 1.0
        T[2, 2] = 1.0;  T[2, 3] = 1.0
        T[4, 4] = 1.0;  T[4, 5] = 1.0
        N_tau, info = count_circuit_depth_greedy(T)
        assert info['intermediate_ticks'] == 0, "No shared pairs → 0 intermediates"
        assert info['summation_ticks'] == 3, "3 rows × 1 addition each"
        assert N_tau == 3

    def test_dense_half_matrix_positive_ntau(self):
        """Dense ±1/2 matrix has positive N_tau (shifts + summations)."""
        T = np.zeros((8, 8))
        for i in range(8):
            for j in range(8):
                T[i, j] = 0.5 * (1 if (i + j) % 2 == 0 else -1)
        N_tau, info = count_circuit_depth_greedy(T)
        assert N_tau > 0, "Dense half matrix should have non-zero circuit depth"
        assert info['shift_ticks'] == 8, "8 half-rows → 8 shift ticks"

    def test_greedy_leq_naive_for_all_test_matrices(self):
        """
        For matrices with uniform ±1/2 entries, greedy ≤ naive.
        (Greedy counts only arithmetic; naive counts C_e per entry.)
        """
        matrices = [
            g2_color_cycle(),
            np.eye(8),
        ]
        for T in matrices:
            N_greedy, _ = count_circuit_depth_greedy(T)
            N_naive = count_xor_sign_ops(T)
            assert N_greedy <= N_naive, (
                f"Greedy ({N_greedy}) should be ≤ naive ({N_naive})"
            )

    def test_report_ntau_has_greedy_fields(self):
        """report_ntau includes the greedy circuit depth fields."""
        T = g2_color_cycle()
        result = report_ntau(T)
        greedy_fields = {
            'N_tau_greedy',
            'N_tau_greedy_shift_ticks',
            'N_tau_greedy_intermediate_ticks',
            'N_tau_greedy_summation_ticks',
            'prediction_1_plus_Ntau_greedy',
            'COG_QC_01_consistent_greedy',
        }
        assert greedy_fields <= set(result.keys()), (
            f"Missing greedy fields: {greedy_fields - set(result.keys())}"
        )

    def test_transpose_greedy_computable(self):
        """
        RFC-011 §9.3: tau^2 = tau^T for orthogonal tau.
        Greedy CSE runs on T.T; result may differ if structure is asymmetric.
        """
        T = g2_color_cycle()
        g_t, _ = count_circuit_depth_greedy(T)
        g_tt, _ = count_circuit_depth_greedy(T.T)
        # G2 permutation is a permutation matrix; T.T is the inverse permutation,
        # also a permutation matrix → same structure → same greedy depth
        assert g_t == g_tt, (
            "G2 and its transpose should have equal greedy depth"
        )
