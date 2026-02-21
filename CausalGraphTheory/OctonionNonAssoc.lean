/-
  CausalGraphTheory/OctonionNonAssoc.lean
  Phase 1.2c: Non-associativity witness

  Proves that the octonions are genuinely non-associative by exhibiting
  a specific triple (e₁, e₂, e₄) where the associator is nonzero.
  Also counts the non-associative triples.

  Claim: claims/octonion_nonassoc.yml
-/

import CausalGraphTheory.Octonion

namespace Octonion

/--
  Non-associativity witness: (e₁ * e₂) * e₄ ≠ e₁ * (e₂ * e₄).
-/
theorem non_associative_witness :
    let e1 := Octonion.basis (R := Int) 1
    let e2 := Octonion.basis (R := Int) 2
    let e4 := Octonion.basis (R := Int) 4
    (e1 * e2) * e4 ≠ e1 * (e2 * e4) := by
  native_decide

/--
  A triple of distinct imaginary basis indices is associative iff all three
  lie on the same Fano line.
-/
def isAssociativeTriple (i j k : FanoPoint) : Bool :=
  -- Check if there exists a line containing all three
  (List.finRange 7).any fun l =>
    incident i l && incident j l && incident k l

/-- Build all ordered triples (i,j,k) with i < j < k from Fin 7. -/
private def allOrderedTriples : List (FanoPoint × FanoPoint × FanoPoint) :=
  (List.finRange 7).flatMap fun i =>
    (List.finRange 7).flatMap fun j =>
      (List.finRange 7).filterMap fun k =>
        if i < j && j < k then some (i, j, k) else none

/-- Exactly 7 out of 35 unordered triples of distinct imaginary units are associative
    (those lying on a Fano line). The remaining 28 are non-associative. -/
theorem associative_triple_count :
    let allTriples := allOrderedTriples
    let assocCount := allTriples.filter (fun ⟨i, j, k⟩ => isAssociativeTriple i j k) |>.length
    assocCount = 7 := by
  decide

/-- The complementary count: 28 non-associative triples. -/
theorem non_associative_triple_count :
    let allTriples := allOrderedTriples
    let nonAssocCount := allTriples.filter (fun ⟨i, j, k⟩ => !isAssociativeTriple i j k) |>.length
    nonAssocCount = 28 := by
  decide

end Octonion
