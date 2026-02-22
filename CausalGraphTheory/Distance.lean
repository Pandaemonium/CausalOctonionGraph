/-
  CausalGraphTheory/Distance.lean
  Phase 2.2: Topological Distance

  Defines the shortest path distance in the CausalGraph.
  Since the graph is a strict DAG ordered by ID (source < target),
  we can compute distance using structural recursion on a fuel parameter
  bound by (target - source).

  Claim: claims/dag_distance_triangle.yml
-/

import CausalGraphTheory.State
import Mathlib.Data.Nat.Basic
import Mathlib.Order.Basic
import Mathlib.Data.List.Basic

namespace CausalGraph

/-- 
  Helper: outgoing neighbors of a node `u`. 
  Returns list of `v` such that `u -> v` is an edge.
-/
def neighbors (G : CausalGraph) (u : Nat) : List Nat :=
  G.edges.filterMap (fun e => if e.source = u then some e.target else none)

/--
  Computes shortest path distance with fuel to ensure termination.
  Fuel represents the maximum possible remaining path length (t - s).
-/
def distFuel (fuel : Nat) (G : CausalGraph) (s t : Nat) : Option Nat :=
  match fuel with
  | 0 => none
  | n + 1 =>
    if h : s = t then
      some 0
    else if s > t then
      none
    else
      -- s < t. Neighbors must satisfy v > s.
      let nbrs := neighbors G s
      let options := nbrs.filterMap (fun v => 
        match distFuel n G v t with
        | some d => some (d + 1)
        | none => none
      )
      match options with
      | [] => none
      | (d::ds) => some (ds.foldl min d)

/-- 
  Public distance function using sufficient fuel (t - s + 1).
  If s > t, returns none immediately.
-/
def dist (G : CausalGraph) (s t : Nat) : Option Nat :=
  if s > t then none else distFuel (t - s + 1) G s t

/--
  Triangle inequality for the distance function.
  dist(a, c) <= dist(a, b) + dist(b, c)
-/
theorem dist_triangle (G : CausalGraph) (a b c : Nat) :
  ∀ dab dbc dac,
    dist G a b = some dab →
    dist G b c = some dbc →
    dist G a c = some dac →
    dac ≤ dab + dbc := by
  -- Proof omitted for Phase 2 prototype.
  intros dab dbc dac hab hbc hac
  sorry

end CausalGraph
