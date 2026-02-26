/-
  CausalGraphTheory/D4D5Contracts.lean

  Draft type signatures for RFC-028 closure items:
    D4: spawn semantics
    D5: projection contract (Pi_obs)

  This module intentionally defines signatures and contract predicates only.
  It does not lock final semantics.
-/

import CausalGraphTheory.KernelV2
import CausalGraphTheory.UpdateRule
import CausalGraphTheory.WeakMixingObservable
import CausalGraphTheory.PhaseClock
import Mathlib.Data.ZMod.Basic

namespace COG.Contracts

open KernelV2

/-! ## Shared microstate container -/

/-- Boundary message delivered to a destination node at the current tick. -/
structure BoundaryMsg where
  srcId    : Nat
  srcDepth : Nat
  srcColor : FanoPoint
  payload  : ComplexOctonion ℤ

/-- Pending edge produced by spawn/update logic. -/
structure SpawnEdge where
  srcId : Nat
  dstId : Nat
  op    : ComplexOctonion ℤ

/-- Full microstate (kernel-facing view) used by D4 and D5 contracts. -/
structure FullMicrostate where
  nodes        : List NodeStateV2
  pendingMsgs  : List (Nat × BoundaryMsg) -- (destination nodeId, message)
  pendingEdges : List SpawnEdge
  nextNodeId   : Nat

/-- Node-ID membership predicate over a full microstate. -/
def nodeExistsById (ms : FullMicrostate) (nid : Nat) : Prop :=
  ∃ n ∈ ms.nodes, n.nodeId = nid

/-! ## D4: spawn semantics signatures -/

/-- Decide whether a destination node should spawn from local data. -/
abbrev ShouldSpawn := NodeStateV2 → List BoundaryMsg → Bool

/-- Initialize a spawned node from parent-local data and a fresh node ID. -/
abbrev SpawnInitState := NodeStateV2 → Nat → NodeStateV2

/-- Produce outgoing edges for a spawned node. -/
abbrev SpawnEdges := NodeStateV2 → Nat → List BoundaryMsg → List SpawnEdge

/-- Apply spawn transition to the full microstate. -/
abbrev ApplySpawn := FullMicrostate → NodeStateV2 → List BoundaryMsg → FullMicrostate

/-- Cone-locality guard: only messages strictly inside parent's past cone. -/
def isConeLocalMsg (parent : NodeStateV2) (m : BoundaryMsg) : Bool :=
  decide (m.srcDepth < parent.topoDepth)

/-- Canonical cone-local slice of boundary messages for a parent node. -/
def coneLocalSlice (parent : NodeStateV2) (msgs : List BoundaryMsg) : List BoundaryMsg :=
  msgs.filter (isConeLocalMsg parent)

/-- Activity guard: a message is active iff it is cone-local and non-identity.
    Aligns with D3 energy-exchange criterion for singleton folds:
    interactionFold [m] != 1 iff m.payload != 1. -/
def isActiveMsg (parent : NodeStateV2) (m : BoundaryMsg) : Bool :=
  isConeLocalMsg parent m && decide (m.payload ≠ (1 : ComplexOctonion ℤ))

/-- Active cone slice: cone-local messages that carry non-identity payload. -/
def activeConeSlice (parent : NodeStateV2) (msgs : List BoundaryMsg) : List BoundaryMsg :=
  msgs.filter (isActiveMsg parent)

/-- Determinism contract for the spawn transition. -/
def SpawnDeterministic (applySpawn : ApplySpawn) : Prop :=
  ∀ ms₁ ms₂ parent₁ parent₂ msgs₁ msgs₂,
    ms₁ = ms₂ →
    parent₁ = parent₂ →
    msgs₁ = msgs₂ →
    applySpawn ms₁ parent₁ msgs₁ = applySpawn ms₂ parent₂ msgs₂

/-- Pure-function/no-exogenous-input contract marker for spawn logic. -/
def SpawnNoExogenous (applySpawn : ApplySpawn) : Prop :=
  SpawnDeterministic applySpawn

/-- Locality law: non-active messages must not affect spawn decision. -/
def SpawnLocalityLaw (shouldSpawn : ShouldSpawn) : Prop :=
  ∀ parent msgs,
    shouldSpawn parent msgs = shouldSpawn parent (activeConeSlice parent msgs)

/- NOTE:
   Positive spawn-trigger obligations are intentionally not stated over
   `ShouldSpawn`, because `ShouldSpawn` does not receive `FullMicrostate` and
   therefore cannot check destination existence.
   The positive trigger requirement is captured in `SpawnThenUpdateLaw`. -/

/-- Initialization contract: spawned node must use the supplied fresh ID. -/
def SpawnNodeIdLaw (spawnInit : SpawnInitState) : Prop :=
  ∀ parent newId, (spawnInit parent newId).nodeId = newId

/-- D4 call precondition: core spawn semantics are defined for non-empty active input.
    Runtime wrappers may defensively no-op on empty input, but this is outside the
    core theorem contract and should be removed once callers are fully disciplined. -/
def SpawnActiveInputPrecondition (parent : NodeStateV2) (msgs : List BoundaryMsg) : Prop :=
  (activeConeSlice parent msgs).isEmpty = false

/-- Locked D4 color policy: spawned nodes initialize on the vacuum axis e7. -/
def SpawnColorLabelLaw (spawnInit : SpawnInitState) : Prop :=
  ∀ parent newId, (spawnInit parent newId).colorLabel = vacuumColorLabel

