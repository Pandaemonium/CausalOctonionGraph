# Standard Model Free Parameters and COG Derivation Notes

Date: 2026-02-27
Owner: COG research notes

## 1) Scope and Counting Convention

This note lists free parameters in:
1. Minimal Standard Model (massless neutrinos): 19.
2. SM + Dirac neutrino masses: 26.
3. SM + Majorana neutrino masses: 28.

The counts are the standard Lagrangian-parameter counts built from:
1. gauge couplings,
2. Higgs potential coefficients,
3. fermion masses/Yukawas,
4. flavor-mixing phases/angles,
5. strong CP phase,
6. neutrino-sector additions (if enabled).

## 2) Literature Anchors Used

Primary references used for this inventory:
1. PDG 2024 electroweak review (gauge couplings in covariant derivative, Higgs potential, CKM matrix in charged current):
   https://pdg.lbl.gov/2024/reviews/rpp2024-rev-standard-model.pdf
2. PDG 2024 CKM review (3 angles + 1 CP phase):
   https://pdg.lbl.gov/2024/reviews/rpp2024-rev-ckm-matrix.pdf
3. PDG 2024 neutrino-mixing review (Dirac vs Majorana phase counting):
   https://pdg.lbl.gov/2024/reviews/rpp2024-rev-neutrino-mixing.pdf
4. PDG 2024 QCD review (`alpha_s` and `theta` as free QCD parameters):
   https://pdg.lbl.gov/2024/reviews/rpp2024-rev-qcd.pdf

## 3) Complete Free-Parameter Inventory

### 3.1 Minimal SM (19 parameters)

1. `g1` (or `g'`) hypercharge gauge coupling
2. `g2` weak isospin gauge coupling
3. `g3` strong gauge coupling
4. `mu^2` Higgs potential mass term
5. `lambda` Higgs quartic coupling
6. `m_e`
7. `m_mu`
8. `m_tau`
9. `m_u`
10. `m_c`
11. `m_t`
12. `m_d`
13. `m_s`
14. `m_b`
15. `theta12_CKM`
16. `theta13_CKM`
17. `theta23_CKM`
18. `delta_CKM`
19. `theta_QCD` (strong CP angle)

### 3.2 Dirac-neutrino extension (+7 => 26 total)

20. `m_nu1`
21. `m_nu2`
22. `m_nu3`
23. `theta12_PMNS`
24. `theta13_PMNS`
25. `theta23_PMNS`
26. `delta_PMNS`

### 3.3 Majorana-neutrino extension (+9 => 28 total)

Add all Dirac-neutrino parameters, plus:
27. `alpha21_M` (Majorana phase)
28. `alpha31_M` (Majorana phase)

## 4) COG Derivation Notes (Per Parameter)

Status legend:
1. `closed_proxy`: algebraic/proxy claim exists and is reproducible.
2. `partial`: structured mechanism exists but does not yet match physical target or has bridge assumptions.
3. `open`: no accepted extraction pipeline yet.

### 4.1 Gauge Couplings

1. `g1`
   - COG status: `partial`.
   - Route: infer from `alpha_em` and `sin^2(theta_W)` at declared scale after conversion convention lock.
   - Current blockers: `ALPHA-001` is an upper-bound/proxy closure, not full physical-value closure; `WEINBERG-001` IR bridge remains open.
   - Artifacts: `claims/ALPHA-001.yml`, `claims/weinberg_angle.yml`, `claims/WEINBERG-UV-001.yml`.

2. `g2`
   - COG status: `partial`.
   - Route: same as `g1`, from `alpha_em` + `sin^2(theta_W)` with fixed normalization and scale policy.
   - Current blockers: same as above.
   - Artifacts: `claims/weinberg_angle.yml`, `calc/weinberg_coupling_ratio.py`.

3. `g3`
   - COG status: `partial` (strong proxy exists).
   - Route: COG strong-sector observable and running bridge.
   - Current blockers: physical `alpha_s(M_Z)` gap and running closure remain open.
   - Artifacts: `claims/STRONG-001.yml`, `calc/test_strong_alpha.py`.

### 4.2 Higgs Potential

4. `mu^2`
   - COG status: `open`.
   - Route: define scalar/vacuum order-parameter observable, then map to effective potential coefficient.
   - Blockers: no canonical Higgs-sector extraction contract.

5. `lambda`
   - COG status: `open`.
   - Route: same Higgs-sector pipeline as `mu^2`, with fixed normalization and scale calibration.
   - Blockers: no closed quartic observable in current claim set.

### 4.3 Charged-Lepton Masses

6. `m_e`
   - COG status: `partial`.
   - Route: motif-level mass observable (currently drag/tick/correlator candidates).
   - Blockers: mass observable contract still not universally frozen across claims.
   - Artifacts: `claims/mass_tick_frequency.yml`, `rfc/RFC-045_Energy_Mass_Observable_Unification.md`.

