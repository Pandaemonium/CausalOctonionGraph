/-
  CausalGraphTheory/WittBasis.lean
  Phase 1.4: Witt basis ladder operators and vacuum state

  Defines the lowering operators αⱼ, raising operators αⱼ†, and the
  algebraic vacuum ω = ½(1 + i·e₇) in the complex octonions C ⊗ O.

  Convention source of truth: rfc/CONVENTIONS.md §5–6
-/

import CausalGraphTheory.ComplexOctonion

namespace WittBasis

variable {R : Type u} [CommRing R]

-- ============================================================
-- §5.2: Color plane pairings (0-indexed Fin 7)
-- Witt pair j maps to (eₐ, e_b) where αⱼ = ½(eₐ + i·e_b)
--
-- The pairings are derived from the three Fano lines through e₇:
--   L3: (1,7,6) → e₆·e₇ = -e₁, e₁·e₇ = +e₆ → pair (e₆, e₁)
--   L5: (2,5,7) → e₂·e₇ = -e₅, e₅·e₇ = +e₂ → pair (e₂, e₅)
--   L6: (3,4,7) → e₃·e₇ = -e₄, e₄·e₇ = +e₃ → pair (e₃, e₄)
--
-- Annihilation condition: αⱼ·ω = 0 requires eₐ·e₇ = -e_b and e_b·e₇ = +eₐ.
-- Physics (1-indexed): (e₆,e₁), (e₂,e₅), (e₃,e₄)
-- Lean (0-indexed):    (5, 0),   (1, 4),   (2, 3)
-- ============================================================

/-- The three Witt pairings, 0-indexed into Fin 7.
    wittPair j = (a, b) means αⱼ = ½(e_{a+1} + i·e_{b+1}).
    Derived from the Fano lines through e₇ so that αⱼ·ω = 0. -/
def wittPair : Fin 3 → FanoPoint × FanoPoint
  | 0 => (5, 0)  -- (e₆, e₁) from L3: (1,7,6)
  | 1 => (1, 4)  -- (e₂, e₅) from L5: (2,5,7)
  | 2 => (2, 3)  -- (e₃, e₄) from L6: (3,4,7)

/-- The symmetry-breaking axis (0-indexed): e₇ has Fin 7 index 6. -/
def vacuumAxis : FanoPoint := 6

-- ============================================================
-- §5.3–5.4: Ladder operators over ℤ (no ½ factor)
--
-- Over ℤ we cannot write ½. Instead we define the "doubled" operators:
--   αⱼ_doubled = e_{aⱼ} + i·e_{bⱼ}     (= 2·αⱼ)
--   αⱼ†_doubled = e_{aⱼ} - i·e_{bⱼ}    (= 2·αⱼ†)
--
-- This preserves all algebraic relations up to powers of 2.
-- The Clifford relations become {2αⱼ, 2αₖ†} = 4·δⱼₖ.
-- ============================================================

/-- Doubled lowering operator: 2·αⱼ = e_{aⱼ} + i·e_{bⱼ} as a complex octonion over R. -/
def wittLowerDoubled (j : Fin 3) : ComplexOctonion R :=
  let (a, b) := wittPair j
  let ea : ComplexOctonion R := Octonion.basis ⟨a.val + 1, by omega⟩
  let eb : ComplexOctonion R := Octonion.basis ⟨b.val + 1, by omega⟩
  -- e_a as complex octonion (real part) + i * e_b (imaginary part)
  -- e_a has FormalComplex coefficient (1, 0) at position a+1
  -- i*e_b has FormalComplex coefficient (0, 1) at position b+1
  ⟨fun k =>
    if k == ⟨a.val + 1, by omega⟩ then ⟨1, 0⟩
    else if k == ⟨b.val + 1, by omega⟩ then ⟨0, 1⟩
    else ⟨0, 0⟩⟩

/-- Doubled raising operator: 2·αⱼ† = -(e_{aⱼ} - i·e_{bⱼ}) = -e_{aⱼ} + i·e_{bⱼ}.
    This definition ensures {αⱼ, αⱼ†} = 1.
    Note: CONVENTIONS.md previously listed +(e_{aⱼ} - i·e_{bⱼ}) which leads to {α, α†} = -1. -/
def wittRaiseDoubled (j : Fin 3) : ComplexOctonion R :=
  let (a, b) := wittPair j
  ⟨fun k =>
    if k == ⟨a.val + 1, by omega⟩ then ⟨-1, 0⟩       -- -e_a coefficient
    else if k == ⟨b.val + 1, by omega⟩ then ⟨0, 1⟩   -- +i*e_b coefficient
    else ⟨0, 0⟩⟩

-- ============================================================
-- §6: The algebraic vacuum state
-- ω = ½(1 + i·e₇), doubled: 2ω = 1 + i·e₇
-- ============================================================

/-- Doubled vacuum: 2·ω = 1 + i·e₇ = e₀ + i·e₇.
    e₀ has FormalComplex coefficient (1,0) at position 0.
    i·e₇ has FormalComplex coefficient (0,1) at position 7. -/
def vacuumDoubled : ComplexOctonion R :=
  ⟨fun k =>
    if k == 0 then ⟨1, 0⟩            -- e₀ coefficient
    else if k == 7 then ⟨0, 1⟩       -- i·e₇ coefficient
    else ⟨0, 0⟩⟩

-- ============================================================
-- Key properties (stubs for now)
-- ============================================================

/-- The vacuum is (scaled) idempotent: (2ω)² = 2·(2ω).
    This is equivalent to ω² = ω after dividing by 4.
    Proof: (1 + ie₇)² = 1 + 2ie₇ + i²e₇² = 1 + 2ie₇ - (-1) = 2 + 2ie₇ = 2(1 + ie₇).
    Here "2·x" means "x + x" since we work over a general CommRing without OfNat 2. -/
theorem vacuum_idempotent_doubled :
    (vacuumDoubled : ComplexOctonion R) * vacuumDoubled =
    ⟨fun k => ⟨(vacuumDoubled.c k).re + (vacuumDoubled.c k).re,
              (vacuumDoubled.c k).im + (vacuumDoubled.c k).im⟩⟩ := by
  apply Octonion.ext; intro i; fin_cases i
  <;> apply FormalComplex.ext
  <;> simp only [HMul.hMul, Mul.mul, OfNat.ofNat, vacuumDoubled,
                  FormalComplex.add_re, FormalComplex.add_im,
                  FormalComplex.sub_re, FormalComplex.sub_im]
  <;> norm_num [Fin.ofNat, Fin.mk.injEq]
  <;> simp only [Octonion.fold_mul]
  <;> ring

set_option maxHeartbeats 800000 in
/-- Each doubled lowering operator annihilates the doubled vacuum:
    (2·αⱼ) * (2·ω) = 0 for j = 0, 1, 2.
    This is equivalent to αⱼ·ω = 0 after dividing by 4. -/
theorem wittLower_annihilates_vacuum (j : Fin 3) :
    (wittLowerDoubled (R := R) j) * vacuumDoubled = 0 := by
  fin_cases j
  <;> (apply Octonion.ext; intro i; fin_cases i
       <;> apply FormalComplex.ext
       <;> simp only [HMul.hMul, Mul.mul, OfNat.ofNat, Zero.zero,
                       vacuumDoubled, wittLowerDoubled, wittPair,
                       FormalComplex.add_re, FormalComplex.add_im,
                       FormalComplex.sub_re, FormalComplex.sub_im]
       <;> norm_num [Fin.ofNat, Fin.mk.injEq]
       <;> simp only [Octonion.fold_mul]
       <;> ring)

end WittBasis
