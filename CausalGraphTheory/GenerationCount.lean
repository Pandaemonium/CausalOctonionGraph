import CausalGraphTheory.LeptonOrbits

/-!
# GEN-002: Three-Generation Count from Fano Orbit Structure

The Fano plane has 7 lines. The stabilizer of the electron quaternion
subalgebra {e1,e2,e3} partitions those 7 lines into orbits of sizes 1, 3, 3.
The two non-trivial orbits of size 3 each correspond to one generation beyond
the first, giving exactly 3 generations total (1 fixed + 2 non-trivial orbits
= 3 families).

## Main results

* `fano_line_count`                     — 7 Fano lines total
* `orbit_partition_sum`                 — 1 + 3 + 3 = 7
* `generation_count_eq_three`           — exactly 3 generations
* `three_orbits_give_three_generations` — orbit count = 3
* `orbit_sizes_are_one_three_three`     — sizes are [1, 3, 3]
* `singleton_orbit_count`               — 1 fixed orbit
* `nonsingleton_orbit_count`            — 2 non-trivial orbits
* `total_fano_lines_accounted`          — orbits cover all 7 lines

## Proof strategy

`LeptonOrbits` provides `stabOrbits0 : List (Finset (Finset (Fin 7)))`, the
explicit 1-3-3 partition proved by `native_decide`. We define `generationCount`
as `stabOrbits0.length` and derive all results from the already-proved lemmas.
-/

namespace GenerationCount

open LeptonOrbits

/-! ## Core definition -/

/-- The number of generations equals the number of distinct orbits under the
    electron-subalgebra stabilizer of the Fano plane. -/
def generationCount : ℕ := stabOrbits0.length

/-! ## Fano line count -/

/-- The total number of Fano lines is 7. -/
theorem fano_line_count : fanoLines.card = 7 :=
  fanoLines_card

/-! ## Partition arithmetic -/

/-- The 1-3-3 orbit sizes sum to 7 (= total number of Fano lines). -/
theorem orbit_partition_sum : 1 + 3 + 3 = 7 := by native_decide

/-! ## Generation count -/

/-- There are exactly **three** orbits under the stabilizer of the electron
    state, one per generation. -/
theorem generation_count_eq_three : generationCount = 3 :=
  lepton_three_generations

/-- The orbit count of the stabilizer-orbit list equals 3. -/
theorem three_orbits_give_three_generations : stabOrbits0.length = 3 :=
  lepton_three_generations

/-! ## Orbit size analysis -/

/-- The orbit sizes are exactly [1, 3, 3]. -/
theorem orbit_sizes_are_one_three_three : stabOrbits0.map Finset.card = [1, 3, 3] :=
  leptonOrbitSizes

/-- There is exactly **one** singleton orbit (the fixed line under Stab(0)). -/
theorem singleton_orbit_count :
    (stabOrbits0.filter (fun o => o.card = 1)).length = 1 := by native_decide

/-- There are exactly **two** non-trivial orbits of size 3
    (generation 2 and generation 3). -/
theorem nonsingleton_orbit_count :
    (stabOrbits0.filter (fun o => o.card = 3)).length = 2 := by native_decide

/-! ## Completeness -/

/-- The three orbits together cover all 7 Fano lines. -/
theorem total_fano_lines_accounted :
    stabOrbits0.foldr (· ∪ ·) ∅ = fanoLines :=
  stabOrbits0_covers

/-! ## Master theorem -/

/-- **GEN-002**: Exactly 3 lepton generations arise because the stabilizer of
    the electron octonion subalgebra partitions the 7 Fano lines into exactly
    3 orbits (the 1-3-3 partition). -/
theorem three_generations_from_fano_orbit_partition :
    generationCount = 3 ∧
    stabOrbits0.map Finset.card = [1, 3, 3] ∧
    stabOrbits0.foldr (· ∪ ·) ∅ = fanoLines :=
  ⟨generation_count_eq_three, orbit_sizes_are_one_three_three, total_fano_lines_accounted⟩

end GenerationCount
