/-
  CausalGraphTheory/PhaseClock.lean
  RFC-023: Discrete Phase Clocks and Relative-Phase Interactions

  Defines phi4 : NodeStateV2 → ZMod 4, the local phase class derived
  from tickCount.  Each temporal commit advances phi4 by +1 mod 4, matching
  the period-4 e7 action proved in Spinors.lean (universal_Ce_period_four)
  for the full CO type.

  RFC-023 §6 architectural decisions (locked):
    D1: phi4 is DERIVED from tickCount, not stored as primary state.
    D2: phase entropy is epistemic (observer-level), not ontic.
    D3: energy accounting lives in transition semantics (nextState_tickCount).
-/

import CausalGraphTheory.KernelV2

namespace KernelV2

/-! ## Local phase observable -/

/-- `phi4 s` is the local Z4 phase class of node `s`.
    Derived deterministically from `s.tickCount`; never stored separately.
    RFC-023 §6 D1. -/
def phi4 (s : NodeStateV2) : ZMod 4 := s.tickCount

/-! ## Periodicity theorems -/

/-- One temporal commit advances the phase by exactly +1 mod 4. -/
theorem phi4_advances (s : NodeStateV2) :
    phi4 (nextState s) = phi4 s + 1 := by
  simp only [phi4, nextState_tickCount]
  push_cast
  ring

/-- After 4 temporal commits the phase returns to its original value.
    Kernel-level counterpart of `universal_Ce_period_four` in Spinors.lean
    (proved there for the full CO type under e7 left-multiplication). -/
theorem phi4_period4 (s : NodeStateV2) :
    phi4 (nextState (nextState (nextState (nextState s)))) = phi4 s := by
  simp only [phi4_advances]
  have h : ∀ x : ZMod 4, x + 1 + 1 + 1 + 1 = x := by decide
  exact h _

/-- Phase at iterate n equals the initial phase plus n in ZMod 4. -/
theorem phi4_at_tick (s : NodeStateV2) (n : ℕ) :
    phi4 (nextState^[n] s) = phi4 s + n := by
  induction n with
  | zero => simp [phi4]
  | succ n ih =>
    simp only [Function.iterate_succ', Function.comp_apply, phi4_advances, ih]
    push_cast; ring

/-! ## Phase-energy separation (RFC-023 §6 D2–D3, Test C) -/

/-- **phase_uncertainty_not_energy** (RFC-023 Test C):
    The tick increment per temporal commit is exactly 1, independent of
    the current phase value.  Observer uncertainty about phi4 cannot
    alter the underlying tick dynamics or energy accounting. -/
theorem phase_uncertainty_not_energy (s : NodeStateV2) :
    (nextState s).tickCount = s.tickCount + 1 := nextState_tickCount s

/-- Relative phase between two nodes is preserved across a joint tick:
    both advance by +1 in ZMod 4, so their difference is unchanged.
    Formalises H3 (observer-limited relative phase) at the kernel layer. -/
theorem delta_phi4_preserved (s t : NodeStateV2) :
    phi4 (nextState s) - phi4 (nextState t) = phi4 s - phi4 t := by
  simp [phi4_advances]

end KernelV2
