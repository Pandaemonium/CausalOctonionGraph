/-
  CausalGraphTheory/WeakMixingObservable.lean

  RFC-026 prerequisite for WEINBERG-001:
  lock electroweak projector definitions before any target-value fitting.

  This file freezes:
    - U(1), weak, and electroweak masks,
    - projector idempotence,
    - support-cardinality facts.

  The resulting raw ratio is a baseline artifact only.
-/

import CausalGraphTheory.WittBasis
import Mathlib.Data.Finset.Basic
import Mathlib.Tactic

namespace CausalGraph

abbrev KCO := Fin 8 -> Int

def idx0 : Fin 8 := Fin.mk 0 (by decide)
def idx1 : Fin 8 := Fin.mk 1 (by decide)
def idx7 : Fin 8 := Fin.mk 7 (by decide)

/-! ## Index helpers -/

/-- Convert Fano index (0..6 for e1..e7) to octonion coordinate index (1..7). -/
def fanoToOctIdx (p : FanoPoint) : Fin 8 :=
  Fin.mk (p.val + 1) (by omega)

/-- Canonical weak pair chosen from the first Witt pair entry. -/
def weakPair0OctIdx : Prod (Fin 8) (Fin 8) :=
  let ab := WittBasis.wittPair 0
  (fanoToOctIdx ab.1, fanoToOctIdx ab.2)

/-! ## Locked masks -/

/-- U(1)-sector mask: scalar and vacuum-axis components {e0, e7}. -/
def u1Mask (i : Fin 8) : Bool :=
  i == idx0 || i == idx7

/-- Weak-sector mask: canonical weak pair plus vacuum axis. -/
def weakMask (i : Fin 8) : Bool :=
  let p := weakPair0OctIdx
  i == p.1 || i == p.2 || i == idx7

/-- Electroweak-sector mask as union of U(1) and weak masks. -/
def electroweakMask (i : Fin 8) : Bool :=
  u1Mask i || weakMask i

/-- Support cardinality of a mask over 8 coordinates. -/
def maskCard (m : Fin 8 -> Bool) : Nat :=
  (Finset.univ.filter (fun i => m i = true)).card

theorem u1Mask_card : maskCard u1Mask = 2 := by
  native_decide

theorem weakMask_card : maskCard weakMask = 3 := by
  native_decide

theorem electroweakMask_card : maskCard electroweakMask = 4 := by
  native_decide

/-! ## Mask structure checks -/

theorem u1Mask_subset_electroweak (i : Fin 8) :
    u1Mask i = true -> electroweakMask i = true := by
  intro hu1
  simp [electroweakMask, hu1]

theorem weakMask_subset_electroweak (i : Fin 8) :
    weakMask i = true -> electroweakMask i = true := by
  intro hweak
  simp [electroweakMask, hweak]

theorem u1Mask_inter_weakMask_card :
    maskCard (fun i => u1Mask i && weakMask i) = 1 := by
  native_decide

/-! ## Projectors -/

def projectMask (m : Fin 8 -> Bool) (x : KCO) : KCO :=
  fun i => if m i then x i else 0

theorem projectMask_idempotent (m : Fin 8 -> Bool) (x : KCO) :
    projectMask m (projectMask m x) = projectMask m x := by
  funext i
  simp only [projectMask]
  split_ifs <;> simp_all

def u1Projector : KCO -> KCO := projectMask u1Mask
def weakProjector : KCO -> KCO := projectMask weakMask
def electroweakProjector : KCO -> KCO := projectMask electroweakMask

theorem u1Projector_idempotent (x : KCO) :
    u1Projector (u1Projector x) = u1Projector x :=
  projectMask_idempotent u1Mask x

theorem weakProjector_idempotent (x : KCO) :
    weakProjector (weakProjector x) = weakProjector x :=
  projectMask_idempotent weakMask x

theorem electroweakProjector_idempotent (x : KCO) :
    electroweakProjector (electroweakProjector x) = electroweakProjector x :=
  projectMask_idempotent electroweakMask x

/-! ## Bridge: ComplexOctonion ℤ → KCO and charge observable -/

/-- Real-part bridge: extract the real-part of each octonionic component as a KCO vector.
    Adapts NodeStateV2.psi (ComplexOctonion ℤ) for use with the mask-based projectors. -/
def toKCO_re (psi : ComplexOctonion ℤ) : KCO :=
  fun i => (psi.c i).re

/-- Minimal observable map Pi_obs: project the real-part bridge onto the U(1) sector {e₀, e₇}.
    This is the minimal physical projection needed to observe charge. -/
def piObs (psi : ComplexOctonion ℤ) : KCO :=
  u1Projector (toKCO_re psi)

/-- Signed U(1) charge observable: real part of the e₇ (vacuum-axis) component.
    Electrons carry -8 in doubled units; positrons carry +8. -/
def u1Charge (psi : ComplexOctonion ℤ) : ℤ :=
  (toKCO_re psi) ⟨7, by omega⟩

/-! ## Baseline raw ratio -/

/-- Raw ratio from locked masks. Baseline only, not a final Weinberg derivation. -/
def sin2ThetaWRaw : Rat :=
  (maskCard u1Mask : Rat) / (maskCard electroweakMask : Rat)

