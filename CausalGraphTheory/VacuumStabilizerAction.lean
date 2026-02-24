/-
  CausalGraphTheory/VacuumStabilizerAction.lean

  Finite action theorems for the vacuum stabilizer on Witt-pair color labels.

  This file keeps "vacuum stabilizer -> induced S3 action" results separate
  from the base Fano gate checks in WittPairSymmetry.lean.
-/

import CausalGraphTheory.WittPairSymmetry

namespace CausalGraph

/-- Check whether a permutation fixes the vacuum axis e7 (point 6). -/
def fixesVacuumList (sigma : List FanoPoint) : Bool :=
  applyPermList sigma 6 == 6

/-- All Fano automorphisms that fix the vacuum axis. -/
def vacuumStabilizerList : List (List FanoPoint) :=
  (List.finRange 7).permutations.filter
    (fun sigma => isFanoAutList sigma && fixesVacuumList sigma)

/-- Equality test for unordered Witt-pair images. -/
def sameUnorderedPair (p q : Prod FanoPoint FanoPoint) : Bool :=
  (p.1 == q.1 && p.2 == q.2) || (p.1 == q.2 && p.2 == q.1)

/-- Induced color index j |-> k from a vacuum-stabilizer permutation. -/
def pairImageColor (sigma : List FanoPoint) (j : Fin 3) : Fin 3 :=
  let pq := WittBasis.wittPair j
  let img : Prod FanoPoint FanoPoint :=
    (applyPermList sigma pq.1, applyPermList sigma pq.2)
  if sameUnorderedPair img (WittBasis.wittPair 0) then 0
  else if sameUnorderedPair img (WittBasis.wittPair 1) then 1
  else 2

/-- Induced permutation on the three Witt-pair color labels. -/
def inducedColorPerm (sigma : List FanoPoint) : List (Fin 3) :=
  [pairImageColor sigma 0, pairImageColor sigma 1, pairImageColor sigma 2]

/-- Distinct color permutations induced by vacuum stabilizer elements. -/
def inducedColorPerms : List (List (Fin 3)) :=
  (vacuumStabilizerList.map inducedColorPerm).eraseDups

/-- Size of the vacuum stabilizer list. -/
theorem vacuumStabilizerList_count :
    vacuumStabilizerList.length = 24 := by
  native_decide

/-- The Witt-pair 3-cycle is itself a vacuum-stabilizer element. -/
theorem wittPair_cyclic_in_vacuumStabilizerList :
    vacuumStabilizerList.contains wittPairCyclicPerm = true := by
  native_decide

/-- Induced color action of the Witt-pair cycle: [0,1,2] |-> [1,2,0]. -/
theorem wittPair_cyclic_inducedColorPerm :
    inducedColorPerm wittPairCyclicPerm = [1, 2, 0] := by
  native_decide

/-- The induced action contains exactly six distinct color permutations. -/
theorem inducedColorPerms_count :
    inducedColorPerms.length = 6 := by
  native_decide

/-- Fiber sizes of the induced action map over the canonical S3 permutation list. -/
def inducedColorPermFiberSizes : List Nat :=
  (List.permutations (List.finRange 3)).map fun p =>
    (vacuumStabilizerList.filter (fun sigma => inducedColorPerm sigma == p)).length

/-- Every induced S3 color permutation has exactly 4 stabilizer preimages (24 = 6 * 4). -/
theorem inducedColorPermFiberSizes_eq :
    inducedColorPermFiberSizes = [4, 4, 4, 4, 4, 4] := by
  native_decide

/-- The induced action is exactly S3 on three color labels (up to list order). -/
theorem inducedColorPerms_perm_S3 :
    List.Perm inducedColorPerms (List.permutations (List.finRange 3)) := by
  native_decide

/-- Membership characterization of induced color permutations. -/
theorem inducedColorPerms_mem_iff (p : List (Fin 3)) :
    List.Mem p inducedColorPerms <-> List.Mem p (List.permutations (List.finRange 3)) := by
  exact inducedColorPerms_perm_S3.mem_iff

/-- Every S3 color permutation is realized by some vacuum-stabilizer element. -/
theorem color_perm_realized_by_vacuum_stabilizer
    (p : List (Fin 3))
    (hp : List.Mem p (List.permutations (List.finRange 3))) :
    Exists fun sigma => List.Mem sigma vacuumStabilizerList /\ inducedColorPerm sigma = p := by
  have hp' : List.Mem p inducedColorPerms :=
    (inducedColorPerms_mem_iff p).2 hp
  have hExists : Exists fun sigma => List.Mem sigma vacuumStabilizerList /\ inducedColorPerm sigma = p := by
    simpa [inducedColorPerms] using (List.mem_eraseDups.mp hp')
  exact hExists

end CausalGraph
