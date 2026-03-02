# Cellular Automata on S960 and Emergent Lorentz Invariance: A Literature Survey

**Date:** 2026-03-02
**Scope:** Comprehensive literature review covering:
1. Whether cellular automata on S960 (or equivalent octavian/Moufang-loop state spaces) have been studied before
2. How emergent Lorentz invariance is achieved in discrete/CA models, and what setup it requires
3. Related phenomena: QCA and Weyl/Dirac equations, octonions in discrete physics, causal set Lorentz invariance, 't Hooft deterministic CA

---

## 1. Executive Summary

**S960-specific CA: no prior literature found.**
After broad arXiv searches covering hep-th, math-ph, gr-qc, quant-ph, nlin.CG, and cs.DM, no paper studying cellular automata (deterministic or quantum) on the S960 state space — or any structurally similar object (Moufang loop CA, octavian-integer-valued CA, non-associative-algebra CA) — was found. The COG framework is exploring genuinely novel territory.

**Emergent Lorentz invariance from discrete systems is well-studied**, but requires specific structural properties. There are three major known mechanisms:

1. **Random sprinkling (Causal Sets):** Bombelli-Henson-Sorkin theorem (2006): a Poisson-random sprinkling of points into Minkowski space provably breaks no preferred direction. Lorentz invariance comes *for free* from randomness. The catch: S960 is highly structured and deterministic, so this mechanism does NOT apply directly.

2. **Causal invariance (Wolfram/Gorard):** If all orderings of local update rules produce isomorphic causal graphs (confluence/Church-Rosser property), then Lorentz covariance emerges from the requirement that all physical observers see the same causal partial order. This potentially applies to S960 if the branching protocol satisfies confluence.

3. **Quantum Walk / QCA covariance (Arrighi et al.):** Specific quantum cellular automata can be made exactly Lorentz-covariant at the discrete level ("Clock QCA"), and a large class of massless QCAs automatically satisfies the Weyl equation in the continuum limit (Farrelly-Short theorem). This is the mechanism most directly relevant to the photon and neutrino sectors of S960.

**Key COG-specific insight (Section 6):** The S960 branching protocol — which forks the DAG into two causal branches whenever `s_L = -s_R` — may be interpreted as a discrete implementation of causal invariance. If both branches eventually produce equivalent macroscopic observables (even though they differ in sign), the system is effectively causal-invariant, and Lorentz covariance should emerge for macroscopic motifs.

---

## 2. Negative Result: No Prior S960 / Octavian CA Literature

### 2.1 Why S960 Is Novel

S960 is defined as:

```
S960 = M_240 x Z_4 = { zeta * v : v in M_240, zeta in {1,i,-1,-i} }
```

where M_240 is the set of 240 Coxeter integral octonion units ("octavians" or "Cayley integers" — the unit sphere of the maximal integral domain of the octonions). This is a specific, highly structured 960-element algebraic object.

A search of the literature reveals:

- **No papers** on cellular automata with states drawn from M_240 or S960.
- **No papers** on CA with non-associative algebraic state spaces (Moufang loops, alternative algebras, octonion-valued spins).
- **Sparse literature** on CA with group-valued states (cyclic groups Z_n, finite abelian groups) — these are associative and structurally different.
- **No papers** on dynamics on M_240 as a dynamical system at all, beyond its use as a fixed lattice in number theory (E8 root system, Leech lattice constructions).

This gap is likely because:
1. The octonions are non-associative, making standard CA theory (which implicitly assumes associative composition of state transitions) inapplicable.
2. The size of S960 (960 elements) makes naive enumeration non-trivial but not intractable.
3. The physical motivation (octonion-based Standard Model derivation) is recent (Furey 2014+).

### 2.2 Related But Distinct Literature

The closest related structures that HAVE been studied:

- **E8 lattice dynamics** (Dixon 1994, hep-th/9411063): The octonion X-product is related to E8 lattice operations. Dixon explicitly connects the X-product (a specific non-associative product on octonion units) to E8 lattice geometry and sphere fibrations. However, this is algebraic-geometric, not dynamical.

