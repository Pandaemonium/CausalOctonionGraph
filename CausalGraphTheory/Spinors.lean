/-
  CausalGraphTheory/Spinors.lean
  Phase 2.5: Generation labels and muon state vector

  Defines the three lepton generations using Furey's projector-sector
  construction from C⊗O (arXiv:1910.08395, Eq. 19-21).

  The generation of a state is determined by which (s vs. s*) × (S vs. S*)
  projector block it lives in:
    gen1 (electron): s · _ · S*   sector
    gen2 (muon):     s* · _ · S*  sector
    gen3 (tauon):    s* · _ · S   sector
    sterile:         s · _ · S    sector

  where s = (1/2)(e₀ + i·e₇) acts from the LEFT
  and   S = (1/2)(e₀ + i·e₇) acts from the RIGHT.

  Convention source of truth: rfc/CONVENTIONS.md
  Claim: claims/muon_mass.yml (LEPTON-001)
  Implementation plan: rfc/RFC-010_Rep_Labels_and_Muon_Orbit.md
-/

import CausalGraphTheory.WittBasis

namespace CausalGraph

-- ============================================================
-- Generation labels
-- ============================================================

/--
  The three lepton generations plus the sterile sector.
  Based on the Furey projector-sector construction (arXiv:1910.08395, Eq. 19).
    gen1 = electron family,  s · S*  sector
    gen2 = muon family,      s* · S* sector
    gen3 = tauon family,     s* · S  sector
    sterile = no physical charged lepton, s · S sector
-/
inductive Generation : Type where
  | gen1    : Generation   -- electron family:  s · _ · S*
  | gen2    : Generation   -- muon family:     s* · _ · S*
  | gen3    : Generation   -- tauon family:    s* · _ · S
  | sterile : Generation   -- sterile sector:   s · _ · S
  deriving DecidableEq, Repr

/-- Cyclic generation shift: gen1 → gen2 → gen3 → gen1, sterile fixed. -/
def generationShift : Generation → Generation
  | .gen1    => .gen2
  | .gen2    => .gen3
  | .gen3    => .gen1
  | .sterile => .sterile

/-- The generation shift has order 3 on gen1/gen2/gen3 (Z₃ cyclic action). -/
theorem generationShift_order3 (g : Generation) :
    generationShift (generationShift (generationShift g)) = g := by
  cases g <;> rfl

-- ============================================================
-- Projector elements (working at doubled scale to avoid 1/2)
--   WittBasis.vacuumDoubled  = 2s  = e₀ + i·e₇
--   leftVacConjDoubled       = 2s* = e₀ - i·e₇
--   rightVacConjDoubled      = 2S* = e₀ - i·e₇ (same formula, right action)
-- ============================================================

/-- Doubled conjugate left vacuum: 2·s* = e₀ - i·e₇.
    Used as the left projector for gen2 and gen3 states.
    Components: e₀ has FormalComplex coefficient (1, 0), e₇ has (0, -1). -/
def leftVacConjDoubled : ComplexOctonion ℤ :=
  ⟨fun k =>
    if k == 0 then ⟨1, 0⟩
    else if k == 7 then ⟨0, -1⟩
    else ⟨0, 0⟩⟩

/-- The right conjugate vacuum 2·S* has the same formula as 2·s*.
    Semantically applied from the RIGHT in the s*·(inner)·S* sandwich. -/
abbrev rightVacConjDoubled : ComplexOctonion ℤ := leftVacConjDoubled

-- ============================================================
-- Muon inner state
--
-- Furey (2019), Eq. 21 (second charged lepton):
--   ψμ = s*·S* · (-i·e₂ + e₆ + e₁₂₃ - i·e₁₃₆) · s*·S*
--
-- Triple products (Furey convention, rfc/CONVENTIONS.md §2):
--   e₁₂₃ = (e₁·e₂)·e₃ = e₃·e₃ = -e₀
--          [e₁·e₂ = +e₃ from L1=(1,2,3); e₃·e₃ = -e₀ since eₖ² = -e₀]
--   e₁₃₆ = (e₁·e₃)·e₆ = (-e₂)·e₆ = -(e₂·e₆) = -(-e₄) = +e₄
--          [e₁·e₃ = -e₂ (anti-cyclic L1); e₂·e₆ = -e₄ (sign table)]
--
-- Therefore: innerμ = -i·e₂ + e₆ + (-e₀) - i·(+e₄)
--                     = -e₀  -i·e₂  -i·e₄  +e₆
--
-- Lean-verified (#eval fanoBasisMul):
--   fanoBasisMul 0 1 = (2, 1)   e₁·e₂ = +e₃
--   fanoBasisMul 0 2 = (1, -1)  e₁·e₃ = -e₂
--   fanoBasisMul 1 5 = (3, -1)  e₂·e₆ = -e₄
-- ============================================================

/-- The inner expression in the muon state (Furey 2019, Eq. 21).
    Components as FormalComplex ℤ values at each Fin 8 position:
      index 0 (e₀): (re=-1, im=0)   -- -e₀ (from e₁₂₃ = -e₀)
      index 2 (e₂): (re=0, im=-1)   -- -i·e₂
      index 4 (e₄): (re=0, im=-1)   -- -i·e₄ (from -i·e₁₃₆ = -i·e₄)
      index 6 (e₆): (re=1, im=0)    -- +e₆ -/
def muonInner : ComplexOctonion ℤ :=
  ⟨fun k =>
    if k == 0 then ⟨-1, 0⟩
    else if k == 2 then ⟨0, -1⟩
    else if k == 4 then ⟨0, -1⟩
    else if k == 6 then ⟨1, 0⟩
    else ⟨0, 0⟩⟩

-- ============================================================
-- Gen-2 (muon) state at 4× scale
-- ============================================================

/-- The generation-2 (muon) state at 4× scale (avoids 1/4 denominators).
    Computed as the s*·(inner)·S* sandwich of muonInner:
      4·ψμ = (2s*) · (innerμ · (2S*))
              = (e₀ - i·e₇) · ((-e₀ - i·e₂ - i·e₄ + e₆) · (e₀ - i·e₇))

    Parenthesization: innerμ · (2S*) first, then (2s*) from the left.
    This places the result in the s*·S* sector (generation-2).

    Convention: Furey (2019), Eq. 21, second charged lepton (muon). -/
def gen2StateQuadruple : ComplexOctonion ℤ :=
  leftVacConjDoubled * (muonInner * rightVacConjDoubled)

-- ============================================================
-- Consistency check stub
-- ============================================================

/-- The muon state ψμ = (1/4)·gen2StateQuadruple satisfies ψμ² = −ψμ.
    Numerically verified by calc/test_spinor_state.py (Phase B2):
      gen2StateQuadruple = −2·e₀ + 2i·e₇
      gen2StateQuadruple² = 8·e₀ − 8i·e₇ = −4·gen2StateQuadruple
    The state is anti-idempotent (ψ² = −ψ), not idempotent.
    At 4× scale: gen2StateQuadruple² = −4·gen2StateQuadruple.
    TODO: replace sorry with native_decide once Lean can reduce the product. -/
theorem gen2State_proportional_idempotent :
    gen2StateQuadruple * gen2StateQuadruple =
    ⟨fun k => ⟨-4 * (gen2StateQuadruple.c k).re,
               -4 * (gen2StateQuadruple.c k).im⟩⟩ := by
  sorry

end CausalGraph
