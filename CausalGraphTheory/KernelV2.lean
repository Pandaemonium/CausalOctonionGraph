/-
  CausalGraphTheory/KernelV2.lean

  Kernel v2 Runtime Contract — Gate 1
  ====================================
  Establishes the `ComplexOctonion ℤ` state representation for causal graph
  nodes, per RFC-020_Kernel_Representation_Reconciliation.

  The node state vector lives in `ComplexOctonion ℤ`, represented concretely
  as `Fin 8 → ℤ` — eight integer coordinates, one per octonion basis element
  e₀…e₇.  This is a purely algebraic representation over ℤ:
  no reals, no topology, no analysis.

  Gate 1 requirement (RFC-020): every node stores state in ComplexOctonion ℤ,
  NOT in the legacy 7-bit signed-basis representation.
-/

import Mathlib.Tactic

namespace KernelV2

/-! ## ComplexOctonion type -/

universe u

/-- `ComplexOctonion R` is the type `Fin 8 → R`, representing the
    8-dimensional complex-octonion algebra over a ring `R` as a free module
    with basis {e₀, e₁, …, e₇}.

    For Gate 1 we use `R = ℤ`, giving `ComplexOctonion ℤ` — a tuple of 8
    integers, one coefficient per octonion basis element.
    No reals, no analysis; purely algebraic over ℤ. -/
abbrev ComplexOctonion (R : Type u) : Type u := Fin 8 → R

/-! ## Node state structure -/

/-- A node in the Kernel v2 causal graph.
    • `nodeId`    — globally unique identifier
    • `psi`       — state vector in `ComplexOctonion ℤ` (RFC-020 Gate 1)
    • `tickCount` — discrete ticks elapsed at this node
    • `topoDepth` — topological depth in the causal DAG -/
structure NodeStateV2 where
  nodeId    : Nat
  psi       : ComplexOctonion ℤ
  tickCount : Nat
  topoDepth : Nat

/-! ## Vacuum-orbit predicate -/

/-- `isVacuumOrbit psi` returns `true` iff all 8 integer components of `psi`
    are zero.  This is the RFC-020 Gate 1 vacuum-orbit test. -/
def isVacuumOrbit (psi : ComplexOctonion ℤ) : Bool :=
  psi ⟨0, by omega⟩ == 0 &&
  psi ⟨1, by omega⟩ == 0 &&
  psi ⟨2, by omega⟩ == 0 &&
  psi ⟨3, by omega⟩ == 0 &&
  psi ⟨4, by omega⟩ == 0 &&
  psi ⟨5, by omega⟩ == 0 &&
  psi ⟨6, by omega⟩ == 0 &&
  psi ⟨7, by omega⟩ == 0

/-! ## Vacuum state -/

/-- The vacuum node: all components zero, tick 0, depth 0. -/
def vacuumState (id : Nat) : NodeStateV2 :=
  { nodeId    := id
    psi       := fun _ => 0
    tickCount := 0
    topoDepth := 0 }

/-! ## Deterministic transition -/

/-- Advance the octonion component by the cyclic index shift i ↦ (i+1) mod 8.
    This models a discrete phase rotation in the 8-dimensional integer space. -/
def advanceOctonion (o : ComplexOctonion ℤ) : ComplexOctonion ℤ := fun i =>
  o ⟨(i.val + 1) % 8, Nat.mod_lt _ (by omega)⟩

/-- One-tick transition: advance the octonion component, increment the tick. -/
def nextState (s : NodeStateV2) : NodeStateV2 :=
  { nodeId    := s.nodeId
    psi       := advanceOctonion s.psi
    tickCount := s.tickCount + 1
    topoDepth := s.topoDepth }

/-! ## Gate 1 contract theorem -/

/-- **omega_representable_in_kernel_v2** (KERN-V2-1, RFC-020 Gate 1):
    Every element of `ComplexOctonion ℤ` is representable as the `psi` field
    of some `NodeStateV2`.

    Proof: for any `o : ComplexOctonion ℤ`, the node `⟨0, o, 0, 0⟩`
    has `psi = o` by construction (reflexivity). -/
theorem omega_representable_in_kernel_v2 :
    ∀ (o : ComplexOctonion ℤ), ∃ (s : NodeStateV2), s.psi = o := fun o =>
  ⟨{ nodeId := 0, psi := o, tickCount := 0, topoDepth := 0 }, rfl⟩

/-! ## Supporting lemmas -/

/-- The vacuum state satisfies `isVacuumOrbit`. -/
theorem vacuumState_isVacuumOrbit (id : Nat) :
    isVacuumOrbit (vacuumState id).psi = true := rfl

/-- `nextState` increments the tick by 1. -/
@[simp]
theorem nextState_tickCount (s : NodeStateV2) :
    (nextState s).tickCount = s.tickCount + 1 := rfl

/-- `nextState` preserves the node identity. -/
@[simp]
theorem nextState_nodeId (s : NodeStateV2) :
    (nextState s).nodeId = s.nodeId := rfl

/-- `nextState` preserves topological depth. -/
@[simp]
theorem nextState_topoDepth (s : NodeStateV2) :
    (nextState s).topoDepth = s.topoDepth := rfl

/-- Every `ComplexOctonion ℤ` vector is the `psi` of some node (surjectivity). -/
theorem psi_surjective :
    Function.Surjective (fun s : NodeStateV2 => s.psi) := fun o =>
  ⟨{ nodeId := 0, psi := o, tickCount := 0, topoDepth := 0 }, rfl⟩

end KernelV2