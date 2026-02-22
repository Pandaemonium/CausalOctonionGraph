/-
  CausalGraphTheory/Vacuum.lean
  VAC-001: Stability of the Sterile Vacuum

  Two discrete theorems formalising vacuum stability in the COG framework:

  1. vacuum_is_stable
     A CausalGraph whose every node carries the `.vacuum` label remains
     a vacuum graph after any application of `step`.  The step function
     always appends exactly one node with label = .vacuum (in the genesis
     case: the genesis node; in the non-empty case: the new frontier node).
     Physical reading: the graph update rule cannot spontaneously create
     matter (V, S+, S-) from a pure vacuum without an external operator.

  2. vacuum_annihilates_operators
     The zero ComplexOctonion (the discrete vacuum state vector ⟨fun _ => 0⟩)
     is annihilated by right-multiplication by any operator O:  O * 0 = 0.
     Physical reading: no gauge operator can lift the vacuum to a charged
     state without a non-zero source on the right.

  Claim: claims/vacuum_stability.yml
-/

import CausalGraphTheory.State
import CausalGraphTheory.Update
import Mathlib.Data.List.Basic

namespace CausalGraph

-- ============================================================
-- I. Vocabulary
-- ============================================================

/--
  A CausalGraph is a *vacuum graph* if every node carries the `.vacuum`
  label.  This models the universe before any matter excitations: no
  vector (V) or spinor (S±) particles exist.
-/
def isVacuumGraph (G : CausalGraph) : Prop :=
  ∀ n ∈ G.nodes, n.label = .vacuum

-- ============================================================
-- II. Structural stability
-- ============================================================

/--
  **Vacuum stability (structural).**

  If G is a vacuum graph then `step G` is also a vacuum graph.

  Proof sketch:
  - *Empty graph* (`G.nodes.getLast? = none`): `step` creates the genesis
    node `{ label := .vacuum, ... }`.  The sole node is vacuum.  ✓
  - *Non-empty graph* (`G.nodes.getLast? = some lastNode`): by
    `step_nodes_of_some`, `(step G).nodes = G.nodes ++ [newNode]` where
    `newNode.label = .vacuum`.  Nodes from `G.nodes` are vacuum by
    hypothesis; the appended node is vacuum by construction.  ✓
-/
theorem vacuum_is_stable (G : CausalGraph) :
    isVacuumGraph G → isVacuumGraph (step G) := by
  intro hvac n hmem
  rcases hlast : G.nodes.getLast? with _ | lastNode
  · -- G is empty: step creates the genesis node {label := .vacuum}
    -- Unfold step and use split (not simp) to avoid the named-match problem
    have hstep : (step G).nodes = [{
        id := 0, label := .vacuum,
        state := ⟨fun _ => 0⟩, tickCount := 0}] := by
      unfold step
      split
      · simp_all  -- some branch: contradicts hlast = none
      · rfl        -- none branch: genesisNode = {id := 0, label := .vacuum, ...}
    rw [hstep] at hmem
    simp only [List.mem_singleton] at hmem
    subst hmem
    rfl
  · -- G non-empty: step appends a fresh {label := .vacuum} node
    rw [step_nodes_of_some hlast] at hmem
    simp only [List.mem_append, List.mem_singleton] at hmem
    rcases hmem with h | rfl
    · exact hvac n h           -- old node: vacuum by hypothesis
    · rfl                       -- new node: label = .vacuum by construction

-- ============================================================
-- III. Algebraic annihilation
-- ============================================================

/-- The zero octonion has every component equal to zero (used to unfold
    `(0 : Octonion R).c k` into the literal `0 : R` for `simp`). -/
private lemma zero_c_eq {R : Type*} [CommRing R] (k : Fin 8) :
    (0 : Octonion R).c k = 0 := rfl

/--
  **Vacuum annihilation.**

  The zero `ComplexOctonion ℤ` — the discrete vacuum state vector — is
  annihilated by right-multiplication:  `O * 0 = 0` for any operator O.

  Proof: `Octonion.ext` reduces to 8 component goals.  After unfolding the
  multiplication instance (`HMul.hMul`, `Mul.mul`) and substituting
  `(0 : Octonion R).c k = 0` (via `zero_c_eq`), each LHS component becomes
  a `FormalComplex ℤ` struct literal with `re/im = 0`.  `simp` with
  `FormalComplex.ext_iff` closes the remaining goals.
-/
theorem vacuum_annihilates_operators (O : ComplexOctonion ℤ) :
    O * (0 : ComplexOctonion ℤ) = 0 := by
  apply Octonion.ext
  intro i
  fin_cases i
  <;> simp only [HMul.hMul, Mul.mul, zero_c_eq,
                 FormalComplex.zero_re, FormalComplex.zero_im]
  <;> simp [FormalComplex.ext_iff]

end CausalGraph
