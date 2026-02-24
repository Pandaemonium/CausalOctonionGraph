# RFC-016: Kernel v1 Contract â€” Simulation State and Algebraic Semantics

**Status:** Active â€” Architecture Draft (2026-02-24)
**Module:** `COG.Core.Kernel`
**Dependencies:** `rfc/RFC-001_Canonical_State_and_Rules.md`, `rfc/RFC-002_Deterministic_Tick_Ordering.md`

## 1. Executive Summary

This RFC establishes a two-layer contract separating simulation state from
algebraic semantics. Without this separation, Lean proofs reason about
`ComplexOctonion` algebraic identities while the Python simulator updates
`OctIdx` integer indices â€” and there is no formal bridge between them.
Results proved over the algebra may be irrelevant to what the simulator
actually computes.

**Two-layer contract:**

- **Layer 1 â€” `KernelState`**: The minimal data structure the simulation
  stores and updates. Directly implementable in both Lean 4 and Python.
- **Layer 2 â€” `SemanticMap`**: A total function
  `SemanticMap : KernelState -> C*O` that interprets each simulator state
  as an element of the algebraic universe. All physics claims are statements
  about `SemanticMap(KernelState)`, not about raw `KernelState` integers.

**Gate condition:** No new physics claims shall be accepted into `claims/`
until both the Lean and Python implementations satisfy this contract and
the `SemanticConsistency` theorem is proved.

---

## 2. Motivation: The Kernel/Spec Drift Problem

RFC-001 Â§3 specifies node states as discrete `OctIdx` values (integers 1-7
selecting imaginary octonion basis elements) with explicit branching under
non-associative update. `State.lean` currently implements nodes as
`ComplexOctonion` values using a placeholder update rule. There is no
formal bridge between these two representations.

This drift has two immediate consequences:

1. **Lean proofs are algebraically valid but simulation-irrelevant.**
   Proofs about `FormalComplex Int` component equalities (e.g., PHOTON-001)
   do not directly prove properties of the `OctIdx`-based simulator. They
   prove properties of the algebra, not the kernel.

2. **Simulation results cannot be cited as evidence for algebraic claims.**
   Gate counts, recurrence times, and tick ratios from `calc/mass_drag.py`
   cannot be trusted as evidence for claims about C*O algebra properties
   until the representations are formally aligned.

The kernel/spec drift is architectural debt, not cleanup. It must be
resolved before new physics claims are made.

---

## 3. Layer 1 â€” KernelState Specification

### 3.1 Node State

A `KernelState` node carries exactly:

```
NodeState = {
  nodeId    : Nat           -- globally unique, assigned at creation
  octIdx    : Fin 7         -- index into {e1,...,e7}
  sign      : Bool          -- true = +1, false = -1 (chirality)
  tickCount : Nat           -- accumulated forced-tick evaluations
}
```

**Rationale for `octIdx : Fin 7`:**
RFC-001 specifies node states on the 7 imaginary basis elements.
Kernel v1 stores signed imaginary basis states only. The C*O algebra is
the semantic universe; it is not stored directly in kernel nodes.

**Rationale for explicit `sign : Bool`:**
MU-001 simulation records (phase 11, 2026-02-22) established that
collapsing +eN and -eN produces incorrect recurrence counts and invalid
gate densities. Chirality is a first-class simulation variable. The
signed state `(octIdx, sign)` is the minimal representation that correctly
tracks the non-associative update steps.

### 3.2 Edge State

```
EdgeState = {
  edgeId     : Nat    -- globally unique
  source     : Nat    -- source NodeId
  target     : Nat    -- target NodeId
  operator   : Fin 7  -- which imaginary basis operator to apply (e1..e7)
  operSign   : Bool   -- sign of the operator
}
```

### 3.3 Graph State

```
KernelState = {
  nodes    : List NodeState
  edges    : List EdgeState
  step     : Nat            -- global step counter
  evalPlan : GlobalEvalPlan -- immutable (RFC-002 Â§3.2), single source of truth
}
```

---

## 4. Layer 2 â€” SemanticMap

The `SemanticMap` interprets a `KernelState` in the algebraic universe.

### 4.1 Per-node semantics

```
nodeSemantics : NodeState -> C*O
nodeSemantics nd = sign_coeff(nd.sign) * imag_basis_element(nd.octIdx)
```

where:
- `imag_basis_element : Fin 7 -> C*O` returns the imaginary basis
  element embedded as `1 *_C e_(k+1)`.
- `sign_coeff(true) = +1`, `sign_coeff(false) = -1`.

### 4.2 Per-edge semantics

