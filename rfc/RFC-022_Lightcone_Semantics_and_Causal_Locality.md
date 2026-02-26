# RFC-022: Lightcone Semantics and Causal Locality

**Status:** Active - Literature-Reconciled Draft (2026-02-26)  
**Module:** `COG.Core.Lightcone`, `COG.Core.CausalLocality`  
**Depends on:** `rfc/RFC-002_Deterministic_Tick_Ordering.md`, `rfc/RFC-018_Time_as_Graph_Depth_and_Interaction_Clock.md`, `rfc/RFC-020_Kernel_Representation_Reconciliation.md`  
**Literature basis:** `sources/lightcone_lit_review.md`

---

## 1. Executive Summary

This RFC formalizes how light cones enter COG:

1. Light cones are graph-order objects (causal past/future), not coordinate objects.
2. Candidate update inputs at `(t, v)` are exactly the incoming boundary messages from the causal past of `v`.
3. Updates must satisfy causal locality: perturbations outside the past cone of `v` cannot affect `v` at that tick.
4. COG must explicitly distinguish strict-cone and effective-cone regimes.

This RFC keeps COG consistent with existing deterministic scheduling and Kernel v2 state semantics while making locality a first-class, testable contract.

---

## 2. Motivation

Current RFCs define deterministic ordering (RFC-002), two clocks (RFC-018), and CxO-native state representation (RFC-020), but light-cone semantics are not yet a locked kernel contract.

Without a formal light-cone contract:

- locality assumptions remain implicit,
- debugging cannot separate cone-local failures from scheduler failures,
- event-driven optimizations risk violating causal equivalence.

---

## 3. Literature-Constrained Claims

## 3.1 Claims adopted

1. Causal order is sufficient to define admissible influence structure in order-first frameworks.
2. Discrete causal dynamics can be constrained by bounded propagation speed on graphs.
3. Effective light cones with suppressed outside-cone influence are physically meaningful in local many-body systems.

## 3.2 Claims not adopted

1. Literature does not prove that one specific octonion basis axis uniquely defines light cones.
2. Literature does not justify assuming exact zero outside-cone influence in every discrete kernel without proof.

These remain model hypotheses to be tested, not imported theorems.

---

## 4. Formal Definitions

Let `G_t = (V_t, E_t)` be the directed acyclic causal graph at global tick `t`.

For node `v in V_t`:

- `Past_t(v) := {u | u ->* v}` (transitive causal past)
- `Future_t(v) := {w | v ->* w}` (transitive causal future)

Define `IncomingBoundary_t(v)` as the multiset of active incoming messages delivered to `v` at tick `t` from edges in `E_t`.

Define multiplicity:

`k_t(v) := |IncomingBoundary_t(v)|`

Local state update:

`psi_{t+1}(v) = U(psi_t(v), IncomingBoundary_t(v), EvalPlan_v)`

where `U` is deterministic and `EvalPlan_v` uses immutable tie-break and parenthesization rules from RFC-002.

---

## 5. Architecture Decisions (Locked)

### D1. Cone-local candidate set

At tick `t`, update inputs for node `v` are exactly `IncomingBoundary_t(v)`. No nonlocal heuristic injection is allowed.

### D2. Outside-cone non-influence

For fixed `EvalPlan` and initial microstate, if two runs differ only on nodes outside `Past_t(v)`, then `psi_{t+1}(v)` must be identical.

### D3. Strict vs effective regime must be explicit

Each kernel/operator pair must declare one regime:

1. `strict_cone`: outside-cone effect exactly zero by construction, or
2. `effective_cone`: outside-cone effect bounded by a declared tail estimator.

### D4. Clock compatibility

This RFC does not replace RFC-018:

- `tau_topo` tracks causal ordering progress.
- `tau_int` tracks energy-exchange process count.

Cone-locality constraints apply to both clocks.

### D5. Event-driven equivalence

Skipping null steps is allowed only if the resulting trajectory matches fixed-step replay at all interaction boundaries.

---

## 6. Required Invariants

1. `ConeDeterminism`: `Past_t(v)` and `IncomingBoundary_t(v)` are pure functions of kernel state and immutable plan.
2. `NoConeLeak`: local update output at `(t, v)` is invariant under any outside-`Past_t(v)` perturbation.
3. `FinitePropagation`: causal influence per tick obeys declared locality radius.
4. `ReplayInvariance`: same initial microstate and plan produce bit-identical traces.
5. `SchedulerEquivalence`: fixed-step and event-driven traces agree at interaction boundaries.

