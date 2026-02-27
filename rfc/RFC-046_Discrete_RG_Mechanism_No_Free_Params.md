# RFC-046: Discrete RG Mechanism (No Free Parameters)

Status: Active - Analysis Draft (2026-02-26)
Module:
- `COG.Core.DiscreteRG`
Depends on:
- `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
- `rfc/RFC-029_Weinberg_Angle_Gap_Closure.md`
- `rfc/RFC-037_Weinberg_Derivation_Avenues_and_Gates.md`
- `rfc/RFC-038_Vacuum_Phase_Locking_and_Higgs_Mechanism.md`
- `rfc/RFC-040_Particle_Motif_and_Interaction_Rule_Contract.md`
Related artifacts:
- `calc/weinberg_associator_running.py`
- `calc/weinberg_associator_ensemble.py`
- `calc/weinberg_associator_ensemble_conditions.json`

---

## 1. Executive Summary

This RFC defines how COG should model running-like behavior (including Weinberg-angle evolution) without fitted attenuation constants.

Core position:
1. Running must emerge from repeated application of locked microdynamics under predeclared environment ensembles.
2. No free attenuation or target-tuned constants are allowed in the running map.
3. If declared ensembles do not approach observed values, the result is a falsification event, not a tuning opportunity.

---

## 2. Problem Statement

COG has a UV structural result pipeline (for example, fixed-ratio projector outcomes), but the project still needs a principled IR bridge.

Current failure mode to avoid:
1. Start from a UV value.
2. Introduce ad hoc attenuation factor.
3. Adjust factor until a target value appears.

That produces numerology, not derivation.

---

## 3. Literature Synthesis

## 3.1 RG foundations

1. Wilson and Kogut established that running comes from coarse-graining and scale-dependent effective couplings, not direct curve fitting.
   - Wilson and Kogut (1974), *The renormalization group and the epsilon expansion*.
2. Polchinski's exact RG equation formalizes flow as a deterministic equation for effective action under changing cutoff.
   - Polchinski (1984), *Renormalization and Effective Lagrangians*.

Inference for COG:
1. A valid discrete RG analogue must define deterministic coarse-graining/effective-map rules first.
2. Parameter fitting after seeing outcomes is methodologically invalid.

## 3.2 Discrete and lattice-compatible RG constructions

1. Real-space/lattice RG and perfect-action programs show that discrete systems can realize RG flow without introducing arbitrary fit factors at each step.
   - Hasenfratz and Niedermayer (1993), hep-lat/9307004.
2. Tensor-network RG gives deterministic, explicit coarse-graining operators.
   - Levin and Nave (2007), cond-mat/0611687.
   - Evenbly and Vidal (2015), arXiv:1412.0732.

Inference for COG:
1. Environment-ensemble rollout is the right family of discrete RG analogs for this codebase.
2. Flow should be represented by explicit transformation rules over declared micro-environment classes.

## 3.3 Non-associative RG algebra relevance

Recent work shows RG fixed-point structures can be governed by non-associative algebraic data.
1. Flodgren and Sundborg (2023), arXiv:2303.13884.
2. Flodgren and Sundborg (2023), arXiv:2312.04954.

Inference for COG:
1. Associator-load channels are a physically motivated running mechanism candidate.
2. This supports Avenue-13 style running hypotheses, but does not prove COG-specific formulas.

## 3.4 Electroweak running constraints

Modern electroweak analyses emphasize scheme/threshold dependence and careful matching across scales.
1. Spiesberger (2024), arXiv:2403.12145.

Inference for COG:
1. A COG running model must clearly specify:
   - what observable is evolved,
   - what "scale step" means,
   - how environment composition changes with step depth.

---

## 4. COG Discrete-RG Contract

Let:
1. `U` be the locked micro-update map from RFC-028.
2. `E` be a predeclared environment-condition distribution.
3. `O` be a declared observable extraction map.
4. `R_E` be the rollout operator induced by applying `U` under `E` and reading via `O`.

Then running is represented by:

`O_n = R_E^n (O_0)`

with these constraints:
1. `E` must be predeclared before execution.
2. `R_E` must be deterministic for fixed seed/config.
3. `n`-to-scale interpretation must be fixed by an independently derived bridge, not tuned to match target observables.

---

## 5. No-Free-Parameter Governance Rule

Forbidden:
1. Any attenuation parameter chosen after seeing target mismatch.
2. Any per-run policy mutation not predeclared and checksum-pinned.
3. Any run filtering that removes declared environments post hoc.

Required:
1. Predeclared condition bundle with immutable IDs.
2. Explicit aggregation protocol.
3. Full provenance bundle:
   - policy file hash,
   - code commit hash,
   - run seed/config hash.

---

## 6. Decisions To Lock

## D1. Environment schema

Lock required fields:
1. matter-content mix
2. neighborhood topology class
3. update horizon
4. initialization class

## D2. Aggregation protocol

Lock one of:
1. tickwise averaging
2. histogram-based averaging
3. dual reporting (recommended)

## D3. Observable family

For each study, lock:
1. primary observable
2. secondary diagnostics

## D4. Horizon policy

Lock:
1. fixed horizon,
2. or declared horizon family with summary statistic.

## D5. Scale-bridge policy

Lock:
1. independent calibration source for mapping step depth to physical scale.
2. explicit declaration that no target-observable fitting enters this bridge.

---

## 7. Recommended Path For Weinberg Running

1. Keep UV structural result explicit (for example, 1/4 channel baseline where applicable).
2. Apply only declared environment ensembles through deterministic rollout.
3. Report full distribution of evolved values, not only best-case members.
4. If ensemble mean/interval misses measured target, record as falsification of that mechanism class.

Do not:
1. search for a single custom environment that matches target and call it derivation.

---

## 8. Deliverables

## 8.1 Code

1. Canonical condition schema and validator.
2. Rollout engine with deterministic replay.
3. Aggregation/report generator.

## 8.2 Tests

1. policy immutability checks
2. replay determinism checks
3. anti-retrofitting checks:
   - fail if undeclared policy IDs appear,
   - fail if artifact checksums mismatch.

## 8.3 Reporting

1. JSON artifact for machine checks
2. markdown summary for human review
3. claim-linkable run IDs

---

## 9. Falsification Gates

1. Any run requiring tuned free parameters is invalid.
2. Any undeclared policy mutation after results is invalid.
3. Any claim based on best-member cherry-picking without ensemble statistics is invalid.
4. If declared ensembles do not approach target behavior, mark mechanism as falsified or partial, not tuned.

---

## 10. Acceptance Criteria

1. No-free-parameter rule is enforceable by CI checks.
2. Ensemble-driven results are reproducible with pinned policies.
3. At least one high-value constant study uses this mechanism end-to-end.
4. Claims include explicit `rg_policy_profile` metadata.

---

## 11. Open Questions

1. What is the minimal environment basis that is expressive enough but still tractable?
2. Which observables are robust under policy perturbations?
3. What independent calibration is most defensible for step-depth to scale mapping in COG?

---

## 12. Sources

1. Wilson and Kogut (1974), *The renormalization group and the epsilon expansion*  
   https://doi.org/10.1016/0370-1573(74)90023-4
2. Polchinski (1984), *Renormalization and Effective Lagrangians*  
   https://doi.org/10.1016/0550-3213(84)90287-6
3. Hasenfratz and Niedermayer (1993), *Perfect lattice action for asymptotically free theories*  
   https://arxiv.org/abs/hep-lat/9307004
4. Levin and Nave (2007), *Tensor Renormalization Group Approach to 2D Classical Lattice Models*  
   https://arxiv.org/abs/cond-mat/0611687
5. Evenbly and Vidal (2015), *Tensor Network Renormalization*  
   https://arxiv.org/abs/1412.0732
6. Flodgren and Sundborg (2023), *RG fixed points from non-associative algebras*  
   https://arxiv.org/abs/2303.13884
7. Flodgren and Sundborg (2023), *Non-associative RG structures and fixed-point data*  
   https://arxiv.org/abs/2312.04954
8. Spiesberger (2024), *Running electroweak mixing in precision observables*  
   https://arxiv.org/abs/2403.12145

