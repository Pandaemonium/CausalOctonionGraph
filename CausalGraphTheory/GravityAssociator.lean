/-
  CausalGraphTheory/GravityAssociator.lean

  Algebra-only gravity primitives:
  - associator as nonassociative curvature proxy,
  - indicator form used by runtime probes,
  - basic theorems under associativity hypothesis.

  This module introduces no extra gravity field.
-/

namespace CausalGraph

/-- Associator of a binary operation `mul` on `α`. -/
def associator {α : Type} (mul : α → α → α) (a b c : α) : α × α :=
  (mul (mul a b) c, mul a (mul b c))

/-- Indicator: `true` iff associator mismatch is nonzero. -/
def associatorMismatch {α : Type} [DecidableEq α]
    (mul : α → α → α) (a b c : α) : Bool :=
  ((mul (mul a b) c) != (mul a (mul b c)))

/-- If `mul` is associative, associator components are equal. -/
theorem associator_eq_of_assoc {α : Type} (mul : α → α → α)
    (hassoc : ∀ x y z, mul (mul x y) z = mul x (mul y z))
    (a b c : α) :
    (associator mul a b c).1 = (associator mul a b c).2 := by
  unfold associator
  simpa using hassoc a b c

/-- Associativity forces mismatch indicator to be false. -/
theorem associatorMismatch_false_of_assoc {α : Type} [DecidableEq α]
    (mul : α → α → α)
    (hassoc : ∀ x y z, mul (mul x y) z = mul x (mul y z))
    (a b c : α) :
    associatorMismatch mul a b c = false := by
  unfold associatorMismatch
  have h : (mul (mul a b) c) = (mul a (mul b c)) := hassoc a b c
  simp [h]

end CausalGraph
