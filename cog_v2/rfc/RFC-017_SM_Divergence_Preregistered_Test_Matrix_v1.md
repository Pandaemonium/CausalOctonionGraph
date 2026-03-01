# RFC-017: SM Divergence Preregistered Test Matrix v1

Status: Draft  
Date: 2026-03-01  
Owner: COG Core  
Depends on:
- `cog_v2/rfc/RFC-001_Canonical_Axiom_Profile.md`
- `cog_v2/rfc/RFC-003_Theta_Continuum_Identification_Contract.md`
- `cog_v2/rfc/RFC-006_Bridge_Construction_from_CxO_Combinatorics.md`
- `cog_v2/rfc/RFC-015_Operational_Velocity_Definition_v1.md`
- `cog_v2/rfc/RFC-016_Operational_Mass_Definition_v1.md`

## 1. Purpose

Define a preregistered, falsifiable experiment matrix where COG v2 makes predictions
that can differ from Standard Model (SM) expectations.

This RFC is an execution contract. It is not a claim that divergences are already proven.

## 2. Pre-registration Rules (mandatory)

For each test lane, freeze before any fit:

1. hypothesis id and exact observable,
2. event/sample selection cuts,
3. model form (SM null and COG alternative),
4. estimator and test statistic,
5. threshold and decision rule,
6. accepted nuisance handling,
7. train/validation split policy (if any),
8. allowed sensitivity analyses.

Prohibited:

1. changing cuts after seeing target statistic,
2. swapping primary statistic post hoc,
3. changing COG bridge functional form post hoc.

## 3. Tier A: Most Accessible (now / next few years)

### A1. CP topology conditioning in heavy flavor

1. **Context:** LHCb/Belle-II style CP asymmetry analysis by event-topology classes.
2. **SM null:** asymmetry pattern follows CKM-driven smooth dependence after known hadronic systematics.
3. **COG prediction:** asymmetry residuals correlate with motif-decoherence class, yielding class-conditioned offsets not captured by smooth CKM-only fit.
4. **Primary statistic:** out-of-sample likelihood gain (`Delta logL`) of preregistered COG class term over SM baseline.
5. **Pass criterion:** COG term improves fit with preregistered significance and stable sign across datasets.
6. **Falsification:** no significant gain or unstable sign under prereg robustness checks.
7. **Accessibility:** high.

### A2. Running-coupling shape reanalysis (staircase vs smooth)

1. **Context:** meta-analysis of existing coupling-vs-scale points.
2. **SM null:** smooth logarithmic RG trend.
3. **COG prediction:** piecewise/staircase effective running in specific scale windows from discrete combinatoric sectors.
4. **Primary statistic:** information-criterion delta (AIC/BIC) between preregistered staircase and smooth models.
5. **Pass criterion:** staircase model wins with preregistered penalty and cross-validation stability.
6. **Falsification:** smooth model consistently preferred under prereg penalties.
7. **Accessibility:** high.

### A3. Sidereal / orientation anisotropy residual search

1. **Context:** reanalysis of precision anisotropy-sensitive data streams.
2. **SM null:** no sidereal modulation beyond known systematics.
3. **COG prediction:** tiny harmonic modulation tied to residual fold/axis anisotropy leakage.
4. **Primary statistic:** preregistered harmonic amplitude (`A_1`, `A_2`) and phase consistency.
5. **Pass criterion:** amplitude above threshold with stable phase over independent runs.
6. **Falsification:** amplitudes consistent with null after systematics controls.
7. **Accessibility:** medium-high.

### A4. EDM regime-conditioned analysis

1. **Context:** neutron/proton/deuteron EDM constraints.
2. **SM null:** extremely small effective EDM (near-zero in current reach).
3. **COG prediction:** regime-conditioned CP leakage can produce nonzero class-dependent EDM contribution.
4. **Primary statistic:** bounded effect-size inference under prereg regime map.
5. **Pass criterion:** coherent nonzero regime-conditioned term across channels.
6. **Falsification:** all channels consistent with null within prereg sensitivity.
7. **Accessibility:** medium (depends on experiment access/updates).

### A5. Neutrino oscillation waveform-shape deformation

1. **Context:** long-baseline oscillation probability shape tests.
2. **SM null:** PMNS-driven sinusoidal form plus standard matter effects.
3. **COG prediction:** small preregistered non-sinusoidal deformation basis linked to discrete phase-lock sectors.
4. **Primary statistic:** likelihood ratio for fixed deformation basis coefficients.
5. **Pass criterion:** nonzero coefficients with reproducible sign/ordering.
6. **Falsification:** coefficients consistent with zero in all datasets.
7. **Accessibility:** medium (next data cycles).

## 4. Tier B: Less Accessible but High-Discrimination

### B1. Proton-decay channel hierarchy bias

1. **SM null:** no proton decay observed (or model-dependent channel patterns in BSM scenarios).
2. **COG prediction:** channel ordering reflects motif-break pathway combinatorics.
3. **Statistic:** channel-rank concordance with preregistered ordering.
4. **Accessibility:** low near-term.

### B2. Regime-dependent strong-CP nonuniformity map

1. **SM null:** single tiny effective theta behavior.
2. **COG prediction:** near-zero in coherent domains, potentially nonzero in specific decohered motif classes.
3. **Statistic:** class-conditioned CP-odd residual map consistency.
4. **Accessibility:** low-medium (analysis-heavy, indirect observables).

### B3. Quantized transport plateaus

1. **SM null:** smooth continuum transport in effective vacuum.
2. **COG prediction:** rational-plateau transport families (`dx/N`) in motif-stable domains.
3. **Statistic:** plateau occupancy significance vs smooth model.
4. **Accessibility:** low in direct particle experiments; high in simulation-lab falsification.

## 5. Matrix Execution Priority

Priority order:

1. A1 CP topology conditioning,
2. A2 running-shape reanalysis,
3. A3 sidereal anisotropy residuals,
4. A4 EDM regime-conditioned map,
5. A5 neutrino deformation basis,
6. Tier B lanes as longer-horizon campaigns.

## 6. Required Outputs per Lane

Each lane must emit:

1. prereg YAML/JSON spec,
2. frozen analysis script hash,
3. dataset manifest hash,
4. result packet with decision and falsification status,
5. skeptic review note.

## 7. Machine-readable Companion

Companion matrix:

- `cog_v2/sources/sm_divergence_preregistered_test_matrix_v1.json`
