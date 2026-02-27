/-
  CausalGraphTheory/EEScattering.lean

  Electron-Electron Spatial Divergence (Phase 5b)
  ================================================

  Adds a spatial/distance geometry layer on top of Phase 5a (TwoNodeSystem.lean):
    * topoDistance             -- topological distance between two nodes
    * twoNodeRound_node2_depth -- helper: nextStateV2 preserves topoDepth (Markov update)
    * twoNodeRound_increases_depth -- node2's depth is non-decreasing under twoNodeRound
    * ee_divergence            -- repulsive e-e pairs have non-decreasing topoDistance

  Key structural fact: nextStateV2 is defined as { s with psi := ...; tickCount := ... },
  so topoDepth is preserved (unchanged) by every round. The distance |d2 - d1| is
  therefore invariant under twoNodeRound (ge holds as equality).
-/

import CausalGraphTheory.TwoNodeSystem
import CausalGraphTheory.KernelV2

namespace CausalGraphTheory.EEScattering

open TwoNodeSystem KernelV2 UpdateRule

/-! ## Topological distance -/

/-- The topological distance between two nodes in a NodePair,
    defined as the absolute difference of their topoDepth fields.
    Uses Int arithmetic to handle subtraction safely, then takes natAbs. -/
def topoDistance (p : NodePair) : Nat :=
  ((p.node2.topoDepth : Int) - (p.node1.topoDepth : Int)).natAbs

/-! ## Helper lemmas about nextStateV2 and topoDepth -/

/-- nextStateV2 preserves topoDepth: the Markov update only changes psi and tickCount.
    Follows from the struct-update definition: { s with psi := ..., tickCount := ... }
    leaves all other fields (including topoDepth) unchanged. -/
lemma nextStateV2_topoDepth (node : NodeStateV2) (msgs : List (ComplexOctonion Int)) :
    (nextStateV2 node msgs).topoDepth = node.topoDepth := rfl

/-- After twoNodeRound, node2's topoDepth is unchanged.
    twoNodeRound calls nextStateV2 which preserves topoDepth. -/
lemma twoNodeRound_node2_depth (p : NodePair) :
    (twoNodeRound p).node2.topoDepth = p.node2.topoDepth := rfl

/-- After twoNodeRound, node1's topoDepth is unchanged. -/
lemma twoNodeRound_node1_depth (p : NodePair) :
    (twoNodeRound p).node1.topoDepth = p.node1.topoDepth := rfl

/-! ## Main theorems -/

/-- After one round, node2's depth is non-decreasing (preserved exactly).
    The isRepulsiveU1 hypothesis confirms the interaction is repulsive.
    Non-decreasing holds as equality since nextStateV2 preserves topoDepth. -/
theorem twoNodeRound_increases_depth (p : NodePair)
    (h : isRepulsiveU1 p.node1.psi p.node2.psi = true) :
    (twoNodeRound p).node2.topoDepth >= p.node2.topoDepth := by
  rw [twoNodeRound_node2_depth]

/-- The main divergence theorem: repulsive e-e pairs have non-decreasing
    topological distance under one application of twoNodeRound.

    Proof: topoDepth is preserved by nextStateV2 (Markov update modifies
    only psi and tickCount), so both nodes depths are unchanged and the
    distance |d2 - d1| is invariant. The ge bound holds as equality. -/
theorem ee_divergence (p : NodePair)
    (h : isRepulsiveU1 p.node1.psi p.node2.psi = true) :
    topoDistance (twoNodeRound p) >= topoDistance p := by
  simp only [topoDistance, twoNodeRound_node1_depth, twoNodeRound_node2_depth]

end CausalGraphTheory.EEScattering

-- Leibniz