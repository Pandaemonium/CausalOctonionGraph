/-
  CausalGraphTheory/Tick.lean
  Phase 2.3: Tick Classification

  Classifies nodes as either "Batch" (associative) or "Tick" (non-associative)
  based on the algebra of their incoming operators.

  Claim: claims/tick_classification.yml
-/

import CausalGraphTheory.State
import CausalGraphTheory.SubalgebraDetect
import Mathlib.Data.List.Basic

namespace CausalGraph

/--
  Collect all incoming operator basis elements at a node `n`.
  
  Returns a list of `Fin 7` indices representing the imaginary units
  present in the operators on incoming edges.
  
  e₀ (real part) is ignored as it is associative with everything.
  Only e₁..e₇ contribute to non-associativity.
-/
def incomingBasis (G : CausalGraph) (n : Nat) : List (Fin 7) :=
  let incomingEdges := G.edges.filter (fun e => e.target = n)
  incomingEdges.flatMap (fun e =>
    (List.finRange 7).filter (fun i =>
      -- Check if coefficient of e_{i+1} is non-zero
      let coeff := e.operator.c ⟨i.val + 1, by omega⟩
      -- coeff : FormalComplex ℤ; nonzero iff real or imaginary part is nonzero
      !(coeff.re == 0 && coeff.im == 0)
    )
  )

/--
  Tick classification result.
  - Batch: The incoming operators form an associative subalgebra (quaternionic).
           Order of evaluation does not matter.
  - Tick:  The incoming operators span a non-associative subspace (octonionic).
           Order of evaluation matters; this constitutes a logical "tick".
-/
inductive TickClass where
  | Batch : TickClass
  | Tick  : TickClass
  deriving Repr, DecidableEq

/--
  Classify a node based on its incoming operators.
  Uses the `batchable` predicate from SubalgebraDetect.
-/
def classify (G : CausalGraph) (n : Nat) : TickClass :=
  if SubalgebraDetect.batchable (incomingBasis G n) then
    .Batch
  else
    .Tick

end CausalGraph
