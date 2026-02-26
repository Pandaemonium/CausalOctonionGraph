# Superconductivity and Ferroelectricity Modeling Clues for COG

Date: 2026-02-26
Scope anchors:
- `rfc/RFC-020_Kernel_Representation_Reconciliation.md`
- `rfc/RFC-022_Lightcone_Semantics_and_Causal_Locality.md`
- `rfc/RFC-023_Discrete_Phase_Clocks_and_Relative_Phase_Interactions.md`
- `rfc/RFC-024_Discrete_Phase_Signatures_Across_Physics.md`

Question:
- Which established results in superconductivity and ferroelectricity are most useful as modeling targets in COG?

---

## 1. Executive Summary

Highest-value cross-domain clues:

1. Both domains are phase-order systems with collective order parameters.
2. Both have defect dynamics (vortices or domain walls) that dominate response.
3. Both show strongly history-dependent behavior under drive (hysteresis, switching, phase slips).
4. Both require careful separation between microscopic mechanism and mesoscopic observables.

Immediate COG implication:
- Model observables first (phase locking, winding, domain switching, hysteresis loops), then test whether your octonionic local rules reproduce those signatures.

---

## 2. Superconductivity: Reliable Anchors

## 2.1 Microscopic pairing and emergent phase order

- BCS gives the conventional pairing mechanism and coherent condensate phase.
- Ginzburg-Landau gives mesoscopic order-parameter dynamics usable as an effective benchmark language.

COG modeling clue:
- Define graph-level phase-coherence metrics and test for low-dissipation transport proxies in coherent subgraphs.

## 2.2 Direct phase observables

- Josephson relations connect phase difference to supercurrent and frequency-voltage locking.
- Flux quantization and Little-Parks give loop periodicity diagnostics.

COG modeling clue:
- Build loop and weak-link experiments in simulation and measure:
  - phase-lock plateaus under periodic drive,
  - winding-number stability,
  - periodic response of loop observables.

## 2.3 Critical caution

- Some signatures (for example missing odd Shapiro steps) are not unique to topological mechanisms.

COG modeling rule:
- Require multi-signature agreement; no single phase signature is enough for mechanism claims.

---

## 3. Ferroelectricity: Reliable Anchors

## 3.1 Polarization as a branch quantity

- Modern polarization theory treats polarization differences as geometric and branch-valued.

COG modeling clue:
- Represent polarization-like observables as sector/branch variables, not absolute scalar labels detached from history.

## 3.2 Switching kinetics and hysteresis

- Landau-Khalatnikov and KAI/NLS families provide competing switching descriptions.
- Real materials often deviate from ideal KAI due to disorder, finite size, and interface effects.

COG modeling clue:
- Add explicit sweep protocols (field ramps) and fit multiple kinetics families to graph responses.

## 3.3 Domain walls as active degrees of freedom

- Domain walls can carry distinct transport and functional behavior.

COG modeling clue:
- Track phase-sector boundaries as first-class objects; measure wall density, mobility, and pinning.

---

## 4. Cross-Domain Structure to Reuse in COG

Common structure that can be directly mapped:

1. Local update rules produce emergent mesoscopic order.
2. Relative phase between regions controls channel behavior.
3. Defect populations control dissipation and switching cost.
4. Drive protocols expose hidden state structure via hysteresis/locking.

This aligns naturally with:
- `phi4` and `DeltaPhi4` observables (RFC-023),
- lightcone-local updates (RFC-022),
- kernel-state determinism (RFC-020).

---

## 5. Suggested COG Observable Set

Superconductivity-inspired:

1. `Coh(t)`:
   - coherence score over a chosen subgraph (phase alignment metric).
2. `W(loop, t)`:
   - integer winding-like index around closed graph loops.
3. `SlipRate(t)`:
   - rate of discrete phase-slip events.
4. `LockPlateau`:
   - stability regions in driven weak-link simulations.

Ferroelectricity-inspired:

1. `P_sector(region, t)`:
   - discrete polarization-sector label for a region.
2. `WallDensity(t)`:
   - number of sector boundaries per unit subgraph.
3. `SwitchLatency`:
   - ticks between bias threshold and bulk sector reversal.
4. `HystArea`:
   - loop area under periodic bias cycles.

---

## 6. Minimal Benchmark Program

1. Weak-link phase-lock benchmark:
   - Two coherent regions coupled by a sparse boundary, periodic forcing.
   - Log plateaus and phase-slip statistics.

2. Loop quantization benchmark:
   - Closed loop motifs under controlled forcing.
   - Track winding-state persistence and transition rates.

3. Polarization switching benchmark:
   - Two-sector initialization plus bias ramps.
   - Measure switching thresholds, hysteresis area, and reversibility.

4. Domain-wall kinetics benchmark:
   - Seed multiple sector boundaries.
   - Measure wall motion under noise-free and perturbed update schedules.

---

## 7. Non-Claims (Important)

This review does not claim:

1. COG has derived BCS microphysics.
2. COG has derived ab initio ferroelectric chemistry.
3. Any one condensed-matter signature uniquely validates COG foundations.

It does justify these as high-quality external benchmark targets for your discrete model.

---

## 8. Primary References

Superconductivity

1. Bardeen, Cooper, Schrieffer (1957), Theory of Superconductivity.
   - DOI: https://doi.org/10.1103/PhysRev.108.1175
2. Ginzburg, Landau (1950), On the Theory of Superconductivity.
   - Record: https://www.osti.gov/biblio/4372225
3. Josephson (1962), Possible new effects in superconductive tunnelling.
   - DOI: https://doi.org/10.1016/0031-9163(62)91369-0
4. Little, Parks (1962), Quantum periodicity in superconducting cylinder.
   - DOI: https://doi.org/10.1103/PhysRevLett.9.9
5. Anderson (1963), Plasmons, gauge invariance, and mass.
   - DOI: https://doi.org/10.1103/PhysRev.130.439
6. Dartiailh et al. (2021), Missing Shapiro steps in topologically trivial junction.
   - DOI: https://doi.org/10.1038/s41467-020-20382-y
7. de Gennes (1999), Superconductivity of Metals and Alloys (book benchmark).
   - Publisher page: https://www.routledge.com/Superconductivity-Of-Metals-And-Alloys/de-Gennes/p/book/9780738201019

Ferroelectricity

8. Cohen (1992), Origin of ferroelectricity in perovskite oxides.
   - DOI: https://doi.org/10.1038/358136a0
9. King-Smith, Vanderbilt (1993), Theory of polarization of crystalline solids.
   - DOI: https://doi.org/10.1103/PhysRevB.47.1651
10. Resta (1994), Macroscopic polarization in crystalline dielectrics.
   - DOI: https://doi.org/10.1103/RevModPhys.66.899
11. Tagantsev et al. (2002), Non-KAI switching kinetics in thin films.
   - DOI: https://doi.org/10.1103/PhysRevB.66.214109
12. Chen (2008), Phase-field method for ferroelectrics (review).
   - DOI: https://doi.org/10.1111/j.1551-2916.2008.02413.x
13. Benedek, Fennie (2011), Hybrid improper ferroelectricity.
   - DOI: https://doi.org/10.1103/PhysRevLett.106.107204
   - arXiv: https://arxiv.org/abs/1007.1003
14. Meier, Selbach (2022), Ferroelectric domain walls for nanotechnology.
   - DOI: https://doi.org/10.1038/s41578-021-00375-z
15. Das et al. (2023), First-principles domain wall energies in perovskites.
   - DOI: https://doi.org/10.1016/j.actamat.2022.118351

