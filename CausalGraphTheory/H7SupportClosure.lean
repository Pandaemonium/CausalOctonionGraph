/-
  CausalGraphTheory/H7SupportClosure.lean

  Primitive 5 of the H7 Kernel: support-closure stability predicate.

  For any subset S of the 7 imaginary units, the support closure cl(S) is:
  - always a subset of H7Imag (the full 7-element set)
  - idempotent: if S is already XOR-index-closed, cl(S) = S
  - never introduces the vacuum element (index 0)
  - each canonical Fano line is already XOR-index-closed

  h7Index : H7Imag → H7Imag → ℕ  (returns the XOR as a natural number)
  H7Imag = {n : Fin 8 // 0 < n.val}  (values 1..7)

  Allowed: Algebra, GroupTheory, LinearAlgebra, Combinatorics, Data.Fintype
  Forbidden: Mathlib.Analysis.*, Mathlib.Topology.*, Mathlib.Data.Real.*
-/

import Mathlib.Data.Fin.Basic
import Mathlib.Data.Fintype.Basic
import Mathlib.Data.Finset.Basic
import Mathlib.Tactic
import CausalGraphTheory.H7IndexFunction
import CausalGraphTheory.H7SignFunction
import CausalGraphTheory.H7CycleExtraction
-- No Mathlib.Analysis, Topology, or Data.Real imports

namespace H7SupportClosure

open H7IndexFunction H7SignFunction

/-! ## Closure predicate: XOR-closure of a Finset H7Imag

    Since h7Index returns ℕ, and the product of two H7Imag elements
    under XOR stays in {1..7} for distinct elements (Fano property),
    we define closure by checking membership of the index result
    lifted back to H7Imag.  For the stability theorems we use the
    fact that h7Index i j (for i ≠ j in H7Imag) lands in {1..7}.
-/

/-- The unique H7Imag element with val.val = n, if it exists. -/
def liftIndex (n : ℕ) : Option H7Imag :=
  if h : 0 < n ∧ n < 8 then
    some ⟨⟨n, h.2⟩, h.1⟩
  else
    none

/-- S is XOR-closed if for all distinct i j ∈ S, liftIndex (h7Index i j) ∈ S. -/
def isXorClosed (S : Finset H7Imag) : Prop :=
  ∀ i j : H7Imag, i ∈ S → j ∈ S → i ≠ j →
    ∃ k ∈ S, k.val.val = h7Index i j

/-- The XOR closure of S: S plus all index-products of pairs in S that land in H7Imag. -/
def xorClosure (S : Finset H7Imag) : Finset H7Imag :=
  Finset.univ.filter (fun k =>
    k ∈ S ∨
    ∃ i ∈ S, ∃ j ∈ S, i ≠ j ∧ k.val.val = h7Index i j)

/-! ## Theorem 1: support_closure_subset -/

/-- For any subset S : Finset H7Imag, the closure cl(S) is a subset of Finset.univ.
    This is trivial since xorClosure is defined as a filter on Finset.univ. -/
theorem support_closure_subset (S : Finset H7Imag) :
    xorClosure S ⊆ Finset.univ := by
  intro x _
  exact Finset.mem_univ x

/-! ## Theorem 2: support_closure_stable -/

/-- If S is already XOR-closed, then xorClosure S = S (fixed-point / idempotency). -/
theorem support_closure_stable (S : Finset H7Imag) (hS : isXorClosed S) :
    xorClosure S = S := by
  ext x
  simp only [xorClosure, Finset.mem_filter, Finset.mem_univ, true_and]
  constructor
  · intro hx
    rcases hx with hxS | ⟨i, hiS, j, hjS, hij, hval⟩
    · exact hxS
    · obtain ⟨k, hkS, hkval⟩ := hS i j hiS hjS hij
      have : x = k := by
        apply Subtype.ext
        apply Subtype.ext
        simp only [hval, hkval]
      rw [this]
      exact hkS
  · intro hx
    left
    exact hx

/-! ## Theorem 3: vacuum_not_in_support -/

/-- The XOR of any two distinct H7Imag elements is nonzero.
    Since H7Imag has values in {1..7} and XOR of distinct such values
    never equals 0, the vacuum (index 0) never appears. -/
theorem vacuum_not_in_support (S : Finset H7Imag) :
    ∀ x ∈ xorClosure S, x.val.val ≠ 0 := by
  intro x _
  exact Nat.not_eq_zero_of_lt x.property

/-! ## Theorem 4: fano_line_is_closed -/

/-- Each canonical Fano line triple (a, b, c) from fanoLines is XOR-closed:
    h7Index a b = c.val.val, h7Index a c = b.val.val, h7Index b c = a.val.val.
    Proved by native_decide over the finite 7-element set. -/
theorem fano_line_is_closed :
    ∀ triple ∈ fanoLines,
      let (a, bc) := triple
      let (b, c) := bc
      h7Index a b = c.val.val ∧
      h7Index a c = b.val.val ∧
      h7Index b c = a.val.val := by
  native_decide

end H7SupportClosure

-- Leibniz