- **Octonion X-product and G2 actions** (da Rocha and Vaz 2006, math-ph/0603053): The Clifford-parametrized octonionic X-product connects to parallelizing torsion on S7, triality maps, and G2 symmetry. No CA dynamics.

- **Cl(6) left ideal dynamics** (Furey 2014-2025): Left-multiplication operators on the Clifford envelope Cl(6) of the octonions produce a 4-dimensional minimal left ideal with SM quantum numbers. The update rules in RFC-001 are closer to this than to any known CA framework.

---

## 3. Emergent Lorentz Invariance: Mechanism 1 — Causal Sets (Poisson Sprinkling)

### 3.1 The Core Result

Dowker, Henson, and Sorkin (2003, gr-qc/0311055) established what is now the canonical result in the field:

> **A fundamental spacetime discreteness need NOT contradict Lorentz invariance.**
> A causal set's discreteness is locally Lorentz invariant, for the following reason: the
> elements of a causal set are placed by a Poisson-random process (a "sprinkling") into
> Minkowski space. Any Lorentz transformation of the background Minkowski space is absorbed
> into a permutation of the points. There is no preferred frame.

This was strengthened by Bombelli, Henson, and Sorkin (2006, gr-qc/0605006) into a formal theorem:

> **Theorem (Bombelli-Henson-Sorkin 2006):** There exists no equivariant measurable map
> from sprinklings into Minkowski space to spacetime directions, even locally.
> Therefore, a discrete structure associated to a sprinkling in an intrinsic manner will
> NOT pick out a preferred frame, locally or globally.

The implication: no modified dispersion relation, no preferred spatial direction, no preferred reference frame arises from the discreteness alone — provided the discreteness comes from Poisson sprinkling.

### 3.2 What Setup Is Required

The Poisson-sprinkling route to Lorentz invariance requires:
1. **Randomness:** The discrete points are placed by a fundamentally random (Poisson) process.
2. **No structure:** No additional geometric structure (like a lattice) is imposed.
3. **Lorentz invariance of the background:** The background Minkowski space admits the Lorentz group as a symmetry.

### 3.3 Limitation for COG

S960 is NOT random. It is a fixed, highly symmetric algebraic structure (a Moufang loop). The Bombelli-Henson-Sorkin theorem does not apply.

Kent (2018, arXiv:1803.11484) raises a subtle further point: even for random sprinklings, "full" Poincare invariance of the resulting theory is delicate — any pair of timelike-separated events can define a preferred spacelike direction for a typical sprinkling, partially breaking rotational invariance. Genuinely testing Poincare invariance in these models is non-trivial.

The COG framework needs a different mechanism.

---

## 4. Emergent Lorentz Invariance: Mechanism 2 — Causal Invariance (Wolfram/Gorard)

### 4.1 Causal Invariance as Discrete General Covariance

Gorard (2020, arXiv:2004.14810) proved within the Wolfram model framework:

> **Theorem (Gorard 2020):** Causal invariance — the requirement that all causal graphs be
> isomorphic irrespective of the choice of hypergraph updating order — is equivalent to a
> discrete version of general covariance, with changes to updating order corresponding to
> discrete gauge transformations. This implies a discrete analog of Lorentz covariance.

The key concept is **confluence** (the Church-Rosser / diamond property): if two sequences of local updates both terminate, they reach the same macroscopic state. This is standard in term-rewriting theory.

Gorard further shows (in the same paper) that the correction factor for the volume of a discrete spacetime cone in the causal graph corresponds to a timelike projection of a discrete Ricci tensor, and that the Einstein field equations emerge from requiring that the updating rules preserve causal graph dimensionality.

The companion paper (2011.12174) shows that causal invariance of the Wolfram model implies conformal invariance of the causal partial order, in a way compatible with the measure-theoretic arguments of Bombelli, Henson, and Sorkin.

### 4.2 What Setup Is Required

The causal invariance route requires:
1. **Local update rules** that act on small neighborhoods (matching the COG 3-body product rule).
2. **Confluence:** All update orderings produce isomorphic causal graphs at the macroscopic level.
3. **No external background:** The causal graph IS spacetime, not embedded in it.

### 4.3 Applicability to COG

