/-
  CausalGraphTheory/Octonion.lean
  Phase 1.2: Octonion algebra over a commutative ring

  Defines the octonion algebra as an 8-component structure with
  multiplication driven by the Fano sign table from FanoMul.lean.

  No Mathlib imports. No ℝ. Works over any CommRing (typically ℤ or ℚ).

  Convention source of truth: rfc/CONVENTIONS.md §1–2
  Claim: claims/octonion_alternativity.yml
-/

import CausalGraphTheory.FanoMul
import CausalGraphTheory.Algebra

/--
  An octonion over a commutative ring R.
  Components: c[0] is the real part (coefficient of e₀),
  c[1]..c[7] are imaginary parts (coefficients of e₁..e₇).

  Note: c[i] for i ∈ {1..7} corresponds to the 0-indexed FanoPoint (i-1).
-/
structure Octonion (R : Type u) [CommRing R] where
  c : Fin 8 → R

namespace Octonion

variable {R : Type u} [CommRing R]

/-- Extensionality: two octonions are equal iff all components are equal. -/
theorem ext {x y : Octonion R} (h : ∀ i, x.c i = y.c i) : x = y := by
  cases x; cases y; simp; funext i; exact h i

/-- The zero octonion. -/
instance : Zero (Octonion R) where
  zero := ⟨fun _ => 0⟩

/-- The real unit (e₀ = 1). -/
instance : One (Octonion R) := ⟨{ c := fun i => if i = 0 then 1 else 0 }⟩

/-- Additive structure. -/
instance : Add (Octonion R) where
  add x y := ⟨fun i => x.c i + y.c i⟩

instance : Neg (Octonion R) where
  neg x := ⟨fun i => -x.c i⟩

instance : Sub (Octonion R) where
  sub x y := ⟨fun i => x.c i - y.c i⟩

/-- Scalar multiplication from the base ring. -/
def smul (r : R) (x : Octonion R) : Octonion R :=
  ⟨fun i => r * x.c i⟩

instance : HSMul R (Octonion R) (Octonion R) where
  hSMul := smul

/-- Construct a basis octonion: the element with 1 in position i and 0 elsewhere. -/
def basis (i : Fin 8) : Octonion R :=
  ⟨fun j => if j = i then 1 else 0⟩

/-- Extract the real part (coefficient of e₀). -/
def re (x : Octonion R) : R := x.c 0

/-- Extract an imaginary coefficient (coefficient of e_{i+1}, 0-indexed). -/
def im (x : Octonion R) (i : Fin 7) : R := x.c ⟨i.val + 1, by omega⟩

/--
  Octonion multiplication, fully expanded from the Fano plane structure constants.

  Each component of x * y is a direct formula in the 8 components of x and y.
  The signs come from the directed cyclic triples in Fano.lean:
  - e₀ is the real unit: e₀ * eⱼ = eⱼ, eᵢ * e₀ = eᵢ
  - eᵢ² = -e₀ for i > 0
  - Cross products eᵢ * eⱼ (i ≠ j, both > 0) determined by Fano plane
