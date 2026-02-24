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

import CausalGraphTheory.OctonionAlt
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
-- Universal C_e = 4 theorem (LEPTON-001 support)
-- ============================================================

abbrev CO := ComplexOctonion Int

/-- Left-action photon operator used in COG: multiply by e7 from the left. -/
def e7LeftOp : CO := Octonion.basis (R := FormalComplex Int) 7

private theorem neg_neg_octonion {R : Type} [CommRing R] (x : Octonion R) :
    -(-x) = x := by
  apply Octonion.ext
  intro i
  exact neg_neg (x.c i)

private theorem neg_one_mul_octonion {R : Type} [CommRing R] (x : Octonion R) :
    (-(1 : Octonion R)) * x = -x := by
  apply Octonion.ext
  intro i
  fin_cases i
  <;> dsimp only [HMul.hMul, Mul.mul, OfNat.ofNat, One.one, Neg.neg]
  <;> norm_num [Fin.ofNat, Fin.mk.injEq]
  <;> simp only [Octonion.fold_mul]
  <;> ring

private theorem mul_neg_one_octonion {R : Type} [CommRing R] (x : Octonion R) :
    x * (-(1 : Octonion R)) = -x := by
  apply Octonion.ext
  intro i
  fin_cases i
  <;> dsimp only [HMul.hMul, Mul.mul, OfNat.ofNat, One.one, Neg.neg]
  <;> norm_num [Fin.ofNat, Fin.mk.injEq]
  <;> simp only [Octonion.fold_mul]
  <;> ring

private theorem basis7_square_neg_one {R : Type} [CommRing R] :
    (Octonion.basis (R := R) 7) * (Octonion.basis (R := R) 7) = -(1 : Octonion R) := by
  apply Octonion.ext
  intro i
  fin_cases i
  <;> dsimp only [HMul.hMul, Mul.mul, OfNat.ofNat, One.one, Neg.neg, Octonion.basis]
  <;> norm_num [Fin.ofNat, Fin.mk.injEq]
  <;> simp only [Octonion.fold_mul]
  <;> ring

/-- e7^2 = -1 for the left-action operator in C x O over Z. -/
theorem e7LeftOp_square_eq_neg_one :
    e7LeftOp * e7LeftOp = -(1 : CO) := by
  simpa [e7LeftOp] using (basis7_square_neg_one (R := FormalComplex Int))

/-- Two left e7 actions give a sign flip for every state. -/
theorem e7_left_twice_neg (x : CO) :
    e7LeftOp * (e7LeftOp * x) = -x := by
  calc
    e7LeftOp * (e7LeftOp * x) = (e7LeftOp * e7LeftOp) * x := by
      simpa using Octonion.left_alternative e7LeftOp x
    _ = (-(1 : CO)) * x := by
      rw [e7LeftOp_square_eq_neg_one]
    _ = -x := by
      simpa using neg_one_mul_octonion x

/-- Four left e7 actions return any state exactly. -/
theorem e7_left_four_id (x : CO) :
    e7LeftOp * (e7LeftOp * (e7LeftOp * (e7LeftOp * x))) = x := by
  calc
    e7LeftOp * (e7LeftOp * (e7LeftOp * (e7LeftOp * x))) = -(e7LeftOp * (e7LeftOp * x)) := by
      simpa using e7_left_twice_neg (x := e7LeftOp * (e7LeftOp * x))
    _ = -(-x) := by
      rw [e7_left_twice_neg]
    _ = x := by
      simpa using neg_neg_octonion x

private theorem neg_eq_self_implies_zero (x : CO) (h : -x = x) : x = 0 := by
  apply Octonion.ext
  intro i
  have hi : -(x.c i) = x.c i := by
    exact congrArg (fun y => y.c i) h
  exact FormalComplex.ext
    (by
      have hire : -((x.c i).re) = (x.c i).re := by
        exact congrArg FormalComplex.re hi
      have hre0 : (x.c i).re = 0 := by omega
      simpa using hre0)
    (by
      have hiim : -((x.c i).im) = (x.c i).im := by
        exact congrArg FormalComplex.im hi
      have him0 : (x.c i).im = 0 := by omega
      simpa using him0)

