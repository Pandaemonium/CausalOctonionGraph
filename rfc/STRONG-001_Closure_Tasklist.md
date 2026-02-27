# STRONG-001 Closure Tasklist: Vacuum Stabilizer to Strong-Force Link

Status: Active execution plan  
Scope: Close the largest gaps between current proved facts and the strong-force claim (`claims/alpha_strong.yml`).
Governance note: confinement-grade interpretations must pass RFC-047 gates before promotion-grade status.

---

## 1. Goal and Exit Conditions

Primary goal:
- Replace the current leading-order proxy (`24/168 = 1/7`) with a defensible, kernel-level, dynamics-aware strong-force observable tied to the vacuum stabilizer.

Exit conditions:
1. The stabilizer identity and action are linked in one canonical Lean path (no split-witness ambiguity).
2. A deterministic trapped-vs-escaped operation classifier exists at Kernel v2 level.
3. Non-associative tick behavior is formally connected to stabilizer action (equivariance/invariance results).
4. Numerical pipeline measures `R(N)` with confidence intervals and finite-density corrections.
5. Claim status for `STRONG-001` is updated based on evidence (not optimism).

---

## 2. Baseline (Already Established)

These are currently available and should be treated as hard prerequisites:

1. Fano automorphism count = 168 (`GaugeGroup.fano_aut_count`).
2. Vacuum-axis stabilizer count = 24 (`GaugeGroup.vacuum_stabilizer_count`, `CausalGraph.vacuumStabilizerList_count`).
3. In current encoding, stabilizer is identified with S4-action structure, not SL(2,3) (`RFC-017` and related Lean checks).
4. Non-associative vs associative classification machinery exists (`SubalgebraDetect.batchable`, `Tick.classify`).
5. `STRONG-001` is still `stub` with unresolved ~21 percent gap.

---

## 3. Critical Open Gaps

Gap G1: Two stabilizer artifacts are not linked by one direct theorem.

Gap G2: "Trapped color-cycle operation" is not defined on runtime kernel transitions.

Gap G3: No theorem currently ties stabilizer action to tick-class behavior preservation.

Gap G4: No hadron-level confinement invariant is formalized at kernel dynamics level.

Gap G5: No statistical pipeline turns graph dynamics into an `alpha_s(Q)` comparison with uncertainty.

---

## 4. Work Packages

## WP-A: Canonical Stabilizer Link (Lean)

Objective:
- Collapse split proofs into one canonical subgroup object used by all downstream derivations.

Tasks:
1. Create `CausalGraphTheory/VacuumStabilizerBridge.lean`.
2. Define canonical stabilizer list alias in one namespace.
3. Prove list-level equivalence/permutation theorem between:
   - `GaugeGroup` stabilizer enumeration and
   - `VacuumStabilizerAction.vacuumStabilizerList`.
4. Re-export theorem in a stable import path for downstream use.

Suggested theorem names:
- `vacuum_stabilizer_lists_perm`
- `vacuum_stabilizer_lists_same_card`

Done criteria:
- `lake build` passes.
- GAUGE-001 blocked item "link theorem" can be checked off.

---

## WP-B: Kernel v2 Strong Observable Definition

Objective:
- Define strong-force observable at transition level, not only group-order level.

Tasks:
1. Add `CausalGraphTheory/StrongObservable.lean`:
   - `OperationClass := Trapped | Escaped`
   - `isTrappedOperation : Transition -> Bool`
2. Ensure predicate is computed from algebraic/kernal state only (RFC-020 compatible).
3. Prove classifier totality and exclusivity:
   - every transition classified,
   - never both trapped and escaped.

Done criteria:
- Lean proofs for total/exclusive classification.
- Documented mapping from transition record fields to classification.

---

## WP-C: Non-Associativity Coupling Theorems

Objective:
- Prove interaction between stabilizer symmetry and tick generation logic.

Tasks:
1. Add theorem:
   - `stabilizer_preserves_batchability`
2. Add theorem:
   - `stabilizer_preserves_tick_class`
3. Add theorem:
   - `stabilizer_orbit_tick_stats_invariant` (finite-sample/list form first is acceptable).

