# RFC-027: Foundational Phenomena Validation Battery

Status: Active - Research and Validation Design Draft (2026-02-26)
Module:
- `COG.Benchmarks.Foundational`
- `COG.Benchmarks.Correlation`
- `COG.Benchmarks.PhaseLoop`
Depends on:
- `rfc/RFC-020_Kernel_Representation_Reconciliation.md`
- `rfc/RFC-021_Entanglement_Interaction_and_Causal_Projection.md`
- `rfc/RFC-022_Lightcone_Semantics_and_Causal_Locality.md`
- `rfc/RFC-023_Discrete_Phase_Clocks_and_Relative_Phase_Interactions.md`
- `rfc/RFC-025_Superconductivity_and_Ferroelectricity_Modeling.md`
- `rfc/RFC-026_Gauge_Constant_Derivation_Strategy.md`
Literature basis:
- `sources/foundational_phenomena_validation_lit_review.md`

---

## 1. Executive Summary

This RFC defines a validation battery of external physics phenomena to constrain COG core assumptions before deeper constant-fitting and spectrum claims.

Priority families:

1. Bell/CHSH with strict no-signaling audits.
2. Loop-phase responses (Aharonov-Bohm and Josephson/Shapiro analogs).
3. Confinement diagnostics (Wilson-loop area-law analogs).
4. Multi-period mixing/oscillation benchmarks.
5. Decoherence/pointer-state benchmarks.
6. Universality/critical-scaling benchmarks.
7. Precision spectral ladder checks.

---

## 2. Motivation

COG has strong local algebra/theorem momentum, but model risk remains:

1. overfitting to recent tasks,
2. promoting constants before validating core update semantics,
3. confusing analogy-level wins with mechanism-level evidence.

This RFC addresses that risk by forcing cross-domain falsification tests tied to base assumptions.

---

## 3. Core Assumptions Under Test

A1. Causal locality (`RFC-022`) is strict in kernel semantics.

A2. Discrete phase observables (`RFC-023`) are dynamically meaningful, not decorative.

A3. Entanglement/projection semantics (`RFC-021`) can reproduce nonclassical correlations without signaling leaks.

A4. Strong/gauge observables (`RFC-026`) correspond to real confinement-like structure, not static counting artifacts.

A5. Coarse-graining and observer projection produce uncertainty in a way consistent with decoherence-style behavior.

---

## 4. Validation Tracks

## T1. Correlation and no-signaling track (Bell/CHSH)

Goal:
- produce nonclassical correlation structure while preserving no-signaling in all kernel observables.

Required outputs:

1. `chsh_value` under declared measurement settings.
2. `signaling_leak_score` from perturbation-based locality checks.
3. deterministic replay consistency hash.

Fail conditions:

1. `chsh_value` never exceeds classical bound in any admissible regime.
2. nonzero signaling leak above tolerance.

## T2. Loop-phase track (AB + Josephson/Shapiro)

Goal:
- show loop-conditioned phase response and driven locking/step structure from COG phase semantics.

Required outputs:

1. loop phase-response curves.
2. locking plateau map under periodic forcing.
3. phase-slip event statistics.

Fail conditions:

1. no reproducible loop-sensitive phase response.
2. no stable locking regions under controlled drive.

## T3. Confinement track (Wilson-loop analog)

Goal:
- test whether strong-sector observables exhibit area-like loop scaling regimes.

Required outputs:

1. loop-cost scaling fits (`area`, `perimeter`, mixed models).
2. fit quality and model selection scores.
3. finite-size sensitivity table.

Fail conditions:

1. only perimeter-like behavior across tested regimes.
2. area-like regime appears only under fragile tuning.

## T4. Oscillation track (neutrino-like mixing analog)

Goal:
- verify robust multi-period mixing motifs and baseline/energy-like dependence.

Required outputs:

1. transition-probability surfaces versus baseline proxy and energy proxy.
2. extracted effective frequency differences.
3. replay-stable mixing matrix estimate (if defined).

Fail conditions:

1. no stable oscillation motifs.
2. oscillation patterns collapse under small perturbations.

## T5. Decoherence track

Goal:
- test whether coarse-grained observer projection plus environment coupling yields pointer-like stability and entropy growth behavior.

Required outputs:

