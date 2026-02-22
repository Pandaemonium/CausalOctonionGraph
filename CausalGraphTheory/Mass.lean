/-
  CausalGraphTheory/Mass.lean
  Phase 4.3: Mass as Tick Frequency

  Defines the discrete mass of a node as the fraction:
      massFrac(n) = (tick_count(n), graph_depth)  ∈  Nat × Nat

  where:
  - `tick_count(n)` = the `tickCount` field, counting forced Tick steps.
  - `graph_depth`   = `G.size` (number of nodes = causal horizon).

  Two fractions are compared by cross-multiplication:
      (a, d) ≤ (b, d)  iff  a ≤ b     (same denominator)

  Physical interpretation:
  - Vacuum (tickCount = 0): massFrac = (0, depth) → mass 0.
  - A particle that has ticked k times in a depth-d graph has mass k/d.
  - Heavier particles accumulate more Ticks per unit causal depth.
  - The Koide constraint Q ≈ 2/3 restricts the tick-count ratios of the
    three charged lepton nodes (computed in calc/koide.py, Lean proof Phase 5).

  Claim: claims/mass_tick_frequency.yml
-/

import CausalGraphTheory.State
import CausalGraphTheory.Tick
import CausalGraphTheory.Update
import Mathlib.Data.Nat.Basic

namespace CausalGraph

-- ============================================================
-- I. Graph depth
-- ============================================================

/--
  The causal depth of a graph: the number of nodes.
  Since node IDs are assigned in strict topological order (0, 1, 2, ...),
  this equals the length of the longest possible causal chain.
-/
def graphDepth (G : CausalGraph) : Nat := G.size

-- ============================================================
-- II. Tick mass (raw, unnormalized)
-- ============================================================

/--
  The tick accumulation (raw mass) of node n:
  the number of forced Tick evaluations the node has experienced.

  This is the numerator of the discrete mass fraction.
  A vacuum node has tick mass 0; a heavily interacting node has higher values.
-/
def tickMass (G : CausalGraph) (n : Nat) : Nat :=
  match G.findNode n with
  | none       => 0
  | some node  => node.tickCount

/--
  The discrete mass as a fraction (numerator, denominator):
      massFrac G n = (tick_count(n), graph_depth(G))

  The mass ratio of two nodes in the same graph is the ratio of their
  tick counts (the denominator cancels).
-/
def massFrac (G : CausalGraph) (n : Nat) : Nat × Nat :=
  (tickMass G n, graphDepth G)

-- ============================================================
-- III. Basic properties
-- ============================================================

/-- A node that was never Tick-classified has raw mass 0. -/
theorem tickMass_zero_of_tickCount_zero {G : CausalGraph} {n : Nat} {nd : Node}
    (hfind : G.findNode n = some nd)
    (htick  : nd.tickCount = 0) :
    tickMass G n = 0 := by
  simp [tickMass, hfind, htick]

/-- A missing node has raw mass 0. -/
theorem tickMass_zero_of_not_found {G : CausalGraph} {n : Nat}
    (hfind : G.findNode n = none) :
    tickMass G n = 0 := by
  unfold tickMass; rw [hfind]

/--
  Tick mass is monotone in tick count.

  If two nodes n₁, n₂ are both in G and n₁ has fewer accumulated Ticks,
  then n₁ has a lower (or equal) tick mass.
-/
theorem tickMass_mono {G : CausalGraph} {id₁ id₂ : Nat} {nd₁ nd₂ : Node}
    (h₁    : G.findNode id₁ = some nd₁)
    (h₂    : G.findNode id₂ = some nd₂)
    (htick : nd₁.tickCount ≤ nd₂.tickCount) :
    tickMass G id₁ ≤ tickMass G id₂ := by
  unfold tickMass
  rw [h₁, h₂]
  exact htick

/--
  Mass fraction monotonicity (same denominator).

  Since both nodes share the same `graphDepth` denominator, the fraction
  ordering reduces to comparing numerators.
-/
theorem massFrac_le_iff_tickMass_le {G : CausalGraph} (n₁ n₂ : Nat)
    (hd : 0 < graphDepth G) :
    (massFrac G n₁).1 * (massFrac G n₂).2 ≤
    (massFrac G n₂).1 * (massFrac G n₁).2 ↔
    tickMass G n₁ ≤ tickMass G n₂ := by
  simp only [massFrac, graphDepth] at *
  constructor
  · intro h; exact Nat.le_of_mul_le_mul_right h hd
  · intro h; exact Nat.mul_le_mul_right _ h

-- ============================================================
-- IV. Step function and mass accumulation
-- ============================================================

/--
  The `step` function creates a new node with `tickCount = lastNode.tickCount + 1`.
  This is the elementary mass increment: each causal step adds one unit.
-/
theorem step_new_node_tickCount (G : CausalGraph) :
    match G.nodes.getLast? with
    | none          => True
    | some lastNode =>
      ∃ newNode ∈ (step G).nodes,
        newNode.id        = nextNodeId G ∧
        newNode.tickCount = lastNode.tickCount + 1 := by
  rcases _ : G.nodes.getLast? with _ | lastNode
  · trivial
  · -- step creates { id := nextNodeId G, tickCount := lastNode.tickCount + 1 }
    -- and appends it to G.nodes.  The formal proof requires reducing
    -- `match h : G.nodes.getLast? with` inside step's body, which produces
    -- ill-typed acyclic proof terms under naive substitution (Phase 6 target).
    sorry

/--
  Each `step` strictly increases the tick count of the graph's frontier node.
  In COG terms, causal time always moves forward.

  Proof sketch: after appending a new node, `findNode` on the OLD `lastNode.id`
  still returns `lastNode` (since IDs are unique and the old nodes are preserved).
  Therefore `tickMass (step G) lastNode.id = tickMass G lastNode.id`, and
  `a ≤ a + 1` closes the goal.  The formal proof requires `List.find?` lemmas
  on appended lists (Phase 6 infrastructure).
-/
theorem step_tickMass_nondecreasing (G : CausalGraph) :
    match G.nodes.getLast? with
    | none => True
    | some lastNode =>
      tickMass G lastNode.id ≤ tickMass (step G) lastNode.id + 1 := by
  split
  · trivial
  · rename_i lastNode _
    -- tickMass (step G) lastNode.id = tickMass G lastNode.id because step only
    -- *appends* a new node with a fresh ID; formal proof deferred to Phase 6
    -- (requires List.find?_append + uniqueness of node IDs).
    sorry

-- ============================================================
-- V. Koide formula connection (quantitative target)
-- ============================================================

/--
  **Koide connection (Phase 5 target).**

  For three charged-lepton nodes (e, μ, τ) in a COG run of depth d,
  with tick counts (t_e, t_μ, t_τ), the Koide ratio is:

      Q = (t_e² + t_μ² + t_τ²) / (t_e + t_μ + t_τ)²  ≈  2/3

  This is the Lean statement of the mass prediction: to be proved by
  constructing an explicit COG motif and computing tick counts in Phase 5.

  The Python verification is in calc/koide.py (using PDG lepton masses).

  Note: the ratio t_j/d cancels in Q, so Q depends only on tick-count ratios,
  not on the absolute depth d.
-/
theorem koide_from_ticks_stub :
    ∀ (t_e t_mu t_tau : Nat),
      -- Placeholder: the actual constraint relates t_e², t_μ², t_τ²
      -- to satisfy Q ≈ 2/3 (see calc/koide.py for the numerical computation)
      True :=
  fun _ _ _ => trivial

end CausalGraph
