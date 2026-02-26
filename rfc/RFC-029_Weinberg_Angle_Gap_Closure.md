# RFC-029: Weinberg Angle Gap Closure (Baseline 1/2 -> Physical 0.231)

Status: Active - Decision and Validation Draft (2026-02-26)
Module:
- `COG.Core.WeakMixing`
- `COG.Core.GaugeObservables`
Depends on:
- `rfc/RFC-017_Vacuum_Stabilizer_Reconciliation.md`
- `rfc/RFC-020_Kernel_Representation_Reconciliation.md`
- `rfc/RFC-026_Gauge_Constant_Derivation_Strategy.md`
- `claims/weinberg_angle.yml`
Literature basis:
- `sources/weinberg_angle_gap_lit_review.md`

---

## 1. Executive Summary

COG now has a locked structural baseline:
- `sin2ThetaWRaw = 1/2` from fixed projector masks in `WeakMixingObservable.lean`.

This RFC treats `1/2` as a baseline checkpoint, not a final prediction, and defines a falsifiable closure program to explain the gap to physical weak-mixing observables near `0.231`.

Primary decision:
- move from cardinality ratio to a physically weighted observable contract, then test whether scale running is still required.

---

## 2. Problem Statement

Current state:
1. projectors are locked and idempotent (good),
2. raw ratio is exact `1/2` (good as baseline),
3. claim statement still targets `~0.231` (unresolved mechanism).

Main risk:
- retrofitting denominator or masks after seeing mismatch.

Main opportunity:
- promote WEINBERG-001 from heuristic dimension ratio to an invariant weighted observable with ablation gates.

---

## 3. Hypotheses Under Test

## H1. UV boundary + running

Interpretation:
- COG computes a UV boundary weak angle; observed `M_Z` value requires running.

Test requirement:
- explicit graph-scale -> `Q` map and weak-angle running bridge with uncertainty.

## H2. Metric mismatch (cardinality is not physical weight)

Interpretation:
- physical quantity must be a weighted projector ratio (trace/norm/coupling weighted), not coordinate count.

Test requirement:
- define one frozen weighting map before checking target agreement.

## H3. EW projector support mismatch

Interpretation:
- current EW support set is incomplete.

Test requirement:
- any expanded support must be derived from predeclared algebraic selection rules, then frozen prior to numeric comparison.

---

## 4. Canonical Observable Upgrade

Replace baseline-only ratio:
- `sin2ThetaWRaw = |U1| / |EW|`

with canonical candidate:
- `sin2ThetaWObs = Tr(W_U1 * P_U1) / Tr(W_EW * P_EW)`

where:
1. `P_U1`, `P_EW` are locked projector operators,
2. `W_U1`, `W_EW` are fixed weighting operators derived from one declared representation/normalization policy,
3. all objects are deterministic functions of kernel state and frozen conventions.

No post-hoc weight tuning is allowed.

---

## 5. S4 Role Clarification

Locked fact:
- vacuum stabilizer action is S4 in current encoding.

Policy:
1. S4 may define admissible representation weights and invariance checks.
2. S4 alone is not accepted as direct proof of weak-angle value.
3. Any S4-trace method is model-internal and must pass independent ablations.

---

## 6. Lean Deliverables

Add/extend in `CausalGraphTheory/WeakMixingObservable.lean`:

1. `weightedTrace : Weight -> Projector -> Rat`
2. `sin2ThetaWObs : WeightPolicy -> Rat`
3. invariance theorem(s) under allowed basis/stabilizer actions:
   - `sin2ThetaWObs_invariant`
4. anti-retrofit theorem stubs:
   - changing projector/weight policy changes a hash-locked definition id.

Baseline theorem `sin2ThetaWRaw_eq_one_half` remains as reference.

---

## 7. Python Deliverables

Add script:
- `calc/estimate_weinberg_angle_weighted.py`

Required outputs:
1. baseline `1/2`,
2. weighted candidate value(s) from frozen policy set,
3. ablation matrix:
   - weight policy,
   - projector support policy,
   - scale bridge on/off,
4. uncertainty decomposition and deterministic replay hash.

Optional bridge script extension:
- `calc/gauge_scale_bridge.py` for H1 testing.

---

## 8. Acceptance Gates

WEINBERG-001 can move beyond current partial state only if all pass:

1. `sin2ThetaWObs` definition is frozen before target comparison.
2. Lean invariance checks build with no `sorry`.
3. Ablation matrix published; value is not a single-case coincidence.
4. If running is invoked, scale map and uncertainty are explicit.
5. Claim notes clearly separate:
   - baseline structural ratio,
   - weighted observable result,
   - running-adjusted comparison (if used).

---

## 9. Falsification Conditions

Reject H2 branch if:
1. no admissible frozen weighting policy yields stable movement away from `1/2`, or
2. results are highly basis-fragile.

Reject H1 branch if:
1. no consistent scale bridge maps COG boundary value to `M_Z` with realistic uncertainty, or
2. required running assumptions exceed declared model scope.

If both fail, WEINBERG-001 remains open and no promotion is allowed.

---

## 10. Claim File Impact

`claims/weinberg_angle.yml` should remain `partial` until this RFC closes.

Required wording updates (follow-up patch):
1. classify `sin2ThetaWRaw_eq_one_half` as baseline,
2. move `~0.231` target to "open mechanism under RFC-029",
3. forbid projector-denominator changes without policy-id update.

---

## 11. Recommended Execution Order

1. Freeze weighting policy candidates and identifiers.
2. Implement weighted observable in Lean and Python.
3. Run ablations without running bridge.
4. If still offset, add scale bridge and rerun.
5. Update claim metadata and governance notes.

---

## 12. References

1. PDG 2024 Electroweak review:
   https://pdg.lbl.gov/2024/reviews/rpp2024-rev-standard-model.pdf
2. Georgi and Glashow (1974):
   https://doi.org/10.1103/PhysRevLett.32.438
3. Erler and Ramsey-Musolf:
   https://arxiv.org/abs/hep-ph/0409169
4. Erler et al. (2024):
   https://arxiv.org/abs/2406.16691
5. Atzori Corona et al. (2024):
   https://arxiv.org/abs/2405.09416
6. CMS (2024):
   https://arxiv.org/abs/2405.11484
7. Kim (2004):
   https://arxiv.org/abs/hep-ph/0403196
8. Schwichtenberg (2019):
   https://doi.org/10.1140/epjc/s10052-019-6878-1
9. Bazzocchi et al. (2009):
   https://arxiv.org/abs/0901.2086
10. Ding et al. (2024):
    https://arxiv.org/abs/2408.15988
