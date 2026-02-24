/-
  CausalGraphTheory/VacuumStabilizerStructure.lean

  Structural diagnostics for the 24-element vacuum stabilizer:
  - exact element-order histogram,
  - involution count,
  - explicit order-3 cycle witness.

  These theorems are finite exhaustive checks over the canonical stabilizer list.
-/

import CausalGraphTheory.VacuumStabilizerQuotient

namespace CausalGraph

/-- n-th power of a 7-point permutation list under `composePermList`. -/
def permPow (sigma : List FanoPoint) (n : Nat) : List FanoPoint :=
  Nat.rec idPermList (fun _ acc => composePermList sigma acc) n

/-- Search order of a permutation in S7 within the universal bound lcm(1..7)=420. -/
def permOrderBounded (sigma : List FanoPoint) : Nat :=
  ((List.range 420).find? (fun n => permPow sigma (n + 1) == idPermList)).getD 0 + 1

/-- Order histogram (order, count) for vacuum stabilizer elements. -/
def vacuumStabilizerOrderHistogram : List (Nat × Nat) :=
  ((vacuumStabilizerList.map permOrderBounded).eraseDups).map fun n =>
    (n, (vacuumStabilizerList.filter (fun s => permOrderBounded s == n)).length)

/-- Exact order profile of the 24-element vacuum stabilizer. -/
theorem vacuumStabilizer_order_histogram :
    vacuumStabilizerOrderHistogram = [(1, 1), (2, 9), (4, 6), (3, 8)] := by
  native_decide

/-- Number of involutions (order-2 elements) in the vacuum stabilizer. -/
def vacuumStabilizerInvolutionCount : Nat :=
  (vacuumStabilizerList.filter (fun s => permOrderBounded s == 2)).length

/-- The vacuum stabilizer has 9 involutions. -/
theorem vacuumStabilizer_involution_count :
    vacuumStabilizerInvolutionCount = 9 := by
  native_decide

/-- Profile gate: the stabilizer does not have a single involution. -/
theorem vacuumStabilizer_not_single_involution :
    vacuumStabilizerInvolutionCount != 1 := by
  native_decide

/-- The canonical Witt-pair cycle has order 3 in the stabilizer. -/
theorem wittPair_cyclic_order_three :
    permPow wittPairCyclicPerm 3 = idPermList /\
    permPow wittPairCyclicPerm 1 != idPermList /\
    permPow wittPairCyclicPerm 2 != idPermList := by
  native_decide

end CausalGraph
