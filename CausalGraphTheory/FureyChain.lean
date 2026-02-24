/-
  CausalGraphTheory/FureyChain.lean

  Stepwise Furey-state construction identities.

  This file isolates symbolic chain proofs from Spinors.lean:
  - primal chain  α1† · (α2† · (α3† · ω))
  - dual chain    α1  · (α2  · (α3  · ω†))

  It also adds scalar-bridge statements for the closed forms.
-/

import CausalGraphTheory.Spinors

namespace CausalGraph

abbrev alpha1DagDoubled : CO := WittBasis.wittRaiseDoubled (R := Int) 0
abbrev alpha2DagDoubled : CO := WittBasis.wittRaiseDoubled (R := Int) 1
abbrev alpha3DagDoubled : CO := WittBasis.wittRaiseDoubled (R := Int) 2

abbrev alpha1Doubled : CO := WittBasis.wittLowerDoubled (R := Int) 0
abbrev alpha2Doubled : CO := WittBasis.wittLowerDoubled (R := Int) 1
abbrev alpha3Doubled : CO := WittBasis.wittLowerDoubled (R := Int) 2

/-- First primal-chain intermediate: (2α₃†)·(2ω). -/
def fureyStep1Expected : CO :=
  Octonion.mk (fun k =>
    if k == 3 then FormalComplex.mk (-2) 0
    else if k == 4 then FormalComplex.mk 0 2
    else 0)

/-- Second primal-chain intermediate: (2α₂†)·((2α₃†)·(2ω)). -/
def fureyStep2Expected : CO :=
  Octonion.mk (fun k =>
    if k == 1 then FormalComplex.mk 4 0
    else if k == 6 then FormalComplex.mk 0 (-4)
    else 0)

/-- First dual-chain intermediate: (2α₃)·(2ω†). -/
def fureyDualStep1Expected : CO :=
  Octonion.mk (fun k =>
    if k == 3 then FormalComplex.mk 2 0
    else if k == 4 then FormalComplex.mk 0 2
    else 0)

/-- Second dual-chain intermediate: (2α₂)·((2α₃)·(2ω†)). -/
def fureyDualStep2Expected : CO :=
  Octonion.mk (fun k =>
    if k == 1 then FormalComplex.mk 4 0
    else if k == 6 then FormalComplex.mk 0 4
    else 0)

/-- Multiply each coefficient by central complex i. -/
def mulI_CO (x : CO) : CO :=
  Octonion.mk (fun k => FormalComplex.I * x.c k)

/-- Integer scaling of each complex-octonion coefficient. -/
def scaleInt_CO (n : Int) (x : CO) : CO :=
  Octonion.mk (fun k =>
    FormalComplex.mk (n * (x.c k).re) (n * (x.c k).im))

set_option maxHeartbeats 800000

/-- Step 1 of primal chain: (2α₃†)·(2ω). -/
theorem alpha3Dag_mul_omega_step :
    alpha3DagDoubled * omegaDoubled = fureyStep1Expected := by
  apply Octonion.ext
  intro i
  fin_cases i
  <;> apply FormalComplex.ext
  <;> simp only [HMul.hMul, Mul.mul, OfNat.ofNat,
                  alpha3DagDoubled, omegaDoubled, WittBasis.vacuumDoubled,
                  WittBasis.wittRaiseDoubled, WittBasis.wittPair,
                  fureyStep1Expected,
                  FormalComplex.add_re, FormalComplex.add_im,
                  FormalComplex.sub_re, FormalComplex.sub_im]
  <;> norm_num [Fin.ofNat, Fin.mk.injEq]

/-- Step 2 of primal chain: (2α₂†)·((2α₃†)·(2ω)). -/
theorem alpha2Dag_mul_step1 :
    alpha2DagDoubled * fureyStep1Expected = fureyStep2Expected := by
  apply Octonion.ext
  intro i
  fin_cases i
  <;> apply FormalComplex.ext
  <;> simp only [HMul.hMul, Mul.mul, OfNat.ofNat,
                  alpha2DagDoubled, fureyStep1Expected, fureyStep2Expected,
                  WittBasis.wittRaiseDoubled, WittBasis.wittPair,
                  FormalComplex.add_re, FormalComplex.add_im,
                  FormalComplex.sub_re, FormalComplex.sub_im]
  <;> norm_num [Fin.ofNat, Fin.mk.injEq]

/-- Step 3 of primal chain: (2α₁†)·(step2). -/
theorem alpha1Dag_mul_step2 :
    alpha1DagDoubled * fureyStep2Expected = negEightIOmegaDagDoubled := by
  apply Octonion.ext
  intro i
  fin_cases i
  <;> apply FormalComplex.ext
  <;> simp only [HMul.hMul, Mul.mul, OfNat.ofNat,
                  alpha1DagDoubled, fureyStep2Expected, negEightIOmegaDagDoubled,
                  WittBasis.wittRaiseDoubled, WittBasis.wittPair,
                  FormalComplex.add_re, FormalComplex.add_im,
                  FormalComplex.sub_re, FormalComplex.sub_im]
  <;> norm_num [Fin.ofNat, Fin.mk.injEq]

