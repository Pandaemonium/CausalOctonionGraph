# RFC-025: Superconductivity and Ferroelectricity Modeling Program

Status: Active - Research Design Draft (2026-02-26)
Module:
- `COG.Benchmarks.Superconductivity`
- `COG.Benchmarks.Ferroelectricity`
Depends on:
- `rfc/RFC-020_Kernel_Representation_Reconciliation.md`
- `rfc/RFC-022_Lightcone_Semantics_and_Causal_Locality.md`
- `rfc/RFC-023_Discrete_Phase_Clocks_and_Relative_Phase_Interactions.md`
- `rfc/RFC-024_Discrete_Phase_Signatures_Across_Physics.md`
Literature basis:
- `sources/superconductivity_ferroelectricity_lit_review.md`

---

## 1. Executive Summary

This RFC defines how COG should approach superconductivity-like and ferroelectricity-like behavior:

1. Treat both as benchmark classes for emergent phase-order dynamics.
2. Prioritize mesoscopic observables (locking, winding, switching, hysteresis, domain walls).
3. Avoid mechanism overreach (no immediate claim of full BCS or ab initio lattice chemistry).
4. Require falsifiable tests and multi-signature evidence before promoting any claim.

---

## 2. Motivation

The project now has:

1. A deterministic kernel representation (RFC-020).
2. Local causal update constraints (RFC-022).
3. Discrete phase observables (`phi4`, `DeltaPhi4`) as active hypotheses (RFC-023).

The next foundational step is to test whether these ingredients can reproduce high-value condensed-matter signatures in controlled graph experiments.

---

## 3. Scope and Non-Scope

## 3.1 In scope

1. Graph-level analog modeling of superconductivity signatures.
2. Graph-level analog modeling of ferroelectric signatures.
3. Comparison against known phenomenology classes.

## 3.2 Explicitly out of scope (for this RFC)

1. Claiming COG has already derived microscopic BCS pairing.
2. Claiming COG has already derived full material-specific ferroelectric chemistry.
3. Claiming direct quantitative agreement with real materials without calibration protocol.

---

## 4. Target Signature Families

## 4.1 Superconductivity family S

S1. Phase coherence growth and persistence.
S2. Weak-link phase-locking plateaus under periodic drive.
S3. Loop winding or flux-periodic analog behavior.
S4. Phase-slip events as defect-mediated dissipation proxy.

## 4.2 Ferroelectricity family F

F1. Discrete polarization-sector stability.
F2. Reversible and irreversible switching under field-like bias ramps.
F3. Hysteresis loop generation and area scaling.
F4. Domain-wall creation, migration, pinning, and annihilation.

---

## 5. COG Observable Contract (New)

Every benchmark run must emit:

1. `coherence_score(t)`:
   - alignment/coherence statistic over selected subgraphs.
2. `delta_phi_histogram(t)`:
   - distribution of `DeltaPhi4` at active interaction sites.
3. `winding_index(loop, t)`:
   - integer loop index for selected cycles.
4. `phase_slip_events`:
   - discrete slip log with timestamps and locations.
5. `polarization_sector(region, t)`:
   - branch/sector label for ferroelectric analog regions.
6. `domain_wall_density(t)` and `domain_wall_velocity(t)`.
7. `hysteresis_loop_area(run)` for driven sweeps.

These are required even when the run fails, to improve debugger quality.

---

## 6. Benchmark Designs

## 6.1 Benchmark B-SC-1: weak-link locking

Setup:
- two coherent regions connected by sparse coupling edges;
- periodic external forcing at controllable amplitude/frequency.

Outputs:
- lock-plateau map,
- slip statistics,
- stability windows.

Pass condition:
- reproducible plateau structure across deterministic replay.

## 6.2 Benchmark B-SC-2: loop quantization analog

Setup:
- closed graph loops with controlled perturbation.

Outputs:
- winding-index persistence,
- transition thresholds between winding sectors.

Pass condition:
- long-lived quantized winding sectors with discrete transitions.

## 6.3 Benchmark B-FE-1: switching and hysteresis

Setup:
- two-sector initialization with cyclical bias sweep.

Outputs:
- switching latency,
- coercive-threshold proxy,
- loop area vs sweep rate.

Pass condition:
- stable hysteresis loops under repeated cycles.

## 6.4 Benchmark B-FE-2: domain-wall kinetics

Setup:
- seeded multi-domain initial states plus controlled perturbation schedules.

Outputs:
- wall-density evolution,
- mobility/pinning map.

Pass condition:
- nontrivial wall transport regimes (mobile, pinned, annihilating).

---

## 7. Lean and Python Work Split

## 7.1 Lean (definitions and invariants)

1. Define formal observable interfaces:
   - `coherenceScore`
   - `windingIndex`
   - `polarizationSector`
   - `domainWallDensity`
2. Prove deterministic replay invariance for observable extraction.
3. Prove boundedness/integer-valuedness where expected (winding, sector labels).

## 7.2 Python (benchmark execution)

1. Add scripts:
   - `calc/bench_sc_weak_link.py`
   - `calc/bench_sc_loop_winding.py`
   - `calc/bench_fe_hysteresis.py`
   - `calc/bench_fe_domain_walls.py`
2. Emit standardized JSONL metrics for dashboard and debugger.
3. Add smoke tests that verify deterministic replay and metric schema.

---

## 8. Falsification and Promotion Rules

A claim can be promoted from `hypothesis` to `simulation_supported` only if:

1. At least two independent signatures in the same family are reproduced (for example S2 plus S4).
2. Results survive seed/control sweeps without fragile parameter tuning.
3. Deterministic replay exactly reproduces trajectory and derived metrics.

A claim can be promoted to `theorem_proved` only when the corresponding kernel property is formalized in Lean.

---

## 9. Risk Register

R1. Overfitting risk:
- tuned benchmarks can produce fake analogs.
- Mitigation: cross-benchmark validation and held-out protocols.

R2. Mechanism conflation risk:
- matching one signature can be non-unique.
- Mitigation: multi-signature requirement and negative controls.

R3. Semantic drift risk:
- dashboard language may imply stronger physics claims than evidence supports.
- Mitigation: force evidence mode tags (`theorem_proved`, `simulation_supported`, `literature_analogy_only`) in all benchmark reports.

---

## 10. Open Questions

1. Which minimal local COG rule set yields robust loop-winding sectors without fragile tuning?
2. Does `DeltaPhi4` directly control switching barriers in ferroelectric analogs?
3. Are there stable domain-wall quasiparticles with reusable transport function in the graph?
4. Can one shared defect framework explain both phase slips and domain-wall pinning?

---

## 11. Acceptance Criteria

This RFC is considered operational when:

1. All four benchmark scripts exist and run in CI smoke mode.
2. Observable JSONL schema is stable and consumed by dashboard/debugger.
3. At least one superconductivity-family and one ferroelectricity-family benchmark produce reproducible nontrivial behavior.
4. Claim files for these results carry explicit evidence mode tags.

---

## 12. References

See:
- `sources/superconductivity_ferroelectricity_lit_review.md`

