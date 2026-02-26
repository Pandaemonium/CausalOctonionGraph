# RFC-033: Double-Slit Interference and Path Resolution in COG

**Status:** Active - Exploratory Draft (2026-02-26)  
**Module:** `COG.Theory.Interference`  
**Dependencies:** `rfc/RFC-020_Kernel_Representation_Reconciliation.md`, `rfc/RFC-022_Lightcone_Semantics_and_Causal_Locality.md`, `rfc/RFC-023_Discrete_Phase_Clocks_and_Relative_Phase_Interactions.md`, `rfc/RFC-028_Canonical_Update_Rule_Closure.md`, `rfc/RFC-031_Decoherence_as_Forced_Interaction_Resolution.md`

---

## 1. Executive Summary

This RFC defines how COG interprets the double-slit experiment without adding non-deterministic collapse rules.

1. Each shot is fully deterministic at the microstate level (initial state plus deterministic update order).
2. The two-slit geometry creates two causal input families at screen nodes.
3. Interference is the ensemble-level pattern produced by deterministic non-associative updates plus projection to observables.
4. Which-way instrumentation increases local interaction load near slits and forces early path resolution, suppressing interference.
5. No observer magic is required; "collapse" is forced local resolution under dense boundary input (RFC-031).

---

## 2. Motivation

Double-slit behavior is a core benchmark for any candidate microphysical model.  
COG already has key pieces:

1. C x O state container (RFC-020),
2. cone-local deterministic updates (RFC-022),
3. discrete internal phase clocks (RFC-023),
4. deterministic update skeleton with temporal commit and ordered interaction fold (RFC-028, partial lock),
5. decoherence framing as forced interaction resolution (RFC-031).

This RFC ties those pieces into one experiment-level interpretation.

---

## 3. COG Mapping of the Double-Slit Setup

Define a finite DAG experiment motif:

1. source region `S`,
2. slit regions `A` and `B`,
3. detector/screen region `D`,
4. optional which-way detector nodes `W_A`, `W_B`.

For detector node `v in D` at tick `t`, update remains kernel-local:

`psi_{t+1}(v) = U( T(psi_t(v)), O_t(v), H_t(v) )`

with input multiset `O_t(v)` partitioned into path families:

`O_t(v) = O_t^A(v) union O_t^B(v) union O_t^env(v)`

Interpretation:

1. `O_t^A(v)` are boundary messages whose causal ancestry passes slit A.
2. `O_t^B(v)` are boundary messages whose causal ancestry passes slit B.
3. `O_t^env(v)` is detector/environment coupling.

Interference in COG means detector outcomes depend on joint ordered contribution of both path families, not a classical sum of independent one-slit counts.

---

## 4. What "Interference" Means in This Model

COG does not require a continuum pilot wave in physical space.  
Instead, interference is a structured consequence of:

1. non-associative composition order (fixed by initial deterministic plan),
2. relative phase structure (RFC-023),
3. projection from full microstate to observable readout (D5, currently open in RFC-028).

Operationally:

1. Single-slit runs define baselines `I_A(x)` and `I_B(x)` across detector bins `x`.
2. Two-slit run gives `I_AB(x)`.
3. COG interference signature is:
   - constructive bins where `I_AB(x) > I_A(x) + I_B(x)`,
   - suppressive bins where `I_AB(x) < I_A(x) + I_B(x)`.

This is a data-level criterion and does not assume Born-rule amplitudes at kernel level.

---

## 5. Which-Way Measurement and Decoherence

In COG, "which-way" instrumentation is additional local coupling near slits:

1. extra incoming boundary messages at slit-adjacent nodes,
2. increased `tau_int` increments through `isEnergyExchange` logic,
3. earlier forced resolution of path-sensitive pending structure (RFC-031 framing).

Prediction:

1. As slit-local interaction density rises, fringe visibility `V` monotonically drops.
2. In the strong which-way regime, `I_AB(x)` approaches `I_A(x) + I_B(x)` (fringes suppressed).

No consciousness term appears anywhere in the mechanism.

---

## 6. Determinism vs Apparent Randomness

COG stance:

1. Each shot outcome is fixed by full microstate and deterministic update order.
2. Apparent randomness comes from ignorance of full environment/meter microstate and from projection to limited observables.

This is consistent with the project-wide superdetermined interpretation, but it remains an interpretation-level claim until D5 (`Pi_obs`) is locked and tested against benchmark statistics.

---

## 7. Delayed-Choice and No Retrocausality

COG interpretation:

1. Future measurement settings change future interaction topology and boundary inputs.
2. They do not rewrite already-resolved past nodes in a DAG.

So delayed-choice effects are correlation-structure effects under one deterministic causal graph, not retrocausal edits.

---

## 8. Falsifiable Program

### 8.1 Python target

Add `calc/double_slit_cog_sim.py` with:

1. one-slit baseline runs (A only, B only),
2. two-slit run (A and B),
3. which-way coupling sweep (interaction density near slits),
4. outputs:
   - detector histogram,
   - visibility metric `V = (I_max - I_min) / (I_max + I_min)`,
   - interference-strength metric `S_int = L1(I_AB, I_A + I_B)` on normalized profiles,
   - monotonicity check of interference suppression under increasing which-way coupling
     (e.g., `S_int` non-increasing).

### 8.2 Lean target (scaffold first)

Add `CausalGraphTheory/Interference.lean`:

1. define finite experiment topology (source, two path families, detector bins),
2. define one-slit and two-slit observable count functions over a finite replay set,
3. prove topology-level no-retrocausality invariant:
   settings chosen after depth `d` cannot alter resolved states at depth `< d`.

Do not claim quantitative quantum-fit theorems before D5 is locked.

---

## 9. Current Blockers

1. RFC-028 D4 (spawn semantics) remains open for full dynamic graph growth behavior.
2. RFC-028 D5 (`Pi_obs`) remains open; this blocks a fully formal mapping from microstate to detector click probabilities.
3. Pending-state kernel type from RFC-031 is not yet formalized.

Therefore this RFC is currently a test program plus interpretation contract, not a closed derivation.

---

## 10. Compatibility Requirements

| Check | Status | Blocking? |
|-------|--------|-----------|
| Uses C x O kernel state | Yes | No |
| Uses cone-local deterministic update contract | Yes (RFC-022/028 framing) | No |
| Requires nonlocal signaling | No | No |
| Requires observer-dependent postulate | No | No |
| Requires D5 `Pi_obs` for quantitative claims | Not yet | Yes (for full claim closure) |
| Requires pending-state kernel formalization | Not yet | Yes (for RFC-031 style collapse formalization) |

---

## 11. Minimum Viable Path

1. Implement Python simulation and produce one reproducible fringe/decoherence report.
2. Lock minimal D5 projection contract for detector bins.
3. Add Lean topology/no-retrocausality scaffold.
4. Only then attempt quantitative matching claims (fringe envelope, parameter fits).

---

## 12. References (background physics)

1. R. P. Feynman, R. Leighton, M. Sands, *The Feynman Lectures on Physics, Vol. 3* (double-slit as central QM example).
2. W. H. Zurek, "Decoherence, einselection, and the quantum origins of the classical", Rev. Mod. Phys. 75, 715 (2003).
3. C. Joos et al., *Decoherence and the Appearance of a Classical World in Quantum Theory* (Springer).