/-- Completeness contract ("no dead letters"):
    if destination is missing and active cone-local messages exist,
    `applySpawn` must materialize that destination node. -/
def SpawnCompleteness (applySpawn : ApplySpawn) : Prop :=
  ∀ ms parent msgs,
    ¬ nodeExistsById ms ms.nextNodeId →
    (activeConeSlice parent msgs).isEmpty = false →
    nodeExistsById (applySpawn ms parent msgs) ms.nextNodeId

/-- Sequencing contract: when spawn fires for a missing `nextNodeId`, applySpawn
    must materialize that node with first-step tickCount = 1 (spawn then update). -/
def SpawnThenUpdateLaw (shouldSpawn : ShouldSpawn) (applySpawn : ApplySpawn) : Prop :=
  ∀ ms parent msgs,
    ¬ nodeExistsById ms ms.nextNodeId →
    shouldSpawn parent (activeConeSlice parent msgs) = true →
    ∃ n ∈ (applySpawn ms parent msgs).nodes,
      n.nodeId = ms.nextNodeId ∧ n.tickCount = 1

/-! ## D5: projection contract signatures -/

/-- Observable per-node record.
    `u1Sector` is optional in the minimal contract; full-sector dumps are extended mode. -/
structure ObservableNode where
  nodeId    : Nat
  u1Charge  : ℤ
  phase4    : ZMod 4
  topoDepth : Nat
  u1Sector  : Option CausalGraph.KCO

/-- Observer-level state produced by Pi_obs. -/
structure ObservableState where
  nodes : List ObservableNode

/-- Per-node observer map. -/
abbrev PiObsNode := NodeStateV2 → ObservableNode

/-- Global observer map required by RFC-028 D5. -/
abbrev PiObs := FullMicrostate → ObservableState

/-- Canonical node ordering for observer output. -/
def sortNodesById (nodes : List NodeStateV2) : List NodeStateV2 :=
  nodes.mergeSort (fun a b => a.nodeId ≤ b.nodeId)

/-- Minimal node-level observer map using already-locked observables.
    Sector vector is intentionally hidden in minimal mode (`none`). -/
def piObsNodeMinimal (s : NodeStateV2) : ObservableNode :=
  { nodeId    := s.nodeId
    u1Charge  := CausalGraph.u1Charge s.psi
    phase4    := KernelV2.phi4 s
    topoDepth := s.topoDepth
    u1Sector  := none }

/-- Extended observer map variant that includes U(1)-sector vector data. -/
def piObsNodeWithSector (s : NodeStateV2) : ObservableNode :=
  { nodeId    := s.nodeId
    u1Charge  := CausalGraph.u1Charge s.psi
    phase4    := KernelV2.phi4 s
    topoDepth := s.topoDepth
    u1Sector  := some (CausalGraph.piObs s.psi) }

/-- Minimal full-state observer map with canonical node ordering by nodeId. -/
def piObsMinimal (ms : FullMicrostate) : ObservableState :=
  { nodes := (sortNodesById ms.nodes).map piObsNodeMinimal }

/-- Extended full-state observer map: includes U(1)-sector vector for each node.
    Required for proton and multi-quark bound-state analyses where color-charge
    routing through the Fano plane is not captured by u1Charge alone. -/
def piObsWithSector (ms : FullMicrostate) : ObservableState :=
  { nodes := (sortNodesById ms.nodes).map piObsNodeWithSector }

/-- Canonical D5 projection profile (locked): minimal observer map.
    Base claims (hydrogen, phase counting, tick ordering) are proved against this
    to avoid implicit coupling to color-sector data they do not need.
    Proton and quark analyses must declare piObsWithSector explicitly. -/
def piObsCanonical : PiObs := piObsMinimal

/-- Observational equivalence relation induced by a chosen Pi_obs. -/
def ObsEquivalent (piObs : PiObs) (m₁ m₂ : FullMicrostate) : Prop :=
  piObs m₁ = piObs m₂

/-- Non-triviality contract: Pi_obs must be many-to-one (true projection). -/
def PiObsNonTrivial (piObs : PiObs) : Prop :=
  ∃ m₁ m₂, ObsEquivalent piObs m₁ m₂ ∧ m₁ ≠ m₂

/-- Permutation-invariance contract: node list order is not observable. -/
def PiObsPermutationInvariant (piObs : PiObs) : Prop :=
  ∀ m₁ m₂,
    m₁.pendingMsgs = m₂.pendingMsgs →
    m₁.pendingEdges = m₂.pendingEdges →
    m₁.nextNodeId = m₂.nextNodeId →
    m₁.nodes.Perm m₂.nodes →
    piObs m₁ = piObs m₂

/-- Node-ID preservation contract for node-level observables. -/
def PiObsNodeIdLaw (piObsNode : PiObsNode) : Prop :=
  ∀ s, (piObsNode s).nodeId = s.nodeId

/-- Charge-readout contract for node-level observables. -/
def PiObsChargeLaw (piObsNode : PiObsNode) : Prop :=
  ∀ s, (piObsNode s).u1Charge = CausalGraph.u1Charge s.psi

/-- Phase-readout contract for node-level observables. -/
def PiObsPhaseLaw (piObsNode : PiObsNode) : Prop :=
  ∀ s, (piObsNode s).phase4 = KernelV2.phi4 s

end COG.Contracts
