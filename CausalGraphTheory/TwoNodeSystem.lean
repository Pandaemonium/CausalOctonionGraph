/-
  CausalGraphTheory/TwoNodeSystem.lean

  Two-node interaction semantics (e-e interaction, Phase 5a)
  ==========================================================

  Implements the Codex-recommended staged approach to electron-electron interaction:
    Step 1 (this file): interaction semantics, NOT scattering/kinematics.
    Step 2 (future): distance/geometry for actual scattering trajectories.

  Provides:
    * u1Charge_electron_neg8  -- electron has U(1) charge -8 (doubled units)
    * NodePair                -- two Kernel v2 nodes for pairwise interaction
    * twoNodeRound            -- deterministic one-round update (each node sees other's psi)
    * sameU1ChargeSign        -- both states carry the same sign of U(1) charge
    * isRepulsiveU1           -- energy exchange AND same-sign U(1) charge
    * ee_repulsion_predicate  -- two electron states satisfy isRepulsiveU1
    * twoNodeRound_deterministic -- pure-function guarantee (RFC-028 Invariant 1)

  SCOPE NOTE: isRepulsiveU1 detects interaction kind (repulsive / attractive).
  There is no spatial separation or momentum in the current kernel; those belong
  to a future Distance-based scattering file.
-/

import CausalGraphTheory.KernelV2
import CausalGraphTheory.UpdateRule
import CausalGraphTheory.WeakMixingObservable
import CausalGraphTheory.FureyChain

namespace TwoNodeSystem

open KernelV2 UpdateRule CausalGraph

/-! ## Step 1: Charge observable on the electron state -/

/-- The Furey electron state carries U(1) charge -8 (in doubled units).
    Proof: (toKCO_re fureyElectronStateDoubled) ⟨7, _⟩ = (c_7).re = -8. -/
theorem u1Charge_electron_neg8 :
    u1Charge fureyElectronStateDoubled = -8 := by
  native_decide

/-! ## Two-node system structure -/

/-- A pair of Kernel v2 nodes for modeling pairwise (e-e) interactions.
    RFC-028 D2 Markov: each node receives the other's current psi as its boundary message. -/
structure NodePair where
  node1 : NodeStateV2
  node2 : NodeStateV2

/-! ## Deterministic two-node round update -/

/-- One round of two-node interaction:
    * node1 receives node2.psi as its single boundary message
    * node2 receives node1.psi as its single boundary message
    Both updates are computed from the *same* round-start state (no in-round feedback). -/
def twoNodeRound (sys : NodePair) : NodePair :=
  { node1 := nextStateV2 sys.node1 [sys.node2.psi]
    node2 := nextStateV2 sys.node2 [sys.node1.psi] }

/-- twoNodeRound is a pure function: identical inputs yield identical outputs. -/
theorem twoNodeRound_deterministic (s1 s2 : NodePair) (h : s1 = s2) :
    twoNodeRound s1 = twoNodeRound s2 := by
  subst h; rfl

/-! ## Sign-sensitive interaction predicates -/

/-- Both psi vectors carry the same non-zero sign of U(1) charge.
    Uses Int.sign ∈ {-1, 0, 1}; zero is excluded so vacuum is neutral. -/
def sameU1ChargeSign (psi1 psi2 : ComplexOctonion ℤ) : Bool :=
  let s1 := (u1Charge psi1).sign
  let s2 := (u1Charge psi2).sign
  s1 != 0 && s1 == s2

/-- Repulsive U(1) interaction: energy exchange occurs AND both carriers have the same charge sign.
    isEnergyExchangeLocked detects that a non-identity interaction happened (RFC-028 D3).
    sameU1ChargeSign distinguishes repulsion (same sign) from attraction (opposite sign). -/
def isRepulsiveU1 (psi1 psi2 : ComplexOctonion ℤ) : Bool :=
  isEnergyExchangeLocked [psi2] && sameU1ChargeSign psi1 psi2

/-! ## Electron-electron repulsion theorem -/

/-- Two electron states are classified as repulsive under isRepulsiveU1.
    Proof:
      (a) isEnergyExchangeLocked [fureyElectronStateDoubled] = true
          because interactionFold ≠ 1 (electron ≠ multiplicative identity).
      (b) sameU1ChargeSign: both charges are -8, sign = -1 ≠ 0, same. -/
theorem ee_repulsion_predicate :
    isRepulsiveU1 fureyElectronStateDoubled fureyElectronStateDoubled = true := by
  native_decide

end TwoNodeSystem