/-- No non-zero state has period 2 under repeated left e7 action. -/
theorem e7_left_period_two_impossible {x : CO} (hx : Ne x 0) :
    Ne (e7LeftOp * (e7LeftOp * x)) x := by
  intro h2
  have hneg : -x = x := by
    simpa [e7_left_twice_neg (x := x)] using h2
  exact hx (neg_eq_self_implies_zero x hneg)

/-- No non-zero state is fixed by a single left e7 action. -/
theorem e7_left_period_one_impossible {x : CO} (hx : Ne x 0) :
    Ne (e7LeftOp * x) x := by
  intro h1
  have h2 : e7LeftOp * (e7LeftOp * x) = x := by
    calc
      e7LeftOp * (e7LeftOp * x) = e7LeftOp * x := by
        simp [h1]
      _ = x := h1
  exact e7_left_period_two_impossible (x := x) hx h2

/-- Universal C_e theorem: every non-zero state has exact period 4 under left e7 action. -/
theorem universal_Ce_period_four (x : CO) (hx : Ne x 0) :
    e7LeftOp * (e7LeftOp * (e7LeftOp * (e7LeftOp * x))) = x /\
    Ne (e7LeftOp * x) x /\
    Ne (e7LeftOp * (e7LeftOp * x)) x := by
  exact And.intro (e7_left_four_id x)
    (And.intro (e7_left_period_one_impossible (x := x) hx)
      (e7_left_period_two_impossible (x := x) hx))

/-- Two right e7 actions give a sign flip for every state. -/
theorem e7_right_twice_neg (x : CO) :
    (x * e7LeftOp) * e7LeftOp = -x := by
  calc
    (x * e7LeftOp) * e7LeftOp = x * (e7LeftOp * e7LeftOp) := by
      simpa using (Octonion.right_alternative e7LeftOp x)
    _ = x * (-(1 : CO)) := by
      rw [e7LeftOp_square_eq_neg_one]
    _ = -x := by
      simpa using mul_neg_one_octonion x

/-- Four right e7 actions return any state exactly. -/
theorem e7_right_four_id (x : CO) :
    (((x * e7LeftOp) * e7LeftOp) * e7LeftOp) * e7LeftOp = x := by
  calc
    (((x * e7LeftOp) * e7LeftOp) * e7LeftOp) * e7LeftOp = -((x * e7LeftOp) * e7LeftOp) := by
      simpa using e7_right_twice_neg (x := (x * e7LeftOp) * e7LeftOp)
    _ = -(-x) := by
      rw [e7_right_twice_neg]
    _ = x := by
      simpa using neg_neg_octonion x

/-- No non-zero state has period 2 under repeated right e7 action. -/
theorem e7_right_period_two_impossible {x : CO} (hx : Ne x 0) :
    Ne ((x * e7LeftOp) * e7LeftOp) x := by
  intro h2
  have hneg : -x = x := by
    simpa [e7_right_twice_neg (x := x)] using h2
  exact hx (neg_eq_self_implies_zero x hneg)

/-- No non-zero state is fixed by a single right e7 action. -/
theorem e7_right_period_one_impossible {x : CO} (hx : Ne x 0) :
    Ne (x * e7LeftOp) x := by
  intro h1
  have h2 : (x * e7LeftOp) * e7LeftOp = x := by
    calc
      (x * e7LeftOp) * e7LeftOp = x * e7LeftOp := by
        simp [h1]
      _ = x := h1
  exact e7_right_period_two_impossible (x := x) hx h2

