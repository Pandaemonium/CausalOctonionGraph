/-
  CausalGraphTheory/GenerationSeparation.lean

  Algebraic separation lemmas for generation-sector states.

  This file keeps state-inequality proofs separate from Spinors.lean so that
  large symbolic state constructions and small "sector distinctness" results
  evolve independently.
-/

import CausalGraphTheory.Spinors

namespace CausalGraph

/-- Generation-1 (Furey electron) state is not generation-2 (muon) state. -/
theorem gen1_ne_gen2 :
    Ne fureyElectronStateDoubled gen2StateQuadruple := by
  intro h
  have h0 : (fureyElectronStateDoubled.c 0).re = (gen2StateQuadruple.c 0).re := by
    exact congrArg (fun z : CO => (z.c 0).re) h
  rw [show (fureyElectronStateDoubled.c 0).re = (0 : Int) by rfl] at h0
  rw [show (gen2StateQuadruple.c 0).re = (-2 : Int) by rfl] at h0
  norm_num at h0

/-- Dual generation-1 state is not generation-2 (muon) state. -/
theorem gen1dual_ne_gen2 :
    Ne fureyDualElectronStateDoubled gen2StateQuadruple := by
  intro h
  have h0 : (fureyDualElectronStateDoubled.c 0).re = (gen2StateQuadruple.c 0).re := by
    exact congrArg (fun z : CO => (z.c 0).re) h
  rw [show (fureyDualElectronStateDoubled.c 0).re = (0 : Int) by rfl] at h0
  rw [show (gen2StateQuadruple.c 0).re = (-2 : Int) by rfl] at h0
  norm_num at h0

/-- Primal and dual generation-1 states are distinct. -/
theorem gen1_ne_gen1dual :
    Ne fureyElectronStateDoubled fureyDualElectronStateDoubled := by
  intro h
  have h7 : (fureyElectronStateDoubled.c 7).re = (fureyDualElectronStateDoubled.c 7).re := by
    exact congrArg (fun z : CO => (z.c 7).re) h
  rw [show (fureyElectronStateDoubled.c 7).re = (-8 : Int) by rfl] at h7
  rw [show (fureyDualElectronStateDoubled.c 7).re = (8 : Int) by rfl] at h7
  norm_num at h7

end CausalGraph

