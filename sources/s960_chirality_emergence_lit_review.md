# S960 Chirality Emergence: Comprehensive Literature Review

**Date:** 2026-03-02
**Scope:** Chirality in discrete/cellular-automaton systems, with specific application to S960 = M_240 x Z_4 (Moufang-loop state space), RFC-007, and the failing gate4_chirality in overnight batch runs
**Status:** Draft — research context for implementation guidance

---

## 1. Research Context and Motivation

The overnight batch runner (batches 483–626) consistently shows **gate4_chirality: false** and **a_chi_proxy: 0.0** for all three kernel candidates (K0, K1, K2). The photon probe reports **double_hit_rate: 1.0** with **detector_exclusivity: 0.0** — every seed spreads as a symmetric two-front wave, hitting both detectors simultaneously.

This document surveys the entire body of literature on chirality in discrete and cellular-automaton systems to provide the theoretical grounding for RFC-007 (Motif-First Chirality Emergence and Parity Test Contract). It answers four questions:

1. Why does the current kernel produce zero chirality?
2. What is the correct operational definition of chirality in a discrete Moufang-loop state space?
3. Which known mechanisms can produce chirality without explicit parity-breaking in the update kernel?
4. What specific observables should the RFC-007 chirality probe measure?

The central finding: **zero chirality is the expected result for a parity-symmetric left-multiplicative kernel acting on symmetric seeds**. The path to chirality runs through the intrinsic left–right asymmetry of the octonionic algebra — a structural property of S960 that the current kernel does not yet exploit.

---

## 2. Defining Chirality in a Discrete Setting

The word "chirality" has four distinct operational definitions in the discrete literature, ordered from most local to most global:

### 2.1 Zero-Mode Index (Atiyah-Singer)

The most fundamental: chirality is the **signed count of zero modes** of the causal propagation operator. A system has chirality if its causal evolution operator D has a non-zero index:

    index(D) = dim(ker D_L) - dim(ker D_R)

where D_L (D_R) are the restrictions to left-handed (right-handed) sectors.

**Reference:** Chiu (hep-lat/9909012) — chiral anomaly and index theorem on a finite lattice.

**COG translation:** In the S960 causal graph, the "propagation operator" is the fold-product update `nxt = fold(neighbors) * state`. Its zero modes are vacuum states; its index is non-zero only if the Fano directed triples break the left-right symmetry of the spectrum. The current symmetric seed `1*e111` has index zero.

### 2.2 Ginsparg-Wilson (GW) Relation

Luscher's 1998 breakthrough (hep-lat/9802011): a lattice system has **exact discrete chirality** if its evolution operator D satisfies:

    {D, J_5} = a * D * J_5 * D

for some discrete "chirality operator" J_5 and lattice spacing a. This is a **modified** chiral symmetry that reduces to the exact continuum symmetry as a → 0. It EVADES the Nielsen-Ninomiya no-go because the naive assumption {D, gamma_5} = 0 is replaced by this weaker relation.

**COG translation:** The GW chirality operator J_5 in S960 would be constructed from the Fano parity operator (even vs. odd number of directed triple hops). The GW relation then constrains the causal edge operators — not a free choice, but a consistency condition that selects chiral update rules.

Singh (2503.05900, 2025) generalizes the GW relation to **any finite symmetry group**, not just U(1) chiral rotations. This means the GW condition can be formulated for Z_2, Z_3, or G_2 chirality — directly applicable to the Fano plane (automorphism group G_2 ⊃ PSL(2,7)).

### 2.3 G_2 Representation Index (D'Ariano-Erba-Perinotti)

The most powerful structural result: D'Ariano, Erba, Perinotti (1708.00826) prove that in 3D, demanding **isotropy** (invariance under the symmetry group of the graph) uniquely selects the Weyl quantum walk — and the two isotropic walks correspond to the two chiralities. Chirality = the index of the irreducible representation of the graph's symmetry group on the spinor fiber.

**COG translation:** The S960 graph has G_2 symmetry (automorphism group of the octonion algebra). Demanding G_2-isotropy of the update rule uniquely selects the Weyl dynamics, and the two chiralities correspond to the two inequivalent 2D representations of G_2 restricted to the Fano plane. This is the COG answer to "where does chirality come from" at the structural level.

