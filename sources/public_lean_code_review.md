# Public Lean 4 Code for Physics and Causal Graph Theory: An Overview

This document summarizes existing public Lean 4 repositories and projects that could potentially be leveraged for Causal Graph Theory (COG) development.

**Last updated:** 2026-02-24. All Lean claims verified by `lean_run_code` against the project's pinned Mathlib version (v4.29.0-rc1) unless noted otherwise.

---

## 0. Verified High-Value Mathlib Facts

These were confirmed via `lean_run_code` and are immediately actionable.

### 0.1 `Matrix.GeneralLinearGroup (Fin 3) (ZMod 2)` has cardinality 168

```lean
import Mathlib.LinearAlgebra.Matrix.GeneralLinearGroup.Defs
import Mathlib.FieldTheory.Finite.Basic

#eval Fintype.card (Matrix.GeneralLinearGroup (Fin 3) (ZMod 2))
-- output: 168

example : Fintype.card (Matrix.GeneralLinearGroup (Fin 3) (ZMod 2)) = 168 := by
  native_decide
```

**COG use:** `GaugeGroup.lean` currently proves `fano_aut_count` by enumerating all 168 Fano permutations via `decide`. We can add a cross-check theorem that equates our Fano automorphism group with `GL (Fin 3) (ZMod 2)` — making the GL(3,2) isomorphism machine-verified, not just a matching number. This is stronger than just having two `decide`-proved equalities to 168.

**Note:** The report mentions a lemma called `Matrix.card_GL_field` — **this name does not exist** in the pinned Mathlib version. The actual approach is `Fintype.card` on the `GeneralLinearGroup` instance, computed by `native_decide`.

### 0.2 `Configuration.ProjectivePlane` typeclass exists

```lean
import Mathlib.Combinatorics.Configuration
#check Configuration.ProjectivePlane  -- confirmed present
```

**COG use:** The Fano plane is PG(2,2), the projective plane of order 2. Defining a `Configuration.ProjectivePlane` instance on our 7-point Fano encoding would give access to Mathlib's incidence geometry lemma library (uniqueness of line through two points, point-line duality, etc.) without reproving them. This is a medium-effort refactor of `Fano.lean` with high structural payoff — particularly for the `wittPairs_on_distinct_lines` class of theorems (§4i, PROGRESS.md).

### 0.3 `FDRep.finrank_hom_simple_simple` — formal Schur's Lemma

```lean
import Mathlib.RepresentationTheory.FDRep
#check @FDRep.finrank_hom_simple_simple
-- ∀ {k G : Type u} [Field k] [Monoid G] [IsAlgClosed k]
--   (V W : FDRep k G) [Simple V] [Simple W],
--   Module.finrank k (V ⟶ W) = if Nonempty (V ≅ W) then 1 else 0
```

**COG use:** The current "no 8×8 intertwiner between V-rep and S+-rep" result in `muon_mass.yml` is an eigenvalue-spectrum heuristic (Python). This theorem would let us prove it structurally: define both representations as `FDRep k G` objects, prove each is `Simple`, prove they are non-isomorphic, and conclude the Hom-space has dimension 0.

**Catch:** `IsAlgClosed k` is required. The natural choice is `k = ℂ`, but `Mathlib.Data.Complex.Basic` transitively imports `ℝ` — which is **forbidden** by `CLAUDE.md §3`. A workaround: work over an abstract algebraically closed field of characteristic 0 (no ℝ required), or use `ZMod p` for a suitable prime if the representation is defined over a finite field. For the specific V/S+ question, the group is `Spin(8)` and the field needs to be characteristic 0 — so this is an open design question. **Action: investigate whether `FDRep` can be used over an abstract `IsAlgClosed` field without pulling in `ℝ`.**

### 0.4 `CliffordAlgebra.even` — even subalgebra

```lean
import Mathlib.LinearAlgebra.CliffordAlgebra.Even
#check CliffordAlgebra.even  -- Subalgebra R (CliffordAlgebra Q)
```

**COG use:** Triality acts on the three 8-dimensional representations of Spin(8) = Cl(8)⁺ (the even subalgebra of the Clifford algebra on ℝ⁸). If we ever formalize the triality circuit depth = 14 = dim(G₂) result in Lean (Category 4 in the proof roadmap), the `CliffordAlgebra.even` subalgebra is the correct algebraic home. The `foldr`/`foldl` recursion patterns documented in the Mathlib implementation notes give a reusable structure for CSE-style circuit depth arguments.

---

## 1. PhysLean

* **Repository:** `lean-phys-community/PhysLean` / physlean.com
* **Scope (early 2026):** Maxwell's equations, quantum harmonic oscillators, Wick's theorem, tight-binding model.
* **Relevance to COG:** PhysLean has **no** modules for octonions, the Fano plane, CFS, or causal graph theory. Its physics modules lean heavily on analysis (normed spaces, continuity, etc.) — precisely the **forbidden** import territory in `CLAUDE.md §3`.
* **Verdict:** Low direct value. Useful only as a project-structure reference (CI discipline, module layout). Do not attempt to depend on or reuse PhysLean modules in the core Lean kernel.