/-- Universal C_e theorem in right-action form: every non-zero state has exact period 4. -/
theorem universal_Ce_right_period_four (x : CO) (hx : Ne x 0) :
    (((x * e7LeftOp) * e7LeftOp) * e7LeftOp) * e7LeftOp = x /\
    Ne (x * e7LeftOp) x /\
    Ne ((x * e7LeftOp) * e7LeftOp) x := by
  exact And.intro (e7_right_four_id x)
    (And.intro (e7_right_period_one_impossible (x := x) hx)
      (e7_right_period_two_impossible (x := x) hx))

/-- Doubled vacuum state from the Witt construction over Z. -/
abbrev omegaDoubled : CO := (WittBasis.vacuumDoubled (R := Int))

/-- -i * (2ω) written in components over Z. -/
def negIOmegaDoubled : CO :=
  Octonion.mk (fun k =>
    if k == 0 then FormalComplex.mk 0 (-1)
    else if k == 7 then FormalComplex.mk 1 0
    else 0)

set_option maxHeartbeats 800000

/-- Explicit phase action of left e7 on doubled vacuum: e7·(2ω) = -i·(2ω). -/
theorem e7Left_on_omegaDoubled :
    e7LeftOp * omegaDoubled = negIOmegaDoubled := by
  apply Octonion.ext
  intro i
  fin_cases i
  <;> apply FormalComplex.ext
  <;> simp only [HMul.hMul, Mul.mul, OfNat.ofNat,
                  e7LeftOp, omegaDoubled, WittBasis.vacuumDoubled,
                  negIOmegaDoubled, Octonion.basis,
                  FormalComplex.add_re, FormalComplex.add_im,
                  FormalComplex.sub_re, FormalComplex.sub_im]
  <;> norm_num [Fin.ofNat, Fin.mk.injEq]

/-- Explicit phase action of right e7 on doubled vacuum: (2ω)·e7 = -i·(2ω). -/
theorem e7Right_on_omegaDoubled :
    omegaDoubled * e7LeftOp = negIOmegaDoubled := by
  apply Octonion.ext
  intro i
  fin_cases i
  <;> apply FormalComplex.ext
  <;> simp only [HMul.hMul, Mul.mul, OfNat.ofNat,
                  e7LeftOp, omegaDoubled, WittBasis.vacuumDoubled,
                  negIOmegaDoubled, Octonion.basis,
                  FormalComplex.add_re, FormalComplex.add_im,
                  FormalComplex.sub_re, FormalComplex.sub_im]
  <;> norm_num [Fin.ofNat, Fin.mk.injEq]

/-- The doubled vacuum state is non-zero. -/
theorem omegaDoubled_ne_zero : Ne omegaDoubled 0 := by
  intro h
  have h0 : (omegaDoubled.c 0) = (0 : CO).c 0 := by
    simpa using congrArg (fun z : CO => z.c 0) h
  have h0re : (omegaDoubled.c 0).re = ((0 : CO).c 0).re := by
    exact congrArg FormalComplex.re h0
  have hone : (omegaDoubled.c 0).re = 1 := by
    simp [omegaDoubled, WittBasis.vacuumDoubled]
  have : (1 : Int) = 0 := by
    calc
      (1 : Int) = (omegaDoubled.c 0).re := by simpa using hone.symm
      _ = ((0 : CO).c 0).re := h0re
      _ = 0 := rfl
  exact Int.one_ne_zero this

/-- The doubled vacuum has exact period 4 under repeated left e7 action. -/
theorem vacuum_orbit_exact_period_four :
    e7LeftOp * (e7LeftOp * (e7LeftOp * (e7LeftOp * omegaDoubled))) = omegaDoubled /\
    Ne (e7LeftOp * omegaDoubled) omegaDoubled /\
    Ne (e7LeftOp * (e7LeftOp * omegaDoubled)) omegaDoubled := by
  exact universal_Ce_period_four omegaDoubled omegaDoubled_ne_zero

