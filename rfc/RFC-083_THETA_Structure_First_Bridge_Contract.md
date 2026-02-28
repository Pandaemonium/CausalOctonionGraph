# RFC-083: THETA Structure-First Bridge Contract

Status: Active Draft  
Date: 2026-02-28  
Owner: CP-Symmetry + Bridge Team  
Depends on:
1. `rfc/RFC-057_CPT_via_Causal_Graph_Involutions.md`
2. `rfc/RFC-069_Canonical_Simulation_Artifact_Contract.md`
3. `rfc/RFC-075_Autonomous_Lab_Epistemic_Architecture.md`
4. `claims/THETA-001.yml`
5. `calc/build_theta001_witness.py`
6. `calc/build_theta001_bridge_closure.py`

## 1. Purpose

Lock THETA-001 as a structure-first claim lane and define the bridge boundary
between:
1. discrete CP-odd residual witnesses in COG, and
2. the continuum EFT `theta_QCD` coefficient interpretation.

## 2. Scope Decision (Normative)

THETA-001 is currently a `structure_first` claim.

Allowed closure target in this phase:
1. `supported_bridge` only.

Not allowed in this phase:
1. full hadronic phenomenology closure,
2. `proved_core` status while bridge assumptions remain open.

Language constraint in this phase:
1. THETA statements may assert structural consistency and conditional bridge implications,
   but may not assert unconditional physical-value derivation of `theta_QCD`.

## 3. Locked Observable Boundary

In-scope (required):
1. deterministic CP map witness on CxO states,
2. orientation-flip closure on canonical Fano triples,
3. exact sign-balance witness (`21/21`, signed sum `0`),
4. deterministic CP-dual and weighted residual checks,
5. deep-cone weak-leakage suite (`N > 10`) under weak-sector perturbations,
   with strong-sector residual reported.

Out-of-scope (bridge-level):
1. full continuum path-integral derivation of `F*F_tilde`,
2. direct hadronic EDM closure.

## 4. Required Contract Metadata

THETA claims under this contract must declare:
1. `closure_scope`,
2. `bridge_contract_id`,
3. `bridge_observable_id`,
4. `discrete_residual_artifact`,
5. `weak_leakage_artifact`,
6. `eft_bridge_artifact`,
7. `skeptic_review_artifact`,
8. `skeptic_model_diversity_required`,
9. `skeptic_verdict`,
10. `bridge_assumptions`,
11. `falsification_condition`,
12. `falsification_attempts` (list; may be empty but must be present).

## 5. Skeptic Gate Policy (Normative)

1. At least one independent skeptic artifact is required.
2. Skeptic must be model-family-diverse from builder:
   reviewer model family must differ from builder model family.
3. Promotable verdicts: `PASS` or `PASS_WITH_LIMITS`.
4. `pending` or `FAIL` blocks promotion.
5. Skeptic JSON artifact must include:
   `timestamp`,
   `review_summary` (>= 200 characters),
   `bridge_comment`,
   `falsification_comment`,
   `reviewer_model_family`,
   `builder_model_family`,
   `independent_from_builder`.
6. `PASS_WITH_LIMITS` verdict must include a non-empty `limits` list.

## 6. Promotion Rules

`partial -> supported_bridge` for THETA requires:
1. deterministic and replayable witnesses,
2. bridge assumptions explicitly declared,
3. weak-leakage artifact reports `all_zero = true`,
4. EFT bridge artifact includes explicit conditional-map assumptions and theorem refs,
5. `rfc083` contract fields complete and valid,
6. skeptic verdict is promotable,
7. claim `gate_3` is `done: true`.

`supported_bridge -> proved_core` is not allowed while `closure_scope = structure_first`.

## 7. Immediate Tasks

1. Keep witness artifacts deterministic on each update.
2. Maintain weak-leakage suite artifact (`theta001_bridge_closure`).
3. Keep skeptic artifact current and model-diversity-checked.
4. Reserve proved-core attempts for a separate continuum bridge RFC/claim lane.

## 8. Acceptance Criteria

RFC-083 reaches `supported` when:
1. THETA claim carries complete `rfc083` metadata,
2. validator enforces weak-leakage + skeptic-gate rules,
3. promotion pipeline blocks invalid THETA promotions.
