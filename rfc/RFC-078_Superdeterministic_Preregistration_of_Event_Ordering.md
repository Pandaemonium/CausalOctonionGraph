# RFC-078: Superdeterministic Pre-Registration of Event Ordering

Status: Active Draft
Date: 2026-02-27
Owner: Research Director + Kernel Team
Depends on:
1. `rfc/RFC-002_Deterministic_Tick_Ordering.md`
2. `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
3. `rfc/RFC-051_Scheduler_Semantics_and_Update_Cadence.md`
4. `rfc/RFC-069_Canonical_Simulation_Artifact_Contract.md`
5. `world_code/Python_code/minimal_world_kernel.py`
6. `world_code/Python_code/minimal_world_kernel_preregistered_unity.py`

---

## 1. Executive Summary

Current `minimal_world_kernel.py` is deterministic, but ordering is derived at runtime with:
1. `sorted(node_ids)`,
2. `sorted(parents[nid])`.

This is reproducible but weaker than strict superdeterministic pre-registration.

Decision:
1. Define a preregistered ordering contract where round order and parent order are explicit immutable input data.
2. Runtime must consume that plan directly and must not infer ordering heuristics.
3. Missing/mismatched plan entries are hard errors.

This RFC also establishes a validated exploratory pathway for unit CxO projector dynamics under the preregistered ordering contract.

---

## 2. Problem Statement

Why `sorted(...)` is insufficient for strict superdeterminism:
1. It creates order from naming/serialization metadata at runtime.
2. It allows accidental semantic drift when IDs are renamed/re-encoded.
3. It does not certify that the event ordering was part of the initial microstate.

Superdeterministic requirement:
1. Event order is an initial condition, not a runtime choice.

---

## 3. Pre-Registered Ordering Contract

Required input field:
1. `eval_plan`

### 3.1 `eval_plan` schema

1. `round_order: List[node_id]`
   - exact permutation of `node_ids`.
2. `parent_order: Dict[node_id, List[parent_id]]`
   - exact per-node ordering of that node's parent contributor set.
3. `projection_policy: str` (for profiles that use projector dynamics)
   - declared policy identifier, immutable during run.

### 3.2 Hard validation rules

1. `round_order` must include each node exactly once.
2. `parent_order` keys must match `node_ids` exactly.
3. `set(parent_order[n]) == set(parents[n])` for every node `n`.
4. duplicates in round or parent order are forbidden.

---

## 4. Update Semantics Under Pre-Registration

For each round:
1. iterate nodes in `eval_plan.round_order` exactly,
2. gather messages by `eval_plan.parent_order[n]` exactly,
3. apply locked local update rule.

No `sorted(...)` fallback is allowed in preregistered profile.

If plan validation fails:
1. run is invalid and must halt.

---

## 5. Unit CxO Projector Pathway

This RFC approves a non-canonical exploratory pathway:
1. coefficients are projected to unit set `U = {0, +1, -1, +i, -i}`,
2. projection timing is controlled by preregistered `projection_policy`.

Supported policy IDs:
1. `fold_and_update`
2. `fold_only`
3. `update_only`

Implemented profile:
1. `world_code/Python_code/minimal_world_kernel_preregistered_unity.py`

Default profile:
1. `fold_and_update`

---

## 6. Canonical vs Exploratory Status

Canonical claim-grade kernel remains:
1. `minimal_world_kernel.py` (integer CxO, current canonical profile).

Exploratory preregistered unit profile:
1. `minimal_world_kernel_preregistered_unity.py`
2. non-canonical unless explicitly promoted by future closure RFC.

Promotion constraint:
1. any unity-profile claim must include integer-baseline companion run and delta disclosure.

---

## 7. Front-to-Back Validation Path

Path artifacts:
1. example input with preregistered plan:
   - `world_code/Python_code/lightcone_example_preregistered_unity.json`
2. kernel:
   - `world_code/Python_code/minimal_world_kernel_preregistered_unity.py`
3. validation runner:
   - `world_code/Python_code/validate_preregistered_unity_pathway.py`
4. tests:
   - `world_code/Python_code/test_minimal_world_kernel_preregistered_unity.py`

Validation requirements:
1. schema + plan validation pass,
2. replay determinism pass (same input -> identical state hash),
3. unity closure pass (all coefficients in unit set after run),
4. negative tests for malformed plan must fail.

---

## 8. What This Changes Immediately

1. Pre-registered ordering becomes available and runnable today.
2. Strict separation between:
   - deterministic runtime order derived by heuristic (`sorted`),
   - deterministic runtime order declared by initial condition (`eval_plan`).
3. Projector pathway is now executable and test-gated end to end.

---

## 9. Non-Goals

This RFC does not:
1. replace canonical integer kernel,
2. prove unity projector profile is physically correct,
3. settle equivalence of projector and non-projector dynamics.

---

## 10. Acceptance Criteria

RFC-078 reaches `supported` when:
1. preregistered ordering profile is implemented and passing tests,
2. front-to-back validation runner passes on reference input,
3. manager/claim docs can tag artifacts as `ordering_profile=preregistered_v1`,
4. promotion pipeline rejects unity-profile claims without integer baseline companion.

