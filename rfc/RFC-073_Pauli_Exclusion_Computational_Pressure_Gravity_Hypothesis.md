# RFC-073: Pauli Exclusion as Computational Pressure for Mass and Gravity-like Curvature

Status: Active Draft - Hypothesis RFC (2026-02-27)
Module:
- `COG.Gravity.PauliPressure`
- `COG.Mass.ExclusionLoad`
Depends on:
- `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
- `rfc/RFC-035_Distance_as_Next_Interaction_Node_Gap.md`
- `rfc/RFC-063_XOR_Octonion_Gate_and_Signed_Handed_Dynamics.md`
- `rfc/RFC-067_Objective_Time_as_Graph_Depth.md`
- `rfc/RFC-069_Canonical_Simulation_Artifact_Contract.md`
- `rfc/RFC-070_Left_Handed_vs_Right_Handed_Interaction_Contract.md`
- `rfc/RFC-030_Gravity_as_Emergent_Graph_Density.md`
- `world_code/Python_code/minimal_world_kernel.py`
- `world_code/Lean_code/MinimalWorldKernel.lean`

---

## 1. Executive Summary

This RFC formalizes the hypothesis that Pauli exclusion pressure is a load-bearing contributor to:
1. effective mass (computational drag),
2. gravity-like curvature (geodesic deflection in directed graph metrics).

Core idea:
1. exclusion constraints reject some local update candidates,
2. those rejections create extra local computation load,
3. extra load increases local slowdown field,
4. probe trajectories in a weighted directed graph bend toward high-load regions.

This RFC does not claim closure. It defines a falsifiable program.

---

## 2. Problem Statement

Current mass and gravity framing in COG uses:
1. mass as update drag / tick cost,
2. gravity-like behavior as emergent topological/metric distortion.

What is missing:
1. a concrete mechanistic source for part of that drag,
2. a direct test for whether exclusion constraints drive measurable curvature-like effects.

This RFC proposes Pauli exclusion pressure as that source and defines tests.

---

## 3. Scope and Non-Scope

In scope:
1. operational observables for exclusion pressure,
2. deterministic simulation protocol on full predetermined lightcones,
3. falsification gates linking exclusion pressure to slowdown and deflection.

Out of scope:
1. replacing the canonical kernel update rule,
2. claiming GR-equivalence,
3. adding continuum manifold assumptions.

---

## 4. Hypothesis Statement

Hypothesis H-PE:
1. local exclusion conflict density contributes positively to local computational slowdown,
2. slowdown gradients contribute to directed-geodesic deflection of probes,
3. therefore Pauli exclusion pressure contributes to mass and gravity-like effects.

Equivalent chain:
1. higher exclusion conflict -> higher drag (`tau_int` load),
2. higher drag -> larger local slowdown field,
3. larger slowdown gradients -> stronger path bending / edge-gap drift.

---

## 5. Canonical Observables

Define per node `v` at tick `t`:

1. Exclusion conflict count:
   - `E(v,t)`: number of candidate local updates rejected by exclusion constraints.

2. Exclusion pressure field:
   - `P(v,t) := rolling_mean_k(E(v,t))` over a declared finite horizon `k`.

3. Slowdown field:
   - `S(v,t) := tau_int(v,t) / tau_topo(v,t)` (or approved finite-depth proxy).

4. Probe deflection observable:
   - `D_probe(t)`: change in directed shortest-path behavior for a probe trajectory
     relative to matched control.

5. Distance-gap drift (RFC-035 compatible):
   - `Delta_gap(t) := edge_gap_future(t) - edge_gap_past(t)` for declared motif pairs.

Control subtraction rule:
1. always compare treated run vs matched control with same lightcone topology,
2. only one toggled factor per experiment.

---

## 6. Experimental Protocol (Deterministic, Full-Lightcone)

All runs must satisfy:
1. full predetermined lightcone microstate input,
2. deterministic update rule only,
3. canonical artifact contract (RFC-069),
4. no stochastic sampling inside kernel dynamics.

Recommended first experiment family:
1. choose one probe motif and one source motif in same cone topology,
2. run baseline with exclusion rule active,
3. run matched counterfactual with exclusion check disabled in analysis harness only,
4. keep all else fixed (input, ordering, hand schedule, steps),
5. compare `P`, `S`, `D_probe`, and `Delta_gap`.

---

## 7. Falsification Gates

Gate G1: Exclusion-load coupling
1. If increasing exclusion conflict does not increase slowdown field in matched runs,
   H-PE is falsified for that regime.

Gate G2: Deflection linkage
1. If slowdown gradients change but probe deflection/distance-gap does not, the
   gravity-like part of H-PE is falsified for that regime.

Gate G3: Control subtraction integrity
1. If effect size vanishes or reverses under corrected control subtraction,
   claim is demoted.

Gate G4: Replay determinism
1. Same input + same rule + same schedule must reproduce identical output hashes.

Gate G5: Robustness across motifs
1. If effect only appears in one narrowly tuned motif setup, classify as weak support,
   not closure.

---

## 8. Implementation Targets

## 8.1 Python harness (new)

Suggested file:
1. `calc/pauli_pressure_gravity.py`

Required outputs:
1. per-node `E`, `P`, `S` traces,
2. probe path and directed-metric summaries,
3. control-subtracted effect report,
4. deterministic replay hash.

Suggested tests:
1. `calc/test_pauli_pressure_gravity.py`
2. deterministic replay,
3. gate checks for G1-G3 on toy fixtures.

## 8.2 Lean stubs (new)

Suggested file:
1. `CausalGraphTheory/PauliPressure.lean`

Initial theorems to target:
1. well-definedness of exclusion conflict counting over finite cones,
2. monotone property of `P` under added exclusion rejections (if assumptions hold),
3. deterministic replay invariance of declared observables.

---

## 9. Relationship to Existing Gravity RFC

This RFC specializes and operationalizes `RFC-030` by proposing a concrete source term:
1. `RFC-030` says curvature-like behavior emerges from computational density,
2. `RFC-073` says exclusion pressure is one measurable contributor to that density.

If `RFC-073` fails gates:
1. `RFC-030` may still hold with different source terms.

If `RFC-073` passes gates:
1. it provides a mechanistic bridge from exclusion constraints to gravity-like behavior.

---

## 10. Risks and Confounders

1. Electromagnetic or color effects may mimic deflection unless controls are strict.
2. Metric choice for directed DAG paths can inject artifacts.
3. Small-cone finite-size effects may overstate or hide true trend.
4. Observable leakage (analysis-layer assumptions) can produce false positives.

Mitigations:
1. strict control subtraction,
2. multiple metric variants with preregistered ranking,
3. scale sweep over cone horizons,
4. skeptic claim-by-claim review with model-anchor citations.

---

## 11. Promotion Policy for Related Claims

No claim may be promoted to `proved` on this hypothesis unless:
1. all falsification gates pass on preregistered protocols,
2. artifacts satisfy RFC-069,
3. skeptic report is `PASS` or `PASS_WITH_LIMITS` with explicit limits,
4. independent rerun reproduces the effect.

Until then, status remains `partial` or `hypothesis`.

---

## 12. Immediate Next Actions

1. Implement `calc/pauli_pressure_gravity.py` with full-lightcone input only.
2. Define one canonical toy experiment and one medium-cone experiment.
3. Add replay and control-subtraction tests.
4. Produce first artifact bundle under the constant-factory contract.
