# RFC-006: SM-Divergence Predictions from Triplet Orientation and Chiral Commit

Status: Draft  
Date: 2026-03-02  
Owner: COG Core  
Depends on:
- `cog_v3/rfc/RFC-003_e000_Anchor_Chirality_and_C_Asymmetry_Test_Contract.md`
- `cog_v3/rfc/RFC-004_Physics_Grounded_Kernel_Selection_Criteria.md`
- `cog_v3/rfc/RFC-005_Triplet_Decay_Commit_and_Neutrino_Chirality_Hypothesis.md`

## 1. Purpose

Pre-register the main ways COG-v3 is expected to differ from Standard Model (SM)
effective behavior if the following hypothesis is true:

1. baryon triplet motifs have real internal orientation,
2. weak conversion is governed by a chiral commit mechanism (`tau_bridge` vs `tau_relock`),
3. neutrino-like branch carries directional/chiral commit information.

This RFC defines explicit predictions, observables, and falsification paths.

## 2. Scope and Epistemic Status

This RFC is:

1. a prediction registry,
2. a measurement contract,
3. a falsification plan.

This RFC is not:

1. a claim that divergences are already observed,
2. a replacement of SM for current data interpretation.

## 3. Baseline Hypothesis

Assume:

1. triplet motifs have a transverse internal orientation label `O`,
2. perturbation can create transient `d*` branch,
3. conversion outcome is controlled by timescale competition:
   - commit: `tau_bridge`,
   - rollback: `tau_relock`,
4. parity mirror `P` flips orientation sign and changes commit bias.

## 4. Divergence Prediction Matrix

### 4.1 P1: Orientation-dependent beta transition term

Claim:

1. beta-like transitions include an extra orientation-coupled term not present in
   standard low-energy parameterization.

Operational form (model-level):

1. `p_commit = p0 + k_O * f(O, spin, direction)`,
2. with `k_O != 0` under this hypothesis.

SM comparison:

1. SM includes known spin/polarization correlations but no extra persistent internal
   motif orientation variable of this class.

Primary observable:

1. `A_commit_orient` from matched orientation-prepared panels.

### 4.2 P2: Commit-threshold signature in short-time decay hazard

Claim:

1. at short times, conversion probability is not purely memoryless exponential,
2. there is a threshold-like dependence on `delta_tau = tau_bridge - tau_relock`.

Primary observable:

1. `p_commit(delta_tau)` crossover curve with fitted threshold location.

SM comparison:

1. no explicit microstate threshold variable of this type in standard treatment.

### 4.3 P3: Effective site-class preference in triplet conversion

Claim:

1. in motif coordinates, one leg class may convert with higher probability under
   matched orientation conditions.

Important caveat:

1. this is an effective motif-site prediction,
2. it is not a claim that identical fermions become permanently labeled particles.

Primary observable:

1. `A_site = (p_site_a - p_site_b) / (p_site_a + p_site_b)`.

### 4.4 P4: Suppressed RH-like neutrino leakage branch

Claim:

1. dominant branch remains LH-like in weak lane,
2. rare RH-like leakage appears in specific transient/misalignment conditions.

Primary observable:

1. `r_RH = N_RH_like / (N_RH_like + N_LH_like)` in controlled decay panels.

SM comparison:

1. minimal SM has no weak-coupled RH neutrino channel.

### 4.5 P5: Two-front wave occupancy with detector-layer asymmetry

Claim:

1. wave layer can show two-front-balanced occupancy,
2. detector-layer events remain asymmetric/exclusive under absorptive measurement rules.

Primary observables:

1. `wave_transport_class`,
2. `detector_exclusivity`,
3. `double_hit_rate`.

SM comparison:

1. this is a model-side structural prediction, not a direct contradiction of QED
   unless mapped to experimental coincidence distributions.

### 4.6 P6: Residual lattice anisotropy at extreme scales

Claim:

1. anisotropy is small but not exactly zero at micro lattice scales,
2. it should reduce with coarse-graining if kernel is viable.

Primary observable:

1. `v_max / v_min` from axis/face/body probes versus scale.

## 5. Priority Ranking (what to test first)

Priority order:

1. `P2` commit-threshold signature (most internal and directly testable in sim),
2. `P1` orientation-coupled commit term,
3. `P4` RH-like leakage bound,
4. `P5` wave-vs-detector split quantification,
5. `P6` anisotropy scaling,
6. `P3` site-class preference (exploratory).

## 6. Pre-registered Observables and Thresholds

Exploratory thresholds for "signal worth follow-up":

1. `|A_commit_orient| >= 0.05` with 95 percent CI excluding zero,
2. threshold model fit for `p_commit(delta_tau)` beats null monotonic/no-threshold
   model by pre-registered information criterion delta,
3. `r_RH > 0` with stable non-artifactual confidence bound and strict controls,
4. `detector_exclusivity >= 0.30` under two-front occupancy panels,
5. anisotropy ratio improves or stays bounded under scale increase.

These are provisional and can be tightened after pilot runs.

## 7. Falsification Conditions

This divergence lane is disfavored if all hold:

1. orientation-coupled term collapses to noise across mirrors/seeds/scales,
2. no reproducible commit-threshold effect appears,
3. RH-like leakage remains statistically null under validated chirality classifier,
4. two-front occupancy never yields detector asymmetry above noise,
5. anisotropy does not improve with kernel upgrades and scaling.

## 8. Controls and Confound Guards

Required controls:

1. mirror (`P`) and conjugation (`C`) matched runs,
2. seed reruns with fixed and shifted seed basins,
3. box-size reruns for finite-size artifact checks,
4. convention-id reruns where possible,
5. no mixed-kernel comparisons without explicit metadata.

Known confounds:

1. stationary attractor inflation in candidate scoring,
2. near-detector immediate-arrival artifacts in small boxes,
3. event-order policy leakage into false asymmetry.

## 9. Artifact Contract

Planned scripts:

1. `cog_v3/calc/build_v3_sm_divergence_prediction_panel_v1.py`
2. `cog_v3/calc/test_v3_sm_divergence_prediction_panel_v1.py`

Planned outputs:

1. `cog_v3/sources/v3_sm_divergence_prediction_panel_v1.json`
2. `cog_v3/sources/v3_sm_divergence_prediction_panel_v1.md`

Required fields:

1. `kernel_profile`
2. `kernel_candidate_id`
3. `convention_id`
4. `event_order_policy`
5. `stencil_id`
6. `A_commit_orient`
7. `delta_tau_curve`
8. `r_RH`
9. `wave_transport_class`
10. `detector_exclusivity`
11. `anisotropy_ratio`
12. confidence intervals for all registered primary metrics.

## 10. Immediate Next Steps

1. implement metric extraction for `A_commit_orient` and `delta_tau` panels,
2. patch scorer to deweight stationary attractors in divergence tests,
3. run pilot panel and publish first registered table,
4. decide keep/pivot based on pre-registered falsification criteria.
