# Discrete Spacetime, Deterministic QM & Graph Dynamics — Literature Survey

**Generated:** 2026-02-21
**Purpose:** Catalog approaches to physics that treat spacetime/dynamics as fundamentally discrete,
deterministic, and graph-based. These are the closest structural cousins to the COG framework.
**Scope:** 't Hooft CA interpretation, Wolfram model, causal fermion systems, spin foam / LQG,
causal set dynamics, and discrete field theory.

---

## 1. 't Hooft — Cellular Automaton Interpretation of Quantum Mechanics

The most important philosophical precedent for COG: a fully deterministic, discrete substructure
that _reproduces_ quantum mechanics as an emergent statistical description.

### CA1. The Cellular Automaton Interpretation of Quantum Mechanics (2014)
- **Author:** Gerard 't Hooft
- **arXiv:** [1405.1548](https://arxiv.org/abs/1405.1548) (quant-ph)
- **Key result:** Comprehensive monograph (book-length). Quantum mechanics is a tool, not a
  fundamental theory. Classical, deterministic models with local degrees of freedom can be
  analysed using quantum techniques. The Standard Model + gravity may be a quantum mechanical
  analysis of a classically deterministic core. The "arrow of time" and vacuum complexity arise
  from the deterministic substrate.
- **Core claim:** For any discrete, deterministic, reversible evolution rule on a countable set
  of ontological states, one can define a Hilbert space and a Hamiltonian such that the quantum
  evolution reproduces the deterministic one. The quantum superpositions are emergent — they
  encode statistical correlations over equivalence classes of ontological histories.
- **Relevance to COG:** Direct philosophical backing for the Prime Directive. COG's deterministic
  DAG evolution is exactly the kind of substrate 't Hooft envisions. The "tick = forced evaluation"
  mechanism maps onto 't Hooft's distinction between beables (ontological states) and superpositions
  (epistemic covers). The key challenge 't Hooft identifies — getting a bounded-below Hamiltonian —
  may correspond to COG's non-associativity enforcing a causal order.

### CA2. Determinism beneath Quantum Mechanics (2002)
- **Author:** Gerard 't Hooft
- **arXiv:** [quant-ph/0212095](https://arxiv.org/abs/quant-ph/0212095)
- **Key result:** Early paper establishing the framework. A deterministic theory with information
  loss at the Planck scale can reproduce quantum statistics. Non-locality in Bell inequality
  experiments is compatible with "superdeterminism" if the ontological and quantum bases are
  non-trivially related.
- **Relevance to COG:** Provides justification for why COG's deterministic microstate evolution
  can be compatible with the apparent non-determinism of quantum measurement.

### CA3. Duality between a deterministic cellular automaton and a bosonic QFT in 1+1 dimensions (2012)
- **Author:** Gerard 't Hooft
- **arXiv:** [1205.4107](https://arxiv.org/abs/1205.4107) (quant-ph, hep-th)
- **Key result:** Explicit exact correspondence between a 1+1D deterministic cellular automaton
  and a bosonic quantum field theory. The automaton consists of left-movers and right-movers;
  the QFT emerges from this structure. Demonstrates concretely how QFT can be "dual" to a
  purely deterministic discrete model.
- **Relevance to COG:** Provides the simplest worked example of the CA ↔ QFT duality. Useful
  template for how COG's DAG evolution might reproduce perturbative QFT in the continuum limit.

### CA4. Cellular automaton ontology, bits, qubits, and the Dirac equation (2024)
- **Author:** Hans-Thomas Elze
- **arXiv:** [2401.08253](https://arxiv.org/abs/2401.08253) (quant-ph, nlin.CG)
- **Key result:** Constructs a "necklace of necklaces" discrete deterministic automaton whose
  continuum limit reproduces the 1+1D Dirac equation. A classical Ising spin chain is shown to
  relate to the Weyl equation. Small deformations of the discrete model generate quantum
  superpositions (qubits). Mass terms arise from the structure of the discrete model, not from
  a Higgs field.
- **Relevance to COG:** Most directly relevant to COG's mass mechanism. The "mass = tick
  frequency" hypothesis is the COG analog of Elze's observation that mass terms come from the
  discrete structure itself.

---

## 2. Wolfram Model — Hypergraph Rewriting as Fundamental Physics

The Wolfram Model replaces spacetime with a hypergraph whose evolution is governed by local
substitution rules. The causal graph of the evolution is the conformal structure of spacetime.
COG's DAG is structurally similar but carries octonionic node data and has a fixed algebraic
update rule rather than an abstract rewriting rule.

### WM1. Some Relativistic and Gravitational Properties of the Wolfram Model (2020)
- **Author:** Jonathan Gorard
- **arXiv:** [2004.14810](https://arxiv.org/abs/2004.14810) (cs.DM, gr-qc)
- **Key result:** Rigorous derivations proving that large classes of Wolfram model hypergraph
  rewriting systems obey discrete special and general relativity in the continuum limit.
  **Causal invariance** (all causal graphs isomorphic regardless of update order) is proven to be
  equivalent to a discrete form of general covariance. Discrete Riemann and Ricci curvature for
  hypergraphs are defined, and the constraint on the discrete Ricci tensor corresponds to the
  Einstein field equations.
- **Relevance to COG:** Proves that causal invariance is equivalent to Lorentz covariance. If COG's
  step function is causally invariant (i.e., the DAG is the same regardless of which non-associative
  tick is processed first — the confluence property in `RaceCondition.lean`), then Lorentz covariance
  is automatically satisfied.

### WM2. Algorithmic Causal Sets and the Wolfram Model (2020)
- **Author:** Jonathan Gorard
- **arXiv:** [2011.12174](https://arxiv.org/abs/2011.12174) (gr-qc, cs.DM)
- **Key result:** The Wolfram model provides an _algorithmic dynamics_ for causal set evolution.
  Causal invariance of the rewriting system implies conformal invariance of the induced causal
  partial order. Local dimension estimation algorithms for Wolfram systems generalize the
  Myrheim-Meyer estimators for causal sets. The Benincasa-Dowker action (causal set action) is
  recovered as a special case of the discrete Einstein-Hilbert action over Wolfram systems.
- **Relevance to COG:** Bridges the Wolfram model and causal set theory, showing they are
  complementary. COG's DAG is a causal set (Section CS* of `furey_and_related_literature.md`);
  this paper shows how to derive its dynamics algorithmically from local rules.

### WM3. Hypergraph Discretization of the Cauchy Problem in GR via Wolfram Model Evolution (2021)
- **Author:** Jonathan Gorard
- **arXiv:** [2102.09363](https://arxiv.org/abs/2102.09363) (gr-qc)
- **Key result:** Wolfram model evolution with hypergraph initial data recovers the CCZ4
  formulation of the Cauchy problem for the Einstein equations. Adaptive mesh refinement is
  implemented by refining/coarsening the hypergraph topology. Validated against Schwarzschild,
  Kerr, and binary black hole mergers.
- **Relevance to COG:** Demonstrates that discrete hypergraph evolution can reproduce continuous
  GR to high precision. Directly relevant to COG's Phase 5 attack vector: proving that the
  discrete DAG recovers Lorentzian geometry in the appropriate limit.

### WM4. Pregeometric Spaces from Wolfram Model Rewriting Systems as Homotopy Types (2021)
- **Authors:** Xerxes Arsiwalla, Jonathan Gorard
- **arXiv:** [2111.03460](https://arxiv.org/abs/2111.03460) (math.CT, cs.LO, gr-qc, hep-th)
- **Key result:** Wolfram model multiway rewriting systems can be interpreted as homotopy types.
  Spatial structures are inherited functorially from pregeometric type-theoretic constructions.
  The $n \to \infty$ limit of the multiway system is an $\infty$-groupoid (Grothendieck's homotopy
  hypothesis). The classifying space of multiway systems is an $(\infty,1)$-topos.
- **Relevance to COG:** Provides the highest-level mathematical context for COG's DAG. The
  homotopy type perspective is relevant to the question of how continuous topology emerges from
  discrete causal structure. Also relevant to COG's Lean formalization: homotopy type theory
  is the foundation of modern proof assistants.

---

## 3. Causal Set Theory — Sequential Growth Dynamics

Causal sets are the most developed discrete spacetime approach. COG's DAG is a causal set
with extra algebraic structure (octonionic node data).

### CS_RS1. A Classical Sequential Growth Dynamics for Causal Sets (1999)
- **Authors:** David Rideout, Rafael Sorkin
- **arXiv:** [gr-qc/9904062](https://arxiv.org/abs/gr-qc/9904062) (gr-qc, hep-th)
- **Key result:** Starting from causality conditions and discrete general covariance, derives a
  very general family of classically stochastic sequential growth dynamics for causal sets. Key
  point: matter can arise **dynamically from the causal set** without being built in at the
  fundamental level (via Ising spin correlations on the relations). The discrete covariance
  condition alone severely restricts the allowed dynamics.
- **Relevance to COG:** This is the most important causal set dynamics paper for COG. The
  "matter arises dynamically from the causal structure" result is the causal set analog of COG's
  claim that gauge bosons and fermions emerge from the algebraic update rules on the DAG nodes.
  The Ising spins on relations correspond to COG's edge labels (U1, SU2, SU3).

### CS_RS2. Evidence for a Continuum Limit in Causal Set Dynamics (2000)
- **Authors:** David Rideout, Rafael Sorkin
- **arXiv:** [gr-qc/0003117](https://arxiv.org/abs/gr-qc/0003117) (gr-qc, hep-lat)
- **Key result:** A particularly simple causal set sequential growth model (equivalent to 1D
  directed percolation) shows evidence for a continuum limit as the coupling parameter is varied.
  The model is easy to simulate on a computer.
- **Relevance to COG:** Provides a concrete example of how discrete causal evolution can
  produce a continuum limit. The percolation model's simplicity makes it a useful comparison
  point for COG's graph engine.

### CS_S1. Scalar Field Theory on a Causal Set in Histories Form (2011)
- **Author:** Rafael Sorkin
- **arXiv:** [1107.0698](https://arxiv.org/abs/1107.0698) (gr-qc, hep-th)
- **Key result:** Recasts a quantum scalar field on a background causal set into a
  histories-based (path integral) form. The discrete d'Alembertian is a generalized inverse
  of the retarded Green function. Outlines how to include interactions.
- **Relevance to COG:** Provides the field theory infrastructure needed for Phase 4 (matter
  fields on the COG causal graph). The discrete d'Alembertian construction is directly relevant
  to how propagators should be defined on the COG DAG.

---

## 4. Causal Fermion Systems (Finster et al.)

Causal fermion systems (CFS) provide a unified framework where spacetime geometry, matter,
and gauge interactions all emerge from a single variational principle (the causal action).
The CFS-octonion connection (G9 in `furey_and_related_literature.md`) is particularly relevant.

### CFS1. The Continuum Limit of Causal Fermion Systems (2016) [MONOGRAPH]
- **Author:** Felix Finster
- **arXiv:** [1605.04742](https://arxiv.org/abs/1605.04742) (math-ph, gr-qc, hep-th)
- **Key result:** Full mathematical monograph. CFS yields quantum mechanics, general relativity,
  and QFT as limiting cases. Spacetime points are represented by operators on a Hilbert space;
  the causal action principle determines the dynamics. The SM + gravity Lagrangian emerges at
  the level of second-quantized fermionic fields coupled to classical bosonic fields.
- **Relevance to COG:** The CFS causal action is the continuous-limit analog of COG's discrete
  update rule. Reading this monograph provides the mathematical framework within which COG's
  discrete dynamics should converge in the large-graph limit. The recovery of SM + gravity from
  pure algebraic/causal principles is the strongest existence proof that this program can work.

### CFS2. Causal Fermion Systems and Octonions (2024)
- **Authors:** Finster, Gresnigt, Isidro, Marciano, Paganini, Singh
- **arXiv:** [2403.00360](https://arxiv.org/abs/2403.00360) (math-ph, hep-th)
- **Key result:** Octonions and division algebra tensor products arise naturally in the symmetries
  of the CFS vacuum configuration. The real/imaginary octonion basis elements are associated with
  the neutrino/charged sectors of the fermionic projector. Conversely, CFS provides octonionic
  theories with spacetime structures and dynamical equations via the causal action principle.
- **Relevance to COG:** **CRITICAL BRIDGE PAPER.** Explicitly connects the octonionic algebraic
  program (Furey, Dixon, Gresnigt) with the causal structure program (Finster). Shows that these
  are not competing but complementary approaches: algebra provides the node data, causal structure
  provides the dynamics. This is exactly the COG architecture.

### CFS3. Causal Fermion Systems: Classical Gravity and Beyond (2021)
- **Author:** Felix Finster
- **arXiv:** [2109.05906](https://arxiv.org/abs/2109.05906) (gr-qc, math-ph)
- **Key result:** Short review of how the causal action principle gives rise to classical gravity
  and the Einstein equations. Also covers a positive mass theorem for static CFS, a connection
  between area change and matter flux, and construction of a quantum state.
- **Relevance to COG:** Mass in CFS is connected to area change and matter flux — an independent
  route to mass-as-structural-property that may inform COG's tick-frequency mass definition.

### CFS4. Causal Fermion Systems: Spacetime as the Web of Correlations (2025)
- **Authors:** Patrick Fischer, Claudio Paganini
- **arXiv:** [2504.19272](https://arxiv.org/abs/2504.19272) (math-ph)
- **Key result:** Argues that spacetime in CFS is best understood as the web of correlations
  of a many-body quantum system — a completely relational theory. In the $N \to \infty$ limit
  of states, macroscopic spacetime emerges from the relational structure. The causal action
  minimizes fluctuations in the causal structure.
- **Relevance to COG:** Provides the conceptual framework for how COG's discrete, relational
  DAG (which has no background geometry) gives rise to apparent spacetime at large scales.

### CFS5. Introduction to Causal Fermion Systems (2021)
- **Author:** Christoph Langer
- **arXiv:** [2111.07405](https://arxiv.org/abs/2111.07405) (math-ph)
- **Key result:** Pedagogical introduction to CFS: fermionic projector principle, causal action
  principle, main structures.
- **Relevance to COG:** Accessible entry point to CFS before reading the Finster monograph.

---

## 5. Spin Foam Models & Loop Quantum Gravity

Spin foam models are the main alternative to causal set theory for discrete spacetime. They
discretize spacetime into a 2-complex (dual to a triangulation) and assign algebraic data
(representations and intertwiners) to faces and edges. Matter fields can be added as
excitations of the foam.

### LQG1. The Spin-Foam Representation of Loop Quantum Gravity (2006)
- **Author:** Alejandro Perez
- **arXiv:** [gr-qc/0601095](https://arxiv.org/abs/gr-qc/0601095)
- **Key result:** Review of spin foam models as the path integral representation of LQG.
  In 2+1D, the spin foam representation is mathematically rigorous. In 4D, the construction
  remains incomplete (regularization dependence). The "geometric meaning" of spin foam histories
  is clarified.
- **Relevance to COG:** Provides context: LQG/spin foam is the established competitor to
  COG's approach. Key question for COG: how does octonionic node data relate to the $SU(2)$
  representation labels on spin foam faces? The exceptional group $G_2 = \text{Aut}(\mathbb{O})$
  appearing in LQG-octonionic bridges would be relevant.

### LQG2. Coarse Graining Spin Foam Quantum Gravity — A Review (2020)
- **Author:** Sebastian Steinhaus
- **arXiv:** [2007.01315](https://arxiv.org/abs/2007.01315) (gr-qc, hep-th)
- **Key result:** Review of renormalization group methods for spin foam QG. Coarse graining
  in background-independent settings, tensor network renormalization applied to spin foams,
  restoration of diffeomorphism symmetry via RG flow.
- **Relevance to COG:** The coarse-graining question is exactly what COG faces in Phase 5:
  how do many discrete DAG steps produce effective continuous physics? The RG methods developed
  for spin foams may be applicable to COG.

### LQG3. Loop Quantum Gravity and Quantum Information (2023)
- **Authors:** Eugenio Bianchi, Etera Livine
- **arXiv:** [2302.05922](https://arxiv.org/abs/2302.05922) (gr-qc)
- **Key result:** Entanglement entropy of spin-network states, link/intertwiner/boundary
  entanglement. Area-law states encode semiclassical geometry. Geometric entanglement entropy
  as a probe of semiclassicality.
- **Relevance to COG:** The entanglement structure of spin networks is the LQG analog of COG's
  edge structure. The area-law / volume-law distinction may correspond to whether the COG DAG
  encodes a locally flat or curved geometry.

---

## 6. Discrete Field Theory on Causal Graphs

### DFT1. Non-Associative Geometry and the Spectral Action Principle (2013)
- **Authors:** Shane Farnsworth, Latham Boyle
- **arXiv:** [1303.1782](https://arxiv.org/abs/1303.1782) (hep-th)
- **(See also B3 in `furey_and_related_literature.md`)**
- **Key result:** The spectral action principle extended to non-associative geometries. The
  simplest example (octonions) gives Einstein gravity + $G_2$ gauge theory + 8 Dirac fermions.
  Non-associativity introduces a "Jacobiator" term that modifies the action.
- **Relevance to COG:** This is the closest existing work to COG's core claim. The non-associative
  Jacobiator = COG's non-associative tick overhead. The $G_2$ gauge theory from octonions is
  the gauge group generated by left-multiplication by $e_i$, which Todorov identifies with the
  SM gauge group precursor.

### DFT2. Star Products Made (Somewhat) Easier (2016)
- **Authors:** Vladislav Kupriyanov, Richard Szabo
- **arXiv:** [1601.03607](https://arxiv.org/abs/1601.03607) (hep-th, math-ph)
- **Key result:** Explicit star products for non-associative phase spaces using alternative
  (Moufang) algebras. Non-associativity leads to modified uncertainty relations and
  non-trivial "Jacobiator" terms. Alternative identity = minimal weakening of associativity
  that still permits a consistent star product.
- **Relevance to COG:** Technical framework for understanding how non-associative operations
  at graph nodes create irreducible computational overhead. The Jacobiator in star products
  is the symbol-calculus analog of COG's associator $[a,b,c] = (ab)c - a(bc)$.

---

## Cross-Reference: Relation to COG Architecture

| COG component | Closest literature analog |
|---|---|
| DAG as causal structure | Causal set theory (CS*), Wolfram model (WM*) |
| Octonionic node data | Furey/Gresnigt/Todorov program (see `furey_and_related_literature.md`) |
| CFS bridge (algebra + causality) | Finster-Gresnigt et al. CFS2 |
| Tick = non-associative overhead | 't Hooft CA (CA1-CA4), Elze CA4 |
| Causal invariance ↔ Lorentz covariance | Wolfram model WM1 |
| Discrete → continuum limit | Wolfram WM1-WM3, Rideout-Sorkin CS_RS2 |
| Gauge group from causal structure | Rideout-Sorkin CS_RS1 (matter from causal order) |
| Mass from discrete structure | Elze CA4 (mass from discrete automaton) |
| Star product / quantum limit | Kupriyanov-Szabo DFT2 |

---

## Priority Reading for COG Phase 5 (Continuum Limit)

1. **WM1** (Gorard): Causal invariance = general covariance — read this before implementing `RaceCondition.lean`
2. **CA1** ('t Hooft): Full monograph — philosophical backbone of the entire project
3. **CFS1** (Finster): Full monograph — mathematical target that COG should converge to
4. **CFS2** (Finster+Gresnigt): Bridge paper — shows CFS + octonions = COG's architecture
5. **CS_RS1** (Rideout-Sorkin): Sequential growth dynamics — template for COG's `Update.lean`
