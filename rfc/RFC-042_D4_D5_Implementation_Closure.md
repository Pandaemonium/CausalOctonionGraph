# RFC-042: D4/D5 Implementation Closure

Status: Active Draft - Lit-backed closure plan (2026-02-26)
Module:
- `COG.Core.Spawn`
- `COG.Core.PiObs`
Depends on:
- `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
- `rfc/RFC-044_Projection_Profile_Governance.md`
- `CausalGraphTheory/D4D5Contracts.lean`
- `CausalGraphTheory/UpdateRule.lean`

---

## 1. Executive Summary

D1-D3 are policy-locked and partially implemented. D4 (spawn) and D5 (projection) are contract-locked but still missing implementation-level closure proofs. This RFC upgrades RFC-042 from stub to an executable closure program:

1. concrete `applySpawn` semantics consistent with `activeConeSlice`,
2. concrete `piObsCanonical` runtime behavior and profile governance,
3. proof obligations that move D4/D5 from contract signatures to verified implementation,
4. deterministic replay and projection-stability gates in CI.

---

## 2. What "Closed" Means

D4/D5 are closed only when all four are true:

1. `ShouldSpawn`, `SpawnInitState`, and `ApplySpawn` have concrete definitions,
2. implementation-level theorems discharge locked contracts (`SpawnCompleteness`, `SpawnThenUpdateLaw`, permutation invariance, etc.),
3. runtime replay and permutation tests pass on randomized seeds,
4. RFC-028 status can be updated from "implementation/proof wiring in progress" to "implemented and verified".

---

## 3. Literature-Grounded Constraints

This section maps external theory to closure constraints already emerging in COG.

### 3.1 Causal order before total order

Lamport's happened-before relation gives a partial order; any total order used in implementation must refine it, not replace it. In COG terms: sort boundary inputs by causal depth first, then deterministic tie-break (`srcId`/`nodeId`) only for concurrent events.

Implication for D4:
1. `activeConeSlice` must remain depth-gated (`srcDepth < parent.topoDepth`),
2. message folding order must be canonical and deterministic.

### 3.2 Consistent global snapshots for observables

Chandy-Lamport shows global-state claims are only meaningful when the snapshot algorithm is consistent with causal channels. In COG terms: `piObs` must be insensitive to container/list insertion order and must expose profile metadata.

Implication for D5:
1. canonical sort by `nodeId` in projection output is mandatory,
2. claim docs must declare projection profile explicitly.

### 3.3 Local growth with covariance constraints

Causal set sequential growth (Rideout-Sorkin) and broader causal-set literature motivate local growth rules with covariance constraints (no label artifacts in physical statements). COG is deterministic, but the structural lesson applies: growth law must be local and representation-independent.

Implication for D4:
1. spawn trigger must be cone-local and payload-active,
2. "no dead letters" (`SpawnCompleteness`) is a physical completeness condition, not an implementation preference.

### 3.4 Local causal graph dynamics

Causal graph dynamics formalizes bounded-speed local evolution on dynamic graphs and compositional closure under local rules.

Implication for D4/D5:
1. topology changes stay round-boundary scoped (aligned with RFC-028 A7),
2. observer maps are explicit projections from full microstate, not implicit side effects.

---

## 4. D4 Closure Semantics (Spawn)

### 4.1 Canonical implementation target

Implement:

1. `shouldSpawnImpl : ShouldSpawn`
   - definition: spawn iff `activeConeSlice parent msgs` is non-empty.
   - note: destination-existence check is in `applySpawnImpl`, not `shouldSpawnImpl`.

2. `spawnInitImpl : SpawnInitState`
   - `nodeId := newId`
   - `psi := omega_vac`
   - `tickCount := 0` (first tick applied by `nextStateV2`)
   - `topoDepth := minActiveSrcDepth + 1` when active input exists
   - defensive fallback for empty active slice: `parent.topoDepth + 1` (temporary wrapper policy)
   - `colorLabel := vacuumColorLabel`

3. `applySpawnImpl : ApplySpawn`
   - if destination already exists: no-op
   - else derive active slice
   - if active slice empty: defensive no-op (wrapper only; not core semantics)
   - else create spawned node via `spawnInitImpl`, run one `nextStateV2` over canonical payload order, insert node, increment `nextNodeId`
   - optional: emit deterministic `pendingEdges` from `SpawnEdges` in canonical order.

### 4.2 Why this closes the current gaps

1. `SpawnCompleteness` is enforced at the microstate level where destination existence is visible.
2. `SpawnThenUpdateLaw` is satisfied because materialization and first tick are fused in `applySpawnImpl`.
3. D4 remains purely local and deterministic (no RNG, no wall-clock, no map iteration dependence).

### 4.3 Remaining D4 decision already acknowledged

Defensive empty-slice fallback remains temporarily allowed in wrapper mode only. It should be removed once call-site discipline is proved in CI. Removal condition is inherited from RFC-028.

---

## 5. D4 Proof Obligations

Prove these over concrete implementations:

1. `spawnInitImpl_nodeId_law`
2. `spawnInitImpl_color_law`
3. `shouldSpawnImpl_locality_law`
4. `applySpawnImpl_deterministic`
5. `applySpawnImpl_completeness`
6. `applySpawnImpl_then_update_tick1`
7. `applySpawnImpl_no_exogenous`

If any of (4-6) fails, D4 is not closed.

---

## 6. D5 Closure Semantics (Projection)

### 6.1 Canonical profile

Lock runtime canonical projection to:

1. `piObsCanonical := piObsMinimal`
2. per-node fields:
   - `nodeId`
   - `u1Charge`
   - `phase4`
   - `topoDepth`
   - `u1Sector := none`

### 6.2 Extended profile

`piObsWithSector` remains available and is required for proton/multi-quark analyses. It is not canonical for baseline claim promotion.

### 6.3 D5 invariance requirements

1. output node list must be sorted by `nodeId`,
2. projection must be invariant under permutation of `ms.nodes`,
3. projection must be many-to-one (nontrivial coarse-graining), not identity.

---

## 7. D5 Proof Obligations

Prove:

1. `piObsCanonical_nodeId_law`
2. `piObsCanonical_charge_law`
3. `piObsCanonical_phase_law`
4. `piObsCanonical_permutation_invariant`
5. `piObsCanonical_nontrivial`

If (4) fails, D5 is blocked regardless of numeric outputs.

---

## 8. Runtime and CI Gates

Add or enforce:

1. replay determinism hash for D4 transition traces,
2. "no dead letters" randomized test (missing destination + active input must materialize node),
3. spawn sequencing test (`tickCount = 1` on first materialization),
4. permutation-fuzz test for `piObsCanonical`,
5. projection-profile declaration check in claim YAML (`pi_obs_profile` required field).

---

## 9. Failure Modes and Interpretation

1. If D4 fails completeness: update rule is physically incomplete (causal input can disappear).
2. If D4 fails determinism: superdetermined contract is broken.
3. If D5 fails permutation invariance: observer map is implementation-artifact-sensitive.
4. If D5 nontriviality fails: projection is not a coarse-graining and profile separation is invalid.

---

## 10. Implementation Sequence (Recommended)

1. Implement `shouldSpawnImpl`, `spawnInitImpl`, `applySpawnImpl` in Lean.
2. Prove D4 obligations.
3. Finalize `piObsCanonical` runtime path and prove D5 obligations.
4. Add CI/runtime gates.
5. Update RFC-028 status line and linked claims once all proofs/tests pass.

---

## 11. References (Literature Basis)

1. Lamport, L. (1978). Time, Clocks and the Ordering of Events in a Distributed System.  
   https://www.microsoft.com/en-us/research/publication/time-clocks-ordering-events-distributed-system/
2. Chandy, K. M., Lamport, L. (1985). Distributed Snapshots: Determining Global States of a Distributed System.  
   https://www.microsoft.com/en-us/research/publication/distributed-snapshots-determining-global-states-distributed-system/
3. Bombelli, L., Lee, J., Meyer, D., Sorkin, R. D. (1987). Space-time as a causal set.  
   https://doi.org/10.1103/PhysRevLett.59.521
4. Rideout, D. P., Sorkin, R. D. (2000). A Classical Sequential Growth Dynamics for Causal Sets.  
   https://arxiv.org/abs/gr-qc/9904062
5. Surya, S. (2019). The causal set approach to quantum gravity.  
   https://arxiv.org/abs/1903.11544
6. Arrighi, P., Dowek, G. (2012). Causal graph dynamics.  
   https://arxiv.org/abs/1202.1098
