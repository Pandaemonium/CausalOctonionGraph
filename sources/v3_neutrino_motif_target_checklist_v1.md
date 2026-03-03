# Neutrino Motif Target Checklist (Delta m^2 + theta23 Sector) (v1)

Date: 2026-03-02
Owner: COG Core
Status: Draft (`test_ready` targeting checklist)

## 1) Goal

Define a practical target checklist for neutrino motifs using observables that are actually measured with precision:
1. `Delta m^2_21`
2. `Delta m^2_3l` (NO: `Delta m^2_31`, IO: `Delta m^2_32`)
3. `sin^2(theta_23)` and octant structure

This replaces any attempt to target a precise ratio `m_{nu_mu}/m_{nu_tau}`, which is not directly measured as a robust flavor-mass observable.

## 2) Experimental targets (NuFIT v6.1, 2025)

Primary reference:
1. NuFIT v6.1 results page (data through Nov 2025): https://www.nu-fit.org/?q=node/309
2. NuFIT global analysis paper: https://arxiv.org/abs/2410.05380
3. Journal version: https://doi.org/10.1007/JHEP12(2024)216

Use the `IC24 with SK atmospheric data` block by default.

## 2.1 Normal ordering (NO) targets

1. `Delta m^2_21 = 7.537 (+0.094/-0.10) x 10^-5 eV^2`
2. `Delta m^2_3l = +2.511 (+0.021/-0.020) x 10^-3 eV^2`
3. `sin^2(theta_23) = 0.470 (+0.017/-0.014)`
4. `theta_23 = 43.29 deg (+0.96/-0.79)`

## 2.2 Inverted ordering (IO) targets

1. `Delta m^2_21 = 7.537 (+0.094/-0.10) x 10^-5 eV^2`
2. `Delta m^2_3l = -2.483 (+0.020/-0.020) x 10^-3 eV^2`
3. `sin^2(theta_23) = 0.550 (+0.013/-0.016)`
4. `theta_23 = 47.90 deg (+0.73/-0.92)`

Global preference in this table:
1. IO disfavored with `Delta chi^2 = 5.9` versus NO.

## 3) What to fit in COG

Do not start from flavor-labeled neutrino masses.

Fit these layers instead:
1. three long-lived neutrino-like motif modes (`nu_1, nu_2, nu_3`) as mass-eigenstate analogs,
2. an emergent mixing map from motif basis to flavor-probe basis,
3. oscillation-like transition probabilities versus a simulation analog of `L/E`.

## 4) Derived target ratios (good early checks)

These are useful because they are scale-light and robust:
1. `r = Delta m^2_21 / |Delta m^2_3l|`

Targets:
1. NO: `r ~ 0.0300`
2. IO: `r ~ 0.0304`

If your motif model misses this ratio class badly, do not trust absolute-scale calibration.

## 5) Checklist (execution)

## A. Motif identification

1. [ ] Find at least 3 replay-stable neutrino-like motifs under fixed kernel/profile.
2. [ ] Verify each candidate has long lifetime and low interaction cross-coupling in neutral test lanes.
3. [ ] Confirm no trivial duplicate under symmetry transforms.

## B. Effective mass-eigenstate extraction

1. [ ] Define an effective frequency/phase-evolution observable per motif.
2. [ ] Convert pairwise frequency gaps to `Delta m^2` analogs (with preregistered map).
3. [ ] Rank motifs consistently into `(1,2,3)` by extracted gap ordering.

## C. Mixing-sector extraction

1. [ ] Define three flavor probes (`e`, `mu`, `tau`) as operational detectors/projectors (preregistered).
2. [ ] Measure transition probabilities `P(alpha -> beta)` over `L/E` analog grid.
3. [ ] Fit for `theta_23` sector first (hold other sectors nuisance if needed in early phase).

## D. Target comparison

1. [ ] Match `r = Delta m^2_21 / |Delta m^2_3l|` within exploratory tolerance.
2. [ ] Match sign and magnitude class of `Delta m^2_3l` for chosen ordering hypothesis.
3. [ ] Match `sin^2(theta_23)` central region and octant behavior.

## E. Robustness

1. [ ] Reproduce under orientation panels.
2. [ ] Reproduce under boundary panels.
3. [ ] Reproduce under seeded event-order panel.
4. [ ] Report uncertainty bands from bootstrap over seeds/windows.

## 6) Promotion gates (suggested)

## Gate 1 (coarse viability)

1. `r` within factor 2 of NuFIT target.
2. stable sign and ordering pattern for `Delta m^2_3l` analog.

## Gate 2 (intermediate)

1. `r` within 30%.
2. `sin^2(theta_23)` in correct octant band for selected ordering lane.

## Gate 3 (serious)

1. `r` within 10%.
2. `sin^2(theta_23)` within 2-sigma NuFIT window.
3. passes all robustness panels.

## 7) Non-goals (for this checklist)

1. full PMNS closure in one pass,
2. absolute neutrino mass-scale closure (`m_beta`, `sum m_nu`, `m_betabeta`),
3. CP-phase closure.

These can be added after `Delta m^2` + `theta_23` lane is stable.

## 8) Data artifact contract (recommended)

1. `cog_v3/sources/v3_neutrino_motif_candidates_v1.json`
2. `cog_v3/sources/v3_neutrino_delta_m2_fit_v1.json`
3. `cog_v3/sources/v3_neutrino_theta23_fit_v1.json`
4. `cog_v3/sources/v3_neutrino_oscillation_panel_v1.md`

## 9) Reality check

If this lane fails repeatedly, likely causes are:
1. wrong motif family (not true neutrino-like modes),
2. detector/probe definition leakage,
3. kernel anisotropy contaminating oscillation analog,
4. phase-sector map (C12) not yet physically aligned.

Treat these as kernel/model diagnostics, not as reasons to force-fit targets.