-/
instance : Mul (Octonion R) where
  mul x y := ⟨fun
    -- Real part: e₀² = +1, eᵢ² = -1 for i > 0
    | ⟨0, _⟩ => x.c 0 * y.c 0 - x.c 1 * y.c 1 - x.c 2 * y.c 2 - x.c 3 * y.c 3
                - x.c 4 * y.c 4 - x.c 5 * y.c 5 - x.c 6 * y.c 6 - x.c 7 * y.c 7
    -- e₁: Lines L1(1,2,3), L2(1,4,5), L3(1,7,6)
    | ⟨1, _⟩ => x.c 0 * y.c 1 + x.c 1 * y.c 0 + x.c 2 * y.c 3 - x.c 3 * y.c 2
                + x.c 4 * y.c 5 - x.c 5 * y.c 4 - x.c 6 * y.c 7 + x.c 7 * y.c 6
    -- e₂: Lines L1(1,2,3), L4(2,4,6), L5(2,5,7)
    | ⟨2, _⟩ => x.c 0 * y.c 2 + x.c 2 * y.c 0 - x.c 1 * y.c 3 + x.c 3 * y.c 1
                + x.c 4 * y.c 6 - x.c 6 * y.c 4 + x.c 5 * y.c 7 - x.c 7 * y.c 5
    -- e₃: Lines L1(1,2,3), L6(3,4,7), L7(3,6,5)
    | ⟨3, _⟩ => x.c 0 * y.c 3 + x.c 3 * y.c 0 + x.c 1 * y.c 2 - x.c 2 * y.c 1
                + x.c 4 * y.c 7 - x.c 7 * y.c 4 + x.c 6 * y.c 5 - x.c 5 * y.c 6
    -- e₄: Lines L2(1,4,5), L4(2,4,6), L6(3,4,7)
    | ⟨4, _⟩ => x.c 0 * y.c 4 + x.c 4 * y.c 0 - x.c 1 * y.c 5 + x.c 5 * y.c 1
                - x.c 2 * y.c 6 + x.c 6 * y.c 2 - x.c 3 * y.c 7 + x.c 7 * y.c 3
    -- e₅: Lines L2(1,4,5), L5(2,5,7), L7(3,6,5)
    | ⟨5, _⟩ => x.c 0 * y.c 5 + x.c 5 * y.c 0 + x.c 1 * y.c 4 - x.c 4 * y.c 1
                - x.c 2 * y.c 7 + x.c 7 * y.c 2 + x.c 3 * y.c 6 - x.c 6 * y.c 3
    -- e₆: Lines L3(1,7,6), L4(2,4,6), L7(3,6,5)
    | ⟨6, _⟩ => x.c 0 * y.c 6 + x.c 6 * y.c 0 + x.c 1 * y.c 7 - x.c 7 * y.c 1
                + x.c 2 * y.c 4 - x.c 4 * y.c 2 - x.c 3 * y.c 5 + x.c 5 * y.c 3
    -- e₇: Lines L3(1,7,6), L5(2,5,7), L6(3,4,7)
    | ⟨7, _⟩ => x.c 0 * y.c 7 + x.c 7 * y.c 0 - x.c 1 * y.c 6 + x.c 6 * y.c 1
                + x.c 2 * y.c 5 - x.c 5 * y.c 2 + x.c 3 * y.c 4 - x.c 4 * y.c 3
    | ⟨n + 8, h⟩ => absurd h (by omega)⟩

/-- Octonion conjugation: conj(a₀ + Σ aᵢeᵢ) = a₀ - Σ aᵢeᵢ -/
def conj (x : Octonion R) : Octonion R :=
  ⟨fun i => if i = 0 then x.c i else -x.c i⟩

/-- The norm squared: N(x) = re(x * conj(x)). For octonions this equals Σ (cᵢ)². -/
def normSq (x : Octonion R) : R :=
  (x * x.conj).re

-- ============================================================
-- Basic identities
-- ============================================================

-- Fold bare typeclass operations back into notation for ring tactic
lemma fold_mul (a b : R) : @Mul.mul R _ a b = a * b := rfl
lemma fold_add (a b : R) : @Add.add R _ a b = a + b := rfl
lemma fold_sub (a b : R) : @Sub.sub R _ a b = a - b := rfl

/-- The real unit is a multiplicative identity on the left: 1 * x = x. -/
theorem one_mul (x : Octonion R) : (1 : Octonion R) * x = x := by
  apply ext
  intro i
  fin_cases i
  <;> dsimp only [HMul.hMul, Mul.mul, OfNat.ofNat, One.one]
  <;> norm_num [Fin.ofNat, Fin.mk.injEq]
  <;> simp only [fold_mul]
  <;> ring

/-- Conjugation is an involution: conj(conj(x)) = x. -/
theorem conj_involution (x : Octonion R) : x.conj.conj = x := by
  apply ext
  intro i
  simp [conj]
  split
  · rfl
  · exact neg_neg _

/-- DecidableEq for octonions when the base ring has DecidableEq. -/
instance instDecidableEq [DecidableEq R] : DecidableEq (Octonion R) := fun a b =>
  if h : ∀ i, a.c i = b.c i then .isTrue (ext h)
  else .isFalse (fun heq => h (fun i => by subst heq; rfl))

end Octonion
