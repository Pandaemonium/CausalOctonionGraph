# RFC-020: Kernel Representation Reconciliation (CxO-Native Kernel v2)

**Status:** Active - Decision RFC (2026-02-25)  
**Module:** `COG.Core.KernelV2`  
**Depends on:** `rfc/CONVENTIONS.md`, `rfc/RFC-002_Deterministic_Tick_Ordering.md`, `rfc/RFC-013_Algebraic_Vacuum_and_Causal_Spawning.md`, `rfc/RFC-016_Kernel_v1_Contract.md`, `rfc/RFC-018_Time_as_Graph_Depth_and_Interaction_Clock.md`, `rfc/RFC-019_e7_Temporal_Axis_Vacuum_Photon_Duality.md`

---

## 1. Executive Summary

This RFC resolves a blocking architectural conflict:

- RFC-013 requires full `C x O` node states so vacuum `omega = 1/2(1 + i e7)` is representable.
- RFC-016 Kernel v1 stores only signed imaginary basis labels (`octIdx`, `sign`), which cannot represent `omega`.

**Decision:** Kernel v2 is **algebra-first and CxO-native**.  
Canonical node state is a full complex-octonion value. Any compressed or label view is derived-only.

This keeps the model consistent with RFC-013, RFC-018, and RFC-019 while preserving deterministic implementation requirements from RFC-002.

---

## 2. Problem Statement

The current stack contains incompatible assumptions:

1. RFC-019 requires runtime evaluation of `isVacuumOrbit(x)` to classify phase-only steps.
2. RFC-016 v1 state (`octIdx`, `sign`) maps only to `+/- e1..+/-e7`.
3. `omega` is not in that set.

Therefore, the v1 kernel cannot express the current vacuum/time semantics.

---

## 3. Decision

### D1. Canonical state representation

Kernel v2 node state is:

```
psi : C x O
```

Implementation may store this as:

- 8 coefficients in `FormalComplex Int` (Lean), or
- 8 complex components with exact/integer-compatible policy (Python layer).

### D2. Algebraic predicates are authoritative

All physics branching uses predicates on `psi`, including:

- `isVacuumOrbit(psi)`
- `isPhaseOnlyStep(transition)`
- `isEnergyExchange(transition)`

Metadata labels are optional caches only. They are never semantic source-of-truth.

### D3. Derived views are allowed

For performance/UX, derived fields are permitted (for example basis index, phase class, display label), but must be recomputable from `psi` and validated.

### D4. Legacy v1 state becomes compatibility-only

`octIdx/sign` representation is retained only via adapters for migration/tests, not as primary kernel storage.

---

## 4. Kernel v2 Contract

### 4.1 Node state

```
NodeStateV2 = {
  nodeId      : Nat
  psi         : C x O
  tickCount   : Nat
  topoDepth   : Nat
  cache       : Optional DerivedCache
}
```

### 4.2 Derived cache (non-authoritative)

```
DerivedCache = {
  maybe_basis_tag     : Option (Fin 7 x Bool)
  maybe_vacuum_phase  : Option (Fin 4)
  last_validated_step : Nat
}
```

Constraint:

- Any cache mismatch with recomputed algebraic value is a deterministic validation error.

### 4.3 Time observables

Per RFC-018:

- `tau_topo`: causal depth progress
- `tau_int`: interaction/energy progress

Per RFC-019:

- temporal commit operator is `T(x) := e7 * x`

---

## 5. Required Theorems and Properties

### 5.1 Representation adequacy

Lean theorem target:

```
omega_representable_in_kernel_v2 : Exists psi, psi = omega
```

and explicit negative legacy theorem:

```
omega_not_in_legacy_signed_basis :
  omega not in { +/- e1, ..., +/- e7 }
```

### 5.2 Algebraic classification correctness

Theorems/properties:

1. `isVacuumOrbit` sound/complete over the 4-phase orbit.
2. `phase-only step => delta(tau_int)=0`.
3. `energy-exchange step => delta(tau_int)>0`.
4. Replay determinism with immutable eval plan.

### 5.3 Scheduler equivalence

Fixed-step and event-driven schedulers are equivalent at interaction boundaries for identical initial microstate and plan.

---

## 6. Implementation Plan

### 6.1 Lean

Add:

- `CausalGraphTheory/KernelV2.lean`
- optional: `CausalGraphTheory/KernelV2Bridge.lean`

Define:

- `NodeStateV2`
- algebraic predicate suite (`isVacuumOrbit`, `isPhaseOnlyStep`, `isEnergyExchange`)
- deterministic transition function on `psi`

Prove:

- representation adequacy + legacy insufficiency theorem
- predicate correctness for vacuum orbit and temporal commit behavior
- replay/scheduler equivalence lemmas (or theorem skeletons with finite executable checks where needed)

### 6.2 Python

Add/update:

- v2 node dataclass with full 8-component state
- deterministic algebraic predicate evaluators
- cache validation hooks
- migration adapter from legacy `(octIdx, sign)` nodes

Tests:

1. `omega` round-trip representability
2. vacuum orbit period-4 classification
3. phase-only and energy-exchange clock deltas
4. fixed-step vs event-driven equivalence
5. legacy adapter parity on states representable in legacy domain

---

## 7. Migration and Compatibility

### Phase A: Dual-path

- Keep v1 and v2 kernels in parallel.
- Run identical scenarios and compare where v1 domain is valid.

### Phase B: Default switch

- Make v2 default execution path.
- Keep v1 only for historical replay.

### Phase C: Retirement

- Mark v1 kernel code and v1-only claims as legacy/superseded where applicable.

---

## 8. Claim Governance Impact

1. Claims relying on label-based vacuum fixed-point semantics remain superseded.
2. Claims using vacuum orbit and phase-only logic must depend on Kernel v2 readiness.
3. No claim may cite v1 kernel behavior as evidence for RFC-019 temporal-axis semantics.

---

## 9. Non-goals

This RFC does not:

- derive continuum units of time,
- settle all mass-observable debates,
- prove full Standard Model emergence.

It only fixes representational consistency at the kernel layer.

---

## 10. Acceptance Gates

Kernel v2 is accepted when all are true:

1. `omega` is representable and exercised in runtime tests.
2. `isVacuumOrbit` is computed from algebraic state, not label metadata.
3. `tau_topo`/`tau_int` semantics are implemented and tested.
4. Fixed-step/event-driven equivalence passes on canonical scenarios.
5. Deterministic replay hash matches across repeated runs.
6. RFC-013, RFC-016, RFC-018, and RFC-019 contain no remaining representation contradiction.

---

## 11. Relationship to RFC-016

RFC-016 remains useful for determinism and plan immutability constraints, but its
Kernel v1 state representation is superseded by this RFC for temporal-axis and vacuum-orbit work.

If needed, a follow-up patch should mark RFC-016 section 3.1 as "legacy v1 representation."

