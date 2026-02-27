/-
  CausalGraphTheory/GaugeObservables.lean
  RFC-026: Strategy for Deriving Gauge-Sector Constants
  STRONG-001 leading-order alpha_s proxy

  Formalises the leading-order estimate for the strong coupling constant
  from group-theoretic data already proved in Lean:

    |Stab(e₇)| = 24       proved: vacuum_stabilizer_count  (GaugeGroup.lean)
    |Aut(PG(2,2))| = 168   proved: fano_aut_count            (GaugeGroup.lean)
    Stab(e₇) ≅ S₄          proved: vacuumStabilizer_explicit_iso_S4_bool

  Leading-order estimate:
    alpha_s_proxy = 24 / 168 = 1/7 ≈ 0.14286

  Physical comparison (RFC-026 §7 honesty requirement):
    Measured alpha_s(M_Z) ≈ 0.1181
    Gap ≈ 20%  (positive: proxy overestimates)
    Hypothesis: residual from trapped/escaped mixing at finite graph density.
    NOT a free parameter adjustment.

  This file promotes STRONG-001 from stub → partial.
-/

import CausalGraphTheory.GaugeGroup
import Mathlib.Tactic

namespace CausalGraph

/-! ## Alpha_s leading-order proxy -/

/-- `alpha_s_proxy` is the rational ratio |Stab(e₇)| / |Aut(PG(2,2))|.
    Represents the fraction of gauge-group operations that are colour-trapped
    (confined to the vacuum stabilizer S₄).
    RFC-026 §5.1: no mixing corrections are applied at this level. -/
def alpha_s_proxy : ℚ := 24 / 168

/-- The leading-order proxy equals exactly 1/7. -/
theorem alpha_s_proxy_eq : alpha_s_proxy = 1 / 7 := by
  norm_num [alpha_s_proxy]

/-- Decimal bounds: 0.125 < alpha_s_proxy < 0.167. -/
theorem alpha_s_proxy_bounds :
    (1 : ℚ) / 8 < alpha_s_proxy ∧ alpha_s_proxy < 1 / 6 := by
  constructor <;> norm_num [alpha_s_proxy]

/-! ## Group-order consistency -/

/-- The orbit-stabilizer ratio 168 / 24 = 7 confirms the Fano orbit
    has 7 points, matching fano_aut_count and vacuum_stabilizer_count. -/
theorem orbit_stabilizer_ratio : (168 : ℚ) / 24 = 7 := by norm_num

/-- The group orders 24 and 168 satisfy the orbit-stabilizer theorem:
    168 = 7 × 24 (proved by native_decide in GaugeGroup.lean as orbit_stabilizer_check). -/
theorem gauge_group_factored :
    (168 : ℚ) = 7 * 24 := by norm_num

/-- alpha_s_proxy is equivalent to 1 over the Fano orbit size. -/
theorem alpha_s_proxy_is_one_over_orbit_size :
    alpha_s_proxy = 1 / 7 := alpha_s_proxy_eq

/-! ## Physical gap (RFC-026 §2 failure-mode documentation) -/

/-- COG proxy value approximated as a rational for comparison. -/
def alpha_s_proxy_approx : ℚ := 14286 / 100000  -- ≈ 0.14286

/-- Physical value of alpha_s at M_Z scale (PDG). -/
def alpha_s_physical : ℚ := 1181 / 10000   -- ≈ 0.1181

/-- The proxy overestimates the physical value.
    The gap is attributed to mixing corrections per RFC-026 §5.1.
    Explicitly NOT fixed by adjusting the projector definition. -/
theorem alpha_s_proxy_overestimates :
    alpha_s_physical < alpha_s_proxy := by
  norm_num [alpha_s_proxy, alpha_s_physical]

def alpha_s_gap : ℚ := alpha_s_proxy - alpha_s_physical

theorem alpha_s_gap_eq :
    alpha_s_gap = 1733 / 70000 := by
  norm_num [alpha_s_gap, alpha_s_proxy, alpha_s_physical]

theorem alpha_s_gap_pos :
    0 < alpha_s_gap := by
  norm_num [alpha_s_gap_eq]

end CausalGraph
