# RFC-045: Energy/Mass Observable Unification

Status: Active - Analysis Draft (2026-02-26)
Module:
- `COG.Core.EnergyMass`
Depends on:
- `rfc/RFC-018_Time_as_Graph_Depth_and_Interaction_Clock.md`
- `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
- `rfc/RFC-040_Particle_Motif_and_Interaction_Rule_Contract.md`
- `rfc/RFC-042_D4_D5_Implementation_Closure.md`
- `rfc/RFC-034_Electron_Mass_Mechanism.md`
Related:
- `claims/proton_electron_ratio.yml`
- `calc/mass_drag.py`
- `calc/mass_drag_v2.py`

---

## 1. Executive Summary

Multiple mass/energy proxies are currently used across COG. Some are useful diagnostics, but the project needs one canonical observable stack for claims.

This RFC proposes:
1. A primary mass observable defined as a discrete mass-gap style quantity from long-horizon dynamics.
2. A primary energy observable defined as interaction-work rate over declared clocks.
3. Demotion of recurrence-only and gate-density-only metrics to diagnostic status unless proven equivalent to the primary stack.

---

## 2. Problem Inventory

Current proxies in use:
1. first-recurrence periods
2. gate-density / associator-load counts
3. interaction-clock density (`tau_int` relative to `tau_topo`)
4. path-cost / overhead style formulas

Issues:
1. proxies are not equivalent by default,
2. claims can silently switch observable definition,
3. result comparisons become non-falsifiable.

---

## 3. Literature Synthesis

## 3.1 Mass in field theory and lattice settings

In standard QFT/lattice practice, mass is tied to dynamical spectrum, not a single local counter:
1. Pole/spectral definitions link mass to propagator structure.
2. On Euclidean lattices, masses are extracted from exponential decay of two-point correlators (effective mass methods).
3. The physically robust object is a gap/rate derived from long-horizon behavior.

Inference for COG:
1. A primary mass observable should be a long-horizon dynamical invariant, not a single-step local statistic.

## 3.2 Discrete causal frameworks

Causal-set and related order-first models support:
1. time from causal order/depth,
2. dynamics from local link structure,
3. event/process observables from histories/traces.

Inference for COG:
1. `tau_topo` and `tau_int` are the right clock backbone.
2. Energy/mass observables should be defined over traces indexed by these clocks.

## 3.3 Deterministic discrete models and effective mass

Discrete deterministic/automaton approaches show mass-like terms can emerge from update structure and transition algebra, but they still require a clear extraction observable.

Inference for COG:
1. Gate/associator statistics are plausible contributors.
2. They should feed into a canonical derived observable, not serve as independent mass definitions.

---

## 4. Proposed Observable Hierarchy

## 4.1 Primary mass observable: discrete mass-gap estimator

Define a motif-level correlator `C(Delta)` over a declared projection profile and deterministic trace family. Let `Delta` be measured in `tau_int` (default) with `tau_topo` reported in parallel.

Primary estimator:
1. `m_gap := - slope( log C(Delta) )` over declared fitting window(s).

This is the COG analog of effective-mass extraction from correlation decay.

Rationale:
1. It uses long-horizon dynamics.
2. It is robust against short-step noise.
3. It can be compared consistently across motifs.

## 4.2 Primary energy observable: interaction-work rate

Define:
1. `E_rate := Delta W / Delta tau_int`

where `W` is a declared interaction-work accumulator derived from locked D3 events and message-action magnitudes.

Reporting requirement:
1. always report paired clock context:
   - `E_rate_int` over `tau_int`
   - `E_rate_topo` over `tau_topo`

## 4.3 Secondary diagnostics

Retain as diagnostics only:
1. recurrence period
2. raw gate density
3. associator event counts
4. path-overhead formulas

They may be promoted only after a proven mapping to primary observables.

---

## 5. Canonical Definitions To Lock

## D1. Clock basis

Recommendation:
1. mass extraction windows indexed primarily by `tau_int`
2. mandatory paired report in `tau_topo`

## D2. Correlator family

Recommendation:
1. lock one canonical correlator definition per projection profile:
   - `minimal` profile for baseline
   - `with_sector` only for color-sensitive studies

## D3. Fitting protocol

Recommendation:
1. predeclare window family and regression method before seeing targets.
2. report robustness across at least two adjacent windows.

## D4. Work accumulator

Recommendation:
1. define `W` from locked D3 energy-exchange events and folded interaction action.
2. prohibit ad hoc per-motif definitions.

## D5. Unit conventions

Recommendation:
1. preserve integer/doubled internal units.
2. define a single external normalization layer for comparison to physical ratios.

---

## 6. Migration Policy

Until full migration:
1. Legacy metrics must be tagged `diagnostic`.
2. Claims using legacy-only metrics cannot exceed `partial` status.

Migration order:
1. map each active claim to primary mass/energy stack,
2. add side-by-side legacy-to-primary comparison table,
3. deprecate unmapped legacy formulas.

---

## 7. Deliverables

## 7.1 Lean

Planned file:
- `CausalGraphTheory/EnergyMass.lean`

Planned items:
1. trace-indexed observable definitions (clock-aware),
2. monotonicity/sanity lemmas for accumulator components,
3. theorem references for claim metadata.

## 7.2 Python

Planned file:
- `calc/energy_mass_unification.py`

Planned tests:
1. deterministic replay stability for primary estimators,
2. window-robustness checks,
3. legacy-to-primary mapping checks.

## 7.3 Governance

1. claim metadata fields:
   - `mass_observable_profile`
   - `energy_observable_profile`
   - `clock_basis`
2. CI lint for missing fields on active mass/energy claims.

---

## 8. Falsification Gates

1. If primary mass estimator is unstable under deterministic replay, reject lock.
2. If small fitting-window shifts cause uncontrolled ranking flips, reject lock.
3. If no transparent mapping exists from active legacy claims to primary stack, keep RFC open.
4. If primary and diagnostic observables systematically disagree without declared mechanism, downgrade affected claims.

---

## 9. Acceptance Criteria

1. Primary mass and energy observables are documented and implemented.
2. At least three active claims are migrated to primary stack reporting.
3. Legacy observables are tagged as `diagnostic` or `deprecated`.
4. A reproducible benchmark report compares old and new observables on the same traces.

---

## 10. Open Questions

1. Which correlator definition is most robust across motif classes?
2. How much of associator-load statistics is independent signal vs redundant proxy?
3. What is the cleanest normalization from internal units to external ratio comparisons?

---

## 11. Sources

Primary references used for this analysis:

1. Wilson and Kogut (1974), *The renormalization group and the epsilon expansion*  
   https://doi.org/10.1016/0370-1573(74)90023-4
2. Johnston (2010), *Quantum Fields on Causal Sets*  
   https://arxiv.org/abs/1010.5514
3. Sorkin (2009), *Scalar field theory on a causal set in histories form*  
   https://arxiv.org/abs/0910.0673
4. Surya (2019), *The causal set approach to quantum gravity*  
   https://arxiv.org/abs/1903.11544
5. D'Ariano et al. (2014), *Dirac quantum cellular automaton*  
   https://arxiv.org/abs/1406.1021
6. Earle (2010), *Feynman checkerboard and lattice amplitudes*  
   https://arxiv.org/abs/1012.1564
7. Elze (2024), *Cellular automaton ontology and Dirac dynamics*  
   https://arxiv.org/abs/2401.08253
8. Finster et al. (2024), *Causal Fermion Systems and Octonions*  
   https://arxiv.org/abs/2403.00360

