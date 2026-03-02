# v3 CMB-to-COG Validation Targets (v1)

Date: 2026-03-02  
Owner: COG Core  
Purpose: Convert standard CMB observables into explicit COG validation targets.

## 1. Scope

This document does not claim CMB correspondence yet.
It defines what must be measured in COG for that claim to be credible.

## 2. CMB Property to COG Target Mapping

## 2.1 Near-perfect blackbody spectrum (`T0 ~ 2.725 K`)

COG target:

1. Build a synthetic radiance spectrum from photon-like motif flux crossing an observer shell.
2. Fit to Planck form and report residuals.

Required bridge:

1. Map motif-level frequency/phase-cycle statistics to effective frequency bins.
2. Define an energy proxy per motif crossing event.

Pass signal:

1. Single-temperature blackbody fit dominates over non-Planck alternatives.

Falsification signal:

1. Persistent non-Planck shoulders/lines not explainable by finite-size artifacts.

## 2.2 High isotropy with tiny anisotropy (`DeltaT/T ~ 1e-5`)

COG target:

1. Build synthetic sky map `T_eff(theta, phi)` from observer null-shell sampling.
2. Measure mean, variance, and angular anisotropy amplitude.

Required bridge:

1. Observer definition (worldline + local tetrad analogue).
2. Null-shell sampling protocol from kernel events.

Pass signal:

1. Nearly isotropic map with stable small anisotropy regime under scale growth.

Falsification signal:

1. Large persistent directional lattice imprint at mesoscale.

## 2.3 CMB dipole from observer motion

COG target:

1. Compare sky maps for rest observer vs boosted observer construction.
2. Extract dipole amplitude and alignment in synthetic map.

Required bridge:

1. Operational definition of observer boost in kernel coordinates.

Pass signal:

1. Dominant dipole mode appears under boost and scales with boost proxy.

Falsification signal:

1. No consistent dipole response or strong non-dipole contamination under simple boosts.

## 2.4 Acoustic peak structure in angular power spectrum

COG target:

1. Compute `C_l` from synthetic sky maps.
2. Test whether repeated peak-like harmonic structure appears.

Required bridge:

1. Coarse-grained pre-recombination-like coupling analog in COG dynamics.
2. Stable horizon-scale simulation procedure.

Pass signal:

1. Multi-peak pattern robust to seed reruns and box scaling.

Falsification signal:

1. Flat/noisy `C_l` without structured peaks after artifact controls.

## 2.5 Polarization (E-mode dominant; B-mode mostly lensing-level)

COG target:

1. Define local polarization proxy from oriented photon-like motif transport.
2. Derive synthetic Stokes `Q/U`, then `E/B` decomposition.

Required bridge:

1. Orientation transport law for photon-like motifs.
2. Projection from motif orientation to detector polarization basis.

Pass signal:

1. E-dominant spectrum in baseline runs.

Falsification signal:

1. B-dominated baseline without a modeled lensing-like mechanism.

## 2.6 Last-scattering epoch behavior (`z ~ 1100` in standard cosmology)

COG target:

1. Identify a sharp transition from high to low photon-matter interaction rate in simulated cosmic history.
2. Show post-transition free-streaming-like behavior.

Required bridge:

1. COG analog of optical depth / interaction opacity over coarse-grained time.

Pass signal:

1. Distinct transition epoch with stable downstream free-streaming signatures.

Falsification signal:

1. No clear transition; continuous strong scattering regime.

## 2.7 Tight spectral-distortion bounds (`mu`, `y` small)

COG target:

1. Quantify departures from blackbody in synthetic spectrum.
2. Fit distortion-like templates and report amplitudes.

Required bridge:

1. Distortion estimator over effective frequency bins from motif events.

Pass signal:

1. Distortions remain small and stable under enlarged simulation volume.

Falsification signal:

1. Large persistent distortions not attributable to finite-size transients.

## 3. Core Measurement Objects to Add in v3

1. `observer_shell_sampler_v1`: null-shell event collection around an observer.
2. `radiance_spectrum_builder_v1`: motif-event to spectral proxy pipeline.
3. `sky_map_builder_v1`: angular map construction from shell events.
4. `cmb_harmonics_v1`: `C_l` estimator and dipole extraction.
5. `polarization_estimator_v1`: `Q/U -> E/B` decomposition from motif orientation proxy.

## 4. Minimal Execution Order (Practical)

1. Build isotropy + dipole pipeline first (cheapest, fastest falsification).
2. Add blackbody-fit pipeline second.
3. Add harmonic (`C_l`) structure tests third.
4. Add polarization and distortion analyses after observer pipeline stabilizes.

## 5. Artifact Contract

Planned files:

1. `cog_v3/sources/v3_cmb_correspondence_panel_v1.json`
2. `cog_v3/sources/v3_cmb_correspondence_panel_v1.md`

Required fields:

1. `kernel_profile`
2. `convention_id`
3. `observer_definition_id`
4. `spectrum_fit_summary`
5. `anisotropy_summary`
6. `dipole_summary`
7. `harmonic_summary`
8. `polarization_summary`
9. `distortion_summary`
10. `falsification_flags`

## 6. Interpretation Rule

Do not label "CMB solved" unless at least:

1. blackbody fit,
2. isotropy + dipole behavior,
3. nontrivial harmonic structure

are all reproduced with stable scale trends and documented uncertainty.
