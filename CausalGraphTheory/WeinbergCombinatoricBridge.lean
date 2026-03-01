import CausalGraphTheory.WeakMixingObservable
import Mathlib.Tactic

/-!
  CausalGraphTheory/WeinbergCombinatoricBridge.lean

  Exact combinatoric constants for the v2 WEINBERG bridge lane:
    1) UV anchor from exclusive-U(1) / electroweak mask card ratio.
    2) Leakage coefficient from basis-card ratio (e000 sink / non-e000 channels).

  This file does not claim IR value closure by itself; it formalizes the
  exact finite-cardinality constants used in the bridge formula.
-/

namespace CausalGraph

/-- Number of non-e000 basis channels in the 8-channel CxO basis. -/
def nonE000Card : Nat := 7

/-- Number of e000 sink channels. -/
def e000SinkCard : Nat := 1

/-- Overlap mask cardinality from locked U(1) and weak masks. -/
def u1WeakOverlapCard : Nat := maskCard (fun i => u1Mask i && weakMask i)

theorem u1WeakOverlapCard_eq_one : u1WeakOverlapCard = 1 := by
  simpa [u1WeakOverlapCard] using u1Mask_inter_weakMask_card

/-- Exclusive-U(1) cardinality used for the UV anchor. -/
def exclusiveU1Card : Nat := maskCard u1Mask - u1WeakOverlapCard

theorem exclusiveU1Card_eq_one : exclusiveU1Card = 1 := by
  rw [exclusiveU1Card, u1Mask_card, u1WeakOverlapCard_eq_one]

/-- UV anchor constant used by the combinatoric bridge lane. -/
def uvAnchorCombinatoric : Rat :=
  (exclusiveU1Card : Rat) / (maskCard electroweakMask : Rat)

theorem uvAnchorCombinatoric_eq_one_four : uvAnchorCombinatoric = 1 / 4 := by
  unfold uvAnchorCombinatoric
  rw [exclusiveU1Card_eq_one, electroweakMask_card]
  norm_num

/-- Leakage coefficient from basis-card combinatorics. -/
def leakageCoeffCombinatoric : Rat :=
  (e000SinkCard : Rat) / (nonE000Card : Rat)

theorem leakageCoeffCombinatoric_eq_one_seven : leakageCoeffCombinatoric = 1 / 7 := by
  unfold leakageCoeffCombinatoric e000SinkCard nonE000Card
  norm_num

/-- Frozen bridge form for sin²θ_W with a rational e000-share input. -/
def sin2ThetaWBridgeCombinatoric (e000Share : Rat) : Rat :=
  uvAnchorCombinatoric - leakageCoeffCombinatoric * e000Share

theorem sin2ThetaWBridgeCombinatoric_zero_share :
    sin2ThetaWBridgeCombinatoric 0 = 1 / 4 := by
  unfold sin2ThetaWBridgeCombinatoric
  rw [uvAnchorCombinatoric_eq_one_four, leakageCoeffCombinatoric_eq_one_seven]
  norm_num

theorem sin2ThetaWBridgeCombinatoric_unit_share :
    sin2ThetaWBridgeCombinatoric 1 = 3 / 28 := by
  unfold sin2ThetaWBridgeCombinatoric
  rw [uvAnchorCombinatoric_eq_one_four, leakageCoeffCombinatoric_eq_one_seven]
  norm_num

theorem sin2ThetaWBridgeCombinatoric_antitone
    {a b : Rat} (h : a ≤ b) :
    sin2ThetaWBridgeCombinatoric b ≤ sin2ThetaWBridgeCombinatoric a := by
  unfold sin2ThetaWBridgeCombinatoric
  have hcoeff : (0 : Rat) ≤ leakageCoeffCombinatoric := by
    rw [leakageCoeffCombinatoric_eq_one_seven]
    norm_num
  have hmul : leakageCoeffCombinatoric * a ≤ leakageCoeffCombinatoric * b :=
    mul_le_mul_of_nonneg_left h hcoeff
  have hneg : -(leakageCoeffCombinatoric * b) ≤ -(leakageCoeffCombinatoric * a) :=
    neg_le_neg hmul
  have hsub :
      (-(leakageCoeffCombinatoric * b)) + uvAnchorCombinatoric
        ≤ (-(leakageCoeffCombinatoric * a)) + uvAnchorCombinatoric :=
    add_le_add_left hneg uvAnchorCombinatoric
  simpa [sub_eq_add_neg, add_comm, add_left_comm, add_assoc] using hsub

end CausalGraph
