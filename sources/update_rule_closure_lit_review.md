# Deterministic Lightcone Update Rules: Literature Review for COG

Date: 2026-02-26
Scope: settle a canonical COG update rule over `C x O` node states with lightcone-local inputs, explicit ordering, and deterministic replay.
Primary question: what must be fixed to turn "kernel state + lightcone + trace + superdetermined initial condition" into a complete update law?

---

## 1. Executive Summary

Your intuition is directionally correct. A defensible COG update rule needs four layers:

1. Lightcone-local boundary messages.
2. A predeclared deterministic ordering/parenthesization plan.
3. Optional finite trace-memory terms (if non-Markov effects are modeled).
4. A fixed combine law that maps base temporal evolution and interaction terms to the next state.

Literature strongly supports layers 1-3 in structure. The main unsolved COG-specific choice is layer 4 (the exact `combine` operator and conservation contract).

---

## 2. What Literature Constrains

## 2.1 Locality and causal update structure

- Causal graph dynamics formalizes local, synchronous, bounded-speed graph rewrites.
- Sequential growth in causal-set work emphasizes causality and label-independence constraints on growth order.
- Lieb-Robinson style bounds motivate strict or effective lightcone constraints in local dynamics.

COG implication:
- Candidate interactions at `(t, v)` should come only from an explicit incoming boundary set.
- Any outside-cone influence must be either impossible (strict cone) or bounded/logged (effective cone).

## 2.2 Determinism and ordering

- Deterministic graph transformations are well-defined when local maps and update scheduling are fixed.
- Non-associative algebras require explicit parenthesization for unambiguous multi-input composition.

COG implication:
- Superdetermined initial condition should include immutable tie-break and parenthesization data.
- Runtime ordering disputes should never be resolved ad hoc.

## 2.3 Trace and memory

- Process tensor / quantum comb formalisms show that non-Markov dynamics requires explicit history dependence.
- History dependence can be represented with finite memory windows when full-history dependence is not needed.

COG implication:
- If COG claims non-Markov updates, trace state must be part of kernel semantics, not logging only.
- If COG stays Markov, trace is optional and should not alter state transition.

## 2.4 Superdeterminism and no-signaling constraints

- Measurement dependence can reproduce Bell-violating correlations in deterministic hidden-variable models.
- This does not remove the requirement to enforce no-signaling operationally.

COG implication:
- A superdetermined initial condition is internally consistent, but must be explicit and auditable.
- No-signaling audits still remain mandatory in derived correlation claims.

## 2.5 Coarse-graining and uncertainty

- Decoherence/coarse-graining literature supports uncertainty emerging from observer-limited projections of larger deterministic states.

COG implication:
- The "uncertainty from projection of larger event information" hypothesis is viable if COG defines a fixed projection map and quantifies information loss.

---

## 3. What Literature Does Not Settle for COG

1. The exact `combine` law for `C x O` updates.
2. The exact energy-exchange predicate used for `tau_int`.
3. The exact trace window size and memory kernel.
4. Whether `k > 4` is negligible for key observables (must be measured, not assumed).
5. The concrete projection map from full causal microstate to reported observables.

These are model decisions, not imported theorems.

---

## 4. Recommended Closure Pattern for COG

1. Lock `IncomingBoundary_t(v)` and deterministic ordering as kernel-level definitions.
2. Decide one `combine` operator family before further derived-constant work.
3. Define one explicit trace contract:
   - Markov (`m=0`) or
   - finite-memory (`m>0`, declared).
4. Add no-cone-leak and scheduler-equivalence tests as promotion gates.
5. Add projection map and information-loss metrics before strong claims about uncertainty/entropy.

---

## 5. References

1. P. Arrighi, G. Dowek (2012), Causal graph dynamics, arXiv:1202.1098, https://arxiv.org/abs/1202.1098
2. P. Arrighi, S. Martiel (2016), Quantum Causal Graph Dynamics, arXiv:1607.06700, https://arxiv.org/abs/1607.06700
3. L. Maignan, A. Spicher (2024), Causal Graph Dynamics and Kan Extensions, arXiv:2403.13393, https://arxiv.org/abs/2403.13393
4. L. Bombelli, J. Lee, D. Meyer, R. D. Sorkin (1987), Space-Time as a Causal Set, Phys. Rev. Lett. 59, 521, https://doi.org/10.1103/PhysRevLett.59.521
5. D. P. Rideout, R. D. Sorkin (1999), A Classical Sequential Growth Dynamics for Causal Sets, arXiv:gr-qc/9904062, https://arxiv.org/abs/gr-qc/9904062
6. S. Surya (2019), The causal set approach to quantum gravity, arXiv:1903.11544, https://arxiv.org/abs/1903.11544
7. E. H. Lieb, D. W. Robinson (1972), The finite group velocity of quantum spin systems, https://doi.org/10.1007/BF01645779
8. T. Kuwahara, T. S. Cubitt, A. Lucia, N. Shammah (2022), Strict light cones in long-range interacting systems, PRX Quantum 3, 030333, https://doi.org/10.1103/PRXQuantum.3.030333
9. F. A. Pollock et al. (2018), Operational Markov Condition for Quantum Processes, arXiv:1801.09811, https://arxiv.org/abs/1801.09811
10. G. Chiribella, G. M. D'Ariano, P. Perinotti (2008), Quantum Circuit Architecture, arXiv:0803.3231, https://arxiv.org/abs/0803.3231
11. J. S. Bell (1964), On the Einstein-Podolsky-Rosen paradox, https://doi.org/10.1103/PhysicsPhysiqueFizika.1.195
12. J. F. Clauser, M. A. Horne, A. Shimony, R. A. Holt (1969), Proposed Experiment to Test Local Hidden-Variable Theories, https://doi.org/10.1103/PhysRevLett.23.880
13. M. J. W. Hall (2010), Local deterministic model of singlet state correlations based on relaxing measurement independence, arXiv:1007.5518, https://arxiv.org/abs/1007.5518
14. A. S. Friedman et al. (2019), Measurement dependence in Bell tests, arXiv:1901.04521, https://arxiv.org/abs/1901.04521
15. S. Hossenfelder, T. Palmer (2020), Rethinking Superdeterminism, arXiv:1912.06462, https://arxiv.org/abs/1912.06462
16. W. H. Zurek (2003), Decoherence, einselection, and the quantum origins of the classical, arXiv:quant-ph/0306072, https://arxiv.org/abs/quant-ph/0306072
17. F. Finster et al. (2024), Causal Fermion Systems and Octonions, arXiv:2403.00360, https://arxiv.org/abs/2403.00360
