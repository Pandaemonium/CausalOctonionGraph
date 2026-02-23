"""
calc/triality_map.py
RFC-011 Action Item A: Triality automorphism on the 8-dimensional state space.

MATHEMATICAL STATUS
-------------------
The SO(8) triality automorphism tau is an 8x8 REAL ORTHOGONAL MATRIX
with entries typically in {0, +/-1/2}.  It is NOT a simple permutation of
basis indices.  Applying tau to a single unit basis vector yields a
superposition of multiple basis vectors.  This is the key correction
relative to the original RFC-011 draft (Gemini feedback, 2026-02-22).

The three 8-dimensional representations of SO(8) are:
  V  = vector representation        (electron sector in Furey)
  S+ = left  spinor representation  (muon    sector in Furey)
  S- = right spinor representation  (tau     sector in Furey)

Tau cycles V -> S+ -> S- -> V (order 3).

IMPLEMENTATION STATUS
---------------------
Two maps are provided:

1. octonion_left_mul_matrix(k): EXACT.
   8x8 real matrix for left-multiplication by e_k.  Derived directly from
   the locked Fano convention (CONVENTIONS.md §2 / calc/conftest.py).

2. g2_color_cycle(): PLACEHOLDER (inner automorphism only).
   8x8 permutation matrix for the order-3 G2 automorphism that cycles the
   three Witt color planes: {e6,e1} -> {e2,e5} -> {e3,e4} -> {e6,e1}.
   This IS order-3 and preserves the Fano plane structure, but it is an
   INNER automorphism (element of G2 = Aut(O) subset SO(7) subset SO(8)).
   It is NOT the SO(8) outer triality automorphism.

The true 8x8 state-space intertwiner requires extracting T from:
    T . V_ij . T^{-1} = L_{H(ij)}   for all 28 generator pairs (i,j)
where V_ij are the vector-rep generators, L_ij are the S+ generators
(from McRae 2025 Clifford algebra construction), and H is McRae's 4x4
triality matrix acting on quartets of generators.  This derivation is
deferred to RFC-010 Phase D.

References
----------
- McRae (2025) arXiv:2502.14016, Sections 2.1-2.3 (SO(8) compact case)
- Schray & Manogue (1994) arXiv:hep-th/9407179 (S3 x SO(8) structure)
- rfc/CONVENTIONS.md (locked Furey convention, vacuum axis e7)

Convention
----------
State vectors are 8-component numpy arrays indexed as:
  index 0 = e0 (real unit)
  index 1 = e1, ..., index 7 = e7  (imaginary units)

FANO_SIGN / FANO_THIRD in conftest.py use 0-indexed FANO POINTS:
  Fano point 0 = e1, ..., Fano point 6 = e7
i.e., Fano index = state index - 1 for imaginary units.
"""

import numpy as np
from calc.conftest import FANO_SIGN, FANO_THIRD, WITT_PAIRS, VACUUM_AXIS


# ================================================================
# Left-multiplication matrices (exact, from Fano convention)
# ================================================================

def octonion_left_mul_matrix(k: int) -> np.ndarray:
    """
    Build the 8x8 real matrix L_k = left multiplication by e_k.

    (L_k)_{ij} = coefficient of e_i in the product e_k * e_j.

    Properties:
      L_0 = I_8                  (e0 is the real identity)
      L_k^2 = -I_8  (k=1..7)    (e_k^2 = -1 for imaginary units)
      L_k is real orthogonal     (|e_k * x| = |x|)
      L_k^T = -L_k  for k!=0    (e_k * e_j = -(e_j * e_k) for j!=k)

    These 7 matrices generate the Clifford algebra Cl(0,7) acting on O.
    They are building blocks for the spinor representations of SO(8).

    Args:
        k: State-vector index in 0..7 (0=e0, 1=e1, ..., 7=e7).

    Returns:
        8x8 real numpy array.
    """
    if k == 0:
        return np.eye(8)

    M = np.zeros((8, 8))
    fano_k = k - 1  # Convert to 0-indexed Fano point

    for j in range(8):
        if j == 0:
            # e_k * e_0 = e_k  ->  result index = k, sign = +1
            M[k, 0] = 1.0
        elif j == k:
            # e_k * e_k = -e_0  ->  result index = 0, sign = -1
            M[0, k] = -1.0
        else:
            fano_j = j - 1  # Convert to 0-indexed Fano point
            sign = FANO_SIGN[(fano_k, fano_j)]       # +1 or -1
            result_fano = FANO_THIRD[(fano_k, fano_j)]  # 0-indexed result
            result_idx = result_fano + 1              # Back to state index
            M[result_idx, j] = float(sign)

    return M


