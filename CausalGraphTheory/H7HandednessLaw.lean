/-
  CausalGraphTheory/H7HandednessLaw.lean

  Primitive 3 of the H7 Kernel: the handedness law.

  Left-multiplication and right-multiplication by a Fano imaginary eᵢ on a distinct
  eⱼ (from the same Fano line) preserve the XOR index and flip the sign. This is the
  bridge between the sign function (Primitive 2) and the full multiplication table.

  Convention (CONVENTIONS.md §2, cyclic/anti-cyclic rules):
    If (i,j,k) is a directed Fano triple with ε_ijk = +1, then:
      eᵢ * eⱼ = +eₖ  (left-mul by eᵢ gives +)
      eⱼ * eᵢ = -eₖ  (right-mul by eᵢ gives -)
    So left and right multiplication give opposite signs.

  Allowed: Algebra, GroupTheory, LinearAlgebra, Combinatorics, Data.Fintype
  Forbidden: Mathlib.Analysis.*, Mathlib.Topology.*, Mathlib.Data.Real.*
-/

import Mathlib.Data.Fin.Basic
import Mathlib.Data.Fintype.Basic
import Mathlib.Tactic
import CausalGraphTheory.H7IndexFunction
import CausalGraphTheory.H7SignFunction

namespace H7HandednessLaw

open H7IndexFunction H7SignFunction

/-! ## Handedness definitions -/

/-- Left-multiplication sign: the sign you get from eᵢ * eⱼ.
    This is just h7Sign i j. -/
def leftMulSign (i j : H7Imag) : Int := h7Sign i j

/-- Right-multiplication sign: the sign you get from eⱼ * eᵢ (i.e., reversing order).
    This is h7Sign j i = -(h7Sign i j) by antisymmetry. -/
def rightMulSign (i j : H7Imag) : Int := h7Sign j i

/-! ## Core handedness theorems -/

/-- Theorem 1 (Handedness Sign Flip):
    Left-multiplication and right-multiplication by eᵢ on eⱼ (i ≠ j on a Fano line)
    produce opposite signs. This follows from antisymmetry of h7Sign. -/
theorem h7_handedness_sign_flip :
    ∀ (i j : H7Imag), i ≠ j →
      leftMulSign i j = -(rightMulSign i j) := by
  intro i j h
  simp only [leftMulSign, rightMulSign]
  exact h7Sign_antisymm i j h

/-- Theorem 2 (XOR Index Symmetry):
    The XOR index h7Index i j = h7Index j i — it is the same for left- and
    right-multiplication since XOR is commutative. -/
theorem h7_mul_index_preserved :
    ∀ (i j : H7Imag), h7Index i j = h7Index j i := by
  intro i j
  exact h7Index_symm i j

/-- Theorem 3 (Nonzero Sign for Distinct Fano Pairs):
    For distinct imaginaries, the left-multiplication sign is nonzero. -/
theorem h7_left_mul_sign_nonzero :
    ∀ (i j : H7Imag), i ≠ j →
      leftMulSign i j ≠ 0 := by
  intro i j h
  simp only [leftMulSign]
  exact h7Sign_consistent_with_index i j h

/-- Theorem 4 (Right-multiplication sign nonzero):
    For distinct imaginaries, the right-multiplication sign is also nonzero. -/
theorem h7_right_mul_sign_nonzero :
    ∀ (i j : H7Imag), i ≠ j →
      rightMulSign i j ≠ 0 := by
  intro i j h
  simp only [rightMulSign]
  have hne : j ≠ i := fun heq => h heq.symm
  exact h7Sign_consistent_with_index j i hne

/-- Theorem 5 (Handedness for all Fano lines):
    For every canonical oriented triple (i,j,k) in the Fano line list,
    the left sign equals +1 and the right sign equals -1. -/
theorem h7_fano_handedness_all_lines :
    ∀ triple ∈ fanoLines,
      let (i, j, _) := triple
      leftMulSign i j = 1 ∧ rightMulSign i j = -1 := by
  native_decide

/-- Theorem 6 (Left and right signs sum to zero on Fano lines):
    For each canonical Fano triple, leftMulSign i j + rightMulSign i j = 0. -/
theorem h7_fano_handedness_sum_zero :
    ∀ triple ∈ fanoLines,
      let (i, j, _) := triple
      leftMulSign i j + rightMulSign i j = 0 := by
  native_decide

/-- Theorem 7 (Global antisymmetry of left/right signs):
    For ALL distinct H7 imaginaries (not just Fano triples),
    leftMulSign i j + rightMulSign i j = 0. -/
theorem h7_handedness_antisymm_all :
    ∀ (i j : H7Imag), i ≠ j →
      leftMulSign i j + rightMulSign i j = 0 := by
  intro i j h
  simp only [leftMulSign, rightMulSign]
  have := h7Sign_antisymm i j h
  omega

end H7HandednessLaw

-- Leibniz