The COG branching protocol (RFC-001 §3.3) does something structurally related to causal invariance:
- When `s_L = -s_R`, the DAG spawns BOTH branches.
- Both branches are retained in the DAG — the universe "remembers" both causal futures.
- The final macroscopic motif is defined over the ensemble of all branches.

If the macro-observable (the period-T replay hash of a motif) is the same across both branches, then the system satisfies a weak version of causal invariance: different update orderings (left-first vs right-first) agree on macroscopic properties.

**Key open question for COG:** Is the S960 update rule confluent at the macro-motif level? This is a falsifiable computational test.

---

## 5. Emergent Lorentz Invariance: Mechanism 3 — Quantum Walks and QCA

### 5.1 The Farrelly-Short Theorem (Causal Fermions)

The most directly applicable result for the COG photon/neutrino morphology question is by Farrelly and Short (2013, arXiv:1303.4652):

> **Theorem (Farrelly-Short 2013):** Any fermionic system in discrete spacetime evolving
> causally (unitary, bounded propagation speed) can be viewed as a quantum cellular automaton.
> In the continuum limit:
> - A massless 2D-internal-DoF causal fermion → Weyl equation.
> - A 4D-internal-DoF causal fermion → Dirac equation (massive or massless).
> - The Thirring model (interacting) can be recovered similarly.

The companion paper (arXiv:1312.2852, 2014) by the same authors gives the massless uniqueness theorem used in our `s960_particle_morphology_search.md`.

This is a *universality* result: the Weyl/Dirac equations are the unique continuum limits of the most general causal discrete fermionic dynamics. No specific lattice structure is assumed.

### 5.2 The Arrighi Program

Pablo Arrighi and collaborators have developed this into an extensive program:

**Arrighi, Forets, Nesme (2013, arXiv:1307.3524):** The standard Dirac QW (proposed independently by Succi-Benzi, Bialynicki-Birula, and Meyer) is derived in all dimensions for hyperbolic symmetric systems. For any time t, the model converges to the continuous Dirac solution with discrepancy O(eps^2). This is the key quantitative convergence result.

**Arrighi, Facchini, Forets (2014, arXiv:1404.4499):** Formalizes discrete Lorentz transforms for QWs and QCA in 1+1D. Shows:
- The standard Dirac QW is Lorentz-covariant at first order only.
- The "Clock QW" and "Clock QCA" (introduced in this paper) are exactly Lorentz-covariant.
- Non-homogeneous (non-inertial) Lorentz transforms are also handled.

**Arrighi et al. (2018, arXiv:1803.01015):** The Dirac equation in 2+1D can be simulated on any lattice (square, honeycomb, triangular). The discretization is lattice-topology-independent, only requiring locality and unitarity.

**Arrighi et al. (2024, arXiv:2404.09840):** The Dirac equation in 3+1D from a QW on tetrahedra (simplicial lattice). This "paves the way to simulate Dirac on curved spacetime" and "suggests an ordered scheme for propagating matter over a spin network, of interest in Loop Quantum Gravity."

**Arrighi et al. (2018, arXiv:1802.07644):** A gauge-invariant reversible CA. Provides discrete counterparts to the main gauge-theory concepts directly in terms of CA. Step-by-step gauging procedure to enforce local symmetries on any given CA.

### 5.3 The Elze Program ('t Hooft's Inheritance)

**'t Hooft (2002, quant-ph/0212095):** Proposed that quantum mechanics could be an emergent phenomenon from deterministic hidden variables at Planck scale. Key insight: information loss in the deterministic system can produce the non-commuting observables of QM as equivalence classes.

**'t Hooft (2012, arXiv:1205.4107):** Proved duality between a deterministic CA in 1+1D and a bosonic QFT. The CA states map exactly to QFT states. The QFT Hilbert space is the *Koopman-von Neumann* (KvN) space of the CA, not an independently postulated object.

**Blasone, Jizba, Scardigli (2009, arXiv:0901.3907):** Born's rule emerges naturally when 't Hooft's Hamiltonian for "be-ables" is combined with the KvN formulation of classical physics. Born's rule is not postulated — it follows from the deterministic CA structure.

**Elze (2014, arXiv:1403.2646):** Shows that integer-valued CAs with a specific action principle map to bandwidth-limited harmonic oscillators, which in turn give the Schrodinger equation. Linearity of QM traces to the CA action principle.

