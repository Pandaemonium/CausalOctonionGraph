import CausalGraphV2.Fano

namespace CausalGraphV2

def fanoBasisMul (i j : FanoPoint) : FanoPoint × Int :=
  if i == j then
    (i, 0)
  else
    let result := (List.finRange 7).findSome? fun l =>
      let a := fanoCycles l 0
      let b := fanoCycles l 1
      let c := fanoCycles l 2
      if i == a && j == b then some (c, (1 : Int))
      else if i == b && j == c then some (a, (1 : Int))
      else if i == c && j == a then some (b, (1 : Int))
      else if i == b && j == a then some (c, (-1 : Int))
      else if i == c && j == b then some (a, (-1 : Int))
      else if i == a && j == c then some (b, (-1 : Int))
      else none
    result.getD (i, 0)

def fanoSign (i j : FanoPoint) : Int :=
  (fanoBasisMul i j).2

def fanoThird (i j : FanoPoint) : FanoPoint :=
  (fanoBasisMul i j).1

example : fanoBasisMul 0 1 = (2, 1) := by decide
example : fanoBasisMul 1 0 = (2, -1) := by decide
example : fanoBasisMul 0 3 = (4, 1) := by decide
example : fanoBasisMul 2 5 = (4, 1) := by decide
example : fanoBasisMul 1 4 = (6, 1) := by decide

theorem fano_sign_antisymmetric (i j : FanoPoint) (h : i ≠ j) :
    fanoSign i j = -fanoSign j i := by
  revert h
  revert j
  revert i
  decide

theorem fano_sign_nonzero (i j : FanoPoint) (h : i ≠ j) :
    fanoSign i j ≠ 0 := by
  revert h
  revert j
  revert i
  decide

theorem fano_third_xor_one_indexed (i j : FanoPoint) (h : i ≠ j) :
    (fanoThird i j).val + 1 = Nat.xor (i.val + 1) (j.val + 1) := by
  revert h
  revert j
  revert i
  decide

theorem fano_sign_unit (i j : FanoPoint) (h : i ≠ j) :
    fanoSign i j = 1 ∨ fanoSign i j = -1 := by
  revert h
  revert j
  revert i
  decide

end CausalGraphV2