/-- The doubled vacuum also has exact period 4 under right e7 action. -/
theorem vacuum_orbit_exact_period_four_right :
    (((omegaDoubled * e7LeftOp) * e7LeftOp) * e7LeftOp) * e7LeftOp = omegaDoubled /\
    Ne (omegaDoubled * e7LeftOp) omegaDoubled /\
    Ne ((omegaDoubled * e7LeftOp) * e7LeftOp) omegaDoubled := by
  exact universal_Ce_right_period_four omegaDoubled omegaDoubled_ne_zero

/-- Lean-side doubled Furey electron state:
    (2α₁†)·((2α₂†)·((2α₃†)·(2ω))). -/
def fureyElectronStateDoubled : CO :=
  (WittBasis.wittRaiseDoubled (R := Int) 0) *
    ((WittBasis.wittRaiseDoubled (R := Int) 1) *
      ((WittBasis.wittRaiseDoubled (R := Int) 2) * omegaDoubled))

/-- -8i * (2ω†) in component form over Z.
    This is the closed form of the doubled Furey electron state:
    16·ψ_e = α₁†·(α₂†·(α₃†·ω)) at 16× scale = -8i·e₀ - 8·e₇. -/
def negEightIOmegaDagDoubled : CO :=
  Octonion.mk (fun k =>
    if k == 0 then FormalComplex.mk 0 (-8)
    else if k == 7 then FormalComplex.mk (-8) 0
    else 0)

/-- The doubled Furey electron state equals -8i·(2ω†):
    α₁†·(α₂†·(α₃†·(2ω))) = negEightIOmegaDagDoubled = -8i·e₀ - 8·e₇.
    Proof: component-by-component norm_num over ℤ. -/
theorem fureyElectronStateDoubled_closed_form :
    fureyElectronStateDoubled = negEightIOmegaDagDoubled := by
  apply Octonion.ext
  intro i
  fin_cases i
  <;> apply FormalComplex.ext
  <;> simp only [HMul.hMul, Mul.mul, OfNat.ofNat,
                  fureyElectronStateDoubled, negEightIOmegaDagDoubled,
                  omegaDoubled, WittBasis.vacuumDoubled,
                  WittBasis.wittRaiseDoubled, WittBasis.wittPair,
                  FormalComplex.add_re, FormalComplex.add_im,
                  FormalComplex.sub_re, FormalComplex.sub_im]
  <;> norm_num [Fin.ofNat, Fin.mk.injEq]

/-- The doubled Furey electron state is non-zero. -/
theorem fureyElectronStateDoubled_ne_zero : Ne fureyElectronStateDoubled 0 := by
  intro h
  have h0 : (fureyElectronStateDoubled.c 7).re = ((0 : CO).c 7).re := by
    exact congrArg (fun z : CO => (z.c 7).re) h
  rw [show (fureyElectronStateDoubled.c 7).re = (-8 : Int) by rfl] at h0
  have hz : ((0 : CO).c 7).re = (0 : Int) := rfl
  rw [hz] at h0
  norm_num at h0

/-- The doubled Furey electron state has exact period 4 under left e7 action. -/
theorem fureyElectronState_left_orbit_exact_period_four :
    e7LeftOp * (e7LeftOp * (e7LeftOp * (e7LeftOp * fureyElectronStateDoubled))) =
      fureyElectronStateDoubled /\
    Ne (e7LeftOp * fureyElectronStateDoubled) fureyElectronStateDoubled /\
    Ne (e7LeftOp * (e7LeftOp * fureyElectronStateDoubled)) fureyElectronStateDoubled := by
  exact universal_Ce_period_four fureyElectronStateDoubled fureyElectronStateDoubled_ne_zero

/-- The doubled Furey electron state has exact period 4 under right e7 action. -/
theorem fureyElectronState_right_orbit_exact_period_four :
    (((fureyElectronStateDoubled * e7LeftOp) * e7LeftOp) * e7LeftOp) * e7LeftOp =
      fureyElectronStateDoubled /\
    Ne (fureyElectronStateDoubled * e7LeftOp) fureyElectronStateDoubled /\
    Ne ((fureyElectronStateDoubled * e7LeftOp) * e7LeftOp) fureyElectronStateDoubled := by
  exact universal_Ce_right_period_four fureyElectronStateDoubled fureyElectronStateDoubled_ne_zero

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