**Elze (2024, arXiv:2401.08253):** A classical Ising spin chain CA gives the Weyl equation in the continuum limit. When slightly deformed, it unavoidably becomes quantum-mechanical (superpositions form). The "Necklace of Necklaces" automaton recovers the Dirac equation in 1+1D with a mass term.

**Elze (2025, arXiv:2504.06883):** Constructs the full Dirac equation in 1+1D from permutation-based automaton states. Mass enters via a specific scattering operator. The structure requires a torus-like topology ("necklace of necklaces").

### 5.4 What Setup Is Required

For the QCA/QW route to Lorentz covariance:
1. **Unitarity** of the evolution operator (or its deterministic-CA analog: bijective state transitions).
2. **Causality** (bounded propagation speed = no superluminal signaling).
3. **Homogeneity** (translation-invariance and time-independence) — this is satisfied by the COG update rule.
4. For *exact* Lorentz covariance (not just continuum limit): the Clock QCA structure or equivalent.

---

## 6. COG-Specific Analysis: Does S960 Have a Lorentz Invariance Mechanism?

### 6.1 The COG Lorentz Problem

Standard lattice field theories (e.g., Wilson lattice QCD on a hypercubic lattice) break Lorentz invariance explicitly: the hypercubic lattice has only the discrete cubic symmetry group O_h, not the full Lorentz group SO(1,3). Lorentz invariance is recovered only in the continuum limit (a → 0), and corrections are O(a^2).

For the COG causal DAG, the situation is potentially better or worse depending on the structure:

**Potentially better:** The COG graph has no fixed spatial lattice. Nodes are connected by causal edges in a dynamically generated DAG. There is no preferred "up" or "right" direction baked in from a lattice. The graph structure is determined entirely by causal precedence.

**Potentially worse:** The COG state space IS structured (S960 is a specific algebraic object with 7-fold Fano symmetry). The Fano plane's 7-fold symmetry is NOT the continuous SO(3) rotation symmetry. Any emergent "spatial" structure will inherit the Fano plane's discrete symmetry group, which is PGL(2,7) ≅ PSL(2,7) (168 elements) — much smaller than SO(3).

### 6.2 The Branching Protocol as Proto-Causal Invariance

Looking at the RFC-001 branching protocol through the lens of Gorard's causal invariance:

The 3-body interaction `(a, g, b)` produces:
- If Fano triple (associative): one output `s = s_L = s_R` (single branch).
- If non-Fano triple: two outputs `s_L` and `s_R = -s_L` (two branches, both spawned).

The key question is: **are these two branches macroscopically equivalent?**

If a motif is defined by its period-T hash (RFC-043 §7), and if the two branches of any non-Fano interaction produce motifs with the same period-T hash (just with opposite global phases), then:
- The "left update first" and "right update first" orderings produce equivalent macroscopic motifs.
- The system is effectively causal-invariant at the motif level.
- Lorentz covariance should emerge from the same mechanism as in the Wolfram model.

This is a specific, falsifiable prediction. It can be tested computationally: for any motif candidate, run it under "left-first" and "right-first" update orderings and compare the period-T hashes.

### 6.3 The Fano Isotropy Hypothesis

A related question: does the Fano symmetry group PGL(2,7) act isotropically on the COG state space?

The 7 Fano triples are invariant under the 168-element automorphism group of the Fano plane PGL(2,7). If this group acts transitively on the "color" Witt pairs, then no Witt pair direction is distinguished from another. This would give a discrete but isotropic color-space symmetry.

However, PGL(2,7) is not a subgroup of SO(3), so spatial isotropy is not directly implied. The connection between color-space isotropy and spacetime isotropy must be established separately.

A stronger hypothesis: the 7-fold Fano symmetry is the discrete remnant of the G2 symmetry of the octonions. G2 is the automorphism group of the octonions and IS a subgroup of SO(7) (the 7-dimensional rotation group). If spatial 3D directions are somehow embedded in the 7-dimensional Fano space, the G2 symmetry might provide approximate Lorentz invariance at large scales.

