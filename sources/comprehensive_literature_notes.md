# Comprehensive Literature Review: Causal Graph Theory & Octonions

**Date:** 2026-02-22
**Purpose:** Consolidate external literature search results to ground the COG implementation plan.

---

## 1. Causal Fermion Systems (CFS) & Octonions
**Key Researcher:** Felix Finster (and collaborators like N. Gresnigt).
**Core Relevance:** The theoretical "bridge" between causal sets and octonionic algebra.

*   **Vacuum Symmetries:** Finster's work demonstrates that octonions are not just an arbitrary choice for internal symmetry but naturally describe the symmetries of the vacuum configuration within the CFS framework.
*   **Complementarity:** CFS provides the "spacetime" container (causal action principle, dynamics), while octonions provide the "matter" content (algebraic microstructure). This mirrors the COG architecture exactly:
    *   *CFS* $\approx$ `CausalGraph` (topology/dynamics)
    *   *Octonions* $\approx$ `NodeLabel` / `EdgeLabel` (local algebra)
*   **Continuum Limit:** The existence of the "causal action principle" in CFS gives COG a specific target for its continuum limit. As the graph density $N \to \infty$, the discrete update rule `step(G)` should approximate the minimization of the causal action.

**Reference:** Finster, F., Gresnigt, N., et al. (2024). *Causal Fermion Systems and Octonions*. arXiv:2403.00360.

---

## 2. Octonions and the Standard Model
**Key Researchers:** Murat Günaydin, Feza Gürsey, Cohl Furey.
**Core Relevance:** Deriving the Standard Model (SM) gauge group $G_{SM} = SU(3) \times SU(2) \times U(1)$ from first principles.

*   **Gunaydin-Gürsey (1973):** Established the foundational link. The automorphism group of the octonions $\mathbb{O}$ is the exceptional Lie group $G_2$. If one imaginary unit (say $e_7$) is fixed/stabilized, the remaining symmetry group is exactly $SU(3)$ (the color group).
    *   *Implication for COG:* The "vacuum axis" $e_7$ in `WittBasis.lean` is not arbitrary; it is the geometric constraint that breaks $G_2 \to SU(3)$.
*   **Furey's "Dixon Algebra" Program:** Uses $\mathbb{R} \otimes \mathbb{C} \otimes \mathbb{H} \otimes \mathbb{O}$ (Clifford algebra $\mathbb{C}\ell(6)$) to generate the full SM gauge group.
    *   *Ideals as Particles:* Fermions appear as minimal left ideals of the algebra.
    *   *Generations:* The algebra naturally contains 64 complex dimensions, which breaks down into spinor representations matching a single generation of SM particles (plus sterile neutrino). The origin of the *three* generations remains the hardest open problem, often linked to $Spin(8)$ triality.

**References:**
*   Günaydin, M., & Gürsey, F. (1973). *Quark structure and octonions*. J. Math. Phys.
*   Furey, C. (2016). *Standard model physics from an algebra?*. arXiv:1611.09138.

---

## 3. Discrete Physics & Koide Formula
**Key Concept:** Empirical mass relations from discrete structures.

*   **The Formula:** $Q = \frac{m_e + m_\mu + m_\tau}{(\sqrt{m_e} + \sqrt{m_\mu} + \sqrt{m_\tau})^2} = \frac{2}{3}$ (exact).
*   **Status:** Highly accurate experimentally (within error bars for pole masses), but lacks a consensus theoretical derivation in QFT.
*   **Discrete Explanations:**
    *   *Brannen:* Koide's formula relates to the Discrete Fourier Transform of mass roots, suggesting masses arise from eigenvalues of a "circulant matrix" (a discrete operator).
    *   *Clifford Torus:* Geometric arguments involving the topology of phase space ($S^3$).
*   **COG Hypothesis:** If mass is defined as "tick frequency" (an integer count of non-associative updates per global depth), then mass ratios are ratios of integers. The Koide formula might be a Diophantine constraint on allowed graph topologies/frequencies, rendering it exact in the discrete theory.

---

## 4. Formalization Efforts (Lean)
**Key Project:** PhysLean (Tooby-Smith).

*   **Context:** A recent effort to formalize high-energy physics in Lean 4.
*   **Coverage:** Includes tensor calculus (Einstein notation), group representations, and potentially SM gauge definitions.
*   **Relevance:** Instead of building `GaugeGroup.lean` from scratch, COG should leverage PhysLean if possible to handle the continuous group theory, while COG focuses on the discrete algebraic emergence.
*   **Action:** Verify if `PhysLean` (arXiv:2411.07667) is public and usable as a `lake` dependency.

**Reference:** Tooby-Smith, J. (2024). *PhysLean: Digitalising theoretical physics*. arXiv:2411.07667.

---

## 5. Synthesis: The "Master Plan" Logic
The literature supports the specific sequence in `MASTER_IMPLEMENTATION_PLAN.md`:

1.  **Algebra (Octonions):** Well-grounded in Furey/Gunaydin.
2.  **Dynamics (Causal Graph):** Well-grounded in Finster/Wolfram.
3.  **Bridge (Confluence):** The "Race Condition" proof is the standard way to recover relativity in discrete gravity (Rideout/Sorkin, Wolfram).
4.  **Mass (Koide):** The most speculative part, but aligns with "Discrete Physics" research (Brannen).

**Conclusion:** The project is not inventing new physics `ab initio` but rather proposing a *computational unification* of existing, isolated theoretical results.
