import CausalGraphTheory.Fano
import Mathlib

/-!
  CausalGraphTheory/AlphaCombinatoricBridge.lean

  Exact combinatoric bridge constants for ALPHA-001.

  Locked bridge form:

    alphaBridgeCombinatoric = 1 / (L^2 * P - D)

  where:
  - `L` is the Fano line cardinality,
  - `P` is points per Fano line,
  - `D` is a fixed finite-cardinality degeneracy subtraction term.

  This file formalizes exact arithmetic identities for the bridge constants and
  the resulting rational bridge value. It does not claim continuum closure by
  itself.
-/

namespace CausalGraph

/-- Number of Fano lines. -/
def fanoLineCard : Nat := Fintype.card FanoLine

theorem fanoLineCard_eq_seven : fanoLineCard = 7 := by
  unfold fanoLineCard
  native_decide

/-- Number of points on each Fano line. -/
def pointsPerFanoLine : Nat := 3

theorem pointsPerFanoLine_exact (l : FanoLine) :
    (fanoLinePoints l).length = pointsPerFanoLine := by
  simpa [pointsPerFanoLine] using each_line_has_three_points l

/-- Fixed degeneracy subtraction term in the locked bridge family. -/
def degeneracySubtractCard : Nat := 2

/-- Denominator for the locked alpha bridge map. -/
def alphaDenominatorCombinatoric : Nat :=
  fanoLineCard * fanoLineCard * pointsPerFanoLine - degeneracySubtractCard

theorem alphaDenominatorCombinatoric_eq_145 :
    alphaDenominatorCombinatoric = 145 := by
  unfold alphaDenominatorCombinatoric
  rw [fanoLineCard_eq_seven]
  norm_num [pointsPerFanoLine, degeneracySubtractCard]

/-- UV anchor from pure Fano line-card combinatorics. -/
def alphaUvAnchorCombinatoric : Rat :=
  1 / ((fanoLineCard * fanoLineCard : Nat) : Rat)

theorem alphaUvAnchorCombinatoric_eq_one_div_49 :
    alphaUvAnchorCombinatoric = (1 : Rat) / 49 := by
  unfold alphaUvAnchorCombinatoric
  rw [fanoLineCard_eq_seven]
  norm_num

/-- Locked alpha bridge value. -/
def alphaBridgeCombinatoric : Rat :=
  1 / (alphaDenominatorCombinatoric : Rat)

theorem alphaBridgeCombinatoric_eq_one_div_145 :
    alphaBridgeCombinatoric = (1 : Rat) / 145 := by
  unfold alphaBridgeCombinatoric
  rw [alphaDenominatorCombinatoric_eq_145]
  norm_num

theorem alphaBridgeCombinatoric_pos :
    (0 : Rat) < alphaBridgeCombinatoric := by
  rw [alphaBridgeCombinatoric_eq_one_div_145]
  norm_num

theorem alphaBridgeCombinatoric_lt_alphaUvAnchor :
    alphaBridgeCombinatoric < alphaUvAnchorCombinatoric := by
  rw [alphaBridgeCombinatoric_eq_one_div_145, alphaUvAnchorCombinatoric_eq_one_div_49]
  norm_num

theorem alphaBridgeCombinatoric_lt_one_div_137 :
    alphaBridgeCombinatoric < (1 : Rat) / 137 := by
  rw [alphaBridgeCombinatoric_eq_one_div_145]
  norm_num

theorem alphaBridgeCombinatoric_gt_one_div_150 :
    (1 : Rat) / 150 < alphaBridgeCombinatoric := by
  rw [alphaBridgeCombinatoric_eq_one_div_145]
  norm_num

end CausalGraph