def build_all_left_mul_matrices() -> dict[int, np.ndarray]:
    """
    Build all 8 left-multiplication matrices L_0 ... L_7.

    Returns:
        dict mapping k (0..7) -> 8x8 real matrix.
    """
    return {k: octonion_left_mul_matrix(k) for k in range(8)}


def verify_left_mul_algebra(L: dict[int, np.ndarray], tol: float = 1e-10) -> dict:
    """
    Verify basic algebraic properties of the left-multiplication matrices.

    Checks:
      1. L[k] @ L[k] = -I  for k=1..7     (imaginary units square to -1)
      2. L[k] @ L[j] + L[j] @ L[k] = 0   for k!=j, k,j in 1..7
         (anticommutativity of distinct imaginary units)
      3. L[0] = I                           (identity)
      4. L[k] is orthogonal: L[k].T @ L[k] = I

    Returns:
        dict with bool fields for each check.
    """
    I = np.eye(8)
    results = {
        'identity_ok': np.allclose(L[0], I, atol=tol),
        'squares_to_neg_identity': all(
            np.allclose(L[k] @ L[k], -I, atol=tol) for k in range(1, 8)
        ),
        'anticommutative': all(
            np.allclose(L[k] @ L[j] + L[j] @ L[k], np.zeros((8, 8)), atol=tol)
            for k in range(1, 8) for j in range(1, 8) if k != j
        ),
        'orthogonal': all(
            np.allclose(L[k].T @ L[k], I, atol=tol) for k in range(8)
        ),
    }
    results['all_ok'] = all(results.values())
    return results


# ================================================================
# Placeholder triality: G2 color-plane cycle
# ================================================================

def g2_color_cycle() -> np.ndarray:
    """
    PLACEHOLDER: Order-3 G2 automorphism cycling the three Witt color planes.

    Permutation (in state-vector indices 0=e0 ... 7=e7):
        0 -> 0   (e0 fixed)
        1 -> 2   (e1 -> e2)
        2 -> 4   (e2 -> e4)
        4 -> 1   (e4 -> e1)   [closes the (1,2,4) 3-cycle]
        3 -> 6   (e3 -> e6)
        6 -> 5   (e6 -> e5)
        5 -> 3   (e5 -> e3)   [closes the (3,6,5) 3-cycle]
        7 -> 7   (e7 fixed)

    Witt pair cycle (state indices, from CONVENTIONS.md §5.2):
        {e6, e1} = {6, 1}  ->  {e5, e2} = {2, 5}  (pair 2, reordered)
        {e2, e5} = {2, 5}  ->  {e4, e3} = {3, 4}  (pair 3, reordered)
        {e3, e4} = {3, 4}  ->  {e6, e1} = {6, 1}  (pair 1)

    This IS a G2 = Aut(O) automorphism of order 3, confirmed by:
      - The permutation maps Fano lines to Fano lines.
      - It fixes the vacuum axis e7.

    WARNING: This is an INNER automorphism of O (element of G2 subset SO(7)
    subset SO(8)). It is NOT the SO(8) outer triality automorphism tau.
    The outer tau maps basis vectors to +-1/2 linear combinations; this
    permutation maps each basis vector to exactly one other.  Therefore:
      - N_tau from this matrix will be MUCH SMALLER than the true N_tau.
      - The mass-ratio prediction from this placeholder is NOT reliable.

    The true 8x8 SO(8) outer triality matrix requires deriving the
    intertwiner between the V and S+ representations from the Clifford
    algebra (McRae 2025, §2.2).  Tracked as RFC-010 Phase D.

    Returns:
        8x8 real permutation matrix with entries in {0, 1}, order = 3.
    """
    # src_index -> dst_index
    src_to_dst = {0: 0, 1: 2, 2: 4, 3: 6, 4: 1, 5: 3, 6: 5, 7: 7}
    T = np.zeros((8, 8))
    for src, dst in src_to_dst.items():
        T[dst, src] = 1.0
    return T


