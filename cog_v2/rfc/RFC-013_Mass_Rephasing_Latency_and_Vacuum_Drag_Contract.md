# RFC-013: Mass as Rephasing Latency and Vacuum-Coupling Drag Contract

Status: Draft  
Date: 2026-03-01  
Owner: COG Core  
Depends on:
- `cog_v2/rfc/RFC-001_Canonical_Axiom_Profile.md`
- `cog_v2/rfc/RFC-004_Triplet_Coherence_and_e000_Leakage_Hypothesis.md`
- `cog_v2/rfc/RFC-008_Layered_Causality_and_Defect_Falsification_Contract.md`

## 1. Purpose

Define a canonical, falsifiable mass interpretation under v2 axioms:

1. time advances strictly one layer per edge (no skipped causal ticks),
2. apparent "time skipping" is reinterpreted as low spatial transport per tick,
3. effective mass is an emergent latency ratio from internal rephasing plus vacuum-coupling drag.

This RFC provides an operational contract, not a full SM mass closure.

## 2. Core Decision

In canonical v2, mass is represented by a transport-latency ratio:

`m_eff ~ <R_t + lambda * V_t> / <Y_t>`

where:

1. `R_t` = internal rephasing load at tick `t`,
2. `V_t` = vacuum-coupling drag at tick `t` (e000-coupled),
3. `Y_t` = transport yield at tick `t`,
4. `lambda` = fixed preregistered coupling weight.

Interpretation:

1. higher `m_eff` means more update budget goes to internal phase reconciliation and less to displacement,
2. all nodes still advance one depth step per tick,
3. "slow particle" means low displacement per tick, not lower tick rate.

## 3. Geometry and Causality Guardrail

Canonical layered causality remains mandatory:

1. edges satisfy `depth(dst) = depth(src) + 1`,
2. no topological-defect interpretation is allowed inside canonical mass runs,
3. any variable path-length lane is a non-canonical defect probe and must be separately labeled.

Mass claims under this RFC are invalid if produced in a defect lane.

## 4. Normative Observables

All observables are tick-indexed and replay-deterministic.

1. `rho_non_e000(x,t)`  
   `sum_{k=1..7} abs2(psi_k(x,t))`

2. `X_t` (motif centroid)  
   `sum_x x * rho_non_e000(x,t) / sum_x rho_non_e000(x,t)`  
   For 3D, apply component-wise.

3. `Y_t` (transport yield)  
   `norm(X_{t+1} - X_t)` or a preregistered directional component.

4. `V_t` (vacuum-coupling drag)  
   `E_t = abs2(e000)/(abs2(e000)+sum_{k=1..7} abs2(psi_k))`  
   `V_t := E_t` at the tracked motif node/worldline sample.

5. `R_t` (rephasing load)  
   operationally fixed as one of:
   - (A) coherence-repair form: `R_t := max(0, C_ref - C_t)`, or
   - (B) phase-increment form: per-tick motif phase realignment work.

The chosen `R_t` form must be preregistered before measurement.

6. `m_eff_window`  
   ratio computed on a fixed window `[t0, t1]`:
   `m_eff_window = mean(R_t + lambda*V_t)/mean(Y_t)`.

## 5. Required Preregistration Fields

Every mass run must lock:

1. kernel profile and projector id,
2. motif ids and initialization microstates,
3. impulse protocol (if any),
4. spatial observable definition (`centroid`, `front`, or both),
5. `R_t` form and `lambda`,
6. window policy (`warmup`, `measure`, `tail`),
7. acceptance/falsification thresholds.

No per-motif retuning is allowed after preregistration.

## 6. Falsification Contract

The model is falsified (for the tested lane) if any preregistered claim fails:

1. monotonicity failure: larger predicted drag does not reduce measured transport yield,
2. acceleration failure: under equal impulse, higher `m_eff` motif does not show lower acceleration,
3. robustness failure: ordering flips under minor topology/seed perturbations beyond declared tolerance,
4. replay failure: rerun changes metric ordering with same replay hash inputs.

## 7. Minimal Benchmark Battery

Mass RFC closure requires all three:

1. Free propagation lane  
   single motif, no external perturber, verify stable `m_eff_window` estimate.

2. Equal impulse lane  
   electron/muon/tau motifs under identical impulse protocol.

3. Interaction lane  
   two-motif approach test where transport slowdown is decomposed into `R_t` and `V_t`.

At least one lane must be 3D for any claim about realistic transport.

## 8. Lean Formalization Scope

Required theorem targets:

1. layered-time invariant: no skipped-causal-tick interpretation in canonical lane,
2. metric well-definedness: denominator positivity conditions for `m_eff_window`,
3. replay-id determinism for all mass observables under fixed event ordering.

Lean does not need to prove numeric SM masses in this RFC.

## 9. Artifact Contract (proposed ids)

1. script: `cog_v2/calc/build_mass_rephasing_latency_contract_v1.py`
2. tests: `cog_v2/calc/test_mass_rephasing_latency_contract_v1.py`
3. source JSON: `cog_v2/sources/mass_rephasing_latency_contract_v1.json`
4. source markdown: `cog_v2/sources/mass_rephasing_latency_contract_v1.md`

Schema id:

`mass_rephasing_latency_contract_v1`

## 10. Relation to Existing Mass Language

This RFC does not invalidate existing `M_t` and `E_t` observables from RFC-004.
It reuses them in a transport-aware composition:

1. `E_t` directly contributes to `V_t`,
2. `M_t` remains a useful non-e000 occupancy diagnostic,
3. "mass" becomes a latency-to-transport ratio rather than a single occupancy scalar.

## 11. Non-Goals

This RFC does not:

1. claim absolute SM lepton/quark masses are solved,
2. assert gravitational equivalence of `m_eff`,
3. choose a continuum unit calibration anchor,
4. replace THETA/Weinberg/alpha bridge contracts.

## 12. Promotion Criteria

Promotion from draft to active requires:

1. preregistered benchmark battery executed with replay-stable artifacts,
2. all falsification checks reported explicitly,
3. at least one independent skeptic pass on metric leakage/overfitting risk,
4. no post hoc metric or lambda changes on accepted runs.

