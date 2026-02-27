/-
  CausalGraphTheory/PhotonMasslessness.lean
  Phase 6.5: Photon Masslessness from Locked Conventions

  Proves that the photon operator (L_{e7}) acting on the vacuum
  produces zero color-sector excitations at every step of the orbit.
  The vacuum orbit {2ω, -i·2ω, -2ω, i·2ω} stays entirely
  in the {e₀, e₇} subspace (Fano indices 0 and 7).
  Since the SU(3)_c color sector is indices 1-6, no G₂ triality
  overhead is triggered: V_photon = 0.

  Physical interpretation (RFC-015 §6):
    The photon is massless because U(1)_EM = Q = N/3 commutes with
    SU(3)_c. The vacuum orbit confirms this algebraically: the e7
    operator never excites the color sector of the vacuum state.

  Claim:   claims/PHOTON-001.yml
  RFC:     rfc/RFC-015_Photon_Energy_COG.md
  Sources: sources/photon_energy_discrete_models.md
-/

import CausalGraphTheory.Spinors

namespace CausalGraph

-- colorFin i : Fin 8 is the color-sector index (i.val + 1) for i : Fin 6.
-- Uses Fin.mk (pure ASCII) rather than ⟨⟩ anonymous constructor to avoid
-- UTF-8 encoding issues on Windows with the Edit tool.
private def colorFin (i : Fin 6) : Fin 8 := Fin.mk (i.val + 1) (by omega)

-- ============================================================
-- Color-sector zero: individual orbit points
-- ============================================================

/--
  The doubled vacuum state (2ω) has zero color-sector components.
  Color sector = Fano basis indices 1 through 6 (the Witt pairs).
  The vacuum lives purely in the {e₀, ie₇} subspace.
-/
theorem omegaDoubled_colorSector_zero (i : Fin 6) :
    omegaDoubled.c (colorFin i) = 0 := by
  fin_cases i <;> simp [colorFin, omegaDoubled, WittBasis.vacuumDoubled] <;> rfl

/--
  The photon-hit vacuum (-i·2ω = e7·2ω) also has zero color-sector components.
  Proved separately so downstream theorems can cite this directly.
-/
theorem negIOmegaDoubled_colorSector_zero (i : Fin 6) :
    negIOmegaDoubled.c (colorFin i) = 0 := by
  fin_cases i <;> simp [colorFin, negIOmegaDoubled]

-- ============================================================
-- Full orbit: all four steps are colorless
-- ============================================================

/--
  **The vacuum orbit is colorless.**

  The photon operator L_{e₇}, applied to the vacuum ω, produces no
  color-sector excitations at any step of the 4-cycle orbit:
    Step 0:  2ω             (indices 1-6 all zero)
    Step 1:  e7 · 2ω = -i·2ω   (indices 1-6 all zero)
    Step 2:  e7² · 2ω = -2ω    (indices 1-6 all zero)
    Step 3:  e7³ · 2ω = i·2ω    (indices 1-6 all zero)

  This is the algebraic grounding of V_photon = 0:
  no SU(3)_c charge is excited during photon-vacuum traversal,
  so zero G₂ triality overhead is incurred.

  Physical consequence: photon propagation through vacuum nodes costs
  exactly 1 tick/hop with zero drag (c = 1 tick/node, from RFC-013).
-/
theorem vacuum_orbit_colorSector_zero (i : Fin 6) :
    omegaDoubled.c (colorFin i) = 0 ∧
    (e7LeftOp * omegaDoubled).c (colorFin i) = 0 ∧
    (e7LeftOp * (e7LeftOp * omegaDoubled)).c (colorFin i) = 0 ∧
    (e7LeftOp * (e7LeftOp * (e7LeftOp * omegaDoubled))).c (colorFin i) = 0 := by
  refine ⟨omegaDoubled_colorSector_zero i, ?_, ?_, ?_⟩
  · rw [e7Left_on_omegaDoubled]
    exact negIOmegaDoubled_colorSector_zero i
  · have h2 : e7LeftOp * (e7LeftOp * omegaDoubled) = -omegaDoubled :=
      e7_left_twice_neg omegaDoubled
    rw [h2]
    change -(omegaDoubled.c (colorFin i)) = 0
    simp [omegaDoubled_colorSector_zero i]
  · have h3 : e7LeftOp * (e7LeftOp * (e7LeftOp * omegaDoubled)) =
        -(e7LeftOp * omegaDoubled) :=
      e7_left_twice_neg (e7LeftOp * omegaDoubled)
    rw [h3, e7Left_on_omegaDoubled]
    change -(negIOmegaDoubled.c (colorFin i)) = 0
    simp [negIOmegaDoubled_colorSector_zero i]

end CausalGraph
