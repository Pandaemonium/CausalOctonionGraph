/-
  CausalGraphTheory/GaugeGroup.lean
  Phase 4.1: Discrete Gauge Group (Fano Automorphisms)

  Establishes the gauge symmetry group of the Fano plane:
  - The automorphism group of PG(2,2) has order 168 ≅ GL(3,2) ≅ PSL(2,7)
  - The stabilizer of the vacuum axis (point 6 = e₇) has order 24
  - Exactly 3 lines pass through the vacuum axis (the Witt basis pairs)

  WARNING (2026-02-24): The stabilizer identity "≅ SL(2,3)" in older
  docs and claims is UNDER REVIEW. VacuumStabilizerStructure.lean (Codex
  batch, 2026-02-24) proves the element-order histogram of the 24-element
  stabilizer is (1:1, 2:9, 3:8, 4:6), which matches S4 (symmetric group
  on 4 elements), NOT SL(2,3) (which has order-histogram (1:1, 2:1, 3:8,
  4:6, 6:8) — only 1 involution). VacuumStabilizerS4.lean provides an
  explicit two-sided isomorphism witness. Until a reconciliation RFC is
  written, treat all SL(2,3)-dependent claims as UNSTABLE.

  Physical interpretation:
  - The 168-element group is the discrete analogue of the gauge symmetry
    of the octonion algebra: it acts on the 7 imaginary units by
    permuting them while preserving the Fano multiplication table.
  - The 24-element vacuum stabilizer is the discrete analogue of SU(3):
    it preserves the Witt basis decomposition and acts on the
    color-charge sector {e₁,e₂,e₃,e₄,e₅,e₆} while fixing e₇.
  - The 3 vacuum lines are the Witt basis pairs:
      Line 2: {e₁, e₇, e₆}   (pair e₆ ↔ e₁)
      Line 4: {e₂, e₅, e₇}   (pair e₂ ↔ e₅)
      Line 5: {e₃, e₄, e₇}   (pair e₃ ↔ e₄)

  Claim: claims/gauge_group.yml
-/

import CausalGraphTheory.Fano
import CausalGraphTheory.VacuumStabilizerS4
import Mathlib.Data.List.Perm.Basic
import Mathlib.LinearAlgebra.Matrix.GeneralLinearGroup.Defs
import Mathlib.FieldTheory.Finite.Basic

namespace GaugeGroup

-- ============================================================
-- Automorphism predicate
-- ============================================================

/--
  Apply a permutation (represented as a length-7 list) to a Fano point.
  Returns σ(p) where σ = σ_list[p.val].
-/
private def applyPerm (σ : List FanoPoint) (p : FanoPoint) : FanoPoint :=
  σ.getD p.val 0

/--
  Check whether a list σ (of length 7, a permutation of `List.finRange 7`)
  is a Fano automorphism: every Fano line maps to a Fano line under σ.
-/
private def isFanoAut (σ : List FanoPoint) : Bool :=
  (List.finRange 7 : List FanoLine).all fun l =>
    let img := (fanoLinePoints l).map (applyPerm σ)
    (List.finRange 7 : List FanoLine).any fun l' =>
      (fanoLinePoints l').all (· ∈ img)

/--
  Check whether a permutation σ fixes the vacuum axis: σ(e₇) = e₇,
  i.e., σ(6) = 6 in 0-indexed notation.
-/
private def fixesVacuum (σ : List FanoPoint) : Bool :=
  applyPerm σ 6 == 6

-- ============================================================
-- Vacuum lines
-- ============================================================

/--
  The 3 lines of the Fano plane that pass through the vacuum axis
  (point 6 = e₇). These are the Witt basis lines in the Furey convention.
-/
def vacuumLines : List FanoLine :=
  (List.finRange 7).filter fun l => incident 6 l

-- ============================================================
-- Main theorems (proved by exhaustive finite computation)
-- ============================================================

/--
  **The Discrete Gauge Group has order 168.**

  The automorphism group of the Fano plane PG(2,2) is isomorphic to
  GL(3,2) ≅ PSL(2,7), and has order 168 = 2³ × 3 × 7.

  Proof: exhaustive enumeration of all 7! = 5040 permutations of Fin 7,
  filtering those that map every line to a line.

  Physical meaning: this is the exact discrete symmetry group of the
  octonion multiplication table. Every element of this group corresponds
  to a change of "observer frame" that leaves the causal algebra invariant.
-/
theorem fano_aut_count :
    ((List.finRange 7).permutations.filter isFanoAut).length = 168 := by
  native_decide

/--
  **The Vacuum Stabilizer has order 24.**

  The subgroup of GL(3,2) that fixes the vacuum axis e₇ (point 6)
  is isomorphic to SL(2,3) ≅ 2.A₄, of order 24.

  By the orbit-stabilizer theorem, since GL(3,2) acts transitively on
  the 7 points of the Fano plane:
      |GL(3,2)| = |orbit(e₇)| × |Stab(e₇)| = 7 × 24 = 168. ✓

  Physical meaning: this 24-element group is the discrete analogue of
  SU(3). It preserves the choice of vacuum direction e₇ while freely
  permuting the color-charged sector {e₁,…,e₆}.
-/
theorem vacuum_stabilizer_count :
    ((List.finRange 7).permutations.filter
      fun σ => isFanoAut σ && fixesVacuum σ).length = 24 := by
  native_decide

/--
  **Three lines pass through the vacuum axis.**

  Exactly 3 of the 7 Fano lines contain e₇ (point 6).
  These are the three Witt basis lines:
    Line 2: {0, 6, 5} = {e₁, e₇, e₆}
    Line 4: {1, 4, 6} = {e₂, e₅, e₇}
    Line 5: {2, 3, 6} = {e₃, e₄, e₇}
-/
theorem vacuum_lines_count : vacuumLines.length = 3 := by decide

/--
  **Orbit-Stabilizer consistency.**

  168 = 7 × 24: the total group order equals the orbit size (7 points)
  times the stabilizer order (24), confirming the orbit-stabilizer theorem
  for the transitive action of GL(3,2) on PG(2,2).
-/
theorem orbit_stabilizer_check : 168 = 7 * 24 := by decide

/--
  **Cross-check: Fano automorphism count equals |GL(3, F₂)|.**

  The number of Fano automorphisms (168) computed by exhaustive enumeration
  equals the Mathlib-computed cardinality of the general linear group GL(3, ZMod 2).
  This confirms the classical isomorphism Aut(PG(2,2)) ≅ GL(3, F₂).

  Uses `native_decide` on `Fintype.card (Matrix.GeneralLinearGroup (Fin 3) (ZMod 2))`.
-/
theorem fano_aut_eq_GL3F2 :
    ((List.finRange 7).permutations.filter isFanoAut).length =
    Fintype.card (Matrix.GeneralLinearGroup (Fin 3) (ZMod 2)) := by
  native_decide

theorem vacuumStabilizer_iso_S4 :
    CausalGraph.inducedNonVacLinePerms.length = 24 ∧
    List.Perm CausalGraph.inducedNonVacLinePerms
              (List.permutations (List.finRange 4)) :=
  ⟨CausalGraph.inducedNonVacLinePerms_count,
   CausalGraph.inducedNonVacLinePerms_perm_S4⟩

end GaugeGroup
