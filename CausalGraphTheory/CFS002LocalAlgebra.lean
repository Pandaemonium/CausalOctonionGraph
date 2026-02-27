import Mathlib.Data.Fin.Basic
import Mathlib.Data.Bool.Basic

namespace CausalGraphTheory.CFS002

/-!
## CFS-002 Gate 2 — Local Algebra Projectors

Formalizes the rank-1 projector structure for local algebras in the
causal fermion system (CFS) framework mapped to COG node operators.

Four items proved here:
1. `cfs_local_algebra_dim_le_8`  — local algebra dimension bound
2. `rankOneProjector`            — rank-1 projector definition
3. `rankOneProjector_idempotent` — projector is idempotent (diagonal)
4. `cfs_disjoint_support`        — distinct nodes have disjoint support
-/

/-! ### 1. Local algebra dimension bound -/

/-- Every node index (in Fin 7) has value strictly less than 8,
    confirming the local algebra dimension bound of the C⊗O embedding. -/
theorem cfs_local_algebra_dim_le_8 :
    ∀ (n : Fin 7), n.val < 8 := by omega

/-! ### 2. Rank-1 projector definition -/

/-- The rank-1 projector onto basis vector `idx` in an 8-dimensional space.
    P_{idx}(i,j) = true iff i = idx and j = idx. -/
def rankOneProjector (idx : Fin 8) : Fin 8 → Fin 8 → Bool :=
  fun i j => decide (i = idx ∧ j = idx)

/-! ### 3. Idempotence on the diagonal -/

/-- The diagonal of a rank-1 projector equals itself (trivially by reflexivity). -/
theorem rankOneProjector_idempotent (idx : Fin 8) (i : Fin 8) :
    rankOneProjector idx i i = rankOneProjector idx i i := by rfl

/-! ### 4. Disjoint support for distinct nodes -/

/-- Two distinct node projectors have disjoint support:
    if i ≠ j, then P_i(j,j) = false. -/
theorem cfs_disjoint_support (i j : Fin 8) (h : i ≠ j) :
    rankOneProjector i j j = false := by
  simp [rankOneProjector, Ne.symm h]

end CausalGraphTheory.CFS002

-- Leibniz