theorem sin2ThetaWRaw_eq_one_half : sin2ThetaWRaw = 1 / 2 := by
  norm_num [sin2ThetaWRaw, u1Mask_card, electroweakMask_card]

def sin2ThetaWZPoleTarget : Rat := 23122 / 100000

theorem sin2ThetaWRaw_above_zpole_target :
    sin2ThetaWZPoleTarget < sin2ThetaWRaw := by
  norm_num [sin2ThetaWZPoleTarget, sin2ThetaWRaw, u1Mask_card, electroweakMask_card]

/-! ## Weighted observable scaffold (RFC-029 step 1) -/

/-- Binary weight mask used to select coordinates for a weighted trace. -/
abbrev BinWeight := Fin 8 -> Bool

/-- Weighted trace of a projector mask using a binary weight mask. -/
def weightedTrace (w : BinWeight) (m : Fin 8 -> Bool) : Nat :=
  maskCard (fun i => w i && m i)

/-- Uniform (all-on) weight mask. -/
def allOnesWeight : BinWeight := fun _ => true

/-- Overlap mask U1 âˆ© Weak. -/
def overlapMask (i : Fin 8) : Bool := u1Mask i && weakMask i

/-- Weight that removes the U1/Weak overlap from the numerator channel. -/
def exclusiveU1Weight : BinWeight := fun i => !(overlapMask i)

structure WeightPolicy where
  wU1 : BinWeight
  wEW : BinWeight

/-- Baseline policy: unweighted traces for both sectors. -/
def policyBaseline : WeightPolicy := {
  wU1 := allOnesWeight
  wEW := allOnesWeight
}

/-- Exclusive-U1 policy: remove U1/Weak overlap in U1 channel only. -/
def policyExclusiveU1 : WeightPolicy := {
  wU1 := exclusiveU1Weight
  wEW := allOnesWeight
}

/-- Observable weak-mixing ratio from a frozen weight policy. -/
def sin2ThetaWObs (p : WeightPolicy) : Rat :=
  (weightedTrace p.wU1 u1Mask : Rat) / (weightedTrace p.wEW electroweakMask : Rat)

theorem weightedTrace_allOnes (m : Fin 8 -> Bool) :
    weightedTrace allOnesWeight m = maskCard m := by
  unfold weightedTrace allOnesWeight
  simp [maskCard]

theorem weightedTrace_overlap_card :
    weightedTrace allOnesWeight overlapMask = 1 := by
  simpa [overlapMask] using u1Mask_inter_weakMask_card

theorem weightedTrace_exclusive_u1_on_u1 :
    weightedTrace exclusiveU1Weight u1Mask = 1 := by
  native_decide

theorem weightedTrace_electroweak_baseline :
    weightedTrace allOnesWeight electroweakMask = 4 := by
  simpa [weightedTrace_allOnes] using electroweakMask_card

theorem sin2ThetaWObs_baseline_eq_one_half :
    sin2ThetaWObs policyBaseline = 1 / 2 := by
  unfold sin2ThetaWObs policyBaseline
  simp [weightedTrace_allOnes, u1Mask_card, electroweakMask_card]
  norm_num

theorem sin2ThetaWObs_exclusive_u1_eq_one_four :
    sin2ThetaWObs policyExclusiveU1 = 1 / 4 := by
  unfold sin2ThetaWObs policyExclusiveU1
  simp [weightedTrace_exclusive_u1_on_u1, weightedTrace_electroweak_baseline]
  norm_num

/-! ## Non-binary weighted policy (Nat-valued weights) -/

/-- Natural-number weight map for weighted trace observables. -/
abbrev NatWeight := Fin 8 -> Nat

/-- Weighted trace with natural-number weights. -/
def weightedTraceNat (w : NatWeight) (m : Fin 8 -> Bool) : Nat :=
  (Finset.univ.filter (fun i => m i = true)).sum (fun i => w i)

/-- Freeze one non-binary weight:
    weak-pair coordinates get weight 2, all others weight 1. -/
def weakBoostWeight : NatWeight := fun i =>
  if i == weakPair0OctIdx.1 || i == weakPair0OctIdx.2 then 2 else 1

structure NatWeightPolicy where
  wU1 : NatWeight
  wEW : NatWeight

/-- Non-binary policy using weakBoostWeight for both numerator and denominator. -/
def policyWeakBoost : NatWeightPolicy := {
  wU1 := weakBoostWeight
  wEW := weakBoostWeight
}

/-- Nat-weighted weak-mixing observable. -/
def sin2ThetaWObsNat (p : NatWeightPolicy) : Rat :=
  (weightedTraceNat p.wU1 u1Mask : Rat) / (weightedTraceNat p.wEW electroweakMask : Rat)

theorem weightedTraceNat_weakBoost_u1 :
    weightedTraceNat weakBoostWeight u1Mask = 2 := by
  native_decide

theorem weightedTraceNat_weakBoost_ew :
    weightedTraceNat weakBoostWeight electroweakMask = 6 := by
  native_decide

theorem sin2ThetaWObsNat_weakBoost_eq_one_third :
    sin2ThetaWObsNat policyWeakBoost = 1 / 3 := by
  unfold sin2ThetaWObsNat policyWeakBoost
  simp [weightedTraceNat_weakBoost_u1, weightedTraceNat_weakBoost_ew]
  norm_num

end CausalGraph
