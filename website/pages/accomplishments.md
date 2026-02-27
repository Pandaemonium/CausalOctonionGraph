# COG Lab Accomplishments

This page is the public-facing accomplishments list for COG Lab.

For live, timestamped upgrades with Layman/Student/Physicist summaries, see:
- `/web/proof_ledger`

Source of truth:
- `website/accomplishments.yml`
- `claims/CLAIM_STATUS_MATRIX.yml`

Display rules:
1. `supported` claims may use strongest language.
2. `partial` and `active_hypothesis` claims must include explicit open gaps.
3. Every card must include evidence pointers.

## Spotlight Wins

### 1) Machine-checked electroweak UV invariant: 1/4
- Claim: `WEINBERG-UV-001`
- Status: `supported`
- Why it matters: A nontrivial electroweak structural value is formally locked and invariant in the current transport frame.
- Evidence:
  - `claims/WEINBERG-UV-001.yml`
  - `CausalGraph.sin2ThetaWObs_exclusive_u1_eq_one_four`
  - `CausalGraph.sin2ThetaWObs_exclusive_u1_stabilizer_invariant_bool`
  - `calc/test_weinberg_h2_governance.py::test_expected_baseline_values`
- Open gap: Z-pole running to 0.23122 remains under `WEINBERG-001`.

### 2) Vacuum stabilizer reconciliation in the gauge stack
- Claim: `GAUGE-001`
- Status: `partial`
- Why it matters: Locks a core symmetry structure used by downstream constant and motif claims.
- Evidence:
  - `claims/gauge_group.yml`
  - `GaugeGroup.fano_aut_count`
  - `GaugeGroup.vacuum_stabilizer_count`
  - `calc/test_gauge.py`
- Open gap: final bridge harmonization remains in claim notes.

### 3) Photon-vacuum color-sector exclusion in the current model
- Claim: `PHOTON-001`
- Status: `partial`
- Why it matters: Sharp selection-rule behavior for photon/vacuum orbit semantics.
- Evidence:
  - `claims/PHOTON-001.yml`
  - `CausalGraph.vacuum_orbit_colorSector_zero`
  - `CausalGraphTheory/PhotonMasslessness.lean`
- Open gap: full physical energy-scale mapping is not closed.

## Promising Frontier

### Mass as tick-overhead observable
- Claim: `MASS-001`
- Status: `partial`
- Evidence: `CausalGraph.tickMass_mono`, `CausalGraph.step_tickMass_nondecreasing`, `calc/test_koide.py`
- Open gap: calibrated physical-units closure.

### Universal period-4 lepton-orbit backbone
- Claim: `LEPTON-001`
- Status: `active_hypothesis`
- Evidence: `CausalGraph.universal_Ce_period_four`, `calc/test_furey_electron_orbit.py`
- Open gap: mechanism to `m_mu / m_e = 206.768...`.

### Strong-coupling structured proxy (1/7 baseline)
- Claim: `STRONG-001`
- Status: `partial`
- Evidence: `calc/estimate_alpha_strong.py`, `calc/test_constants.py::TestAlphaStrong::test_alpha_strong_candidate_is_stab_ratio`
- Open gap: running-corrected closure at physical scale.

## Foundational Rigor Layer

### Graph-distance triangle semantics
- Claim: `DIST-001`
- Status: `partial`
- Evidence: `CausalGraph.dist_triangle`, `calc/test_graph.py::test_distance_triangle`
- Open gap: macro-level metric-recovery bridge.

### Confluence and race-condition control
- Claim: `RACE-001`
- Status: `partial`
- Evidence: `RaceCondition.confluence`, `calc/test_tick.py::TestClassify`
- Open gap: broader many-body stress testing.

### Alternativity as time-driver primitive
- Claim: `ALG-001`
- Status: `partial`
- Evidence: `left_alternative`, `right_alternative`, `non_associative_witness`
- Open gap: end-to-end observable mapping.

## What This Page Does Not Claim

1. It does not claim COG has replaced the Standard Model or relativity.
2. It does not present partial claims as experimentally closed.
3. It does not hide open mechanisms, calibration gaps, or unresolved running bridges.
