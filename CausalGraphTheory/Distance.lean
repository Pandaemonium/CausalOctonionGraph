/-
  CausalGraphTheory/Distance.lean
  Phase 2.2 (revised): Topological Distance via Path Reachability

  Reformulation of the causal-graph distance using an explicit
  Bool-valued n-step reachability predicate.  The main advantage over
  the previous fuel-based BFS approach is that reasoning about paths
  (concatenation, bounding) is carried by the inductive structure of
  `reachableIn` rather than by opaque fuel accounting.

  Definitions
  -----------
  * `reachableIn G s t n`  — Bool: is there a directed path of exactly
    n hops from node-id s to node-id t in G?
  * `dist G s t`           — Option Nat: the length of the shortest
    directed path from s to t, or `none` if none exists (or s > t).

  Key lemmas (all proved, no sorry)
  ----------------------------------
  * reachableIn_bound    : reachableIn G s t d = true → s ≤ t ∧ d ≤ t - s
  * reachableIn_concat   : n-step reach a→b and m-step reach b→c
                           give (n+m)-step reach a→c.
  * dist_implies_reachable: dist G s t = some d → reachableIn G s t d
  * reachable_implies_dist_le: reachable in d steps → dist ≤ d
  * dist_triangle        : dist(a,c) ≤ dist(a,b) + dist(b,c) (no sorry)

  Claim: claims/dag_distance_triangle.yml
-/

import CausalGraphTheory.State
import Mathlib.Data.Nat.Basic
import Mathlib.Data.List.Basic

namespace CausalGraph

-- ============================================================
-- I. Outgoing neighbours (kept for readability / future use)
-- ============================================================

/-- Outgoing neighbours of node `u`. -/
def neighbors (G : CausalGraph) (u : Nat) : List Nat :=
  G.edges.filterMap (fun e => if e.source = u then some e.target else none)

-- ============================================================
-- II. Bool-valued n-step reachability
-- ============================================================

/--
  `reachableIn G s t n` is `true` iff there is a directed path of
  exactly `n` edges from node-id `s` to node-id `t` in G.

  * 0 hops: only if `s = t`.
  * n+1 hops: there exists an edge s → v and a path of n hops v → t.
-/
def reachableIn (G : CausalGraph) : Nat → Nat → Nat → Bool
  | s, t, 0     => s == t
  | s, t, n + 1 => G.edges.any (fun e => e.source == s && reachableIn G e.target t n)

-- ============================================================
-- III. Shortest-path distance
-- ============================================================

/--
  The distance from `s` to `t` is the minimum number of hops, computed
  by finding the first (smallest) `n ∈ {0, 1, …, t−s}` for which
  `reachableIn G s t n = true`.

  Returns `none` if `s > t` (impossible in a DAG ordered by ID) or if
  no path exists within the bound.
-/
def dist (G : CausalGraph) (s t : Nat) : Option Nat :=
  if s > t then none
  else (List.range (t - s + 1)).find? (fun n => reachableIn G s t n)

-- ============================================================
-- IV. Key helper lemmas
-- ============================================================

/--
  **DAG path bound**: If `reachableIn G s t d = true` then `s ≤ t` and
  `d ≤ t - s`.

  The bound uses `G.acyclic` (every edge has `source < target`), which
  guarantees that each hop strictly increases the current node ID.
  Therefore any path of `d` hops from `s` increases the ID by at least
  `d`, giving `t ≥ s + d`, i.e., `d ≤ t - s`.
-/
private lemma reachableIn_bound {G : CausalGraph} {s t d : Nat}
    (h : reachableIn G s t d = true) : s ≤ t ∧ d ≤ t - s := by
  induction d generalizing s with
  | zero =>
    simp [reachableIn] at h
    subst h
    exact ⟨Nat.le_refl _, Nat.sub_self _ ▸ Nat.le_refl _⟩
  | succ n ih =>
    simp only [reachableIn, List.any_eq_true, Bool.and_eq_true, beq_iff_eq] at h
    obtain ⟨e, he_mem, he_src, he_reach⟩ := h
    obtain ⟨hv_le, hn_le⟩ := ih he_reach
    have hv_gt : s < e.target := he_src ▸ G.acyclic e he_mem
    constructor
    · exact Nat.le_of_lt (Nat.lt_of_lt_of_le hv_gt hv_le)
    · have hv_ge : e.target ≥ s + 1 := hv_gt
      omega

