# RFC-037: Weinberg Derivation Avenues and Closure Gates

Status: Active  
Depends on:
- `rfc/RFC-026_Gauge_Constant_Derivation_Strategy.md`
- `rfc/RFC-029_Weinberg_Angle_Gap_Closure.md`
- `claims/weinberg_angle.yml`

## 1. Purpose

Define all active avenues for deriving `sin^2(theta_W)` in COG, with explicit
pass/fail gates and anti-retrofit controls.

Target for comparison:
- `sin^2(theta_W)(M_Z) = 0.23122` (policy-fixed reference target).

## 2. Avenues

1. H2 fixed-weight projector derivation.
2. S4 character-theory class weighting.
3. Subgroup-orbit measure weighting.
4. Dynamic occupancy weighting from deterministic graph trajectories.
5. H1 discrete scale bridge from UV observable to `M_Z`.
6. H3 projector-support expansion via predeclared algebraic rules.
7. Coupling-ratio route (`g`, `g'` proxies then `g'^2/(g^2+g'^2)`).
8. Cross-constant closure with `alpha_s` and `alpha_em`.
9. Lean invariance proofs for chosen observable family.
10. Robustness ablations (basis, finite-size, policy perturbation).
11. Phenomenology proxy checks (NC/CC structure-level constraints).
12. Formal falsification ledger for each failed branch.
13. Associator-load differential running from deterministic update dynamics.

## 3. Current Implemented Infrastructure

H2 policy-locked harness:
- `calc/weinberg_s4_decomp.py`
- `calc/weinberg_h2_policies.json`
- `calc/run_weinberg_h2_ablation.py`
- `sources/weinberg_h2_ablation_results.md`

H1 discrete bridge scaffold:
- `calc/gauge_scale_bridge.py`
- `calc/weinberg_h1_bridge_policies.json`
- `calc/estimate_weinberg_angle_weighted.py`
- `sources/weinberg_weighted_estimate_results.md`

S4 character-theory probe:
- `calc/weinberg_s4_character_weights.py`
- `sources/weinberg_s4_character_weight_scan.md`

Coupling-ratio scaffold (Avenue 7):
- `calc/weinberg_coupling_policies.json`
- `calc/weinberg_coupling_ratio.py`
- `calc/test_weinberg_coupling_ratio.py`
- `sources/weinberg_coupling_ratio_results.md`

Associator-running prototype (Avenue 13):
- `calc/weinberg_associator_policies.json`
- `calc/weinberg_associator_running.py`
- `calc/test_weinberg_associator_running.py`
- `sources/weinberg_associator_running_results.md`

Associator-running ensemble (Avenue 13, macro-conditioned):
- `calc/weinberg_associator_ensemble_conditions.json`
- `calc/weinberg_associator_ensemble.py`
- `calc/test_weinberg_associator_ensemble.py`
- `sources/weinberg_associator_ensemble_results.md`

Current verdict snapshot:
- Locked structural baseline: `1/2`.
- Strongest frozen H2 candidate: `1/4`.
- Character-weight avenue (current scanned families): no near-target candidate.
- H2 ceiling for current fixed-weight branch is therefore treated as `1/4` pending a
  new, predeclared observable family.
- Associator-load running avenue is instrumented with rollout-derived traffic and
  has initial robustness checks (basis selector, source ordering).
- Ensemble layer is now available to evaluate statistical combinatoric averages
  under predeclared environmental condition families.

## 3A. Associator-Load Running Hypothesis (Avenue 13)

Working idea:
- The electroweak core subspace is associative (quaternionic), so static EW-only
  evolution does not by itself generate a differential running effect.
- Running appears when updates involve non-associative interactions outside that core.
- The COG running proxy is the differential local associator load between channel
  observables used for `g'^2` and `g^2`.

Non-negotiable constraint:
- Any running correction must be computed from deterministic kernel events
  (`temporalCommit`, ordered `interactionFold`, `combine`) rather than fitted
  attenuation constants.

## 4. Closure Gates

Gate A (definition lock):
- observable definition and policy IDs frozen before target comparison.

Gate B (invariance):
- Lean proof(s) of invariance under allowed S4/basis actions for the selected observable.

Gate C (robustness):
- ablation table does not collapse under small policy/basis changes.

Gate D (scale honesty):
- if scale bridge used, bridge policy is fixed and uncertainty disclosed.
- bridge rows are not promotable unless bridge parameters are derived from
  model-internal dynamics.

Gate G (associator mechanism):
- if running is claimed, publish an explicit associator-load observable and show
  the claimed `sin^2(theta_W)` shift is reproduced by that observable under fixed
  rollout rules.

Gate H (quaternionic control):
- control experiments restricted to associative EW-core dynamics must show no
  spurious running from the estimator itself.

Gate E (cross-constant consistency):
- no contradiction with active `alpha_s` and `alpha_em` contracts at same scale policy.

Gate F (governance):
- failed branches are retained as falsification artifacts; no silent replacement.

## 5. Immediate Execution Order

1. Lock H2 ceiling in governance artifacts:
   - record `1/4` as current fixed-weight ceiling,
   - prevent unbounded H2 policy fishing.
2. Promote Avenue 7 coupling-ratio route:
   - freeze `g'^2` and `g^2` proxy-source policy IDs,
   - compare proxy ratios against H2 observables.
3. Implement Avenue 13 instrumentation:
   - define channel-resolved associator-load observables from deterministic updates,
   - add quaternionic-control and non-associative-mixing rollouts.
4. Add robust perturbation harness for Avenue 10:
   - finite-size and basis perturbation stability report.
5. Formalize selected H2/A7 observable in Lean (Avenue 9).
6. Run cross-constant consistency check (Avenue 8).
7. Re-open H1 only after a derived bridge mechanism exists.

## 6. Success Criteria for WEINBERG-001 Promotion

`WEINBERG-001` can only move beyond `partial` when:
1. one observable family is frozen and proven invariant,
2. H2 and/or H1 branch passes robustness gates,
3. scale policy is explicit and fixed,
4. claim notes include full ablation + falsification context.
5. any running correction is backed by a derived mechanism (Avenue 13),
   not policy literals.

If no branch passes, claim remains `partial` with explicit failed-branch records.
