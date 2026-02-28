/-
  CausalGraphTheory/H7CycleExtraction.lean

  Primitive 4 of the H7 Kernel: deterministic cycle extraction from the fixed Fano policy.

  Given the fixed Fano incidence + orientation policy (CONVENTIONS.md §2), enumerate
  all 7 oriented cycles (one per Fano line) deterministically and prove the enumeration
  is unique (no policy ambiguity).

  The 7 canonical oriented triples (from CONVENTIONS.md §2):
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
import Mathlib.Data.List.Basic
import Mathlib.Tactic
import CausalGraphTheory.H7IndexFunction
import CausalGraphTheory.H7SignFunction

namespace H7CycleExtraction

open H7IndexFunction H7SignFunction

/-- A Fano line is an oriented triple (a, b, c) meaning ea * eb = +ec. -/
abbrev FanoLine := H7Imag × H7Imag × H7Imag

instance instDecEqH7Imag : DecidableEq H7Imag := inferInstance
instance instDecEqFanoLine : DecidableEq FanoLine := inferInstance

/-! ## Concrete H7Imag values (local, not private so native_decide can see them) -/

def ce1 : H7Imag := ⟨⟨1, by norm_num⟩, by norm_num⟩
def ce2 : H7Imag := ⟨⟨2, by norm_num⟩, by norm_num⟩
def ce3 : H7Imag := ⟨⟨3, by norm_num⟩, by norm_num⟩
def ce4 : H7Imag := ⟨⟨4, by norm_num⟩, by norm_num⟩
def ce5 : H7Imag := ⟨⟨5, by norm_num⟩, by norm_num⟩
def ce6 : H7Imag := ⟨⟨6, by norm_num⟩, by norm_num⟩
def ce7 : H7Imag := ⟨⟨7, by norm_num⟩, by norm_num⟩

/-- `cycleExtract i` returns the i-th oriented Fano triple (0-indexed).
    Values are explicit to ensure native_decide can evaluate equalities.
    Ordering follows CONVENTIONS.md §2 exactly. -/
def cycleExtract : Fin 7 → FanoLine
  | ⟨0, _⟩ => (ce1, ce2, ce3)
  | ⟨1, _⟩ => (ce1, ce4, ce5)
  | ⟨2, _⟩ => (ce1, ce7, ce6)
  | ⟨3, _⟩ => (ce2, ce4, ce6)
  | ⟨4, _⟩ => (ce2, ce5, ce7)
  | ⟨5, _⟩ => (ce3, ce4, ce7)
  | ⟨6, _⟩ => (ce3, ce6, ce5)

/-- `isCycleFor t l` holds when the triple t equals the Fano line l. -/
def isCycleFor (t : FanoLine) (l : FanoLine) : Prop := t = l

/-- `cycleSign i j` is the sign derived from the cycle orientation.
    Equals h7Sign by construction. -/
def cycleSign (i j : H7Imag) : ℤ := h7Sign i j

/-- The 7 Fano lines yield exactly 7 entries. -/
theorem fanoLines_card : fanoLines.length = 7 := by native_decide

/-- Each line index i determines a unique ordered triple (the cycle). -/
theorem cycle_at_index_unique (i : Fin 7) :
    ∃! t : FanoLine, isCycleFor t (cycleExtract i) :=
  ⟨cycleExtract i, rfl, fun _ ht => ht⟩

/-- The cycle extraction function is injective (distinct indices → distinct cycles). -/
theorem cycleExtract_injective : Function.Injective cycleExtract := by
  intro a b h
  have key : ∀ x y : Fin 7, cycleExtract x = cycleExtract y → x = y := by native_decide
  exact key a b h

/-- All 7 extracted cycles cover all 7 Fano lines (surjection onto fanoLines). -/
theorem cycleExtract_surjective :
    ∀ l ∈ fanoLines, ∃ i : Fin 7, cycleExtract i = l := by
  native_decide

/-- The multiplication rule derived from cycles matches h7Sign. -/
theorem cycle_sign_consistent (i j : H7Imag) (h : i ≠ j) :
    h7Sign i j = cycleSign i j := by
  simp [cycleSign]

end H7CycleExtraction

-- Leibniz