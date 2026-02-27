/-
  CausalGraphTheory/Fano.lean
  Phase 1.1: Fano plane incidence structure

  Defines the 7 points and 7 lines of PG(2,2) using the Furey convention
  (rfc/CONVENTIONS.md §2). All downstream octonion multiplication is
  derived from these directed triples.

  Convention source of truth: rfc/CONVENTIONS.md §2
  Claim: claims/fano_plane.yml (FANO-001)
-/

/-- A point in the Fano plane is an element of Fin 7. -/
abbrev FanoPoint := Fin 7

/-- A line in the Fano plane is an element of Fin 7. -/
abbrev FanoLine := Fin 7

/--
  The 7 directed cyclic triples (SOURCE OF TRUTH).
  Each triple (a, b, c) means e_{a+1} * e_{b+1} = +e_{c+1}.
  Line 0: (0,1,2)  Line 1: (0,3,4)  Line 2: (0,6,5)
  Line 3: (1,3,5)  Line 4: (1,4,6)  Line 5: (2,3,6)  Line 6: (2,5,4)
-/
def fanoCycles : FanoLine → Fin 3 → FanoPoint
  | 0, 0 => 0  | 0, 1 => 1  | 0, 2 => 2
  | 1, 0 => 0  | 1, 1 => 3  | 1, 2 => 4
  | 2, 0 => 0  | 2, 1 => 6  | 2, 2 => 5
  | 3, 0 => 1  | 3, 1 => 3  | 3, 2 => 5
  | 4, 0 => 1  | 4, 1 => 4  | 4, 2 => 6
  | 5, 0 => 2  | 5, 1 => 3  | 5, 2 => 6
  | 6, 0 => 2  | 6, 1 => 5  | 6, 2 => 4

/-- The set of points on a given Fano line. -/
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
