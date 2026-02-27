/- 
  CausalGraphTheory/ElectronSelfInteraction.lean

  Formal electron self-interaction contract on top of RFC-028 update rule.

  This file provides:
  1. A single-node "self-loop" interaction (node receives its own electron psi).
  2. A two-electron pair constructor for explicit e-e interaction rounds.
  3. Basic invariants (determinism, tick advance, depth/color stability).
  4. Repulsion/observation facts specialized to the canonical Furey electron motif.
-/

import CausalGraphTheory.TwoNodeSystem
import CausalGraphTheory.UpdateRule
import CausalGraphTheory.FureyChain

namespace CausalGraphTheory.ElectronSelfInteraction

open KernelV2 UpdateRule TwoNodeSystem
open CausalGraph

/-! ## Canonical electron data -/

/-- Canonical electron state used by interaction semantics. -/
abbrev electronPsi : ComplexOctonion ℤ := fureyElectronStateDoubled

/-- Canonical electron color label (Fano index 3 in current lock). -/
def electronColorLabel : FanoPoint := ⟨3, by omega⟩

/-- Build a Kernel v2 node whose psi is the canonical electron motif. -/
def mkElectronNode (nodeId topoDepth tickCount : Nat) : NodeStateV2 :=
  { nodeId := nodeId
    psi := electronPsi
    tickCount := tickCount
    topoDepth := topoDepth
    colorLabel := electronColorLabel }

/-! ## Single-node self-loop interaction -/

/-- Self-loop message list: node receives its own electron psi. -/
def electronSelfMsgs : List (ComplexOctonion ℤ) := [electronPsi]

/-- One deterministic self-interaction step for a single electron node. -/
def electronSelfStep (nodeId topoDepth tickCount : Nat) : NodeStateV2 :=
  nextStateV2 (mkElectronNode nodeId topoDepth tickCount) electronSelfMsgs

/-- Self-loop interaction is classified as an energy exchange event. -/
theorem electron_self_energy_exchange :
    isEnergyExchangeLocked electronSelfMsgs = true := by
  native_decide

/-- Self-loop interaction is also an observation under locked D5 semantics. -/
theorem electron_self_observed :
    interactionObserved electronSelfMsgs = true := by
  simpa [interactionObserved] using electron_self_energy_exchange

/-- RFC-028 deterministic update: self-step matches combine/temporal/fold form exactly. -/
theorem electronSelfStep_psi_formula (nodeId topoDepth tickCount : Nat) :
    (electronSelfStep nodeId topoDepth tickCount).psi =
      combine (temporal_commit (mkElectronNode nodeId topoDepth tickCount))
        (interactionFold electronSelfMsgs) := rfl

/-- Self-step advances tick count by exactly one. -/
theorem electronSelfStep_tick (nodeId topoDepth tickCount : Nat) :
    (electronSelfStep nodeId topoDepth tickCount).tickCount = tickCount + 1 := rfl

/-- Self-step preserves topological depth (no spawn, no depth rewrite in nextStateV2). -/
theorem electronSelfStep_topoDepth (nodeId topoDepth tickCount : Nat) :
    (electronSelfStep nodeId topoDepth tickCount).topoDepth = topoDepth := rfl

/-- Self-step preserves color label (static particle-axis metadata). -/
theorem electronSelfStep_colorLabel (nodeId topoDepth tickCount : Nat) :
    (electronSelfStep nodeId topoDepth tickCount).colorLabel = electronColorLabel := rfl

/-! ## Two-electron interaction specialization -/

/-- Canonical two-electron pair constructor for explicit e-e rounds. -/
def electronElectronPair (id1 id2 depth1 depth2 tick1 tick2 : Nat) : NodePair :=
  { node1 := mkElectronNode id1 depth1 tick1
    node2 := mkElectronNode id2 depth2 tick2 }

/-- Two canonical electron motifs satisfy the repulsive U(1) predicate. -/
theorem electronElectron_repulsive :
    isRepulsiveU1 electronPsi electronPsi = true := by
  simpa [electronPsi] using ee_repulsion_predicate

/-- Any canonical e-e pair is repulsive under the current interaction classifier. -/
theorem electronElectronPair_repulsive
    (id1 id2 depth1 depth2 tick1 tick2 : Nat) :
    isRepulsiveU1
      (electronElectronPair id1 id2 depth1 depth2 tick1 tick2).node1.psi
      (electronElectronPair id1 id2 depth1 depth2 tick1 tick2).node2.psi = true := by
  simpa [electronElectronPair, mkElectronNode, electronPsi] using electronElectron_repulsive

end CausalGraphTheory.ElectronSelfInteraction
