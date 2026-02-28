import Std
import Std.Tactic

namespace CausalGraphV2

universe u

/-!
Layered causality theorem lane:

If every primitive edge increments depth by exactly one, then any two directed
paths between the same endpoints have identical edge count.
-/

inductive Path (Edge : α -> α -> Prop) : α -> α -> Nat -> Prop where
  | nil (a : α) : Path Edge a a 0
  | cons {a b c : α} {n : Nat} :
      Edge a b -> Path Edge b c n -> Path Edge a c (n + 1)

theorem path_depth_eq
    {α : Type u}
    (Edge : α -> α -> Prop)
    (depth : α -> Nat)
    (hLayer : ∀ {a b : α}, Edge a b -> depth b = depth a + 1) :
    ∀ {a b : α} {n : Nat}, Path Edge a b n -> depth b = depth a + n := by
  intro a b n hp
  induction hp with
  | nil x =>
      simp
  | @cons a b c n hE hp ih =>
      have hb : depth b = depth a + 1 := hLayer hE
      calc
        depth c = depth b + n := ih
        _ = (depth a + 1) + n := by simp [hb]
        _ = depth a + (n + 1) := by omega

theorem path_length_unique
    {α : Type u}
    (Edge : α -> α -> Prop)
    (depth : α -> Nat)
    (hLayer : ∀ {a b : α}, Edge a b -> depth b = depth a + 1)
    {a b : α} {n1 n2 : Nat}
    (p1 : Path Edge a b n1)
    (p2 : Path Edge a b n2) :
    n1 = n2 := by
  have h1 : depth b = depth a + n1 := path_depth_eq Edge depth hLayer p1
  have h2 : depth b = depth a + n2 := path_depth_eq Edge depth hLayer p2
  have hEq : depth a + n1 = depth a + n2 := by
    calc
      depth a + n1 = depth b := by simpa using h1.symm
      _ = depth a + n2 := by simpa using h2
  exact Nat.add_left_cancel hEq

theorem no_path_length_spread
    {α : Type u}
    (Edge : α -> α -> Prop)
    (depth : α -> Nat)
    (hLayer : ∀ {a b : α}, Edge a b -> depth b = depth a + 1)
    {a b : α} :
    ¬ ∃ n1 n2 : Nat, Path Edge a b n1 ∧ Path Edge a b n2 ∧ n1 ≠ n2 := by
  intro h
  rcases h with ⟨n1, n2, p1, p2, hne⟩
  exact hne (path_length_unique Edge depth hLayer p1 p2)

end CausalGraphV2

