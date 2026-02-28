/-
  CausalGraphTheory/H7SignFunction.lean

  Primitive 2 of the H7 Kernel: the sign function from the oriented Fano line convention.

  The 7 canonical positive triples (from CONVENTIONS.md §2):
    L1: (1,2,3)  e1*e2 = +e3
    L2: (1,4,5)  e1*e4 = +e5
    L3: (1,7,6)  e1*e7 = +e6
    L4: (2,4,6)  e2*e4 = +e6
    L5: (2,5,7)  e2*e5 = +e7
    L6: (3,4,7)  e3*e4 = +e7
    L7: (3,6,5)  e3*e6 = +e5

  Allowed: Algebra, GroupTheory, LinearAlgebra, Combinatorics, Data.Fintype
  Forbidden: Mathlib.Analysis.*, Mathlib.Topology.*, Mathlib.Data.Real.*
-/

import Mathlib.Data.Fin.Basic
import Mathlib.Data.Fintype.Basic
import Mathlib.Tactic
import CausalGraphTheory.H7IndexFunction

namespace H7SignFunction

open H7IndexFunction

/-! ## Oriented Fano lines -/

/-- A structure representing an oriented Fano line triple (i,j,k) meaning ei*ej = +ek. -/
structure OrientedFanoLine where
  fst : H7Imag
  snd : H7Imag
  thd : H7Imag

/-! ## Helper constructors for H7Imag elements -/

private def e1 : H7Imag := ⟨⟨1, by norm_num⟩, by norm_num⟩
private def e2 : H7Imag := ⟨⟨2, by norm_num⟩, by norm_num⟩
private def e3 : H7Imag := ⟨⟨3, by norm_num⟩, by norm_num⟩
private def e4 : H7Imag := ⟨⟨4, by norm_num⟩, by norm_num⟩
private def e5 : H7Imag := ⟨⟨5, by norm_num⟩, by norm_num⟩
private def e6 : H7Imag := ⟨⟨6, by norm_num⟩, by norm_num⟩
private def e7 : H7Imag := ⟨⟨7, by norm_num⟩, by norm_num⟩

/-- The 7 canonical oriented Fano triples from CONVENTIONS.md §2.
    Each triple (i,j,k) means ei * ej = +ek. -/
def fanoLines : List (H7Imag × H7Imag × H7Imag) :=
  [ (e1, e2, e3)
  , (e1, e4, e5)
  , (e1, e7, e6)
  , (e2, e4, e6)
  , (e2, e5, e7)
  , (e3, e4, e7)
  , (e3, e6, e5)
  ]

/-! ## The sign function -/

/-- Check if (i, j) is a positive cyclic pair from any oriented Fano triple. -/
def isPositivePair (i j : H7Imag) : Bool :=
  fanoLines.any (fun triple => triple.1 == i && triple.2.1 == j) ||
  fanoLines.any (fun triple => triple.2.1 == i && triple.2.2 == j) ||
  fanoLines.any (fun triple => triple.2.2 == i && triple.1 == j)

/-- h7Sign i j returns +1 if (i,j) is a positive cyclic pair, -1 if reversed, 0 if i=j. -/
def h7Sign (i j : H7Imag) : Int :=
  if i == j then 0
  else if isPositivePair i j then 1
  else if isPositivePair j i then -1
  else 0

/-! ## Required theorems -/

/-- The sign function is antisymmetric for distinct elements. -/
theorem h7Sign_antisymm (i j : H7Imag) (h : i ≠ j) :
    h7Sign i j = -(h7Sign j i) := by
  have key : ∀ (a b : H7Imag), a ≠ b → h7Sign a b = -(h7Sign b a) := by
    native_decide
  exact key i j h

/-- The sign of an element with itself is zero. -/
theorem h7Sign_self_zero (i : H7Imag) :
    h7Sign i i = 0 := by
  have key : ∀ (a : H7Imag), h7Sign a a = 0 := by native_decide
  exact key i

/-- Every distinct pair on a Fano line has a nonzero sign. -/
theorem h7Sign_consistent_with_index (i j : H7Imag) (h : i ≠ j) :
    h7Sign i j ≠ 0 := by
  have key : ∀ (a b : H7Imag), a ≠ b → h7Sign a b ≠ 0 := by
    native_decide
  exact key i j h

/-- All canonical oriented triples have sign +1 on their defining pair. -/
theorem h7Sign_all_lines : ∀ triple ∈ fanoLines,
    let (i, j, _) := triple; h7Sign i j = 1 := by
  native_decide

end H7SignFunction

-- Leibniz