Target files:
- `CausalGraphTheory/SubalgebraDetect.lean`
- `CausalGraphTheory/Tick.lean`
- optionally new `CausalGraphTheory/StrongTickLink.lean`

Done criteria:
- At least first two theorems proved without `sorry`.
- Tick-class invariance available as reusable lemma for simulation correctness.

---

## WP-D: Hadron/Confinement Structure

Objective:
- Move from abstract trapped ratio to physically relevant color-singlet dynamics.

Tasks:
1. Define minimal proton motif state schema in Lean/Python.
2. Define color-singlet invariant predicate.
3. Prove/pseudo-prove (Lean finite checks acceptable initially):
   - trapped operations preserve singlet invariant.
4. Add simulation tests:
   - escaped operations produce nonzero singlet-break tendency under controlled perturbations.

Target files:
- Lean: `CausalGraphTheory/ProtonMotif.lean` (new)
- Python: `calc/proton_confinement_checks.py` (new)

Done criteria:
- Automated tests showing trapped/escaped behavioral separation.
- Clear statement of what is theorem vs empirical check.

---

## WP-E: Numerical Estimation and Scale Bridge

Objective:
- Quantify `R(N)` and connect to physical `alpha_s` scale dependence.

Tasks:
1. Add `calc/alpha_strong_trap_ratio.py`
   - estimate `R(N)` over increasing graph sizes.
2. Add `calc/alpha_strong_finite_density_fit.py`
   - fit correction term to leading `1/7`.
3. Add `calc/alpha_strong_scale_map.py`
   - map graph scale proxy to `Q`,
   - compare against reference running behavior.
4. Add reproducible report:
   - `sources/alpha_strong_closure_results.md`.

Done criteria:
- Confidence intervals reported.
- Sensitivity analysis across random seeds and initial microstates.
- Explicit "matches / does not match" verdict at chosen scales.

---

## WP-F: Claim and Governance Closure

Objective:
- Keep claim quality synchronized with evidence.

Tasks:
1. Update `claims/alpha_strong.yml` theorem/test list with new artifacts.
2. If evidence still incomplete:
   - keep `status: stub` or move to `partial` with exact unresolved gaps.
3. If closure criteria met:
   - move to `status: proved` only with theorem and simulation evidence references.
4. Add one-paragraph residual risk note either way.
5. Record confinement-gate status and artifact pointers used by RFC-047/RFC-049.

Done criteria:
- Claim status matches actual evidence state.
- No ambiguity between structural ratio and physical coupling derivation.

---

## 5. Recommended Execution Order (Critical Path)

1. WP-A (canonical stabilizer link)
2. WP-B (runtime observable definition)
3. WP-C (symmetry-to-tick theorem link)
4. WP-E (measurement pipeline)
5. WP-D (motif/confinement depth)
6. WP-F (claim status update)

Rationale:
- A/B/C define what is being measured.
- E measures it.
- D deepens physical interpretation.
- F finalizes claim governance.

---

## 6. Acceptance Checklist

- [ ] No new `sorry` in added Lean files.
- [ ] `lake build` clean.
- [ ] New Python scripts have deterministic tests and fixed-seed mode.
- [ ] Report includes confidence intervals and ablations.
- [ ] Claim wording avoids SL(2,3)-specific assumptions.
- [ ] Claim status updated with explicit evidence citations.

---

## 7. Common Failure Modes to Avoid

1. Treating `1/7` as final derivation instead of leading-order prior.
2. Mixing S4-encoding facts with old SL(2,3)/Q8 quotient arguments.
3. Using simulation outputs without uncertainty quantification.
4. Conflating "symmetry preserved" with "physical confinement derived".
5. Updating claim status before theorem and measurement gates are both passed.

---

## 8. Minimal Deliverables Package

Required files to consider STRONG-001 materially advanced:

1. `CausalGraphTheory/VacuumStabilizerBridge.lean`
2. `CausalGraphTheory/StrongObservable.lean`
3. `CausalGraphTheory/StrongTickLink.lean` (or equivalent additions)
4. `calc/alpha_strong_trap_ratio.py`
5. `calc/alpha_strong_finite_density_fit.py`
6. `calc/alpha_strong_scale_map.py`
7. `sources/alpha_strong_closure_results.md`
8. Updated `claims/alpha_strong.yml`