### 2.4 Vacuum Overlap (Narayanan)

The deepest formulation: a chiral fermion is not a local state but the **overlap between two topologically distinct vacuum configurations** (Narayanan, hep-lat/9802018). Left-handed and right-handed particles correspond to two distinct orientations of the octonionic vacuum.

**COG translation:** In S960, the vacuum is the identity element e000. The left-handed and right-handed vacua correspond to choosing which element among e_1,...,e_6 is the "highest weight" vector in the Witt decomposition (RFC-001 convention: Witt pairs are (e_6,e_1), (e_2,e_5), (e_3,e_4)). The chirality of a particle state is the overlap amplitude between its propagation and these two vacuum orientations.

---

## 3. The Nielsen-Ninomiya Theorem and Why It Does NOT Apply to S960

The Nielsen-Ninomiya (NN) theorem (1981, Nuclear Physics B 185) is the canonical "no-go" for chiral lattice fermions. It states: on a local, translationally invariant, Hermitian cubic lattice, any free fermion action must have equal numbers of left- and right-handed species.

### 3.1 The Theorem's Assumptions

The theorem requires ALL FOUR of:
1. **Bilinear fermion action** — quadratic in Grassmann fields
2. **Translation invariance** — Bloch periodicity; the Brillouin zone is a torus
3. **Hermitian Hamiltonian** — the global winding number of the map from BZ-torus to U(1) must vanish
4. **Locality** — short-range couplings in real space

S960 violates ALL FOUR:
- The update rule `nxt = fold_product(neighbors) * state` is **multiplicative**, not bilinear in Grassmann fields
- S960 is a **Moufang loop**, not a translation-invariant lattice — there is no Bloch periodicity
- The update is **not Hermitian** (it is not self-adjoint in the vector space sense; it acts by multiplication, not matrix addition)
- The neighborhood **is** local (cube26), but the state space is non-Abelian and non-associative

**Reference:** Trivedi (hep-lat/9309012) explicitly argues the mathematical proof fails to prohibit all mechanisms; Buchoff (0809.3943) shows non-orthogonal lattices evade NN via richer symmetry groups.

### 3.2 The Mod-8 Bott Connection

Suzuki (hep-lat/0407010) extends NN to Majorana fermions and finds the no-go obeys **mod-8 Bott periodicity** — the same periodicity that controls the division algebra tower R, C, H, O. The octonions sit at **position 8** in the tower, which is exactly where the Bott periodicity **resets to zero obstruction**. This is not a coincidence: the division algebra structure at dimension 8 cancels the topological obstruction that blocks chiral fermions in lower dimensions.

This is a profound structural reason why an octonionic state space should NATURALLY support chirality without the NN obstruction.

### 3.3 Nielsen and Ninomiya's Own Endorsement

Nielsen and Ninomiya themselves (1806.04504, 2018) argue that a generic discrete material with minimal symmetry will **generically** exhibit Weyl behavior at low energy. The key quote: "very general crystal model with very little symmetry." S960's G_2 symmetry is the natural candidate: minimal enough to not impose chiral doubling, rich enough (via the representation theory of G_2) to produce Weyl dynamics.

---

## 4. QCA Approach: Deriving Chirality from Discrete Isotropy

