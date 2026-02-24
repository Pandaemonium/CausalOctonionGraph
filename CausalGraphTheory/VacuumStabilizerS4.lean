/-
  CausalGraphTheory/VacuumStabilizerS4.lean

  Explicit S4 identification via the vacuum stabilizer action on the
  four Fano lines not incident to the vacuum axis e7.
-/

import CausalGraphTheory.VacuumStabilizerQuotient

namespace CausalGraph

/-- Fano lines not incident to the vacuum axis (point 6). -/
def nonVacuumLines : List FanoLine :=
  (List.finRange 7).filter fun l => !(incident 6 l)

/-- Canonical order of non-vacuum lines in the locked convention. -/
def nonVacuumLinesCanonical : List FanoLine := [0, 1, 3, 6]

/-- Canonical non-vacuum line list is [0,1,3,6]. -/
theorem nonVacuumLines_eq_canonical :
    nonVacuumLines = nonVacuumLinesCanonical := by
  native_decide

/-- Image of a Fano line under a point permutation (found by finite search). -/
def imageLineUnder (sigma : List FanoPoint) (l : FanoLine) : FanoLine :=
  let img := (fanoLinePoints l).map (applyPermList sigma)
  ((List.finRange 7).find? fun l' =>
    (fanoLinePoints l').all (fun p => img.contains p)).getD 0

/-- Encode canonical non-vacuum lines [0,1,3,6] as indices [0,1,2,3]. -/
def nonVacLineToIdx (l : FanoLine) : Fin 4 :=
  if l == 0 then 0
  else if l == 1 then 1
  else if l == 3 then 2
  else 3

/-- Induced permutation on the four non-vacuum lines. -/
def inducedNonVacLinePerm (sigma : List FanoPoint) : List (Fin 4) :=
  [nonVacLineToIdx (imageLineUnder sigma 0),
   nonVacLineToIdx (imageLineUnder sigma 1),
   nonVacLineToIdx (imageLineUnder sigma 3),
   nonVacLineToIdx (imageLineUnder sigma 6)]

/-- Distinct induced permutations on the 4 non-vacuum lines. -/
def inducedNonVacLinePerms : List (List (Fin 4)) :=
  (vacuumStabilizerList.map inducedNonVacLinePerm).eraseDups

/-- Explicit lift from a 4-line permutation back to a stabilizer element. -/
def liftFromS4Perm (p : List (Fin 4)) : List FanoPoint :=
  (vacuumStabilizerList.find? fun sigma => inducedNonVacLinePerm sigma == p).getD idPermList

/-- Composition on 4-point permutations encoded as 4-lists. -/
def composePermList4 (a b : List (Fin 4)) : List (Fin 4) :=
  [a.getD (b.getD 0 0).val 0,
   a.getD (b.getD 1 0).val 0,
   a.getD (b.getD 2 0).val 0,
   a.getD (b.getD 3 0).val 0]

/-- All 24 permutations of the 4 non-vacuum lines are realized. -/
theorem inducedNonVacLinePerms_count :
    inducedNonVacLinePerms.length = 24 := by
  native_decide

/-- The induced non-vacuum-line action is exactly S4 (up to list order). -/
theorem inducedNonVacLinePerms_perm_S4 :
    List.Perm inducedNonVacLinePerms (List.permutations (List.finRange 4)) := by
  native_decide

/-- Every S4 permutation has a lifted stabilizer preimage. -/
theorem liftFromS4Perm_mem_vacuumStabilizer_bool :
    ((List.permutations (List.finRange 4)).all fun p =>
      vacuumStabilizerList.contains (liftFromS4Perm p)) = true := by
  native_decide

/-- Right-inverse check: induced action after lift returns the original S4 permutation. -/
theorem liftFromS4Perm_right_inv_bool :
    ((List.permutations (List.finRange 4)).all fun p =>
      inducedNonVacLinePerm (liftFromS4Perm p) == p) = true := by
  native_decide

/-- Left-inverse check: lift of the induced action returns the original stabilizer element. -/
theorem liftFromS4Perm_left_inv_bool :
    (vacuumStabilizerList.all fun sigma =>
      liftFromS4Perm (inducedNonVacLinePerm sigma) == sigma) = true := by
  native_decide

/-- Induced action on non-vacuum lines is a homomorphism on the stabilizer. -/
theorem inducedNonVacLinePerm_hom_on_vacuumStabilizer_bool :
    (vacuumStabilizerList.all fun sigma =>
      vacuumStabilizerList.all fun tau =>
        inducedNonVacLinePerm (composePermList sigma tau) ==
          composePermList4 (inducedNonVacLinePerm sigma) (inducedNonVacLinePerm tau)) = true := by
  native_decide

/-- Faithfulness check: only identity acts trivially on non-vacuum lines. -/
theorem inducedNonVacLinePerm_faithful_bool :
    (vacuumStabilizerList.filter (fun sigma => inducedNonVacLinePerm sigma == [0, 1, 2, 3])).length = 1 := by
  native_decide

/-- The induced action map is injective on the stabilizer list. -/
theorem inducedNonVacLinePerm_injective_bool :
    (vacuumStabilizerList.all fun sigma =>
      vacuumStabilizerList.all fun tau =>
        (inducedNonVacLinePerm sigma == inducedNonVacLinePerm tau) == (sigma == tau)) = true := by
  native_decide

/-- Combined summary: stabilizer action on 4 non-vacuum lines is faithful and S4-surjective. -/
theorem vacuumStabilizer_action_on_nonVacLines_S4 :
    inducedNonVacLinePerms.length = 24 /\
    List.Perm inducedNonVacLinePerms (List.permutations (List.finRange 4)) /\
    (vacuumStabilizerList.filter (fun sigma => inducedNonVacLinePerm sigma == [0, 1, 2, 3])).length = 1 := by
  exact ⟨inducedNonVacLinePerms_count, inducedNonVacLinePerms_perm_S4, inducedNonVacLinePerm_faithful_bool⟩

/-- Explicit list-level isomorphism witness summary between stabilizer and S4 action. -/
theorem vacuumStabilizer_explicit_iso_S4_bool :
    ((List.permutations (List.finRange 4)).all fun p =>
      inducedNonVacLinePerm (liftFromS4Perm p) == p) = true /\
    (vacuumStabilizerList.all fun sigma =>
      liftFromS4Perm (inducedNonVacLinePerm sigma) == sigma) = true := by
  exact ⟨liftFromS4Perm_right_inv_bool, liftFromS4Perm_left_inv_bool⟩

end CausalGraph
