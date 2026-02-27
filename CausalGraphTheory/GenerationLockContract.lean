/-
  CausalGraphTheory/GenerationLockContract.lean

  Proof-first generation lock contract.

  This file intentionally does not define a canonical gen3 state representative.
  It provides constructor-level sector contracts and a minimal proved
  uniqueness-class relation (sign gauge) so gen3 can remain a derived target
  until a stronger uniqueness theorem is closed.
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
  Exists fun inner : CO => psi = mkGen2 inner

def InGen3Sector (psi : CO) : Prop :=
  Exists fun inner : CO => psi = mkGen3 inner

theorem mkGen2_in_sector (inner : CO) : InGen2Sector (mkGen2 inner) :=
  Exists.intro inner rfl

theorem mkGen3_in_sector (inner : CO) : InGen3Sector (mkGen3 inner) :=
  Exists.intro inner rfl

theorem gen2_sector_nonempty : Exists fun psi : CO => InGen2Sector psi :=
  Exists.intro (mkGen2 0) (mkGen2_in_sector 0)

theorem gen3_sector_nonempty : Exists fun psi : CO => InGen3Sector psi :=
  Exists.intro (mkGen3 0) (mkGen3_in_sector 0)

/-
  Current muon witness from Spinors.lean is a concrete inhabitant of gen2 sector.
-/
theorem gen2StateQuadruple_in_gen2_sector : InGen2Sector gen2StateQuadruple := by
  refine Exists.intro muonInner ?_
  rfl

abbrev muonMotifQuadruple : CO := gen2StateQuadruple

theorem muonMotif_in_gen2_sector : InGen2Sector muonMotifQuadruple := by
  simpa [muonMotifQuadruple] using gen2StateQuadruple_in_gen2_sector

/-!
## Minimal uniqueness-class contract for gen3 (P2 foundation)

Until the full global-Gaussian-phase uniqueness class is formalized, we lock a
strictly weaker but proved relation: equivalence up to global sign. This is a
deterministic, theorem-backed contract and is enough to prevent accidental
representation churn while stronger phase contracts are developed.
-/

inductive SignGauge : Type where
  | pos
  | neg
  deriving DecidableEq, Repr

def signAct (s : SignGauge) (psi : CO) : CO :=
  match s with
  | .pos => psi
  | .neg => -psi

def Gen3SignEq (psi phi : CO) : Prop :=
  Exists fun s : SignGauge => phi = signAct s psi

private theorem neg_neg_co (x : CO) : -(-x) = x := by
  apply Octonion.ext
  intro i
  exact neg_neg (x.c i)

private theorem neg_mul_octonion {R : Type} [CommRing R] (x y : Octonion R) :
    (-x) * y = -(x * y) := by
  apply Octonion.ext
  intro i
  fin_cases i
  <;> dsimp only [HMul.hMul, Mul.mul, OfNat.ofNat, One.one, Neg.neg]
  <;> norm_num [Fin.ofNat, Fin.mk.injEq]
  <;> simp only [Octonion.fold_mul]
  <;> ring

private theorem mul_neg_octonion {R : Type} [CommRing R] (x y : Octonion R) :
    x * (-y) = -(x * y) := by
  apply Octonion.ext
  intro i
  fin_cases i
  <;> dsimp only [HMul.hMul, Mul.mul, OfNat.ofNat, One.one, Neg.neg]
  <;> norm_num [Fin.ofNat, Fin.mk.injEq]
  <;> simp only [Octonion.fold_mul]
  <;> ring

theorem signAct_pos (psi : CO) : signAct .pos psi = psi :=
  rfl

theorem signAct_neg (psi : CO) : signAct .neg psi = -psi :=
  rfl

theorem Gen3SignEq_refl (psi : CO) : Gen3SignEq psi psi :=
  Exists.intro .pos rfl

theorem Gen3SignEq_symm {psi phi : CO} : Gen3SignEq psi phi -> Gen3SignEq phi psi := by
  intro h
  rcases h with ⟨s, hs⟩
  cases s with
  | pos =>
      refine Exists.intro .pos ?_
      simpa [signAct] using hs.symm
  | neg =>
      refine Exists.intro .neg ?_
      calc
        psi = -(-psi) := by simpa using (neg_neg_co psi).symm
        _ = -phi := by simp [signAct, hs]

theorem Gen3SignEq_trans {a b c : CO} :
    Gen3SignEq a b -> Gen3SignEq b c -> Gen3SignEq a c := by
  intro hab hbc
  rcases hab with ⟨s1, hs1⟩
  rcases hbc with ⟨s2, hs2⟩
  subst b
  subst c
  cases s1 <;> cases s2
  · exact Exists.intro .pos (by simp [signAct])
  · exact Exists.intro .neg (by simp [signAct])
  · exact Exists.intro .neg (by simp [signAct])
  · exact Exists.intro .pos (by simpa [signAct] using (neg_neg_co a))

theorem mkGen3_neg_inner (inner : CO) : mkGen3 (-inner) = -(mkGen3 inner) := by
  have hMulNegInner : ((-inner) * rightVacDoubled) = -(inner * rightVacDoubled) := by
    simpa using (neg_mul_octonion inner rightVacDoubled)
  have hMulNegRight : leftVacConjDoubled * (-(inner * rightVacDoubled)) =
      -(leftVacConjDoubled * (inner * rightVacDoubled)) := by
    simpa using (mul_neg_octonion leftVacConjDoubled (inner * rightVacDoubled))
  calc
    mkGen3 (-inner) = leftVacConjDoubled * ((-inner) * rightVacDoubled) := rfl
    _ = leftVacConjDoubled * (-(inner * rightVacDoubled)) := by simp [hMulNegInner]
    _ = -(leftVacConjDoubled * (inner * rightVacDoubled)) := hMulNegRight
    _ = -(mkGen3 inner) := rfl

