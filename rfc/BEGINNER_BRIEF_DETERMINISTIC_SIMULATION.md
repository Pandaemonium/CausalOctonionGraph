# Beginner Brief: Deterministic COG Simulation

Status: Active  
Audience: New contributors and worker models  
Scope: Exactly how to run deterministic simulations with current `world_code`

---

## 1. One-Sentence Core Idea

A deterministic COG simulation is fully specified by exactly two inputs:
1. the full superdetermined initial lightcone microstate,
2. the update rule.

If those two are fixed, the entire future trajectory is fixed.

---

## 2. Which Kernel This Brief Covers

This brief is for the executable kernel:
1. `world_code/Python_code/minimal_world_kernel.py`

Formal minimal contract:
1. `world_code/Lean_code/MinimalWorldKernel.lean`

Important note about repo scope:
1. The repo also contains a richer RFC-028 kernel (`CausalGraphTheory/UpdateRule.lean`) with additional structure (for example explicit temporal commit in that contract).
2. The beginner workflow here is the current `world_code` minimal deterministic kernel that workers can run immediately.

---

## 3. Input #1: The Superdetermined Initial Lightcone Microstate

## 3.1 Required JSON shape

Every simulation input JSON must contain:
1. `node_ids`: all nodes in the chosen lightcone horizon,
2. `parents`: incoming causal parents for each node,
3. `init_state`: `C x O` initial state for each node.

Template:

```json
{
  "node_ids": ["n0", "n1"],
  "parents": {
    "n0": [],
    "n1": ["n0"]
  },
  "init_state": {
    "n0": [[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[1,0]],
    "n1": [[1,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
  }
}
```

## 3.2 What a node state is

Each node state is 8 octonion basis slots:
1. index 0 is `e0`,
2. index 1..7 are `e1..e7`.

Each slot stores a Gaussian integer `[re, im]`.

So one node state is:
1. 8 pairs,
2. 16 integers total.

## 3.3 Integer rule (strict)

All coefficients must be integer literals:
1. valid: `1`, `0`, `-3`,
2. invalid: `1.0`, `0.0`, `-3.5`.

This is enforced in code (`_parse_int_coeff` in `minimal_world_kernel.py`).

## 3.4 Superdetermined means full closure up front

To keep the run deterministic and self-contained:
1. include every node you intend to simulate within the horizon,
2. include every parent link between included nodes,
3. include initial state for every listed node,
4. do not rely on implicit or missing external nodes.

In practice: your initial JSON is the complete causal context for the run.

---

## 4. Input #2: The Update Rule (Exact Current Implementation)

The rule in `world_code/Python_code/minimal_world_kernel.py` is:

1. fold parent messages into one payload by ordered octonionic multiplication,
2. left-multiply payload onto current state.

Written as code-level math:
1. `payload = interaction_fold(parent_messages)`
2. `next = cxo_mul(payload, current)`

## 4.1 Algebra primitives

The kernel uses these exact primitives:
1. Gaussian integer add/multiply (`g_add`, `g_mul`, `g_neg`),
2. octonion basis multiplication (`basis_mul`),
3. full `C x O` multiplication (`cxo_mul`).

## 4.2 Canonical Fano orientation (hard-coded)

Directed triples:
1. `(1,2,4)`
2. `(2,3,5)`
3. `(3,4,6)`
4. `(4,5,7)`
5. `(5,6,1)`
6. `(6,7,2)`
7. `(7,1,3)`

Product logic:
1. cyclic order gives positive sign,
2. anti-cyclic order gives negative sign,
3. `e0` is identity,
4. `e_i * e_i = -e0` for `i != 0`.

## 4.3 `cxo_mul(a,b)` exactly does

For each nonzero coefficient pair `(a_i, b_j)`:
1. compute basis product `e_i * e_j = sign * e_k`,
2. compute Gaussian product `a_i * b_j`,
3. apply sign if needed,
4. accumulate into output slot `k`.

That is the entire noncommutative local algebra step.

## 4.4 Parent-message fold

`interaction_fold(messages)`:
1. starts from multiplicative identity `cxo_one()`,
2. folds left in list order: `(((1 * m1) * m2) * ... * mk)`.

Empty parents:
1. `interaction_fold([]) = identity`,
2. so `next = identity * current = current` for that step.

## 4.5 Global deterministic step order

