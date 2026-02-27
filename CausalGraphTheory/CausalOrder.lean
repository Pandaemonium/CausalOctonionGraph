/-
  CausalGraphTheory/CausalOrder.lean
  Phase 5.1: Causal Partial Order and Light Cones

  Proves that the edge relation of a CausalGraph induces a strict partial order:
  - Reachability implies the topological ID strictly increases (the key bound).
  - Therefore the causal order is irreflexive, asymmetric, and transitive.

  Also defines one-step forward/backward light cones and causal disconnection.

  Physical meaning: this is the COG's discrete analogue of the causal structure
  of spacetime. The partial order IS the discrete light cone ordering.

  Claim: claims/causal_order.yml
-/

import CausalGraphTheory.State
import Mathlib.Data.Nat.Basic

namespace CausalGraph

-- ============================================================
-- I. Reachability (transitive closure of the edge relation)
-- ============================================================

/--
  Causal reachability: n is reachable from m if there exists a
  directed path m = v₀ → v₁ → ... → vₖ = n in G.

  The `edge` constructor handles one-hop reachability; `trans` builds
  arbitrary-length paths.
-/
inductive reachable (G : CausalGraph) : Nat → Nat → Prop where
  /-- A direct edge m → n witnesses one-step reachability. -/
  | edge  {m n : Nat}
          (he  : ∃ e ∈ G.edges, e.source = m ∧ e.target = n)
          : reachable G m n
  /-- If m reaches k and k reaches n, then m reaches n. -/
  | trans {m k n : Nat}
          (hmk : reachable G m k)
          (hkn : reachable G k n)
          : reachable G m n

-- ============================================================
-- II. The fundamental causal bound
-- ============================================================

/--
  Every direct edge goes strictly forward in topological ID.
  This is the `CausalGraph.acyclic` invariant rephrased for the witness form.
-/
theorem directEdge_lt {G : CausalGraph} {m n : Nat}
    (h : ∃ e ∈ G.edges, e.source = m ∧ e.target = n) : m < n := by
  obtain ⟨e, he, rfl, rfl⟩ := h
  exact G.acyclic e he

/--
  **The Fundamental Causal Bound.**

  If n is reachable from m (by any directed path), then m < n.

  Proof: induction on the path length.
  - One hop: `directEdge_lt`.
  - Composition: transitivity of `<` on `Nat`.

  This single inequality drives all strict partial order axioms below.
-/
theorem reachable_implies_lt {G : CausalGraph} {m n : Nat}
    (h : reachable G m n) : m < n := by
  induction h with
  | edge he          => exact directEdge_lt he
  | trans _ _ hm hk  => exact Nat.lt_trans hm hk

-- ============================================================
-- III. Strict partial order axioms
-- ============================================================

/--
  **Irreflexivity.**
  No node can reach itself: the causal order is acyclic at every scale.
-/
theorem reachable_irrefl {G : CausalGraph} {n : Nat} :
    ¬ reachable G n n :=
  fun h => Nat.lt_irrefl n (reachable_implies_lt h)

/--
  **Asymmetry.**
  If m causally precedes n, then n cannot precede m.
-/
theorem reachable_asymm {G : CausalGraph} {m n : Nat}
    (h : reachable G m n) : ¬ reachable G n m :=
  fun h' => Nat.lt_irrefl m
    (Nat.lt_trans (reachable_implies_lt h) (reachable_implies_lt h'))

/--
  **Transitivity.**
  Causal influence composes: a → b and b → c gives a → c.
-/
theorem reachable_trans {G : CausalGraph} {a b c : Nat}
    (hab : reachable G a b) (hbc : reachable G b c) : reachable G a c :=
  .trans hab hbc

/--
  **Strict separation.**
  Causally related nodes have distinct IDs.
-/
theorem reachable_ne {G : CausalGraph} {m n : Nat}
    (h : reachable G m n) : m ≠ n :=
  Nat.ne_of_lt (reachable_implies_lt h)

-- ============================================================
-- IV. One-step light cones (computable approximation)
-- ============================================================

/--
  The **direct future** of node n: all nodes immediately caused by n.
  (One-hop forward light cone — computable in O(|edges|).)

  For the full transitive closure, iterate this via BFS (Phase 5.2).
-/
def directFuture (G : CausalGraph) (n : Nat) : List Nat :=
  (G.edges.filter (fun e => e.source = n)).map (·.target)

/--
  The **direct past** of node n: all nodes that immediately cause n.
  (One-hop backward light cone — computable in O(|edges|).)
-/
def directPast (G : CausalGraph) (n : Nat) : List Nat :=
  (G.edges.filter (fun e => e.target = n)).map (·.source)

/-- Every direct future node has a strictly larger ID than n. -/
theorem directFuture_gt {G : CausalGraph} {n m : Nat}
    (hm : m ∈ directFuture G n) : n < m := by
  simp only [directFuture, List.mem_map, List.mem_filter] at hm
  obtain ⟨e, ⟨heedge, hnsrc⟩, rfl⟩ := hm
  have hsrc : e.source = n := by rwa [decide_eq_true_eq] at hnsrc
  rw [← hsrc]
  exact G.acyclic e heedge

/-- Every direct past node has a strictly smaller ID than n. -/
theorem directPast_lt {G : CausalGraph} {n m : Nat}
    (hm : m ∈ directPast G n) : m < n := by
  simp only [directPast, List.mem_map, List.mem_filter] at hm
  obtain ⟨e, ⟨heedge, hntgt⟩, rfl⟩ := hm
  have htgt : e.target = n := by rwa [decide_eq_true_eq] at hntgt
  rw [← htgt]
  exact G.acyclic e heedge

-- ============================================================
-- V. Causal separation
-- ============================================================

/--
  Two nodes m and n are **causally disconnected** if neither lies in the
  causal future of the other.  In COG terms: space-like separation.
-/
def causallyDisconnected (G : CausalGraph) (m n : Nat) : Prop :=
  ¬ reachable G m n ∧ ¬ reachable G n m

/-- Causal disconnection is symmetric. -/
theorem causallyDisconnected_symm {G : CausalGraph} {m n : Nat}
    (h : causallyDisconnected G m n) : causallyDisconnected G n m :=
  ⟨h.2, h.1⟩

/-- An edge m → n means m and n are NOT causally disconnected. -/
theorem not_disconnected_of_edge {G : CausalGraph} {m n : Nat}
    (he : ∃ e ∈ G.edges, e.source = m ∧ e.target = n) :
    ¬ causallyDisconnected G m n :=
  fun ⟨h, _⟩ => h (.edge he)

/--
  Any two nodes with a common reachable descendant must have
  comparable or equal IDs (since both precede the descendant).
-/
theorem common_future_lt {G : CausalGraph} {m n k : Nat}
    (hm : reachable G m k) (hn : reachable G n k) (hne : m ≠ n) :
    m < n ∨ n < m :=
  Nat.lt_or_gt_of_ne hne

end CausalGraph
