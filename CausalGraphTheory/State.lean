/-
  CausalGraphTheory/State.lean
  Phase 2.1: Graph State Definitions

  Defines the core data structures for the causal graph:
  - NodeLabel: Physical representation (Vector, Spinor, Vacuum)
  - EdgeLabel: Gauge interaction (U(1), SU(2), SU(3))
  - Node: A point in the causal history with state Ψ ∈ ℂ⊗𝕆
  - Edge: A causal link carrying an operator O ∈ ℂ⊗𝕆
  - CausalGraph: The aggregate DAG structure

  Convention source of truth: rfc/RFC-001 §2
  Claim: claims/step_preserves_dag.yml (depends on this structure)
-/

import CausalGraphTheory.ComplexOctonion
import Mathlib.Data.Fin.Basic
import Mathlib.Data.Nat.Basic

/--
  Node classification based on the representation of the complex octonion algebra.
  - V: Vector representation
  - S_plus: Positive spinor (left-handed fermion)
  - S_minus: Negative spinor (right-handed fermion)
  - vacuum: The sterile vacuum state v
-/
inductive NodeLabel where
  | V       : NodeLabel
  | S_plus  : NodeLabel
  | S_minus : NodeLabel
  | vacuum  : NodeLabel
  deriving Repr, DecidableEq

/--
  Edge classification based on the gauge group generator it carries.
  - U1: U(1) generator (photon-like)
  - SU2: SU(2) generator (W/Z-like), indexed by Fin 3
  - SU3: SU(3) generator (gluon-like), indexed by Fin 8
-/
inductive EdgeLabel where
  | U1    : EdgeLabel
  | SU2   : Fin 3 → EdgeLabel
  | SU3   : Fin 8 → EdgeLabel
  deriving Repr, DecidableEq

/--
  A node in the causal graph.
  Represents a discrete moment in the history of a particle/field.
  
  - id: Unique identifier (and topological index)
  - label: The type of representation
  - state: The internal state vector Ψ ∈ ℂ⊗𝕆 (integer coefficients)
  - tickCount: Local time counter (number of Tick steps experienced)
-/
structure Node where
  id        : Nat
  label     : NodeLabel
  state     : ComplexOctonion ℤ
  tickCount : Nat

/--
  A directed edge in the causal graph.
  Represents a causal influence or interaction.
  
  - source: ID of the originating node
  - target: ID of the destination node
  - label: The type of interaction
  - operator: The algebraic operator O ∈ ℂ⊗𝕆 carried by the link
-/
structure Edge where
  source   : Nat
  target   : Nat
  label    : EdgeLabel
  operator : ComplexOctonion ℤ

/--
  The Causal Graph: a Directed Acyclic Graph (DAG) of Nodes and Edges.
  
  Invariants:
  1. Acyclicity: Enforced by requiring source < target for all edges.
     This implies that `id` serves as a strict topological index.
  2. Validity: Edges must connect nodes that actually exist in the graph.
-/
structure CausalGraph where
  nodes : List Node
  edges : List Edge
  /-- Topological ordering enforcement: edges always point forward in ID. -/
  acyclic : ∀ e ∈ edges, e.source < e.target
  /-- Edges connect existing nodes. -/
  valid_source : ∀ e ∈ edges, ∃ n ∈ nodes, n.id = e.source
  valid_target : ∀ e ∈ edges, ∃ n ∈ nodes, n.id = e.target

namespace CausalGraph

/-- Helper to find a node by ID. -/
def findNode (G : CausalGraph) (id : Nat) : Option Node :=
  G.nodes.find? (fun n => n.id = id)

/-- The graph size (number of nodes). -/
def size (G : CausalGraph) : Nat := G.nodes.length

end CausalGraph
