# RFC-030: Exploratory Broad Physics Phenomena in COG

**Status:** Active - Exploratory Draft (2026-02-26)  
**Module:** `COG.Core.Phenomenology`  
**Dependencies:** `rfc/RFC-018_Time_as_Graph_Depth_and_Interaction_Clock.md`, `rfc/RFC-019_e7_Temporal_Axis_Vacuum_Photon_Duality.md`

---

## 1. Executive Summary

This RFC addresses the strategic need to broaden the project's phenomenological horizons. While the lab has focused heavily on the Koide formula and mass ratios (which are complex, cumulative, emergent properties), there are other foundational physical phenomena that may offer *more straightforward and immediate* interpretations within Causal Octonion Graph (COG) dynamics.

By exploring these broad phenomena, we can solidify the core graph update rules and state representations more efficiently than by brute-forcing high-level parameter matches. This document proposes four candidate phenomena that naturally map to discrete, algebraically-driven causal graph properties.

---

## 2. Motivation

A purely deductive approach from octonions to Standard Model constants risks dead-ends if the core discrete engine (spawn semantics, temporal advancement) isn't fully robust.

If we look at the universe of physical phenomena, some behaviors are almost "native" to a system defined by:
1. Directed acyclic graphs (DAGs).
2. Phase-cycling node states (period-4 operations via `e7`).
3. Multipath interference.

Pursuing these structural parallels offers a faster cadence of high-impact theoretical wins and can directly constrain our foundational update rules.

---

## 3. Top Candidate Phenomena for COG Interpretation

### 3.1 Interference and Path Integrals (The Double-Slit)
**Phenomenon:** The core mystery of quantum mechanics: a particle takes multiple paths, and the phases of these paths interfere upon measurement.
**COG Interpretation:**
- In COG, a particle is not a persistent point but a propagating wave of state updates across the causal graph.
- When a state is spawned across multiple branches (divergence) and then paths reconverge (causal intersection), the total payload is the sum of `BoundaryMsg` payloads.
- Because `e7` temporal commit operates as a phase rotation (`tau_topo`), paths of different graph depths will arrive with different octonion phases. Reconvergence naturally produces constructive or destructive interference based on topological path length differences, immediately mirroring Feynman's Path Integral formulation.

### 3.2 Zitterbewegung (Trembling Motion)
**Phenomenon:** The theoretical rapid jittering motion of elementary particles (like electrons), derived from the Dirac equation, with a frequency proportional to `2mc^2 / h`.
**COG Interpretation:**
- The discrete update rule and the `e7` temporal commit (RFC-019) guarantee that every node step involves an algebraic rotation.
- A static particle (e.g., an electron in a rest frame) is not "doing nothing"; it is continuously spawning updates. If the e7 action cycles the state through left/right chirality or phase with period 4, this oscillation is a literal, inescapable property of the microstate.
- This creates an intrinsic "micro-clock" (Zitterbewegung) that underpins mass (RFC-018 links interaction clock to energy).

### 3.3 Quantum Entanglement and EPR Correlations
**Phenomenon:** Spatially separated particles exhibit correlated states that cannot be explained by local hidden variables (Bell's Theorem).
**COG Interpretation:**
- The universe's topology in COG is the graph itself. What appears as "spacelike separation" in emergent spacetime is simply two nodes with a high topological distance.
- However, two entangled particles share a very recent common causal ancestor in the graph.
- If the octonion rules enforce a zero-sum conservation law upon splitting (e.g., opposite phases/chiralities on the two spawned branches), this algebraic correlation persists perfectly down both branches. Since COG lacks a pre-existing geometric background space to "dilute" this correlation, the perfect anti-correlation upon eventual measurement is geometrically natural. It perfectly obeys graph-local causality while appearing non-local in emergent 3D space.

### 3.4 CPT Symmetry and Anti-Matter
**Phenomenon:** The universe is perfectly symmetric under the simultaneous inversion of Charge (C), Parity (P), and Time (T).
**COG Interpretation:**
- Time (T) is directly mapped to the direction of causal edges and the sign of the `e7` temporal action (RFC-019).
- Parity (P) corresponds to the spatial orientation of the Fano plane or the algebraic handedness (left- vs right-action) of the octonions.
- Charge (C) corresponds to the octonion conjugate or inversion of the specific subspace phases.
- CPT invariance in COG should be provable as a fundamental algebraic theorem: flipping edge directions (T), swapping left/right multiplication (P), and conjugating the state (C) results in an isomorphic causal graph and update rule.

---

## 4. Proposed Exploratory Lab Tasks

To prevent the lab from getting stuck in the "Koide groove," we recommend injecting the following into the orchestrator backlog:

1. **Path-Interference Simulation Check:** Create a small, simplified graph where a "photon" state splits into two paths of varying depth `D1` and `D2`, then recombines. Log the phase of the result as a function of `|D1 - D2|`. This immediately validates if our update rules naturally produce wave mechanics.
2. **Period-4 Jitter Logging:** In the current mass_drag simulations, trace the raw state of a single electron over 20 ticks. Verify if a literal period-4 or period-8 Zitterbewegung pattern is observable in the raw `ComplexOctonion` components before any time-averaging.
3. **CPT Algebraic Proof:** Formalize the CPT symmetry claim in Lean by proving that the `D4` spawn semantics and `e7` update rule are invariant under the algebraic equivalent of CPT conjugation.

---

## 5. Conclusion

By testing our foundational rules against these broad, universally recognized phenomena, we ensure the COG update rule is structurally sound before demanding that it precisely compute complex empirical values like the muon mass. If the graph cannot produce basic interference or Zitterbewegung, it is not yet ready to solve Koide.