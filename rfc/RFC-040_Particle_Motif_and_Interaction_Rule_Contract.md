# RFC-040: Particle Motif and Interaction Rule Contract

Status: Active - Contract Draft (2026-02-26)
Module:
- `COG.Core.ParticleMotif`
- `COG.Core.InteractionRuleRegistry`
Depends on:
- `rfc/CONVENTIONS.md`
- `rfc/RFC-022_Lightcone_Semantics_and_Causal_Locality.md`
- `rfc/RFC-023_Discrete_Phase_Clocks_and_Relative_Phase_Interactions.md`
- `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
- `rfc/RFC-038_Vacuum_Phase_Locking_and_Higgs_Mechanism.md`
- `rfc/RFC-039_Charge_as_Discrete_Z4_Cycle.md`
- `rfc/RFC-043_Motif_Catalog_v1.md`
- `rfc/RFC-044_Projection_Profile_Governance.md`
- `rfc/RFC-047_Confinement_Claim_Gates.md`
- `rfc/RFC-054_Observable_Equivalence_and_Physical_Indistinguishability.md`
- `rfc/RFC-056_Spin_as_Missing_H_Factor.md`

---

## 1. Executive Summary

This RFC defines the canonical way COG should model "real physics" in practice:

1. **Dynamics are primary:** node state evolves in `C x O` by deterministic local rules.
2. **Particles are motifs, not labels:** a particle is a stable orbit/signature of the update rule.
3. **Observables are projections:** measured quantities are maps from microstate to observer state.

The goal is to prevent conceptual drift between:
- algebraic phase periodicity,
- charge observables,
- interaction semantics,
- physical claims.

---

## 2. Problem

Current RFCs and Lean files contain strong pieces, but they are distributed:

- kernel state and update contracts (`KernelV2`, `UpdateRule`),
- phase clocks (`PhaseClock`),
- charge projection (`WeakMixingObservable`),
- two-node polarity (`TwoNodeSystem`),
- spawn/projection contracts (`D4D5Contracts`),
- spin observable mode contract (`RFC-056`).

Without a single motif/rule contract, teams can over-interpret hypotheses (e.g., "charge = Z4 phase") beyond what is currently proved.

---

## 3. Layered Physics Contract

### L1. Microdynamics (kernel truth)

A node state is:

`NodeStateV2 = {nodeId, psi : CxO(Z), tickCount, topoDepth, colorLabel}`.

One-step update is:

`psi_{t+1} = combine(temporal_commit(psi_t), interactionFold(msgs))`

with currently locked defaults:

1. `temporal_commit(s) = e7 * s.psi`
2. `combine(a,b) = a * b`
3. `interactionFold = foldl (*) 1`
4. `isEnergyExchangeLocked(msgs) = (msgs != []) && (interactionFold(msgs) != 1)`

Reference: `CausalGraphTheory/UpdateRule.lean`.

### L2. Motif identity (particle definition)

A particle motif is a tuple:

`Motif := (SeedState, UpdateFamily, OrbitPredicate, ObservableSignature, StabilityGate)`

where:

1. `SeedState` is a concrete CxO seed,
2. `UpdateFamily` is a declared interaction regime,
3. `OrbitPredicate` defines motif closure/periodicity,
4. `ObservableSignature` defines charge/phase sector outputs,
5. `StabilityGate` defines persistence criteria.

### L3. Projection (measurement truth)

Physical claims must specify projection profile:

1. `piObsMinimal` for phase/charge/topology-level claims,
2. `piObsWithSector` for color-sector-sensitive claims.

Reference: `CausalGraphTheory/D4D5Contracts.lean`.

---

## 4. Canonical Motif Registry (Current)

## M1. Vacuum motif (locked)

Seed:
- `omega_vac` / `vacuumState`

Signature:
- phase orbit in 4-cycle under `e7` action,
- cone/colorless support in `{e0, e7}` for known photon-stack results.

Evidence:
- Lean proved (`Spinors.lean`, `KernelV2.lean`).

## M2. Electron motif (locked at algebraic state level)

Seed:
- `fureyElectronStateDoubled`

Signature:
- nonzero,
- exact period-4 under e7 stack,
- U(1) charge sign negative under current `u1Charge` observable.

Evidence:
- Lean proved (`FureyChain.lean`, `Spinors.lean`, `TwoNodeSystem.lean`).

## M3. Positron-like dual motif (locked at algebraic state level)

Seed:
- dual-chain state (Furey dual electron construction)

Signature:
- opposite U(1) sign to electron under current observable.

Evidence:
- Lean + Python harness.

## M4. Two-node interaction-class motif (locked, pre-kinematic)

Seed:
- any pair `(psi1, psi2)`

Signature:
- repulsive / attractive / neutral classification from:
  - energy-exchange gate,
  - U(1) sign relation.

Evidence:
- Lean theorem (`ee_repulsion_predicate`) + Python matrix tests.

Non-goal:
- not yet a scattering trajectory model.

---

## 5. Charge and Phase: Required Separation

### C1. What is established

1. Imaginary-unit actions have period-4 orbit structure in current theorem stack.
2. Local phase observable can be represented as `tickCount mod 4` in current phase-clock module.

### C2. What must not be conflated

1. "Has a 4-cycle" does not imply "same physical charge".
2. Phase-class equality does not imply equal charge operator value.
3. Charge quantization claims require operator-spectrum arguments, not periodicity alone.

### C3. Contract language

Use:
- "Z4 periodic scaffold" for orbit-level claims,
- "charge observable/operator" for measured charge claims.

---

## 6. Interaction Rule Registry

Every physics claim must declare which rule profile was used.

## R1. Boundary-locality profile

- only cone-local boundary messages are admissible inputs.

## R2. Ordering profile

- deterministic total order + fixed parenthesization.

## R3. Combine/fold profile

- multiplicative combine, Markov fold (current locked default).

## R4. Spawn profile

- D4 contracts: active-cone gating, completeness, spawn-then-update sequencing.

## R5. Projection profile

- D5 minimal or extended projection must be explicit in claim metadata.

## R6. Pair polarity profile

- for two-node claims, indicate receiver-oriented or symmetric-pair predicate.

## R7. Confinement claim profile

- confinement language in claim docs is valid only after RFC-047 gate requirements are passed.

## R8. Spin mode profile

- spin-sensitive claims must declare `spin_mode`.
- allowed modes: `parity`, `label`, `algebraic`.
- precision spin claims require `spin_mode: algebraic`.

---

## 7. Evidence Levels (Mandatory in claim docs)

Every motif/rule statement must be tagged:

1. `lean_proved`
2. `python_verified`
3. `hypothesis`

Claims may compose levels, but the weakest level governs the claim status.

---

## 8. Immediate Deliverables

## 8.1 Lean scaffold

Add:
- `CausalGraphTheory/ParticleMotifContract.lean`

Initial definitions:
- `structure ParticleMotif`
- `def motifStableOverN`
- `def motifSignature`

Initial theorem targets:
1. vacuum motif closure under period-4 orbit,
2. electron motif nontriviality and phase periodicity,
3. electron vs positron-like opposite-sign signature under `u1Charge`.

## 8.2 Python harness

Add:
- `calc/motif_registry.py`
- `calc/test_motif_registry.py`

Checks:
1. deterministic replay of motif traces,
2. signature extraction consistent with declared projection profile,
3. explicit fail if claim omits rule profile.

## 8.3 Governance integration

Update claim template:
- add required fields:
  - `motif_id`
  - `rule_profile`
  - `pi_obs_profile`
  - `projection_sensitivity`
  - `equivalence_mode` (when equivalence language is used)
  - `spin_mode` (for spin-sensitive claims)
  - `evidence_level`

---

## 9. Falsification Gates

### G1. Projection fragility gate

If a claim outcome flips when changing from `piObsMinimal` to `piObsWithSector`, mark as projection-sensitive and downgrade broad physical interpretation.

### G2. Rule-profile drift gate

If outcome depends on undocumented rule variations (ordering/fold/combine), claim is invalid until profile is declared and replay-locked.

### G3. Phase-charge conflation gate

Reject any claim that infers charge magnitude solely from phase periodicity without operator/projection proof.

### G4. Motif stability gate

A particle motif claim requires explicit finite-horizon stability evidence or theorem; otherwise classify as exploratory.

### G5. Spin-mode mismatch gate

Reject spin-sensitive claims whose wording exceeds declared `spin_mode` strength.

---

## 10. Relation to RFC-039

RFC-039 is retained as the high-level charge hypothesis.

This RFC adds operational constraints:

1. converts charge-cycle narrative into a layered contract,
2. enforces separation between orbit periodicity and observable charge,
3. defines motif/rule/projection metadata required for credible physics claims.

RFC-039 answers "what might charge be."  
RFC-040 answers "how we are allowed to claim it in this codebase."

---

## 11. Acceptance Criteria

This RFC is closed when:

1. `ParticleMotifContract.lean` exists with the scaffold and at least two motif theorem connections,
2. motif registry Python tests pass,
3. claim template includes motif/rule/projection/evidence fields,
4. at least one existing claim is migrated to full RFC-040 metadata.
