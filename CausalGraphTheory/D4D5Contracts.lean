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

/-- Computable node-ID membership test over a full microstate. -/
def nodeExistsByIdB (ms : FullMicrostate) (nid : Nat) : Bool :=
  ms.nodes.any (fun n => n.nodeId == nid)

/-! ## D4: spawn semantics signatures -/

/-- Decide whether a destination node should spawn from local data. -/
abbrev ShouldSpawn := NodeStateV2 → List BoundaryMsg → Bool

/-- Initialize a spawned node from parent-local data and a fresh node ID. -/
abbrev SpawnInitState := NodeStateV2 → Nat → NodeStateV2

/-- Produce outgoing edges for a spawned node. -/
abbrev SpawnEdges := NodeStateV2 → Nat → List BoundaryMsg → List SpawnEdge

/-- Apply spawn transition to the full microstate. -/
abbrev ApplySpawn := FullMicrostate → NodeStateV2 → List BoundaryMsg → FullMicrostate

/-- Canonical boundary ordering: source depth first, source id as tiebreaker. -/
def sortBoundaryMsgs (msgs : List BoundaryMsg) : List BoundaryMsg :=
  msgs.mergeSort (fun a b =>
    if a.srcDepth < b.srcDepth then true
    else if a.srcDepth > b.srcDepth then false
    else a.srcId ≤ b.srcId)

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

/-- Ordered active payloads consumed by the spawn first-tick update. -/
def activePayloadsOrdered (parent : NodeStateV2) (msgs : List BoundaryMsg) :
    List (ComplexOctonion ℤ) :=
  (sortBoundaryMsgs (activeConeSlice parent msgs)).map (fun m => m.payload)

/-- Spawn depth policy: min active source depth + 1; defensive fallback uses parent+1. -/
def spawnTopoDepth (parent : NodeStateV2) (msgs : List BoundaryMsg) : Nat :=
  match (sortBoundaryMsgs (activeConeSlice parent msgs)).head? with
  | some m => m.srcDepth + 1
  | none => parent.topoDepth + 1

/-! ## D4: concrete implementation (Phase 1) -/

/-- Concrete spawn trigger: spawn iff active cone-local input exists. -/
def shouldSpawnImpl : ShouldSpawn := fun parent msgs =>
  !(activeConeSlice parent msgs).isEmpty

/-- Concrete spawn initializer for a fresh node id. -/
def spawnInitImpl : SpawnInitState := fun _parent newId =>
  { nodeId     := newId
    psi        := omega_vac
    tickCount  := 0
    topoDepth  := 0
    colorLabel := vacuumColorLabel }

/-- Concrete spawn transition:
    1) no-op if destination already exists,
    2) no-op on empty active input (temporary defensive wrapper),
    3) else materialize a spawned node and apply one `nextStateV2` tick
       using canonically ordered active payloads. -/
def applySpawnImpl : ApplySpawn := by
  intro ms parent msgs
  if nodeExistsByIdB ms ms.nextNodeId then
    exact ms
  else
    let activeSlice := activeConeSlice parent msgs
    if hActive : activeSlice.isEmpty then
      exact ms
    else
      let active := sortBoundaryMsgs activeSlice
      let spawned0 : NodeStateV2 := spawnInitImpl parent ms.nextNodeId
      let spawned1 : NodeStateV2 := { spawned0 with topoDepth := spawnTopoDepth parent msgs }
      let spawned2 : NodeStateV2 := UpdateRule.nextStateV2 spawned1 (active.map (fun m => m.payload))
      exact
        { ms with
          nodes := spawned2 :: ms.nodes
          nextNodeId := ms.nextNodeId + 1 }

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

/-! ## D4: concrete Phase 2 closure theorems -/

/-- Bridge lemma: computable membership implies propositional membership. -/
theorem nodeExistsById_of_nodeExistsByIdB_true
    {ms : FullMicrostate} {nid : Nat}
    (h : nodeExistsByIdB ms nid = true) :
    nodeExistsById ms nid := by
  unfold nodeExistsByIdB at h
  rw [List.any_eq_true] at h
  rcases h with ⟨n, hnMem, hnEq⟩
  refine ⟨n, hnMem, ?_⟩
  exact beq_iff_eq.mp hnEq