7. `m_mu`
   - COG status: `open`.
   - Route: generation-2 motif + triality/intertwiner + mass observable extraction.
   - Blockers: unique motif lock, full phase-gauge closure, and observable lock.
   - Artifacts: `claims/muon_mass.yml`, `claims/triality_generations.yml`.

8. `m_tau`
   - COG status: `open`.
   - Route: generation-3 motif closure and same mass extraction pipeline.
   - Blockers: same as `m_mu`, with less mature motif closure.
   - Artifacts: `calc/xor_furey_ideals.py`, `claims/triality_generations.yml`.

### 4.4 Quark Masses

9. `m_u`
10. `m_c`
11. `m_t`
12. `m_d`
13. `m_s`
14. `m_b`
   - COG status: `open` for all six.
   - Route: lock quark motif basis and extraction observable compatible with confinement/strong-sector contracts.
   - Blockers: no canonical quark mass extraction claims at this time.
   - Candidate dependencies: `GAUGE-001`, `STRONG-001`, confinement gates in `rfc/RFC-047_Confinement_Claim_Gates.md`.

### 4.5 CKM Flavor Parameters

15. `theta12_CKM`
16. `theta13_CKM`
17. `theta23_CKM`
18. `delta_CKM`
   - COG status: `open`.
   - Route: derive up/down sector mismatch from motif/projector overlap and transported bases.
   - Blockers: no locked CKM extraction theorem/script pipeline.
   - Notes: `GEN-001` generation structure support exists but does not yet produce CKM numerics.

### 4.6 Strong CP

19. `theta_QCD`
   - COG status: `open`.
   - Route: identify CP-odd topological/associator invariant mapping to effective `F \tilde{F}` coefficient.
   - Blockers: no canonical `theta` observable in current COG claim registry.

### 4.7 Neutrino Sector (if enabled)

20. `m_nu1`
21. `m_nu2`
22. `m_nu3`
23. `theta12_PMNS`
24. `theta13_PMNS`
25. `theta23_PMNS`
26. `delta_PMNS`
27. `alpha21_M` (Majorana only)
28. `alpha31_M` (Majorana only)
   - COG status: `open`.
   - Route: neutrino motif family + lepton-sector mixing observable + phase-gauge-safe extraction.
   - Blockers: no neutrino motif contract and no PMNS extraction framework in claims.

## 5) Practical Conversion Rules (When COG Observables Are Ready)

With a fixed scale `Q` and fixed convention:
1. `e^2(Q) = 4*pi*alpha_em(Q)`
2. `g2(Q) = e(Q)/sin(theta_W(Q))`
3. `gY(Q) = e(Q)/cos(theta_W(Q))`
4. If GUT normalization is used: `g1(Q) = sqrt(5/3)*gY(Q)`
5. `g3(Q)` from `alpha_s(Q)` via `g3^2(Q)=4*pi*alpha_s(Q)`

These are not COG derivations by themselves; they are conversion bridges from COG observables to standard coupling conventions.

## 6) High-Value Next Closures

1. Freeze one canonical mass observable contract (control subtraction, normalization, plateau window).
2. Close full phase-gauge equivalence for triality/intertwiner pathway before promoting muon/tau mass claims.
3. Close `WEINBERG-001` running bridge to target scale under locked governance.
4. Promote `STRONG-001` from fixed proxy to running-calibrated extraction.
5. Add claim files for CKM and PMNS with explicit bridge assumptions and falsification conditions.

## 7) Foundational Decision Locks (Do Not Skip)

1. Discrete running policy lock (`rfc/RFC-080_Discrete_RGE_Contract.md`) before claiming IR couplings.
2. Single-anchor calibration lock (`rfc/RFC-081_Mass_Anchor_Policy_Decision.md`) before claiming absolute masses.
3. Matrix-first flavor lock (`rfc/RFC-082_Flavor_Unitary_Extraction_Contract.md`) before claiming CKM/PMNS angles/phases.
4. Charge-derivation lock (`CHARGE-DERIVATION-001`) before promoting anomaly results as first-principles charge derivations.

## 8) Closure Order (Enforced Priority)

Recommended strict closure order to minimize drift:

1. `THETA-001` (structure-first, low calibration dependency).
2. `WEINBERG-001` running bridge under one fixed RFC-080 bundle.
3. `STRONG-001` running bridge under one fixed RFC-080 bundle.
4. Anchor decision (`RFC-081`) before absolute mass promotions.
5. CKM/PMNS matrix extraction (`RFC-082`) before any angle-level closures.

## 9) Stop Conditions (Prevent Scope Creep)

Pause new closure lanes if any condition is true:

1. active lane has unresolved contract-gate errors,
2. active lane changed profile/policy without reset,
3. claim artifacts are missing replay hash/checksum,
4. promoted outputs depend on mixed kernel profiles.
