# RFC-021: Entanglement, Interaction, and Causal-Past Projection

**Status:** Active - Literature-Reconciled Draft (2026-02-25)  
**Module:** `COG.Core.Entanglement`, `COG.Core.Observation`, `COG.Core.Memory`  
**Depends on:** `rfc/RFC-002_Deterministic_Tick_Ordering.md`, `rfc/RFC-018_Time_as_Graph_Depth_and_Interaction_Clock.md`, `rfc/RFC-019_e7_Temporal_Axis_Vacuum_Photon_Duality.md`, `rfc/RFC-020_Kernel_Representation_Reconciliation.md`

---

## 1. Executive Summary

This RFC evaluates the proposal:

- entanglement is interaction,
- every interaction creates entanglement,
- a state includes its full causal-past information,
- uncertainty is caused by projecting a very large hidden state onto a 16-dimensional observable.

Result after literature scrutiny:

1. Keep a weaker claim: interactions have measurable **entangling power**, but entanglement is not identical to interaction.
2. Reject the universal claim "every interaction entangles."
3. Keep a causal-memory model: effective state can depend on multi-time history.
4. Keep projection-loss as a mechanism for uncertainty.
5. Treat "16 dimensions" as a COG hypothesis to test, not as a literature theorem.

---

## 2. Hypothesis Triage

### H1. "Entanglement is interaction."

**Verdict:** reject as identity claim.  
**Adoptable form:** entanglement is a key signature/resource of interaction structure.

Reason: entanglement can appear between systems that never directly interacted (entanglement swapping), so direct interaction is not necessary for final-pair entanglement.

### H2. "Any interaction results in entanglement."

**Verdict:** reject as universal law.  
**Adoptable form:** generic nonlocal dynamics can generate entanglement, but there are explicit non-entangling and entanglement-breaking maps.

Reason: entanglement-breaking channels and LOCC-class operations provide counterexamples.

### H3. "Complete state includes causal past."

**Verdict:** adopt with implementation constraints.  
**Adoptable form:** use a finite, explicit history object (memory kernel / bounded process tensor proxy).

Reason: process-tensor literature formalizes multi-time memory and Markov/non-Markov distinctions.

### H4. "Future branch is selected by fully superdetermined initial condition."

**Verdict:** keep as COG modeling assumption, not a settled physics theorem.  
**Adoptable form:** expose measurement-dependence assumptions as parameters and test sensitivity.

### H5. "Uncertainty comes from projection onto 16D observables."

**Verdict:** partially adopt.  
**Adoptable form:** uncertainty can arise from many-to-one projection from full microstate to observables; dimension `16` is currently a project hypothesis.

---

## 3. Literature-Backed Principles To Adopt

### P1. Entangling-power classification

For each update operator, track:

- whether it is entangling-capable on the tested domain,
- expected entanglement gain on product inputs,
- explicit exception class (non-entangling / entanglement-breaking).

This follows entangling-power and Hamiltonian-capacity literature.

### P2. Mediated-entanglement compatibility

Model rules must allow entanglement to arise through a larger causal process, not only by direct final-pair coupling.

### P3. Causal-memory representation

State update may depend on bounded causal history. This should be explicit in the kernel contract, not implicit in ad hoc caches.

### P4. Projection-loss observable

Define uncertainty as information discarded by observation map `Pi_d`, where `d` is configurable (`8`, `16`, `32`, ...).

### P5. Measurement-dependence accounting

If superdeterministic language is used, include an explicit measurement-dependence budget rather than qualitative claims.

---

## 4. Proposed Formal Model (Compatible with RFC-020)

Define at tick `t`:

```text
Sigma_t     : full hidden microstate (CxO-native, plus bounded memory payload)
M_t(v)      : deterministic incoming message multiset from causal past of node v
Sigma_{t+1} = F(Sigma_t, EvalPlan_t, M_t)
x_t         = Pi_d(Sigma_t)    -- observable projection, default d = 16 (hypothesis)
```

Define two diagnostics:

```text
DeltaE_t = E(Sigma_{t+1}) - E(Sigma_t)    -- chosen entanglement measure/witness
U_t      = Loss(Sigma_t -> x_t)           -- projection information loss proxy
```

Interpretation:

- interaction step does not imply `DeltaE_t > 0` in every case,
- uncertainty can increase via larger projection loss even under deterministic `F`.

---

## 5. What Is Explicitly Not Adopted

1. "All interactions necessarily create entanglement."
2. "Direct interaction between two systems is required for their entanglement."
3. "16 dimensions is uniquely correct without ablation."
4. "Superdeterminism is established rather than parameterized."

