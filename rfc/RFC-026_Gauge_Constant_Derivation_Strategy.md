# RFC-026: Strategy for Deriving Gauge-Sector Constants

Status: Active - Derivation Strategy Draft (2026-02-26)
Module:
- `COG.Core.GaugeObservables`
- `COG.Core.ScaleBridge`
Depends on:
- `rfc/RFC-017_Vacuum_Stabilizer_Reconciliation.md`
- `rfc/RFC-020_Kernel_Representation_Reconciliation.md`
- `rfc/RFC-022_Lightcone_Semantics_and_Causal_Locality.md`
- `rfc/RFC-023_Discrete_Phase_Clocks_and_Relative_Phase_Interactions.md`
- `claims/alpha_strong.yml`
- `claims/weinberg_angle.yml`
- `claims/alpha_fine_structure.yml`

---

## 1. Executive Summary

This RFC defines a single strategy for three targets:

1. `STRONG-001`: strong coupling proxy (`alpha_s` at a declared reference scale).
2. `WEINBERG-001`: weak mixing angle (`sin^2(theta_W)` at a declared reference scale).
3. `ALPHA-001`: fine-structure constant (`alpha_em`) as an electroweak consequence.

Core rule:
- do not derive the three constants from independent heuristics;
- derive them from one shared gauge-observable layer, then compare at one explicit scale convention.

---

## 2. Motivation

Current claim files have useful ingredients but also known failure modes:

1. residual numerology risk (integer-ratio fitting after seeing the answer),
2. scale ambiguity (mixing low-energy and high-energy values),
3. old SL(2,3)-specific assumptions now invalid under RFC-017 (S4 reconciliation).

This RFC reduces those risks by forcing one coherent derivation pipeline.

---

## 3. Scope and Non-Scope

## 3.1 In scope

1. Defining canonical COG observables for strong and electroweak sectors.
2. Proving representation invariance of those observables (Lean).
3. Computing constant candidates from deterministic simulation traces (Python).
4. Updating claim statuses based on evidence gates.

## 3.2 Out of scope

1. Full Yukawa matrix derivation.
2. CKM/PMNS phase derivations.
3. Absolute fermion masses.
4. Full QFT renormalization proof inside Lean.

---

## 4. Canonical Observable Contract (New)

All three constants must derive from observables in one contract:

1. `O_strong(trace)`:
   - trapped vs escaped color-channel statistics under S4-consistent stabilizer action.
2. `O_weak(trace)`:
   - weak-isospin channel weight under fixed projector definitions.
3. `O_hyper(trace)`:
   - hypercharge/U(1)-like channel weight under fixed projector definitions.
4. `O_mix(trace)`:
   - mixed electroweak channel coupling map derived from `O_weak` and `O_hyper`.

No formula may introduce an extra ad hoc observable not in this contract.

---

## 5. Derivation Strategy by Constant

## 5.1 STRONG-001 (`alpha_s`)

Target:
- derive a scale-declared strong coupling proxy from trapped/escaped channel dynamics.

Method:
1. Define a runtime classifier on transitions: `Trapped | Escaped`.
2. Prove classifier totality/exclusivity in Lean.
3. Estimate `R(N)` and finite-density correction terms over increasing graph sizes.
4. Map graph scale proxy to declared physical comparison scale.

Required output:
- `alpha_s_candidate(Q_ref)` with confidence interval and sensitivity report.

## 5.2 WEINBERG-001 (`sin^2(theta_W)`)

Target:
- derive weak mixing from a projector/coupling ratio that is invariant under allowed basis actions.

Method:
1. Define canonical weak and hypercharge projectors.
2. Prove projector traces/weights are representation-invariant under admissible symmetries.
3. Compute `sin^2(theta_W)_candidate` from the observable contract, not from hand-picked dimension ratios.

Required output:
- `sin2_thetaW_candidate(Q_ref)` plus ablation showing which assumptions drive the value.

## 5.3 ALPHA-001 (`alpha_em`)

Target:
- derive `alpha_em` as a consequence of electroweak observables rather than an independent fit.

Method:
1. Use `O_mix` relation from `O_weak` and `O_hyper`.
2. Declare one normalization convention and reuse it globally.
3. Produce `alpha_em_candidate(Q_ref)` from the same pipeline used for `sin^2(theta_W)`.

Required output:
- `alpha_em_candidate(Q_ref)` with explicit dependency chain to WEINBERG observable definitions.

---

## 6. Recommended Execution Order

For implementation (not priority ranking), use this order:

1. lock electroweak observable definitions (`WEINBERG-001` prerequisites),
2. lock strong observable classifier (`STRONG-001` prerequisites),
3. run joint scale bridge,
4. derive `alpha_em` from electroweak map.

Rationale:
- `alpha_em` is structurally downstream of electroweak definitions in this strategy.

---

## 7. Scale Convention Rules

Every reported candidate must include:

1. declared comparison scale `Q_ref`,
2. mapping from graph-scale proxy to `Q_ref`,
3. uncertainty from scale mapping.

Hard constraints:

1. no per-constant scale tuning,
2. at most one global calibration constant for the whole gauge pipeline,
3. no claim can compare to PDG values without scale declaration.

---

## 8. Proof and Simulation Split

## 8.1 Lean obligations

1. formal definitions of canonical observables,
2. invariance/equivariance theorems under allowed symmetries,
3. determinism/replay invariance of extraction maps,
4. no new `sorry`.

## 8.2 Python obligations

1. estimator scripts for each observable family,
2. finite-size and sensitivity analysis,
3. fixed-seed reproducibility tests,
4. machine-readable result artifacts for dashboard/debugger ingestion.

---

## 9. Promotion Gates (Claim Governance)

A constant claim may move from `stub` to `partial` only when:

1. canonical observable definition exists,
2. corresponding Lean invariance checks pass,
3. deterministic estimator exists with uncertainty.

A claim may move from `partial` to `proved` only when:

1. derivation map is fixed and non-retrofitted,
2. cross-checks pass under ablations and perturbations,
3. scale mapping is declared and stable,
4. evidence citations are complete in claim metadata.

---

## 10. Anti-Numerology Safeguards

The following are disallowed:

1. choosing formulas by proximity to known constants without prior derivation,
2. changing projector definitions after seeing mismatch,
3. using SL(2,3)-specific quotient arguments in reconciled S4 encoding,
4. promoting status based on one lucky simulation run.

---

## 11. Deliverables Required by This RFC

1. New tasklist file:
   - `rfc/GAUGE_CONSTANTS_Closure_Tasklist.md`
2. New or updated Lean modules:
   - `CausalGraphTheory/GaugeObservables.lean`
   - `CausalGraphTheory/WeakMixingObservable.lean`
   - `CausalGraphTheory/StrongObservable.lean` (or equivalent canonical location)
3. New Python scripts (minimum):
   - `calc/estimate_alpha_strong.py`
   - `calc/estimate_weinberg_angle.py`
   - `calc/estimate_alpha_em.py`
   - `calc/gauge_scale_bridge.py`
4. Claim updates:
   - `claims/alpha_strong.yml`
   - `claims/weinberg_angle.yml`
   - `claims/alpha_fine_structure.yml`

