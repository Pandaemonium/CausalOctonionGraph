# RFC-019: e7 Temporal Axis and Vacuum-Photon Duality

**Status:** Active - Hypothesis and Architecture Draft (2026-02-25)  
**Module:** `COG.Core.TimeAxis`  
**Dependencies:** `rfc/CONVENTIONS.md`, `rfc/RFC-013_Algebraic_Vacuum_and_Causal_Spawning.md`, `rfc/RFC-017_Vacuum_Stabilizer_Reconciliation.md`, `rfc/RFC-018_Time_as_Graph_Depth_and_Interaction_Clock.md`, `rfc/RFC-020_Kernel_Representation_Reconciliation.md`

---

## 1. Executive Summary

This RFC formalizes the hypothesis:

`e7` is the distinguished temporal axis in COG because it is the vacuum axis fixed by the
vacuum stabilizer structure and because `e7`-action is the minimal ordered operation that
propagates phase/information through the vacuum sector.

In this framing:

1. `e7` defines orientation of the octonionic decomposition used by the model.
2. The vacuum state is `omega = 1/2 (1 + i e7)`.
3. The photon operator is left action by `e7`: `L_e7(x) = e7 * x`.
4. Time advancement is represented by ordered `e7`-mediated updates.

This RFC also resolves the apparent "vacuum vs photon" tension:

- `e7` inside `omega` is a state-defining axis.
- `e7` as `L_e7` is an update operator.

Same algebra element, different semantic role.

---

## 2. Literature Search Synthesis

The search targeted octonion vacuum structure, stabilizers of chosen imaginary directions,
and causal-order-first dynamics.

### 2.1 What literature supports directly

1. A chosen imaginary octonion direction can define a preferred decomposition and vacuum-like
   idempotent/projector structure in C x O model building.
   - Furey (2016): https://arxiv.org/abs/1603.04078
   - Furey (2016 thesis): https://arxiv.org/abs/1611.09182
   - Furey (2019): https://arxiv.org/abs/1910.08395
   - Furey and Hughes (2022): https://arxiv.org/abs/2209.13016
   - Furey and Stoica (2019): https://arxiv.org/abs/1904.03186

2. Octonionic non-associativity makes ordering operationally meaningful.
   - Non-associative flux backgrounds and ordered star-products:
     https://arxiv.org/abs/1207.0926
   - Review context:
     https://arxiv.org/abs/2012.11515

3. Causal-order-first programs support deriving dynamics/time from discrete causal structure
   rather than assuming continuum time first.
   - Bombelli et al. (1987): https://doi.org/10.1103/PhysRevLett.59.521
   - Rideout and Sorkin (1999): https://arxiv.org/abs/gr-qc/9904062
   - Surya (2019 review): https://arxiv.org/abs/1903.11544

4. CFS-octonion bridge framing supports "octonions for vacuum symmetry, causal dynamics for
   spacetime evolution."
   - Finster et al. (2024): https://arxiv.org/abs/2403.00360

### 2.2 What literature does not yet prove

No external source directly proves the exact COG statement:

"`e7` is the universal direction of temporal advance because it is the vacuum stabilizer axis."

This remains a COG postulate that must be validated by internal derivation and falsification tests.

---

## 3. Existing Internal Evidence (Lean and RFC)

Already proved/locked in this repository:

1. Vacuum axis and vacuum state conventions are locked to `e7`.
   - `rfc/CONVENTIONS.md`

2. `e7` left action on vacuum gives phase rotation.
   - `CausalGraphTheory/Spinors.lean`: `e7Left_on_omegaDoubled`

3. `e7` action has exact period 4 for nonzero states (left and right forms proved).
   - `CausalGraphTheory/Spinors.lean`: `universal_Ce_period_four`, `universal_Ce_right_period_four`

4. Vacuum stabilizer in the current finite encoding is identified as `S4` (not `SL(2,3)`).
   - `rfc/RFC-017_Vacuum_Stabilizer_Reconciliation.md`
   - `CausalGraphTheory/VacuumStabilizerS4.lean`

5. Two-clock time architecture (`tau_topo`, `tau_int`) is already established.
   - `rfc/RFC-018_Time_as_Graph_Depth_and_Interaction_Clock.md`

---

## 4. Reconciliation of Stabilizer Language

This RFC uses two distinct meanings of "stabilizer" and keeps them separate:

