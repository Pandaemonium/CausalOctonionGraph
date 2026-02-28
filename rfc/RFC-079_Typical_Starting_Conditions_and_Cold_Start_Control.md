# RFC-079: Typical Starting Conditions and Cold-Start Control Contract

Status: Active Draft - Policy Lock Candidate (2026-02-27)  
Module:
- `COG.Sim.StartProfile`
- `COG.Sim.Preconditioning`
Depends on:
- `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
- `rfc/RFC-069_Canonical_Simulation_Artifact_Contract.md`
- `rfc/RFC-072_Tritium_Typical_Microstate_Approximation_Strategies.md`
- `sources/typical_starting_conditions_lit_review.md`

---

## 1. Executive Summary

This RFC closes the "cold start" governance gap.

Locked direction:
1. Canonical production runs are **preconditioned full-lightcone runs**.
2. Cold starts are **required controls**, not default truth proxies.
3. Typical-initialization claims are ensemble-level epistemic claims with declared deterministic generation policy.

This makes initialization handling explicit, reproducible, and falsifiable across ALPHA/WEINBERG/STRONG/MASS campaigns.

---

## 2. What Is Already Locked

From existing RFCs:
1. `RFC-028`: canonical runs must start from full-lightcone microstate; sparse starts are non-canonical.
2. `RFC-069`: simulation artifact must include full initial state and deterministic update rule.
3. `RFC-072`: "typical microstate" is epistemic ensemble support, not ontic randomness.

Current missing piece:
1. a single cross-project contract for start-profile classes and mandatory cold/warm control reporting.

---

## 3. Definitions

1. `cold_start`: preconditioning ticks = 0.
2. `preconditioned_start`: same initial full-lightcone state, then deterministic rollout for `K_pre > 0` ticks before measurement.
3. `start_profile`: named policy tuple
   - `{lightcone_profile_id, init_state_hash, preconditioning_ticks, boundary_policy_id}`.
4. `typical_set`: deterministic ensemble of admissible start profiles under declared constraints (`RFC-072`).

---

## 4. Policy Locks

## 4.1 Canonical start profile (mandatory)

For claim-bearing production runs:
1. initialize full lightcone per `RFC-028`,
2. run declared preconditioning ticks `K_pre`,
3. begin measurement at global tick `K_pre + 1`.

`K_pre` must be declared before execution and stored in artifact metadata.

## 4.2 Cold-start control (mandatory)

For every production case bundle:
1. run a matched cold-start control (`K_pre = 0`) on identical topology, seeds, and horizon,
2. store control outputs side-by-side with production outputs,
3. publish delta metrics.

## 4.3 No hidden start tuning

Forbidden:
1. post-hoc changing `K_pre` to improve target fit without policy-id update,
2. changing boundary/seed profile without new start-profile ID and rerun,
3. selecting only favorable starts while suppressing controls.

---

## 5. Observable Reporting Contract

Each simulation package must include:
1. `start_profile.json`,
2. `control_profile.json` (cold start),
3. `start_sensitivity_report.json` containing:
   - per-case warm/cold deltas,
   - plateau-window summary deltas,
   - max divergence and mean divergence.

Minimum metrics:
1. `delta_mean_post_overlap`,
2. `delta_final_tick`,
3. `delta_plateau_window`.

---

## 6. Promotion Gates (Initialization Robustness)

A claim depending on simulation observables cannot be promoted unless:
1. both production and cold-control runs are present,
2. start-policy metadata hashes replay correctly,
3. divergence metrics are reported on fixed windows,
4. either
   - divergence is below declared tolerance, or
   - divergence is explicitly incorporated as uncertainty/branch split.

If this gate fails, status remains `partial`.

---

## 7. Typical-Initialization Campaign Rules

When exact physical microstate is unknown:
1. generate deterministic ensemble of candidate starts (per `RFC-072`),
2. canonicalize by symmetry/orbit rules if declared,
3. run fixed preconditioning + control protocol for each candidate,
4. report support-weighted or robustness-filtered summaries.

No single-run output may be labeled "typical" without a declared ensemble policy.

---

## 8. Immediate Implementation Tasks

1. Add `start_profile` and `control_profile` fields to simulation artifact templates (RFC-069 alignment).
2. Add validator checks:
   - preconditioning metadata present,
   - cold-control pair present for promotable claims.
3. Add one runner helper per constant family that emits `start_sensitivity_report.json`.
4. Update manager/skeptic dossiers to request initialization-sensitivity tables by default.

---

## 9. Decision Record

Locked by this RFC:
1. cold start is a control, not canonical production default,
2. canonical production requires explicit deterministic preconditioning,
3. initialization sensitivity must be measured and published for promotion-eligible claims,
4. "typical start" remains an epistemic ensemble construct with deterministic generation policy.

