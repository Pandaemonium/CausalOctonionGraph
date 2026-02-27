/-
  CausalGraphTheory/GaugeSL23.lean
  GAUGE-001 sub-lemma: SL(2,3) order-24 subchain and S4 non-abelian witness.

  Establishes:
  1. |SL(2,3)| = 24  (binary tetrahedral group)
  2. |S4| = 24        (symmetric group on 4 elements)
  3. Equal orders    (same-order embedding context)
  4. S4 is non-abelian

  All proofs use native_decide / decide on finite decidable propositions.
  No sorry.
-/

import Mathlib.LinearAlgebra.Matrix.SpecialLinearGroup
import Mathlib.Data.ZMod.Basic
import Mathlib.Data.Fintype.Card
import Mathlib.GroupTheory.Perm.Basic
import Mathlib.Data.Fin.Basic

namespace GaugeSL23

/--
  **SL(2,3) has order 24.**
  The special linear group SL(2, F₃) has exactly 24 elements (binary tetrahedral group).
  Proof: exhaustive finite computation via native_decide.
-/
theorem sl23_order_eq :
    Fintype.card (Matrix.SpecialLinearGroup (Fin 2) (ZMod 3)) = 24 := by
  native_decide

/--
  **S4 has order 24.**
  The symmetric group on 4 elements Equiv.Perm (Fin 4) ≅ S₄ has exactly 24 = 4! elements.
  Proof: exhaustive finite computation via native_decide.
-/
theorem s4_order_eq' :
    Fintype.card (Equiv.Perm (Fin 4)) = 24 := by
  native_decide

/--
  **SL(2,3) and S4 have equal order.**
  Both groups have order 24, establishing the same-order embedding context for GAUGE-001.
-/
theorem sl23_s4_same_order :
    Fintype.card (Matrix.SpecialLinearGroup (Fin 2) (ZMod 3)) =
    Fintype.card (Equiv.Perm (Fin 4)) := by
  simp [sl23_order_eq, s4_order_eq']

/--
  **S4 is non-abelian.**
  Witness: swap(0,1) and swap(1,2) do not commute.
  Proof: explicit witness checked by decide.
-/
theorem s4_nonabelian :
    ¬ Commutative (· * · : Equiv.Perm (Fin 4) → _ → _) := by
  intro h
  let σ : Equiv.Perm (Fin 4) := Equiv.swap 0 1
  let τ : Equiv.Perm (Fin 4) := Equiv.swap 1 2
  have hne : σ * τ ≠ τ * σ := by decide
  exact hne (h σ τ)

end GaugeSL23
-- Leibniz