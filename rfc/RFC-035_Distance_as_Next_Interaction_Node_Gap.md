# RFC-035: Distance as Next-Interaction Node Gap

**Status:** Active - Draft (2026-02-26)  
**Module:** `COG.Theory.DistanceGap`  
**Depends on:** `rfc/RFC-020_Kernel_Representation_Reconciliation.md`, `rfc/RFC-022_Lightcone_Semantics_and_Causal_Locality.md`, `rfc/RFC-028_Canonical_Update_Rule_Closure.md`, `rfc/RFC-033_Double_Slit_Interference_and_Path_Resolution.md`

---

## 1. Executive Summary

This RFC defines operational distance in COG as:

1. not Euclidean metric distance,
2. not coordinate distance in an embedding space,
3. but the **integer number of graph nodes between two states before their next interaction event**.

Core claim:

`distance(a, b, t) = number of intermediate nodes on the canonical next-interaction route between a and b at tick t`.

In isolated two-body toy systems this is deterministic and branchless.  
In many-body systems it appears statistical after projection, but remains deterministic at full microstate level.

---

## 2. Motivation

COG already has:

1. discrete state container (`C x O`),
2. deterministic local update,
3. cone-local message passing.

What is missing is a physically meaningful, graph-native notion of separation for interaction dynamics (repel/attract trends) that does not reintroduce continuous geometry assumptions.  
This RFC supplies that notion.

---

## 3. Definitions

Let `a, b` be two node IDs in microstate `ms_t`.

Define:

1. **Interaction event** (pair-level): a tick where the pair's interaction predicate is evaluated from exchanged boundary payloads.
2. **Canonical route**: deterministic, predeclared route used for the pair's next interaction under RFC-002 ordering and RFC-028 scheduler policy.
3. **Intermediate-node count**: nodes on the route excluding endpoints `a` and `b`.

Then:

`d_next(a, b, t) : Nat = intermediate-node count on the canonical route that culminates in the next pair interaction after tick t`.

Interpretation:

1. `d_next = 0` means direct next-tick interaction channel (adjacent in interaction graph).
2. `d_next = k` means exactly `k` relay nodes lie between the pair before next interaction.

---

## 4. Two-Body Toy Semantics (Branchless Baseline)

For an isolated pair `(a,b)` with no external messages:

State:

1. `psi_a`, `psi_b`,
2. `d : Nat`,
3. `countdown : Nat` where `countdown = d + 1`.

Per tick:

1. Update `psi_a`, `psi_b` by `nextStateV2`.
2. Decrement `countdown`.
3. If `countdown > 0`, no distance change.
4. If `countdown = 0`, evaluate pair polarity and update `d`:
   - attractive -> `d := max(0, d - 1)`
   - repulsive -> `d := d + 1`
   - neutral -> `d := d`
5. Reset `countdown := d + 1`.

This gives a minimal deterministic motion law in graph space without continuous coordinates.

---

## 5. Many-Body Interpretation

In full many-body dynamics, additional cone-local interactions affect each node between pair events.  
Therefore observed "moving closer/farther" is generally an aggregate effect:

`d_{t+} = d_t + delta_pair + delta_bg(t)`

where:

1. `delta_pair` is pair-polarity contribution (attract/repel/neutral),
2. `delta_bg(t)` is deterministic background contribution from other scheduled interactions in the superdetermined microstate.

No stochastic dynamics are required at kernel level.

---

## 6. Relation to Superdetermination and Statistics

COG stance under this RFC:

1. Full trajectory of `d_next` is fixed by initial microstate + deterministic update order.
2. Statistical behavior appears only after projection (`Pi_obs`) when hidden background interactions are not observed.
3. "Force laws" at observer level are effective summaries of deterministic graph-depth updates.

---

## 7. Invariants

Any conforming implementation must satisfy:

1. `d_next >= 0` always.
2. `d_next` is integer-valued.
3. `d_next` depends only on local update contracts + deterministic scheduling (no RNG, no wall-clock).
4. For isolated two-body mode, repeated runs from identical initial microstate produce identical `d_next` traces.
5. `d_next` is endpoint-order symmetric for symmetric pair channels: `d_next(a,b,t) = d_next(b,a,t)` in the symmetric toy model.

---

## 8. Open Design Decisions

### DIST-1. Pair interaction predicate symmetry

Current charge-sign matrix is receiver-oriented in one helper path.  
Need explicit pair-level lock:

1. receiver-oriented predicate (asymmetric but simple), or
2. symmetric pair predicate (recommended for distance updates).

### DIST-2. Canonical route in general DAGs

When multiple admissible routes exist, route choice must be fixed by deterministic tie-break policy (depth, nodeId, then predeclared parenthesization family).

### DIST-3. Spawn interaction with route length

When D4 spawning creates new relay nodes, define exactly when `d_next` is recomputed:

1. immediate recompute after spawn, or
2. next round only.

---

## 9. Implementation Plan

### 9.1 Python

Add:

1. `calc/two_node_spatial_dynamics.py`
2. `calc/test_two_node_spatial_dynamics.py`

Required outputs:

1. deterministic `d` traces for e-e, e-e+, and neutral baselines,
2. monotonic trend checks in isolated mode:
   - repulsive baseline non-decreasing `d`,
   - attractive baseline non-increasing `d`,
3. replay hash equality for identical initial states.

### 9.2 Lean (scaffold first)

Add:

1. `CausalGraphTheory/DistanceGap.lean`

Initial signatures:

1. `def nextInteractionGap : FullMicrostate -> Nat -> Nat -> Nat`
2. `theorem nextInteractionGap_nonneg`
3. `theorem nextInteractionGap_deterministic`
4. `theorem nextInteractionGap_symmetric_toy` (for isolated two-body model)

Do not claim physical trajectory derivations until D4 concrete `applySpawn` proofs are complete.

---

## 10. Claim Governance Impact

Until this RFC is implemented:

1. "attractive implies moves closer" remains an interpretation, not a model-derived theorem,
2. e-e scattering remains at interaction-classification stage,
3. any distance-based claim must declare whether it uses isolated toy mode or full many-body mode.

---

## 11. Acceptance Criteria

This RFC is considered closed when:

1. Python isolated two-body dynamics module and tests pass in CI,
2. deterministic replay hashes are stable,
3. distance update policy (DIST-1, DIST-2, DIST-3) is locked in one canonical contract,
4. at least one Lean scaffold theorem for distance determinism is merged.
