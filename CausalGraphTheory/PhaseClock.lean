/-
  CausalGraphTheory/PhaseClock.lean
  RFC-023: Discrete phase clocks and relative-phase interactions

  Exposes a derived local phase observable `phi4 : NodeStateV2 -> ZMod 4`
  from KernelV2 tick counts.
-/

import CausalGraphTheory.KernelV2
import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic

namespace KernelV2

/-! ## Local phase observable -/

/-- Local phase class in Z4, derived from tickCount. -/
def phi4 (s : NodeStateV2) : ZMod 4 := s.tickCount

/-! ## Tick transition used for phase-clock observables -/

/-- Minimal temporal-step map for phase-clock tracking:
    increments `tickCount` by one and leaves other fields unchanged. -/
def nextState (s : NodeStateV2) : NodeStateV2 :=
  { s with tickCount := s.tickCount + 1 }

@[simp] theorem nextState_tickCount (s : NodeStateV2) :
    (nextState s).tickCount = s.tickCount + 1 := rfl

/-! ## Tick-level periodicity lemmas -/

/-- One `nextState` step advances phase by +1 in Z4. -/
theorem phi4_advances (s : NodeStateV2) :
    phi4 (nextState s) = phi4 s + 1 := by
  simp [phi4, nextState_tickCount, Nat.cast_add]

/-- Tick count after n iterations of `nextState`. -/
theorem tickCount_at_tick (s : NodeStateV2) (n : Nat) :
    (nextState^[n] s).tickCount = s.tickCount + n := by
  induction n generalizing s with
  | zero =>
      simp
  | succ n ih =>
      simp [Function.iterate_succ, ih, nextState_tickCount, Nat.add_comm, Nat.add_left_comm]

/-- Phase after n iterations of `nextState`. -/
theorem phi4_at_tick (s : NodeStateV2) (n : Nat) :
    phi4 (nextState^[n] s) = phi4 s + n := by
  simp [phi4, tickCount_at_tick, Nat.cast_add]

/-- Four commits return to the same phase class in Z4. -/
theorem phi4_period4 (s : NodeStateV2) :
    phi4 (nextState (nextState (nextState (nextState s)))) = phi4 s := by
  have h1 : phi4 (nextState (nextState (nextState (nextState s)))) = phi4 s + 4 := by
    simpa [Function.iterate_succ] using (phi4_at_tick s 4)
  have h4 : (4 : ZMod 4) = 0 := by decide
  calc
    phi4 (nextState (nextState (nextState (nextState s))))
        = phi4 s + 4 := h1
    _ = phi4 s + 0 := by simp [h4]
    _ = phi4 s := by simp

/-! ## Phase-energy separation -/

/-- Phase uncertainty does not alter tick dynamics: one step always adds one tick. -/
theorem phase_uncertainty_not_energy (s : NodeStateV2) :
    (nextState s).tickCount = s.tickCount + 1 :=
  nextState_tickCount s

/-- Relative phase is preserved under synchronized one-step updates. -/
theorem delta_phi4_preserved (s t : NodeStateV2) :
    phi4 (nextState s) - phi4 (nextState t) = phi4 s - phi4 t := by
  calc
    phi4 (nextState s) - phi4 (nextState t)
        = (phi4 s + 1) - (phi4 t + 1) := by simp [phi4_advances]
    _ = phi4 s - phi4 t := by abel

end KernelV2