/-- Active-slice filtering is idempotent. -/
theorem activeConeSlice_idem (parent : NodeStateV2) (msgs : List BoundaryMsg) :
    activeConeSlice parent (activeConeSlice parent msgs) = activeConeSlice parent msgs := by
  unfold activeConeSlice
  simp [List.filter_filter, Bool.and_self]

/-- Concrete spawn initializer satisfies node-id law. -/
theorem spawnInitImpl_nodeId_law : SpawnNodeIdLaw spawnInitImpl := by
  intro parent newId
  rfl

/-- Concrete spawn initializer satisfies locked vacuum-color law. -/
theorem spawnInitImpl_color_law : SpawnColorLabelLaw spawnInitImpl := by
  intro parent newId
  rfl

/-- Concrete trigger satisfies locality law over active cone slice. -/
theorem shouldSpawnImpl_locality_law : SpawnLocalityLaw shouldSpawnImpl := by
  intro parent msgs
  unfold shouldSpawnImpl
  rw [activeConeSlice_idem]

/-- Concrete spawn transition is deterministic. -/
theorem applySpawnImpl_deterministic : SpawnDeterministic applySpawnImpl := by
  intro ms₁ ms₂ parent₁ parent₂ msgs₁ msgs₂ hms hparent hmsgs
  subst hms
  subst hparent
  subst hmsgs
  rfl

/-- Concrete spawn transition satisfies no-exogenous-input contract. -/
theorem applySpawnImpl_no_exogenous : SpawnNoExogenous applySpawnImpl := by
  exact applySpawnImpl_deterministic

/-- Concrete spawn transition satisfies "no dead letters" completeness. -/
theorem applySpawnImpl_completeness : SpawnCompleteness applySpawnImpl := by
  intro ms parent msgs hMissing hActive
  have hExistsBFalse : nodeExistsByIdB ms ms.nextNodeId = false := by
    cases hB : nodeExistsByIdB ms ms.nextNodeId with
    | true =>
        exfalso
        apply hMissing
        exact nodeExistsById_of_nodeExistsByIdB_true hB
    | false =>
        simp
  let active := sortBoundaryMsgs (activeConeSlice parent msgs)
  let spawned0 : NodeStateV2 := spawnInitImpl parent ms.nextNodeId
  let spawned1 : NodeStateV2 := { spawned0 with topoDepth := spawnTopoDepth parent msgs }
  let spawned2 : NodeStateV2 := UpdateRule.nextStateV2 spawned1 (active.map (fun m => m.payload))
  have hOut :
      applySpawnImpl ms parent msgs =
        { ms with
          nodes := spawned2 :: ms.nodes
          nextNodeId := ms.nextNodeId + 1 } := by
    unfold applySpawnImpl
    simp [hExistsBFalse, hActive, active, spawned0, spawned1, spawned2]
  rw [hOut]
  unfold nodeExistsById
  refine ⟨spawned2, ?_, ?_⟩
  · simp
  · simp [spawned2, spawned1, spawned0, spawnInitImpl, UpdateRule.nextStateV2]

/-- Concrete spawn transition materializes with first-step tickCount = 1. -/
theorem applySpawnImpl_then_update_tick1 :
    SpawnThenUpdateLaw shouldSpawnImpl applySpawnImpl := by
  intro ms parent msgs hMissing hSpawn
  have hExistsBFalse : nodeExistsByIdB ms ms.nextNodeId = false := by
    cases hB : nodeExistsByIdB ms ms.nextNodeId with
    | true =>
        exfalso
        apply hMissing
        exact nodeExistsById_of_nodeExistsByIdB_true hB
    | false =>
        simp
  have hActiveFalseAA :
      (activeConeSlice parent (activeConeSlice parent msgs)).isEmpty = false := by
    have hNotEmptyAA :
        !(activeConeSlice parent (activeConeSlice parent msgs)).isEmpty = true := by
      simpa [shouldSpawnImpl] using hSpawn
    cases hE : (activeConeSlice parent (activeConeSlice parent msgs)).isEmpty with
    | true =>
        simp [hE] at hNotEmptyAA
    | false =>
        simp
  have hActiveFalse : (activeConeSlice parent msgs).isEmpty = false := by
    simpa [activeConeSlice_idem] using hActiveFalseAA
  unfold applySpawnImpl
  simp [hExistsBFalse, hActiveFalse, spawnInitImpl, UpdateRule.nextStateV2]

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