1. **Discrete kernel stabilizer (current Lean encoding):** finite stabilizer of the vacuum axis
   action in the Fano-permutation model, identified as `S4` (RFC-017).
2. **Continuous algebraic stabilizer (octonion literature):** stabilizer of a chosen imaginary
   unit inside the continuous automorphism context used in C x O constructions.

This RFC makes no claim that these two groups are the same object.  
The claim is weaker and operational: both frameworks single out a preferred axis, and COG
uses that axis as `e7`.

---

## 5. Core Postulates

### P1. Temporal Axis Postulate

`e7` is the unique temporal axis token in Kernel v2 dynamics.

### P2. Dual-role Postulate

`e7` has two role types:

1. **Vacuum role:** defines the vacuum axis inside `omega = 1/2 (1 + i e7)`.
2. **Propagation role:** defines the canonical time-advance operator `T := L_e7`.

### P3. Ordered-advance Postulate

A causal update contributes temporal progression only through deterministic ordered evaluation
that includes `T`-commit semantics.

### P4. Two-clock Compatibility

Every accepted implementation must preserve:

- `tau_topo`: causal depth progress
- `tau_int`: interaction/energy progress

`T`-applications always advance topological ordering; they advance interaction clock only when
`is_energy_exchange = true` (RFC-018).

---

## 6. Operational Semantics

Define:

- `T(x) := e7 * x`
- `isVacuumOrbit(x) := x in {omega, -i*omega, -omega, i*omega}`

At each deterministic local update:

1. Evaluate incoming causal messages using RFC-002 ordering.
2. Compute provisional state content update.
3. Apply temporal commit `T`.
4. If result is phase-only vacuum-orbit motion, count as topological progression only.
5. If result includes energy exchange by model predicate, increment interaction clock.

This makes "vacuum operator" and "photon operator" two outcomes of the same `e7` temporal commit.

---

## 7. Falsifiable Predictions and Tests

### Test A: Axis substitution stress test

Replace `e7` with another imaginary basis unit `ek` while preserving all other rules.

Expected under this RFC:

- Loss of current vacuum/projector alignment and degradation of existing low-cost
  propagation and/or symmetry structure.

### Test B: Remove `T`-commit and use generic operator-driven clocking

Expected under this RFC:

- Reduced replay invariance quality for time observables or increased ambiguity in
  null-step handling.

### Test C: Phase-only vs energy-exchange separation

Expected under this RFC:

- Vacuum-orbit transport events dominate `tau_topo` increments while only a subset
  increment `tau_int`.

### Test D: Scheduler equivalence

Fixed-step vs event-driven runs must agree at interaction boundaries even with explicit
`T`-commit phase.

---

## 8. Implementation Targets

### 8.1 Lean

Add module:

- `CausalGraphTheory/TimeAxis.lean`

Target definitions:

- `temporalCommit : CO -> CO := fun x => e7LeftOp * x`
- `isVacuumOrbit : CO -> Prop`
- `isPhaseOnlyTemporalStep : Transition -> Prop`

Target theorem skeletons:

- `temporalCommit_on_vacuum : temporalCommit omegaDoubled = negIOmegaDoubled`
- `temporalCommit_period4 : temporalCommit^[4] x = x` (for nonzero `x`, reuse existing stack)
- `phase_only_implies_no_tau_int_increment`

### 8.2 Python

Add to kernel/scheduler:

- explicit `temporal_commit_e7(state)` stage
- logging fields:
  - `used_temporal_commit`
  - `phase_only_step`
  - `tau_topo_delta`
  - `tau_int_delta`

Required tests:

1. deterministic replay with temporal commit on/off flag (off should fail acceptance)
2. axis substitution regression (`e7` vs `ek`) with metric comparison
3. fixed-step vs event-driven equivalence with temporal commit enabled

---

## 9. Non-goals and Caution

This RFC does not claim:

1. a full derivation of SI time units
2. a complete derivation of photon spectra
3. proof that external literature uniquely mandates `e7` as time axis

It claims that this is a coherent and testable COG architecture choice with partial
literature support and strong internal algebraic alignment.

---

## 10. Validation Checklist

- [ ] Temporal commit stage is explicit in simulator architecture.
- [ ] `tau_topo` and `tau_int` are both reported per run.
- [ ] `phase_only_step` is tracked and audited.
- [ ] Axis substitution stress test implemented.
- [ ] Scheduler equivalence still passes with temporal commit enabled.
- [ ] Claim docs referencing this postulate mark it as "active hypothesis" until tests pass.