/-- +i * (2ω†) in component form over Z, where 2ω† = e₀ - i·e₇. -/
def posIOmegaDagDoubled : CO :=
  Octonion.mk (fun k =>
    if k == 0 then FormalComplex.mk 0 1
    else if k == 7 then FormalComplex.mk 1 0
    else 0)

/-- The doubled conjugate vacuum is non-zero. -/
theorem leftVacConjDoubled_ne_zero : Ne leftVacConjDoubled 0 := by
  intro h
  have h0 : (leftVacConjDoubled.c 0) = ((0 : CO).c 0) := by
    exact congrArg (fun z : CO => z.c 0) h
  have h0re : (leftVacConjDoubled.c 0).re = ((0 : CO).c 0).re := by
    exact congrArg FormalComplex.re h0
  have hone : (leftVacConjDoubled.c 0).re = 1 := by
    simp [leftVacConjDoubled]
  have : (1 : Int) = 0 := by
    calc
      (1 : Int) = (leftVacConjDoubled.c 0).re := by simpa using hone.symm
      _ = ((0 : CO).c 0).re := h0re
      _ = 0 := rfl
  exact Int.one_ne_zero this

set_option maxHeartbeats 800000

/-- Explicit phase action of left e7 on doubled conjugate vacuum: e7·(2ω†) = +i·(2ω†). -/
theorem e7Left_on_leftVacConjDoubled :
    e7LeftOp * leftVacConjDoubled = posIOmegaDagDoubled := by
  apply Octonion.ext
  intro i
  fin_cases i
  <;> apply FormalComplex.ext
  <;> simp only [HMul.hMul, Mul.mul, OfNat.ofNat,
                  e7LeftOp, leftVacConjDoubled, posIOmegaDagDoubled,
                  Octonion.basis,
                  FormalComplex.add_re, FormalComplex.add_im,
                  FormalComplex.sub_re, FormalComplex.sub_im]
  <;> norm_num [Fin.ofNat, Fin.mk.injEq]

/-- Explicit phase action of right e7 on doubled conjugate vacuum: (2ω†)·e7 = +i·(2ω†). -/
theorem e7Right_on_leftVacConjDoubled :
    leftVacConjDoubled * e7LeftOp = posIOmegaDagDoubled := by
  apply Octonion.ext
  intro i
  fin_cases i
  <;> apply FormalComplex.ext
  <;> simp only [HMul.hMul, Mul.mul, OfNat.ofNat,
                  e7LeftOp, leftVacConjDoubled, posIOmegaDagDoubled,
                  Octonion.basis,
                  FormalComplex.add_re, FormalComplex.add_im,
                  FormalComplex.sub_re, FormalComplex.sub_im]
  <;> norm_num [Fin.ofNat, Fin.mk.injEq]

/-- Scaled idempotence for doubled conjugate vacuum: (2ω†)² = 2·(2ω†). -/
theorem leftVacConjDoubled_idempotent_scaled :
    leftVacConjDoubled * leftVacConjDoubled = WittBasis.doubleCO leftVacConjDoubled := by
  apply Octonion.ext
  intro i
  fin_cases i
  <;> apply FormalComplex.ext
  <;> simp only [HMul.hMul, Mul.mul, OfNat.ofNat,
                  leftVacConjDoubled, WittBasis.doubleCO,
                  FormalComplex.add_re, FormalComplex.add_im,
                  FormalComplex.sub_re, FormalComplex.sub_im]
  <;> norm_num [Fin.ofNat, Fin.mk.injEq]

