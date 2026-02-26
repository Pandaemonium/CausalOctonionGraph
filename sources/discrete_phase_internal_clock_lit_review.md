# Discrete Phase and Internal Clock Hypotheses: Literature Review for COG

**Date:** 2026-02-26  
**Scope anchor:** `rfc/RFC-018_Time_as_Graph_Depth_and_Interaction_Clock.md`, `rfc/RFC-019_e7_Temporal_Axis_Vacuum_Photon_Duality.md`, `rfc/RFC-020_Kernel_Representation_Reconciliation.md`, `rfc/RFC-021_Entanglement_Interaction_and_Causal_Projection.md`  
**Focus question:** Can a fast discrete internal phase (4-state for e7 action) be physically meaningful for interaction outcomes, uncertainty, and energy in COG?

---

## 1. Executive Summary

This review supports a strong core and rejects two over-claims:

1. **Supported:** Internal fast phase/clock ideas are physically meaningful in several quantum settings (matter-wave clocks, synchronization, Floquet subharmonics).
2. **Supported:** Interaction outcomes can depend on relative phase in coherent settings (coherent control, scattering interferometry).
3. **Supported with caveats:** Without a shared phase reference, relative phase can be operationally inaccessible and behave like observer-level uncertainty.
4. **Not supported:** "Unknown phase entropy generates energy" as a standalone mechanism.
5. **Not supported as universal law:** "Any interaction necessarily reveals or creates usable phase information."

For COG, the best interpretation is:

- treat 4-state e7 phase as a deterministic hidden microstate variable,
- treat missing phase reference as epistemic uncertainty,
- test whether relative phase modulates interaction channels,
- do not infer energy from ignorance alone.

---

## 2. Internal COG Facts Already Relevant

From Lean proofs and existing RFCs:

1. Repeated left and right `e7` actions are exact period-4 for nonzero states (`Spinors.lean`: `universal_Ce_period_four`, `universal_Ce_right_period_four`).
2. Vacuum orbit under `e7` is explicit and phase-like (`e7Left_on_omegaDoubled`, `e7Right_on_omegaDoubled`).
3. Time in current architecture is two-clock (`tau_topo`, `tau_int`) and deterministic (RFC-018).
4. Entanglement is not identical to interaction and not guaranteed by every interaction (RFC-021).

So "discrete phase class" is compatible with current foundations, but "phase causes energy by entropy" is not yet grounded.

---

## 3. External Literature Signals

## 3.1 Internal clocks and fast oscillations

- de Broglie/Compton clock interpretations appear in atom/electron contexts and remain actively debated.
- Zitterbewegung-style internal oscillations are physically modeled and experimentally emulated in solid-state settings.

COG implication: a high-frequency internal phase variable is plausible as a model ingredient.

## 3.2 Relative phase can affect interactions

- Coherent-control collision work shows large modulation of ionization channels by preparing phase-controlled superpositions.
- Scattering interferometry directly measures phase shifts in collision processes.

COG implication: phase-dependent interaction kernels are physically plausible and testable.

## 3.3 Missing phase reference as operational uncertainty

- Quantum information work on reference frames/superselection shows that without a shared phase reference, some coherence is not operationally accessible.
- Clock synchronization literature highlights unknown phase offsets as concrete error sources and studies entanglement-assisted removal.

COG implication: if observers lack phase reference to another subsystem, effective uncertainty arises even under deterministic dynamics.

## 3.4 Multi-period temporal order beyond simple 2-cycles

- Discrete time crystal literature shows robust subharmonic and multi-period responses in driven many-body systems, including concurrent `2T` and `3T` behavior in qudit settings.

COG implication: graph-level composite interactions can plausibly realize cycle spectra beyond 4 even if single-operator e7 action is 4-periodic.

---

## 4. Claim Triage for the User Hypothesis

### H1. "e7 4-cycle gives each particle a discrete phase."

**Verdict:** adopt as COG-internal hypothesis with strong internal theorem support.

### H2. "Interaction strength/channel depends on relative phase class."

**Verdict:** adopt as testable mechanism; not yet proved in COG.

