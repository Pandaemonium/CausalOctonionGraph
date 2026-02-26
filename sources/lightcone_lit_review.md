# Light Cones in Discrete Causal Models: Literature Review for COG

**Date:** 2026-02-26  
**Scope anchor:** `ORIENTATION.md`, `rfc/RFC-018_Time_as_Graph_Depth_and_Interaction_Clock.md`, `rfc/RFC-020_Kernel_Representation_Reconciliation.md`  
**Focus question:** How should "light cone" be defined and used in a deterministic CxO causal-graph kernel?

---

## 1. Executive Summary

This review supports four high-confidence design decisions:

1. Causal order should define admissible influence (light-cone locality), not coordinate time.
2. In a discrete graph kernel, local update inputs should come only from the incoming causal past.
3. Finite-speed propagation should be treated as either strict (hard cone) or effective (cone with exponentially suppressed tails), and the choice must be explicit.
4. Event-driven execution is valid only if equivalent to fixed-step replay at interaction boundaries.

And it rejects two over-strong claims:

1. Literature does not force one unique algebraic axis (such as `e7`) to be "the" light-cone direction.
2. Literature does not justify assuming all outside-cone effects are exactly zero in every discrete model; some frameworks imply effective tails.

---

## 2. Literature Findings

## 2.1 Causal structure as primary

- Hawking-King-McCarthy and later Malament-type results establish that causal order strongly constrains spacetime geometry (up to conformal factor under standard conditions).
- Causal set theory uses locally finite posets as fundamental structure and treats order intervals as discrete analogues of causal diamonds.

COG implication: define light cones from graph order first, then derive observables.

## 2.2 Discrete causal growth and locality

- Classical sequential growth models build causal sets by order-respecting stochastic growth.
- Causal graph dynamics (classical and quantum) formalize bounded information speed on evolving graphs and prove locality-preserving composition properties.

COG implication: per-tick candidate interactions should be computed from the incoming cone only.

## 2.3 Effective light cones in many-body quantum systems

- Lieb-Robinson theory gives finite-velocity bounds where influence outside the cone is exponentially suppressed.
- Modern tightened bounds and experiments support this effective-cone picture.

COG implication: if kernel updates use short-range rules, "outside-cone leakage" should be tracked as a measurable quantity; do not assume it is always exactly zero unless proven.

## 2.4 Propagators on causal sets

- Causal-set propagator constructions recover retarded/Feynman behavior in suitable regimes and define time-ordering from linear extensions.

COG implication: light-cone semantics should distinguish strict causal precedence from implementation-level ordering choices.

## 2.5 CFS and octonion context

- CFS-octonion work supports splitting responsibilities: octonionic algebra for vacuum/symmetry structure and causal dynamics for spacetime evolution.

COG implication: keep light-cone definitions in causal-graph semantics, not in an ad hoc basis-label layer.

---

## 3. Adopt / Reject Matrix

- Adopt: light cone = transitive causal past/future in the graph order.
- Adopt: update inputs = incoming cone boundary messages at the current tick.
- Adopt: finite-speed invariant as a hard kernel rule or an explicit effective bound.
- Adopt: cone observability metrics (`k`, shell depth, tail mass, replay equivalence).
- Reject: "light cone is equivalent to one specific octonion basis axis" as a literature theorem.
- Reject: "outside-cone effects are always identically zero" without proof in the chosen kernel.

---

## 4. Immediate COG Actions Suggested by Literature

1. Add a formal light-cone module that computes `PastCone`, `FutureCone`, and message boundary sets deterministically.
2. Add a hard no-leak test: updates must be invariant under perturbations outside causal past.
3. Add an effective-cone diagnostic: quantify any measurable outside-cone influence if nonlocal operators are introduced.
4. Keep `tau_topo` and `tau_int` separate (already in RFC-018), with cone-locality checks applied to both clocks.

---

## 5. References

1. S. W. Hawking, A. R. King, P. J. McCarthy (1976), *A new topology for curved space-time which incorporates the causal, differential, and conformal structures*. J. Math. Phys. 17, 174-181. https://doi.org/10.1063/1.522874  
2. L. Bombelli, J. Lee, D. Meyer, R. D. Sorkin (1987), *Space-Time as a Causal Set*. Phys. Rev. Lett. 59, 521. https://doi.org/10.1103/PhysRevLett.59.521  
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