/-- The doubled conjugate vacuum has exact period 4 under left e7 action. -/
theorem leftVacConjDoubled_left_orbit_exact_period_four :
    e7LeftOp * (e7LeftOp * (e7LeftOp * (e7LeftOp * leftVacConjDoubled))) = leftVacConjDoubled /\
    Ne (e7LeftOp * leftVacConjDoubled) leftVacConjDoubled /\
    Ne (e7LeftOp * (e7LeftOp * leftVacConjDoubled)) leftVacConjDoubled := by
  exact universal_Ce_period_four leftVacConjDoubled leftVacConjDoubled_ne_zero

/-- The doubled conjugate vacuum has exact period 4 under right e7 action. -/
theorem leftVacConjDoubled_right_orbit_exact_period_four :
    (((leftVacConjDoubled * e7LeftOp) * e7LeftOp) * e7LeftOp) * e7LeftOp = leftVacConjDoubled /\
    Ne (leftVacConjDoubled * e7LeftOp) leftVacConjDoubled /\
    Ne ((leftVacConjDoubled * e7LeftOp) * e7LeftOp) leftVacConjDoubled := by
  exact universal_Ce_right_period_four leftVacConjDoubled leftVacConjDoubled_ne_zero

/-- Lean-side doubled dual Furey electron state:
    (2α₁)·((2α₂)·((2α₃)·(2ω†))). -/
def fureyDualElectronStateDoubled : CO :=
  (WittBasis.wittLowerDoubled (R := Int) 0) *
    ((WittBasis.wittLowerDoubled (R := Int) 1) *
      ((WittBasis.wittLowerDoubled (R := Int) 2) * leftVacConjDoubled))

/-- -8i * (2ω) in component form over Z.
    This is the closed form of the doubled dual Furey electron state:
    16·ψ_dual = α₁·(α₂·(α₃·ω†)) at 16× scale = -8i·e₀ + 8·e₇.
    Shows the dual sector (lowering operators from conjugate vacuum) maps to
    a state proportional to the regular vacuum ω, connecting the two projector sectors. -/
def negEightIOmegaDoubled : CO :=
  Octonion.mk (fun k =>
    if k == 0 then FormalComplex.mk 0 (-8)
    else if k == 7 then FormalComplex.mk 8 0
    else 0)

/-- The doubled dual Furey electron state equals -8i·(2ω):
    α₁·(α₂·(α₃·(2ω†))) = negEightIOmegaDoubled = -8i·e₀ + 8·e₇.
    Proof: component-by-component norm_num over ℤ. -/
theorem fureyDualElectronStateDoubled_closed_form :
    fureyDualElectronStateDoubled = negEightIOmegaDoubled := by
  apply Octonion.ext
  intro i
  fin_cases i
  <;> apply FormalComplex.ext
  <;> simp only [HMul.hMul, Mul.mul, OfNat.ofNat,
                  fureyDualElectronStateDoubled, negEightIOmegaDoubled,
                  leftVacConjDoubled, WittBasis.wittLowerDoubled, WittBasis.wittPair,
                  FormalComplex.add_re, FormalComplex.add_im,
                  FormalComplex.sub_re, FormalComplex.sub_im]
  <;> norm_num [Fin.ofNat, Fin.mk.injEq]

/-- The doubled dual Furey electron state is non-zero. -/
theorem fureyDualElectronStateDoubled_ne_zero : Ne fureyDualElectronStateDoubled 0 := by
  intro h
  have h0 : (fureyDualElectronStateDoubled.c 7).re = ((0 : CO).c 7).re := by
    exact congrArg (fun z : CO => (z.c 7).re) h
  rw [show (fureyDualElectronStateDoubled.c 7).re = (8 : Int) by rfl] at h0
  have hz : ((0 : CO).c 7).re = (0 : Int) := rfl
  rw [hz] at h0
  norm_num at h0

