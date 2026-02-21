/-
  CausalGraphTheory/FanoMul.lean
  Phase 1.1b: Fano-derived sign table and basis multiplication

  The sign tensor ε(i,j) and the basis multiplication table are generated
  programmatically from the directed cyclic triples in Fano.lean.
  Nothing is hardcoded independently of fanoCycles.

  Convention source of truth: rfc/CONVENTIONS.md §2
-/

import CausalGraphTheory.Fano

/--
  Find which Fano line (if any) contains both points p and q.
  Returns `some l` if p and q are both on line l, `none` if no such line.
-/
def findLine (p q : FanoPoint) : Option FanoLine :=
  (List.finRange 7).find? (fun l => incident p l && incident q l)

/--
  Given two distinct imaginary basis indices (0-indexed, ∈ Fin 7),
  compute the sign (+1 or -1) and the third index k such that
  e_{i+1} * e_{j+1} = sign * e_{k+1} in physics notation.

  Returns (k, sign) where k is 0-indexed.
  If i = j, returns (i, 0) as a sentinel (e_i * e_i = -e_0, handled separately).
-/
def fanoBasisMul (i j : FanoPoint) : FanoPoint × Int :=
  if i == j then (i, 0)  -- sentinel: e_i² = -1, caller handles this
  else
    -- Search all 7 lines for the one containing both i and j
    let result := (List.finRange 7).findSome? fun l =>
      let a := fanoCycles l 0
      let b := fanoCycles l 1
      let c := fanoCycles l 2
      -- Check if {i, j} ⊆ {a, b, c} and determine sign from cyclic order
      if i == a && j == b then some (c, (1 : Int))
      else if i == b && j == c then some (a, (1 : Int))
      else if i == c && j == a then some (b, (1 : Int))
      else if i == b && j == a then some (c, (-1 : Int))
      else if i == c && j == b then some (a, (-1 : Int))
      else if i == a && j == c then some (b, (-1 : Int))
      else none
    result.getD (i, 0)  -- fallback should never be reached for valid distinct inputs

/--
  The sign tensor: fanoSign i j = +1 or -1 for the product e_{i+1} * e_{j+1}.
  Returns 0 when i = j (since e_i² = -e_0 is not a basis element product).
-/
def fanoSign (i j : FanoPoint) : Int :=
  (fanoBasisMul i j).2

/--
  The third-index function: fanoThird i j = k where e_{i+1} * e_{j+1} = ±e_{k+1}.
  Only meaningful when i ≠ j.
-/
def fanoThird (i j : FanoPoint) : FanoPoint :=
  (fanoBasisMul i j).1

-- ============================================================
-- Smoke tests: verify specific products match CONVENTIONS.md
-- ============================================================

/-- e₁ * e₂ = +e₃ (Line L1) -/
example : fanoBasisMul 0 1 = (2, 1) := by decide

/-- e₂ * e₁ = -e₃ (anti-cyclic) -/
example : fanoBasisMul 1 0 = (2, -1) := by decide

/-- e₁ * e₄ = +e₅ (Line L2, 0-indexed: e₁=0, e₄=3, e₅=4) -/
example : fanoBasisMul 0 3 = (4, 1) := by decide

/-- e₃ * e₆ = +e₅ (Line L7, 0-indexed: e₃=2, e₆=5, e₅=4) -/
example : fanoBasisMul 2 5 = (4, 1) := by decide

/-- e₂ * e₅ = +e₇ (Line L5, 0-indexed: e₂=1, e₅=4, e₇=6) -/
example : fanoBasisMul 1 4 = (6, 1) := by decide

/-- Anti-symmetry: fanoSign i j = -fanoSign j i for all i ≠ j. -/
theorem fano_sign_antisymmetric (i j : FanoPoint) (h : i ≠ j) :
    fanoSign i j = -fanoSign j i := by
  revert h; revert j; revert i; decide

/-- Every pair of distinct points produces a nonzero sign. -/
theorem fano_sign_nonzero (i j : FanoPoint) (h : i ≠ j) :
    fanoSign i j ≠ 0 := by
  revert h; revert j; revert i; decide