This is speculative but is consistent with the Furey/Todorov program, where G2 acts as an approximate spacetime symmetry that is broken by the Witt decomposition into the color SU(3) subgroup.

### 6.4 CDT as a Benchmark

Causal Dynamical Triangulations (CDT, Ambjorn et al. 2011 arXiv:1105.5582) provides a useful benchmark. CDT is a discrete lattice approach to quantum gravity in which:
- Spacetime is triangulated with Lorentzian simplices.
- The triangulation is dynamical (geometry fluctuates).
- Lorentz invariance is imposed via the Lorentzian signature constraint.

CDT recovers de Sitter space (the correct large-scale behavior) and approximately reproduces GR at large scales — but only by explicitly baking in the Lorentzian signature at the smallest scale. CDT does NOT derive Lorentz invariance from scratch; it enforces it as a constraint.

The COG framework, by contrast, aims to derive Lorentz invariance from the octonion non-associativity structure. This is a harder problem and has not been established.

---

## 7. Structurally Related Approaches

### 7.1 Structurally Dynamic Cellular Networks (Requardt)

Requardt and Rastgoo (2015, arXiv:1501.00391) model spacetime as a "structurally dynamic cellular network" — essentially a generalized CA where the network topology itself evolves by CA-like rules. Key features:
- Nodes have discrete states; edge weights change dynamically.
- Continuum GR emerges as a coarse-grained, renormalized limit.
- A geometric renormalization group connects the microscopic CA-like dynamics to the macroscopic metric.
- Phenomena like holography and black hole entropy-area law are emergent.

This is structurally closer to the COG framework than standard regular-lattice CA or QCA, because the graph topology is dynamic. The COG causal DAG grows as new nodes are created by branching events — it is a dynamic graph.

### 7.2 Group Field Theory and Geometrogenesis (Oriti)

Oriti (2013, arXiv:1302.2849) introduces "geometrogenesis": spacetime is a condensate that emerges from a phase transition of pre-geometric discrete quantum space constituents. The Group Field Theory (GFT) formalism provides the pre-geometric theory; GR emerges as its effective low-energy theory.

The connection to COG: the COG vacuum (omega_vac, the e7-sector state) could be the "condensate" from which spacetime geometry emerges. Motifs are topological excitations above the condensate. This is exactly the Vaid/Bilson-Thompson picture discussed in `s960_particle_morphology_search.md`.

### 7.3 Volovik's Fermi-Point Scenario

Volovik (2007, arXiv:0709.1258) proposes that Lorentz invariance emerges from a Fermi-point (topological defect in momentum space) in an underlying Planck-scale medium. The "speed of light" is simply the slope of the Dirac cone at the Fermi point. All low-energy physics (GR, SM) emerge from the topology of the Fermi point.

This is relevant to COG because the Weyl/Dirac equations arise from the minimal QCA motifs (photon, neutrino), and the Fermi point in momentum space corresponds to the massless-limit motif structure. The Lorentz group emerges as the symmetry that preserves the Fermi-point topology, not as a symmetry of the underlying discrete structure.

---

## 8. Octonions in Discrete Physics: Prior Work

### 8.1 Dixon's Octonion X-Product and E8

Dixon (1994, hep-th/9411063) showed that the octonion X-product (defined as `x*y = x×y + [x,y]` where `×` is the standard octonion product and `[x,y]` is the commutator) is directly related to the E8 root lattice and integral domains.

Key result: the X-product generates E8 lattice geometry from the octonion units. Since M_240 IS the E8 root lattice scaled to unit sphere, Dixon's result directly applies: the S960 state space carries E8 structure through its X-product dynamics.

Dixon also notes connections to:
- Sphere fibrations (Hopf fibrations S1 → S3 → S2, S3 → S7 → S4, S7 → S15 → S8)
- Integral domains and division algebra structure
- Octonion parallelizing torsion on S7

### 8.2 Da Rocha and Vaz: Clifford-Parametrized Octonions

Da Rocha and Vaz (2006, math-ph/0603053) connect:
- The octonionic X-product to the parallelizing torsion on S7
- The X-product to G2 actions and triality maps (triality being the key to the three generations of fermions in the Furey framework)
- Hopf fibrations and twistor formalism in 10D
- An "octonionic M-algebra" in D=11 describing M-theory with super-2-branes and super-5-branes

