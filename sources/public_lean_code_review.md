# Public Lean 4 Code for Physics and Causal Graph Theory: An Overview

This document summarizes existing public Lean 4 repositories and projects that could potentially be leveraged for Causal Graph Theory (COG) development.

## 1. PhysLean (The Primary Candidate)

* **Repository:** `lean-phys-community/PhysLean`
* **Website:** physlean.com
* **Description:** PhysLean is the major open-source, community-driven effort to create a formalized library of physics in Lean 4. It aims to be for physics what Mathlib is for mathematics.

### Current Scope & Capabilities
Based on current data (as of early 2026), PhysLean covers several foundational areas of physics, including:
*   Maxwell's Equations
*   Quantum Harmonic Oscillators
*   Wick's Theorem (Quantum Field Theory)
*   The Tight-Binding Model

### Relevance to COG
*   **Direct Overlap:** Currently, PhysLean does *not* appear to have explicit modules for Causal Graph Theory, Octonions, the Fano Plane, or Causal Fermion Systems.
*   **Potential for Leverage:** While direct modules may be missing, PhysLean is highly valuable as a foundational resource. It likely contains formalized definitions of vector spaces, quantum states, basic operators, and other mathematical structures that COG can build upon. By aligning with PhysLean's conventions, COG can ensure interoperability and potentially contribute back to the broader physics formalization community.

## 2. Mathlib4 (The Mathematical Foundation)

* **Description:** The standard mathematical library for Lean 4.
* **Relevance to COG:** Mathlib4 is essential. It provides the rigorous definitions for groups (like SL(2,3) or GL(3,2)), rings, fields, combinatorics, and basic linear algebra. COG's proofs regarding the Fano plane and the Koide formula (over rational numbers) rely heavily on Mathlib4's algebraic hierarchy.

## 3. Dedicated Physics Formalization (Niche Areas)

*   **Causal Fermion Systems (CFS):** While CFS is a well-established theoretical framework with its own dedicated research community (causal-fermion-system.com), there is currently no public evidence of a dedicated Lean 4 formalization of CFS outside of what we are building in COG.
*   **Octonions and Fano Plane:** While there is extensive literature on the connections between octonions, the Fano plane, and particle physics (e.g., Furey's work), there are no major public Lean 4 libraries specifically formalizing these structures for physics outside of Mathlib's basic algebraic definitions.

## Conclusion and Strategy

1.  **Embrace Mathlib4:** Continue to heavily utilize and align with Mathlib4 for all foundational algebraic and combinatorial proofs.
2.  **Investigate PhysLean:** Perform a deep dive into the `lean-phys-community/PhysLean` repository. Specifically look for formalizations of:
    *   Hilbert spaces and quantum states (to ensure our `Spinors.lean` aligns).
    *   Lorentz group representations (if available, for future relativistic extensions).
3.  **Contribute Back:** Consider structuring COG's foundational proofs (like the formalization of the Fano plane or octonion alternativity) in a way that could eventually be submitted as a pull request to Mathlib4 or PhysLean. This increases the visibility and robustness of the COG project.
