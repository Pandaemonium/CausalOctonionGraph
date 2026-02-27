# RFC-072: Tritium Typical-Microstate Approximation Strategies

Status: Active Draft - Methodology RFC (2026-02-27)
Module:
- `COG.Nuclear.TritiumMicrostateApprox`
- `COG.Ensemble.ConstraintSampling`
Depends on:
- `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
- `rfc/RFC-035_Distance_as_Next_Interaction_Node_Gap.md`
- `rfc/RFC-064_Superdeterminism_and_Lightcone_Information_Volume.md`
- `rfc/RFC-069_Canonical_Simulation_Artifact_Contract.md`
- `world_code/Python_code/minimal_world_kernel.py`
- `calc/tritium_microstate.py`

---

## 1. Executive Summary

In COG, reality has one exact superdetermined initial microstate.  
So "typical tritium microstate" is not an ontic claim; it is an epistemic approximation problem.

This RFC defines reasonable approximation strategies for selecting and ranking candidate initial microstates that are:
1. fully deterministic and replayable,
2. consistent with tritium macro-constraints,
3. useful for downstream extraction work (fine structure, strong coupling, mass-drag programs).

---

## 2. Problem Statement

Tritium simulations require a full predetermined lightcone state.  
But the project does not currently know the exact real-world microstate.

We therefore need a principled way to approximate a "typical" tritium initial state without:
1. adding stochastic kernel dynamics,
2. fitting ad-hoc parameters to target outputs,
3. violating full-lightcone initialization policy.

---

## 3. Scope and Non-Scope

In scope:
1. candidate generation methods,
2. filtering/ranking methods,
3. validation and falsification gates.

Out of scope:
1. claiming the exact ontic microstate of physical tritium,
2. final numerical closure of all nuclear observables,
3. replacing canonical update semantics.

---

## 4. Core Principle: Typicality Is Epistemic

Locked interpretation:
1. microdynamics remain deterministic (RFC-028, RFC-064),
2. typicality means "high-support under declared uncertainty over initial conditions,"
3. uncertainty is in observer knowledge, not in kernel laws.

Equivalent statement:
1. we define an ensemble over admissible initial states,
2. run deterministic evolution on each,
3. infer which regions of initial-state space are robustly tritium-like.

---

## 5. Hard Constraints for Candidate States

Any candidate initial microstate must satisfy:
1. full-lightcone initialization (no partial seed starts),
2. DAG validity and canonical ordering constraints,
3. composition constraints matching tritium scenario declaration,
4. declared motif basis (e.g. Furey-aligned motif mapping if selected),
5. deterministic replay compatibility.

Suggested mandatory metadata per candidate:
1. `candidate_id`
2. `constraint_profile_id`
3. `generator_policy_id`
4. `initial_lightcone_hash`

---

## 6. Reasonable Approximation Strategies

## 6.1 Constraint-first ensemble (recommended baseline)

Method:
1. define strict macro constraints (charge class, baryon content class, motif class),
2. generate many microstates that satisfy only those constraints,
3. avoid additional tuning in generator.

Why reasonable:
1. minimizes hidden assumptions,
2. keeps search broad while physically constrained.

---

## 6.2 Symmetry-orbit canonicalization

Method:
1. identify symmetry-equivalent initial states (label permutations / automorphism actions),
2. keep one canonical representative per orbit.

Why reasonable:
1. avoids over-counting equivalent configurations,
2. reduces computational waste and bias in "typicality" estimates.

---

## 6.3 Persistence-conditioned typicality

Method:
1. evolve all candidates for fixed horizons,
2. retain states showing tritium-like persistence/interaction signature,
3. define typical set from survivors.

Why reasonable:
1. uses dynamical behavior, not just static constraints,
2. aligns with COG notion of motifs as stable/long-lived structures.

---

## 6.4 Hierarchical bootstrap from simpler systems

Method:
1. start with validated hydrogen/deuterium-like seeds,
2. extend to tritium by minimal deterministic additions,
3. track which added structures preserve stability signatures.

Why reasonable:
1. leverages already validated subsystems,
2. provides interpretable incremental construction path.

---

## 6.5 Max-entropy under hard constraints (optional)

Method:
1. among all states satisfying hard constraints, choose a near-uniform sampler over admissible representations.

Why reasonable:
1. least-commitment prior when no stronger evidence is available.

Caution:
1. must be implemented as deterministic pseudo-enumeration/replayable index policy in canonical workflows,
2. no hidden RNG in kernel evolution.

---

## 7. Ranking and Selection Metrics

Candidate ranking should be declared before runs and may include:
1. persistence score across depth window,
2. bounded drift in motif-support signature,
3. interaction-recurrence pattern consistency,
4. edge-distance evolution consistency (RFC-035 metric family),
5. axis-weight trajectory stability (`e0`, `e7`, and declared derived ratios).

No post-hoc metric switching is allowed inside a single campaign.

---

## 8. Recommended Workflow

1. Define `constraint_profile`.
2. Generate candidate set with deterministic generator policy.
3. Canonicalize by symmetry orbits.
4. Run fixed-horizon deterministic evolution for each candidate.
5. Compute declared metrics.
6. Select robust survivor set.
7. Publish:
   - full candidate list,
   - filtered list,
   - reasons for rejection,
   - replay commands and hashes.

---

## 9. Output Artifact Contract

Each tritium-typicality campaign must output:
1. `candidate_manifest.json`
2. `constraint_profile.json`
3. `generator_policy.json`
4. `selection_metrics.json`
5. `survivor_set.json`
6. `not_claimed.md` (explicit boundaries)

These extend RFC-069 simulation package rules for ensemble campaigns.

---

## 10. Falsification Gates

Reject the approximation framework if:
1. replay hash instability appears for fixed candidate inputs,
2. selected typical set is highly sensitive to irrelevant label permutations,
3. small declared metric-policy changes cause complete rank collapse,
4. all candidate families fail to produce tritium-like persistence under declared constraints.

If (4) occurs, record as model-pressure evidence rather than silently retuning.

---

## 11. Immediate Implementation Tasks

1. Add deterministic candidate-generator script for tritium ensemble variants.
2. Add symmetry-canonicalization utility for candidate deduplication.
3. Add campaign runner that emits required artifacts in Section 9.
4. Add skeptic review template for claim-by-claim acceptance of survivor-set evidence.

---

## 12. Decision Record

Locked by this RFC:
1. "typical tritium microstate" is an epistemic ensemble concept, not an ontic kernel claim,
2. approximation must be constraint-first, deterministic, replayable, and transparently reported,
3. no hidden tuning or stochastic kernel edits are allowed to force tritium behavior.