---

## 7. Instrumentation Contract

Each run must log:

1. `k_t(v)` distribution and `P(k > 4)`.
2. Cone width/depth metrics for updated nodes.
3. `no_cone_leak` test outcomes.
4. If `effective_cone`: measured tail magnitude outside cone.
5. Replay hash and fixed-vs-event equivalence verdict.

---

## 8. Lean and Python Targets

## 8.1 Lean targets

Add module(s):

- `CausalGraphTheory/Lightcone.lean`
- optional: `CausalGraphTheory/CausalLocality.lean`

Definitions:

- `pastCone : KernelState -> NodeId -> Finset NodeId`
- `incomingBoundary : KernelState -> NodeId -> Multiset Message`
- `noConeLeak : KernelState -> NodeId -> Prop`

Theorem targets:

1. `incomingBoundary_deterministic`
2. `outside_pastCone_perturbation_invariant`
3. `fixed_event_equiv_at_boundaries` (under RFC-018 assumptions)

## 8.2 Python targets

Add/update:

- cone-extraction utility for each tick/node
- deterministic outside-cone perturbation test harness
- fixed-step vs event-driven equivalence harness
- dashboard metrics for cone occupancy and leak flags

Required tests:

1. perturbing outside past cone does not change local update result
2. perturbing inside past cone can change local update result (sanity check)
3. fixed-step/event-driven equivalence
4. determinism replay hash

---

## 9. Falsification and Decision Tests

1. **Leak test:** if outside-cone perturbations affect local update under `strict_cone`, kernel is invalid.
2. **Tail test:** if `effective_cone` tails are large enough to alter priority observables, strict-cone approximation is invalid.
3. **Clock test:** if cone-locality holds for `tau_topo` but fails for `tau_int`, energy predicate implementation is inconsistent.
4. **Scheduler test:** if event-driven diverges from fixed-step at interaction boundaries, event mode is not admissible.

---

## 10. Open Questions

1. What is the minimal locality radius for each operator family in CxO kernel dynamics?
2. Does measured cone-tail behavior stay negligible for target observables under high-depth runs?
3. Which observables are most sensitive to rare high-`k` cone intersections?
4. How should cone-locality be represented in claims metadata (`strict_cone` vs `effective_cone`)?

---

## 11. Governance Impact

1. Any claim that assumes locality must specify whether it depends on `strict_cone` or `effective_cone`.
2. Any optimization that truncates cone inputs must report an empirical error bound.
3. No claim may treat nonlocal behavior as "debug noise"; it must be classified as model failure, approximation, or explicit operator design.

---

## 12. References

1. S. W. Hawking, A. R. King, P. J. McCarthy (1976), *A new topology for curved space-time which incorporates the causal, differential, and conformal structures*. https://doi.org/10.1063/1.522874  
2. L. Bombelli, J. Lee, D. Meyer, R. D. Sorkin (1987), *Space-Time as a Causal Set*. https://doi.org/10.1103/PhysRevLett.59.521  
3. D. P. Rideout, R. D. Sorkin (1999), *A Classical Sequential Growth Dynamics for Causal Sets*. https://arxiv.org/abs/gr-qc/9904062  
4. S. Surya (2019), *The causal set approach to quantum gravity*. https://arxiv.org/abs/1903.11544  
5. P. Arrighi, G. Dowek (2012), *Causal graph dynamics*. https://arxiv.org/abs/1202.1098  
6. P. Arrighi, S. Martiel (2016), *Quantum Causal Graph Dynamics*. https://arxiv.org/abs/1607.06700  
7. E. H. Lieb, D. W. Robinson (1972), *The finite group velocity of quantum spin systems*. https://doi.org/10.1007/BF01645779  
8. Z. Wang, K. R. A. Hazzard (2019), *Tightening the Lieb-Robinson Bound in Locally-Interacting Systems*. https://arxiv.org/abs/1908.03997  
9. M. Cheneau et al. (2011), *Light-cone-like spreading of correlations in a quantum many-body system*. https://arxiv.org/abs/1111.0776  
10. S. Johnston (2008), *Particle propagators on discrete spacetime*. https://arxiv.org/abs/0806.3083  
11. N. X, F. Dowker, S. Surya (2017), *Scalar Field Green Functions on Causal Sets*. https://arxiv.org/abs/1701.07212  
12. F. Finster et al. (2024), *Causal Fermion Systems and Octonions*. https://arxiv.org/abs/2403.00360  