# ================================================================
# Order verification
# ================================================================

def verify_order(T: np.ndarray, expected_order: int = 3,
                 tol: float = 1e-10) -> tuple[bool, int]:
    """
    Find the multiplicative order of T: smallest n >= 1 s.t. T^n = I.

    Args:
        T:              8x8 matrix.
        expected_order: The order we expect (default 3 for triality).
        tol:            Tolerance for np.allclose comparison.

    Returns:
        (is_expected_order, actual_order)
        actual_order = -1 if order > 9 (not found in 9 steps).
    """
    I = np.eye(T.shape[0])
    current = T.copy()
    for n in range(1, 10):
        if np.allclose(current, I, atol=tol):
            return (n == expected_order), n
        current = current @ T
    return False, -1


# ================================================================
# XOR+sign cost analysis
# ================================================================

def classify_entries(T: np.ndarray, tol: float = 1e-10) -> dict:
    """
    Classify the entries of the triality matrix by magnitude.

    Categories (per the XOR+sign cost model, CONVENTIONS.md / RFC-011 §6):
      - zero:   |T[i,j]| < tol           (no cost)
      - unit:   |T[i,j]| ~ 1.0           (1 XOR + 1 sign = 2 ops, or C_e = 3)
      - half:   |T[i,j]| ~ 0.5 = 1/2     (1 XOR + 1 sign + 1 shift = C_e = 3)
      - other:  anything else (unexpected for the triality matrix)

    Returns:
        dict with counts and a per-row breakdown.
    """
    n_zero = 0
    n_unit = 0
    n_half = 0
    n_other = 0
    per_row = []

    for i in range(T.shape[0]):
        row_nonzero = 0
        for j in range(T.shape[1]):
            v = abs(T[i, j])
            if v < tol:
                n_zero += 1
            elif abs(v - 1.0) < tol:
                n_unit += 1
                row_nonzero += 1
            elif abs(v - 0.5) < tol:
                n_half += 1
                row_nonzero += 1
            else:
                n_other += 1
                row_nonzero += 1
        per_row.append(row_nonzero)

    return {
        'n_zero': n_zero,
        'n_unit': n_unit,
        'n_half': n_half,
        'n_other': n_other,
        'per_row_nonzero': per_row,
    }


def count_xor_sign_ops(T: np.ndarray, tol: float = 1e-10) -> int:
    """
    Count total elementary XOR+sign operations for one application of tau.

    Cost model (RFC-011 §6, C_e = 3 ops per elementary product):
      - Each non-zero entry T[i,j] requires:
          1 XOR (compute output index from input)
        + 1 sign lookup (from Fano parity table)
        + 1 optional bit-shift (if |T[i,j]| = 1/2)
        = C_e = 3 ops per non-zero entry.
      - Zero entries cost 0 ops.

    NOTE: This is an UPPER BOUND for a naive implementation.  A
    circuit-optimized implementation may share intermediate computations
    across rows and reduce the total count.  The minimum depth (N_tau)
    may therefore be lower.  See count_circuit_depth_cse() for the
    common-sub-expression (CSE) optimized count.

    Returns:
        Total op count = C_e * (number of non-zero entries in T).
    """
    C_e = 3
    n_nonzero = int(np.sum(np.abs(T) > tol))
    return C_e * n_nonzero


