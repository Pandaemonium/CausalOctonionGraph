/-
  CausalGraphTheory/GenerationLockContract.lean

  Proof-first generation lock contract.

  This file intentionally does not define a canonical gen3 state representative.
  It provides constructor-level sector contracts so gen3 can remain a derived
  target until a uniqueness-class theorem is closed.
-/

import CausalGraphTheory.Spinors

namespace CausalGraph

/-
  rightVacDoubled is the doubled right vacuum projector 2S = e0 + i*e7.
  We reuse omegaDoubled to keep conventions aligned with Spinors.lean.
-/
abbrev rightVacDoubled : CO := omegaDoubled

def mkGen2 (inner : CO) : CO :=
  leftVacConjDoubled * (inner * rightVacConjDoubled)

def mkGen3 (inner : CO) : CO :=
  leftVacConjDoubled * (inner * rightVacDoubled)

def InGen2Sector (psi : CO) : Prop :=
  ∃ inner : CO, psi = mkGen2 inner

def InGen3Sector (psi : CO) : Prop :=
  ∃ inner : CO, psi = mkGen3 inner

theorem mkGen2_in_sector (inner : CO) : InGen2Sector (mkGen2 inner) :=
  ⟨inner, rfl⟩

theorem mkGen3_in_sector (inner : CO) : InGen3Sector (mkGen3 inner) :=
  ⟨inner, rfl⟩

theorem gen2_sector_nonempty : ∃ psi : CO, InGen2Sector psi :=
  ⟨mkGen2 0, mkGen2_in_sector 0⟩

theorem gen3_sector_nonempty : ∃ psi : CO, InGen3Sector psi :=
  ⟨mkGen3 0, mkGen3_in_sector 0⟩

/-
  Current muon witness from Spinors.lean is a concrete inhabitant of gen2 sector.
-/
theorem gen2StateQuadruple_in_gen2_sector : InGen2Sector gen2StateQuadruple := by
  refine ⟨muonInner, ?_⟩
  rfl

/-
  Governance marker theorem: gen3 is treated as derived target in this contract.
  Canonical representative lock requires a future uniqueness-class theorem.
-/
theorem gen3_proof_first_policy (psi : CO) : InGen3Sector psi → True := by
  intro _
  trivial

end CausalGraph
