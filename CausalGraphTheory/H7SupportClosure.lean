/-
  CausalGraphTheory/H7SupportClosure.lean

  Primitive 5 of the H7 Kernel: the support-closure stability predicate.

  A motif (Finset H7Imag) is support-closed if for every pair of distinct
  elements i, j in the motif, the element whose XOR-index equals h7Index i j
  is also in the motif. This encodes Fano-plane closure.

  All four theorems are fully proved (no admitted gaps).

  Allowed: Algebra, GroupTheory, LinearAlgebra, Combinatorics, Data.Fintype
  Forbidden: Mathlib.Analysis.*, Mathlib.Topology.*, Mathlib.Data.Real.*
-/

import Mathlib.Data.Fin.Basic
import Mathlib.Data.Fintype.Basic
import Mathlib.Data.Finset.Basic
import Mathlib.Tactic
import CausalGraphTheory.H7IndexFunction
import CausalGraphTheory.H7SignFunction

namespace H7SupportClosure

open H7IndexFunction H7SignFunction

def supportClosed (S : Finset H7Imag) : Prop :=
  ∀ i j : H7Imag, i ∈ S → j ∈ S → i ≠ j →
    ∀ k : H7Imag, k.val.val = h7Index i j → k ∈ S

theorem supportClosed_empty : supportClosed (∅ : Finset H7Imag) := by
  intro i j hi _hj _hne _k _hk
  simp at hi

theorem supportClosed_full : supportClosed (Finset.univ : Finset H7Imag) := by
  intro _i _j _hi _hj _hne _k _hk
  exact Finset.mem_univ _

private abbrev e1' : H7Imag := ⟨⟨1, by decide⟩, by decide⟩
private abbrev e2' : H7Imag := ⟨⟨2, by decide⟩, by decide⟩
private abbrev e3' : H7Imag := ⟨⟨3, by decide⟩, by decide⟩
private abbrev e4' : H7Imag := ⟨⟨4, by decide⟩, by decide⟩
private abbrev e5' : H7Imag := ⟨⟨5, by decide⟩, by decide⟩
private abbrev e6' : H7Imag := ⟨⟨6, by decide⟩, by decide⟩
private abbrev e7' : H7Imag := ⟨⟨7, by decide⟩, by decide⟩

def fanoLineFinsets : Fin 7 → Finset H7Imag
  | ⟨0, _⟩ => {e1', e2', e3'}
  | ⟨1, _⟩ => {e1', e4', e5'}
  | ⟨2, _⟩ => {e1', e7', e6'}
  | ⟨3, _⟩ => {e2', e4', e6'}
  | ⟨4, _⟩ => {e2', e5', e7'}
  | ⟨5, _⟩ => {e3', e4', e7'}
  | ⟨6, _⟩ => {e3', e6', e5'}

theorem fanoLine_supportClosed (l : Fin 7) : supportClosed (fanoLineFinsets l) := by
  have key : ∀ (l : Fin 7) (i j k : H7Imag),
      i ∈ fanoLineFinsets l → j ∈ fanoLineFinsets l → i ≠ j →
      k.val.val = h7Index i j → k ∈ fanoLineFinsets l := by
    native_decide
  intro i j hi hj hne k hk
  exact key l i j k hi hj hne hk

theorem supportClosed_inter (A B : Finset H7Imag)
    (hA : supportClosed A) (hB : supportClosed B) : supportClosed (A ∩ B) := by
  intro i j hi hj hne k hk
  rw [Finset.mem_inter] at hi hj ⊢
  obtain ⟨hiA, hiB⟩ := hi
  obtain ⟨hjA, hjB⟩ := hj
  exact ⟨hA i j hiA hjA hne k hk, hB i j hiB hjB hne k hk⟩

end H7SupportClosure

-- Leibniz