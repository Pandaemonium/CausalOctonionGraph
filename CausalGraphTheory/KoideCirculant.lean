import Mathlib.Data.Int.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Omega
import Mathlib.Tactic.NormNum

namespace KoideCirculant

/-!
# Koide Circulant Gate 3: B/A = √2 Algebraic Condition

For a 3×3 circulant matrix Circ(b, a, a) with integer parameters,
where `b` is the diagonal entry and `a` is the off-diagonal entry,
the eigenvalues are:
  λ₀ = b + 2a  (eigenvector (1,1,1))
  λ₁ = b - a   (repeated, eigenvectors orthogonal to (1,1,1))
  λ₂ = b - a

The Koide sum-rule:
  (λ₀+λ₁+λ₂)² = (3/2)(λ₀²+λ₁²+λ₂²)

holds over ℚ if and only if b² = 2a², i.e. b/a = √2.

Note: The integer/ℤ version avoids the 3/2 fraction by multiplying through by 2:
  2*(λ₀+λ₁+λ₂)² = 3*(λ₀²+λ₁²+λ₂²)
-/

/-- Diagonal eigenvalue of the circulant Circ(b, a, a) -/
def lambda0 (a b : ℤ) : ℤ := b + 2 * a

/-- Degenerate eigenvalue (first copy) of the circulant Circ(b, a, a) -/
def lambda1 (a b : ℤ) : ℤ := b - a

/-- Degenerate eigenvalue (second copy) of the circulant Circ(b, a, a) -/
def lambda2 (a b : ℤ) : ℤ := b - a

/-- Sum of the three circulant eigenvalues -/
def sumLambda (a b : ℤ) : ℤ := lambda0 a b + lambda1 a b + lambda2 a b

/-- Sum of squares of the three circulant eigenvalues -/
def sumSqLambda (a b : ℤ) : ℤ := lambda0 a b ^ 2 + lambda1 a b ^ 2 + lambda2 a b ^ 2

/-- The Koide condition over ℤ: 2*(sum)² = 3*(sumSq).
    This is the integer form of (sum)² = (3/2)*(sumSq), obtained by multiplying by 2. -/
def koideCondition (a b : ℤ) : Prop :=
  2 * (sumLambda a b) ^ 2 = 3 * (sumSqLambda a b)

/-- The sum of eigenvalues simplifies to 3b (independent of a). -/
theorem sumLambda_eq (a b : ℤ) : sumLambda a b = 3 * b := by
  unfold sumLambda lambda0 lambda1 lambda2
  ring

/-- The Koide condition holds if and only if b² = 2a².
    This is the algebraic statement that b/a = √2 (over ℤ, avoiding irrationals). -/
theorem koide_circulant_iff (a b : ℤ) :
    koideCondition a b ↔ b ^ 2 = 2 * a ^ 2 := by
  unfold koideCondition sumLambda sumSqLambda lambda0 lambda1 lambda2
  constructor
  · intro h
    nlinarith [sq_nonneg a, sq_nonneg b, sq_nonneg (b + 2 * a), sq_nonneg (b - a)]
  · intro h
    nlinarith [sq_nonneg a, sq_nonneg b, sq_nonneg (b + 2 * a), sq_nonneg (b - a)]

/-- The B/A ratio squared equals 2 when the Koide condition holds. -/
theorem ba_ratio_sq (a b : ℤ) (h : koideCondition a b) : b ^ 2 = 2 * a ^ 2 :=
  (koide_circulant_iff a b).mp h

/-- There is no integer r satisfying r² = 2. This formalizes that √2 is irrational,
    so the exact Koide condition b² = 2a² has no nonzero integer solution. -/
theorem no_integer_sqrt2 : ¬ (∃ (r : ℤ), r ^ 2 = 2) := by
  intro ⟨r, hr⟩
  have h0 : r = 0 ∨ r = 1 ∨ r = -1 ∨ r ≥ 2 ∨ r ≤ -2 := by omega
  rcases h0 with h | h | h | h | h
  · simp [h] at hr
  · simp [h] at hr
  · norm_num [h] at hr
  · nlinarith [sq_nonneg r]
  · nlinarith [sq_nonneg r]

/-- Consequence: the Koide circulant condition has no solution with a ≠ 0 and b/a ∈ ℤ.
    In other words, there is no integer b with b² = 2a² unless a = 0. -/
theorem no_integer_ba_sqrt2 (a b : ℤ) (ha : a ≠ 0) (hkoide : koideCondition a b) :
    ¬ (∃ (r : ℤ), r * a = b) := by
  intro ⟨r, hr⟩
  have hb2 : b ^ 2 = 2 * a ^ 2 := ba_ratio_sq a b hkoide
  have : r ^ 2 * a ^ 2 = 2 * a ^ 2 := by nlinarith [sq_nonneg r, sq_nonneg a, sq_nonneg b]
  have ha2 : a ^ 2 > 0 := by positivity
  have : r ^ 2 = 2 := by
    have := mul_right_cancel₀ (ne_of_gt ha2) (show r ^ 2 * a ^ 2 = 2 * a ^ 2 from this)
    exact this
  exact no_integer_sqrt2 ⟨r, this⟩

end KoideCirculant