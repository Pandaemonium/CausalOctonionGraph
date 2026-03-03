# RFC-027: Solar 3-Phase Assimilation, Neutrino Fronts, and Extrasolar Meteor Re-Phasing Contract

Status: Draft (Prediction Lock)  
Date: 2026-03-03  
Owner: COG Core (Codex lane)  
Depends on:
- `cog_v3/rfc/RFC-010_C12_Phase_Sector_Generation_and_Rare_Hop_Test_Contract.md`
- `cog_v3/rfc/RFC-022_CKM_Mixing_from_C12_Hop_Statistics.md`
- `sources/solar_neutrino_muon_tau_fronts_lit_review_v1.md`

---

## 1. Purpose

This RFC locks a concrete prediction set for the hypothesis:

1. Stellar neutrino output phase-biases nearby matter/vacuum into one dominant C12 generation sector (`g = p mod 3`), called **solar 3-phase assimilation**.
2. The Sun's motion through the ambient medium produces a **front-tail asymmetry** in neutrino flavor composition and phase-domain structure.
3. Extrasolar meteoroids entering the solar domain can begin off-phase, then re-phase toward local solar phase; during partial re-phase they exhibit internal interaction signatures.

This RFC is intentionally strict and falsifiable against existing public data.

---

## 2. Hypothesis Definitions

## 2.1 Generation phase

- Generation index: `g = p mod 3`, with `p in C12`.
- Local solar phase domain (working lock): Gen1-dominant.

## 2.2 Solar front and tail

- **Front direction**: upwind direction of Sun's motion through ambient interstellar medium (fixed before analysis from published heliosphere/apex vector).
- **Tail direction**: opposite vector.

## 2.3 Assimilation mechanism (model claim)

- Neutrino propagation through same-phase medium: weak effective phase exchange.
- Neutrino propagation through off-phase medium: enhanced effective phase exchange, driving medium toward local stellar phase over long time.

Note: this mechanism is a COG-model claim and is not assumed in SM.

---

## 3. Locked Predictions

## 3.1 Solar-neutrino directional prediction (primary)

Primary claim `P1`:
- After controlling for known annual `1/r^2` modulation and day-night matter effects, residual neutrino flavor composition contains a non-zero dipole aligned with solar front-tail axis.

Operational model:

`R(t, dir) = A0 + A1*cos(2*pi*t/T_year + phi_year) + A2*D_daynight(t) + A3*(n_dir . n_front)`

Where:
- `R` is chosen neutrino observable (flavor ratio proxy or event class ratio),
- `n_front` is fixed solar front unit vector,
- `A3` is front-tail coefficient of interest.

Prediction:
- `A3 != 0` with sign consistent with:
  - front: larger off-phase flavor content (mu/tau fraction),
  - tail: stronger e-like dominance (Gen1 lock).

## 3.2 Sidereal structure prediction (primary)

Primary claim `P2`:
- Residual anisotropy projects onto sidereal frame aligned to solar apex, not explainable by annual-only harmonics.

Pass condition:
- Apex-aligned component survives model comparison vs annual+daynight null model.

## 3.3 Phase-boundary / front-trap prediction (secondary)

Secondary claim `P3`:
- If multiple large phase domains coexist, boundary regions exhibit elevated flavor-conversion-like activity (effective "front trap" zones).

Immediate-data expectation:
- weak in current solar datasets; stronger in environments with competing strong neutrino sources.

## 3.4 Extrasolar meteor re-phasing prediction (primary for meteor lane)

Primary claim `P4`:
- A subset of incoming interstellar meteoroids shows trajectory-dependent anomalous atmospheric entry behavior consistent with transient internal stress during phase re-phasing.

Predicted signature family:
1. elevated multi-stage fragmentation rate,
2. atypical light-curve jitter bursts near entry path segments that maximize integrated solar neutrino column,
3. directional dependence relative to solar front-tail axis.

## 3.5 Relative-phase interaction prediction

Primary claim `P5`:
- Meteor anomalies are strongest when inferred native phase differs from local solar phase; as re-phasing progresses, anomalies decay.

