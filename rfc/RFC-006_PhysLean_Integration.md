# RFC-006: PhysLean Integration Strategy

**Status:** Strategic
**Created:** 2026-02-22
**Purpose:** Define safe usage of the PhysLean library within the COG project.

---

## 1. Context

*   **PhysLean:** (arXiv:2411.07667) is a formalization of high-energy physics in Lean 4.
*   **Goal:** Use PhysLean for standard results (SM gauge group, representations, tensor identities) to avoid reinventing the wheel.
*   **Constraint:** COG's axioms must remain **discrete and algebraic**. Importing `Real`, `Manifold`, or `Analysis` into core logic files violates the "No Continuum" mandate.

---

## 2. Policy: The "Safe Subset"

We distinguish between **Core Axioms** and **Model Verification**.

### 2.1 Core Axioms (Forbidden Zone)

*   **Files (complete list):**
    *   `Basic.lean`, `Fano.lean`, `FanoMul.lean`, `Algebra.lean`
    *   `Octonion.lean`, `OctonionAlt.lean`, `OctonionNonAssoc.lean`, `ComplexOctonion.lean`
    *   `SubalgebraDetect.lean`, `WittBasis.lean`
    *   `State.lean`, `Update.lean`, `Tick.lean`
    *   `CausalOrder.lean`, `DAGProof.lean`, `Distance.lean`
    *   `RaceCondition.lean`, `Mass.lean`, `ExportOracle.lean`
*   **Imports:** **Strictly Forbidden.**
    *   `Mathlib.Analysis.*`, `Mathlib.Topology.*`, `Mathlib.MeasureTheory.*`
    *   `Mathlib.Data.Real.*`, `Mathlib.Data.Complex.Basic`
    *   `Mathlib.Geometry.Manifold.*`
    *   `PhysLean.Manifold.*`, `PhysLean.Analysis.*`
*   **Reason:** The core graph evolution must be purely combinatorial/algebraic. It cannot depend on the real numbers.
*   **Contamination Check:** After adding any new import to any file in this list, run:
    ```bash
    lake exe graph | grep -E "Analysis|Topology|MeasureTheory|Data\.Real|Manifold"
    ```
    If any output appears, the import chain is contaminated and must be removed.

### 2.2 Model Verification (Allowed Zone)

*   **Files:** `GaugeGroup.lean`, `Triality.lean`, `StandardModel.lean`.
*   **Imports:** **Allowed with Caution.**
    *   `PhysLean.GroupTheory.*` (Representations, Lie Algebras)
    *   `PhysLean.StandardModel.*` (Gauge groups)
*   **Reason:** We need to prove that our discrete structure *isomorphic* to the standard continuous physics objects in the limit or algebraic projection.
    *   Example: "The automorphism group of the node algebra is isomorphic to `PhysLean.StandardModel.GaugeGroup`."
    *   This requires importing the continuous definition to state the isomorphism theorem.

---

## 3. Implementation Plan

1.  **Add Dependency:** Add `PhysLean` to `lakefile.toml` (once public URL is confirmed).
2.  **Facade Pattern:** Create `CausalGraphTheory/PhysLean/Facade.lean` to re-export only the safe, algebraic parts of PhysLean.
3.  ** CI Check:** The `.github/workflows/lean_action_ci.yml` linter must distinguish between core files (strict) and verification files (relaxed).

---

## 4. Specific Targets

*   **Tensor Notation:** Use PhysLean's index notation for contracting octonion structure constants $\varepsilon_{ijk}$.
*   **Lie Algebras:** Use PhysLean's `LieAlgebra` typeclass for $\mathfrak{su}(3)$ and $\mathfrak{su}(2)$.
*   **Representations:** Use PhysLean to check that our `V`, `S_plus`, `S_minus` match the `Fundamental` and `Spinor` representations of $Spin(8)$.

---

## 5. Fallback Strategy

If PhysLean is too heavy or deeply entwined with analysis:
1.  **Isolate:** Copy only the necessary discrete group theory definitions into `CausalGraphTheory/External/`.
2.  **Mock:** Define our own simple `SU3` / `SU2` types using `Matrix 3 3 Complex` and proving the group axioms directly.
