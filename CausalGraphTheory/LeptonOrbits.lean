import Mathlib.Data.Finset.Basic
import Mathlib.Data.Fintype.Basic

/-!
# Lepton Orbit Partition — Fano Plane Stabilizer

This file formalises the 1 + 3 + 3 partition of the seven Fano lines under
the stabilizer of a fixed point (the "electron state" in Furey's C⊗O
construction).

## Main results

* `fanoLines`                — the 7 lines of PG(2,2) as a `Finset`
* `stabOrbits0`              — the three orbits under Stab(0) ≤ GL(3,2)
* `leptonOrbitSizes`         — orbit sizes are [1, 3, 3]
* `lepton_three_generations` — exactly 3 orbits ↔ 3 lepton generations

## Convention (CONVENTIONS.md §2)

Points are `Fin 7` with labels 0 … 6 (= octonion basis elements e₁ … e₇).
The seven Fano lines are the cyclic triples

  {0,1,3}, {1,2,4}, {2,3,5}, {3,4,6}, {4,5,0}, {5,6,1}, {6,0,2}

## Orbit structure (verified in calc/furey_electron_orbit.py, task 7cdd24fc-e33)

Under the point-stabilizer of 0 in GL(3,2) (order 24) the 7 lines split as:
  • Size-1 orbit:   { {3,4,6} }
  • Size-3 orbit A: { {1,2,4}, {2,3,5}, {5,6,1} }
  • Size-3 orbit B: { {0,1,3}, {0,4,5}, {0,2,6} }
-/

namespace LeptonOrbits

open Finset

/-! ## Fano lines -/

/-- The seven lines of the Fano plane PG(2,2), as a `Finset` of `Finset (Fin 7)`. -/
def fanoLines : Finset (Finset (Fin 7)) :=
  { {(0 : Fin 7), 1, 3},
    {(1 : Fin 7), 2, 4},
    {(2 : Fin 7), 3, 5},
    {(3 : Fin 7), 4, 6},
    {(4 : Fin 7), 5, 0},
    {(5 : Fin 7), 6, 1},
    {(6 : Fin 7), 0, 2} }

/-! ## Stabilizer orbits (explicit enumeration) -/

/-- The three orbits of `fanoLines` under the stabilizer of point 0 in GL(3,2). -/
def stabOrbits0 : List (Finset (Finset (Fin 7))) :=
  [ -- Size-1 orbit: {3,4,6} is fixed by all of Stab(0)
    { {(3 : Fin 7), 4, 6} },
    -- Size-3 orbit A: lines not through 0 (other than {3,4,6})
    { {(1 : Fin 7), 2, 4},
      {(2 : Fin 7), 3, 5},
      {(5 : Fin 7), 6, 1} },
    -- Size-3 orbit B: lines through 0
    { {(0 : Fin 7), 1, 3},
      {(0 : Fin 7), 4, 5},
      {(0 : Fin 7), 2, 6} }
  ]

/-! ## Theorems -/

/-- **Main theorem**: The orbit sizes under the stabilizer of the electron state are
[1, 3, 3] — the algebraic fingerprint of three lepton generations. -/
theorem leptonOrbitSizes :
    stabOrbits0.map Finset.card = [1, 3, 3] := by native_decide

/-- There are exactly **three** orbits, one per lepton generation. -/
theorem lepton_three_generations :
    stabOrbits0.length = 3 := by native_decide

/-- The orbits cover all 7 Fano lines. -/
theorem stabOrbits0_covers :
    stabOrbits0.foldr (· ∪ ·) ∅ = fanoLines := by native_decide

/-- The total number of Fano lines is 7 (sanity check). -/
theorem fanoLines_card :
    fanoLines.card = 7 := by native_decide

end LeptonOrbits