def count_circuit_depth_cse(T: np.ndarray,
                             tol: float = 1e-10) -> tuple[int, dict]:
    """
    Estimate N_tau using common sub-expression elimination (CSE).

    The naive count (count_xor_sign_ops) treats every non-zero entry as an
    independent operation.  But hardware can CACHE intermediate values: if
    multiple output rows draw from the same source column j with the same
    magnitude, the scaled value is computed ONCE and accumulated into each
    output row with a free sign flip (single bit complement).

    This is the "straight-line program" (SLP) optimization for fixed-matrix
    vector multiplication (RFC-011 §7.3).

    Algorithm:
      - Group non-zero entries by (source_column j, magnitude |T[i,j]|).
      - Each unique (column, magnitude) pair = ONE intermediate computation.
      - CSE cost = C_e × (number of unique (column, magnitude) groups).
      - Sign flips and accumulations into output rows cost 0 (native ops).

    For a permutation matrix (G2 placeholder): every column has exactly one
    non-zero entry, so unique_sources = n_nonzero → no savings.

    For the true SO(8) tau with k entries per column, all at magnitude 1/2:
    unique_sources = n_columns_used = 8 (one per input) → CSE cost = 24,
    regardless of how many output rows share each input.

    Args:
        T:   8x8 candidate triality matrix.
        tol: Floating-point tolerance.

    Returns:
        (cse_cost, info_dict) where:
        - cse_cost:  estimated N_tau after CSE (lower bound vs. naive).
        - info_dict: breakdown including naive cost, reuse count, savings.
    """
    from collections import defaultdict

    # Group by (source column, magnitude) -> list of (row, sign)
    col_mag: dict[tuple[int, float], list[tuple[int, int]]] = defaultdict(list)
    for i in range(T.shape[0]):
        for j in range(T.shape[1]):
            v = T[i, j]
            if abs(v) < tol:
                continue
            # Snap magnitude to nearest recognizable value
            mag = abs(v)
            if abs(mag - 1.0) < tol:
                mag = 1.0
            elif abs(mag - 0.5) < tol:
                mag = 0.5
            sign = 1 if v > 0 else -1
            col_mag[(j, mag)].append((i, sign))

    n_unique_sources = len(col_mag)
    n_total_nonzero = sum(len(rows) for rows in col_mag.values())
    n_reuses = n_total_nonzero - n_unique_sources

    C_e = 3
    cse_cost = C_e * n_unique_sources
    naive_cost = C_e * n_total_nonzero

    return cse_cost, {
        'naive_cost': naive_cost,
        'unique_sources': n_unique_sources,
        'n_total_nonzero': n_total_nonzero,
        'n_reuses': n_reuses,
        'cse_savings': naive_cost - cse_cost,
        'cse_cost': cse_cost,
    }


