# RFC-002: Event Resolution Modes and Interpretation Layer

Status: Active  
Date: 2026-02-28  
Owner: COG Core  
Depends on: `cog_v2/rfc/RFC-001_Canonical_Axiom_Profile.md`
Related:
- `cog_v2/rfc/Targeted_Branching_Policy_for_Computational_Efficiency_and_Statistical_Integrity.md`
- `cog_v2/rfc/RFC-003_Theta_Continuum_Identification_Contract.md`

## 1. Executive Decision

COG v2 separates:

1. **Dynamics layer (axiomatic):**
   - DAG causal structure,
   - `C x O` over unity state domain,
   - projector-based lightcone update rule.
2. **Resolution layer (interpretive policy):**
   - how projector action order / branch realization is resolved at runtime.

This RFC defines the resolution layer as explicit, selectable policy rather than hidden assumption.

## 2. Core Clarification

`Canonical event ordering` means:

> the order in which lightcone projector actions are applied to prior-state information to form the current state.

It does **not** change the algebraic update operator itself; it changes resolution policy for applying that operator in ambiguous or branching contexts.

## 3. Resolution Modes

Exactly one `event_resolution_mode` is active per run.

### 3.1 `deterministic_single_path`

Intent:
- deterministic completion rule (superdeterministic-style execution policy).

Contract:
1. single realized path,
2. fixed pre-registered projector action order,
3. replay-identical outputs for same inputs and config.

Required fields:
- `event_resolution_mode = deterministic_single_path`
- `event_order_policy_id` (non-empty string)
- optional explicit `event_order` permutation; otherwise contract fallback applies.

### 3.2 `stochastic_single_path`

Intent:
- agnostic single realized history with probabilistic selection (Copenhagen-style execution policy).

Contract:
1. single realized path per run,
2. projector ordering or branch choice may be sampled,
3. reproducible only when RNG seed and sampler contract are fixed.

Required fields:
- `event_resolution_mode = stochastic_single_path`
- `rng_policy_id`
- `rng_seed`
- `sampler_id`

### 3.3 `branching_paths`

Intent:
- explicit branch expansion (Many-Worlds-style execution policy).

Contract:
1. multiple branches retained,
2. branch weights or multiplicities tracked,
3. aggregate observables are branch-reduction dependent.

Required fields:
- `event_resolution_mode = branching_paths`
- `branch_policy_id`
- `branch_merge_policy_id` (or explicit `no_merge`)
- `max_branch_factor` (safety cap)

## 4. Promotion Eligibility Rules

For claim promotion in v2:

1. `supported_bridge` and `proved_core` promotion artifacts MUST include at least one deterministic witness run under `deterministic_single_path`.
2. `stochastic_single_path` and `branching_paths` may provide supplemental evidence, but are non-blocking unless a specific claim RFC states otherwise.
3. If a claim is promoted using non-deterministic evidence, deterministic witness parity is required in the same artifact package.

Rationale:
- preserves strict replayability for gate decisions,
- still allows exploration under stochastic/branching semantics.

## 5. Artifact Schema Additions

Every simulation artifact in v2 SHOULD include:

1. `event_resolution_mode`
2. `event_order_policy_id` (deterministic mode)
3. `rng_policy_id`, `rng_seed`, `sampler_id` (stochastic mode)
4. `branch_policy_id`, `branch_merge_policy_id`, `max_branch_factor` (branching mode)
5. `resolution_profile_version`

## 6. Validator Requirements

`cog_v2/scripts/validate_claim_contracts_v2.py` (or successor) should enforce:

1. required mode-specific fields are present and non-placeholder,
2. promoted claims include deterministic witness references,
3. stochastic/branching artifacts are explicitly labeled `supplemental` unless claim-level contract overrides.

## 7. Relation to Superdeterminism, Copenhagen, Many Worlds

This RFC treats those as resolution policies, not different base dynamics:

1. superdeterministic-style execution corresponds to `deterministic_single_path`,
2. Copenhagen-style execution corresponds to `stochastic_single_path`,
3. Many-Worlds-style execution corresponds to `branching_paths`.

The base COG v2 axioms remain unchanged.

## 8. Safety and Tractability Constraints

1. deterministic mode: no additional runtime branching overhead.
2. stochastic mode: require seed logging for reproducibility.
3. branching mode: hard cap on branch expansion to avoid unbounded memory growth.

## 9. Initial Rollout Plan

Phase A:
1. add schema fields to v2 simulation outputs,
2. default mode remains `deterministic_single_path`.

Phase B:
1. add stochastic mode behind explicit flag,
2. enforce seed and sampler metadata.

Phase C:
1. add bounded branching mode,
2. add branch-aggregation test suite and memory guards.

## 10. Non-Goals

This RFC does not:

1. prove a foundational interpretation of quantum mechanics,
2. mandate one interpretation as physically true,
3. alter the projector algebra or Fano multiplication laws.

## 11. Acceptance Criteria

RFC-002 is considered implemented when:

1. v2 kernel accepts and records `event_resolution_mode`,
2. deterministic mode remains replay-identical and gate-compatible,
3. validator enforces deterministic witness presence for promoted claims,
4. docs and claims clearly distinguish dynamics layer vs interpretation layer.
