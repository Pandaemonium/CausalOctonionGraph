/-
  CausalGraphTheory/PhotonMassless.lean
  PHOTON-001 Gate 2: Photon Masslessness from Zero Gate Density

  Proves photon_gate_density_zero: every PhotonState has gateCount = 0.

  Type chain:
    CO := ComplexOctonion Int = Octonion (FormalComplex Int)
    omegaDoubled : CO := WittBasis.vacuumDoubled (R := Int)
    .c : Fin 8 -> FormalComplex Int

  Physical meaning:
  - Photon lives in {e0, e7} subspace (no SU(3)_c charge).
  - Zero G2 triality overhead -> V_photon = 0.

  Claim:   claims/PHOTON-001.yml
  RFC:     rfc/RFC-015_Photon_Energy_COG.md
-/

import CausalGraphTheory.PhotonMasslessness

namespace CausalGraph

/-- Color-sector Fano index: i : Fin 6 |-> i.val+1 : Fin 8. -/
def colorSectorIdx (i : Fin 6) : Fin 8 := Fin.mk (i.val + 1) (by omega)

/--
  A PhotonState bundles a CO = Octonion (FormalComplex Int) element
  with proof that all color-sector (Fano indices 1-6) components vanish.
-/
structure PhotonState where
  state     : CO
  colorZero : forall i : Fin 6, state.c (colorSectorIdx i) = 0

/-- Gate count: number of non-zero color-sector entries (G2 triality overhead). -/
noncomputable def gateCount (s : PhotonState) : Nat :=
  (Finset.univ.filter (fun i : Fin 6 => s.state.c (colorSectorIdx i) ≠ 0)).card

/--
  photon_gate_density_zero: Every PhotonState has gateCount = 0.

  Proof: colorZero forces all filter predicates to False,
  so the filter set is empty and has cardinality 0.

  Physical consequence: V_photon = 0 in the COG model.
-/
theorem photon_gate_density_zero (s : PhotonState) : gateCount s = 0 := by
  simp only [gateCount]
  have hempty : (Finset.univ.filter (fun i : Fin 6 => s.state.c (colorSectorIdx i) ≠ 0)) = ∅ := by
    ext i
    simp only [Finset.mem_filter, Finset.mem_univ, true_and, Finset.not_mem_empty, iff_false,
               not_not]
    exact s.colorZero i
  simp [hempty]

/--
  omegaDoubled is a canonical PhotonState.

  We prove colorZero by fin_cases on Fin 6, directly unfolding the
  definitions to confirm each of the 6 color-sector components is 0.
  This avoids dependence on the private colorFin from PhotonMasslessness.
-/
def omegaDoubledPhoton : PhotonState where
  state     := omegaDoubled
  colorZero := by
    intro i
    fin_cases i <;>
      simp [colorSectorIdx, omegaDoubled, WittBasis.vacuumDoubled] <;>
      rfl

/-- The canonical vacuum state has zero gate count. -/
theorem omegaDoubled_gateCount_zero : gateCount omegaDoubledPhoton = 0 :=
  photon_gate_density_zero omegaDoubledPhoton

end CausalGraph

-- Leibniz