1. coherence decay curves.
2. pointer-sector occupancy stability.
3. projection-loss vs uncertainty metrics.

Fail conditions:

1. no pointer-sector stabilization.
2. uncertainty metrics are inconsistent with projection-loss behavior.

## T6. Universality/critical track

Goal:
- test robustness via scaling behavior across different micro-motif choices.

Required outputs:

1. extracted critical-like exponents where applicable.
2. cross-motif universality comparisons.
3. ablation report for update-rule perturbations.

Fail conditions:

1. exponents or scaling collapse are non-reproducible.
2. behavior is highly motif-specific without structural explanation.

## T7. Precision spectrum track

Goal:
- benchmark whether electromagnetic-sector dynamics reproduce ladder/splitting structure, not just isolated ratio fits.

Required outputs:

1. spectral ladder for selected bound-state motifs.
2. splitting hierarchy diagnostics.
3. residual structure relative to baseline model family.

Fail conditions:

1. one-point fit only with no ladder coherence.
2. hierarchy unstable under replay or mild perturbation.

---

## 5. Evidence Modes and Promotion Rules

Each track result must be labeled with one mode:

1. `theorem_proved`
2. `simulation_supported`
3. `literature_analogy_only`

Promotion constraints:

1. no claim can move to `simulation_supported` without deterministic replay and ablation checks.
2. no claim can move to `theorem_proved` unless kernel-map properties are formalized in Lean.
3. no single benchmark outcome is sufficient for broad model-validation claims.

---

## 6. Priority and Sequencing

Execution priority:

1. T1 Correlation/no-signaling.
2. T2 Loop-phase.
3. T3 Confinement.
4. T5 Decoherence.
5. T4 Oscillation.
6. T6 Universality.
7. T7 Precision spectrum.

Rationale:
- first three directly test locality, phase semantics, and strong-sector structure.
- middle tracks constrain observation and multi-period dynamics.
- precision spectrum is high-value but should follow foundational locking.

---

## 7. Implementation Targets

## 7.1 Python benchmark scripts (minimum set)

1. `calc/bench_chsh_no_signaling.py`
2. `calc/bench_phase_loop_ab.py`
3. `calc/bench_josephson_shapiro.py`
4. `calc/bench_wilson_loop_scaling.py`
5. `calc/bench_mixing_oscillations.py`
6. `calc/bench_decoherence_pointer.py`
7. `calc/bench_universality_scaling.py`
8. `calc/bench_spectral_ladders.py`

## 7.2 Lean obligations (stubs acceptable initially)

1. no-signaling invariant skeleton linked to `RFC-022` locality definitions.
2. loop-winding integer-valuedness and replay invariance.
3. classifier determinism for confinement observables.
4. projection-map non-injectivity and observer-loss definitions.

---

## 8. Instrumentation Contract

Each benchmark run must emit:

1. standardized metadata (`seed`, `config_hash`, `trace_hash`),
2. primary metrics per track,
3. uncertainty estimates (variance + finite-size sensitivity),
4. ablation outcomes,
5. pass/fail verdict against track-specific criteria.

Output format:
- JSONL events plus markdown summary in `sources/`.

---

## 9. Governance and Claim Impact

1. `STRONG-001`, `WEINBERG-001`, and `ALPHA-001` cannot be promoted solely on ratio fits while T1-T3 remain untested.
2. Any entanglement-related claim must include explicit no-signaling audit output.
3. Any phase-related claim must include loop-phase or locking evidence, not only period statements.

---

## 10. Open Questions

1. Which minimal COG parameter set can satisfy T1-T3 simultaneously?
2. Are loop-phase and confinement signatures compatible under one fixed kernel configuration?
3. Does the projection model in `RFC-021` survive decoherence and no-signaling stress tests together?
4. Which benchmark is most discriminative for rejecting weak model variants quickly?

---

## 11. Acceptance Criteria for RFC-027

This RFC is operational when:

1. all T1-T7 scripts exist with deterministic smoke tests,
2. at least T1-T3 have first baseline runs and published summaries,
3. evidence-mode tags are applied in downstream claim updates,
4. manager/debugger workflow enforces track pass/fail logging.

---

## 12. References

See:
- `sources/foundational_phenomena_validation_lit_review.md`