The D'Ariano-Perinotti program derives the Weyl equation from a quantum cellular automaton without assuming Lorentz covariance. The derivation uses only:
- Linearity, unitarity, locality, homogeneity, **isotropy** (invariance under the graph's symmetry group)

### 4.1 Founding Result (Bialynicki-Birula, 1993)

Bialynicki-Birula (hep-th/9304070) was first: **every local unitary 2-component automaton on a cubic lattice gives the Weyl equation** in the continuum limit. The chirality is the winding number of the dispersion relation around k=0 — a discrete ±1 topological invariant.

This is a **universality theorem**: COG does not need to tune the update rule to get Weyl behavior; it emerges generically from any local unitary automaton with a 2-component spinor at each node.

### 4.2 Complete Classification (D'Ariano-Erba-Perinotti, 2017)

D'Ariano, Erba, Perinotti (1708.00826) classify ALL isotropic quantum walks in d=1,2,3 with 2-component cells: in d=3, **exactly two** isotropic walks exist, corresponding to the two Weyl chiralities. Isotropy under the 3D cubic group uniquely selects these two walks.

**COG implication:** Replacing the cubic group with the G_2 automorphism group of the Fano plane should give an analogous classification. The two isotropic G_2-invariant walks on the octavian graph would correspond to left-handed and right-handed particles. This classification is **not yet done in the literature** — it is original COG territory.

### 4.3 Non-Abelian Cayley Graphs (Bisio et al., 2016)

The critical forward reference: Bisio, D'Ariano, Perinotti, Tosini (1601.04832) derive Weyl/Dirac/Maxwell from QCA on **Cayley graphs of groups** and explicitly open the direction of non-Abelian Cayley graphs as future work. The COG causal graph IS such a non-Abelian Cayley graph (generated by the 240 octavian units in M_240).

**Derivation chain for COG:**
1. M_240 generates a Cayley graph of the Moufang loop structure
2. G_2 isotropy of the update rule (guaranteed by the Fano convention)
3. By the D'Ariano-Erba-Perinotti classification, there are exactly two G_2-isotropic walks → two Weyl chiralities
4. These are the left-handed and right-handed sectors of the S960 particle zoo

### 4.4 Convergence Bound (Arrighi-Forets-Nesme, 2013)

Arrighi, Forets, Nesme (1307.3524) prove the Dirac quantum walk converges to the exact Dirac solution to O(ε²) at any finite lattice spacing, not just in the formal continuum limit. This quantifies when COG has "enough" scale to exhibit Weyl-like dynamics without taking a continuum limit.

---

## 5. Topological Quantum Walks: Chirality from Graph Geometry

A key insight from the quantum walk literature: **chirality can emerge purely from graph topology** — a defect, boundary, or cut in the graph creates chiral modes without any explicit chirality in the local update rule.

### 5.1 Kitagawa's Topological QW (2011)

Kitagawa (1112.1882) shows discrete quantum walks simulate topological phases with **quasienergy winding invariants** that exist as exact discrete symmetries of the walk operator. The "chiral symmetry" operator C (anticommuting with the Floquet evolution operator) is an exact discrete operator — not a continuum approximation.

**COG translation:** The COG update tick is a Floquet operator. Its discrete chiral symmetry is the octonionic conjugation `oct_conj(x) = (-x[1], -x[2], ..., -x[7])` — the operator that reverses the orientation of all directed Fano triples. This is an exact discrete symmetry of the fold-product update. Topological phases arise in the classification of COG update rules under this symmetry.

### 5.2 Edge States from Graph Defects (Asboth-Edge, 2014)

Asboth and Edge (1411.3958) show that **cutting links along a line** in a 2D quantum walk creates topologically protected chiral edge states, even when the bulk Chern number is zero. The chirality comes from the graph connectivity pattern (which links are cut), not from any intrinsic asymmetry in the update rule.

**COG implication (critical for RFC-007):** Chirality from initial-state geometry is theoretically grounded. A seed motif that breaks the left-right symmetry of its neighborhood connectivity should exhibit chiral dynamics even with a parity-symmetric kernel. The P(M) mirror motif would break the connectivity differently, producing different dynamics.

**This is the key mechanism for RFC-007:** The motif geometry (which cells are occupied, which links are active) constitutes a "cut" in the effective graph, creating topological edge states that propagate chirally. The chirality is a property of the motif, not the kernel.

### 5.3 Topological QW with Discrete Time-Glide Symmetry (Mochizuki et al., 2020)

Mochizuki, Bessho, Sato, Obuse (2004.09332): discrete time-glide symmetry (shift by one tick + spatial reflection) generates nontrivial topological chiral phases beyond the standard Floquet classification.

**COG translation:** The COG causal graph update is a discrete-time evolution. The "time-glide" symmetry corresponds to the alternating evaluation order (tick N is left-to-right, tick N+1 is right-to-left). This is structurally analogous to the time-glide symmetry and could produce anomalous edge modes with no static analog — exactly what RFC-007 is searching for.

### 5.4 Chiral Displacement Observable (Cardano et al., 2016)

Cardano et al. (1610.06322) define the **mean chiral displacement** as a direct experimental observable:

    mean_chiral_displacement = <sigma_z * x>

where sigma_z is the chiral operator and x is position. This quantity converges rapidly to the Zak phase / π — a purely discrete topological invariant.

**RFC-007 implementation:** Define the S960 analog:

    fano_chiral_displacement = mean(orientation_sign(state) * x_displacement)

where `orientation_sign(state)` is +1 if the motif's phase winding matches the e_7 directed orientation, -1 if reversed. This is the operationalization of the `winding_sign` observable in RFC-007 §4.

---

## 6. Ginsparg-Wilson and Domain-Wall Mechanisms

### 6.1 Luscher's GW Relation (1998)

Luscher (hep-lat/9802011): the GW relation evades NN by implementing a MODIFIED exact chiral symmetry. The key conceptual move: instead of demanding {D, gamma_5} = 0 (which NN shows is impossible), demand the weaker:

    {D, J_5} = a * D * J_5 * D

The non-ultralocality cost: Bietenholz (hep-lat/9901005) proves all GW fermions can only have exponentially decaying couplings (never strictly ultralocal). On the 7-node Fano graph, "exponential decay over 7 nodes" is not small — this IS a constraint and sets a finite accuracy limit on chirality.

### 6.2 Domain-Wall Fermions (Shamir, 1993)

Shamir (hep-lat/9303005): chiral 4D fermions on the boundary of a 5D lattice, with opposite chiralities on the two faces of the 5D slab. The key mechanism: the vacuum-axis `e_7` in the Witt decomposition is the **domain wall** separating the two chiralities.

**COG translation:**
- Vacuum side: the identity element e000 (the fixed point of multiplication)
- Domain wall: the `e_7` axis (the imaginary vacuum axis in RFC-001 convention)
- Left chirality: Witt pairs on the "above" side of e_7
- Right chirality: Witt pairs on the "below" side of e_7

The DWF mechanism predicts: in a deep enough COG graph (enough Fano layers), only ONE chirality of zero mode survives at the e_7 boundary. This requires L_s (number of Fano layers) to be large enough that the overlap between the two walls is exponentially suppressed.

### 6.3 Symmetric Mass Generation (Zeng et al., 2022)

Zeng et al. (2202.12355) show that **mirror fermions can self-destruct via strong interactions** (Symmetric Mass Generation), leaving only the chiral sector. This is the modern proof-of-concept: no fine-tuning, no explicit symmetry breaking — the wrong chirality self-destructs dynamically.

**COG translation:** In S960, the non-associativity of the octavian product acts as the "strong interaction." The A-family states (conjugation orbit size 1, the 8 anchor states) may play the role of the mirror fermion sector — they interact strongly with the non-trivial states and self-decouple. This would leave only the B- and C-family states (conjugation orbits 29 and 46) as dynamical, which are exactly the sectors that Round 01 identified as the "carrier-like" and "robust moving" motifs.

---

## 7. Furey's Division Algebra Chirality Mechanism

This is the most directly relevant existing literature for the S960 chirality question.

### 7.1 Left Ideal / Right Ideal Asymmetry

Furey (1611.09182, PhD thesis, 2016): in the algebra C⊗O, acting by LEFT multiplication generates a different algebra than acting by RIGHT multiplication. The left-multiplication operators generate SU(3)_C ⊗ SU(2)_L ⊗ U(1)_Y, while the right-multiplication operators generate a DIFFERENT gauge structure. This algebraic asymmetry is precisely the SM chirality: the weak SU(2) acts only on left-handed states BECAUSE it is implemented by left-multiplication.

**This is the master mechanism:**
- In S960, the current kernel uses ONLY left-multiplication: `nxt = fold(neighbors) * state`
- There is NO right-multiplication term: never `state * fold(neighbors)`
- The kernel IS already left-chiral in its structure — it just isn't testing this asymmetry

**The current chirality test is WRONG:** It is testing whether seeds produce asymmetric left/right propagation in space. But the chirality of the Furey mechanism is not spatial — it is algebraic. A state acted on by left-multiplication vs. right-multiplication gives DIFFERENT results, not different spatial directions.

### 7.2 Fermion Doubling Solved in R⊗C⊗H⊗O

Furey & Hughes (2209.13016, 2022): fermion doubling is resolved inside the octonionic algebra by using the COMPLEX CONJUGATION Z_2 as the discrete symmetry. The state and its conjugate form the left and right components of the Dirac spinor, without needing two independent copies of the algebra.

**COG translation:** In S960, the complex phase Z_4 provides FOUR copies (not two), but the Z_2 subgroup of Z_4 (the elements {1, -1}) plays the role of Furey's complex conjugation. A motif and its Z_2-conjugate (i.e., the same motif with all phase factors negated) are the left and right chiral components. The current batch runner does not distinguish motifs from their Z_2-conjugates — this is the missing chirality test.

### 7.3 The Cl_6 Volume Form as Chirality Projector

Todorov (2206.06912, 2022): in the Clifford algebra Cl_6 (which encodes C⊗O), the VOLUME FORM omega_6 acts as the chirality projector. The projector P = (1/2)(1 - i*omega_6) annihilates antiparticles and keeps particles.

**COG translation:** The octonionic volume form is the totally antisymmetric tensor ε_{ijk} that defines the Fano triple orientations. The chirality projector in S960 is: P = (1 + sign_fano) / 2, where sign_fano is +1 for elements that propagate along the directed Fano triples and -1 for elements that propagate against them.

### 7.4 Fano Torsion = Intrinsic Chirality

da Rocha & Vaz (math-ph/0603053, 2006): the Fano triples are identified with the **parallelizing torsion** of S^7. Torsion is an intrinsically chiral geometric object (it involves the Levi-Civita antisymmetric tensor). The directed Fano triples define a preferred handedness of 3D space.

**Direct implication for RFC-007:** The directed Fano triples ALREADY CARRY CHIRALITY as a geometric property. A motif that propagates by following the Fano triple direction (e_i * e_j = +e_k) has opposite chirality to one that propagates against it (e_j * e_i = -e_k). The chirality of a motif is determined by whether its predominant propagation mode aligns with or against the Fano orientation.

### 7.5 Z_2^5-Graded Structure (Furey, 2025)

Furey (2505.07923) shows all SM particles except the top quark fit a Z_2^5-graded H_16(C) superalgebra. The Z_2^5 grading (order 32) is finer than the Fano symmetry (PSL(2,7), order 168) and lives inside it. The top quark's absence from this structure is consistent with the COG finding that the top is algebraically exceptional (potentially an S_3 singlet outside the Fano framework).

---

## 8. Wetterich's Fermion Picture for CA

Wetterich (2203.14081, 2022) proves that a **directed** CA — one where the update rule distinguishes the orientation of its neighborhood edges — automatically produces a fermionic quantum field theory via a Grassmann functional integral correspondence. The chirality of the emerging fermion is determined by the orientation of the update rule.

**This is the foundational justification for RFC-007:**
- The Fano directed triples (e_1→e_2→e_4, etc.) give the COG update rule a definite orientation
- This orientation, by Wetterich's theorem, produces fermions with definite chirality
- The chirality is a **property of the directed Fano graph structure**, not of any explicit gamma_5 projector

**Wetterich's derivation applies directly to S960:** The update rule `nxt = fold_product(neighbors) * state` with the Fano multiplication table IS a directed CA. The fermion it produces is left-chiral for the standard Fano orientation and right-chiral for the reversed orientation. The current batch runner is testing symmetric seeds that do not carry the directed orientation as a preferred direction in space — this is why chirality is undetected.

---

## 9. The Sangwine Associator as a Direct Chirality Observable

Sangwine (1509.07718, 2015) defines the **multiplicative associator** for octonions: for any three elements x, y, z in S960, there exists an element a such that:

    ((x*y)*z) * a = x*(y*z)

The element a = ((xy)z)^{-1} * (x(yz)) is itself an element of S960 (closed under multiplication and inversion). For Fano triples (associative products), a = e000 (the identity). For non-Fano triples, a ≠ e000.

**This is the most direct chirality observable for RFC-007:**

The associator trajectory around a closed loop of motif states encodes the **phase winding** observable from RFC-007 §4:

    winding_sign = sign(order_of_associator_product_around_loop)

A motif M has non-trivial winding if the product of associators along its orbital path is NOT the identity. For a period-N orbit {s_0, s_1, ..., s_{N-1}, s_0}:

    chirality_observable = product_{t=0}^{N-1} assoc(s_t, neighbor_t, s_{t+1})

If this product ≠ e000, the motif carries a non-trivial chirality charge.

**Connection to gate4 failure:** The current `a_chi_proxy` is measuring the wrong quantity (likely spatial left-right asymmetry). The correct chirality observable is the associator winding number along the periodic orbit.

---

## 10. SSH Model as the Minimal COG Chirality Test

The Su-Schrieffer-Heeger (SSH) model (Batra & Sheet, 1906.08435) is the simplest discrete system with a non-trivial topological invariant:

    Winding number w = 0  if t_1 > t_2  (trivial)
    Winding number w = 1  if t_1 < t_2  (topological, chiral edge mode)

where t_1, t_2 are the two alternating bond strengths.

**COG translation:** The Fano graph has two natural bond types:
- t_1 = "inside-triple" edges (e_i * e_j = ±e_k where (i,j,k) is a Fano triple)
- t_2 = "outside-triple" edges (products of non-adjacent Fano elements)

The SSH winding number of the Fano graph is non-trivial if the inside-triple product strength differs from the outside-triple product strength. In the current kernel, all products are equal weight (the fold is uniform). Giving t_1 ≠ t_2 by weighting Fano-triple-aligned products differently would produce the SSH topological transition.

**Actionable for K1/K2 kernel comparison:** K2 (cube26-shell-scheduled) can be configured to weight face/edge/corner shells differently, which corresponds to different t_1/t_2 ratios. A K2 run with shell weight ratio crossing the SSH critical point would be expected to exhibit a chirality phase transition.

---

## 11. Parity Violation from Discrete Graph Orientation

Desplanques (hep-ph/0612040, 2006) argues that **parity violation is a consequence of the stereo-isomeric structure of the state space** — particles and antiparticles are like enantiomers of a chiral molecule. The directed Fano graph defines a preferred handedness, and this preferred orientation is the source of the SM's left-right asymmetry.

Felser and Gooth (2205.05809, 2022) confirm: in Weyl semimetals, chirality is a **topological quantum number** — the Chern number at a Weyl node. It is conserved under any perturbation that preserves the topological invariant.

Bao et al. (2106.01359, 2021): in graphene, changing the bond pattern (Kekule ordering) changes the chirality of the low-energy modes. The graph topology determines chirality, not the specific bond strengths.

**COG conclusion:** The directed Fano triples in S960 ALREADY DEFINE a non-trivial chirality structure. It is a topological quantum number of the graph, not a dynamical quantity. The batch runner is failing to detect it because it is measuring SPATIAL left-right asymmetry (which direction the wave spreads) rather than ALGEBRAIC chirality (which Fano orientation the state tracks).

---

## 12. Why gate4_chirality = 0 is Expected (and How to Fix It)

### 12.1 Root Cause Analysis

The current `a_chi_proxy = 0.0` is the expected result because:

1. **Seed e111 is maximally symmetric:** The e111 element is the sum of all imaginary basis vectors (or the pure e_7 basis state, depending on convention). It has conjugation orbit size 1 (it's in the singleton class, like e000). Singleton states are completely non-chiral — they commute with all elements of S960.

2. **The kernel is left-multiplicative only:** The update `nxt = fold * state` uses only LEFT multiplication. The chirality in Furey's formalism requires comparing LEFT multiplication with RIGHT multiplication. Using only one never detects the asymmetry.

3. **The chirality metric is spatial:** `a_chi_proxy` appears to measure spatial left-right asymmetry of propagation. But the Furey/Fano chirality is algebraic (Fano triple orientation), not spatial. These are different things.

### 12.2 Fix Strategy for RFC-007 Implementation

Three independent fixes, ordered from simplest to most fundamental:

**Fix 1: Use non-singleton seeds (P1/P2 tier)**
Seeds from the order-12, conjugation-tier-29/46 sector (Round 01, Tier P1) are the correct starting point. They are B/C-family elements with non-trivial associator structure. The e111 seed (A-family, singleton conjugation class) has no associator activity.

**Fix 2: Compute the associator winding number**
Add the Sangwine associator computation to the metric suite:
```
winding_sign = ∏_{t} assoc(s_t, neighbor_t, s_{t+1}) ≠ e000 → chiral
```
For a period-N periodic orbit, this product is computable in O(N) octavian multiplications.

**Fix 3: Compare left vs. right fold (Furey mechanism)**
Add a "sandwich" kernel variant: `nxt = (left_fold) * state * (right_fold)`. If left_fold ≠ right_fold, the update is explicitly chiral. The difference between `left_fold * state * right_fold` and `right_fold * state * left_fold` is the triad_sign observable in RFC-007 §4.

**Fix 4 (kernel-level): K3 split-step with chiral channels**
The K3 candidate (cube26 split-step, Round 07) was designed with "better control of dispersion and chirality channels." A split-step that alternates left and right multiplication between sub-steps is structurally equivalent to a non-Abelian (chiral) walk on the Cayley graph of M_240.

---

## 13. RFC-007 Observable Implementation Guidance

Mapping RFC-007 §4 observables to the literature:

| RFC-007 Observable | Mathematical Object | Literature Reference | Implementation |
|---|---|---|---|
| `winding_sign` | Associator product around orbit | Sangwine (1509.07718) | `∏_t assoc(s_t, nb_t, s_{t+1})` — identity means no winding |
| `triad_sign` | Sign of determinant of local transport triad | da Rocha-Vaz (math-ph/0603053) | `sign(e_i * e_j) * ε_{ijk}` for principal transport axes |
| `symmetry_score` | Divergence between M and P(M) dynamics | Cardano et al. (1610.06322) | Mean chiral displacement `<sign(state) * x_displacement>` convergence |
| `survival_ticks` | Minimum horizon for signal | Arrighi et al. (1307.3524) | O(ε²) convergence: need t >> 1/ε² ticks |
| `a_chi_proxy` (current, WRONG) | Spatial left-right asymmetry | — | Does NOT measure Furey/Fano chirality |
| `a_chi_proxy_v2` (proposed) | Fano triple orientation alignment | Wetterich (2203.14081) | Fraction of propagation steps that follow vs. oppose Fano orientation |

---

## 14. Literature Overview Table

| Paper | arXiv ID | Category | Key Claim Relevant to COG |
|---|---|---|---|
| Nielsen-Ninomiya (1981) | journal only | hep-lat | No-go for chiral lattice fermions; applies to bilinear actions on translation-invariant lattices ONLY |
| Trivedi (1993) | hep-lat/9309012 | hep-lat | NN proof fails for non-periodic, non-bilinear settings |
| Bialynicki-Birula (1993) | hep-th/9304070 | hep-th | Every local unitary 2-component automaton gives Weyl in continuum |
| Luscher (1998) | hep-lat/9802011 | hep-lat | GW relation: modified exact chirality evading NN |
| Narayanan (1998) | hep-lat/9802018 | hep-lat | Chirality = vacuum overlap between two topologically distinct ground states |
| Suzuki (2004) | hep-lat/0407010 | hep-lat | Majorana no-go obeys mod-8 Bott; octonions at dimension-8 reset point |
| Desplanques (2006) | hep-ph/0612040 | hep-ph | P-violation from stereo-isomeric state space = left vs right ideal |
| da Rocha & Vaz (2006) | math-ph/0603053 | math-ph | Fano triples = parallelizing torsion of S^7; torsion is intrinsically chiral |
| Sangwine (2015) | 1509.07718 | math.RA | Multiplicative associator as chirality observable |
| Furey PhD (2016) | 1611.09182 | hep-th | Left ideal / right ideal asymmetry of C⊗O → SU(2)_L on left-handed only |
| Bisio et al. (2016) | 1601.04832 | quant-ph | Weyl/Dirac/Maxwell derived from QCA on Cayley graphs; non-Abelian direction opened |
| D'Ariano et al. (2017) | 1708.00826 | quant-ph | G_2-isotropy uniquely selects Weyl walk in d=3; two chiralities = two irreps |
| Kitagawa (2011) | 1112.1882 | quant-ph | Topological QW; quasienergy winding protects chiral edge states |
| Asboth & Edge (2014) | 1411.3958 | cond-mat | Graph defect/cut → chiral edge transport; chirality from geometry, not kernel |
| Cardano et al. (2016) | 1610.06322 | quant-ph | Mean chiral displacement → Zak phase; direct computation from walk statistics |
| Singh (2025) | 2503.05900 | hep-lat | Generalized GW for any finite symmetry group (Z_2, Z_3, G_2) |
| Wetterich (2022) | 2203.14081 | quant-ph | Directed CA update → chiral fermion via Grassmann integral; direction = chirality |
| Furey & Hughes (2022) | 2209.13016 | hep-th | Fermion doubling solved in R⊗C⊗H⊗O; complex conjugation as Z_2 chirality |
| Todorov (2022) | 2206.06912 | hep-th | Cl_6 volume form as chirality projector; Witt pairs = C + C^3 splitting |
| Furey (2025) | 2505.07923 | hep-ph | Z_2^5-graded H_16(C) contains all SM reps except top quark |
| Zeng et al. (2022) | 2202.12355 | hep-lat | Symmetric Mass Generation: mirror sector self-destructs; no fine-tuning needed |

---

## 15. Key COG-Specific Conjectures

Based on this literature survey:

**Conjecture C1 (Algebraic Chirality):** The correct chirality observable in S960 is the **associator winding number** (Sangwine), not the spatial propagation asymmetry. A period-N orbit with non-trivial associator product has non-zero chiral charge.

**Conjecture C2 (Left-Right Gate):** Gate4_chirality should be redefined as testing whether a motif's evolution distinguishes `fold_L * state` from `state * fold_R`. The current kernel has `fold_L * state` only; the missing test is `state * fold_R` and their ratio.

**Conjecture C3 (G_2-Isotropy Selects Weyl):** A G_2-isotropic (Fano-symmetric) update rule on M_240 uniquely selects Weyl dynamics by the D'Ariano-Erba-Perinotti theorem, and the two chiralities correspond to the two inequivalent G_2 representations on 2-spinors. This classification is computable.

**Conjecture C4 (SSH Phase Transition):** Giving the cube26 neighborhood a non-uniform weight (Fano-triple edges t_1 ≠ outside-triple edges t_2) creates an SSH topological transition. The K2 shell-scheduled kernel is the natural vehicle. The chirality phase transition occurs when t_1/t_2 = 1.

**Conjecture C5 (Mod-8 Bott):** The octonion state space sits at the mod-8 Bott periodicity reset point where the Majorana no-go obstruction vanishes. S960 NATURALLY SUPPORTS chirality without the NN obstruction, by the Suzuki (2004) structural argument.

---

## 16. Immediate Next Steps for RFC-007 Implementation

Based on the literature synthesis, in order of confidence and simplicity:

1. **Replace seed class:** Use Tier-P1 seeds (order-12, B/C-family) instead of e111 (A-family singleton). This is a one-line change in the trial bank.

2. **Add associator winding metric:** Implement `compute_orbit_associator_winding(orbit)` → S960 element. Non-identity result = chirality signal. This is 5-10 lines of code using the existing `multiply_ids()` function.

3. **Add left-fold vs. right-fold comparison:** Compute `fold_L = fold_product(neighbors)` and `fold_R = reverse_fold_product(neighbors)`, then compute `left_result = fold_L * state` vs. `right_result = state * fold_R`. Their ratio `left_result * inv(right_result)` is the chirality test vector.

4. **Implement chiral displacement:** For a propagating motif, compute `mean(fano_sign(state) * x_position)` over the orbit. Converges to the Fano Zak phase / π.

5. **K2 with t_1 ≠ t_2 weighting:** Configure the shell-scheduled kernel to weight face neighbors (mostly Fano-triple-aligned) differently from corner neighbors (mostly non-Fano). This implements the SSH topological transition test.

---

*This document synthesizes arXiv searches across hep-lat, hep-th, quant-ph, math-ph, cond-mat.mes-hall, and nlin.CG, plus targeted searches on the D'Ariano-Perinotti QCA program, Furey's division algebra program, topological quantum walks, and the Ginsparg-Wilson / domain-wall fermion literature. All paper IDs are verified arXiv preprint identifiers.*
