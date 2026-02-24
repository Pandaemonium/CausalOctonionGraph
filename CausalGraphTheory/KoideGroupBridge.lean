/-
  CausalGraphTheory/KoideGroupBridge.lean

  Group-to-Koide bridge lemmas:
  - explicit Z3 cycle action on Witt-pair color labels,
  - algebraic Brannen consequences from Z3 constraints,
  - pipeline theorem: Z3 + B^2 = 2 implies Koide Q = 2/3 equation.
-/

import CausalGraphTheory.Koide
import CausalGraphTheory.VacuumStabilizerStructure

namespace CausalGraph

/-- Color action of the canonical cycle and its first powers. -/
theorem wittPair_cyclic_color_powers :
    inducedColorPerm (permPow wittPairCyclicPerm 1) = [1, 2, 0] /\
    inducedColorPerm (permPow wittPairCyclicPerm 2) = [2, 0, 1] /\
    inducedColorPerm (permPow wittPairCyclicPerm 3) = [0, 1, 2] := by
  native_decide

/-- Z3 trig constraints imply fixed quadratic norm: c0^2 + c1^2 + c2^2 = 3/2. -/
theorem z3_sumprod_implies_sumsq (c0 c1 c2 : Rat)
    (hsum : c0 + c1 + c2 = 0)
    (hprod : c0 * c1 + c1 * c2 + c2 * c0 = -3/4) :
    c0 ^ 2 + c1 ^ 2 + c2 ^ 2 = 3/2 := by
  have h1 : (c0 + c1 + c2) ^ 2 =
      c0 ^ 2 + c1 ^ 2 + c2 ^ 2 + 2 * (c0 * c1 + c1 * c2 + c2 * c0) := by
    ring
  have h2 : (c0 + c1 + c2) ^ 2 = 0 := by
    rw [hsum]
    ring
  linarith

/-- Brannen ansatz with Z3 constraints and B^2 = 2 implies the Koide SOS condition. -/
theorem brannen_sos_from_z3_and_b2 (A B c0 c1 c2 : Rat)
    (hsum : c0 + c1 + c2 = 0)
    (hprod : c0 * c1 + c1 * c2 + c2 * c0 = -3/4)
    (hB2 : B ^ 2 = 2) :
    (A * (1 + B * c0)) ^ 2 + (A * (1 + B * c1)) ^ 2 + (A * (1 + B * c2)) ^ 2 =
      4 *
        ((A * (1 + B * c0)) * (A * (1 + B * c1)) +
         (A * (1 + B * c1)) * (A * (1 + B * c2)) +
         (A * (1 + B * c2)) * (A * (1 + B * c0))) := by
  have hss : c0 ^ 2 + c1 ^ 2 + c2 ^ 2 = 3/2 :=
    z3_sumprod_implies_sumsq c0 c1 c2 hsum hprod
  have hsquare_form :
      (A * (1 + B * c0)) ^ 2 + (A * (1 + B * c1)) ^ 2 + (A * (1 + B * c2)) ^ 2 =
      A ^ 2 * (3 + 2 * B * (c0 + c1 + c2) + B ^ 2 * (c0 ^ 2 + c1 ^ 2 + c2 ^ 2)) := by
    ring
  have hpair_form :
      (A * (1 + B * c0)) * (A * (1 + B * c1)) +
      (A * (1 + B * c1)) * (A * (1 + B * c2)) +
      (A * (1 + B * c2)) * (A * (1 + B * c0)) =
      A ^ 2 * (3 + B * ((c0 + c1) + (c1 + c2) + (c2 + c0)) +
        B ^ 2 * (c0 * c1 + c1 * c2 + c2 * c0)) := by
    ring
  have hsum_pairs : ((c0 + c1) + (c1 + c2) + (c2 + c0)) = 2 * (c0 + c1 + c2) := by
    ring
  rw [hsquare_form, hpair_form, hsum_pairs]
  rw [hsum, hss, hprod, hB2]
  ring

/-- Pipeline corollary: Brannen Z3 + B^2 = 2 gives Koide Q = 2/3 equation. -/
theorem brannen_koide_from_z3_and_b2 (A B c0 c1 c2 : Rat)
    (hsum : c0 + c1 + c2 = 0)
    (hprod : c0 * c1 + c1 * c2 + c2 * c0 = -3/4)
    (hB2 : B ^ 2 = 2) :
    3 * ((A * (1 + B * c0)) ^ 2 + (A * (1 + B * c1)) ^ 2 + (A * (1 + B * c2)) ^ 2) =
      2 * ((A * (1 + B * c0)) + (A * (1 + B * c1)) + (A * (1 + B * c2))) ^ 2 := by
  apply koide_ratio_is_two_thirds_of_sos
  exact brannen_sos_from_z3_and_b2 A B c0 c1 c2 hsum hprod hB2

end CausalGraph
