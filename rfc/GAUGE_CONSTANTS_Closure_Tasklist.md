# Gauge Constants Closure Tasklist (STRONG-001, WEINBERG-001, ALPHA-001)

Status: Active execution plan
Scope:
- `claims/alpha_strong.yml`
- `claims/weinberg_angle.yml`
- `claims/alpha_fine_structure.yml`
Strategy source:
- `rfc/RFC-026_Gauge_Constant_Derivation_Strategy.md`

---

## 1. Goal and Exit Conditions

Primary goal:
- produce one S4-consistent, scale-declared, reproducible derivation pipeline for `alpha_s`, `sin^2(theta_W)`, and `alpha_em`.

Exit conditions:
1. canonical observables are defined once and reused across all three constants,
2. Lean invariance and determinism obligations are satisfied without `sorry`,
3. Python estimators produce uncertainty-aware outputs with deterministic replay,
4. claim statuses reflect evidence quality (no optimistic promotion).

---

## 2. Baseline (Already Established)

1. vacuum stabilizer reconciliation to S4 is documented (`RFC-017`).
2. kernel representation direction is CxO-native (`RFC-020` track).
3. locality/instrumentation framework exists (`RFC-022`).
4. current constant claims remain `stub` with known blocked reasons.

---

## 3. Critical Open Gaps

Gap G1:
- no canonical shared observable contract across the three claims.

Gap G2:
- weak/hypercharge projector definitions are not formally locked.

Gap G3:
- strong trapped/escaped runtime classifier is not fully formalized at kernel transition level.

Gap G4:
- graph-scale to physics-scale mapping is not standardized.

Gap G5:
- claim metadata does not yet record full evidence-mode and ablation results.

---

## 4. Work Packages

## WP-A: Canonical Gauge Observable Layer (Lean)

Objective:
- define one reusable observable contract for all three constants.

Tasks:
1. Add `CausalGraphTheory/GaugeObservables.lean`.
2. Define:
   - `O_strong`
   - `O_weak`
   - `O_hyper`
   - `O_mix`
3. Prove observable extraction determinism for fixed trace input.

Done criteria:
- module builds clean,
- all three claim pipelines can import the same definitions.

---

## WP-B: Weak Mixing Formalization (Lean + Python)

Objective:
- close WEINBERG-001 prerequisites with fixed projector semantics.

Tasks:
1. Add `CausalGraphTheory/WeakMixingObservable.lean`.
2. Define canonical weak/hypercharge projectors.
3. Prove invariance/equivariance lemmas under allowed symmetries.
4. Add `calc/estimate_weinberg_angle.py`.
5. Add tests for deterministic replay and projector-ablation sensitivity.

Done criteria:
- `sin2_thetaW_candidate(Q_ref)` emitted with uncertainty,
- claim file can move from `stub` to `partial` if gates pass.

---

## WP-C: Strong Observable Closure (Lean + Python)

Objective:
- close STRONG-001 with a runtime transition classifier and finite-size analysis.

Tasks:
1. Add or finalize `CausalGraphTheory/StrongObservable.lean`.
2. Define `OperationClass := Trapped | Escaped`.
3. Prove classifier totality and exclusivity.
4. Add `calc/estimate_alpha_strong.py`.
5. Add finite-size trend and sensitivity analyses.

Done criteria:
- `alpha_s_candidate(Q_ref)` emitted with confidence interval,
- explicit residual-gap note documented if mismatch remains.

---

## WP-D: Electromagnetic Consequence Map (Lean + Python)

Objective:
- derive ALPHA-001 from electroweak observables, not standalone formula hunting.

Tasks:
1. Add `CausalGraphTheory/AlphaEMObservable.lean` (or extend GaugeObservables module).
2. Define `alpha_em` map from `O_mix`.
3. Add `calc/estimate_alpha_em.py`.
4. Add regression test that fails if electroweak definitions change without synchronized alpha_em update.

Done criteria:
- `alpha_em_candidate(Q_ref)` produced with explicit dependency trace.

---

## WP-E: Shared Scale Bridge and Reporting

Objective:
- enforce one global scale convention and result format.

Tasks:
1. Add `calc/gauge_scale_bridge.py`.
2. Define `Q_ref` policy and graph-scale proxy mapping.
3. Emit standard report artifact:
   - `sources/gauge_constants_closure_results.md`
4. Include uncertainty decomposition:
   - estimator variance,
   - finite-size bias,
   - scale-map uncertainty.

Done criteria:
- all three constants are reported at the same declared `Q_ref` policy.

---

## WP-F: Claims and Governance Sync

Objective:
- keep claim files aligned with actual evidence.

Tasks:
1. Update `claims/weinberg_angle.yml`.
2. Update `claims/alpha_strong.yml`.
3. Update `claims/alpha_fine_structure.yml`.
4. Add explicit sections:
   - derivation map used,
   - scale convention,
   - ablation outcomes,
   - residual risks.

Done criteria:
- no claim remains ambiguous about evidence mode.

---

## 5. Recommended Execution Order (Critical Path)

1. WP-A
2. WP-B
3. WP-C
4. WP-E
5. WP-D
6. WP-F

Rationale:
- lock definitions first,
- estimate strong/weak on shared footing,
- then derive `alpha_em` as dependent consequence,
- then update claim statuses.

---

## 6. Acceptance Checklist

- [ ] no new `sorry` in modified Lean files
- [ ] `lake build` passes
- [ ] estimator scripts are fixed-seed reproducible
- [ ] shared scale policy declared and enforced
- [ ] ablation table included in closure report
- [ ] claim statuses updated with explicit evidence citations

---

## 7. Common Failure Modes to Avoid

1. retrofitting formulas after seeing target constants.
2. per-constant scale tuning.
3. mixing deprecated SL(2,3)-specific arguments into S4 encoding.
4. conflating simulation fit with theorem-level derivation.
5. updating claim status without uncertainty and ablation evidence.

---

## 8. Minimal Deliverables Package

1. `rfc/RFC-026_Gauge_Constant_Derivation_Strategy.md`
2. `CausalGraphTheory/GaugeObservables.lean`
3. `CausalGraphTheory/WeakMixingObservable.lean`
4. `CausalGraphTheory/StrongObservable.lean` (or canonical equivalent)
5. `CausalGraphTheory/AlphaEMObservable.lean` (or canonical equivalent)
6. `calc/estimate_weinberg_angle.py`
7. `calc/estimate_alpha_strong.py`
8. `calc/estimate_alpha_em.py`
9. `calc/gauge_scale_bridge.py`
10. `sources/gauge_constants_closure_results.md`
11. updated `claims/weinberg_angle.yml`
12. updated `claims/alpha_strong.yml`
13. updated `claims/alpha_fine_structure.yml`

