# RFC-012: Associator-Field Curvature and Family-Activity Test Contract

Status: Draft
Date: 2026-03-03
Owner: COG Core
Depends on:
- `cog_v3/rfc/RFC-004_Physics_Grounded_Kernel_Selection_Criteria.md`
- `cog_v3/rfc/RFC-009_S960_Phase_Fibered_E8_Symmetry_Model.md`
- `cog_v3/sources/v3_octavian240_elements_v1.csv`
- `cog_v3/sources/v3_s960_elements_v1.csv`

## 1. Purpose

Turn the "associator as curvature" idea into a strict, falsifiable test lane.

This RFC does not assume gravity is solved. It defines measurable proxies:
1. local associator activity fields,
2. radial associator profiles around motifs,
3. family-level associator statistics and mass-lane relevance.

## 2. Core definitions

For state ids with multiplication table `mul`:
1. `Assoc(a,b,c) = 1` if `(a*b)*c != a*(b*c)`, else `0`.
2. `A_local(x,t)`: associator activity density at voxel `x`, tick `t`, computed from sampled local triplets from the update neighborhood.
3. `A_shell(r,t)`: shell-average of `A_local` at lattice radius `r` around motif center.
4. `A_var(r)`: variance of `A_local` in shell `r`.

Interpretation:
1. high `A_local` means strong local ordering sensitivity (nonassociative activity),
2. "curvature proxy" is the radial structure of `A_shell` and `A_var`.

## 3. Baseline facts from current artifacts

## 3.1 S960 counts (already measured)

1. order-6 count: `168`
2. order-12 count: `224`
3. singleton conjugation count: `8`

## 3.2 Q240 family associator activity (direct computation)

Measured as mismatch fraction over all `(b,c)` for each fixed `a`:
1. `A16_basis_signed_unit`: mean `0.809375`, min `0.0`, max `0.925`
2. `B112_line_plus_e000_halfsum`: mean `0.8925`
3. `C112_complement_halfsum`: mean `0.925`

Immediate implication:
1. the statement "A-family always associates" is false.
2. identity and negative identity are special low-activity outliers.

## 4. Hypotheses

## H1 (associator localization)

Around stable motifs, `A_local` is spatially structured and nonuniform versus vacuum baseline.

## H2 (radial decay)

`A_shell(r)` decays with radius from motif center in a reproducible way.
Exploratory target:
1. power-law fit is preferred over flat/noise null.
2. inverse-square is a hypothesis, not a prior truth.

## H3 (family activity hierarchy)

Family-level associator activity contributes to an effective "computational drag" ordering:
1. low-activity lanes easier to propagate,
2. high-activity lanes more rephasing-heavy.

This is a test lane for mass-proxy relevance, not a mass claim.

## 5. Null models

N1:
1. `A_local` indistinguishable from shuffled local-triplet baseline.

N2:
1. no stable radial trend in `A_shell(r)`.

N3:
1. family-level associator metrics have no predictive value for propagation/stability proxies.

## 6. Metrics

1. `A_bg`: baseline associator density in vacuum control.
2. `DeltaA_peak = max_r(A_shell(r) - A_bg)`.
3. fit quality:
   - power-law RMSE,
   - exponential RMSE,
   - flat-null RMSE.
4. `rho_family`: correlation between family associator score and motif drag proxy (`V_hat`, recurrence burden, phase-hop entropy).

## 7. Promotion gates

Gate 1:
1. `DeltaA_peak` above control uncertainty.

Gate 2:
1. radial model beats flat null on repeated seeds.

Gate 3:
1. family-level trend reproducible and not driven by identity outliers only.

## 8. Falsifiers

Reject this lane if:
1. associator fields are noise-like under controls,
2. radial behavior is nonreproducible,
3. family signal disappears after outlier and boundary controls.

## 9. Implementation plan

Planned scripts:
1. `cog_v3/calc/build_v3_associator_field_probe_v1.py`
2. `cog_v3/calc/test_v3_associator_field_probe_v1.py`

Planned outputs:
1. `cog_v3/sources/v3_associator_field_probe_v1.json`
2. `cog_v3/sources/v3_associator_radial_profiles_v1.csv`
3. `cog_v3/sources/v3_associator_family_activity_v1.csv`
4. `cog_v3/sources/v3_associator_field_probe_v1.md`

Required fields:
1. `kernel_profile`
2. `convention_id`
3. `stencil_id`
4. `seed_id`
5. `A_bg`
6. `A_shell_profile`
7. `A_var_profile`
8. `fit_scores`
9. `family_activity_summary`
10. `gate_results`

## 10. Notes

1. This RFC does not import differential-geometry claims by analogy alone.
2. Only reproducible associator-field observables count as evidence.
