# RFC-051: Scheduler Semantics and Update Cadence

Status: Active Draft - Contract Lock Candidate (2026-02-26)
Implements:
- `rfc/MASTER_IMPLEMENTATION_PLAN_V2.md` (WS-A, WS-B)
Companion:
- `rfc/RFC-049_Benchmark_and_Falsification_Battery_v2.md`
- `rfc/RFC-050_Proof_State_and_Claim_Status_Matrix.md`
Module:
- `COG.Core.Scheduler`
Depends on:
- `rfc/RFC-002_Deterministic_Tick_Ordering.md`
- `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
- `rfc/RFC-042_D4_D5_Implementation_Closure.md`
- `rfc/RFC-048_Two_Node_to_Many_Body_Bridge.md`
- `rfc/RFC-054_Observable_Equivalence_and_Physical_Indistinguishability.md`
- `CausalGraphTheory/UpdateRule.lean`

---

## 1. Executive Summary

COG has a locked local update rule, but global outcomes still depend on scheduling semantics unless one canonical scheduler is fixed.

This RFC defines:
1. one canonical claim-grade scheduler mode,
2. one explicit round contract (`M_t -> M_{t+1}`),
3. deterministic tie-break and spawn timing laws,
4. which non-canonical modes are allowed only for sensitivity work.

Core decision:
1. Canonical mode is snapshot-synchronous, round-based, deterministic, and feedback-free within a round.

---

## 2. Problem Statement

Even with fixed local rule `nextStateV2`, different scheduler choices can produce different trajectories:
1. snapshot-synchronous round update,
2. asynchronous event queue update,
3. mixed priority updates.

Without scheduler lock:
1. two runs can both be "correct" but not comparable,
2. claim promotion can accidentally depend on runtime artifacts,
3. replay determinism can fail across containers or implementations.

---

## 3. Scope and Non-Scope

In scope:
1. simulation-level scheduler semantics for kernel transitions,
2. deterministic ordering/tie-break policy,
3. claim metadata and CI gates tied to scheduler mode.

Out of scope:
1. orchestrator task scheduling across AI workers,
2. model/provider routing,
3. physical interpretation beyond scheduler-dependent reproducibility.

---

## 4. Definitions

Let:
1. `M_t` be full microstate at tick `t`,
2. `N_t` be active node set in `M_t`,
3. `B_t(v)` be boundary message list for node `v` derived from `M_t`,
4. `activeConeSlice(v, B_t(v))` follow RFC-042 conventions,
5. `applySpawn` be RFC-042 materialization/update function.

Round transition:
1. `Round(M_t) = M_{t+1}`.

Canonical scheduler requirement:
1. `Round` is a pure function of `M_t` and policy profile.

---

## 5. Scheduler Mode Taxonomy

### 5.1 Canonical mode (claim-grade)

`scheduler_mode = snapshot_sync_v1`

Properties:
1. all reads are from immutable snapshot `M_t`,
2. all writes land in fresh state `M_{t+1}`,
3. no in-round feedback from writes back into reads,
4. deterministic total order is used only where needed for serialization.

### 5.2 Sensitivity-only modes (non-promotable by default)

Allowed for analysis, not for claim promotion unless explicitly declared:
1. `async_fifo_v1` (deterministic queue order),
2. `priority_phase_v1` (deterministic priority buckets),
3. `batched_hybrid_v1` (fixed two-stage batching variant).

Any result from these modes must be labeled sensitivity artifact.

---

## 6. Canonical Round Contract

For each tick `t`:

1. **Snapshot freeze**
   - freeze `M_t`.
2. **Boundary extraction**
   - compute `B_t(v)` for each `v in N_t` from `M_t` only.
3. **Message canonicalization**
   - sort each `B_t(v)` by:
     - ascending `srcDepth`,
     - ascending `srcId`,
     - ascending `destId` (if represented).
4. **Node update planning**
   - compute `nextStateV2(v, payloads(B_t(v)))` from snapshot values.
5. **Spawn planning**
   - evaluate spawn contracts from snapshot and active payload slice.
6. **Commit phase**
   - write all node updates and all spawn materializations into `M_{t+1}`.
7. **Cadence increment**
   - set global tick to `t+1`.

No read in steps 2-5 may observe writes from step 6.

---

## 7. In-Round Feedback Policy (Locked)

Decision:
1. in-round feedback is forbidden in canonical mode.

Reason:
1. it avoids hidden order dependence,
2. it matches RFC-002 determinism goals,
3. it makes replay hashing straightforward.

Formal contract:
1. for canonical mode, every read key is resolved against `M_t`, never against partial `M_{t+1}`.

---

## 8. Spawn Timing Policy (Locked)

Decision:
1. spawn is evaluated and committed within the same round, but spawned nodes are non-emitting until next round.

Details:
1. `applySpawn` may materialize node and apply first update (`tickCount = 1`) during round `t`,
2. spawned nodes do not contribute source messages to any `B_t(*)`,
3. spawned nodes may contribute starting at `B_{t+1}(*)`.

This keeps D4 completeness while preserving snapshot purity.

---

## 9. Deterministic Tie-Break Law (Locked)

Where a total order is required, canonical comparator is:
1. `topoDepth` ascending,
2. `nodeId` ascending,
3. stable fallback on explicit identifier string lexical order if IDs are non-numeric.

Container iteration order is never a source of semantics.

---

## 10. Cadence Semantics

Canonical cadence:
1. one global discrete round per tick,
2. all active nodes are evaluated exactly once per round,
3. no sub-round adaptive stepping in claim-grade mode.

Derived clocks:
1. `tau_topo` and `tau_int` remain per-node observables,
2. scheduler only determines when each node is evaluated, not local rule content.

---

## 11. Metadata Contract for Claims

Any claim using dynamic simulation output must declare:
1. `scheduler_mode` (required),
2. `scheduler_profile_version` (required),
3. `in_round_feedback` (`forbidden` for canonical),
4. `spawn_commit_phase` (`same_round_non_emitting` for canonical),
5. `event_order_policy` (canonical comparator id),
6. `scheduler_seed` (must be `null` in canonical mode).

Missing scheduler metadata blocks promotion.

---

## 12. CI and Runtime Gates

### G1. Replay determinism

1. identical initial `M_0` and policy profile must produce identical trace hash.

### G2. Container independence

1. run result must be invariant under input list permutation and dictionary/map insertion order.

### G3. Mode declaration

1. promoted artifacts must include canonical `scheduler_mode`.

### G4. Spawn discipline

1. spawned node in round `t` is non-emitting until `t+1`.

### G5. No wall-clock dependence

1. scheduler must not read system time, RNG, or thread interleaving state in canonical mode.

---

## 13. Sensitivity Protocol (Non-Canonical Modes)

Non-canonical scheduler studies are allowed only if:
1. canonical baseline run is included,
2. alternate mode is explicitly tagged `sensitivity_only: true`,
3. result report includes delta against canonical metrics.

Required sensitivity outputs:
1. divergence tick index,
2. observable deltas (charge, phase, interaction counts),
3. whether qualitative claim conclusion changes.

If qualitative conclusion changes, claim cannot be promoted as scheduler-robust.

---

## 14. Reference Implementation Plan

### 14.1 Python

Add:
1. `calc/scheduler_replay_harness.py`
2. `calc/test_scheduler_replay_harness.py`
3. `calc/test_scheduler_spawn_timing.py`

Outputs:
1. `scheduler_trace_hash.json`,
2. canonical vs sensitivity delta table.

### 14.2 Lean scaffold

Add:
1. `CausalGraphTheory/Scheduler.lean` (or equivalent section in existing module).

Initial theorem targets:
1. `round_deterministic` (pure function),
2. `snapshot_read_purity`,
3. `spawn_non_emitting_same_round`.

---

## 15. Failure Modes

1. Hidden async behavior from runtime containers.
2. Implicit dependence on map/list iteration order.
3. Spawned nodes emitting in same round.
4. Claims promoted from non-canonical mode without disclosure.
5. Mixed scheduler profiles inside one artifact bundle.

---

## 16. Acceptance Criteria

This RFC is closed when:
1. canonical scheduler profile is implemented and documented,
2. replay determinism and spawn-timing tests pass in CI,
3. claim artifacts include scheduler metadata and validator checks,
4. at least one sensitivity report demonstrates comparison against canonical mode.

---

## 17. Decision Register

Locked by this RFC draft:
1. canonical mode is `snapshot_sync_v1`,
2. in-round feedback is forbidden,
3. spawn is same-round materialization but non-emitting until next round,
4. deterministic comparator order is fixed by depth then id.

Open:
1. whether additional canonical versions (`snapshot_sync_v2`) are needed later,
2. whether cadence must support regime-specific sub-rounds in future many-body studies.

---

## 18. References

1. Lamport, L. (1978), Time, Clocks, and the Ordering of Events in a Distributed System.
2. Chandy, K. M., Lamport, L. (1985), Distributed Snapshots: Determining Global States of a Distributed System.
3. Arrighi, P., Dowek, G. (2012), Causal graph dynamics.
