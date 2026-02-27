# RFC-053: Many-Body Closure and N-to-2 Reduction

Status: Active Draft - Contract Lock Candidate (2026-02-26)
Implements:
- `rfc/MASTER_IMPLEMENTATION_PLAN_V2.md` (WS-A, WS-D)
Companion:
- `rfc/RFC-048_Two_Node_to_Many_Body_Bridge.md`
- `rfc/RFC-051_Scheduler_Semantics_and_Update_Cadence.md`
- `rfc/RFC-050_Proof_State_and_Claim_Status_Matrix.md`
Module:
- `COG.Core.ManyBodyClosure`
Depends on:
- `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
- `rfc/RFC-035_Distance_as_Next_Interaction_Node_Gap.md`
- `rfc/RFC-048_Two_Node_to_Many_Body_Bridge.md`
- `rfc/RFC-051_Scheduler_Semantics_and_Update_Cadence.md`
- `CausalGraphTheory/TwoNodeSystem.lean`
- `CausalGraphTheory/UpdateRule.lean`

---

## 1. Executive Summary

COG has working two-node interaction semantics. This RFC defines when those semantics are recovered exactly from larger systems, and how to quantify deviations when background interactions are present.

This RFC locks:
1. a canonical pair-extraction operator from many-body state,
2. exact `N -> 2` reduction conditions,
3. a decomposition of pair dynamics into direct and background terms,
4. closure gates required before promoting pair-level claims from many-body simulations.

Core statement:
1. pair claims from many-body runs are valid only if reduction conditions are satisfied or deviation is explicitly bounded and reported.

---

## 2. Problem Statement

Many-body runs can alter pair observables via:
1. additional cone-local inputs,
2. spawn-driven topology growth,
3. scheduler/order effects.

Without a closure contract:
1. "pair attraction/repulsion" can be over-claimed from dense contexts,
2. two-node results may not transfer cleanly,
3. reproducibility of pair conclusions becomes mode-dependent.

---

## 3. Scope and Non-Scope

In scope:
1. pair observable extraction from many-body trajectories,
2. exact and approximate reduction semantics,
3. claim-grade reporting requirements for pair conclusions.

Out of scope:
1. full continuum force-law derivations,
2. replacing the locked local update rule,
3. choosing physical embedding geometry.

---

## 4. Formal Setup

Let:
1. `M_t^N` be full microstate with `N` active nodes at tick `t`,
2. `Round_N` be canonical round map under `snapshot_sync_v1`,
3. `a,b` be designated node IDs (pair of interest),
4. `Pi_ab` be pair extraction operator from full state.

Define extracted pair state:
1. `S_ab(t) = Pi_ab(M_t^N)`.

Define pair-evolution operator in true two-node system:
1. `Round_2`.

Goal:
1. specify conditions under which `S_ab(t+1) = Round_2(S_ab(t))` exactly.

---

## 5. Pair Extraction Contract

Canonical extraction mode:
1. `pair_extraction_mode = direct_cond_bg_v1`.

For each `(a,b,t)`, compute:
1. `P_direct(a,b,t)`:
   - result using only messages exchanged between `a` and `b` at `t`.
2. `P_cond(a,b,t)`:
   - result in full many-body run under all active inputs.
3. `Delta_bg(a,b,t)`:
   - `P_cond - P_direct` under declared metric (polarity class / charge delta / phase delta / `d_next` delta).

No claim may report `P_cond` without `Delta_bg`.

---

## 6. Exact N-to-2 Reduction Conditions (Locked Family)

Exact reduction `R_exact(a,b,H)` over horizon `H` holds if all conditions are true:

1. **Isolation of incoming channels**
   - for every `t` in horizon, nodes `a,b` receive no active cone-local messages from nodes outside `{a,b}`.
2. **No spawn bridge insertion**
   - D4 spawn does not create a new active path between `a` and `b` over horizon.
3. **Scheduler purity**
   - canonical scheduler (`snapshot_sync_v1`), no in-round feedback.
4. **Same local rule profile**
   - identical D1-D5 rule profile in two-node and many-body runs.
5. **Same initial pair state**
   - extracted pair state at `t0` matches two-node initial state exactly.

Then required theorem/empirical gate:
1. `Pi_ab(M_{t0+k}^N) = Round_2^k(Pi_ab(M_{t0}^N))` for all `k <= H`.

---

## 7. Approximate Reduction Regime

When exact conditions fail, use bounded-deviation reporting:

1. define per-tick reduction error `e_k = dist_metric(P_cond(k), P_direct(k))`,
2. define horizon error aggregates:
   - `E_max = max_k e_k`,
   - `E_mean = mean_k e_k`,
   - divergence tick `k*` (first `k` with `e_k > eps`).

Approximate closure is admissible only with declared threshold `eps` and full error trace.

---

## 8. Distance-Gap Integration (RFC-035)

For pair `(a,b)`:
1. `d_next_direct` is computed under direct channel isolation,
2. `d_next_cond` is computed in full many-body context,
3. `Delta_d_bg = d_next_cond - d_next_direct`.

Canonical recompute timing:
1. post-spawn, end-of-round recomputation (aligned with RFC-048 and RFC-051).

---

## 9. Decisions Locked by This RFC

### D1. Canonical extraction mode

Lock `direct_cond_bg_v1` as required output for pair claims in many-body contexts.

### D2. Exact reduction criterion

Lock `R_exact` condition family in Section 6 as necessary for "exact recovery" language.

### D3. Error-first reporting

If `R_exact` does not hold, pair claims must include `E_max`, `E_mean`, and divergence tick.

### D4. Scheduler compatibility

Claim-grade many-body closure requires canonical scheduler mode only.

### D5. Spawn disclosure

Any horizon where spawn alters pair paths must be tagged `spawn_affected: true`.

---

## 10. Claim Metadata Contract

Many-body claims that include pair conclusions must include:
1. `pair_extraction_mode`,
2. `reduction_mode` (`exact` or `approx`),
3. `reduction_horizon`,
4. `reduction_error_metric`,
5. `reduction_error_summary` (`E_max`, `E_mean`, `k*`),
6. `scheduler_mode`,
7. `spawn_affected`,
8. `reduction_artifact_ref`.

Missing any required field blocks promotion.

---

## 11. Falsification Gates

### G1. Isolated limit failure
If exact conditions hold but extracted pair does not match two-node evolution, bridge fails.

### G2. Ordering dependence
If results depend on container/list insertion order, bridge fails.

### G3. Hidden background leakage
If `Delta_bg` is nonzero but omitted in claim reporting, claim fails.

### G4. Non-replayability
If replay hash diverges for fixed initial state/profile, bridge fails.

### G5. Undeclared spawn path mutation
If spawn affects pair channel without `spawn_affected` disclosure, claim fails.

---

## 12. Benchmark Ladder

Required test ladder:
1. `N=2` baseline (exact by definition),
2. `N=3` with one inert spectator,
3. `N=3` with active spectator,
4. `N=4+` mixed-load motifs.

For each rung:
1. report `P_direct`, `P_cond`, `Delta_bg`,
2. report distance-gap deltas,
3. report replay hash and reduction status.

---

## 13. Implementation Plan

### 13.1 Python

Add:
1. `calc/many_body_reduction_ladder.py`
2. `calc/test_many_body_reduction_ladder.py`
3. `calc/test_many_body_exact_reduction.py`

Outputs:
1. `sources/many_body_reduction_ladder.json`
2. `sources/many_body_reduction_ladder.md`

### 13.2 Lean scaffold

Add:
1. `CausalGraphTheory/ManyBodyReduction.lean`

Initial theorem targets:
1. `isolated_pair_exact_reduction` (under Section 6 assumptions),
2. `round_permutation_invariant_under_canonical_order`,
3. `reduction_error_nonneg` (for finite metric definitions).

---

## 14. Governance Integration

Integrate with:
1. RFC-049 battery:
   - add `MB-REDUCTION` family.
2. RFC-050 matrix:
   - add fields:
     - `pair_extraction_mode`,
     - `reduction_mode`,
     - `reduction_horizon`,
     - `spawn_affected`.

Promotion rule:
1. many-body pair claims cannot be `supported` unless reduction artifacts and metadata are present.

---

## 15. Failure Modes

1. Mistaking `P_cond` for intrinsic pair law without background decomposition.
2. Claiming exact reduction under active external inputs.
3. Using approximate reduction without declared error threshold.
4. Mixing scheduler modes across baseline and comparison runs.
5. Ignoring spawn-induced topology changes in pair-path analysis.

---

## 16. Acceptance Criteria

This RFC is closed when:
1. reduction ladder tooling and tests are implemented,
2. at least one exact-reduction benchmark passes under isolated conditions,
3. at least one non-isolated benchmark reports bounded deviation with full metadata,
4. CI enforces reduction metadata for many-body pair claims.

---

## 17. Open Questions

1. Which pair-distance metric is most stable for `e_k` in mixed-spin regimes?
2. Should approximate thresholds (`eps`) be global or claim-family specific?
3. How should reduction contracts extend to triad-level observables (`N -> 3`) in v2?

---

## 18. Decision Register

Locked now:
1. direct/conditioned/background decomposition is mandatory,
2. exact reduction requires isolation conditions,
3. approximate reduction requires explicit error reporting.

Deferred:
1. canonical numeric threshold policy for `eps`,
2. triad and higher-order closure contracts beyond pair extraction.