/-- The doubled dual Furey electron state has exact period 4 under left e7 action. -/
theorem fureyDualElectronState_left_orbit_exact_period_four :
    e7LeftOp * (e7LeftOp * (e7LeftOp * (e7LeftOp * fureyDualElectronStateDoubled))) =
      fureyDualElectronStateDoubled /\
    Ne (e7LeftOp * fureyDualElectronStateDoubled) fureyDualElectronStateDoubled /\
    Ne (e7LeftOp * (e7LeftOp * fureyDualElectronStateDoubled)) fureyDualElectronStateDoubled := by
  exact universal_Ce_period_four fureyDualElectronStateDoubled fureyDualElectronStateDoubled_ne_zero

/-- The doubled dual Furey electron state has exact period 4 under right e7 action. -/
theorem fureyDualElectronState_right_orbit_exact_period_four :
    (((fureyDualElectronStateDoubled * e7LeftOp) * e7LeftOp) * e7LeftOp) * e7LeftOp =
      fureyDualElectronStateDoubled /\
    Ne (fureyDualElectronStateDoubled * e7LeftOp) fureyDualElectronStateDoubled /\
    Ne ((fureyDualElectronStateDoubled * e7LeftOp) * e7LeftOp) fureyDualElectronStateDoubled := by
  exact universal_Ce_right_period_four fureyDualElectronStateDoubled fureyDualElectronStateDoubled_ne_zero

set_option maxHeartbeats 200000

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
    Proved by unfolding definitions component-wise and applying norm_num
    for integer arithmetic (replacing native_decide per Gemini 2026-02-22). -/
theorem gen2State_proportional_idempotent :
    gen2StateQuadruple * gen2StateQuadruple =
    ⟨fun k => ⟨-4 * (gen2StateQuadruple.c k).re,
               -4 * (gen2StateQuadruple.c k).im⟩⟩ := by
  -- After ext + fin_cases, k is a concrete Fin 8 literal.
  -- The kernel evaluates: if-then-else collapses, integer arithmetic computes.
  -- rfl closes each goal by definitional equality (no simp, no native_decide).
  apply Octonion.ext
  intro k; fin_cases k
  all_goals rfl

/-- The generation-2 state (4·ψ_μ) is non-zero. -/
theorem gen2StateQuadruple_ne_zero : Ne gen2StateQuadruple 0 := by
  intro h
  have h0 : (gen2StateQuadruple.c 0).re = ((0 : CO).c 0).re := by
    exact congrArg (fun z : CO => (z.c 0).re) h
  rw [show (gen2StateQuadruple.c 0).re = (-2 : Int) by rfl] at h0
  have hz : ((0 : CO).c 0).re = (0 : Int) := rfl
  rw [hz] at h0
  norm_num at h0

set_option maxHeartbeats 800000

/-- The generation-2 state inherits exact period 4 under left e7 action. -/
theorem gen2State_left_orbit_exact_period_four :
    e7LeftOp * (e7LeftOp * (e7LeftOp * (e7LeftOp * gen2StateQuadruple))) = gen2StateQuadruple /\
    Ne (e7LeftOp * gen2StateQuadruple) gen2StateQuadruple /\
    Ne (e7LeftOp * (e7LeftOp * gen2StateQuadruple)) gen2StateQuadruple := by
  exact universal_Ce_period_four gen2StateQuadruple gen2StateQuadruple_ne_zero

/-- The generation-2 state also has exact period 4 under right e7 action. -/
theorem gen2State_right_orbit_exact_period_four :
    (((gen2StateQuadruple * e7LeftOp) * e7LeftOp) * e7LeftOp) * e7LeftOp = gen2StateQuadruple /\
    Ne (gen2StateQuadruple * e7LeftOp) gen2StateQuadruple /\
    Ne ((gen2StateQuadruple * e7LeftOp) * e7LeftOp) gen2StateQuadruple := by
  exact universal_Ce_right_period_four gen2StateQuadruple gen2StateQuadruple_ne_zero

set_option maxHeartbeats 200000

end CausalGraph
