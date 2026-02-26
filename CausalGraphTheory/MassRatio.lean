import CausalGraphTheory.Fano
import Mathlib.GroupTheory.Perm.Basic
import Mathlib.GroupTheory.Subgroup.Basic
import Mathlib.Data.Fintype.Card
import Mathlib.Data.Finset.Basic

/-!
# Mass Ratio: Tick Overhead Constant k_gate = 21

Derives the tick overhead constant k_gate = 21 from the structure
of the Fano plane automorphism group.

The Fano plane automorphism group (GL(3,2)) has order 168.
The stabilizer of the associative subalgebra generators e1, e2, e3
(corresponding to Fano points 0, 1, 2) has order 8.
Therefore k_gate = 168 / 8 = 21.

Claim: claims/mass_ratio.yml (MASS-001)
-/

/-! ## Collinearity Relation -/

/-- Three Fano points are collinear if they all lie on a common Fano line. -/
def FanoRel (x y z : FanoPoint) : Prop :=
  ∃ l : FanoLine, incident x l ∧ incident y l ∧ incident z l

/-! ## Fano Automorphism Group -/

/-- A permutation is a Fano automorphism if it preserves FanoRel (collinearity). -/
def IsFanoAut (σ : Equiv.Perm FanoPoint) : Prop :=
  ∀ x y z : FanoPoint, FanoRel x y z ↔ FanoRel (σ x) (σ y) (σ z)

instance IsFanoAut.instDecidable (σ : Equiv.Perm FanoPoint) : Decidable (IsFanoAut σ) := by
  unfold IsFanoAut FanoRel
  infer_instance

/-- The Fano automorphism group as a subgroup of Perm FanoPoint. -/
def FanoAutomorphismGroup : Subgroup (Equiv.Perm FanoPoint) where
  carrier := {σ | IsFanoAut σ}
  one_mem' := by intro x y z; exact Iff.rfl
  mul_mem' := by
    intro σ τ hσ hτ x y z
    exact ⟨fun h => (hσ (τ x) (τ y) (τ z)).mp ((hτ x y z).mp h),
           fun h => (hτ x y z).mpr ((hσ (τ x) (τ y) (τ z)).mpr h)⟩
  inv_mem' := by
    intro σ hσ x y z
    constructor
    · intro h
      have key := (hσ (σ⁻¹ x) (σ⁻¹ y) (σ⁻¹ z)).mp h
      simp [Equiv.Perm.apply_inv_self] at key
      exact key
    · intro h
      have key := (hσ (σ⁻¹ x) (σ⁻¹ y) (σ⁻¹ z)).mpr
      simp [Equiv.Perm.apply_inv_self] at key
      exact key h

/-- The Fano automorphism group has order 168. -/
theorem fano_aut_card : Fintype.card FanoAutomorphismGroup = 168 := by
  native_decide

/-! ## Associative Subalgebra Stabilizer -/

/-- The associative subalgebra generators e1, e2, e3 are at Fano points 0, 1, 2. -/
def assocPoints : Finset FanoPoint := {0, 1, 2}

/-- An automorphism set-wise stabilizes assocPoints. -/
def StabilizesAssoc (σ : Equiv.Perm FanoPoint) : Prop :=
  ∀ x ∈ assocPoints, σ x ∈ assocPoints

instance StabilizesAssoc.instDecidable (σ : Equiv.Perm FanoPoint) :
    Decidable (StabilizesAssoc σ) := by
  unfold StabilizesAssoc
  infer_instance

/-- The stabilizer of e1, e2, e3 within the Fano automorphism group. -/
def AssociativeSubalgebraStabilizer : Subgroup (Equiv.Perm FanoPoint) where
  carrier := {σ | IsFanoAut σ ∧ StabilizesAssoc σ}
  one_mem' := ⟨fun x y z => Iff.rfl, fun x hx => hx⟩
  mul_mem' := by
    intro σ τ ⟨hσ_aut, hσ_stab⟩ ⟨hτ_aut, hτ_stab⟩
    exact ⟨fun x y z =>
        ⟨fun h => (hσ_aut (τ x) (τ y) (τ z)).mp ((hτ_aut x y z).mp h),
         fun h => (hτ_aut x y z).mpr ((hσ_aut (τ x) (τ y) (τ z)).mpr h)⟩,
      fun x hx => hσ_stab (τ x) (hτ_stab x hx)⟩
  inv_mem' := by
    intro σ ⟨hσ_aut, hσ_stab⟩
    refine ⟨fun x y z => ?_, fun x hx => ?_⟩
    · constructor
      · intro h
        have key := (hσ_aut (σ⁻¹ x) (σ⁻¹ y) (σ⁻¹ z)).mp h
        simp [Equiv.Perm.apply_inv_self] at key; exact key
      · intro h
        have key := (hσ_aut (σ⁻¹ x) (σ⁻¹ y) (σ⁻¹ z)).mpr
        simp [Equiv.Perm.apply_inv_self] at key; exact key h
    · -- σ⁻¹ maps assocPoints to itself since σ does bijectively
      have himage : assocPoints.image σ = assocPoints := by
        apply Finset.eq_of_subset_of_card_le
        · intro y hy
          obtain ⟨z, hz, rfl⟩ := Finset.mem_image.mp hy
          exact hσ_stab z hz
        · simp [Finset.card_image_of_injective _ σ.injective]
      obtain ⟨y, hy, hyx⟩ := Finset.mem_image.mp (himage ▸ hx)
      have heq : σ⁻¹ x = y := by
        apply σ.injective
        simp [Equiv.Perm.apply_inv_self, hyx]
      rw [heq]; exact hy

/-- The associative subalgebra stabilizer has order 8. -/
theorem assoc_stab_card : Fintype.card AssociativeSubalgebraStabilizer = 8 := by
  native_decide

/-! ## The Gate Overhead Constant -/

/-- k_gate = |Aut(Fano)| / |Stab({e1,e2,e3})|, the tick overhead constant. -/
def k_gate : ℕ :=
  Fintype.card FanoAutomorphismGroup / Fintype.card AssociativeSubalgebraStabilizer

/-- The gate overhead constant equals 21. -/
theorem k_gate_is_21 : k_gate = 21 := by
  unfold k_gate
  rw [fano_aut_card, assoc_stab_card]