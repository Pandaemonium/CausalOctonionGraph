/-
  CausalGraphTheory/Fano.lean
  Phase 1.1: Fano plane incidence structure

  Defines the 7 points and 7 lines of PG(2,2) using the Furey convention
  (rfc/CONVENTIONS.md §2). All downstream octonion multiplication is
  derived from these directed triples.

  Convention source of truth: rfc/CONVENTIONS.md §2
  Claim: claims/fano_plane.yml (FANO-001)
-/

-- No Mathlib imports needed for Phase 1.1.
-- We use bare Lean 4 with Fin, List, and decidability.

/-- A point in the Fano plane is an element of Fin 7, representing
    the imaginary octonion units e₁ through e₇ (0-indexed: 0 ↦ e₁, ..., 6 ↦ e₇). -/
abbrev FanoPoint := Fin 7

/-- A line in the Fano plane is an element of Fin 7. -/
abbrev FanoLine := Fin 7

/--
  The 7 directed cyclic triples (SOURCE OF TRUTH).

  These encode the Fano plane lines with the Furey convention.
  Each triple (a, b, c) means e_{a+1} * e_{b+1} = +e_{c+1} (using 1-indexed physics notation).

  In our 0-indexed Fin 7:
    Line 0: (0, 1, 2) ↔ physics (1, 2, 3): e₁e₂ = +e₃
    Line 1: (0, 3, 4) ↔ physics (1, 4, 5): e₁e₄ = +e₅
    Line 2: (0, 6, 5) ↔ physics (1, 7, 6): e₁e₇ = +e₆
    Line 3: (1, 3, 5) ↔ physics (2, 4, 6): e₂e₄ = +e₆
    Line 4: (1, 4, 6) ↔ physics (2, 5, 7): e₂e₅ = +e₇
    Line 5: (2, 3, 6) ↔ physics (3, 4, 7): e₃e₄ = +e₇
    Line 6: (2, 5, 4) ↔ physics (3, 6, 5): e₃e₆ = +e₅

  IMPORTANT: The 0-indexed representation maps point p to physics index p+1.
-/
def fanoCycles : FanoLine → Fin 3 → FanoPoint
  | 0, 0 => 0  | 0, 1 => 1  | 0, 2 => 2  -- (1,2,3)
  | 1, 0 => 0  | 1, 1 => 3  | 1, 2 => 4  -- (1,4,5)
  | 2, 0 => 0  | 2, 1 => 6  | 2, 2 => 5  -- (1,7,6)
  | 3, 0 => 1  | 3, 1 => 3  | 3, 2 => 5  -- (2,4,6)
  | 4, 0 => 1  | 4, 1 => 4  | 4, 2 => 6  -- (2,5,7)
  | 5, 0 => 2  | 5, 1 => 3  | 5, 2 => 6  -- (3,4,7)
  | 6, 0 => 2  | 6, 1 => 5  | 6, 2 => 4  -- (3,6,5)

/-- The set of points on a given Fano line, as a list. -/
def fanoLinePoints (l : FanoLine) : List FanoPoint :=
  [fanoCycles l 0, fanoCycles l 1, fanoCycles l 2]

/-- Incidence predicate: point p lies on line l. -/
def incident (p : FanoPoint) (l : FanoLine) : Bool :=
  p ∈ fanoLinePoints l

/-- Each line contains exactly 3 distinct points. -/
theorem each_line_has_three_points (l : FanoLine) :
    (fanoLinePoints l).length = 3 := by
  revert l; decide

/-- The three points on each line are distinct. -/
theorem line_points_nodup (l : FanoLine) :
    (fanoLinePoints l).Nodup := by
  revert l; decide

/-- Each point lies on exactly 3 lines. -/
theorem each_point_on_three_lines (p : FanoPoint) :
    (List.filter (fun l => incident p l) (List.finRange 7)).length = 3 := by
  revert p; decide

/-- Two distinct points determine a unique line. -/
theorem two_points_determine_line (p q : FanoPoint) (h : p ≠ q) :
    ∃ l : FanoLine, incident p l ∧ incident q l ∧
      ∀ l' : FanoLine, incident p l' ∧ incident q l' → l' = l := by
  revert h; revert q; revert p; decide

/-- Two distinct lines meet in exactly one point. -/
theorem two_lines_meet_in_one_point (l₁ l₂ : FanoLine) (h : l₁ ≠ l₂) :
    ∃ p : FanoPoint, incident p l₁ ∧ incident p l₂ ∧
      ∀ q : FanoPoint, incident q l₁ ∧ incident q l₂ → q = p := by
  revert h; revert l₂; revert l₁; decide

/-- Convert a 0-indexed Fano point to its 1-indexed physics label. -/
def toPhysicsIndex (p : FanoPoint) : Fin 8 := ⟨p.val + 1, by omega⟩

/-- Convert a 1-indexed physics label (1..7) to a 0-indexed Fano point. -/
def fromPhysicsIndex (i : Fin 8) (h : 0 < i.val) : FanoPoint :=
  ⟨i.val - 1, by omega⟩