/--
  **Path concatenation auxiliary**: for fixed `G, b, c, m`, if
  there is an `m`-hop path b→c, then for any `n` and any `a`,
  an `n`-hop path a→b gives an `(n+m)`-hop path a→c.

  This is stated as a standalone lemma so that the induction hypothesis
  quantifies over `a` and the path hypothesis, without any extraneous
  fixed hypothesis that would corrupt the IH shape.
-/
private lemma reachableIn_concat_aux (G : CausalGraph) (b c m : Nat)
    (h2 : reachableIn G b c m = true) :
    ∀ (n a : Nat), reachableIn G a b n = true → reachableIn G a c (n + m) = true := by
  intro n
  induction n with
  | zero =>
    intro a h1
    simp [reachableIn] at h1
    subst h1
    simpa using h2
  | succ k ih =>
    intro a h1
    simp only [reachableIn, List.any_eq_true, Bool.and_eq_true, beq_iff_eq] at h1
    obtain ⟨e, he_mem, he_src, he_reach⟩ := h1
    rw [show k + 1 + m = k + m + 1 from by omega]
    simp only [reachableIn, List.any_eq_true, Bool.and_eq_true, beq_iff_eq]
    exact ⟨e, he_mem, he_src, ih e.target he_reach⟩

/--
  **Path concatenation**: An `n`-hop path from `a` to `b` and an
  `m`-hop path from `b` to `c` compose into an `(n + m)`-hop path from
  `a` to `c`.
-/
lemma reachableIn_concat {G : CausalGraph} {a b c n m : Nat}
    (h1 : reachableIn G a b n = true)
    (h2 : reachableIn G b c m = true) :
    reachableIn G a c (n + m) = true :=
  reachableIn_concat_aux G b c m h2 n a h1

/--
  **`List.find?` gives minimum**: if `(List.range n).find? p = some d'`
  and `p d = true` and `d < n`, then `d' ≤ d`.

  Proved by the fact that `find?` returns the *first* matching element,
  and `List.range n = [0,1,…,n−1]` is in increasing order.  By
  contradiction: if `d < d'`, the prefix `List.range d'` (which
  contains `d`) has no match (otherwise `find?` on the full list would
  return something < `d'`), but `p d = true` says it does.
