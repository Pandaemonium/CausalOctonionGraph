/-
  CausalGraphTheory/ComplexOctonion.lean
  Phase 1.3: Complex octonions C ⊗ O

  Defines the complex-octonionic algebra as pairs (re, im) of octonions,
  where `i` is a commuting imaginary unit with i² = -1.

  This avoids importing ℝ or Mathlib's Complex type. Instead we use a
  "formal complex" structure: pairs (a, b) representing a + i*b.

  Convention source of truth: rfc/CONVENTIONS.md §4
-/

import CausalGraphTheory.Octonion

/--
  A formal complex number over a ring R: represents a + i*b where i² = -1.
  The imaginary unit i commutes with everything (it is central).
-/
structure FormalComplex (R : Type u) [CommRing R] where
  re : R
  im : R

namespace FormalComplex

variable {R : Type u} [CommRing R]

/-- Extensionality for FormalComplex. -/
@[ext]
theorem ext {z w : FormalComplex R} (hre : z.re = w.re) (him : z.im = w.im) : z = w := by
  cases z; cases w; simp at *; exact ⟨hre, him⟩

/-- The imaginary unit i. -/
def I : FormalComplex R := ⟨0, 1⟩

/-- Complex conjugation: conj(a + ib) = a - ib. -/
def conj (z : FormalComplex R) : FormalComplex R := ⟨z.re, -z.im⟩

/-- Scalar embedding: r ↦ r + 0i. -/
def ofReal (r : R) : FormalComplex R := ⟨r, 0⟩

-- Helper functions matching the recursive nsmul/zsmul expectations,
-- so that consistency proofs are `rfl`.
private def fcNsmul : ℕ → FormalComplex R → FormalComplex R
  | 0, _ => ⟨0, 0⟩
  | n + 1, z => ⟨(fcNsmul n z).re + z.re, (fcNsmul n z).im + z.im⟩

private def fcZsmul : ℤ → FormalComplex R → FormalComplex R
  | .ofNat n, z => fcNsmul n z
  | .negSucc n, z => ⟨-(fcNsmul (n + 1) z).re, -(fcNsmul (n + 1) z).im⟩

/-- FormalComplex R forms a commutative ring. -/
instance : CommRing (FormalComplex R) where
  zero := ⟨0, 0⟩
  one := ⟨1, 0⟩
  add z w := ⟨z.re + w.re, z.im + w.im⟩
  neg z := ⟨-z.re, -z.im⟩
  sub z w := ⟨z.re - w.re, z.im - w.im⟩
  mul z w := ⟨z.re * w.re - z.im * w.im, z.re * w.im + z.im * w.re⟩
  nsmul := fcNsmul
  zsmul := fcZsmul
  nsmul_zero _ := rfl
  nsmul_succ _ _ := rfl
  zsmul_zero' _ := rfl
  zsmul_succ' _ _ := rfl
  zsmul_neg' _ _ := rfl
  -- Additive axioms (term-mode via R-level lemmas)
  add_comm := fun ⟨a, b⟩ ⟨c, d⟩ => ext (add_comm a c) (add_comm b d)
  add_assoc := fun ⟨a, b⟩ ⟨c, d⟩ ⟨e, f⟩ => ext (add_assoc a c e) (add_assoc b d f)
  zero_add := fun ⟨a, b⟩ => ext (zero_add a) (zero_add b)
  add_zero := fun ⟨a, b⟩ => ext (add_zero a) (add_zero b)
  neg_add_cancel := fun ⟨a, b⟩ => ext (neg_add_cancel a) (neg_add_cancel b)
  sub_eq_add_neg := fun ⟨a, b⟩ ⟨c, d⟩ => ext (sub_eq_add_neg a c) (sub_eq_add_neg b d)
  -- Multiplicative axioms (change reduces to R-level, then ring closes)
  mul_comm := fun ⟨a, b⟩ ⟨c, d⟩ => ext
    (by change a * c - b * d = c * a - d * b; ring)
    (by change a * d + b * c = c * b + d * a; ring)
  mul_assoc := fun ⟨a, b⟩ ⟨c, d⟩ ⟨e, f⟩ => ext
    (by change (a * c - b * d) * e - (a * d + b * c) * f =
              a * (c * e - d * f) - b * (c * f + d * e); ring)
    (by change (a * c - b * d) * f + (a * d + b * c) * e =
              a * (c * f + d * e) + b * (c * e - d * f); ring)
  one_mul := fun ⟨a, b⟩ => ext
    (by change 1 * a - 0 * b = a; ring)
    (by change 1 * b + 0 * a = b; ring)
  mul_one := fun ⟨a, b⟩ => ext
    (by change a * 1 - b * 0 = a; ring)
    (by change a * 0 + b * 1 = b; ring)
  left_distrib := fun ⟨a, b⟩ ⟨c, d⟩ ⟨e, f⟩ => ext
    (by change a * (c + e) - b * (d + f) = (a * c - b * d) + (a * e - b * f); ring)
    (by change a * (d + f) + b * (c + e) = (a * d + b * c) + (a * f + b * e); ring)
  right_distrib := fun ⟨a, b⟩ ⟨c, d⟩ ⟨e, f⟩ => ext
    (by change (a + c) * e - (b + d) * f = (a * e - b * f) + (c * e - d * f); ring)
    (by change (a + c) * f + (b + d) * e = (a * f + b * e) + (c * f + d * e); ring)
  zero_mul := fun ⟨a, b⟩ => ext
    (by change 0 * a - 0 * b = 0; ring)
    (by change 0 * b + 0 * a = 0; ring)
  mul_zero := fun ⟨a, b⟩ => ext
    (by change a * 0 - b * 0 = 0; ring)
    (by change a * 0 + b * 0 = 0; ring)

