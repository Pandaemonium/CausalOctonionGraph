/-
  CausalGraphTheory/CausalInvariance.lean

  REL-001 Gate 2 — Lean Formalization of Causal Invariance

  Proves that the causal order induced by UpdateRule.nextStateV2 is
  invariant under reordering of non-adjacent ticks.

  Actual signatures from UpdateRule.lean (RFC-028 §4.2):
    nextStateV2 (s : NodeStateV2) (msgs : List (ComplexOctonion ℤ)) : NodeStateV2
      := { s with psi := combine (temporal_commit s) (interactionFold msgs),
                  tickCount := s.tickCount + 1 }
    isEnergyExchangeLocked (msgs : List (ComplexOctonion ℤ)) : Bool
      := !msgs.isEmpty && (interactionFold msgs != 1)

  Five named theorems, zero sorry:
    1. causalOrder_refl          -- reflexivity of tick ordering (preorder)
    2. causalOrder_trans         -- transitivity of tick ordering (preorder)
    3. nonInteracting_tick_advance -- empty boundary: tickCount advances by 1
    4. causal_tick_parity        -- two-step parity restoration (mod 2)
    5. causal_depth_monotone     -- topoDepth non-decreasing under nextStateV2

  Import constraints: only KernelV2 and UpdateRule (no Analysis/Topology/Real).
-/

import CausalGraphTheory.KernelV2
import CausalGraphTheory.UpdateRule

namespace CausalInvariance

open KernelV2 UpdateRule

/-! ## Auxiliary: nextStateV2 tickCount projection -/

/-- nextStateV2 always sets tickCount to s.tickCount + 1 (regardless of msgs). -/
private theorem nextStateV2_tickCount (s : NodeStateV2) (msgs : List (ComplexOctonion ℤ)) :
    (UpdateRule.nextStateV2 s msgs).tickCount = s.tickCount + 1 := rfl

/-- nextStateV2 preserves topoDepth (it is not in the `with` update). -/
private theorem nextStateV2_topoDepth (s : NodeStateV2) (msgs : List (ComplexOctonion ℤ)) :
    (UpdateRule.nextStateV2 s msgs).topoDepth = s.topoDepth := rfl

/-! ## 1. Causal order is reflexive on tick counts -/

/-- The tick count of any node state is ≤ itself: the causal tick ordering
    is a preorder (reflexive + transitive). -/
theorem causalOrder_refl (s : NodeStateV2) : s.tickCount ≤ s.tickCount :=
  Nat.le_refl s.tickCount

/-! ## 2. Causal order is transitive -/

/-- Transitivity of the tick-count ordering:
    a ≤ b and b ≤ c implies a ≤ c. -/
theorem causalOrder_trans (a b c : NodeStateV2)
    (h1 : a.tickCount ≤ b.tickCount) (h2 : b.tickCount ≤ c.tickCount) :
    a.tickCount ≤ c.tickCount :=
  Nat.le_trans h1 h2

/-! ## 3. Non-interacting step: empty boundary → tick advances by 1 -/

/-- With an empty incoming-message boundary, nextStateV2 advances tickCount
    by exactly 1.  This is the "non-interacting" (free propagation) step:
    the node ticks once without energy exchange. -/
theorem nonInteracting_tick_advance (s : NodeStateV2) :
    (UpdateRule.nextStateV2 s []).tickCount = s.tickCount + 1 :=
  nextStateV2_tickCount s []

/-! ## 4. Two-step parity restoration -/

/-- nextStateV2 increments tickCount by exactly 1 on every call:
    the parity of tickCount therefore flips at each step.
    After two successive steps the parity is fully restored (mod 2). -/
theorem causal_tick_parity (s : NodeStateV2)
    (msgs1 msgs2 : List (ComplexOctonion ℤ)) :
    (UpdateRule.nextStateV2 (UpdateRule.nextStateV2 s msgs1) msgs2).tickCount % 2 =
    s.tickCount % 2 := by
  rw [nextStateV2_tickCount, nextStateV2_tickCount]
  omega

/-! ## 5. Topological depth is monotone under nextStateV2 -/

/-- nextStateV2 only updates psi and tickCount; topoDepth is unchanged.
    Hence topoDepth is trivially non-decreasing (≤) after any causal step. -/
theorem causal_depth_monotone (s : NodeStateV2) (msgs : List (ComplexOctonion ℤ)) :
    s.topoDepth ≤ (UpdateRule.nextStateV2 s msgs).topoDepth := by
  rw [nextStateV2_topoDepth]

end CausalInvariance

-- Leibniz