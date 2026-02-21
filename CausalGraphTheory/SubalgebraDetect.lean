/-
  CausalGraphTheory/SubalgebraDetect.lean
  Phase 1.5: Quaternionic subalgebra detection

  Determines whether a set of imaginary basis elements generates an
  associative (quaternionic) subalgebra, i.e., whether all elements
  lie on a single Fano line.

  This is the foundation for the "batchable" predicate in the HACG
  causal graph: operations within an associative subalgebra can be
  evaluated in any order (batched), while operations spanning
  non-associative triples force sequential evaluation (ticks).

  Convention source of truth: rfc/CONVENTIONS.md §3
-/

import CausalGraphTheory.OctonionNonAssoc

namespace SubalgebraDetect

/--
  Check if a pair of distinct Fano points share a common line.
  This is always true for any two distinct points in PG(2,2)
  (every pair lies on exactly one line).
-/
def shareLine (p q : FanoPoint) : Bool :=
  (List.finRange 7).any fun l => incident p l && incident q l

/--
  Check if a set of Fano points (given as a list) all lie on a single line.
  If true, they generate an associative (quaternionic) subalgebra.
-/
def allOnOneLine (pts : List FanoPoint) : Bool :=
  (List.finRange 7).any fun l => pts.all fun p => incident p l

/--
  The batchable predicate: a list of imaginary basis indices generates
  an associative subalgebra iff they all lie on a single Fano line.

  When batchable = true, the corresponding octonionic operations can
  be evaluated in any order (the subalgebra is quaternionic, hence
  associative). When false, evaluation order matters and forces a
  sequential "tick" in the causal graph.
-/
def batchable (indices : List FanoPoint) : Bool :=
  allOnOneLine indices

-- ============================================================
-- Properties
-- ============================================================

/-- Any single element is trivially batchable. -/
theorem batchable_singleton (p : FanoPoint) :
    batchable [p] = true := by
  revert p; decide

/-- Any pair of distinct elements is batchable (they share a line). -/
theorem batchable_pair (p q : FanoPoint) (h : p ≠ q) :
    batchable [p, q] = true := by
  revert h; revert q; revert p; decide

/-- Each of the 7 Fano lines is batchable. -/
theorem batchable_fano_line (l : FanoLine) :
    batchable (fanoLinePoints l) = true := by
  revert l; decide

/-- A non-collinear triple is not batchable: e₁, e₂, e₄ (0-indexed: 0, 1, 3). -/
theorem not_batchable_example :
    batchable [0, 1, 3] = false := by decide

/-- Build all ordered triples (i,j,k) with i < j < k from Fin 7. -/
private def allOrderedTriples : List (FanoPoint × FanoPoint × FanoPoint) :=
  (List.finRange 7).flatMap fun i =>
    (List.finRange 7).flatMap fun j =>
      (List.finRange 7).filterMap fun k =>
        if i < j && j < k then some (i, j, k) else none

/-- The number of batchable unordered triples is exactly 7. -/
theorem batchable_triple_count :
    let allTriples := allOrderedTriples
    let batchCount := allTriples.filter (fun ⟨i, j, k⟩ => batchable [i, j, k]) |>.length
    batchCount = 7 := by
  decide

end SubalgebraDetect