Proxy prediction (existing data):
- anomaly rate should be highest near first-entry epochs/segments and reduce along path/evolution.

---

## 4. Immediate Data Targets

## 4.1 Solar neutrino datasets

Priority data families:
1. Super-Kamiokande long-baseline solar neutrino time series (including periodicity/day-night products),
2. Borexino solar neutrino time series/public products,
3. SNO/SNO+ time-dependent products where compatible.

## 4.2 Meteor datasets

Priority data families:
1. CNEOS fireball catalog (trajectory + energetics),
2. published interstellar meteor candidate sets,
3. high-cadence meteor light-curve archives when available.

---

## 5. Preregistered Analysis Plan

## 5.1 Solar neutrino model comparison

Models:
1. `M0`: annual + day-night only,
2. `M1`: `M0 + apex dipole term`,
3. `M2`: `M1 + higher harmonics/robustness terms`.

Primary statistic:
- support for `A3 != 0` with stable sign across detector subsets.

Locked thresholds:
1. per-dataset apex coefficient significance: `|A3|/sigma_A3 >= 3`,
2. combined significance across independent datasets: `>= 5 sigma`,
3. model preference: `DeltaBIC(M0 -> M1) <= -10` (strong evidence for apex term),
4. fitted `A3` sign must match front/tail prediction in all primary datasets.

Robustness:
1. leave-one-era-out,
2. detector-systematics nuisance terms,
3. sidereal vs solar-time leakage checks.

## 5.2 Meteor directional anomaly model

Models:
1. `N0`: baseline entry/fragmentation predictors (speed, mass proxy, angle, composition proxy),
2. `N1`: `N0 + front-tail directional term`,
3. `N2`: `N1 + path-integrated solar exposure proxy`.

Primary statistic:
- incremental explanatory power of directional/re-phasing terms over baseline.

Locked thresholds:
1. directional/re-phasing terms improve fit with `DeltaBIC(N0 -> N2) <= -10`,
2. coefficient signs are stable under bootstrap resampling (`>= 90%` same-sign),
3. at least one anomaly-family metric (fragmentation or light-curve burst metric) shows
   corrected `p < 0.01` after multiple-testing control.

---

## 6. Falsification Criteria (Locked)

Hypothesis is considered falsified in this lane if all hold:
1. solar datasets show no reproducible apex-aligned residual after annual/day-night controls,
2. sign of fitted front-tail term is unstable/inconsistent across datasets,
3. meteor anomaly models show no directional/re-phasing incremental signal over baseline.

Numerical falsification trigger:
1. no primary solar dataset reaches `3 sigma` on `A3`,
2. combined apex evidence remains `< 5 sigma`,
3. `DeltaBIC(M0 -> M1) > -10` and `DeltaBIC(N0 -> N2) > -10`.

Partial support requires:
1. consistent sign and non-zero apex term in at least two independent solar datasets,
2. meteor lane directional signal that remains after standard covariates.

---

## 7. Explicit Divergence from Standard Model

This RFC predicts an additional astrophysical-scale phase-domain phenomenon not present in standard neutrino treatment:
1. stellar-neutrino-driven generation-domain assimilation,
2. front-tail phase asymmetry tied to stellar motion through ambient medium,
3. re-phasing transients in off-phase incoming matter.

These are new COG-model predictions, not established SM claims.

---

## 8. Decision Gate

Proceed to dedicated implementation scripts only after this lock:
1. `build_v3_solar_apex_anisotropy_probe_v1.py`
2. `build_v3_neutrino_front_tail_fit_v1.py`
3. `build_v3_extrasolar_meteor_rephase_anomaly_probe_v1.py`

Output contract:
1. machine-readable coefficients and uncertainty summaries,
2. prereg pass/fail table for `P1-P5`,
3. one-page executive verdict.

---

## 9. Notes on Interpretation Discipline

1. This RFC locks predictions before fitting.
2. Null results are informative and must be reported.
3. If primary signals fail, mechanism is downgraded or replaced; no post-hoc reinterpretation without a new RFC.
