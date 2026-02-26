# RFC-024: Discrete Phase Signatures Across Physics and COG Mapping

**Status:** Active - Literature-Reconciled Draft (2026-02-26)  
**Module:** `COG.Core.PhaseCatalog`  
**Depends on:** `rfc/RFC-020_Kernel_Representation_Reconciliation.md`, `rfc/RFC-023_Discrete_Phase_Clocks_and_Relative_Phase_Interactions.md`  
**Literature basis:** `sources/discrete_phase_catalog_lit_review.md`

---

## 1. Executive Summary

This RFC catalogs independent physics evidence for discrete phase structure and maps each clue to COG test obligations.

Core result:

1. Discrete phase sectors are common in physics (`Z2`, `ZN`, braid/fractional classes, subharmonic temporal classes).
2. These clues support the plausibility of COG's phase-clock hypotheses.
3. None of these clues uniquely proves COG's specific `e7`-driven `Z4` mechanism.
4. Therefore, COG must treat `e7/Z4` as a testable model commitment, not a literature theorem.

---

## 2. Motivation

RFC-023 introduced a local `Z4` phase-clock hypothesis tied to proved period-4 e7 dynamics.  
This follow-on RFC asks a narrower question:

- What established discrete-phase phenomena in mainstream physics should inform COG model design?

The goal is to improve external coherence while preventing overreach.

---

## 3. Discrete-Phase Catalog

### C1. Spinor `4pi` periodicity (`Z2`)

Evidence: fermionic/spinor states can require `4pi` to return exactly.  
COG mapping: precedent that intrinsic state phase can be discrete and operationally relevant.

### C2. Flux-phase periodicity (Aharonov-Bohm)

Evidence: interference observables oscillate with quantized flux period.  
COG mapping: phase sector can control observables without changing local material identity.

### C3. Josephson/Shapiro phase locking

Evidence: driven superconducting junctions exhibit quantized step families tied to phase-frequency lock.  
COG mapping: interaction channels can be phase-conditioned and frequency-ratio conditioned.

### C4. Anyonic exchange phases

Evidence: 2D topological systems show fractional exchange phases and measurable statistical-angle effects.  
COG mapping: relative phase/statistics class can alter collision/correlation outcomes.

### C5. Quantized Berry phases (`ZN`)

Evidence: symmetry/topology can quantize geometric phase into discrete classes.  
COG mapping: phase index can be symmetry-protected and robust against local perturbations.

### C6. Gauge center sectors (`Z_N`)

Evidence: center symmetry organizes distinct gauge-vacuum sectors in finite-temperature gauge theory.  
COG mapping: vacuum-sector labels as discrete phase classes are physically meaningful.

### C7. Time-crystal multi-period order

Evidence: driven many-body systems can exhibit subharmonic and multi-period responses.  
COG mapping: composite subsystem periods may exceed primitive local period (supports cycle-spectrum program).

---

## 4. What This Supports in COG (and What It Does Not)

## 4.1 Supported

1. Maintaining an explicit discrete phase observable (RFC-023 `phi4`, `DeltaPhi4`) is physically reasonable.
2. Testing phase-conditioned interaction kernels is high value.
3. Searching for composite cycle spectra beyond 4 is strongly motivated.

## 4.2 Not supported

1. A claim that external literature proves `e7` is uniquely the temporal axis.
2. A claim that phase ignorance itself provides physical energy.

---

## 5. Architecture Requirements Added by This RFC

### R1. Phase-catalog alignment

Any COG phase claim must declare which external clue family it most closely resembles (`C1`..`C7`), to keep interpretation disciplined.

### R2. Evidence mode tags

Phase-related claims must include one of:

- `mode: theorem_proved` (Lean/kernel theorem),
- `mode: simulation_supported`,
- `mode: literature_analogy_only`.

### R3. Energy-separation guard

Any phase-entropy argument must explicitly separate:

- epistemic uncertainty metric,
- dynamical energy metric.

Claims that conflate them are blocked pending explicit derivation.

---

## 6. Test Program

1. **Phase-conditioned channel test**: estimate channel frequencies by `DeltaPhi4`.
2. **Reference-loss test**: remove phase reference from observer model; measure predictive drop.
3. **Cycle-spectrum test**: estimate period distribution of composite motifs.
4. **Energy-separation test**: vary observer phase knowledge only; verify no energy-accounting drift.

---

## 7. Governance Impact

1. Supports RFC-023 by broadening literature grounding.
2. Imposes stricter claim labeling to avoid over-interpretation.
3. Helps manager/debugger prioritize foundational phase tests before speculative mass links.

---

## 8. Open Questions

1. Which catalog family (`C1`..`C7`) best matches COG phase dynamics empirically?
2. Do COG phase classes show symmetry protection analogues?
3. What minimal experiment/simulation can falsify phase-conditioned interaction effects quickly?

---

## 9. References

See `sources/discrete_phase_catalog_lit_review.md`.

