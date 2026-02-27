# XOR Physics Calculables Roadmap

Status: Active Planning Doc (2026-02-27)  
Scope: Physics quantities and benchmarks calculable with XOR + motif + perturbation framework.

Depends on:
- `rfc/CONVENTIONS.md`
- `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
- `rfc/RFC-063_XOR_Octonion_Gate_and_Signed_Handed_Dynamics.md`
- `rfc/RFC-065_XOR_Vector_Spinor_Operator_and_Ideal_Stabilization.md`

---

## 1) Usage

This roadmap is an execution matrix:
1. `Status` says whether we can compute it now.
2. `Required Modules` identifies code contracts needed.
3. `Artifact` is the concrete output target.
4. `Claim/RFC Link` maps to governance/promotion pathways.

Status legend:
1. `Ready` = computable now with current stack.
2. `Near` = small implementation gap.
3. `Blocked` = requires unresolved model contracts or major new module.

---

## 2) Ready Now (Compute Immediately)

| ID | Quantity / Benchmark | Status | Required Modules | Artifact | Claim / RFC Link |
|---|---|---|---|---|---|
| XCALC-001 | XOR basis multiplication table (index + sign + handedness) | Ready | `calc/xor_octonion_gate.py` | `sources/xor_gate_tables.md` | RFC-063 |
| XCALC-002 | Left/right sign-flip law audit | Ready | `calc/test_xor_octonion_gate.py` | CI test report | RFC-063 |
| XCALC-003 | Associative vs non-associative triad map (35 triples) | Ready | `calc/xor_stable_motif_scan.py` | `sources/xor_associator_map.json` | RFC-040, RFC-063 |
| XCALC-004 | Support-stable motif scan over all triads | Ready | `calc/xor_stable_motif_scan.py` | `sources/xor_stable_triads.json` | RFC-043, RFC-063 |
| XCALC-005 | Vacuum-drive period spectrum (`e7` left/right) | Ready | `calc/xor_stable_motif_scan.py` | `calc/xor_particle_motif_cycles.json` | RFC-023, RFC-063 |
| XCALC-006 | Single-motif policy cycle atlas | Ready | `calc/xor_particle_motif_cycles.py` | `website/data/xor_particle_motif_cycles.json` | RFC-063 |
| XCALC-007 | Coupled pair period histogram | Ready | `calc/xor_coupled_motif_cycles.py` | `website/data/xor_coupled_motif_cycles.json` | RFC-063 |
| XCALC-008 | Count and list of pairs with period > 4 | Ready | `calc/xor_coupled_motif_cycles.py` | CSV/JSON pair table | RFC-063 |
| XCALC-009 | Vector vs spinor phase-cycle comparison in same basis | Ready | `calc/xor_vector_spinor_phase_cycles.py` | `website/data/xor_vector_spinor_phase_cycles.json` | RFC-065 |
| XCALC-010 | Furey ideal motif cycles (`S^u`, `S^d`) in XOR notation | Ready | `calc/xor_furey_ideals.py` | `website/data/xor_furey_ideal_cycles.json` | RFC-065 |
| XCALC-011 | Electron favored-vector motif repeated product traces | Ready | `calc/xor_vector_spinor_phase_cycles.py` | trace JSON | RFC-065 |
| XCALC-012 | Left/right spinor electron repeated product traces | Ready | `calc/xor_vector_spinor_phase_cycles.py` | trace JSON | RFC-065 |
| XCALC-013 | Deterministic replay hashes for motif simulations | Ready | existing test/build scripts | replay hash table | RFC-028, RFC-063 |
| XCALC-014 | Operator-sequence sensitivity scan (same seed, different sequence) | Ready | `calc/xor_vector_spinor_phase_cycles.py` | `sources/xor_sequence_sensitivity.json` | RFC-063, RFC-065 |
| XCALC-015 | Support occupancy fractions by basis channel (`e0..e7`) | Ready | cycle traces + postprocess | `sources/xor_support_occupancy.json` | RFC-063 |
| XCALC-016 | Exhaustive XOR basis conformance table (`8x8`) with stable hash | Ready | `calc/xor_basis_conformance.py` | `website/data/xor_basis_conformance.json` | RFC-063 |
| XCALC-017 | Canonical motif registry (vector + spinor seeds) | Ready | `calc/xor_motif_registry.py` | `website/data/xor_motif_registry.json` | RFC-043, RFC-065 |
| XCALC-018 | Perturbation-to-attractor transition matrix | Ready | `calc/xor_perturbation_attractor_matrix.py` | `website/data/xor_perturbation_attractor_matrix.json` | RFC-049, RFC-063 |
| XCALC-019 | Event engine MVP (typed state + deterministic scheduler + built-in scenarios) | Ready | `calc/xor_event_engine.py` | `website/data/xor_event_engine_scenarios.json` | RFC-040, RFC-063 |

---

## 3) Near-Term (Small Gap, High Value)

| ID | Quantity / Benchmark | Status | Required Modules | Artifact | Claim / RFC Link |
|---|---|---|---|---|---|
| XCALC-101 | Charge-sign interaction matrix (like/opp/neutral) | Near | two-node XOR wrapper + charge proxy | `sources/xor_charge_sign_matrix.json` | RFC-040, RFC-042 |
| XCALC-102 | Electron-electron vs electron-positron interaction class stats | Near | XCALC-101 + perturbation runner | `sources/xor_lepton_pair_classes.json` | RFC-040 |
| XCALC-103 | Hydrogen binding proxy scan (motif overlap + cycle stability) | Near | `calc/hydrogen_binding.py` + XOR bridge | `claims/HYDROGEN-001` Gate artifact | HYDROGEN-001 |
| XCALC-104 | Perturbation-response curves (period vs perturbation load) | Near | perturbation harness | `sources/xor_perturbation_response.json` | RFC-049 |
| XCALC-105 | Attractor basin estimates for motif classes | Near | random seed sweeps + cycle detector | `sources/xor_basin_estimates.json` | RFC-049 |
| XCALC-106 | Entropy of projected motif traces | Near | profile projection + Shannon calculator | `sources/xor_projected_entropy.json` | RFC-055 |
| XCALC-107 | Temperature proxy from interaction intensity | Near | interaction counters + proxy mapping | `sources/xor_temperature_proxy.json` | RFC-036 |
| XCALC-108 | Defect lifetime and annihilation rates | Near | defect predicate + long runs | `sources/xor_defect_lifetimes.json` | RFC-032 |
| XCALC-109 | Discrete running curves from perturbation ensembles | Near | ensemble runner + governance lock | `sources/xor_running_ensemble.json` | RFC-046, RFC-037 |
| XCALC-110 | Spinor ideal leakage rate under raw vs stabilized update | Near | `calc/xor_spinor_stabilizer.py` | `sources/xor_ideal_leakage.json` | RFC-065 |

---

## 4) Blocked by Core Contract Closures

| ID | Quantity / Benchmark | Status | Blocking Item | Required Modules | Claim / RFC Link |
|---|---|---|---|---|---|
| XCALC-201 | Promotion-grade many-body scattering observables | Blocked | D4/D5 full closure + many-body reduction closure | multi-node dynamic graph sim | RFC-028, RFC-053 |
| XCALC-202 | Proton internal color dynamics with claim-grade observables | Blocked | extended projection contract hardening | `piObsWithSector` maturity | RFC-042, RFC-044 |
| XCALC-203 | Hydrogen-level quantitative spectrum analogue | Blocked | proton state + observable calibration | proton motif + two-body stack | HYDROGEN-001 |
| XCALC-204 | Weinberg-angle IR derivation from discrete running | Blocked | running mechanism closure without fitted params | coupling-ratio + running module | RFC-037, RFC-046 |
| XCALC-205 | Gravity proxy calibration to physical scales | Blocked | scale calibration + slowdown-field closure | slowdown field + mapping | RFC-030, RFC-052 |
| XCALC-206 | Lorentz recovery quantitative benchmark | Blocked | continuum-limit mapping and battery | large DAG coarse-graining | RFC-060 |
| XCALC-207 | Dark-matter defect abundance vs observational window | Blocked | cosmological profile + scale mapping | long-run defect sim | RFC-032, RFC-052 |
| XCALC-208 | Thermodynamic-limit equations of state | Blocked | large-ensemble infra + calibration policy | macro-ensemble simulator | RFC-055, RFC-052 |

---

## 5) Prioritized Execution Queue (Next 2 Weeks)

1. XCALC-101: charge-sign interaction matrix.
2. XCALC-103: hydrogen binding proxy via XOR bridge.
3. XCALC-104: perturbation-response curves.
4. XCALC-110: spinor ideal stabilization leakage benchmark.
5. XCALC-106: projected entropy traces.
6. XCALC-107: temperature proxy traces.

Definition of done for each:
1. deterministic artifact generated,
2. tests pass,
3. replay hash recorded,
4. claim/RFC cross-link added.

---

## 6) Data Product Standards

Every calculable should emit:
1. JSON artifact (canonical),
2. CSV summary (human/ops),
3. replay metadata (`generated_at_utc`, schema version, code path),
4. no-fit governance note if compared to physical constants.

Artifact naming:
1. `calc/xor_<topic>.json`
2. `website/data/xor_<topic>.json`
3. optional `sources/xor_<topic>.md` narrative summary.

---

## 7) Promotion and Falsification Rules

1. No promotion without deterministic replay.
2. No fitted attenuation or hidden tuning for constant derivation claims.
3. Explicitly record failed branches as falsification artifacts.
4. Distinguish structural proxy results vs physical calibrated results in all outputs.

---

## 8) Suggested Task Dossiers (Ready to Assign)

1. `DOSSIER-XCALC-101`: Implement charge-sign interaction matrix + tests.
2. `DOSSIER-XCALC-103`: Bridge hydrogen proxy into XOR motif stack.
3. `DOSSIER-XCALC-104`: Add perturbation ensemble runner with fixed seeds.
4. `DOSSIER-XCALC-110`: Implement spinor stabilizer and leakage comparison.
5. `DOSSIER-XCALC-106`: Projected entropy calculator over existing cycle traces.

Each dossier should include:
1. exact files to edit,
2. acceptance tests,
3. required artifacts,
4. claim/RFC links.

---

## 9) Notes

1. This roadmap is intentionally compute-first and calibration-later.
2. SI-unit claims remain gated behind RFC-052 scale calibration policy.
3. XOR notation is execution-level; Furey basis conventions remain source-of-truth semantics.
