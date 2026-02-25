# Time as Graph Depth: Literature Review for COG

**Date:** 2026-02-25  
**Scope anchor:** `ORIENTATION.md` and current COG RFCs on causal ticking, vacuum dynamics, and deterministic updates  
**Focus question:** Can we formalize "time = graph depth" with sparse, lightcone-bounded interactions where energy exchange is the event that advances physical time?

---

## 1. Executive Summary

This review supports a strong core claim and identifies two open modeling choices:

1. **Well supported:** In causal-order-first frameworks, time can be reconstructed from order structure (especially chain depth / longest chain), without assuming continuum time first.
2. **Well supported:** Candidate interactions should be local to causal neighborhoods (lightcone-like bounds), with finite information propagation speed.
3. **Well supported (algorithmic):** If most ticks are null events, event-driven simulation is the right computational pattern.
4. **Open choice (physics):** "Only energy exchange advances physical time" is plausible but not yet a standard theorem in the cited literature.
5. **Open choice (quantitative):** "k > 4 incoming messages is negligible" should be treated as a testable sparsity hypothesis, not a locked axiom.

Bottom line: your framing is technically coherent and aligns with causal-set and causal-graph literature, but it should be encoded as a **two-clock model** (topological depth clock + interaction/energy clock) until the energy-time link is derived.

---

## 2. Hypothesis Decomposed

Your idea can be split into four claims:

- **H1 (Depth-Time):** Time is graph depth (or longest causal chain depth).
- **H2 (Lightcone Candidates):** At each step, candidate interactions are exactly the incoming causal-lightcone messages.
- **H3 (Energy Clock):** Physical time advances when energy exchange occurs.
- **H4 (Low Multiplicity):** Most steps have k=0 incoming messages; k in {1,2,3,4} dominates, and higher k has tiny effect.

Current evidence status:

- **H1:** Strong support in causal set literature.
- **H2:** Strong support in causal graph dynamics / finite-speed causality literature.
- **H3:** Partial support; consistent with several discrete-QFT constructions but still a model decision in COG.
- **H4:** Computationally plausible; needs project-specific measurement.

---

## 3. Relevant Literature

### 3.1 Causal order as primary, time from depth/order

1. **Bombelli, Lee, Meyer, Sorkin (1987)** introduced the causal set program: spacetime as a locally finite partial order, with geometry emerging from order + counting.
2. **Surya (2019, Living Review)** summarizes the standard causal-set reconstruction rule where timelike distance is estimated by longest-chain length between causally related events (following Myrheim and later Brightwell-Gregory results).
3. **Rideout and Sorkin (1999)** define sequential growth dynamics for causal sets under covariance/causality constraints, giving a clean discrete event-generation picture.
4. **Johnston (2010)** shows QFT constructions on causal sets where time-ordering can be defined from linear extensions of the causal order.

Relevance to COG: these works directly support a model where "clock" is derived from causal structure rather than imposed as an external continuum.

### 3.2 Lightcone-bounded interactions and finite propagation

1. **Arrighi and Dowek (2012), Causal Graph Dynamics:** extends cellular automata to time-varying graphs with bounded-speed information flow defined on graph distance.
2. **Arrighi and Martiel (2016), Quantum Causal Graph Dynamics:** causal unitary evolution on dynamic graphs decomposes into finite-depth local circuits.
3. **Lieb and Robinson (1972)** and modern refinements: local quantum systems admit an effective lightcone with finite propagation speed (model-dependent velocity).
4. **Finster (2018, CFS):** discusses finite propagation behavior at macroscopic scales in causal fermion systems.

Relevance to COG: these results support restricting candidate interactions each tick to local causal neighborhoods and treating far-outside-cone effects as suppressed.

### 3.3 Sparse-event dynamics and null-tick handling

1. **Bortz-Kalos-Lebowitz (1975)** introduced rejection-free kinetic Monte Carlo ideas that skip most null proposals in low-activity regimes.
2. **Gillespie (1977)** exact stochastic simulation algorithm (SSA) similarly jumps from event to event instead of fixed small dt stepping.

Relevance to COG: your statement "usually no update, sometimes 1-4 interactions" maps to an event-driven scheduler. Even for deterministic rules, this avoids wasting compute on empty ticks and makes logs easier to interpret.

### 3.4 CFS-Octonion bridge context

**Finster et al. (2024), "Causal Fermion Systems and Octonions"** explicitly frames octonionic vacuum symmetry and CFS dynamical/spacetime machinery as complementary.

Relevance to COG: this supports a research direction where algebraic sector structure (octonionic) and causal-dynamical graph evolution are jointly modeled rather than treated as disconnected layers.

---

## 4. What This Implies for Your Model

### 4.1 Recommended formal split: two clocks

Do not collapse everything into one scalar "time" yet. Use:

- **Topological clock** `tau_topo(n)`:
  - `tau_topo(n) = 0` for roots
  - `tau_topo(n) = 1 + max_{p in Parents(n)} tau_topo(p)` otherwise
- **Interaction clock** `tau_int`:
  - increments only when an update includes an energy-exchange event under your operator semantics.

Interpretation:

