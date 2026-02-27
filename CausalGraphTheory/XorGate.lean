 /-
  CausalGraphTheory/XorGate.lean

  Handed XOR/sign interaction layer for imaginary octonion basis units.

  This module does not replace canonical multiplication; it exposes a compact
  interaction contract:
    - index channel (third basis unit)
    - sign channel (plus-or-minus orientation)
    - handedness (left/right application)
-/

import CausalGraphTheory.FanoMul

/-- Handed interaction mode for applying an operator to a basis-state unit. -/
inductive Handedness where
  | left
  | right
deriving DecidableEq, Repr

/-- Handed sign channel over imaginary basis indices (Fano points 0..6). -/
def handedSign (op state : FanoPoint) (hand : Handedness) : Int :=
  match hand with
  | .left => fanoSign op state
  | .right => fanoSign state op

/-- Handed index channel over imaginary basis indices (Fano points 0..6). -/
def handedThird (op state : FanoPoint) (hand : Handedness) : FanoPoint :=
  match hand with
  | .left => fanoThird op state
  | .right => fanoThird state op

/-- Distinct-pair symmetry of the third-index channel. -/
theorem fano_third_symmetric (i j : FanoPoint) (h : i = j -> False) :
    fanoThird i j = fanoThird j i := by
  revert h
  revert j
  revert i
  decide

/-- Right-handed interaction flips the sign channel for distinct pairs. -/
theorem handed_right_sign_flip (op state : FanoPoint) (h : op = state -> False) :
    handedSign op state .right = -handedSign op state .left := by
  unfold handedSign
  have h' : state = op -> False := by
    intro hs
    exact h hs.symm
  simpa using (fano_sign_antisymmetric state op h')

/-- Handedness does not change index channel for distinct pairs. -/
theorem handed_right_same_index (op state : FanoPoint) (h : op = state -> False) :
    handedThird op state .right = handedThird op state .left := by
  unfold handedThird
  have h' : state = op -> False := by
    intro hs
    exact h hs.symm
  simpa using (fano_third_symmetric state op h')

/-- For distinct pairs, handed sign is always unit-valued (plus one or minus one). -/
theorem handed_sign_unit (op state : FanoPoint) (hand : Handedness) (h : op = state -> False) :
    Or (handedSign op state hand = 1) (handedSign op state hand = -1) := by
  cases hand with
  | left =>
      simpa [handedSign] using (fano_sign_unit op state h)
  | right =>
      have h' : state = op -> False := by
        intro hs
        exact h hs.symm
      simpa [handedSign] using (fano_sign_unit state op h')

/-- Left-handed index channel equals one-indexed XOR channel for distinct pairs. -/
theorem handed_left_xor_one_indexed (op state : FanoPoint) (h : op = state -> False) :
    (handedThird op state .left).val + 1 = Nat.xor (op.val + 1) (state.val + 1) := by
  unfold handedThird
  exact fano_third_xor_one_indexed op state h
