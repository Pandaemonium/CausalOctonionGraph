# RFC-003: Objections and Resolutions (Red Team)

**Status:** Living Document
**Created:** 2026-02-22
**Purpose:** Track critical theoretical objections to the COG model and their formal resolutions.

---

## 1. The "Preferred Frame" Objection (Lorentz Covariance)

**Objection:**
A discrete graph update rule `step(G)` implies a global discrete time parameter $n$, which seems to define a preferred foliation of spacetime (a "cosmic clock"). This violates Lorentz covariance, where no such preferred frame exists.

**Resolution Strategy: Causal Invariance (Confluence)**
*   **Theory:** Following Wolfram (2020) and Rideout/Sorkin (1999), Lorentz covariance in a discrete causal set emerges if the update rule is **causally invariant** (confluent).
*   **Definition:** If two update events $A$ and $B$ are spacelike separated (their inputs are disjoint), the resulting graph must be isomorphic regardless of whether $A$ happens before $B$ or $B$ before $A$.
*   **Mechanism:**
    *   **Batch Updates:** Associative algebraic operations are inherently order-independent. $(ab)c = a(bc)$.
    *   **Tick Updates:** Non-associative operations force a specific parenthesization. We prove that the "Tick" logic in `Tick.lean` ensures that if multiple valid ticks are available, their execution order does not change the final topology or causal history of the DAG.
*   **Deliverable:** `claims/causal_invariance.yml` linked to `CausalGraphTheory/RaceCondition.lean`.

---

## 2. The "3 Generations" Objection

**Objection:**
Triality ($V \leftrightarrow S_+ \leftrightarrow S_-$) permutes three mathematical representations, but in the Standard Model, the three generations ($e, \mu, \tau$) are identical in representation structure (all are leptons/quarks) and differ only in mass. Why does a triality *permutation* result in three distinct physical copies?

**Resolution Strategy: Symmetry Breaking via Fano Directionality**
*   **Theory:** The Fano plane is not symmetric under arbitrary permutations; it has a specific cyclic orientation.
*   **Mechanism:**
    *   The map $V \to S_+$ involves multiplication by specific octonions (e.g., $e_4$).
    *   The map $V \to S_-$ involves different octonions (e.g., $e_5$).
    *   Due to the non-associativity of $\mathbb{O}$, the "computational cost" (number of ticks required to stabilize the state) differs for these transitions.
    *   **Hypothesis:** $Mass \propto TickFrequency$. The slight asymmetry in the algebraic "path length" through the Fano plane creates the mass hierarchy $m_e \ll m_\mu \ll m_\tau$.
*   **Deliverable:** `claims/mass_tick_frequency.yml` and `calc/mass_ratios.py`.

---

## 3. The "Continuum Limit" Objection

**Objection:**
A graph with $N \approx 10^{100}$ nodes is still discrete. How does a smooth manifold $M$ and the Einstein-Hilbert action emerge?

**Resolution Strategy: Causal Action Principle**
*   **Theory:** Rely on the existing proofs by Finster et al. for Causal Fermion Systems (CFS).
*   **Mechanism:**
    *   Show that the COG update rule minimizes a discrete "causal action" $S = \sum_{x,y} \mathcal{L}(x,y)$.
    *   Invoke Finster's continuum limit theorem: as density $\to \infty$, the minimizer of the causal action satisfies the Einstein field equations coupled to the Dirac equation.
*   **Deliverable:** `rfc/RFC-005_Continuum_Limit_Strategy.md`.

---

## 4. The "Chirality" Objection

**Objection:**
The Standard Model is chiral (weak force affects only left-handed particles). Octonions are non-associative but not inherently "left-handed" in a way that breaks parity maximally.

**Resolution Strategy: Witt Basis Projection**
*   **Theory:** The choice of the Witt basis $\alpha_j = \frac{1}{2}(e_a + i e_b)$ selects a specific complex structure.
*   **Mechanism:**
    *   The "vacuum axis" $e_7$ breaks the symmetry.
    *   Furey (2018) shows that the ladder operators acting on $\omega$ naturally generate minimal left ideals (left-handed spinors) and their antiparticles (right-handed).
    *   The "missing" right-handed neutrino corresponds to the sterile vacuum $\omega$ itself, which does not couple to gauge bosons.
*   **Deliverable:** `claims/gauge_group_emergence.yml` (Standard Model representations).

---

## 5. The "Independent Generations" Objection (McRae)

**Objection:**
Triality ($V \leftrightarrow S_+ \leftrightarrow S_-$) is an outer automorphism of $Spin(8)$, meaning all three triality images live in the **same** $Spin(8)$ orbit. They are, by definition, structurally identical representations. If the three generations arise from triality, why are they not literally the same particle? McRae (2024) warns that this identification is too facile.

**Resolution Strategy: Explicit Symmetry Breaking via Witt Projection**
*   **Theory:** Triality is a symmetry of $Spin(8)$, but the physical vacuum $\omega = \frac{1}{2}(1 + i e_7)$ **breaks** $Spin(8)$ down to $U(1)_Y \times SU(2)_L \times SU(3)_C$.
*   **Mechanism:**
    *   The triality images $V \to S_+$ and $V \to S_-$ use different Fano plane directions (e.g., $e_4$ vs. $e_5$). These directions are inequivalent once the $e_7$ vacuum axis is fixed.
    *   After the $e_7$ projection, the three triality images have different residual stabilizers inside $G_2 \subset Spin(7)$.
    *   **Consequence:** The triality images are identical as abstract $Spin(8)$ representations, but they correspond to different cosets of the residual symmetry group, giving them different quantum numbers and, via `claims/mass_tick_frequency.yml`, different tick frequencies (masses).
*   **Key Test:** Compute the stabilizer of each triality image under the $G_2$ subgroup generated by the 7 Fano cycles. If the three stabilizers are non-isomorphic, the generations are genuinely distinct. This is a finite group computation checkable by `calc/gauge_check.py`.
*   **Open Problem (Phase 7):** Formalize the $Spin(8) \to G_2$ projection in Lean and prove that the three coset stabilizers are non-isomorphic. This is the content of `claims/triality_generations.yml`.
*   **Deliverable:** `claims/triality_generations.yml` linked to a future `CausalGraphTheory/Triality.lean`.