While not directly constructing a CA, this shows that the dynamical X-product on octonion units has rich structure already used in physics.

### 8.3 Wilmot (2025): G2 from Clifford Algebra via Pin(7)

Wilmot (2025, arXiv:2505.06011) constructs G2 and non-associative algebras directly from calibrations using Pin(7), without using the Lie bracket. Key results:
- A subalgebra of Spin(7) enables G2 construction.
- The 4-form calibration terms of Spin(7) are related to an ideal with THREE idempotents.
- The construction works for all 480 representations of the octonions.

The "three idempotents" result is striking: it mirrors Furey's three-generation structure and the three Witt pairs of S960. The 480 representations correspond to the 480 octonion multiplication tables (consistent with the 7 sign choices for the Fano triples, 480 = 2^7 * ... / automorphisms).

---

## 9. The Concrete Setup for Lorentz Invariance Tests in COG

Based on the literature review, the following specific tests would determine whether the COG framework has a viable Lorentz invariance mechanism:

### 9.1 Test A: Macro-Causal Invariance of Motifs

**Protocol:**
1. Select a candidate motif M (k-node seed, e.g., the electron or neutrino candidate).
2. Run the RFC-001 update rule in "left-first" order (always choose s_L when branching).
3. Run the same motif in "right-first" order (always choose s_R when branching).
4. Compare: period T, tick cost C_T, and charge sign between the two orderings.

**Prediction (if causal invariance holds):** T, C_T, and charge sign agree between orderings. The two branches differ only by an overall global phase (-1).

**Significance:** If this test passes for all Standard Model motifs, the Wolfram/Gorard mechanism applies and Lorentz covariance emerges from the causal graph structure.

### 9.2 Test B: Dispersion Relation Check

**Protocol:**
1. Place a "photon motif" (1-node e7-cycling state) at position x=0 at tick t=0.
2. Run the COG update rule for N ticks.
3. Measure the motif's effective position at t=N (from the causal graph topology).
4. Check: is effective_position = N exactly (lightlike propagation) or N - delta for some delta>0?

**Prediction (if Lorentz invariance holds):** delta = 0 for the photon motif. Any delta>0 corresponds to a modified dispersion relation (Lorentz violation).

**Constraint from experiment:** Current bounds from blazar flare observations (Lorentz, Brun 2016, arXiv:1606.08600) constrain the Lorentz violation scale to E_QG > 2.6 * 10^19 GeV for linear perturbations — above the Planck scale. Any COG modified dispersion relation must satisfy this.

### 9.3 Test C: Fano Symmetry and Spatial Isotropy

**Protocol:**
1. Apply each of the 168 automorphisms of the Fano plane (elements of PGL(2,7)) to a test motif.
2. Check: does the update rule commute with the Fano automorphism group?

**Prediction (if Fano isotropy holds):** Yes — the update rule is PGL(2,7)-equivariant.

**Significance:** This would establish that the COG dynamics has a 168-element discrete spatial symmetry. Whether this is sufficient for approximate Lorentz invariance at long wavelengths requires a renormalization group analysis.

---

## 10. Comprehensive Literature Table

### 10.1 Directly Relevant Papers

