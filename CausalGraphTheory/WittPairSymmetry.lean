/-
  CausalGraphTheory/WittPairSymmetry.lean

  Finite gate theorems for Witt-pair permutations and line support in the
  locked Fano convention.

  This file is intentionally separate from Spinors.lean to keep geometric
  symmetry checks (Fano/Witt combinatorics) modular and lightweight.
-/

import CausalGraphTheory.WittBasis

namespace CausalGraph

/-- Apply a permutation encoded as a length-7 list to a Fano point. -/
def applyPermList (sigma : List FanoPoint) (p : FanoPoint) : FanoPoint :=
  sigma.getD p.val 0

/-- Check whether a list permutation preserves Fano-line incidence. -/
def isFanoAutList (sigma : List FanoPoint) : Bool :=
  (List.finRange 7 : List FanoLine).all fun l =>
    let img := (fanoLinePoints l).map (applyPermList sigma)
    (List.finRange 7 : List FanoLine).any fun l' =>
      (fanoLinePoints l').all (fun p => img.contains p)

/-- Cyclic map of the three Witt pairs, preserving tuple orientation. -/
def wittPairCyclicPerm : List FanoPoint :=
  [4, 2, 5, 0, 3, 1, 6]

/-- A cycle variant with one internal pair flip. -/
def wittPairCyclicPermFlip : List FanoPoint :=
  [4, 2, 0, 5, 3, 1, 6]

/-- The orientation-preserving Witt-pair cycle is a Fano automorphism. -/
theorem wittPair_cyclic_perm_is_fano_aut :
    isFanoAutList wittPairCyclicPerm = true := by
  decide

/-- The flipped-cycle variant is not a Fano automorphism. -/
theorem wittPair_cyclic_perm_flip_not_fano_aut :
    isFanoAutList wittPairCyclicPermFlip = false := by
  decide

/-- Pair `(p,q)` lies on line `l` if both points are incident to `l`. -/
def pairOnLine (pq : Prod FanoPoint FanoPoint) (l : FanoLine) : Bool :=
  incident pq.1 l && incident pq.2 l

/-- All Fano lines supporting a given pair. -/
def pairSupportingLines (pq : Prod FanoPoint FanoPoint) : List FanoLine :=
  (List.finRange 7).filter (pairOnLine pq)

/-- The first Witt pair `(e6,e1)` is supported on line 2. -/
theorem wittPair0_supporting_line :
    pairSupportingLines (WittBasis.wittPair 0) = [2] := by
  decide

/-- The second Witt pair `(e2,e5)` is supported on line 4. -/
theorem wittPair1_supporting_line :
    pairSupportingLines (WittBasis.wittPair 1) = [4] := by
  decide

/-- The third Witt pair `(e3,e4)` is supported on line 5. -/
theorem wittPair2_supporting_line :
    pairSupportingLines (WittBasis.wittPair 2) = [5] := by
  decide

/-- Distinct Witt pairs are supported on distinct Fano lines. -/
theorem wittPairs_on_distinct_lines :
    forall j k : Fin 3, Ne j k ->
      Ne (pairSupportingLines (WittBasis.wittPair j))
         (pairSupportingLines (WittBasis.wittPair k)) := by
  decide

end CausalGraph