- `tau_topo` is causal depth (ordering).
- `tau_int` is physical process count tied to energy transfer.

This keeps H1 locked while H3 remains testable.

### 4.2 Tick/update rule compatible with your hypothesis

At candidate node/event `v`:

1. Compute incoming causal-lightcone message multiset `M(v)`.
2. Let `k = |M(v)|`.
3. If `k = 0`, no state change (null topological step).
4. If `k > 0`, apply deterministic update rule with canonical parenthesization/tie-breaks from initial microstate conventions.
5. Increment `tau_int` only if the update qualifies as energy exchange.

### 4.3 Treat k > 4 as a measurable tail, not an axiom

Your "higher than four is minuscule" claim is plausible in sparse local graphs, but should be validated by instrumentation:

- empirical distribution `P(k)`
- tail mass `P(k > 4)`
- sensitivity of observables to truncating interactions at `k_max = 4`

If observables are stable under this truncation, you can promote it to an engineering approximation in an RFC.

---

## 5. Gaps and Risks

1. **Energy-time identification gap:** literature supports causal-order clocks strongly; "energy exchange is what advances physical time" is still model-specific and must be justified internally.
2. **Depth ambiguity risk:** "graph depth" can mean local rank, longest chain between endpoints, or global layer index. Lock one formal definition in the kernel contract.
3. **Null-step semantics:** if many ticks are null, fixed-step logs can look active while physics is idle. Use event-centric telemetry.
4. **Tail-event risk:** rare high-k events can dominate certain observables even when frequency is small; this must be measured, not assumed away.

---

## 6. Immediate Next Steps for COG

1. Add an RFC subsection that formalizes `tau_topo` and `tau_int` as separate observables.
2. Instrument simulation logs with `k = incoming_lightcone_count` per attempted update and publish `P(k)`.
3. Add an event-driven execution mode that skips null ticks but preserves deterministic replay.
4. Add invariants:
   - no exogenous information creation,
   - deterministic tie-break ordering,
   - equivalence check between fixed-step and event-driven outcomes.

---

## 7. References

1. Bombelli, L., Lee, J., Meyer, D., Sorkin, R. D. (1987). *Space-Time as a Causal Set*. Phys. Rev. Lett. 59, 521. https://doi.org/10.1103/PhysRevLett.59.521  
2. Rideout, D. P., Sorkin, R. D. (1999). *A Classical Sequential Growth Dynamics for Causal Sets*. arXiv:gr-qc/9904062. https://arxiv.org/abs/gr-qc/9904062  
3. Varadarajan, M., Rideout, D. (2005). *A general solution for classical sequential growth dynamics of Causal Sets*. arXiv:gr-qc/0504066. https://arxiv.org/abs/gr-qc/0504066  
4. Surya, S. (2019). *The causal set approach to quantum gravity*. Living Rev Relativ (review; includes timelike distance via longest chain discussion). https://arxiv.org/abs/1903.11544 and https://doi.org/10.1007/s41114-019-0023-1  
5. Johnston, S. (2009). *Feynman Propagator for a Free Scalar Field on a Causal Set*. arXiv:0909.0944. https://arxiv.org/abs/0909.0944  
6. Johnston, S. (2010). *Quantum Fields on Causal Sets*. arXiv:1010.5514. https://arxiv.org/abs/1010.5514  
7. Arrighi, P., Dowek, G. (2012). *Causal graph dynamics*. arXiv:1202.1098. https://arxiv.org/abs/1202.1098  
8. Arrighi, P., Martiel, S. (2016). *Quantum Causal Graph Dynamics*. arXiv:1607.06700. https://arxiv.org/abs/1607.06700  
9. Lieb, E. H., Robinson, D. W. (1972). *The finite group velocity of quantum spin systems*. Commun. Math. Phys. 28, 251-257. https://doi.org/10.1007/BF01645779  
10. Wang, Z., Hazzard, K. R. A. (2019). *Tightening the Lieb-Robinson Bound in Locally-Interacting Systems*. arXiv:1908.03997. https://arxiv.org/abs/1908.03997  
11. Lamport, L. (1978). *Time, Clocks, and the Ordering of Events in a Distributed System*. Commun. ACM 21(7), 558-565. https://doi.org/10.1145/359545.359563  
12. Bortz, A. B., Kalos, M. H., Lebowitz, J. L. (1975). *A new algorithm for Monte Carlo simulation of Ising spin systems*. J. Comput. Phys. 17(1), 10-18. https://doi.org/10.1016/0021-9991(75)90060-1  
13. Gillespie, D. T. (1977). *Exact stochastic simulation of coupled chemical reactions*. J. Phys. Chem. 81(25), 2340-2361. https://doi.org/10.1021/j100540a008  
14. Finster, F. (2018). *Causal Fermion Systems: Discrete Space-Times, Causation and Finite Propagation Speed*. arXiv:1812.00238. https://arxiv.org/abs/1812.00238  
15. Finster, F., Gresnigt, N. G., Isidro, J. M., Marciano, A., Paganini, C. F., Singh, T. P. (2024). *Causal Fermion Systems and Octonions*. arXiv:2403.00360. https://arxiv.org/abs/2403.00360

