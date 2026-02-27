/-
  CausalGraphTheory/DAGProof.lean
  Phase 2.4b: DAG Preservation Proof

  Proves that the graph update step preserves the acyclicity invariant.
  Since the CausalGraph structure bundles the acyclicity proof,
  this theorem simply exposes the fact that `step` constructs a valid CausalGraph.

  Claim: claims/step_preserves_dag.yml
-/

import CausalGraphTheory.Update

namespace CausalGraph

/--
  The graph update step preserves the acyclicity of the causal graph.
  
  Proof:
  The `step` function constructs a new `CausalGraph` structure.
  The `CausalGraph` definition requires an `acyclic` field:
    ∀ e ∈ edges, e.source < e.target
  
  The construction of `step` ensures this property holds for the new edges
  (which connect existing max-ID nodes to a strictly larger new ID),
  and inherits it for old edges.
  
  Therefore, the resulting graph is acyclic by construction.
-/
theorem step_preserves_acyclic (G : CausalGraph) :
  (step G).acyclic = (step G).acyclic := rfl -- Tautology because it's built-in

-- More meaningful statement:
theorem step_is_acyclic (G : CausalGraph) :
  ∀ e ∈ (step G).edges, e.source < e.target :=
  (step G).acyclic

end CausalGraph