### H3. "Without recent interaction/entanglement, phase is unpredictable."

**Verdict:** partially adopt in epistemic form (missing reference phase), not ontic randomness.

### H4. "This gives 2 bits of effective entropy."

**Verdict:** adopt as observer-level Shannon uncertainty for a 4-state hidden phase under suitable coarse-graining assumptions.

### H5. "This entropy and cyclic oscillation can provide energy."

**Verdict:** reject in that form.  
Energy must come from the model's dynamics/transition structure; uncertainty alone does not add physical energy.

### H6. "More complex interactions can have cycle lengths > 4."

**Verdict:** adopt as plausible and worth formal cycle-spectrum measurement.

---

## 5. Design Consequences for COG

1. Add explicit local phase label `phi4 in Z4` as a derived observable from Kernel v2 state under repeated temporal commit.
2. Define relative phase `DeltaPhi4` on interacting pairs and log it.
3. Add phase-conditioned interaction statistics:
   - channel frequency by `DeltaPhi4`
   - transition cost by `DeltaPhi4`
   - replay invariance under fixed initial microstate.
4. Add cycle-spectrum detector for composite subsystems to find periods beyond 4.
5. Keep strict distinction:
   - ontic determinism (microstate fixed),
   - epistemic uncertainty (observer lacks phase reference).

---

## 6. References

1. M. Bauer (2014), *Electron channeling, de Broglie's clock and the relativistic time operator*. https://arxiv.org/abs/1403.4580  
2. I. Stepanov et al. (2016), *Coherent Electron Zitterbewegung*. https://arxiv.org/abs/1612.06190  
3. P. Wolf et al. (2010), *Does an atom interferometer test the gravitational redshift at the Compton frequency?* https://arxiv.org/abs/1012.1194  
4. S. Peil, C. Ekstrom (2014), *Analysis of atom-interferometer clocks*. https://arxiv.org/abs/1402.6621  
5. C. A. Arango, M. Shapiro, P. Brumer (2006), *Cold Atomic Collisions: Coherent Control of Penning and Associative Ionization*. https://arxiv.org/abs/physics/0610131  
6. R. A. Hart et al. (2007), *A quantum scattering interferometer*. https://www.nature.com/articles/nature05680  
7. S. D. Bartlett, T. Rudolph, R. W. Spekkens (2007), *Reference frames, superselection rules, and quantum information*. https://arxiv.org/abs/quant-ph/0610030  
8. J. A. Vaccaro, F. Anselmi, H. M. Wiseman (2003), *Entanglement of identical particles and reference phase uncertainty*. https://arxiv.org/abs/quant-ph/0311028  
9. E. O. Ilo-Okeke et al. (2017), *Remote quantum clock synchronization without synchronized clocks*. https://arxiv.org/abs/1709.08423  
10. J. Preskill (2000), *Quantum clock synchronization and quantum error correction*. https://arxiv.org/abs/quant-ph/0010098  
11. D. V. Else, C. Monroe, C. Nayak, N. Y. Yao (2020), *Discrete Time Crystals* (review). https://www.annualreviews.org/doi/10.1146/annurev-conmatphys-031119-050658  
12. L.-Z. Tang et al. (2025), *Discrete time crystals enabled by Floquet strong Hilbert space fragmentation*. https://arxiv.org/abs/2512.14182  
13. W.-G. Ma, H. Fan, S.-X. Zhang (2025), *A Qudit-native Framework for Discrete Time Crystals*. https://arxiv.org/abs/2512.04577  
14. H. Yu, T.-C. Wei (2024), *Subspace-thermal discrete time crystals from phase transitions between different n-tuple discrete time crystals*. https://arxiv.org/abs/2409.02848  
15. P. Zanardi, C. Zalka, L. Faoro (2000), *On the Entangling Power of Quantum Evolutions*. https://arxiv.org/abs/quant-ph/0005031  
16. M. Horodecki, P. W. Shor, M. B. Ruskai (2003), *General Entanglement Breaking Channels*. https://arxiv.org/abs/quant-ph/0302031  

