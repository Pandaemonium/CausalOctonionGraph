# Simulation Selection Guide for Combinatoric Bridge Refinement

Status: Active  
Date: 2026-02-28  
Owner: COG Core  
Companion to:
1. `cog_v2/rfc/RFC-006_Bridge_Construction_from_CxO_Combinatorics.md`
2. `rfc/RFC-080_Discrete_RGE_Contract.md`
3. `cog_v2/rfc/Targeted_Branching_Policy_for_Computational_Efficiency_and_Statistical_Integrity.md`

## 1. Purpose

This guide tells simulation workers how to pick runs that are:
1. tractable on real compute budgets,
2. highly informative for bridge refinement,
3. safe against policy-shopping and hidden fitting.

Use this before launching any new bridge campaign.

## 2. Core Rule: One Question Per Campaign

Run simulations to answer one question at a time:
1. **Map-discrimination**: which preregistered combinatoric map family survives falsification?
2. **Robustness**: does the chosen map survive seeds/depth/topology variation?
3. **Value-estimation**: what value does the already-selected map produce?

Do not mix these goals in one campaign.

## 3. Pre-Run Decision Flow (Required)

1. Lock `claim_id`.
2. Lock `policy_id` and `map_family_id`.
3. Choose campaign type: `T1_map_discrimination`, `T2_robustness`, or `T3_value_estimation`.
4. Declare compute budget: max wall-clock, max memory, max run count.
5. Build only the smallest simulation matrix that can falsify your current bridge.

If you cannot state the falsification condition in one sentence, do not run.

## 4. Tractability Filters (Hard No-Go Gates)

Reject a proposed run if any are violated:
1. No deterministic replay path.
2. Missing preregistered input bundle (`policy_id`, seeds, depth, bounds).
3. Requires non-canonical kernel profile for a claim-grade result.
4. Produces artifacts too large to audit (`>10^6` row-scale) without aggregation plan.
5. Requires adaptive parameter tuning after seeing output.

## 5. Information-Per-Compute Scoring

Use this score to rank candidate simulations before launch.

`priority_score = (falsification_power * sensitivity * invariance_coverage) / compute_cost`

Where:
1. `falsification_power` (0-5): likelihood run can clearly kill a wrong bridge.
2. `sensitivity` (0-5): expected signal change under controlled input perturbation.
3. `invariance_coverage` (0-5): number/quality of symmetry and control checks in same run family.
4. `compute_cost` (1-5): normalized cost bucket (1 cheap, 5 expensive).

Run highest score first. Require `priority_score >= 2.0` for any new campaign.

## 6. Minimal Campaign Matrix (Start Here)

For each bridge family, launch this 5-lane matrix first:
1. **Baseline lane**: one exact microstate, fixed depth schedule, fixed map family.
2. **Null/control lane**: motif/control expected to produce zero or known baseline shift.
3. **Single-factor ablation lane**: vary one primitive driver only; keep everything else fixed.
4. **Symmetry lane**: apply declared gauge/CP/ordering transform; require invariant or expected equivariant response.
5. **Perturbation lane**: bounded perturbations in initial microstate; measure stability window.

Do not add more lanes until one of these fails or all pass with low uncertainty.

## 7. Choosing Depth and Seeds

Use geometric depth ladders for early work:
1. short: `8, 16, 32`,
2. medium: `64, 128`,
3. long: `256+` only after short/medium stabilize.

For `T1_map_discrimination`:
1. 1 deterministic seed plus 1 adversarial seed.

For `T2_robustness`:
1. 4 to 12 seeds across declared seed classes.

For `T3_value_estimation`:
1. enough seeds to stabilize your declared summary statistic and uncertainty metric.

## 8. When to Use Branching

Use branching only when:
1. divergence occurs late,
2. prefix sharing is large,
3. branch weighting diagnostics are recorded.

Otherwise use checkpointed reruns.

Claim-grade outputs remain anchored to deterministic witness runs unless claim RFC says otherwise.

## 9. Bridge Refinement Protocol (No Data Leakage)

To avoid overfitting:
1. Split data into `refinement_set` and `holdout_set`.
2. Refine map family only on `refinement_set`.
3. Freeze map family checksum.
4. Evaluate once on `holdout_set`.
5. If map changes, reset status and regenerate holdout results.

## 10. Required Metadata in Every Artifact

1. `claim_id`
2. `campaign_type` (`T1`, `T2`, `T3`)
3. `policy_id`
4. `kernel_profile_id`
5. `init_profile_id`
6. `map_family_id`
7. `free_parameter_count`
8. `posthoc_parameter_update`
9. `depth_schedule`
10. `seed_set_checksum`
11. `replay_hash`
12. `structure_match` and `value_match` fields (separate)

Artifacts missing any field are non-promotable.

## 11. Practical Launch Checklist

Before launch:
1. Can this run falsify something specific?
2. Is map family frozen before run?
3. Are controls and symmetry checks included?
4. Is output size auditable?
5. Is holdout plan declared?

After run:
1. Replay on independent machine.
2. Compare baseline vs control first.
3. Report failures before any refinement.
4. Update bridge status with explicit limits.

## 12. Anti-Patterns

1. Running huge horizons before short-depth mechanism checks pass.
2. Searching many policies then reporting only best one.
3. Treating exploratory scans as promotion evidence.
4. Mixing different kernel profiles inside one bridge conclusion.
5. Changing summary statistic after seeing target mismatch.

## 13. Parameter-Specific Starts

1. `THETA-001`: prioritize symmetry and leakage falsification lanes over value-fitting lanes.
2. `WEINBERG-001`: start with one exact microstate plus one stationary-window estimator, then run map-discrimination on alternative combinatoric corrections.
3. `STRONG-001`: separate structural proxy validation from scale-running bridge.
4. Mass lanes: do not run absolute-mass estimation before anchor and observable lock.

## 14. Collaborator Handoff Pack

Every external compute pack should include:
1. frozen scenario bundle,
2. one-command runner,
3. validation script,
4. artifact schema,
5. expected checksums for smoke tests,
6. upload format for returned datasets.

If a collaborator cannot run and validate in under 15 minutes on a small sample, the pack is not ready.

## 15. Exit Criteria for Refinement-Ready

Simulation set is refinement-ready when:
1. baseline + control + ablation + symmetry lanes are complete,
2. deterministic replay passes,
3. uncertainty is reported,
4. at least one falsification attempt was real,
5. map-family changes are tracked with checksum lineage.
