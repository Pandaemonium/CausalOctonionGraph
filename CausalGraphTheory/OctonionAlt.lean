/-
  CausalGraphTheory/OctonionAlt.lean
  Phase 1.2b: Alternativity proofs for the octonion algebra

  Proves:
  - Left alternativity:  x * (x * y) = (x * x) * y
  - Right alternativity: (y * x) * x = y * (x * x)
  - Flexibility:         x * (y * x) = (x * y) * x

  These are proved first for basis elements (finite case check),
  then extended to general elements by multilinearity.

  Claim: claims/octonion_alternativity.yml
-/

import CausalGraphTheory.Octonion

namespace Octonion

variable {R : Type u} [CommRing R]

-- ============================================================
-- Alternativity on basis elements (computational verification)
-- ============================================================

/--
  The associator [x, y, z] = (x * y) * z - x * (y * z).
  For an alternative algebra, [x, x, y] = 0 and [y, x, x] = 0.
-/
def associator (x y z : Octonion R) : Octonion R :=
  (x * y) * z - x * (y * z)

-- The full alternativity proofs over a general CommRing require showing
-- that the associator vanishes whenever two arguments are equal.
-- Strategy: prove for basis elements over ℤ via decide,
-- then lift to general R by multilinearity.

-- For now, we state the theorems and provide computational witnesses.

/-- Left alternativity for basis elements over ℤ. -/
theorem left_alt_basis (i j : Fin 8) :
    let ei := Octonion.basis (R := Int) i
    let ej := Octonion.basis (R := Int) j
    ei * (ei * ej) = (ei * ei) * ej := by
  revert i j; native_decide

/-- Right alternativity for basis elements over ℤ. -/
theorem right_alt_basis (i j : Fin 8) :
    let ei := Octonion.basis (R := Int) i
    let ej := Octonion.basis (R := Int) j
    (ej * ei) * ei = ej * (ei * ei) := by
  revert i j; native_decide

/-- Flexibility for basis elements over ℤ. -/
theorem flexible_basis (i j : Fin 8) :
    let ei := Octonion.basis (R := Int) i
    let ej := Octonion.basis (R := Int) j
    ei * (ej * ei) = (ei * ej) * ei := by
  revert i j; native_decide

-- ============================================================
-- General alternativity (stated, proof deferred)
-- ============================================================

/-- Left alternativity: x * (x * y) = (x * x) * y for all octonions. -/
theorem left_alternative (x y : Octonion R) :
    x * (x * y) = (x * x) * y := by
  apply ext; intro i; fin_cases i
  <;> dsimp only [HMul.hMul, Mul.mul]
  <;> simp only [fold_mul]
  <;> ring

/-- Right alternativity: (y * x) * x = y * (x * x) for all octonions. -/
theorem right_alternative (x y : Octonion R) :
    (y * x) * x = y * (x * x) := by
  apply ext; intro i; fin_cases i
  <;> dsimp only [HMul.hMul, Mul.mul]
  <;> simp only [fold_mul]
  <;> ring

/-- Flexibility: x * (y * x) = (x * y) * x for all octonions. -/
theorem flexible (x y : Octonion R) :
    x * (y * x) = (x * y) * x := by
  apply ext; intro i; fin_cases i
  <;> dsimp only [HMul.hMul, Mul.mul]
  <;> simp only [fold_mul]
  <;> ring

end Octonion
