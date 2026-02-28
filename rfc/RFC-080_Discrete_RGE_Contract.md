# RFC-080: Discrete RGE Contract (Running Bridge for Couplings)

Status: Active Draft  
Date: 2026-02-28  
Owner: Gauge + Kernel Team  
Depends on:
1. `rfc/RFC-029_Weinberg_Angle_Gap_Closure.md`
2. `rfc/RFC-037_Weinberg_Derivation_Avenues_and_Gates.md`
3. `rfc/RFC-069_Canonical_Simulation_Artifact_Contract.md`
4. `rfc/RFC-078_Superdeterministic_Preregistration_of_Event_Ordering.md`
5. `rfc/RFC-079_Typical_Starting_Conditions_and_Cold_Start_Control.md`

## 1. Purpose

Define one canonical, preregistered running mechanism that maps UV COG observables
to IR coupling values without post-hoc fitting.

Targets:
1. `sin^2(theta_W)` bridge (`WEINBERG-001`).
2. `alpha_s(M_Z)` bridge (`STRONG-001`).
3. downstream `g1`, `g2`, `g3` conversion under fixed normalization.

## 2. Problem

Current state has multiple exploratory running policies and no canonical selection rule.
This creates policy-shopping risk and weakens claim strength.

## 3. Contract (Normative)

1. Running must be computed from a fixed, preregistered policy bundle.
2. No output-driven policy selection is allowed.
3. Observable bounds must be declared and enforced at runtime.
4. Seed ensemble and horizon schedule must be declared before execution.
5. Reported value is an ensemble statistic with declared uncertainty rule.

## 4. Canonical Inputs

Required preregistered fields:
1. `policy_id`
2. `kernel_profile_id`
3. `init_profile_id`
4. `depth_schedule`
5. `seed_set`
6. `observable_bounds`
7. `summary_stat` (median/mean) and uncertainty metric (MAD/std)

## 5. Required Outputs

1. Replay hash and conditions checksum.
2. Full per-depth running trace.
3. Ensemble summary and uncertainty.
4. Contrast/control traces.
5. Falsification notes if invariance/monotonicity expectations fail.

## 6. Promotion Gates

`partial -> supported_bridge` requires:
1. deterministic replay on independent rerun,
2. bounded observable checks pass,
3. no post-hoc policy edits,
4. skeptic report confirms no hidden fit parameter,
5. claim YAML bridge assumptions explicitly reference the contract.

## 7. Immediate Tasks

1. Lock one policy bundle for Weinberg running (`WEINBERG-001`).
2. Lock one policy bundle for strong running (`STRONG-001`).
3. Add convergence criteria (depth and seed stability) to test harness.
4. Add CI checks for policy immutability + replay integrity.

## 8. Non-Goals

1. This RFC does not define absolute mass/energy calibration.
2. This RFC does not choose a GUT normalization convention by itself.

## 9. Acceptance Criteria

RFC-080 reaches `supported` when:
1. one canonical running bundle is used in production for Weinberg and Strong bridges,
2. all required outputs are produced automatically,
3. promotion pipeline rejects non-preregistered or output-tuned running results.

## 10. Critical Decisions to Freeze Now

1. `running_mode`:
   - `theorem_first` (Lean-closed recurrence before long simulation), or
   - `simulation_first` (deterministic simulation artifact first, theorem closure second).
2. `distribution_mode`:
   - fixed rollout schedule, or
   - stationary-distribution running (preferred for IR claims).
3. `cold_start_policy`:
   - burn-in length,
   - inclusion/exclusion rule for pre-overlap ticks,
   - warm-start microstate profile linkage to `RFC-079`.
4. `oracle_mode`:
   - hard fail for tolerance miss, or
   - two-lane output: `structure_match` vs `value_match` (recommended for early bridge work).

## 11. Jumping-the-Gun Risks

1. Closing `g1/g2/g3` before running mode and scale policy are frozen.
2. Reporting IR agreement from hand-picked seeds/horizons.
3. Mixing kernel profiles across runs in one claim closure.
4. Treating exploratory trend lines as promotion-grade evidence.

## 12. Closure Discipline Addendum

1. For each active running claim (`WEINBERG-001`, `STRONG-001`), exactly one
   canonical policy bundle is marked `promotion_candidate` at a time.
2. Policy bundles used for exploratory scans must be tagged `exploratory_only`
   and are non-promotable by default.
3. Any change to `policy_id`, `distribution_mode`, `cold_start_policy`, or
   `depth_schedule` resets claim lane status to `active_hypothesis` until rerun.
4. Running results are invalid for promotion unless replay metadata includes:
   - policy checksum,
   - seed set checksum,
   - kernel/profile ID,
   - artifact hash.