```
edgeSemantics : EdgeState -> C*O
edgeSemantics e = sign_coeff(e.operSign) * imag_basis_element(e.operator)
```

### 4.3 Update semantics

The algebraic update rule must match RFC-001's 3-body interaction.
For source state `a`, operator `g`, and destination state `b`:

```
leftBranch  = (a * g) * b
rightBranch = a * (g * b)

SemanticUpdate(a, g, b, paren_choice) =
  if paren_choice = Left then leftBranch else rightBranch
```

`paren_choice` is read from immutable `evalPlan` metadata (RFC-002).
No runtime branch choice is allowed in Kernel v1.

---

## 5. Correctness Invariants

### 5.1 Semantic Consistency (the key theorem)

For every update `step(G) = G'` and interaction event `(src, edge, dst)`:

```
nodeSemantics(step_node(src, edge, dst)) =
  SemanticUpdate(
    nodeSemantics(src),
    edgeSemantics(edge),
    nodeSemantics(dst),
    paren_choice(evalPlan, dst, edge)
  )
```

This theorem must be proved in Lean before the kernel is accepted.

### 5.2 Determinism (RFC-002)

`step(G) = G'` is a pure function of `G` with no hidden inputs.

### 5.3 Sign Preservation

The sign field evolves according to the octonion multiplication sign tensor
from `rfc/CONVENTIONS.md Â§2`, not an approximation.

### 5.4 Tick-mode Determinism

Tick/Batch classification must be a deterministic function of kernel data
and `CONVENTIONS.md` (no runtime heuristics or randomness).

### 5.5 Plan Immutability (RFC-002 Â§3.2)

`evalPlan` fields are unchanged across all steps.

---

## 6. Implementation Targets

### 6.1 Lean

- Define `NodeState`, `EdgeState`, `KernelState` in a new file
  `CausalGraphTheory/Kernel.lean`.
- Define `nodeSemantics : NodeState -> ComplexOctonion Int`.
- Define triadic `semanticUpdate` matching RFC-001 Â§3.
- Prove `SemanticConsistency` (Invariant 5.1).
- Update `State.lean`, `Update.lean`, `Mass.lean` to use `KernelState`
  rather than raw `ComplexOctonion` node values.

### 6.2 Python

- Define `@dataclass NodeState` with `oct_idx: int`, `sign: bool`,
  `tick_count: int`.
- Implement `node_semantics(nd) -> ComplexOctonion`.
- Update `calc/mass_drag.py` to use `KernelState`-compliant structures.
- Add test: triadic semantic consistency for `(src, op, dst)` updates with fixed plan.

---

## 7. Migration from Current State

The current `State.lean` uses `ComplexOctonion` as the node state type directly.
Migration is a three-phase process to avoid invalidating existing proofs:

**Phase A (introduce):**
Introduce `KernelState` as a new type alongside the existing types.
Implement `SemanticMap` and prove consistency on kernel-supported states
(signed imaginary basis states). Existing `Spinors.lean` projector/superposition
theorems remain algebraic-level results and are not part of Kernel v1 state storage.

**Phase B (bridge):**
Prove `SemanticConsistency`. This is the gate for accepting the kernel.

**Phase C (replace):**
Replace `State.lean` implementations with `KernelState`-based ones.
Retire the `ComplexOctonion`-as-state placeholder.

---

## 8. Claim Labelling During Migration

Until RFC-016 is fully implemented:

- Claims proved purely over `ComplexOctonion` algebraic identities shall
  include `algebraic_only: true` in their YAML metadata. Example: PHOTON-001 P2.

- Claims about simulation output (tick counts, gate densities, recurrence
  times) shall include `simulation_only: true`. Example: MU-001 simulation
  records.

- No claim may be cited as evidence for the physical world until it is
  either proved at the `KernelState` level, or the `SemanticConsistency`
  bridge theorem is proved connecting it to a `KernelState` result.

---

## 9. Validation Checklist

- [ ] `KernelState` defined in `CausalGraphTheory/Kernel.lean` (Lean 4).
- [ ] `nodeSemantics` defined and typechecks.
- [ ] `SemanticConsistency` proved (no sorry).
- [ ] Python `NodeState` dataclass matches Lean field-for-field.
- [ ] `node_semantics` unit test passes for all 14 (octIdx, sign) pairs.
- [ ] Triadic semantic consistency test passes for `(src, op, dst)` updates.
- [ ] `State.lean` and `Update.lean` updated to import `Kernel.lean`.
- [ ] `calc/mass_drag.py` updated to use KernelState-compliant data.

