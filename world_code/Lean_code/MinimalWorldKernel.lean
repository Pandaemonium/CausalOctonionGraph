/-!
MinimalWorldKernel
==================

Smallest formal kernel for "full lightcone + deterministic update rule".

This file intentionally omits observables, claim logic, and UI concerns.
-/

namespace WorldCode

/- Complex integer (Gaussian integer) coefficient. -/
structure GInt where
  re : Int
  im : Int
deriving Repr, DecidableEq

/- One C x O state: 8 octonion basis slots, each with Gaussian-integer coeff. -/
abbrev CxO := Fin 8 → GInt

/- Full predetermined lightcone input. -/
structure LightconeInput where
  nodeIds : List Nat
  parents : Nat → List Nat
  initState : Nat → CxO

/- Deterministic local rule: current state + parent message list -> next state. -/
structure KernelRule where
  updateRule : CxO → List CxO → CxO

/- Runtime world state. -/
structure World where
  lc : LightconeInput
  rule : KernelRule
  state : Nat → CxO
  tick : Nat

def initWorld (lc : LightconeInput) (rule : KernelRule) : World where
  lc := lc
  rule := rule
  state := lc.initState
  tick := 0

def messagesFor (w : World) (nid : Nat) : List CxO :=
  (w.lc.parents nid).map w.state

def step (w : World) : World where
  lc := w.lc
  rule := w.rule
  state := fun nid => w.rule.updateRule (w.state nid) (messagesFor w nid)
  tick := w.tick + 1

def run : Nat → World → World
  | 0, w => w
  | Nat.succ n, w => run n (step w)

/- Core deterministic replay facts for the minimal kernel. -/
theorem step_deterministic (w1 w2 : World) (h : w1 = w2) : step w1 = step w2 := by
  simpa [h]

theorem run_deterministic (n : Nat) (w1 w2 : World) (h : w1 = w2) : run n w1 = run n w2 := by
  simpa [h]

theorem run_zero (w : World) : run 0 w = w := rfl

theorem run_succ (n : Nat) (w : World) : run (Nat.succ n) w = run n (step w) := rfl

end WorldCode

