# RFC-002: Deterministic Tick Ordering and Canonical Parenthesization

**Status:** Active — Architecture Draft (2026-02-24)
**Module:** `COG.Core.TickOrder` and `COG.Core.Dynamics`
**Dependencies:** `rfc/RFC-001_Canonical_State_and_Rules.md`, `rfc/CONVENTIONS.md`

## 1. Executive Summary
This RFC removes runtime ambiguity from non-associative updates.
Every node's evaluation order and parenthesization is fixed by metadata already present in the initial microstate.
The simulator must not introduce new ordering information while running.

Goal: make `step` a total deterministic function of prior state only.

**Superdeterminism guarantee.** The COG model is superdeterministic:
given the **complete** initial microstate (node states + edge operators +
evaluation plans), the entire future causal history is uniquely determined.
No "choice" is ever made at runtime. Any apparent branching (RFC-001 §3.3)
is an artifact of a simulator that does not have access to the full
evaluation plan and must therefore explore all branches. An omniscient
observer — or equivalently, a simulation with the full initial evaluation
plan embedded — sees only one future with no branching. Specifically:

- "Branching" = the simulator's search through the space of evaluation
  plans that are compatible with the given node states and edge operators.
- "Physical reality" = the specific evaluation plan that was embedded in
  the initial conditions of this particular causal history.
- "Canonical future event ordering" = the total ordering on events forced
  by `ordered_edges_n` and `paren_tree_n` (§3.2 below), which are
  immutable after initialization.

This framing is consistent with RFC-006 (no free parameters) and the
Prime Directive (no continuum, no probability amplitudes): the universe
is an algorithm running on a fixed input, not a probabilistic process.

---

## 2. Scope
This RFC defines:
- A canonical ordering for incoming operators at each node.
- A canonical binary parenthesization for Tick-class updates.
- Tie-break rules that always produce one unique schedule.
- Invariants that enforce "no exogenous information creation."

This RFC does not define:
- Node identity merge policy.
- Mass/depth semantics.

---

## 3. Initial Microstate Requirements
The initial microstate must include an immutable evaluation plan.

### 3.1 Required Identifiers
- `NodeId`: globally unique natural number.
- `EdgeId`: globally unique natural number.
- `TopoIndex`: immutable topological index used for DAG order.

### 3.2 Per-Node Evaluation Plan
For each node `n`, define:
- `ordered_edges_n : List EdgeId`  
  A total order over all potential incoming operators for `n`.
- `paren_tree_n : FullBinaryTree EdgeId`  
  A full binary tree whose leaf order is exactly `ordered_edges_n`.
- `tick_mode_n : Batch | Tick` or a deterministic predicate that computes it from state.

Constraints:
- Leaves in `paren_tree_n` are unique.
- Leaves in `paren_tree_n` match `ordered_edges_n` exactly.
- Plans are immutable after initialization.

---

## 4. Canonical Ordering and Tie-Break Rules
At each step, for node `n`, let `E_n` be currently active incoming edges.

### 4.1 Order Selection
1. Select edges in `E_n` that appear in `ordered_edges_n`.
2. Preserve the order from `ordered_edges_n`.
3. If `E_n` contains an edge missing from `ordered_edges_n`, the state is invalid.

### 4.2 Tie-Break Key (if plan is generated from static metadata)
When constructing `ordered_edges_n` from deterministic metadata, sort lexicographically by:
1. `priority_rank` (lower first)
2. `source_topo_index` (lower first)
3. `source_node_id` (lower first)
4. `edge_label_rank` (fixed global enum order)
5. `edge_id` (lower first)

This key must be total and stable.

---

## 5. Canonical Parenthesization
Let `ops_n` be incoming operators in canonical order.

### 5.1 Batch Case
- Evaluate using a fixed left fold on `ops_n` or an equivalent fixed tree.
- No tick increment.

### 5.2 Tick Case
- Evaluate exactly by `paren_tree_n` shape and left/right child ordering.
- Tick increments are deterministic functions of this fixed tree traversal.

No runtime rebalancing, heuristic reordering, or opportunistic optimization is allowed.

---

## 6. Invariants
The following are hard invariants:

1. `Determinism`  
   `step(G_t) = G_(t+1)` is a pure function with no hidden inputs.

2. `Schedule Immutability`  
   `ordered_edges_n` and `paren_tree_n` are constant for each node identity.

3. `No Exogenous Information`  
   No RNG, wall-clock time, external IO, nondeterministic iteration order, or floating-point nondeterminism may influence ordering decisions.

4. `Replay Invariance`  
   Re-running from the same initial microstate produces bit-identical state trajectories.

5. `Observer Entropy Zero (Omniscient View)`  
   All branch choices are predeclared; simulation reveals pre-encoded structure but does not create new branch information.

---

## 7. Lean and Python Implementation Targets
### 7.1 Lean
- Define `EvalTree`, `NodeEvalPlan`, `GlobalEvalPlan`.
- Define `evalNodeWithPlan : GlobalEvalPlan -> CausalGraph -> NodeId -> NodeState`.
- Prove:
  - `evalNodeWithPlan_deterministic`
  - `step_deterministic`
  - `plan_immutability_preserved`

### 7.2 Python
- Implement dataclasses mirroring `NodeEvalPlan` and `EvalTree`.
- Implement:
  - `ordered_incoming(node_id, edges, plan)`
  - `evaluate_with_tree(ops, tree)`
  - `update_step(state, plan)`
- Add tests:
  - same input, multiple runs, identical hashes
  - identical logical edges in different insertion orders, identical output
  - missing edge in plan raises deterministic validation error

---

## 8. Validation Checklist
- [ ] Every node has an evaluation plan before first update.
- [ ] Plan edge order is total and stable.
- [ ] Tick nodes use explicit tree shape from plan.
- [ ] No runtime randomness or external entropy sources.
- [ ] Replay test passes for at least 100 repeated runs.