def count_circuit_depth_greedy(T: np.ndarray) -> tuple[int, dict]:
    """
    Compute the minimal arithmetic circuit depth for T·x using greedy CSE.

    Algorithm (Gemini, 2026-02-22):

    Step 1 — Row-level bit-shift factoring:
      If every non-zero entry in a row has magnitude 1/2, factor out the 1/2
      and charge exactly 1 tick for a bit-shift right (>> 1) at the row output.
      Remaining coefficients become ±1.  This models the E8/D4 spinor structure
      where half-integer coordinates are native hardware bit-shifts.

    Step 2 — Greedy pair CSE:
      Repeatedly find the most common (term_A, term_B) pair that appears in
      two or more row sums.  Cache it as an intermediate register (1 tick) and
      substitute it back into every row that contains the pair.  Repeat until
      no pair appears in more than one row.

    Step 3 — Final row summation:
      A row with k remaining terms costs k−1 addition ticks.

    Total: N_tau = shift_ticks + intermediate_ticks + summation_ticks.

    Cost comparison:
      count_xor_sign_ops    (naive):   C_e × n_nonzero          [upper bound]
      count_circuit_depth_cse (col):   C_e × unique (col,mag)   [intermediate]
      count_circuit_depth_greedy:      arithmetic ops only       [tighter bound]

    For the G2 permutation: N_tau = 0 (trivial routing, no arithmetic).
    For the true SO(8) tau with dense ±1/2 entries: N_tau reflects the
    actual Walsh-Hadamard-like butterfly structure of the matrix.

    Args:
        T: 8x8 candidate triality matrix.

    Returns:
        (N_tau, info_dict) where N_tau is the minimized circuit depth and
        info_dict contains the tick breakdown.
    """
    import itertools
    from collections import Counter

    tol = 1e-10

    # Step 1: Build symbolic rows; factor out row-level bit-shifts
    rows: list[list[tuple[int, str]]] = []
    shift_ticks = 0

    for i in range(T.shape[0]):
        non_zero = [(j, T[i, j]) for j in range(T.shape[1])
                    if abs(T[i, j]) > tol]

        if not non_zero:
            rows.append([])
            continue

        # Check if every non-zero entry in this row has magnitude 1/2
        is_half_row = all(abs(abs(v) - 0.5) < tol for _, v in non_zero)

        terms: list[tuple[int, str]] = []
        for j, v in non_zero:
            if is_half_row:
                coeff = 1 if v > 0 else -1  # Factor out 1/2; coefficient ±1
            else:
                coeff = int(round(v))
            terms.append((coeff, f"x{j}"))

        if is_half_row:
            shift_ticks += 1  # One >> 1 at this row's output

        rows.append(terms)

    # Step 2: Greedy common-subexpression elimination (pair level)
    intermediate_ticks = 0
    var_idx = 0

    while True:
        pair_counts: Counter = Counter()
        for row in rows:
            for pair in itertools.combinations(row, 2):
                # Canonical form: sort by variable name for commutativity
                key = tuple(sorted(pair, key=lambda x: x[1]))
                pair_counts[key] += 1

        if not pair_counts or max(pair_counts.values()) < 2:
            break  # No pair used by more than one row — done

        best_pair, _ = pair_counts.most_common(1)[0]
        new_var = f"t{var_idx}"
        var_idx += 1
        intermediate_ticks += 1  # 1 tick to compute this intermediate

        for row in rows:
            if best_pair[0] in row and best_pair[1] in row:
                row.remove(best_pair[0])
                row.remove(best_pair[1])
                row.append((1, new_var))

    # Step 3: Final row-summation ticks (k terms → k−1 additions)
    summation_ticks = sum(max(0, len(row) - 1) for row in rows)

    N_tau = shift_ticks + intermediate_ticks + summation_ticks

    return N_tau, {
        'N_tau': N_tau,
        'shift_ticks': shift_ticks,
        'intermediate_ticks': intermediate_ticks,
        'n_intermediates': var_idx,
        'summation_ticks': summation_ticks,
        'rows_after_cse': [list(row) for row in rows],
    }


