import Std
import Std.Tactic

namespace CausalGraphV2

/-!
Exact finite formalization for the v2 triplet-decay simulation lane.

This module mirrors the simulation predicates in
`cog_v2/calc/build_triplet_decay_exact_simulation_v1.py` using exact integer
arithmetic only (no floating-point bridge terms):

1) `offMotif` (triplet coherence drop),
2) `vacuumCoupled` (e000 share threshold under active coupling),
3) `daughterChannelsPresent` (support in non-triplet channels),
4) `decayActive` = offMotif AND (vacuumCoupled OR daughterChannelsPresent).

It then locks explicit witness microstates from the JSON artifact and proves the
same predicate outcomes theorem-level.
-/

structure GInt where
  re : Int
  im : Int
deriving DecidableEq, Repr

abbrev CxO := Fin 8 -> GInt

def g (re im : Int) : GInt :=
  GInt.mk re im

def g0 : GInt :=
  g 0 0

def abs2 (z : GInt) : Int :=
  z.re * z.re + z.im * z.im

def mkState
    (a0 a1 a2 a3 a4 a5 a6 a7 : GInt) : CxO :=
  fun i =>
    match i.1 with
    | 0 => a0
    | 1 => a1
    | 2 => a2
    | 3 => a3
    | 4 => a4
    | 5 => a5
    | 6 => a6
    | _ => a7

def sumAbs2 (idxs : List (Fin 8)) (s : CxO) : Int :=
  idxs.foldl (fun acc i => acc + abs2 (s i)) 0

def tripletAbs2 (s : CxO) : Int :=
  sumAbs2 [1, 2, 3] s

def nonE000Abs2 (s : CxO) : Int :=
  sumAbs2 [1, 2, 3, 4, 5, 6, 7] s

def nonTripletAbs2 (s : CxO) : Int :=
  sumAbs2 [4, 5, 6, 7] s

def e000Abs2 (s : CxO) : Int :=
  abs2 (s 0)

def totalAbs2 (s : CxO) : Int :=
  e000Abs2 s + nonE000Abs2 s

/-
Simulation threshold: coherence < 0.45.
Using exact integer arithmetic:
coherence = triplet/nonE000, so coherence < 9/20.
-/
def offMotifB (s : CxO) : Bool :=
  decide (nonE000Abs2 s = 0) || decide (20 * tripletAbs2 s < 9 * nonE000Abs2 s)

def offMotif (s : CxO) : Prop :=
  offMotifB s = true

/-
Simulation threshold: e000_share >= 0.20 under active coupling.
The simulation defines share = 0 when totalAbs2 = 0, so we require totalAbs2 > 0.
-/
def vacuumCoupledB (couplingMultiplicity : Nat) (s : CxO) : Bool :=
  decide (0 < couplingMultiplicity) &&
  decide (totalAbs2 s > 0) &&
  decide (5 * e000Abs2 s >= totalAbs2 s)

def vacuumCoupled (couplingMultiplicity : Nat) (s : CxO) : Prop :=
  vacuumCoupledB couplingMultiplicity s = true

def daughterChannelsPresentB (s : CxO) : Bool :=
  decide (nonTripletAbs2 s > 0)

def daughterChannelsPresent (s : CxO) : Prop :=
  daughterChannelsPresentB s = true

def decayActiveB (couplingMultiplicity : Nat) (s : CxO) : Bool :=
  offMotifB s && (vacuumCoupledB couplingMultiplicity s || daughterChannelsPresentB s)

def decayActive (couplingMultiplicity : Nat) (s : CxO) : Prop :=
  decayActiveB couplingMultiplicity s = true

/-!
Exact witness microstates copied from
`cog_v2/sources/triplet_decay_exact_simulation_v1.json`.

These are direct finite-state points used for theorem-level replay checks.
-/

def stableTripletTick2 : CxO :=
  mkState
    (g 0 0)
    (g 1 0)
    (g 0 1)
    (g 0 (-1))
    g0 g0 g0 g0

def highEnergyTick6 : CxO :=
  mkState
    g0 g0 g0 g0
    (g 0 (-1))
    (g 0 1)
    g0
    g0

def highEnergyTick9 : CxO :=
  mkState
    (g 0 1)
    (g 0 (-1))
    g0
    g0
    (g 1 0)
    (g 1 0)
    g0
    (g 1 0)

def xyProxyTick6 : CxO :=
  mkState
    g0 g0 g0 g0
    (g 1 0)
    (g 1 0)
    (g (-1) 0)
    (g 1 0)

def xyProxyTick9 : CxO :=
  mkState g0 g0 g0 g0 g0 g0 g0 g0

theorem stableTripletTick2_offMotifB_false :
    offMotifB stableTripletTick2 = false := by
  native_decide

theorem stableTripletTick2_decayActiveB0_false :
    decayActiveB 0 stableTripletTick2 = false := by
  native_decide

theorem highEnergyTick6_decayActiveB2_true :
    decayActiveB 2 highEnergyTick6 = true := by
  native_decide

theorem highEnergyTick9_vacuumCoupledB8_true :
    vacuumCoupledB 8 highEnergyTick9 = true := by
  native_decide

theorem highEnergyTick9_decayActiveB8_true :
    decayActiveB 8 highEnergyTick9 = true := by
  native_decide

theorem xyProxyTick6_decayActiveB2_true :
    decayActiveB 2 xyProxyTick6 = true := by
  native_decide

theorem xyProxyTick9_decayActiveB8_false :
    decayActiveB 8 xyProxyTick9 = false := by
  native_decide

/-
Artifact-aligned finite witness contract (v1):

1) stable triplet witness at pre-coupling is not decaying,
2) high-energy perturber witness at first break is decaying,
3) XY proxy witness at first break is decaying,
4) high-energy lane later reaches vacuum-coupled decay,
5) XY proxy all-zero witness is not marked decaying.
-/
theorem tripletDecayExactWitnessContract_v1 :
    (decayActiveB 0 stableTripletTick2 = false) /\
    ((decayActiveB 2 highEnergyTick6 = true) /\
    ((decayActiveB 2 xyProxyTick6 = true) /\
    ((decayActiveB 8 highEnergyTick9 = true) /\
    (decayActiveB 8 xyProxyTick9 = false)))) := by
  native_decide

end CausalGraphV2