-/
private lemma find?_range_le {n d d' : Nat} {p : Nat → Bool}
    (_hd : d < n) (hp : p d = true)
    (hfind : (List.range n).find? p = some d') :
    d' ≤ d := by
  -- By contradiction: assume d' > d
  by_contra h
  push_neg at h  -- h : d < d'
  -- d' is in List.range n, so d' < n
  have hd'n : d' < n := List.mem_range.mp (List.mem_of_find?_eq_some hfind)
  -- Decompose List.range n = List.range d' ++ List.drop d' (List.range n)
  have htake : List.take d' (List.range n) = List.range d' := by
    rw [List.take_range, Nat.min_eq_left (Nat.le_of_lt hd'n)]
  have happ : List.range n = List.range d' ++ List.drop d' (List.range n) := by
    rw [← htake]; exact (List.take_append_drop d' (List.range n)).symm
  -- Show the prefix List.range d' has no match under p
  have hprefix : (List.range d').find? p = none := by
    rcases h_pre : (List.range d').find? p with _ | k
    · rfl
    · -- k is in List.range d', so k < d'
      have hkd' : k < d' := List.mem_range.mp (List.mem_of_find?_eq_some h_pre)
      -- If the prefix has a match k, then the full list also returns some k
      have hfull_k : (List.range n).find? p = some k := by
        rw [happ, List.find?_append, h_pre]; rfl
      -- But hfind says the result is some d', so k = d', contradicting k < d'
      rw [hfull_k] at hfind
      exact absurd (Option.some.inj hfind) (by omega)
  -- Now: d ∈ List.range d' (since d < d'), so p d = false
  have hd_in : d ∈ List.range d' := List.mem_range.mpr h
  exact (List.find?_eq_none.mp hprefix d hd_in) hp

-- ============================================================
-- V. Bridging dist and reachableIn
-- ============================================================

/--
  If `dist G s t = some d`, then `reachableIn G s t d = true`.
  (The BFS found a real path of that length.)
-/
lemma dist_implies_reachable {G : CausalGraph} {s t d : Nat}
    (h : dist G s t = some d) : reachableIn G s t d = true := by
  by_cases hgt : s > t
  · -- s > t: dist returns none, contradicting h
    unfold dist at h
    rw [if_pos hgt] at h
    exact absurd h (by simp)
  · -- s ≤ t: dist returns find? result
    unfold dist at h
    rw [if_neg hgt] at h
    exact List.find?_some h

/--
  If `reachableIn G s t d = true`, then there exists `d' ≤ d` with
  `dist G s t = some d'`.  (The BFS discovers the path; the minimum is
  at most `d`.)
-/
lemma reachable_implies_dist_le {G : CausalGraph} {s t d : Nat}
    (h : reachableIn G s t d = true) :
    ∃ d', dist G s t = some d' ∧ d' ≤ d := by
  obtain ⟨hst, hbound⟩ := reachableIn_bound h
  have hnotgt : ¬(s > t) := Nat.not_lt.mpr hst
  unfold dist
  simp only [hnotgt, ↓reduceIte]
  -- d is in List.range (t - s + 1) since d ≤ t - s
  have hd_lt : d < t - s + 1 := Nat.lt_succ_of_le hbound
  -- find? on the range either returns some d' (which is ≤ d) or none
  rcases h_found : (List.range (t - s + 1)).find? (fun n => reachableIn G s t n) with _ | d'
  · -- none case: all elements of the range fail, but d satisfies the predicate
    exfalso
    exact (List.find?_eq_none.mp h_found d (List.mem_range.mpr hd_lt)) h
  · -- some d' case: d' is the minimum and d' ≤ d by find?_range_le
    exact ⟨d', rfl, find?_range_le hd_lt h h_found⟩

-- ============================================================
-- VI. Triangle inequality
-- ============================================================

/--
  **Triangle inequality for the DAG distance.**

  If `dist G a b = some dab` and `dist G b c = some dbc`, then any
  shortest path `dist G a c = some dac` satisfies `dac ≤ dab + dbc`.

  Proof sketch:
  1. Extract reachability witnesses from the two `dist` hypotheses.
  2. Concatenate the paths to get a `(dab + dbc)`-hop path a → c.
  3. The definition of `dist` gives `dac ≤ dab + dbc` (it is minimum).
-/
theorem dist_triangle (G : CausalGraph) (a b c : Nat) :
    ∀ dab dbc dac,
      dist G a b = some dab →
      dist G b c = some dbc →
      dist G a c = some dac →
      dac ≤ dab + dbc := by
  intro dab dbc dac hab hbc hac
  -- Step 1: extract reachability
  have hab_r : reachableIn G a b dab = true := dist_implies_reachable hab
  have hbc_r : reachableIn G b c dbc = true := dist_implies_reachable hbc
  -- Step 2: concatenate paths
  have hac_r : reachableIn G a c (dab + dbc) = true :=
    reachableIn_concat hab_r hbc_r
  -- Step 3: dist G a c ≤ dab + dbc (and dist G a c = some dac)
  obtain ⟨dac', hac', hle⟩ := reachable_implies_dist_le hac_r
  -- dac' is the minimum found; hac says it's dac; so dac = dac'
  rw [hac] at hac'
  exact Option.some.inj hac' ▸ hle

end CausalGraph
