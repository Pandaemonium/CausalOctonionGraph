/-
  CausalGraphTheory/H7Handedness.lean
  H7 Primitive 3: Handedness Law

  Proves anticommutativity of octonion multiplication signs for distinct
  imaginary units, derived from the Fano plane directed triples.

  Convention: rfc/CONVENTIONS.md §2 (Furey convention, 0-indexed Fin 7).
  Directed triples (0-indexed, matching fanoCycles in Fano.lean):
    L0: (0,1,2)  L1: (0,3,4)  L2: (0,6,5)
    L3: (1,3,5)  L4: (1,4,6)  L5: (2,3,6)  L6: (2,5,4)

  Primitive 3 of H7 closure: sign(ei * ej) = -sign(ej * ei) for i != j.
-/

/- TODO(owner, post-THETA lane):
   1. Refactor this file to reuse canonical definitions from `FanoMul.lean` / `XorGate.lean`
      instead of duplicated sign/index tables.
   2. Keep this module as a thin primitive-closure wrapper and import it from `CausalGraphTheory.lean`
      only after de-duplication is complete.
   3. Strengthen `handedness_fano_consistent` so the proof uses line-incidence assumptions
      in a non-vacuous way (not just global antisymmetry).
-/

import CausalGraphTheory.Fano

/-- The sign of e_i * e_j in octonion multiplication.
    Returns 1 (cyclic), -1 (anti-cyclic), or 0 (diagonal).
    Convention: rfc/CONVENTIONS.md §2 (0-indexed Fin 7). -/
def octonionSign (i j : FanoPoint) : Int :=
  match i.val, j.val with
  | 0, 1 => 1  | 1, 0 => -1
  | 1, 2 => 1  | 2, 1 => -1
  | 2, 0 => 1  | 0, 2 => -1
  | 0, 3 => 1  | 3, 0 => -1
  | 3, 4 => 1  | 4, 3 => -1
  | 4, 0 => 1  | 0, 4 => -1
  | 0, 6 => 1  | 6, 0 => -1
  | 6, 5 => 1  | 5, 6 => -1
  | 5, 0 => 1  | 0, 5 => -1
  | 1, 3 => 1  | 3, 1 => -1
  | 3, 5 => 1  | 5, 3 => -1
  | 5, 1 => 1  | 1, 5 => -1
  | 1, 4 => 1  | 4, 1 => -1
  | 4, 6 => 1  | 6, 4 => -1
  | 6, 1 => 1  | 1, 6 => -1
  | 2, 3 => 1  | 3, 2 => -1
  | 3, 6 => 1  | 6, 3 => -1
  | 6, 2 => 1  | 2, 6 => -1
  | 2, 5 => 1  | 5, 2 => -1
  | 5, 4 => 1  | 4, 5 => -1
  | 4, 2 => 1  | 2, 4 => -1
  | _, _ => 0

/-- The third Fano point on the line through distinct i and j.
    Returns i for the degenerate (diagonal) case. -/
def octonionIndex (i j : FanoPoint) : FanoPoint :=
  match i.val, j.val with
  | 0, 1 => ⟨2, by omega⟩  | 1, 0 => ⟨2, by omega⟩
  | 1, 2 => ⟨0, by omega⟩  | 2, 1 => ⟨0, by omega⟩
  | 2, 0 => ⟨1, by omega⟩  | 0, 2 => ⟨1, by omega⟩
  | 0, 3 => ⟨4, by omega⟩  | 3, 0 => ⟨4, by omega⟩
  | 3, 4 => ⟨0, by omega⟩  | 4, 3 => ⟨0, by omega⟩
  | 4, 0 => ⟨3, by omega⟩  | 0, 4 => ⟨3, by omega⟩
  | 0, 6 => ⟨5, by omega⟩  | 6, 0 => ⟨5, by omega⟩
  | 6, 5 => ⟨0, by omega⟩  | 5, 6 => ⟨0, by omega⟩
  | 5, 0 => ⟨6, by omega⟩  | 0, 5 => ⟨6, by omega⟩
  | 1, 3 => ⟨5, by omega⟩  | 3, 1 => ⟨5, by omega⟩
  | 3, 5 => ⟨1, by omega⟩  | 5, 3 => ⟨1, by omega⟩
  | 5, 1 => ⟨3, by omega⟩  | 1, 5 => ⟨3, by omega⟩
  | 1, 4 => ⟨6, by omega⟩  | 4, 1 => ⟨6, by omega⟩
  | 4, 6 => ⟨1, by omega⟩  | 6, 4 => ⟨1, by omega⟩
  | 6, 1 => ⟨4, by omega⟩  | 1, 6 => ⟨4, by omega⟩
  | 2, 3 => ⟨6, by omega⟩  | 3, 2 => ⟨6, by omega⟩
  | 3, 6 => ⟨2, by omega⟩  | 6, 3 => ⟨2, by omega⟩
  | 6, 2 => ⟨3, by omega⟩  | 2, 6 => ⟨3, by omega⟩
  | 2, 5 => ⟨4, by omega⟩  | 5, 2 => ⟨4, by omega⟩
  | 5, 4 => ⟨2, by omega⟩  | 4, 5 => ⟨2, by omega⟩
  | 4, 2 => ⟨5, by omega⟩  | 2, 4 => ⟨5, by omega⟩
  | _, _ => i

/-- Theorem 1: The octonion index function is symmetric. -/
theorem handedness_preserves_index (i j : Fin 7) (h : i ≠ j) :
    octonionIndex i j = octonionIndex j i := by
  revert h; revert j; revert i; native_decide

/-- Theorem 2: Left and right multiplication by distinct imaginary units
    have opposite signs — the anticommutativity / handedness law. -/
theorem handedness_flips_sign (i j : Fin 7) (h : i ≠ j) :
    octonionSign i j = -octonionSign j i := by
  revert h; revert j; revert i; native_decide

/-- Theorem 3: Self-multiplication sign is zero (e_i^2 = -e_0). -/
theorem handedness_self_zero (i : Fin 7) :
    octonionSign i i = 0 := by
  revert i; native_decide

/-- Theorem 4: Handedness law is consistent with Fano incidence.
    Any two distinct points on the same Fano line have opposite signs. -/
theorem handedness_fano_consistent (l : FanoLine) (i j : Fin 7)
    (_hi : incident i l = true) (_hj : incident j l = true) (h : i ≠ j) :
    octonionSign i j = -octonionSign j i :=
  handedness_flips_sign i j h

-- Leibniz
