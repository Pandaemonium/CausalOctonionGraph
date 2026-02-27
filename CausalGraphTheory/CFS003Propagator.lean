/-
  CFS-003 Gate 2 -- Discrete Propagator on Fano Points

  The Fano plane has 7 points (Fin 7). We define a discrete propagator
  K : Fin 7 -> Fin 7 -> Nat given by the Fano incidence structure:
  K(i,j) = 1 if i = j or i,j share a common Fano line, else 0.

  Named theorems (>=3, no sorry):
    propagatorKernel_symmetric      -- K(i,j) = K(j,i)
    propagatorKernel_diag_one       -- K(i,i) = 1  (vacuum normalization)
    propagatorKernel_bound          -- K(i,j) <= 1  (discrete spectrum)
    propagatorKernel_support_le     -- support of each row <= 7
    propagatorKernel_all_ones       -- all entries equal 1 (PG(2,2) completeness)
-/

import Mathlib.Data.Fintype.Basic
import Mathlib.Data.Fin.Basic
import Mathlib.Data.Finset.Card
import Mathlib.Data.Finset.Basic

namespace CausalGraph

/-- The 7 Fano lines as triples of point indices in Fin 7 -/
def fanoLines : List (Fin 7 × Fin 7 × Fin 7) :=
  [(0,1,3),(1,2,4),(2,3,5),(3,4,6),(4,5,0),(5,6,1),(6,0,2)]

/-- Two Fano points share a common line (or are equal) -/
def sharesLine (i j : Fin 7) : Bool :=
  fanoLines.any (fun ⟨a, b, c⟩ => (i == a || i == b || i == c) && (j == a || j == b || j == c))

/-- Discrete propagator kernel: 1 if collinear or equal, 0 otherwise -/
def propagatorKernel (i j : Fin 7) : ℕ :=
  if sharesLine i j then 1 else 0

/-- Theorem 1: The propagator kernel is symmetric K(i,j) = K(j,i) -/
theorem propagatorKernel_symmetric (i j : Fin 7) :
    propagatorKernel i j = propagatorKernel j i := by
  simp only [propagatorKernel, sharesLine, fanoLines]
  native_decide

/-- Theorem 2: Diagonal entries are 1 -- vacuum normalization -/
theorem propagatorKernel_diag_one (i : Fin 7) :
    propagatorKernel i i = 1 := by
  simp only [propagatorKernel, sharesLine, fanoLines]
  native_decide

/-- Theorem 3: All kernel entries are <= 1 -- discrete spectrum -/
theorem propagatorKernel_bound (i j : Fin 7) :
    propagatorKernel i j ≤ 1 := by
  simp only [propagatorKernel]
  split_ifs <;> simp

/-- Theorem 4: Support of each row has card <= 7 -/
theorem propagatorKernel_support_le (i : Fin 7) :
    (Finset.univ.filter (fun j => propagatorKernel i j ≠ 0)).card ≤ 7 := by
  calc (Finset.univ.filter (fun j => propagatorKernel i j ≠ 0)).card
      ≤ Finset.univ.card := Finset.card_le_card (Finset.filter_subset _ _)
    _ = 7 := by simp [Fintype.card_fin]

/-- Theorem 5: In PG(2,2), every two points share a line, so all kernel entries = 1 -/
theorem propagatorKernel_all_ones (i j : Fin 7) :
    propagatorKernel i j = 1 := by
  simp only [propagatorKernel, sharesLine, fanoLines]
  native_decide

end CausalGraph