---

## 6. Implementation Targets

### 6.1 Lean targets

1. Define `Pi_d : Sigma -> Obs d` and prove non-injectivity for selected `d`.
2. Define transition predicate `InteractionStep` and metric placeholder `DeltaE`.
3. Prove existence of at least one interaction step with `DeltaE = 0` (counterexample to universal-entangling claim).
4. Add mediated-entanglement theorem stub for a finite toy process network.
5. Prove deterministic replay invariance with RFC-002 eval-plan immutability.

### 6.2 Python targets

1. Add `calc/entangling_power_benchmark.py`.
2. Add `calc/entanglement_exception_catalog.py` (non-entangling and entanglement-breaking examples).
3. Add `calc/projection_loss_sweep.py` for `d in {8, 16, 32}`.
4. Add `calc/mediated_entanglement_regression.py` (swapping-style structural test).
5. Emit dashboard metrics: `delta_entanglement`, `projection_loss`, `history_depth_used`.

---

## 7. Falsification and Decision Tests

1. **Universal-entanglement falsification:** find interaction maps with `DeltaE = 0` on broad input sets.
2. **Mediated-entanglement capability:** show entanglement of outputs without direct final-pair interaction.
3. **Projection-dimension ablation:** compare explanatory fit of `d = 8, 16, 32`.
4. **Memory-depth sensitivity:** quantify predictive loss under finite history truncation.
5. **Measurement-dependence sensitivity:** quantify Bell-style fit versus dependence budget.

---

## 8. Claim Governance Impact

No currently proved Lean theorem is invalidated by this RFC.

Governance change:

- Any future claim with wording equivalent to "all interactions entangle" is blocked unless it includes explicit assumptions that exclude known exception classes.
- Any claim using `d = 16` as unique must include dimension-ablation evidence.

---

## 9. References

1. P. Zanardi, C. Zalka, L. Faoro, "On the Entangling Power of Quantum Evolutions" (2000). https://arxiv.org/abs/quant-ph/0005031  
2. W. Dur, G. Vidal, J. I. Cirac, N. Linden, S. Popescu, "Entanglement capabilities of non-local Hamiltonians" (2000). https://arxiv.org/abs/quant-ph/0006034  
3. C. H. Bennett, A. W. Harrow, D. W. Leung, J. A. Smolin, "On the capacities of bipartite Hamiltonians and unitary gates" (2002). https://arxiv.org/abs/quant-ph/0205057  
4. M. Horodecki, P. W. Shor, M. B. Ruskai, "General Entanglement Breaking Channels" (2003). https://arxiv.org/abs/quant-ph/0302031  
5. M. Zukowski, A. Zeilinger, M. A. Horne, A. K. Ekert, "Event-ready-detectors Bell experiment via entanglement swapping" (1993). https://doi.org/10.1103/PhysRevLett.71.4287  
6. J.-W. Pan, D. Bouwmeester, H. Weinfurter, A. Zeilinger, "Experimental Entanglement Swapping: Entangling Photons That Never Interacted" (1998). https://doi.org/10.1103/PhysRevLett.80.3891  
7. F. A. Pollock et al., "Operational Markov Condition for Quantum Processes" (2018). https://arxiv.org/abs/1801.09811  
8. C. Giarmatzi, F. Costa, "A quantum causal discovery algorithm" (2017). https://arxiv.org/abs/1704.00800  
9. W. H. Zurek, "Decoherence, einselection, and the quantum origins of the classical" (2001/2003). https://arxiv.org/abs/quant-ph/0105127  
10. M. Schlosshauer, "Decoherence, the measurement problem, and interpretations of quantum mechanics" (2005). https://doi.org/10.1103/RevModPhys.76.1267  
11. D. N. Page, "Average Entropy of a Subsystem" (1993). https://arxiv.org/abs/gr-qc/9305007  
12. S. Popescu, A. J. Short, A. Winter, "Entanglement and the foundations of statistical mechanics" (2005/2006). https://arxiv.org/abs/quant-ph/0511225  
13. M. J. W. Hall, "Local deterministic model of singlet state correlations based on relaxing measurement independence" (2010). https://arxiv.org/abs/1007.5518  
14. A. S. Friedman et al., "Relaxed Bell Inequalities with Arbitrary Measurement Dependence for Each Observer" (2018). https://arxiv.org/abs/1809.01307  
15. S. Hossenfelder, T. N. Palmer, "Rethinking Superdeterminism" (2019/2020). https://arxiv.org/abs/1912.06462  
16. F. Finster et al., "Causal Fermion Systems and Octonions" (2024). https://arxiv.org/abs/2403.00360