/-- Primal chain assembled: α₁†·(α₂†·(α₃†·ω)) = -8i·(2ω†), at doubled scale. -/
theorem fureyElectronStateDoubled_chain :
    fureyElectronStateDoubled = negEightIOmegaDagDoubled := by
  calc
    fureyElectronStateDoubled
        = alpha1DagDoubled * (alpha2DagDoubled * (alpha3DagDoubled * omegaDoubled)) := by rfl
    _ = alpha1DagDoubled * (alpha2DagDoubled * fureyStep1Expected) := by
          rw [alpha3Dag_mul_omega_step]
    _ = alpha1DagDoubled * fureyStep2Expected := by
          rw [alpha2Dag_mul_step1]
    _ = negEightIOmegaDagDoubled := by
          rw [alpha1Dag_mul_step2]

/-- Step 1 of dual chain: (2α₃)·(2ω†). -/
theorem alpha3_mul_omegaDag_step :
    alpha3Doubled * leftVacConjDoubled = fureyDualStep1Expected := by
  apply Octonion.ext
  intro i
  fin_cases i
  <;> apply FormalComplex.ext
  <;> simp only [HMul.hMul, Mul.mul, OfNat.ofNat,
                  alpha3Doubled, leftVacConjDoubled,
                  WittBasis.wittLowerDoubled, WittBasis.wittPair,
                  fureyDualStep1Expected,
                  FormalComplex.add_re, FormalComplex.add_im,
                  FormalComplex.sub_re, FormalComplex.sub_im]
  <;> norm_num [Fin.ofNat, Fin.mk.injEq]

/-- Step 2 of dual chain: (2α₂)·((2α₃)·(2ω†)). -/
theorem alpha2_mul_dual_step1 :
    alpha2Doubled * fureyDualStep1Expected = fureyDualStep2Expected := by
  apply Octonion.ext
  intro i
  fin_cases i
  <;> apply FormalComplex.ext
  <;> simp only [HMul.hMul, Mul.mul, OfNat.ofNat,
                  alpha2Doubled, fureyDualStep1Expected, fureyDualStep2Expected,
                  WittBasis.wittLowerDoubled, WittBasis.wittPair,
                  FormalComplex.add_re, FormalComplex.add_im,
                  FormalComplex.sub_re, FormalComplex.sub_im]
  <;> norm_num [Fin.ofNat, Fin.mk.injEq]

/-- Step 3 of dual chain: (2α₁)·(dual step2). -/
theorem alpha1_mul_dual_step2 :
    alpha1Doubled * fureyDualStep2Expected = negEightIOmegaDoubled := by
  apply Octonion.ext
  intro i
  fin_cases i
  <;> apply FormalComplex.ext
  <;> simp only [HMul.hMul, Mul.mul, OfNat.ofNat,
                  alpha1Doubled, fureyDualStep2Expected, negEightIOmegaDoubled,
                  WittBasis.wittLowerDoubled, WittBasis.wittPair,
                  FormalComplex.add_re, FormalComplex.add_im,
                  FormalComplex.sub_re, FormalComplex.sub_im]
  <;> norm_num [Fin.ofNat, Fin.mk.injEq]

/-- Dual chain assembled: α₁·(α₂·(α₃·ω†)) = -8i·(2ω), at doubled scale. -/
theorem fureyDualElectronStateDoubled_chain :
    fureyDualElectronStateDoubled = negEightIOmegaDoubled := by
  calc
    fureyDualElectronStateDoubled
        = alpha1Doubled * (alpha2Doubled * (alpha3Doubled * leftVacConjDoubled)) := by rfl
    _ = alpha1Doubled * (alpha2Doubled * fureyDualStep1Expected) := by
          rw [alpha3_mul_omegaDag_step]
    _ = alpha1Doubled * fureyDualStep2Expected := by
          rw [alpha2_mul_dual_step1]
    _ = negEightIOmegaDoubled := by
          rw [alpha1_mul_dual_step2]

/-- Nontrivial bridge: -8i·(2ω†) as explicit scalar action. -/
theorem negEightIOmegaDagDoubled_scalar_bridge :
    negEightIOmegaDagDoubled = scaleInt_CO (-8) (mulI_CO leftVacConjDoubled) := by
  apply Octonion.ext
  intro i
  fin_cases i
  <;> apply FormalComplex.ext
  <;> native_decide

/-- Nontrivial bridge: -8i·(2ω) as explicit scalar action. -/
theorem negEightIOmegaDoubled_scalar_bridge :
    negEightIOmegaDoubled = scaleInt_CO (-8) (mulI_CO omegaDoubled) := by
  apply Octonion.ext
  intro i
  fin_cases i
  <;> apply FormalComplex.ext
  <;> native_decide

set_option maxHeartbeats 200000

end CausalGraph

