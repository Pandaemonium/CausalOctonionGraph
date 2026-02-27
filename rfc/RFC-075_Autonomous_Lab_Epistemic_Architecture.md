# RFC-075: Autonomous Lab Epistemic Architecture (Quality-First, Resource-Unconstrained)

Status: Active Draft  
Date: 2026-02-27  
Owner: Research Director + Lab Manager  
Implements: `rfc/MASTER_IMPLEMENTATION_PLAN_V2.md` (WS-F extension)

Depends on:
1. `rfc/RFC-050_Proof_State_and_Claim_Status_Matrix.md`
2. `rfc/RFC-049_Benchmark_and_Falsification_Battery_v2.md`
3. `rfc/RFC-069_Canonical_Simulation_Artifact_Contract.md`
4. `scripts/run_claim_promotion_pipeline.py`
5. `scripts/validate_claim_status_matrix.py`
6. `scripts/validate_claim_events.py`
7. `calc/derive_sm_quantum_numbers.py`
8. `scripts/validate_qn_claim_ledger.py`

---

## 1. Executive Summary

This RFC defines the target operating model for the autonomous COG lab when the objective is maximum research quality and speed, not token/call minimization.

Core policy shift:
1. Claims are governed by a structured epistemic ledger, not prose brief memory.
2. Every promotable claim must declare assumptions and falsification conditions.
3. Every promotable claim must survive adversarial falsification attempts from model-diverse reviewers.
4. Physics-facing predictions are checked nightly by a deterministic oracle against external targets.

This converts the loop from "task completion" to "scientific validity progression."

---

## 2. Problem Statement

Current failure modes:
1. Context bottleneck: manager decisions depend on long narrative briefs that truncate.
2. Assumption laundering: bridge assumptions are sometimes hidden inside implementation success.
3. Skeptic weakness: post-task review often catches execution defects, not conceptual weaknesses.
4. Missing reality closure: formal derivations can pass internal checks without physical prediction accountability.

Goal:
1. maximize epistemic correctness per round,
2. preserve high throughput,
3. keep every promoted claim reproducible and auditable.

---

## 3. Design Principles

1. **Explicitness over implication**: assumptions, dependencies, and falsifiers are first-class data.
2. **Model diversity by construction**: builder and falsifier must not share model family on same claim round.
3. **Deterministic authority for verification**: scripts and tests decide pass/fail, not narrative summaries.
4. **Promotion is earned, not inferred**: claim state transitions require hard gates.
5. **Short context, high information density**: manager reads generated graph summaries, not raw long-form docs.

---

## 4. Epistemic Data Model

## 4.1 Canonical Claim Entry (required fields)

Every claim record must include:
1. `claim_id`
2. `status`
3. `derivation_status` (`core_derived`, `bridge_assumed`, `falsified`, `untested`)
4. `inputs` (upstream claim IDs)
5. `bridge_assumptions` (explicit non-core assumptions; can be empty only for `core_derived`)
6. `prediction` (quantity, value, tolerance, scale/conditions) when claim is physics-facing
7. `falsification_condition` (machine-readable or deterministic-text condition)
8. `lean_refs`
9. `test_refs`
10. `falsification_attempts` (list of adversarial reports)
11. `confidence`

## 4.2 Promotion-State Semantics (normative)

Canonical statuses:
1. `stub`
2. `active_hypothesis`
3. `partial`
4. `supported_bridge`
5. `proved_core`
6. `falsified`
7. `superseded`

Interpretation:
1. `proved_core`: no unresolved bridge assumptions; core derivation only.
2. `supported_bridge`: evidence strong but bridge assumptions remain explicit.

Backward-compatibility mapping:
1. legacy `supported` maps to `supported_bridge` until migrated.

---

## 5. Role Architecture

Required roles:
1. **Builder**: implements theorem/code/artifacts for a scoped task.
2. **Verifier**: deterministic and procedural correctness checks only.
3. **Falsifier (Premortem)**: attacks assumptions/spec before build.
4. **Falsifier (Postmortem)**: attacks claim validity after implementation.
5. **Synthesizer**: periodic scientific memory and reprioritization.
6. **Reality Oracle (scripted)**: nightly prediction-vs-target comparison.

Hard separation:
1. Builder and any falsifier must be different model families.
2. Falsifier output must be claim-by-claim, not global prose approval.

---

## 6. Multi-Timescale Control Loops

## 6.1 Tactical Loop (every round)

1. manager selects claim task from graph priority queue,
2. falsifier premortem emits weakest-link analysis,
3. builder executes,
4. verifier executes deterministic checks,
5. falsifier postmortem emits full claim-by-claim report,
6. promotion engine applies state transition rules.

## 6.2 Synthesis Loop (every 10 tactical rounds)

Synthesizer emits memo with:
1. newly locked core claims,
2. unresolved bridge assumptions,
3. contradiction set,
4. top reranked priorities,
5. required direction changes.

## 6.3 Direction Review (triggered)

Trigger conditions:
1. major prediction miss (outside tolerance),
2. high-impact claim falsified,
3. repeated contradictory promotions.

Action:
1. pause promotions for affected branch,
2. rerank portfolio,
3. update manager priority policy.

