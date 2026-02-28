import CausalGraphV2.ThetaQCD
import Std.Tactic

namespace CausalGraphV2

/-!
Conditional continuum-bridge primitives for THETA-001 in the v2 canonical lane.

These are bridge-form theorems only:
if a declared map from discrete CP residual to continuum theta coefficient has
the specified form, then theta vanishes because the discrete residual is zero.
-/

/-- Discrete CP-odd residual used by THETA-001 bridge statements. -/
def discreteCpResidual : Int :=
  fanoSignOrderedSum

/-- Exact v2 witness: discrete residual is zero. -/
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
Linear bridge form: if continuum theta is linear in the discrete residual,
then theta is zero.
-/
theorem theta_zero_if_linear_bridge (theta scale : Int) (hmap : theta = scale * discreteCpResidual) :
    theta = 0 := by
  calc
    theta = scale * discreteCpResidual := hmap
    _ = scale * 0 := by rw [discreteCpResidual_zero]
    _ = 0 := by simp

/--
Affine bridge form: if theta is affine in the discrete residual with zero offset,
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

/--
General zero-anchored bridge form: if theta is mapped through any bridge function
that is anchored at zero, then theta is zero when the discrete residual is zero.
-/
theorem theta_zero_if_zero_anchored_bridge
    (theta : Int)
    (f : Int -> Int)
    (hmap : theta = f discreteCpResidual)
    (hzero : f 0 = 0) :
    theta = 0 := by
  calc
    theta = f discreteCpResidual := hmap
    _ = f 0 := by rw [discreteCpResidual_zero]
    _ = 0 := hzero

/-!
Continuum-bridge skeleton lane:
these theorems make the remaining hypotheses explicit for full value closure.
-/

/--
Hypothesis-level continuum identification theorem:
if a selected continuum bridge map is odd and zero-anchored at the origin,
then zero discrete residual implies zero continuum theta coefficient.
-/
theorem theta_zero_if_continuum_identification_hyp
    (theta : Int)
    (f : Int -> Int)
    (hmap : theta = f discreteCpResidual)
    (hodd : ∀ r : Int, f (-r) = -f r)
    (hzero : f 0 = 0) :
    theta = 0 := by
  have _ : ∀ r : Int, f (-r) = -f r := hodd
  calc
    theta = f discreteCpResidual := hmap
    _ = f 0 := by rw [discreteCpResidual_zero]
    _ = 0 := hzero

/--
Bridge-and-isolation skeleton:
if strong-sector leakage is explicitly zero in the declared bridge lane,
and continuum theta is identified by a zero-anchored map, theta remains zero.
-/
theorem theta_zero_if_continuum_bridge_and_no_leakage
    (theta strongLeakage : Int)
    (f : Int -> Int)
    (hmap : theta = f discreteCpResidual)
    (hzero : f 0 = 0)
    (hNoLeakage : strongLeakage = 0) :
    theta = 0 := by
  have _ : strongLeakage = 0 := hNoLeakage
  calc
    theta = f discreteCpResidual := hmap
    _ = f 0 := by rw [discreteCpResidual_zero]
    _ = 0 := hzero

end CausalGraphV2