def report_ntau(T: np.ndarray, label: str = "tau", tol: float = 1e-10) -> dict:
    """
    Full N_tau analysis for a triality-candidate matrix T.

    Computes:
      - Whether T^3 = I
      - Entry classification (zero/unit/half/other)
      - N_tau (naive): total XOR+sign op count = C_e * n_nonzero (upper bound)
      - N_tau (CSE):   op count after common sub-expression elimination
                       = C_e * unique (column, magnitude) sources (lower bound)
      - Predicted mass ratios: 1 + N_tau for both naive and CSE counts
      - Consistency checks against m_mu/m_e = 206.768

    Args:
        T:     8x8 candidate triality matrix.
        label: Human-readable label for display.
        tol:   Floating-point tolerance.

    Returns:
        dict with all analysis results.
    """
    is_order_3, actual_order = verify_order(T, expected_order=3, tol=tol)
    entry_info = classify_entries(T, tol=tol)
    N_tau_naive = count_xor_sign_ops(T, tol=tol)
    N_tau_cse, cse_info = count_circuit_depth_cse(T, tol=tol)
    N_tau_greedy, greedy_info = count_circuit_depth_greedy(T)
    m_mu_me_observed = 206.768
    prediction_naive = 1 + N_tau_naive
    prediction_cse = 1 + N_tau_cse
    prediction_greedy = 1 + N_tau_greedy
    consistent_naive = abs(prediction_naive - m_mu_me_observed) < 1.0
    consistent_cse = abs(prediction_cse - m_mu_me_observed) < 1.0
    consistent_greedy = abs(prediction_greedy - m_mu_me_observed) < 1.0

    return {
        'label': label,
        'is_order_3': is_order_3,
        'actual_order': actual_order,
        'n_nonzero': entry_info['n_unit'] + entry_info['n_half'] + entry_info['n_other'],
        'n_unit_entries': entry_info['n_unit'],
        'n_half_entries': entry_info['n_half'],
        'n_other_entries': entry_info['n_other'],
        'per_row_nonzero': entry_info['per_row_nonzero'],
        # Naive count (upper bound): C_e × n_nonzero
        'N_tau': N_tau_naive,
        'prediction_1_plus_Ntau': prediction_naive,
        'm_mu_me_observed': m_mu_me_observed,
        'COG_QC_01_consistent': consistent_naive,
        # CSE column count (intermediate): C_e × unique (col, mag) sources
        'N_tau_cse': N_tau_cse,
        'N_tau_cse_unique_sources': cse_info['unique_sources'],
        'N_tau_cse_reuses': cse_info['n_reuses'],
        'N_tau_cse_savings': cse_info['cse_savings'],
        'prediction_1_plus_Ntau_cse': prediction_cse,
        'COG_QC_01_consistent_cse': consistent_cse,
        # Greedy CSE (tightest arithmetic lower bound): shifts + pairs + sums
        'N_tau_greedy': N_tau_greedy,
        'N_tau_greedy_shift_ticks': greedy_info['shift_ticks'],
        'N_tau_greedy_intermediate_ticks': greedy_info['intermediate_ticks'],
        'N_tau_greedy_summation_ticks': greedy_info['summation_ticks'],
        'prediction_1_plus_Ntau_greedy': prediction_greedy,
        'COG_QC_01_consistent_greedy': consistent_greedy,
    }


# ================================================================
# Main: print analysis for the placeholder map
# ================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("RFC-011 Triality Map Analysis")
    print("=" * 60)

    # --- Left-multiplication matrices ---
    L = build_all_left_mul_matrices()
    alg_ok = verify_left_mul_algebra(L)
    print("\nLeft-multiplication algebra check:")
    for k, v in alg_ok.items():
        print(f"  {k}: {v}")

    # --- G2 placeholder ---
    T_g2 = g2_color_cycle()
    print("\nG2 color-cycle matrix (PLACEHOLDER, inner automorphism):")
    print(T_g2.astype(int))

    result = report_ntau(T_g2, label="G2 color-cycle (placeholder)")
    print("\nN_tau analysis (placeholder):")
    for k, v in result.items():
        print(f"  {k}: {v}")

    print("\nCost model comparison (3 levels):")
    print(f"  Naive N_tau:     {result['N_tau']:3d}  → 1+N_tau = {result['prediction_1_plus_Ntau']}")
    print(f"  CSE col N_tau:   {result['N_tau_cse']:3d}  → 1+N_tau = {result['prediction_1_plus_Ntau_cse']}"
          f"  (savings: {result['N_tau_cse_savings']})")
    print(f"  Greedy N_tau:    {result['N_tau_greedy']:3d}  → 1+N_tau = {result['prediction_1_plus_Ntau_greedy']}"
          f"  (shifts={result['N_tau_greedy_shift_ticks']},"
          f" intermediates={result['N_tau_greedy_intermediate_ticks']},"
          f" sums={result['N_tau_greedy_summation_ticks']})")

    print("\nNOTE: The placeholder N_tau is too small (permutation matrix).")
    print("The true SO(8) outer triality matrix has dense +-1/2 entries.")
    print("RFC-010 Phase D: derive the 8x8 state-space intertwiner from")
    print("the Clifford algebra generators (McRae 2025, Section 2.2).")
