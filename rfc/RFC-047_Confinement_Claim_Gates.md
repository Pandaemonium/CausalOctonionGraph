# RFC-047: Confinement Claim Gates

Status: Active Draft - Confinement Governance Closure Plan (2026-02-26)
Module:
- `COG.Governance.ConfinementGates`
Depends on:
- `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
- `rfc/RFC-040_Particle_Motif_and_Interaction_Rule_Contract.md`
- `rfc/RFC-043_Motif_Catalog_v1.md`
- `rfc/RFC-044_Projection_Profile_Governance.md`
- `rfc/RFC-049_Benchmark_and_Falsification_Battery_v2.md`
- `rfc/RFC-050_Proof_State_and_Claim_Status_Matrix.md`
- `rfc/RFC-054_Observable_Equivalence_and_Physical_Indistinguishability.md`
- `rfc/STRONG-001_Closure_Tasklist.md`

---

## 1. Executive Summary

This RFC defines the mandatory gates for any claim that says color confinement is derived in COG.

Core rule:
1. no confinement claim can be promoted from hypothesis/partial to supported unless all confinement gates pass under declared profiles, rules, and ensembles.

---

## 2. Problem Statement

Confinement language appears in multiple documents, but evidence is currently split between:
1. algebraic structure facts,
2. motif-level simulations,
3. projection-dependent readouts.

Without one gate contract, status can inflate from narrative momentum instead of reproducible evidence.

---

## 3. Scope and Definitions

### 3.1 Claim scope

This RFC governs claims of type:
1. no stable free-color asymptotic motif under declared environments,
2. color-singlet persistence as a robust outcome of the locked update rule,
3. confinement-linked strong-sector observables.

### 3.2 Free-color signature (profile-indexed)

A free-color signature is defined in observer space, not microstate ontology.
It must be evaluated under declared profile, with default:
1. primary profile: `with_sector`,
2. contrast profile: `minimal` (for sensitivity disclosure only).

### 3.3 Asymptotic persistence

A free-color event is asymptotically relevant only if it persists for at least declared horizon `H_persist`.

### 3.4 Ensemble policy

All confinement runs must declare:
1. initial-condition family,
2. scheduler/rule profile,
3. horizon,
4. sample count and seed policy,
5. pass/fail thresholds.

No post-hoc policy edits are allowed for the same reported result.

---

## 4. Mandatory Gate Families

## C1. Algebraic Well-Posedness Gate (Lean)

Required:
1. color-channel observables and predicates are type-correct and deterministic under locked kernel/update contracts,
2. declared singlet/non-singlet classifier is total and exclusive over declared motif class,
3. no hidden dependence on deprecated state/update contracts.

Fail condition:
1. classifier ambiguity or reliance on superseded kernel assumptions.

## C2. Dynamic Non-Escape Gate (Simulation)

Required:
1. many-body runs over declared ensemble,
2. estimate of asymptotic free-color persistence frequency with confidence interval,
3. reported estimate respects predeclared pass threshold.

Fail condition:
1. persistent free-color signatures above threshold under declared policy.

## C3. Sensitivity and Negative-Control Gate

Required:
1. at least one negative control that should produce higher free-color leakage when a confinement-relevant mechanism is removed or weakened,
2. detector responds in expected direction.

Fail condition:
1. gate passes equally on positive and negative controls (detector non-informative).

## C4. Projection and Equivalence Gate

Required:
1. confinement claim declares `pi_obs_profile: with_sector`,
2. contrast report under `minimal` is attached and labeled (`projection_sensitivity`),
3. equivalence assumptions are declared per RFC-054 where used.

Fail condition:
1. profile reversal or equivalence fragility is undisclosed.

## C5. Replay and Robustness Gate

Required:
1. deterministic replay on fixed seed/config,
2. robustness sweep across declared seed set and initial-condition family,
3. no container-order dependence.

Fail condition:
1. non-reproducible outcomes or threshold pass driven by one cherry-picked run.

## C6. Anti-Retrofit Governance Gate

Required:
1. policy IDs/checksums are pinned before result generation,
2. all failed branches retained in report artifacts,
3. no hidden parameter tuning between report revisions.

Fail condition:
1. post-hoc policy mutation or selective result reporting.

---

## 5. Minimal Evidence Bundle

For any confinement-grade claim promotion, all artifacts below are required:
1. Lean artifact list for C1 (`lean_theorems` + file refs),
2. simulation artifact for C2/C5 (machine summary + human report),
3. negative-control artifact for C3,
4. projection/equivalence metadata and contrast artifact for C4,
5. policy/checksum manifest for C6,
6. claim-matrix row with confinement gate status fields.

Recommended artifact naming:
1. `sources/confinement_gate_summary.json`
2. `sources/confinement_gate_report.md`
3. `sources/confinement_negative_controls.json`

---

## 6. Decisions Locked in This RFC

1. **Primary profile for confinement claims:** `with_sector`.
2. **Contrast requirement:** `minimal` contrast is mandatory for sensitivity disclosure.
3. **Asymptotic requirement:** confinement conclusions require declared `H_persist` and declared ensemble policy.
4. **Defensive threshold policy:** thresholds are mandatory and predeclared; no threshold edits after viewing results.
5. **Status policy:** if any mandatory gate is open/failed, confinement claims cannot be `supported`.

Recommended starting defaults (override allowed only if declared before run):
1. `H_persist >= 256`,
2. `N_samples >= 1000`,
3. one-sided confidence bound and threshold explicitly reported.

---

## 7. Falsification Gates

Any of the following falsifies or blocks a confinement-derived claim:
1. stable free-color asymptotic signatures above declared threshold,
2. projection-sensitive reversal without disclosure,
3. negative-control insensitivity,
4. replay non-determinism for fixed policy/seed,
5. hidden tuning or post-hoc policy edits.

---

## 8. Integration with Battery v2 and Claim Matrix

Battery integration:
1. adds confinement family `B7` in RFC-049.

Claim-matrix integration:
1. confinement-relevant rows must include gate status and artifact references in RFC-050 schema.

Promotion rule:
1. `supported` for confinement-relevant claims requires `B7: pass` plus all other class-required families.

---

## 9. Impacted Claim Classes

Primary impacted classes:
1. strong-routing and confinement claims,
2. proton/quark internal-structure claims using confinement language,
3. any claim interpreting strong-sector observables as confinement evidence.

Immediate target:
1. `STRONG-001` remains partial until C1-C6 are artifact-complete.

---

## 10. Migration Plan

Phase A:
1. add confinement gate metadata fields to claim matrix rows for impacted claims,
2. mark current confinement interpretation as open-gate.

Phase B:
1. run first full C1-C6 gate pass attempt with archived artifacts,
2. run negative controls and profile contrast.

Phase C:
1. permit status promotion only through battery and matrix validators.

---

## 11. Acceptance Criteria

This RFC is closed when:
1. confinement gate family is implemented in battery runner and CI,
2. matrix schema and validators enforce confinement fields for relevant claims,
3. at least one full C1-C6 run is archived with reproducible artifacts,
4. at least one high-value claim (starting with `STRONG-001`) is reclassified using this gate framework.

---

## 12. References

1. Wilson, K. G. (1974), *Confinement of quarks*.
2. Greensite, J. (2011), *An Introduction to the Confinement Problem*.
3. Arrighi, P., Dowek, G. (2012), *Causal graph dynamics*  
   https://arxiv.org/abs/1202.1098
