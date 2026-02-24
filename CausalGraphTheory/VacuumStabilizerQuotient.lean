/-
  CausalGraphTheory/VacuumStabilizerQuotient.lean

  Structural finite-group checks for the vacuum stabilizer action:
  - closure and inverses (by exhaustive finite verification),
  - induced action homomorphism to color permutations,
  - kernel size and normality,
  - explicit transposition witness.
-/

import CausalGraphTheory.VacuumStabilizerAction

namespace CausalGraph

/-- Composition of point permutations encoded as 7-lists. -/
def composePermList (sigma tau : List FanoPoint) : List FanoPoint :=
  (List.finRange 7).map fun p => applyPermList sigma (applyPermList tau p)

/-- Identity permutation on the 7 Fano points. -/
def idPermList : List FanoPoint :=
  List.finRange 7

/-- Functional inverse in the vacuum stabilizer, found by finite search. -/
def inverseInVacuumStabilizer (sigma : List FanoPoint) : List FanoPoint :=
  (vacuumStabilizerList.find? fun tau =>
    composePermList sigma tau == idPermList && composePermList tau sigma == idPermList).getD idPermList

/-- Composition on 3-color permutations encoded as 3-lists. -/
def composeColorPerm3 (a b : List (Fin 3)) : List (Fin 3) :=
  [a.getD (b.getD 0 0).val 0,
   a.getD (b.getD 1 0).val 0,
   a.getD (b.getD 2 0).val 0]

/-- Kernel of the induced color action. -/
def stabilizerKernelList : List (List FanoPoint) :=
  vacuumStabilizerList.filter (fun sigma => inducedColorPerm sigma == [0, 1, 2])

/-- The vacuum stabilizer is closed under composition (boolean exhaustive check). -/
theorem vacuumStabilizer_closed_comp_bool :
    (vacuumStabilizerList.all fun sigma =>
      vacuumStabilizerList.all fun tau =>
        vacuumStabilizerList.contains (composePermList sigma tau)) = true := by
  native_decide

/-- The identity permutation is in the vacuum stabilizer. -/
theorem idPermList_in_vacuumStabilizer :
    vacuumStabilizerList.contains idPermList = true := by
  native_decide

/-- Finite-search inverse satisfies two-sided inverse equations in the stabilizer. -/
theorem inverseInVacuumStabilizer_spec_bool :
    (vacuumStabilizerList.all fun sigma =>
      vacuumStabilizerList.contains (inverseInVacuumStabilizer sigma) &&
      composePermList sigma (inverseInVacuumStabilizer sigma) == idPermList &&
      composePermList (inverseInVacuumStabilizer sigma) sigma == idPermList) = true := by
  native_decide

/-- Induced color action is a homomorphism on the vacuum stabilizer. -/
theorem inducedColorPerm_hom_on_vacuumStabilizer_bool :
    (vacuumStabilizerList.all fun sigma =>
      vacuumStabilizerList.all fun tau =>
        inducedColorPerm (composePermList sigma tau) ==
          composeColorPerm3 (inducedColorPerm sigma) (inducedColorPerm tau)) = true := by
  native_decide

/-- Kernel size is 4. -/
theorem stabilizerKernelList_count :
    stabilizerKernelList.length = 4 := by
  native_decide

/-- Kernel is closed under composition. -/
theorem stabilizerKernel_closed_comp_bool :
    (stabilizerKernelList.all fun sigma =>
      stabilizerKernelList.all fun tau =>
        stabilizerKernelList.contains (composePermList sigma tau)) = true := by
  native_decide

/-- Kernel is normal under stabilizer conjugation. -/
theorem stabilizerKernel_normal_bool :
    (vacuumStabilizerList.all fun g =>
      stabilizerKernelList.all fun k =>
        stabilizerKernelList.contains
          (composePermList g (composePermList k (inverseInVacuumStabilizer g)))) = true := by
  native_decide

/-- Quotient cardinality by kernel is 6 (24 / 4). -/
theorem stabilizer_kernel_index_six :
    vacuumStabilizerList.length / stabilizerKernelList.length = 6 := by
  native_decide

/-- Canonical transposition witness on color labels. -/
def wittPair_swap01_perm : List FanoPoint :=
  [1, 0, 2, 3, 5, 4, 6]

/-- The transposition witness lies in the vacuum stabilizer. -/
theorem wittPair_swap01_in_vacuumStabilizer :
    vacuumStabilizerList.contains wittPair_swap01_perm = true := by
  native_decide

/-- The transposition witness induces the color swap [0,1,2] |-> [1,0,2]. -/
theorem wittPair_swap01_inducedColorPerm :
    inducedColorPerm wittPair_swap01_perm = [1, 0, 2] := by
  native_decide

end CausalGraph