---

## 7. Promotion Gates (normative)

A claim can move `partial -> supported_bridge` only if:
1. required Lean/Python/test gates pass,
2. `derivation_status` present,
3. `bridge_assumptions` declared,
4. `falsification_condition` present,
5. at least one non-trivial falsification attempt recorded,
6. promotion pipeline validators pass.

A claim can move `supported_bridge -> proved_core` only if:
1. `bridge_assumptions` is empty,
2. theorem/test references are non-placeholder,
3. falsifier report confirms no hidden bridge assumption remains,
4. all validators and battery gates pass.

---

## 8. Priority and Routing Strategy

Priority score:
`score = impact * testability * falsifiability * reproducibility / (1 + assumption_load)`

Task routing constraints:
1. if Builder provider is Anthropic, Falsifier provider must be OpenAI or Gemini (and vice versa),
2. high-stakes claims require two independent falsifier passes,
3. long-context synthesis uses highest-context available model.

---

## 9. Reality Oracle Contract

Nightly script (`oracle/check_predictions.py`) must:
1. read claim ledger,
2. evaluate all claims with prediction metadata,
3. compare to external targets/tolerances (CODATA/PDG or declared reference set),
4. emit `oracle_report.json`,
5. generate `oracle_mismatch` events for misses,
6. queue `prediction_review` tasks automatically.

Oracle output is advisory for branch selection but mandatory for promotion eligibility of prediction claims.

---

## 10. Context Injection Contract

Manager context must be graph summary, not full brief scroll.

Required summary fields:
1. top-N open claims by priority score,
2. assumption load per claim,
3. open contradictions,
4. last synthesis memo digest,
5. active oracle mismatches,
6. blocked promotions and reasons.

Worker and falsifier tasks must receive a task dossier bundle:
1. primary task spec,
2. 2-3 background docs,
3. exact artifact paths,
4. acceptance tests,
5. relevant previous attempts (capped/summarized).

---

## 11. Implementation Plan

## Phase 1 (Week 1: minimal high impact)

1. Extend claim schema with:
   - `derivation_status`
   - `bridge_assumptions`
   - `falsification_condition`
2. Add validation gates for these fields in promotion pipeline.
3. Add nightly oracle stub + target table + mismatch events.
4. Inject oracle report into manager context package.

Deliverables:
1. schema migration script(s),
2. validator updates,
3. `oracle/check_predictions.py`,
4. manager summary artifact including oracle block.

## Phase 2 (Week 2: structural)

1. Add `falsifier_premortem` and `falsifier_postmortem` task types.
2. Enforce model-family separation between builder and falsifier.
3. Add queue ratio policy: at least 1 falsification task per 3 build tasks.
4. Add graph summary builder (`scripts/summarize_knowledge_graph.py`) for manager.

Deliverables:
1. orchestration routing updates,
2. new task templates,
3. summary artifact generation.

## Phase 3 (Week 3: systemic)

1. Add synthesis round every 10 tactical rounds.
2. Add direction-review triggers and pause/rerank flow.
3. Publish machine-readable proof ledger on website.
4. Wire oracle mismatch events to automatic follow-up task creation.

Deliverables:
1. synthesis memo generator,
2. direction review policy hooks,
3. website ledger integration.

---

## 12. Metrics (must be tracked)

1. Promotion quality:
   - fraction of promotions with falsifier report attached (target 100%),
   - fraction of promoted claims later downgraded/falsified.
2. Throughput quality:
   - median rounds from `active_hypothesis` to `supported_bridge`,
   - verification pass rate on first attempt.
3. Epistemic health:
   - average bridge assumption count per promoted claim,
   - ratio `proved_core / supported_bridge`.
4. Reality alignment:
   - number of prediction claims within tolerance,
   - time-to-resolution for oracle mismatches.

---

## 13. Risks and Mitigations

1. **Risk**: adversarial overhead slows tactical velocity.
   - **Mitigation**: parallel premortem and build execution where possible.
2. **Risk**: model disagreement noise.
   - **Mitigation**: deterministic verifier/oracle are final authority.
3. **Risk**: promotion gridlock from strict gates.
   - **Mitigation**: allow `supported_bridge` with explicit assumptions while reserving `proved_core` for strict closure.
4. **Risk**: external-target drift and reference inconsistency.
   - **Mitigation**: versioned target source and reference timestamp in oracle outputs.

---

## 14. Immediate Decisions to Lock

1. Adopt two terminal trust labels: `supported_bridge` and `proved_core`.
2. Require at least one falsifier report for all non-trivial promotions.
3. Require claim-level `falsification_condition` before promotion.
4. Make manager input graph-summary first, prose brief second.
5. Treat deterministic oracle mismatch as automatic follow-up task trigger.

---

## 15. Acceptance Criteria for RFC-075 Closure

RFC-075 reaches `supported` when:
1. claim schema fields are migrated and validator-enforced,
2. falsifier premortem/postmortem roles are active in orchestration,
3. model-family separation is enforced in routing,
4. oracle runs nightly and produces queue events,
5. synthesis loop runs at fixed cadence,
6. manager context uses graph summary artifact in production.