theorem InGen3Sector_neg_closed {psi : CO} (h : InGen3Sector psi) : InGen3Sector (-psi) := by
  rcases h with ⟨inner, rfl⟩
  refine Exists.intro (-inner) ?_
  simpa [mkGen3] using (mkGen3_neg_inner inner).symm

theorem InGen3Sector_sign_closed {psi : CO} (h : InGen3Sector psi) (s : SignGauge) :
    InGen3Sector (signAct s psi) := by
  cases s with
  | pos =>
      simpa [signAct] using h
  | neg =>
      simpa [signAct] using (InGen3Sector_neg_closed h)

theorem gen3_sign_equiv_preserves_sector {psi phi : CO}
    (hpsi : InGen3Sector psi) (hEq : Gen3SignEq psi phi) : InGen3Sector phi := by
  rcases hEq with ⟨s, hs⟩
  subst phi
  exact InGen3Sector_sign_closed hpsi s

def gen3SignSetoid : Setoid CO where
  r := Gen3SignEq
  iseqv := ⟨Gen3SignEq_refl, Gen3SignEq_symm, Gen3SignEq_trans⟩

/-!
## Canonical gen3 lock at sign-gauge level (P3 over current P2 relation)

`Gen3SignClass` is the deterministic canonical object for gen3 under the
currently proved equivalence relation (global sign only).

This is intentionally weaker than full Gaussian phase closure, but it gives:
1. a canonical representative object (quotient class),
2. explicit uniqueness criterion (`=` in class iff sign-equivalent in `CO`),
3. sign-action invariance theorem for replay-stable motif identity checks.
-/

abbrev Gen3SignClass : Type := Quotient gen3SignSetoid

def gen3ClassOf (psi : CO) : Gen3SignClass :=
  Quotient.mk'' psi

theorem gen3ClassOf_eq_of_signEq {psi phi : CO} (h : Gen3SignEq psi phi) :
    gen3ClassOf psi = gen3ClassOf phi :=
  by
    simpa [gen3ClassOf] using
      (Quotient.sound h : (Quotient.mk'' psi : Gen3SignClass) = Quotient.mk'' phi)

theorem gen3SignEq_of_class_eq {psi phi : CO} (h : gen3ClassOf psi = gen3ClassOf phi) :
    Gen3SignEq psi phi :=
  by
    exact Quotient.exact (by simpa [gen3ClassOf] using h)

theorem gen3ClassOf_eq_iff {psi phi : CO} :
    gen3ClassOf psi = gen3ClassOf phi ↔ Gen3SignEq psi phi := by
  constructor
  · exact gen3SignEq_of_class_eq
  · exact gen3ClassOf_eq_of_signEq

theorem signAct_involutive (s : SignGauge) (psi : CO) :
    signAct s (signAct s psi) = psi := by
  cases s with
  | pos =>
      simp [signAct]
  | neg =>
      simpa [signAct] using (neg_neg_co psi)

theorem signAct_self_equiv (s : SignGauge) (psi : CO) :
    Gen3SignEq (signAct s psi) psi := by
  refine Exists.intro s ?_
  simpa using (signAct_involutive s psi).symm

def normalizeGen3Sign (psi : CO) : Gen3SignClass :=
  gen3ClassOf psi

theorem normalizeGen3Sign_sign_invariant (psi : CO) (s : SignGauge) :
    normalizeGen3Sign (signAct s psi) = normalizeGen3Sign psi := by
  exact gen3ClassOf_eq_of_signEq (signAct_self_equiv s psi)

theorem normalizeGen3Sign_unique {psi phi : CO} :
    normalizeGen3Sign psi = normalizeGen3Sign phi ↔ Gen3SignEq psi phi := by
  exact gen3ClassOf_eq_iff

theorem normalizeGen3Sign_respects_gen3_sector {psi phi : CO}
    (_hpsi : InGen3Sector psi) (_hphi : InGen3Sector phi)
    (hNorm : normalizeGen3Sign psi = normalizeGen3Sign phi) :
    Gen3SignEq psi phi := by
  exact (normalizeGen3Sign_unique).mp hNorm

/- A concrete, registry-ready gen3 witness (still derived-target at sign gauge). -/
def tauCandidateQuadruple : CO :=
  mkGen3 muonInner

theorem tauCandidate_in_gen3_sector : InGen3Sector tauCandidateQuadruple := by
  exact mkGen3_in_sector muonInner

abbrev tauMotifDerivedQuadruple : CO := tauCandidateQuadruple

theorem tauMotifDerived_in_gen3_sector : InGen3Sector tauMotifDerivedQuadruple := by
  simpa [tauMotifDerivedQuadruple] using tauCandidate_in_gen3_sector

/-
  Governance marker theorem: gen3 is treated as a derived target in this
  contract. Canonical representative lock still requires a future stronger
  uniqueness-class theorem (e.g., full Gaussian phase/gauge closure).
-/
theorem gen3_proof_first_policy (psi : CO) : InGen3Sector psi -> True := by
  intro _
  trivial

end CausalGraph