| arXiv ID | Authors | Year | Title | Relevance |
|----------|---------|------|-------|-----------|
| 1303.4652 | Farrelly, Short | 2013 | Causal Fermions in Discrete Spacetime | KEY: causal fermion = QCA; Dirac/Weyl in continuum limit |
| 1312.2852 | Farrelly, Short | 2014 | Discrete Spacetime and Relativistic Quantum Particles | Massless 2D internal DoF → Weyl (uniqueness theorem) |
| 1404.4499 | Arrighi, Facchini, Forets | 2014 | Discrete Lorentz covariance for QW and QCA | Clock QCA is exactly Lorentz covariant; discrete Lorentz transforms |
| 2004.14810 | Gorard | 2020 | Relativistic and Gravitational Properties of the Wolfram Model | Causal invariance ↔ discrete general covariance → Lorentz covariance |
| 2011.12174 | Gorard | 2020 | Algorithmic Causal Sets and the Wolfram Model | Causal invariance → conformal invariance of causal partial order |
| gr-qc/0311055 | Dowker, Henson, Sorkin | 2003 | QG Phenomenology, Lorentz Invariance and Discreteness | Discreteness does NOT contradict LI if Poisson-random |
| gr-qc/0605006 | Bombelli, Henson, Sorkin | 2006 | Discreteness without symmetry breaking | Theorem: random sprinkling breaks no preferred direction |
| quant-ph/0212095 | 't Hooft | 2002 | Determinism beneath Quantum Mechanics | Deterministic hidden variables at Planck scale → QM |
| 1205.4107 | 't Hooft | 2012 | Duality between deterministic CA and bosonic QFT | Exact CA ↔ QFT duality in 1+1D |
| hep-th/9411063 | Dixon | 1994 | Octonion X-Product and E8 Lattices | Octonionic X-product generates E8 lattice |

### 10.2 Supporting Papers

| arXiv ID | Authors | Year | Title | Relevance |
|----------|---------|------|-------|-----------|
| 1307.3524 | Arrighi, Forets, Nesme | 2013 | Dirac equation as a quantum walk | O(eps^2) convergence of Dirac QW to continuous Dirac |
| 1803.01015 | Arrighi et al. | 2018 | Dirac equation as QW over honeycomb/triangular | Lattice-independent Dirac simulation |
| 2404.09840 | Arrighi et al. | 2024 | Dirac quantum walk on tetrahedra | 3+1D Dirac from QW on spin network (LQG connection) |
| 1802.07644 | Arrighi, Di Molfetta, Eon | 2018 | A gauge-invariant reversible cellular automaton | Discrete gauge theory from CA; step-by-step gauging procedure |
| 2401.08253 | Elze | 2024 | CA ontology, bits, qubits, and the Dirac equation | Ising chain CA → Weyl; "Necklace" → Dirac 1+1D with mass |
| 2504.06883 | Elze | 2025 | The Dirac Equation, Mass and Arithmetic by Permutations | Full Dirac in 1+1D from permutation automaton; mass from scattering op |
| 1403.2646 | Elze | 2014 | Linearity of QM from Hamiltonian cellular automata | QM linearity ← CA action principle; bandwidth-limited oscillators |
| 0901.3907 | Blasone, Jizba, Scardigli | 2009 | Can QM be an emergent phenomenon? | Born's rule emerges from 't Hooft's scheme + KvN formulation |
| 1501.00391 | Requardt, Rastgoo | 2015 | Structurally Dynamic Cellular Network | CA on dynamic graph; geometric RG; continuum/holography emerge |
| 1803.11484 | Kent | 2018 | Are There Testable Discrete Poincare Invariant Theories? | Subtle counterargument: Poincare invariance is very hard to maintain |
| gr-qc/0601121 | Henson | 2006 | The causal set approach to quantum gravity | Review; recovering locality in causal sets |
| 2102.09363 | Gorard | 2021 | Hypergraph Discretization of GR via Wolfram Model | Discrete GR from hypergraph rewriting; validates against Kerr, Schwarzschild |
| math-ph/0603053 | da Rocha, Vaz | 2006 | Clifford algebra-parametrized octonions | X-product, G2, triality, M-theory connection |
| 2505.06011 | Wilmot | 2025 | G2 construction from Clifford algebra using Pin(7) | 3 idempotents from Spin(7) 4-form; all 480 octonion representations |
| 1610.02425 | Song | 2016 | QCA model for the Generalized Dirac Equation | Chiral angle in discrete Dirac → spin polarization observable |
| 1105.5582 | Ambjorn et al. | 2011 | Lattice quantum gravity - CDT update | CDT reproduces de Sitter; Lorentz imposed, not derived |
| 1302.2849 | Oriti | 2013 | Disappearance and emergence of space and time in QG | GFT condensate as spacetime; geometrogenesis |
| 0709.1258 | Volovik | 2007 | Fermi-point scenario for emergent gravity | Lorentz invariance from Fermi-point topology; speed of light = cone slope |
| 1001.4041 | Wallden | 2010 | Causal Sets: QG from fundamentally discrete spacetime | Review |

