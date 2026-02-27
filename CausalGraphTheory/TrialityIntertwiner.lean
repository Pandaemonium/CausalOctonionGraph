/-
  CausalGraphTheory/TrialityIntertwiner.lean

  Incremental triality-intertwiner closure.

  This module does not claim full Spin(8) triality closure. It provides:
  1) an order-3 triality action on NodeLabel (V -> S_plus -> S_minus -> V),
  2) a concrete intertwiner map into the locked gen3 sign-gauge class,
  3) provable sign-gauge equivariance on both input legs.
-/

import CausalGraphTheory.GenerationLockContract
import CausalGraphTheory.State

namespace CausalGraph

/-- Triality action on representation labels (vacuum fixed). -/
def trialityLabel : NodeLabel -> NodeLabel
  | .V => .S_plus
  | .S_plus => .S_minus
  | .S_minus => .V
  | .vacuum => .vacuum

theorem trialityLabel_order3 (l : NodeLabel) :
    trialityLabel (trialityLabel (trialityLabel l)) = l := by
  cases l <;> rfl

theorem trialityLabel_vacuum_fixed :
    trialityLabel .vacuum = .vacuum := rfl

private theorem neg_mul_octonion {R : Type} [CommRing R] (x y : Octonion R) :
    (-x) * y = -(x * y) := by
  apply Octonion.ext
  intro i
  fin_cases i
  <;> dsimp only [HMul.hMul, Mul.mul, OfNat.ofNat, One.one, Neg.neg]
  <;> norm_num [Fin.ofNat, Fin.mk.injEq]
  <;> simp only [Octonion.fold_mul]
  <;> ring

private theorem mul_neg_octonion {R : Type} [CommRing R] (x y : Octonion R) :
    x * (-y) = -(x * y) := by
  apply Octonion.ext
  intro i
  fin_cases i
  <;> dsimp only [HMul.hMul, Mul.mul, OfNat.ofNat, One.one, Neg.neg]
  <;> norm_num [Fin.ofNat, Fin.mk.injEq]
  <;> simp only [Octonion.fold_mul]
  <;> ring

/--
  Triality intertwiner candidate (current closure level):
  take a vector-like and right-spinor-like input payload, multiply to an inner
  payload, project to gen3, then normalize to the canonical sign-gauge class.
-/
def trialityIntertwiner (v sR : CO) : Gen3SignClass :=
  normalizeGen3Sign (mkGen3 (v * sR))

theorem trialityIntertwiner_output_in_gen3_sector (v sR : CO) :
    InGen3Sector (mkGen3 (v * sR)) :=
  mkGen3_in_sector (v * sR)

theorem trialityIntertwiner_eq_iff {v1 sR1 v2 sR2 : CO} :
    trialityIntertwiner v1 sR1 = trialityIntertwiner v2 sR2 ↔
      Gen3SignEq (mkGen3 (v1 * sR1)) (mkGen3 (v2 * sR2)) := by
  simpa [trialityIntertwiner] using
    (normalizeGen3Sign_unique (psi := mkGen3 (v1 * sR1)) (phi := mkGen3 (v2 * sR2)))

theorem trialityIntertwiner_right_sign_invariant (v sR : CO) :
    trialityIntertwiner v (-sR) = trialityIntertwiner v sR := by
  unfold trialityIntertwiner
  have hMul : v * (-sR) = -(v * sR) := by
    simpa using (mul_neg_octonion v sR)
  calc
    normalizeGen3Sign (mkGen3 (v * (-sR)))
        = normalizeGen3Sign (mkGen3 (-(v * sR))) := by simp [hMul]
    _ = normalizeGen3Sign (signAct .neg (mkGen3 (v * sR))) := by
          simp [signAct, mkGen3_neg_inner]
    _ = normalizeGen3Sign (mkGen3 (v * sR)) := by
          simpa using
            (normalizeGen3Sign_sign_invariant (psi := mkGen3 (v * sR)) (s := .neg))

theorem trialityIntertwiner_left_sign_invariant (v sR : CO) :
    trialityIntertwiner (-v) sR = trialityIntertwiner v sR := by
  unfold trialityIntertwiner
  have hMul : (-v) * sR = -(v * sR) := by
    simpa using (neg_mul_octonion v sR)
  calc
    normalizeGen3Sign (mkGen3 ((-v) * sR))
        = normalizeGen3Sign (mkGen3 (-(v * sR))) := by simp [hMul]
    _ = normalizeGen3Sign (signAct .neg (mkGen3 (v * sR))) := by
          simp [signAct, mkGen3_neg_inner]
    _ = normalizeGen3Sign (mkGen3 (v * sR)) := by
          simpa using
            (normalizeGen3Sign_sign_invariant (psi := mkGen3 (v * sR)) (s := .neg))

theorem trialityIntertwiner_both_sign_invariant (v sR : CO) :
    trialityIntertwiner (-v) (-sR) = trialityIntertwiner v sR := by
  calc
    trialityIntertwiner (-v) (-sR) = trialityIntertwiner (-v) sR := by
      exact trialityIntertwiner_right_sign_invariant (-v) sR
    _ = trialityIntertwiner v sR := by
      exact trialityIntertwiner_left_sign_invariant v sR

end CausalGraph