## 2. Mathlib4 — Specific High-Value Modules for COG

All imports below are confirmed allowed by `CLAUDE.md §3` (no analysis, no topology, no `Mathlib.Data.Real.*`).

| Module | What it gives COG | Priority |
|--------|------------------|----------|
| `Mathlib.LinearAlgebra.Matrix.GeneralLinearGroup.Defs` | `GL (Fin n) (ZMod p)` type + `Fintype` instance; `native_decide` proves cardinality | **High** — cross-check with `GaugeGroup.lean` |
| `Mathlib.Combinatorics.Configuration` | `ProjectivePlane` typeclass; incidence axioms | **Medium** — refactor `Fano.lean` |
| `Mathlib.RepresentationTheory.FDRep` | Formal Schur's lemma (`finrank_hom_simple_simple`) | **Medium** — needs design work on field choice |
| `Mathlib.LinearAlgebra.CliffordAlgebra.Even` | Even subalgebra + conjugation; relevant for triality | **Low-medium** — long-range triality work |
| `Mathlib.GroupTheory.SpecificGroups.SL` | `SpecialLinearGroup`; quotient/center machinery | **Medium** — for `SL(2,3)/Q₈ ≅ Z₃` (KOIDE-001 gap) |
| `Mathlib.RepresentationTheory.Character` | Character orthogonality, Z₃ irreps | **Medium** — Koide forcing via Z₃ |
| `Mathlib.Algebra.Group.Defs` | `NonUnitalNonAssocRing` hierarchy; distributivity without associativity | **Low** — `Oct` already has manual distributivity proofs |

## 3. Dedicated Physics / Octonion Formalization

*   **Causal Fermion Systems (CFS):** No public Lean 4 formalization exists. COG is the only formalization effort.
*   **Octonions in Mathlib:** No `Octonion` type in Mathlib4 (confirmed: searching the index finds quaternions but not octonions). Our `Oct` type in `ComplexOctonion.lean` is novel. Potential upstream contribution.
*   **`pygae/lean-ga`** (geometric/Clifford algebra): Partial Lean 4 formalization; most mature examples graduated to Mathlib. Useful as a design-pattern reference for `CliffordAlgebra.even`-based triality work, but do not depend on it directly.
*   **SciLean:** Lean 4 scientific computing library with OpenBLAS dependency. Not relevant to COG's discrete algebra kernel. Potentially relevant if Python simulations are ever migrated to Lean, but that is long-range.

## 4. Search and Discovery Tools

These are already integrated via the `lean-lsp` MCP, which provides `lean_leansearch`, `lean_loogle`, `lean_leanfinder`, `lean_state_search`, and `lean_hammer_premise`. No additional tooling is needed.

*   **Loogle** (loogle.lean-lang.org): Type-pattern search. Use `lean_loogle` tool.
*   **LeanSearch** (leansearch.net): Natural-language search. Use `lean_leansearch` tool.
*   **LeanExplore**: Multi-package semantic search. Similar coverage to the above; the `lean-explore` MCP would be redundant with existing `lean-lsp` tools.

## 5. Claims Needing Retraction / Correction from External Report

The following specific claims from the ChatGPT Deep Research report were checked and found to be incorrect against the pinned Mathlib version:

| Reported claim | Actual status |
|---------------|---------------|
| `Matrix.card_GL_field` lemma gives GL(n,q) cardinality | **Name does not exist.** Use `Fintype.card (GL (Fin n) (ZMod p))` + `native_decide`. |
| `FiniteField.card_units` gives unit group cardinality | **Name does not exist** in this form. |
| `NonUnitalNonAssocRing` instance for ℤ is automatic | **`inferInstance` fails**; the hierarchy requires explicit instance registration for Oct-style types. |
| CliffordAlgebra can replace Oct for triality without analysis imports | Technically true but CliffordAlgebra is defined over `CommRing R` with `Module R M` — still discrete/algebraic, no analysis. However, connecting Spin(8) triality to our specific Fano table is non-trivial and would be original work. |

## 6. Priority Summary for Near-Term Work

1.  **Cross-check `fano_aut_count` with `GL (Fin 3) (ZMod 2)`** — 1–2h, high confidence, makes the GL(3,2) isomorphism machine-verified rather than numerically coincident.
2.  **`ProjectivePlane` instance for Fano plane** — 4–6h, connects `Fano.lean` to Mathlib's incidence geometry library.
3.  **`SL(2,3)/Q₈ ≅ Z₃` via `SpecialLinearGroup`** — prerequisite for closing KOIDE-001; blocked on field-choice decision for `FDRep`.
4.  **Formal Schur's Lemma for V vs S+ reps** — medium effort; needs resolution of the `IsAlgClosed` / forbidden-ℝ tension.
5.  **Upstream contribution: `Oct` type** — COG's octonion formalization (component-by-component over ℤ, no ℝ) is novel; consider Mathlib PR once the type is stable and fully typeclass-annotated.
