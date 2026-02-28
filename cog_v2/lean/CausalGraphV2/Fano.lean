import Std

namespace CausalGraphV2

abbrev FanoPoint := Fin 7
abbrev FanoLine := Fin 7

def fanoCycles : FanoLine -> Fin 3 -> FanoPoint
  | 0, 0 => 0
  | 0, 1 => 1
  | 0, 2 => 2
  | 1, 0 => 0
  | 1, 1 => 3
  | 1, 2 => 4
  | 2, 0 => 0
  | 2, 1 => 6
  | 2, 2 => 5
  | 3, 0 => 1
  | 3, 1 => 3
  | 3, 2 => 5
  | 4, 0 => 1
  | 4, 1 => 4
  | 4, 2 => 6
  | 5, 0 => 2
  | 5, 1 => 3
  | 5, 2 => 6
  | 6, 0 => 2
  | 6, 1 => 5
  | 6, 2 => 4

def fanoLinePoints (l : FanoLine) : List FanoPoint :=
  [fanoCycles l 0, fanoCycles l 1, fanoCycles l 2]

def incident (p : FanoPoint) (l : FanoLine) : Bool :=
  p ∈ fanoLinePoints l

theorem each_line_has_three_points (l : FanoLine) :
    (fanoLinePoints l).length = 3 := by
  revert l
  decide

theorem line_points_nodup (l : FanoLine) :
    (fanoLinePoints l).Nodup := by
  revert l
  decide

theorem each_point_on_three_lines (p : FanoPoint) :
    (List.filter (fun l => incident p l) (List.finRange 7)).length = 3 := by
  revert p
  decide

theorem two_points_determine_line (p q : FanoPoint) (h : p ≠ q) :
    ∃ l : FanoLine, incident p l ∧ incident q l ∧
      ∀ l' : FanoLine, incident p l' ∧ incident q l' → l' = l := by
  revert h
  revert q
  revert p
  decide

theorem two_lines_meet_in_one_point (l1 l2 : FanoLine) (h : l1 ≠ l2) :
    ∃ p : FanoPoint, incident p l1 ∧ incident p l2 ∧
      ∀ q : FanoPoint, incident q l1 ∧ incident q l2 → q = p := by
  revert h
  revert l2
  revert l1
  decide

end CausalGraphV2
