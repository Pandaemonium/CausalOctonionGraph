# Targeted Branching Policy for Computational Efficiency and Statistical Integrity

Status: Active  
Date: 2026-02-28  
Owner: COG Core  
Depends on:
1. `cog_v2/rfc/RFC-001_Canonical_Axiom_Profile.md`
2. `cog_v2/rfc/RFC-002_Event_Resolution_Modes_and_Interpretation_Layer.md`

## 1. Executive Decision

Branching is allowed in v2 as a computational optimization and statistical exploration tool, not as a default claim-grade execution path.

Policy:
1. deterministic single-path remains the promotion baseline,
2. targeted branching is permitted when it reduces redundant recomputation,
3. incomplete branch exploration must be treated as potentially biased unless explicit correction is applied.

## 2. Problem Statement

Long-horizon simulations are expensive. Re-running from tick `0` for each stochastic sample repeats shared prefixes many times.

Observed tradeoff:
1. repeated independent reruns are simple and robust but often waste compute,
2. branch-tree execution reuses shared prefixes but can explode memory and introduce selection bias if truncated improperly.

Goal:
1. recover prefix-sharing efficiency where it is material,
2. keep statistical estimates valid and auditable,
3. preserve deterministic replay for gate decisions.

## 3. Scope

In scope:
1. computational strategy for branch reuse,
2. parameterization of branching controls,
3. statistical validity constraints for partial branch expansion.

Out of scope:
1. interpretation claims (Many-Worlds truth vs Copenhagen truth),
2. changes to projector algebra or CxO state law,
3. automatic promotion based only on branching evidence.

## 4. Core Modes for Efficient Sampling

### 4.1 Independent Reruns (Baseline)

Run `N` stochastic realizations from tick `0`.

Pros:
1. easiest correctness model,
2. unbiased under correct sampler,
3. trivial audit path.

Cons:
1. repeats shared early ticks `N` times,
2. wasteful when divergence starts late.

### 4.2 Checkpointed Reruns (Recommended First Optimization)

Run deterministic prefix once, checkpoint at selected ticks, spawn reruns from checkpoints.

Pros:
1. large compute savings with low complexity,
2. preserves single-path execution semantics per run,
3. easy to validate against baseline reruns.

Cons:
1. requires storage for checkpoints,
2. requires careful checkpoint invalidation when model changes.

### 4.3 Explicit Branch Tree (Advanced)

Maintain multiple branches concurrently with shared ancestry DAG.

Pros:
1. avoids recomputing all shared prefixes,
2. can provide full path-ensemble statistics in one run.

Cons:
1. memory growth risk,
2. branch bookkeeping complexity,
3. biased estimates if branch truncation/selection is unmanaged.

## 5. Efficiency Model

Let:
1. `T` = total ticks,
2. `N` = sample count,
3. `tau` = average divergence tick,
4. `C(t)` = per-tick cost.

Approximate costs:
1. reruns: `O(N * sum_{t=1..T} C(t))`,
2. prefix-share idealized: `O(sum_{t=1..tau} C(t) + N * sum_{t=tau+1..T} C(t))`.

Branching gives strong benefit when:
1. `tau` is large,
2. many samples share long prefixes,
3. state dedup/merge rate is high.

## 6. Required Branching Parameters

Any branching execution artifact must record:
1. `branch_policy_id`,
2. `branch_trigger_policy_id`,
3. `branch_selection_policy_id`,
4. `branch_weight_policy_id`,
5. `branch_merge_policy_id`,
6. `max_branch_factor_per_tick`,
7. `max_branches_total`,
8. `checkpoint_interval`,
9. `random_seed` (if stochastic),
10. `resampling_policy_id` (if pruning/resampling applied).

## 7. Statistical Integrity Rules

### 7.1 Unbiasedness Condition

If branch sampling is incomplete, estimators are unbiased only when inclusion probabilities are known and estimators are weighted accordingly.

Minimum requirement:
1. each retained branch has explicit weight,
2. estimator uses declared weight formula,
3. discarded branches are accounted for by policy, not silent truncation.

### 7.2 When Bias Is Expected

Bias risk is high when:
1. branch truncation depends on outcome-like variables,
2. high-weight tails are pruned without correction,
3. branch exploration budget is exhausted non-randomly.

### 7.3 Required Diagnostics

Artifacts must include:
1. branch coverage ratio,
2. effective sample size proxy,
3. max branch weight concentration,
4. sensitivity check vs independent rerun baseline on a reduced benchmark.

## 8. Practical Strategy (v2 Default)

Default strategy for heavy jobs:
1. deterministic baseline run,
2. checkpointed stochastic reruns,
3. optional targeted branch expansion near identified divergence windows,
4. periodic parity checks against pure rerun estimates.

This captures most efficiency gains without full branch-tree complexity.

## 9. Branch Trigger and Pruning Policies

Branch trigger should be preregistered and deterministic given state and policy config.

Examples:
1. trigger at specified ticks,
2. trigger when local projector ambiguity score exceeds threshold,
3. trigger only on designated motif interactions.

Pruning/resampling must be explicit:
1. top-k by weight,
2. stratified retention,
3. stochastic resampling with logged probabilities.

## 10. Promotion Governance

For `supported_bridge` or `proved_core` claim decisions:
1. deterministic witness artifacts are mandatory,
2. branching artifacts are supplemental unless claim RFC explicitly elevates them,
3. any branching-derived statistic used in argument text must include bias-control metadata.

## 11. Validation Battery

Before trusting a branching policy:
1. run A/B comparison vs independent reruns on tractable benchmark,
2. verify estimate agreement within predeclared tolerance,
3. verify stable result under branching budget sweep,
4. verify no hidden dependence on processing order.

## 12. Tradeoff Matrix

Use independent reruns when:
1. horizon is short,
2. branch fanout is high from early ticks,
3. memory budget is tight.

Use checkpointed reruns when:
1. divergence occurs late,
2. many reruns are needed,
3. storage is available.

Use explicit branching when:
1. branch fanout is moderate and controllable,
2. prefix sharing is substantial,
3. bias controls and branch weights are fully instrumented.

## 13. Risk Register

1. **Risk:** hidden bias from adaptive pruning.  
   **Mitigation:** preregistered pruning + weight-corrected estimators + baseline parity checks.
2. **Risk:** branch explosion causes OOM.  
   **Mitigation:** hard caps on branch factor and total branches; fallback to checkpointed reruns.
3. **Risk:** unverifiable statistics.  
   **Mitigation:** mandatory metadata + deterministic reduced-case replay.

## 14. Rollout Plan

Phase 1:
1. implement checkpointed reruns and metadata schema,
2. add baseline parity test harness.

Phase 2:
1. implement bounded branch tree with explicit weights,
2. add pruning/resampling policies and diagnostics.

Phase 3:
1. enable claim-specific use of branching statistics under validator enforcement.

## 15. Acceptance Criteria

This policy is implemented when:
1. v2 runtime can execute checkpointed reruns with deterministic replay metadata,
2. branching mode enforces hard caps and records full branching policy fields,
3. validation includes baseline parity checks and branch-bias diagnostics,
4. promoted claims remain anchored to deterministic witness artifacts by default.
