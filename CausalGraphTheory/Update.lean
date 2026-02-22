/-
  CausalGraphTheory/Update.lean
  Phase 2.4: Graph Update Step

  Defines the single-step evolution of the causal graph.
  For the purpose of Phase 2, this implements a structural update
  that adds new nodes and edges respecting the topological ordering (ID growth).

  The detailed physics logic (state calculation via Tick/Batch) is
  encapsulated but the structural invariant (acyclicity) is the focus here.

  Claim: claims/step_preserves_dag.yml
-/

import CausalGraphTheory.State
import CausalGraphTheory.Tick
import Mathlib.Data.List.Basic
import Mathlib.Data.Nat.Basic

namespace CausalGraph

/--
  Identify the next available Node ID.
  Returns max(existing IDs) + 1, or 0 for an empty graph.
-/
def nextNodeId (G : CausalGraph) : Nat :=
  match G.nodes.map (·.id) |>.max? with
  | some m => m + 1
  | none   => 0

-- ============================================================
-- Helper lemmas for the acyclicity proof
-- ============================================================

/-- Every element of a non-empty list is ≤ its `max?` value. -/
private lemma le_max?_val {l : List Nat} {x m : Nat}
    (hmem : x ∈ l) (hmax : l.max? = some m) : x ≤ m :=
  (List.max?_eq_some_iff.mp hmax).2 x hmem

/-- A non-empty list's `max?` is `some m` for some `m`. -/
private lemma max?_ne_nil {l : List Nat} (hne : l ≠ []) : ∃ m, l.max? = some m := by
  cases hmax : l.max? with
  | some m => exact ⟨m, rfl⟩
  | none   => exact absurd (List.max?_eq_none_iff.mp hmax) hne

/-- Any existing node's ID is strictly less than `nextNodeId`. -/
private lemma mem_id_lt_nextNodeId {G : CausalGraph} {n : Node}
    (hmem : n ∈ G.nodes) : n.id < nextNodeId G := by
  unfold nextNodeId
  have hmap : n.id ∈ G.nodes.map (·.id) := List.mem_map_of_mem hmem
  have hne  : G.nodes.map (·.id) ≠ [] :=
    fun h => absurd (h ▸ hmap) List.not_mem_nil
  obtain ⟨m, hm⟩ := max?_ne_nil hne
  simp only [hm]
  exact Nat.lt_succ_of_le (le_max?_val hmap hm)

/-- The last element of a non-empty list is a member of that list. -/
private lemma getLast?_mem {α : Type*} {l : List α} {x : α}
    (h : l.getLast? = some x) : x ∈ l := by
  have hne : l ≠ [] := by intro heq; simp [heq] at h
  have hlast : l.getLast? = some (l.getLast hne) := List.getLast?_eq_some_getLast hne
  rw [hlast] at h
  have hxeq : l.getLast hne = x := Option.some.inj h
  rw [← hxeq]
  exact List.getLast_mem hne

-- ============================================================
-- Graph update step
-- ============================================================

/--
  Single-step evolution of the graph.
  Creates a new node (with the next available ID) and a directed edge
  from the current last node to the new node.

  All three CausalGraph invariants are preserved by construction:
  - `acyclic`:      new edge goes from lastNode.id to nextNodeId, which is strictly larger.
  - `valid_source`: new edge's source is lastNode, which is in G.nodes.
  - `valid_target`: new edge's target is newNode, which is in the updated node list.
-/
def step (G : CausalGraph) : CausalGraph :=
  let nextId := nextNodeId G
  match h : G.nodes.getLast? with
  | some lastNode =>
    let newNode : Node := {
      id        := nextId
      label     := .vacuum
      state     := ⟨fun _ => 0⟩
      tickCount := lastNode.tickCount + 1
    }
    let newEdge : Edge := {
      source   := lastNode.id
      target   := nextId
      label    := .U1
      operator := ⟨fun _ => 0⟩
    }
    { nodes := G.nodes ++ [newNode]
      edges := G.edges ++ [newEdge]
      acyclic := by
        intro e he
        simp only [List.mem_append, List.mem_singleton] at he
        rcases he with hOld | rfl
        · exact G.acyclic e hOld
        · -- newEdge.source = lastNode.id < nextNodeId G = newEdge.target
          exact mem_id_lt_nextNodeId (getLast?_mem h)
      valid_source := by
        intro e he
        simp only [List.mem_append, List.mem_singleton] at he
        rcases he with hOld | rfl
        · -- e ∈ G.edges: its source is already in G.nodes ⊆ G.nodes ++ [newNode]
          obtain ⟨nd, hnd, hid⟩ := G.valid_source e hOld
          exact ⟨nd, List.mem_append.mpr (Or.inl hnd), hid⟩
        · -- e = newEdge: source is lastNode.id, and lastNode ∈ G.nodes
          exact ⟨lastNode, List.mem_append.mpr (Or.inl (getLast?_mem h)), rfl⟩
      valid_target := by
        intro e he
        simp only [List.mem_append, List.mem_singleton] at he
        rcases he with hOld | rfl
        · -- e ∈ G.edges: its target is already in G.nodes ⊆ G.nodes ++ [newNode]
          obtain ⟨nd, hnd, hid⟩ := G.valid_target e hOld
          exact ⟨nd, List.mem_append.mpr (Or.inl hnd), hid⟩
        · -- e = newEdge: target is nextId = newNode.id, and newNode ∈ G.nodes ++ [newNode]
          exact ⟨newNode, List.mem_append.mpr (Or.inr (by simp)), rfl⟩ }
  | none =>
    -- Empty graph: initialize with genesis node
    let genesisNode : Node := {
      id        := 0
      label     := .vacuum
      state     := ⟨fun _ => 0⟩
      tickCount := 0
    }
    { nodes := [genesisNode]
      edges := []
      acyclic      := by simp
      valid_source := by simp
      valid_target := by simp }

end CausalGraph