---

## 11. Open Questions and Implications for the COG Research Program

### 11.1 Critical Unanswered Questions

1. **Is the S960 update rule (RFC-001) macro-causal-invariant?** This is the single most important test. If yes, Lorentz covariance is guaranteed by the Wolfram/Gorard mechanism.

2. **What is the emergent dispersion relation for photon/neutrino motifs?** A linear, isotropic dispersion relation is required for Lorentz invariance. A non-linear or anisotropic one is a Lorentz violation signal.

3. **Is there a continuum limit, and does it have SO(1,3) symmetry?** The Arrighi program shows that many CA systems with discrete symmetry (Z_n lattice) still give exactly SO(1,3)-invariant continuum limits. The Fano symmetry group PGL(2,7) is more exotic — does it also lead to an SO(1,3) continuum limit?

4. **Is the 7-state S960 model equivalent to a QCA?** The COG update rule is not unitary in the standard sense (it involves sign-branching, not complex-amplitude evolution). But if the two branches correspond to complex amplitudes `+1` and `-1` (as suggested by `s_L = -s_R`), then the branching protocol is exactly a `{+1,-1}` quantum superposition — a 1-qubit QCA per interaction. This would put COG squarely in the Farrelly-Short / Arrighi framework.

5. **Does the non-associativity of S960 serve as the source of causal invariance violation (or preservation)?** Non-associativity is the source of branching. If the two branches correspond to "all left-associated" vs "all right-associated" update paths, and if these are always macroscopically equivalent (causal invariant), then non-associativity is GENERATING causal invariance rather than violating it. This would be a novel mechanism not present in any prior framework.

### 11.2 The Most Important Positive Finding

The literature establishes a clear, actionable path:

> The COG framework can inherit Lorentz invariance via the same mechanism as the
> Wolfram/Gorard Causal Invariance route — IF the S960 update rule is confluent
> (macro-causal-invariant) at the motif level.

The RFC-001 branching protocol's structure — spawning both s_L and s_R branches rather than choosing one — is *exactly* the structure required for causal invariance. Both orderings (left-first, right-first) are simultaneously present in the DAG. The DAG itself is the "multiway" system of the Wolfram model. If all branches converge to the same macroscopic motif, Lorentz invariance is free.

### 11.3 The Critical Negative Warning

The literature also contains a stark warning from Kent (2018): genuinely testing Poincare invariance in models with fundamental discreteness is extremely subtle. Even Poisson-random sprinklings have broken symmetries that emerge when specific reference points are fixed. For a highly structured model like S960, this is likely a more serious concern.

Any experimental prediction of the COG framework that involves Lorentz invariance — especially at the Planck scale (where experimental tests from Lorentz et al. 2016, H.E.S.S. blazar constraints are available) — must explicitly verify the dispersion relation emerging from the motif dynamics. The current experimental bound E_QG > 2.6 × 10^19 GeV (above Planck scale, arXiv:1606.08600) strongly constrains any modified photon dispersion.

---

## 12. Conclusion

The COG framework with the S960 state space is genuinely novel — no prior work has studied CA dynamics on this specific algebraic object, or on any comparable non-associative/Moufang-loop state space.

The emergent Lorentz invariance question has three known resolution routes in the literature:
1. Poisson randomness (causal sets) — does NOT apply to S960.
2. Causal invariance (Wolfram model) — POTENTIALLY applies if the RFC-001 update rule is confluent.
3. QCA Lorentz covariance (Arrighi / Farrelly-Short) — APPLIES to the photon and neutrino sectors if their motifs are massless 2D-internal-DoF systems.

The most urgent computational test is the macro-causal-invariance test (Section 9.1): run photon and neutrino candidate motifs under "left-first" and "right-first" update orderings and compare macroscopic observables. A passing result would establish Lorentz covariance of the photon sector with no further work.

A failing result would mean the COG framework has a fundamental Lorentz violation at the Planck scale — not necessarily a fatal problem (LIV is constrained but not ruled out at the Planck scale), but one that would need to be quantified and compared against the H.E.S.S. bounds.

*Evidence level: `hypothesis` (literature-supported analysis; no computational verification yet).*
