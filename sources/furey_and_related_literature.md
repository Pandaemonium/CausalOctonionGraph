# Division Algebras & the Standard Model — Comprehensive Literature Survey

**Generated:** 2026-02-21
**Purpose:** Catalog the works of Cohl Furey and closely related researchers for eventual Lean formalization.
**Scope:** Papers deriving Standard Model structure from normed division algebras ($\mathbb{R}, \mathbb{C}, \mathbb{H}, \mathbb{O}$), Clifford algebras, and related discrete algebraic frameworks.

---

## 1. Cohl Furey — Core Papers

These are the primary works to formalize. They form a logical sequence building from $\mathbb{C}\ell(6)$ to the full $\mathbb{R} \otimes \mathbb{C} \otimes \mathbb{H} \otimes \mathbb{O}$ framework.

### F1. Generations: Three Prints, in Colour (2014)
- **arXiv:** [1405.4601](https://arxiv.org/abs/1405.4601) (hep-th)
- **Key result:** The complex octonions $\mathbb{C} \otimes \mathbb{O}$ generate a 64-$\mathbb{C}$-dimensional Clifford algebra $\mathbb{C}\ell(6)$. Within it, $SU(3)$ generators partition the space into six triplets, six singlets, and their antiparticles — exactly three generations of SM fermion color structure. Particle ↔ antiparticle is simply $i \mapsto -i$.
- **Lean target:** Define $\mathbb{C}\ell(6)$ from complex octonions; prove the $SU(3)_C$ representation decomposition.

### F2. $SU(3)_C \times SU(2)_L \times U(1)_Y (\times U(1)_X)$ as a symmetry of division algebraic ladder operators (2018)
- **arXiv:** [1806.00612](https://arxiv.org/abs/1806.00612) (hep-th, hep-ph, math-ph)
- **Key result:** Ladder operators constructed from $\mathbb{R}, \mathbb{C}, \mathbb{H}, \mathbb{O}$ carry $SU(n)$ symmetries. Their combined structure yields $G_{SM} = SU(3)_C \times SU(2)_L \times U(1)_Y / \mathbb{Z}_6$, structurally similar to Georgi-Glashow $SU(5)$ but with proton decay blocked because transformations that mix distinct algebraic actions are forbidden. An extra $U(1)_X$ related to $B - L$ may also be present.
- **Lean target:** Formalize the ladder operator construction; prove the $\mathbb{Z}_6$ quotient; prove proton decay transitions are algebraically blocked.

### F3. Three generations, two unbroken gauge symmetries, and one eight-dimensional algebra (2019)
- **arXiv:** [1910.08395](https://arxiv.org/abs/1910.08395) (hep-th, hep-ph, math-ph)
- **Key result:** Extends F1 by incorporating electric charge. An $su(3) \oplus u(1)$ action on the 64-$\mathbb{C}$-dimensional space splits it into $SU(3)$ generators + 48 states = exactly three generations of quarks and leptons under $SU(3)_C \times U(1)_{EM}$. Outlines how the full SM state space might live inside the left action maps of $\mathbb{R} \otimes \mathbb{C} \otimes \mathbb{H} \otimes \mathbb{O} \cong \mathbb{C}\ell(8)$.
- **Lean target:** Prove the 48-state decomposition under $su(3) \oplus u(1)$.

---

## 2. Furey & Hughes — Joint Papers

These extend the single-generation results to the full SM with symmetry breaking and three generations.

### FH1. One generation of standard model Weyl representations as a single copy of $\mathbb{R} \otimes \mathbb{C} \otimes \mathbb{H} \otimes \mathbb{O}$ (2022)
- **arXiv:** [2209.13016](https://arxiv.org/abs/2209.13016) (hep-ph, hep-th)
- **Key result:** Solves the long-standing **fermion doubling problem**. A single 32-$\mathbb{C}$-dimensional copy of $\mathbb{A} = \mathbb{R} \otimes \mathbb{C} \otimes \mathbb{H} \otimes \mathbb{O}$ suffices to describe $g_{SM}$, its gauge bosons, the Higgs, and one generation of fermions. The subalgebra invariant under complex conjugation is $su(3)_C \oplus u(1)_{EM}$, potentially explaining *why* the SM symmetries break as observed.
- **Lean target:** Formalize $\mathbb{A}$; prove the fermion doubling resolution; prove the complex conjugation invariance result.

### FH2. Division algebraic symmetry breaking (2022)
- **arXiv:** [2210.10126](https://arxiv.org/abs/2210.10126) (hep-ph, hep-th)
- **Key result:** A cascade of complex structures $\mathbb{O} \to \mathbb{H} \to \mathbb{C}$ induces $Spin(10) \mapsto G_{PS} \mapsto G_{LR} \mapsto G_{SM} + B{-}L$, both pre- and post-Higgs. Left-right symmetric Higgs representations stem from quaternionic triality $\text{tri}(\mathbb{H})$.
- **Lean target:** Formalize the complex structure cascade; prove each symmetry-breaking step; formalize $\text{tri}(\mathbb{H})$.

### FH3. Three Generations and a Trio of Trialities (2024)
- **arXiv:** [2409.17948](https://arxiv.org/abs/2409.17948) (hep-ph, hep-th)
- **Key result:** Identifies $\mathfrak{su}(3) \oplus \mathfrak{su}(2) \oplus \mathfrak{u}(1)$ within the triality symmetries $\mathfrak{tri}(\mathbb{C}) \oplus \mathfrak{tri}(\mathbb{H}) \oplus \mathfrak{tri}(\mathbb{O})$. The triality triple $(\Psi_+, \Psi_-, V)$ with $\Psi_+, \Psi_-, V \in \mathbb{C} \otimes \mathbb{H} \otimes \mathbb{O}$ provides representations for all three generations. A "Cartan Factorization" merges the third generation's spinor representations into scalar bosons that include the SM Higgs.
- **Lean target:** Formalize the trio of trialities; prove the Cartan Factorization; prove three-generation decomposition.

---

## 3. Ivan Todorov (and collaborators)

Independent but closely aligned program using Clifford algebras from octonionic multiplication.

### T1. Octonions, exceptional Jordan algebra and the role of the group $F_4$ in particle physics (2018)
- **Authors:** Todorov, Drenska
- **arXiv:** [1805.06739](https://arxiv.org/abs/1805.06739) (hep-th, math-ph)
- **Key result:** The automorphism group $F_4$ of the exceptional Jordan algebra $J_3^8$ (27-dim, hermitian $3 \times 3$ octonionic matrices) has maximal subgroups whose intersection is the SM gauge group. First-generation fermions form a basis of primitive idempotents in the euclidean extension of the Jordan subalgebra $JSpin_9$.

### T2. Deducing the symmetry of the standard model from the automorphism and structure groups of the exceptional Jordan algebra (2018)
- **Authors:** Todorov, Dubois-Violette
- **arXiv:** [1806.09450](https://arxiv.org/abs/1806.09450) (hep-th, math-ph)
- **Key result:** SM symmetry deduced from Borel-de Siebenthal theory of maximal connected subgroups of simple compact Lie groups applied to $F_4$.

### T3. Exceptional quantum geometry and particle physics II (2018)
- **Authors:** Dubois-Violette, Todorov
- **arXiv:** [1808.08110](https://arxiv.org/abs/1808.08110) (hep-th, math-ph)
- **Key result:** $J_2^8$ (hermitian $2 \times 2$ octonionic matrices) describes one generation's internal space. Three generations from $J_3^8$ without introducing new fundamental fermions, avoiding electroweak symmetry problems.

### T4. Octonion Internal Space Algebra for the Standard Model (2022)
- **Authors:** Todorov
- **arXiv:** [2206.06912](https://arxiv.org/abs/2206.06912) (hep-th, hep-ph, math-ph)
- **Key result:** $C\ell_{10}$ from octonionic left-multiplication. Projector $\mathcal{P} = \frac{1}{2}(1 - i\omega_6)$ isolates 16-dim particle subspace. SM gauge group = stabilizer of sterile neutrino in $G_{PS}$. Higgs from superconnection. Expresses $m_H / m_W$ via theoretical Weinberg angle.

---

## 4. Latham Boyle (and Shane Farnsworth)

Non-commutative / non-associative geometry approach to the SM, converging with the division algebra program.

### B1. Non-Commutative Geometry, Non-Associative Geometry and the Standard Model of Particle Physics (2014)
- **Authors:** Boyle, Farnsworth
- **arXiv:** [1401.5083](https://arxiv.org/abs/1401.5083) (hep-th)
- **Key result:** Reformulates Connes' NCG axioms into a single requirement. Generalizes from non-commutative to **non-associative** geometry. Eliminates 7 unwanted terms from the spectral action that previously required ad-hoc removal.

### B2. Rethinking Connes' approach to the standard model (2014)
- **Authors:** Farnsworth, Boyle
- **arXiv:** [1408.5367](https://arxiv.org/abs/1408.5367) (hep-th, hep-ph)
- **Key result:** New NCG perspective yields extended SM with extra $U(1)_{B-L}$ gauge symmetry and a complex scalar singlet field $\sigma$ with $B{-}L = 2$. Novel solution to the Higgs mass vs. NCG prediction discrepancy.

### B3. Non-Associative Geometry and the Spectral Action Principle (2013)
- **Authors:** Farnsworth, Boyle
- **arXiv:** [1303.1782](https://arxiv.org/abs/1303.1782) (hep-th)
- **Key result:** Extends NCG spectral action to non-associative geometries. Simplest example (octonions) gives Einstein gravity + $G_2$ gauge theory + 8 Dirac fermions.

### B4. The standard model, the Pati-Salam model, and "Jordan geometry" (2019)
- **Authors:** Boyle, Farnsworth
- **arXiv:** [1910.11888](https://arxiv.org/abs/1910.11888) (hep-th, hep-ph)
- **Key result:** Proposes replacing non-commutative algebra of spacetime coordinates with a **Jordan algebra** ("Jordan geometry"). The natural Jordan algebra describes an extended SM with 3 right-handed neutrinos, a complex scalar, and $U(1)_{B-L}$. A natural extension gives the Pati-Salam model.

### B5. The Standard Model, The Exceptional Jordan Algebra, and Triality (2020)
- **Authors:** Boyle
- **arXiv:** [2006.16265](https://arxiv.org/abs/2006.16265) (hep-th, hep-ph)
- **Key result:** One generation described by tangent space $(\mathbb{C} \otimes \mathbb{O})^2$ of the complex octonionic projective plane. Three generations related to $SO(8)$ triality.

---

## 5. Ovidiu Cristinel Stoica

### S1. The Standard Model Algebra — Leptons, Quarks, and Gauge from the Complex Clifford Algebra $\mathbb{C}\ell(6)$ (2017)
- **arXiv:** [1702.04336](https://arxiv.org/abs/1702.04336) (hep-th, math-ph)
- **Key result:** $\mathbb{C}\ell(6)$ automatically contains leptons and quarks of one family with electroweak + color gauge symmetries, without extra particles. The Witt decomposition leads to ideals representing leptons and quarks. Electroweak symmetry already broken by the geometry. Predicts bare Weinberg angle $\sin^2 \theta_W = 0.25$.

---

## 6. Niels G. Gresnigt (and collaborators)

Extends the Furey program using sedenions, braids, and $S_3$ family symmetry.

### G1. Braids, normed division algebras, and Standard Model symmetries (2018)
- **arXiv:** [1803.02202](https://arxiv.org/abs/1803.02202) (physics.gen-ph)
- **Key result:** Unifies braid model (Bilson-Thompson Helon model) with Furey's $\mathbb{C}\ell(6)$ construction. Braid groups $B_2$ and $B_3^c$ represented using $\mathbb{C}$ and $\mathbb{H}$. Framed braids ↔ basis states of minimal left ideals of $\mathbb{C}\ell(6)$.

### G2. Braided fermions from Hurwitz algebras (2019)
- **arXiv:** [1901.01312](https://arxiv.org/abs/1901.01312) (physics.gen-ph, hep-th)
- **Key result:** Extends the braid/division-algebra correspondence. Ribbon spectrum related to octonion algebras.

### G3. Three fermion generations with two unbroken gauge symmetries from the complex sedenions (2019)
- **Authors:** Gillard, Gresnigt
- **arXiv:** [1904.03186](https://arxiv.org/abs/1904.03186) (hep-th)
- **Key result:** $\mathbb{C} \otimes \mathbb{S}$ (complexified sedenions) splits into three $\mathbb{C} \otimes \mathbb{O}$ subalgebras via a primitive idempotent, yielding three copies of $\mathbb{C}\ell(6)$ = three generations with $SU(3)_C \times U(1)_{EM}$.

### G4. The $\mathbb{C}\ell(8)$ algebra of three fermion generations with spin and full internal symmetries (2019)
- **Authors:** Gillard, Gresnigt
- **arXiv:** [1906.05102](https://arxiv.org/abs/1906.05102) (physics.gen-ph, hep-th)
- **Key result:** $\mathbb{C}\ell(8)$ contains three generations with full Lorentzian, chiral, weak isospin, spin, and electrocolor degrees of freedom. Triality automorphism of $\mathbb{C}\ell(8)$ (absent in $\mathbb{C}\ell(6)$) extends one generation to exactly three.

### G5. The Standard Model particle content with complete gauge symmetries from the minimal ideals of two Clifford algebras (2020)
- **arXiv:** [2003.08814](https://arxiv.org/abs/2003.08814) (physics.gen-ph)
- **Key result:** Two minimal left ideals of $\mathbb{C}\ell(6)$ + two minimal right ideals of $\mathbb{C}\ell(4)$ give one generation with the full $SU(3)_C \times SU(2)_L \times U(1)_Y$. Combined in $\mathbb{C}\ell(10)$ while preserving individual ideal structure. Like $SU(5)$ GUT but without proton decay.

### G6. Three generations of colored fermions with $S_3$ family symmetry from Cayley-Dickson sedenions (2023)
- **Authors:** Gresnigt, Gourlay, Varma
- **arXiv:** [2306.13098](https://arxiv.org/abs/2306.13098) (physics.gen-ph)
- **Key result:** $S_3$ automorphisms of sedenions (which are *not* automorphisms of $\mathbb{O}$) generate two additional generations from the first. Presents sedenion-based approach in self-contained manner.

### G7. Algebraic realisation of three fermion generations with $S_3$ family and unbroken gauge symmetry from $\mathbb{C}\ell(8)$ (2024)
- **Authors:** Gourlay, Gresnigt
- **arXiv:** [2407.01580](https://arxiv.org/abs/2407.01580) (hep-th, math-ph)
- **Key result:** Generalizes $S_3$ embedding into $\mathbb{C}\ell(8)$, includes $S_3$-invariant $U(1)_{EM}$, achieves linear independence of three generations.

### G8. Electroweak Structure and Three Fermion Generations in Clifford Algebra with $S_3$ Family Symmetry (2026)
- **arXiv:** [2601.07857](https://arxiv.org/abs/2601.07857) (physics.gen-ph)
- **Key result:** Three fermion generations within $\mathbb{C}\ell(10)$, transforming under the full $SU(3)_C \times SU(2)_L \times U(1)_Y$, with intrinsic $S_3$ family symmetry. Gauge generators commute with $S_3$.

### G9. Causal Fermion Systems and Octonions (2024)
- **Authors:** Finster, Gresnigt, Isidro, Marciano, Paganini, Singh
- **arXiv:** [2403.00360](https://arxiv.org/abs/2403.00360) (math-ph, hep-th)
- **Key result:** Connects octonions to causal fermion systems. Division algebra tensor products describe vacuum symmetries. Causal fermion systems provide the spacetime/dynamics that octonionic theories lack.

---

## 7. Robert A. Wilson

### W1. Subgroups of Clifford algebras (2020)
- **arXiv:** [2011.05171](https://arxiv.org/abs/2011.05171) (math.RA)
- **Key result:** Algebraist's perspective. Three generations of fermions and weak symmetry breaking emerge from extending the Dirac algebra from $\mathbb{C}$ to $\mathbb{H}$.

---

## 8. John C. Baez & John Huerta

### BH1. Division Algebras and Supersymmetry I (2009)
- **arXiv:** [0909.0551](https://arxiv.org/abs/0909.0551) (hep-th, math.DG, math.RA)
- **Key result:** Supersymmetric Yang-Mills + massless spinors exist iff spacetime dimension is 3, 4, 6, or 10 — corresponding exactly to $\mathbb{R}, \mathbb{C}, \mathbb{H}, \mathbb{O}$. Self-contained derivation of the division-algebra ↔ SUSY connection.

---

## 9. Geoffrey Dixon

### D1. Integral Octonions, Octonion XY-Product, and the Leech Lattice (2010)
- **arXiv:** [1011.2541](https://arxiv.org/abs/1011.2541) (hep-th, math.RA)
- **Key result:** Integral octonions from the XY-product. Connections to laminated lattices $\Lambda_4, \Lambda_8, \Lambda_{16}, \Lambda_{24}$ (Leech). Dixon pioneered the "Dixon algebra" $\mathbb{R} \otimes \mathbb{C} \otimes \mathbb{H} \otimes \mathbb{O}$ approach to the SM.

---

## 10. Other Notable Papers

### O1. Octonionic representations of Clifford algebras and triality (1994)
- **Authors:** Schray, Manogue
- **arXiv:** [hep-th/9407179](https://arxiv.org/abs/hep-th/9407179)
- **Key result:** Foundational work extending Clifford algebra representations to octonions. Defines octonionic spinors. Triality exhibits $S_3 \times SO(8)$ structure.

### O2. Octonions as Clifford-like algebras (2023)
- **Authors:** Depies, Smith, Ashburn
- **arXiv:** [2310.09972](https://arxiv.org/abs/2310.09972) (math.RA)
- **Key result:** Introduces "Kingdon algebras" — alternative Clifford-like algebras. Octonions and split octonions arise as Kingdon algebras. Gives universality property and superalgebra structure.

### O3. Octonions, trace dynamics and non-commutative geometry (2020)
- **Authors:** Tejinder P. Singh
- **arXiv:** [2006.16274](https://arxiv.org/abs/2006.16274) (hep-th)
- **Key result:** Matrix dynamics at Planck scale with octonionic evolution space. Automorphism group $G_2$ has 14 generators (12 vector bosons + 2 graviton DOF?). References Furey/Dixon algebra as arising naturally.

---

## Formalization Priority Map

The papers above cluster into several **formalizable algebraic cores**. Ordered by dependency and value to the COG project:

### Priority 1: Algebraic Foundations (needed by everything)
| Topic | Key papers | Lean deliverable |
|-------|-----------|-----------------|
| Fano plane & octonion multiplication | F1, BH1 | `Fano.lean`, `Octonion.lean` |
| $\mathbb{C}\ell(6)$ from $\mathbb{C} \otimes \mathbb{O}$ | F1, S1 | `CL6.lean` |
| Witt basis / ladder operators | F2 | `WittBasis.lean` |
| Minimal left ideals | F1, G5 | `MinimalIdeals.lean` |

### Priority 2: One Generation
| Topic | Key papers | Lean deliverable |
|-------|-----------|-----------------|
| $SU(3)_C$ from $\mathbb{C}\ell(6)$ ideals | F1, S1 | `ColorSymmetry.lean` |
| $SU(3)_C \times SU(2)_L \times U(1)_Y / \mathbb{Z}_6$ | F2, FH1 | `SMGaugeGroup.lean` |
| Fermion doubling resolution | FH1 | `FermionDoubling.lean` |
| Proton decay blocking | F2 | `ProtonDecayBlock.lean` |

### Priority 3: Three Generations
| Topic | Key papers | Lean deliverable |
|-------|-----------|-----------------|
| Triality automorphism | FH3, G4, B5 | `Triality.lean` |
| Three-gen decomposition | F3, FH3 | `ThreeGenerations.lean` |
| $S_3$ family symmetry (sedenion route) | G3, G6, G7, G8 | `SedenionGenerations.lean` |

### Priority 4: Symmetry Breaking
| Topic | Key papers | Lean deliverable |
|-------|-----------|-----------------|
| Complex structure cascade $\mathbb{O} \to \mathbb{H} \to \mathbb{C}$ | FH2 | `SymmetryBreaking.lean` |
| Quaternionic triality Higgs | FH2, FH3 | `HiggsFromTriality.lean` |
| Weinberg angle prediction | S1, T4 | `WeinbergAngle.lean` |

### Priority 5: Jordan Algebra & Exceptional Groups
| Topic | Key papers | Lean deliverable |
|-------|-----------|-----------------|
| Exceptional Jordan algebra $J_3^8$ | T1, T2, T3, B5 | `ExceptionalJordan.lean` |
| $F_4$ automorphisms → SM gauge group | T1, T2 | `F4Automorphisms.lean` |
| Jordan geometry | B4 | `JordanGeometry.lean` |

---

## Key Algebraic Structures to Formalize (Summary)

| Structure | Dimension | Key property | Source |
|-----------|-----------|-------------|--------|
| $\mathbb{O}$ (octonions) | 8 real | Alternative, non-associative | All |
| $\mathbb{C} \otimes \mathbb{O}$ | 8 complex | Generates $\mathbb{C}\ell(6)$ | F1 |
| $\mathbb{C}\ell(6)$ | 64 complex | 8 minimal left ideals = leptons + quarks | F1, S1, G5 |
| $\mathbb{R} \otimes \mathbb{C} \otimes \mathbb{H} \otimes \mathbb{O}$ | 32 complex | One full SM generation (no doubling) | FH1 |
| $\mathbb{C}\ell(8)$ | 256 complex | Three gens via triality | G4 |
| $\mathbb{C}\ell(10)$ | 1024 complex | Full SM with $S_3$ family symmetry | G5, G8, T4 |
| $J_3^8$ (exceptional Jordan) | 27 real | $F_4$ automorphisms → SM gauge group | T1, T2, B5 |
| $\mathbb{S}$ (sedenions) | 16 real | $S_3$ auts give three $\mathbb{O}$ subalgebras | G3, G6 |
| Fano plane | 7 pts, 7 lines | Encodes $\mathbb{O}$ multiplication | All |

---

## 11. Cohl Furey — Recent (2025)

### F4. A Superalgebra Within (2025)
- **arXiv:** [2505.07923](https://arxiv.org/abs/2505.07923) (hep-th)
- **Key result:** Constructs a $\mathbb{Z}_2^5$-graded superalgebra from the division algebra tensor product. Uses Bott periodicity to connect the 8-fold periodicity of real Clifford algebras to the division algebra tower. The Jordan algebra $H_{16}(\mathbb{C})$ appears as a natural subalgebra. Suggests the SM algebraic structure is an inevitable consequence of periodicity in Clifford algebra classification.
- **Lean target:** Formalize $\mathbb{Z}_2^5$ grading on the division algebra tensor product; verify Bott periodicity connection.

---

## 12. John C. Baez — Foundational Surveys

### BH2. The Octonions (2001)
- **Authors:** John C. Baez
- **arXiv:** [math/0105155](https://arxiv.org/abs/math/0105155) (math.RA)
- **Key result:** Comprehensive 56-page survey of octonion algebra and its connections to geometry and physics. Covers normed division algebras, Cayley-Dickson construction, automorphism groups ($G_2$), triality, projective planes over division algebras, Lorentzian geometry in dimensions 3/4/6/10, and the role of octonions in string theory and $M$-theory. Essential reference for definitions and classical results.
- **Lean target:** Primary source for definitions of Cayley-Dickson construction, Moufang identities, $G_2$ structure.

### BH3. Division Algebras and Supersymmetry II (2010)
- **Authors:** John C. Baez, John Huerta
- **arXiv:** [1003.3436](https://arxiv.org/abs/1003.3436) (hep-th, math.DG)
- **Key result:** Extends BH1. Proves the super-Poincaré algebra has extensions to 2-superalgebras (Lie 2-superalgebras) iff the spacetime dimension is 3, 4, 6, or 10 — again corresponding exactly to $\mathbb{R}, \mathbb{C}, \mathbb{H}, \mathbb{O}$. The 3-cocycle condition for the extension is equivalent to the "3-$\psi$'s rule" ($\psi \wedge \psi \wedge \psi = 0$), which holds iff the spinor components lie in a normed division algebra.

---

## 13. Geoffrey Dixon — Original Program

### D2. Division Algebras: Octonions, Quaternions, Complex Numbers, and the Algebraic Design of Physics (1993)
- **arXiv:** [hep-th/9303039](https://arxiv.org/abs/hep-th/9303039)
- **Key result:** The foundational paper proposing $T = \mathbb{R} \otimes \mathbb{C} \otimes \mathbb{H} \otimes \mathbb{O}$ as the algebraic basis for one generation of SM fermions. This "Dixon algebra" was the original inspiration for Furey's program. Shows that right-multiplication by octonions generates $SU(3)$, right-multiplication by quaternions gives $SU(2)$, and complex multiplication gives $U(1)$.

### D3. Division Algebras, Lattices, Physics, Windmill Tilting (1993)
- **arXiv:** [hep-th/9302113](https://arxiv.org/abs/hep-th/9302113)
- **Key result:** Explores connections between the Dixon algebra, lattice structures, and particle physics. Discusses the role of integral lattices in the octonion and quaternion number systems.

---

## 14. Causal Set Theory & Discrete Spacetime

These papers provide the spacetime framework that complements the algebraic content above. COG's DAG structure is a causal set with octonionic node data.

### CS1. The causal set approach to quantum gravity (2006)
- **Authors:** Joe Henson
- **arXiv:** [gr-qc/0601121](https://arxiv.org/abs/gr-qc/0601121)
- **Key result:** Review of causal set theory — the hypothesis that spacetime is fundamentally a locally finite partially ordered set (a "causal set"). The order relation encodes causal structure; the counting measure encodes volume. Recovers Lorentzian manifold geometry in the continuum limit. Discusses dynamics via sequential growth models.

### CS2. Directions in Causal Set Quantum Gravity (2011)
- **Authors:** Sumati Surya
- **arXiv:** [1103.6272](https://arxiv.org/abs/1103.6272) (gr-qc)
- **Key result:** Comprehensive review of causal set quantum gravity. Covers kinematics (sprinklings, Hauptvermutung), dynamics (classical sequential growth, quantum measure theory), phenomenology (swerving particles, cosmological constant prediction). Key result: causal set theory naturally predicts a small positive cosmological constant via "everpresent $\Lambda$".

### CS3. Causal Sets: Overview and Status (2010)
- **Authors:** Petros Wallden
- **arXiv:** [1002.3757](https://arxiv.org/abs/1002.3757) (gr-qc)
- **Key result:** Status report on causal sets. Reviews faithful embedding theorems (Malament-Hawking: causal order + volume = full geometry), Rideout-Sorkin classical sequential growth dynamics, and observational signatures.

### CS4. Statistical Lorentzian geometry and the closeness of Lorentzian manifolds (2012)
- **Authors:** Bombelli, Noldus
- **arXiv:** [gr-qc/0210003](https://arxiv.org/abs/gr-qc/0210003) (gr-qc)
- **Key result:** Defines statistical distance measures between Lorentzian manifolds using causal set sprinklings. Relevant to COG's question of how macroscopic Lorentz covariance emerges from discrete graph structure (Phase 5, attack vector 5.1).

### CS5. Causal Sets and Conservation Laws in Tests of Lorentz Symmetry (2010)
- **Authors:** Luca Bombelli, Aron Wall
- **Key result:** Constraints on Lorentz-violating effects in causal set scenarios. Important for COG's need to demonstrate that the discrete DAG structure doesn't produce observable Lorentz violations.

---

## 15. Connes Noncommutative Geometry & Spectral Standard Model

The NCG approach is the most developed alternative algebraic route to the SM. COG should understand its successes and where division algebras may improve upon it.

### NCG1. Gravity and the standard model with neutrino mixing (2006)
- **Authors:** Ali Chamseddine, Alain Connes, Matilde Marcolli
- **arXiv:** [hep-th/0610241](https://arxiv.org/abs/hep-th/0610241)
- **Key result:** Full derivation of the SM Lagrangian (including neutrino mixing and see-saw mechanism) coupled to gravity from the spectral action on a noncommutative geometry $M \times F$, where $F$ is a finite internal space. The finite space $F$ encodes the SM algebra $\mathbb{C} \oplus \mathbb{H} \oplus M_3(\mathbb{C})$.

### NCG2. Why the Standard Model (2007)
- **Authors:** Ali Chamseddine, Alain Connes
- **arXiv:** [0706.3688](https://arxiv.org/abs/0706.3688) (hep-th)
- **Key result:** Classification theorem: among all irreducible finite noncommutative geometries of KO-dimension 6 (mod 8), the SM algebra is the *unique* solution satisfying a set of natural axioms. This is the strongest "inevitability" result for the SM from pure mathematics.

### NCG3. Resilience of the Spectral Standard Model (2012)
- **Authors:** Ali Chamseddine, Alain Connes
- **arXiv:** [1208.1030](https://arxiv.org/abs/1208.1030) (hep-ph, hep-th)
- **Key result:** Shows the NCG prediction survives the Higgs mass measurement at 125 GeV by incorporating a real scalar singlet field $\sigma$ that couples to the Higgs. The NCG framework naturally accommodates this extension.

### NCG4. Spectral Action in Noncommutative Geometry (2019 survey)
- **Authors:** Chamseddine, Connes, van Suijlekom
- **Key result:** Survey of the spectral action principle and its applications. Reviews the full pipeline from NCG axioms to SM + gravity Lagrangian. Discusses higher-order corrections, renormalization group flow, and connections to Pati-Salam unification.

**Relation to COG:** The NCG approach uses continuous geometry ($M^4$ manifold) + finite internal space. COG replaces the manifold with a causal DAG and the finite space with $\mathbb{C} \otimes \mathbb{O}$ node data. Boyle & Farnsworth (B1-B5) provide the bridge, showing non-associative geometry (octonions) may be the correct replacement for Connes' non-commutative but associative algebra.

---

## 16. Bilson-Thompson Braid / Preon Model

Topological approach to SM particle classification. Gresnigt (G1-G2) bridges this with the division algebra program.

### BT1. A topological model of composite preons (2005)
- **Authors:** Sundance O. Bilson-Thompson
- **arXiv:** [hep-ph/0503213](https://arxiv.org/abs/hep-ph/0503213)
- **Key result:** The "Helon model" — first-generation SM fermions (leptons and quarks) are topologically classified by braids on three ribbons. Each ribbon carries $\pm 1/3$ charge (twist). The braid group $B_3$ representations reproduce the correct charges, chiralities, and color states. A purely combinatorial, pre-geometric model.

### BT2. Quantum gravity and the standard model (2006)
- **Authors:** Bilson-Thompson, Markopoulou, Smolin
- **arXiv:** [hep-th/0603022](https://arxiv.org/abs/hep-th/0603022)
- **Key result:** Embeds the Helon braid model into loop quantum gravity. Braided ribbon networks arise as noiseless subsystems of a spin network evolving under local moves. The SM particle spectrum appears as stable topological excitations of quantum geometry.

### BT3. Particle Topology, Braids, and Braided Belts (2009)
- **Authors:** Bilson-Thompson, Hackett, Kauffman, Smolin
- **arXiv:** [0903.1376](https://arxiv.org/abs/0903.1376) (hep-th)
- **Key result:** Extends BT1 to "braided belts" — a more general topological framework. Demonstrates robustness of the braid-particle correspondence under different topological assumptions.

### BT4. Braid Matrices and Quantum Gates for Ising Anyons with Applications to Quantum Computing and Particle Physics (2025)
- **Authors:** Chester, Marrani, Rios
- **arXiv:** [2501.09782](https://arxiv.org/abs/2501.09782) (quant-ph)
- **Key result:** Connects braid matrices for Ising anyons to quantum computing gates and SM particle classification. Demonstrates how topological quantum computation and particle physics share algebraic underpinnings via braid group representations.

---

## 17. Koide Formula & Discrete Mass Relations

COG's Phase 4.3 proposes mass = tick frequency. These papers provide the empirical mass-ratio targets.

### K1. The Koide Lepton Mass Formula and Geometry of Circles (2012)
- **Authors:** Jan Kocik
- **arXiv:** [1201.2067](https://arxiv.org/abs/1201.2067) (physics.gen-ph)
- **Key result:** Reinterprets the Koide formula $(\sum m_i)^2 / (\sum \sqrt{m_i})^2 = 2/3$ as a geometric property of Apollonius circles. The formula becomes a statement about the "angle" between three mass vectors in a specific metric space. Provides a visual, geometric understanding of the mysterious mass relation.

### K2. Family Gauge Symmetry as an Origin of Koide's Mass Formula (2008)
- **Authors:** Yoshio Sumino
- **arXiv:** [0801.2080](https://arxiv.org/abs/0801.2080) (hep-ph)
- **Key result:** Derives the Koide formula from a $U(3)$ family gauge symmetry. The formula is protected from radiative corrections by the gauge symmetry. Predicts additional family gauge bosons.

### K3. Discrete mass relation for 4-body hadronic systems (2017)
- **Authors:** Yoshio Koide
- **arXiv:** Various
- **Key result:** Extensions of the original Koide relation to hadrons and 4-body systems. Suggests the discrete mass relation may be more fundamental than initially appreciated.

### K4. Quark-Lepton Symmetric Model (1994)
- **Authors:** Robert Foot
- **Key result:** Early work connecting quark-lepton mass relations to discrete symmetries. Context for understanding why discrete algebraic frameworks might predict mass ratios.

---

## 18. Non-Associativity & Alternativity in Physics

These papers directly support COG's core mechanism: non-associativity → time.

### NA1. Star Products Made (Somewhat) Easier (2016)
- **Authors:** Vladislav Kupriyanov, Richard Szabo
- **arXiv:** [1601.03607](https://arxiv.org/abs/1601.03607) (hep-th, math-ph)
- **Key result:** Constructs explicit star products for non-associative phase spaces using alternative (Moufang) algebras. Shows that non-associativity in quantum mechanics leads to modified uncertainty relations and non-trivial "Jacobiator" terms. The alternative identity (from octonions) is the minimal weakening of associativity that still permits a consistent star product.
- **Relevance to COG:** Provides the technical framework for understanding how non-associative operations at graph nodes create irreducible computational overhead — the mechanism COG identifies with mass/time.

---

## 19. $G_2$ Structures & Octonion Geometry

### GS1. $G_2$-structures and octonion bundles (2015)
- **Authors:** Sergey Grigorian
- **arXiv:** [1510.04226](https://arxiv.org/abs/1510.04226) (math.DG, hep-th)
- **Key result:** Develops the theory of octonion bundles over manifolds with $G_2$ structure. The structure group of the tangent bundle reduces from $SO(7)$ to $G_2$ iff the manifold admits a torsion-free octonion cross product. Provides the geometric setting for octonionic field theories on 7-manifolds.

### GS2. (Split) Octonion geometry and its applications in physics (2015)
- **Authors:** Merab Gogberashvili, Otari Sakhelashvili
- **arXiv:** [1506.01012](https://arxiv.org/abs/1506.01012) (hep-th, math-ph)
- **Key result:** Split-octonion geometry applied to physics. The split signature gives a natural $(3+4)$-dimensional framework. Applications to electromagnetism and gravity formulated in octonionic language.

---

## 20. Lean Formalization References

Papers relevant to the practical task of formalizing this mathematics in Lean 4.

### LF1. Formalizing Geometric Algebra in Lean (2021)
- **Authors:** Eric Wieser, Utensil Song
- **arXiv:** [2110.03551](https://arxiv.org/abs/2110.03551) (cs.MS, math.RA)
- **Key result:** Formalizes Clifford algebras (geometric algebra) in Lean 3 / mathlib. Defines the universal property of Clifford algebras, exterior algebras as a special case, and various structural results. This is the existing mathlib infrastructure that COG's Lean formalization can build upon for $\mathbb{C}\ell(6)$, $\mathbb{C}\ell(8)$, $\mathbb{C}\ell(10)$.
- **Practical note:** Since COG uses Lean 4 with mathlib4, the Clifford algebra API from this paper is available as `Mathlib.LinearAlgebra.CliffordAlgebra`. However, per CLAUDE.md rules, we must avoid continuous-analysis imports — the discrete Clifford algebra constructions should be safe to use.

### LF2. The Lean Mathematical Library (2019)
- **Authors:** The mathlib Community
- **arXiv:** [1910.09336](https://arxiv.org/abs/1910.09336) (cs.LO, cs.MS)
- **Key result:** Overview of mathlib's architecture and scope. Relevant sections: ring theory, module theory, linear algebra, group theory, category theory. Provides the foundation layer that all COG Lean code will depend on.

---

## Expanded Formalization Priority Map (Updated)

### Priority 0: Infrastructure & Background
| Topic | Key papers | Purpose |
|-------|-----------|---------|
| Mathlib Clifford algebra API | LF1, LF2 | Reuse existing $\mathbb{C}\ell(n)$ formalization |
| Causal set theory concepts | CS1, CS2 | Inform DAG axioms in `State.lean` |
| NCG comparison points | NCG1, NCG2 | Understand what the SM algebra "should" look like |

### Priority 6: Causal Structure & Dynamics (new)
| Topic | Key papers | Lean deliverable |
|-------|-----------|-----------------|
| DAG as causal set | CS1, CS2, CS3 | `CausalOrder.lean` |
| Lorentz covariance from causal order | CS4, CS5 | `LorentzFromOrder.lean` |
| Braid excitations on graphs | BT2, G1 | `BraidExcitations.lean` |
| Non-associative star products | NA1 | `AlternativeStar.lean` |

### Priority 7: Mass Predictions (new)
| Topic | Key papers | Lean/Python deliverable |
|-------|-----------|------------------------|
| Koide formula verification | K1, K2 | `calc/koide.py` |
| Tick frequency → mass ratios | K1, K3, RFC-001 §3.2 | `Mass.lean`, `calc/mass_ratios.py` |
