import CausalGraphTheory.ThetaQCD
import Mathlib.Tactic

/--
  CausalGraphTheory/ThetaEFTBridge.lean

  Conditional continuum-bridge primitives for THETA-001.
  These theorems are intentionally scoped as bridge-form statements:
  if a declared map from discrete CP residual to continuum theta coefficient
  has the given form, then theta vanishes because the discrete residual is zero.
-/

namespace CausalGraph

/-- Discrete CP-odd residual used by THETA-001 bridge statements. -/
def discreteCpResidual : Int := fanoSignOrderedSum

/-- The discrete residual is exactly zero from THETA-001 sign-balance witness. -/
theorem discreteCpResidual_zero : discreteCpResidual = 0 := by
  simpa [discreteCpResidual] using fanoSignOrderedSum_zero

/--
  Direct bridge form: if continuum theta is identified with the discrete residual,
  then theta is zero.
-/
theorem theta_zero_if_direct_bridge (theta : Int) (hmap : theta = discreteCpResidual) : theta = 0 := by
  calc
    theta = discreteCpResidual := hmap
    _ = 0 := discreteCpResidual_zero

/--
  Linear bridge form: if continuum theta is a linear scaling of the discrete residual,
  then theta is zero.
-/
theorem theta_zero_if_linear_bridge (theta scale : Int) (hmap : theta = scale * discreteCpResidual) :
    theta = 0 := by
  calc
    theta = scale * discreteCpResidual := hmap
    _ = scale * 0 := by rw [discreteCpResidual_zero]
    _ = 0 := by simp

/--
  Affine bridge form: if theta is affine in the discrete residual and offset is zero,
  then theta is zero.
-/
theorem theta_zero_if_affine_bridge
    (theta scale offset : Int)
    (hmap : theta = scale * discreteCpResidual + offset)
    (hoffset : offset = 0) :
    theta = 0 := by
  calc
    theta = scale * discreteCpResidual + offset := hmap
    _ = scale * 0 + 0 := by rw [discreteCpResidual_zero, hoffset]
    _ = 0 := by simp

end CausalGraph