One world step (`step(world)`) is deterministic because:
1. node update loop uses `sorted(world.node_ids)`,
2. each parent list is read as `sorted(world.parents[nid])`,
3. all reads come from snapshot `old_states` (no in-step feedback mutation).

Then:
1. each node gets `msgs = [old_states[pid] for pid in sorted_parents]`,
2. each node computes `new_state[nid] = update_rule(old_state[nid], msgs)`,
3. world tick increments by 1.

## 4.6 Multi-step evolution

`run(world, steps)` applies `step` repeatedly exactly `steps` times.

No randomness appears anywhere in this path.

---

## 5. How To Prepare a Microstate for a Given Lightcone

Use this procedure every time.

## Step A: Choose a horizon and node layout

Pick:
1. max depth `D`,
2. node arrangement per depth (for example 1D toy cone or custom DAG slice).

### Concrete default layout (recommended for first custom runs)

Use a 1D layered cone:
1. depth `d` has `d+1` nodes with local index `k in [0, d]`,
2. node id format: `d<d>_n<k>` (example: `d2_n1`),
3. root is `d0_n0`.

## Step B: Enumerate all included nodes

Create `node_ids` containing every node in the chosen horizon.

Rule:
1. if a node is in scope, it must appear in `node_ids`.

For the default 1D layered cone:
1. enumerate all `(d, k)` with `0 <= d <= D` and `0 <= k <= d`,
2. sort first by `d`, then by `k`,
3. generate ids in that order.

## Step C: Define `parents` for each node

For each node in `node_ids`:
1. set `parents[node]` to the list of incoming source nodes from previous depth(s),
2. use `[]` for root nodes.

Rules:
1. every `node_id` must exist as a key in `parents`,
2. every listed parent id must also be in `node_ids`.

For the default 1D layered cone:
1. `parents(d0_n0) = []`,
2. for `d > 0`:
3. if `k = 0`, `parents(d<d>_n0) = [d<d-1>_n0]`,
4. if `k = d`, `parents(d<d>_n<d>) = [d<d-1>_n<d-1>]`,
5. else `parents(d<d>_n<k>) = [d<d-1>_n<k-1>, d<d-1>_n<k>]`.

This gives a fully specified cone with no missing causal ancestry inside the chosen horizon.

## Step D: Define `init_state` for each node

For each node in `node_ids`:
1. provide exactly 8 `[re, im]` integer pairs.

Rules:
1. exactly 8 pairs per node,
2. exactly 2 integers per pair,
3. no floats.

Practical seed strategy:
1. assign one baseline vacuum seed to most nodes,
2. assign motif seeds only on selected source nodes,
3. keep all other nodes explicit anyway (do not omit).

Example baseline vacuum seed used in existing examples:
1. `[[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[1,0]]`

## Step E: Validate with zero-step parse

Run:

```bash
python world_code/Python_code/minimal_world_kernel.py \
  --input <your_input>.json \
  --steps 0 \
  --output <tmp_output>.json
```

If this fails, fix schema/integers first.

## Step F: Run deterministic evolution

Run:

```bash
python world_code/Python_code/minimal_world_kernel.py \
  --input <your_input>.json \
  --steps <N> \
  --output <your_output>.json
```

Suggested checkpoint grid for new runs:
1. `N = 0, 1, 2, 4, 8`.

---

## 6. Minimal Validation Checklist Before You Trust a Run

1. `node_ids`, `parents`, `init_state` all present.
2. Every `node_id` has both `parents[node_id]` and `init_state[node_id]`.
3. Parent references are internal to `node_ids`.
4. Every coefficient is integer literal, not float.
5. Replay test: same input + same `steps` yields identical output JSON.

If any check fails, do not interpret physics from the run yet.

---

## 7. Practical Starter Inputs

Start from:
1. `world_code/Python_code/lightcone_microstate_examples/001_vacuum_cone_depth2.json`
2. `world_code/Python_code/lightcone_microstate_examples/020_two_electrons_small_cone.json`
3. `world_code/Python_code/lightcone_microstate_examples/021_electron_positron_small_cone.json`

Then branch to your own copied input file.

---

## 8. Bottom Line

Deterministic simulation requires only:
1. full superdetermined initial microstate over your chosen lightcone horizon,
2. fixed update rule.

Everything else (observables, fitting, interpretation) sits on top of that base and must not be mixed into kernel evolution.