-- Simp lemmas for unfolding FormalComplex operations to R-level
@[simp] lemma zero_re : (0 : FormalComplex R).re = 0 := rfl
@[simp] lemma zero_im : (0 : FormalComplex R).im = 0 := rfl
@[simp] lemma one_re : (1 : FormalComplex R).re = 1 := rfl
@[simp] lemma one_im : (1 : FormalComplex R).im = 0 := rfl
@[simp] lemma add_re (z w : FormalComplex R) : (z + w).re = z.re + w.re := rfl
@[simp] lemma add_im (z w : FormalComplex R) : (z + w).im = z.im + w.im := rfl
@[simp] lemma neg_re (z : FormalComplex R) : (-z).re = -z.re := rfl
@[simp] lemma neg_im (z : FormalComplex R) : (-z).im = -z.im := rfl
@[simp] lemma sub_re (z w : FormalComplex R) : (z - w).re = z.re - w.re := rfl
@[simp] lemma sub_im (z w : FormalComplex R) : (z - w).im = z.im - w.im := rfl
@[simp] lemma mul_re (z w : FormalComplex R) : (z * w).re = z.re * w.re - z.im * w.im := rfl
@[simp] lemma mul_im (z w : FormalComplex R) : (z * w).im = z.re * w.im + z.im * w.re := rfl

/-- FormalComplex R has decidable equality whenever R does.
    Required so that `native_decide` can evaluate CO component equalities. -/
instance instDecidableEq [DecidableEq R] : DecidableEq (FormalComplex R) :=
  fun a b =>
    if hre : a.re = b.re then
      if him : a.im = b.im then isTrue (FormalComplex.ext hre him)
      else isFalse (fun h => him (congrArg FormalComplex.im h))
    else isFalse (fun h => hre (congrArg FormalComplex.re h))

end FormalComplex

/--
  A complex octonion: an element of C ⊗ O.
  Represented as an octonion with FormalComplex coefficients,
  i.e., each of the 8 components is a formal complex number.

  Equivalently: z = Σⱼ (aⱼ + i bⱼ) eⱼ where aⱼ, bⱼ ∈ R.
-/
abbrev ComplexOctonion (R : Type u) [CommRing R] := Octonion (FormalComplex R)

namespace ComplexOctonion

variable {R : Type u} [CommRing R]

/-- Embed a real octonion into the complex octonions. -/
def ofOctonion (x : Octonion R) : ComplexOctonion R :=
  ⟨fun i => FormalComplex.ofReal (x.c i)⟩

/-- Multiply a complex octonion by the central imaginary unit i.
    This is NOT the same as multiplying by an octonionic basis element.
    The complex i commutes with all octonionic units. -/
def mulI (z : ComplexOctonion R) : ComplexOctonion R :=
  ⟨fun j => FormalComplex.I * z.c j⟩

end ComplexOctonion
