# RFC-001: The Canonical State and Algorithmic Update Rules

**Status:** Active — Phase II (major revision)
**Supersedes:** RFC-001 Phase I (vague prototype, 2026-02-22)
**Module:** `CausalGraphTheory.State`, `CausalGraphTheory.Update`
**Dependencies:** `rfc/CONVENTIONS.md` (locked)

---

## 1. Executive Summary

This RFC gives the **exact, unambiguous algorithmic definitions** required
before any graph simulation can be written. It specifies:

1. What a Node is (its data type and permitted states).
2. What an Edge carries (its algebraic payload).
3. How a new Node's state is computed from its parents (the Interaction Rule).
4. What the graph engine must do when the three operands of a product are
   non-associative (the Branching Protocol).
5. How tick counts accumulate (the Tick Rule).

**No free parameters exist.** Every rule is forced by the Fano plane structure
and the Alternativity Theorem. The simulation's output — the cycle cost ratio
of the proton motif to the electron motif — must emerge from these rules
without any tunable constants.

---

## 2. Definitions

### 2.1 The Node

A **Node** N is a record:

```
N : {
  id        : Nat      -- unique, strictly increasing (DAG topological order)
  state     : OctIdx   -- a member of {1, 2, 3, 4, 5, 6, 7}
  tickCount : Nat      -- cumulative operations consumed to generate this node
}
```

where `OctIdx = {1, 2, 3, 4, 5, 6, 7}` denotes the *index* of one of the
seven imaginary octonionic basis elements from `CONVENTIONS.md §1`.
The state `k` stands for the element $e_k$.

**What a state represents physically.** Each of the 7 imaginary units
occupies a specific structural role in the $\mathbb{C} \otimes \mathbb{O}$
algebra (`CONVENTIONS.md §5.2`):

| OctIdx | Witt pair / role |
|--------|-----------------|
| 1 | Color 1 — raising half of pair $(e_6, e_1)$ |
| 2 | Color 2 — raising half of pair $(e_2, e_5)$ |
| 3 | Color 3 — raising half of pair $(e_3, e_4)$ |
| 4 | Color 3 — lowering half of pair $(e_3, e_4)$ |
| 5 | Color 2 — lowering half of pair $(e_2, e_5)$ |
| 6 | Color 1 — lowering half of pair $(e_6, e_1)$ |
| 7 | Vacuum axis (symmetry-breaking direction $e_7$) |

A quark node of Color $j$ occupies one of the two elements in Witt pair $j$.
A transition to $e_7$ signals an encounter with the vacuum axis (confinement
boundary event — must be tracked but does not terminate the simulation).

**What is NOT a valid node state.** Linear combinations over $\mathbb{R}$ or
$\mathbb{C}$ are not stored in a node's `state` field. The state is always one
of the 7 discrete labels. Any algebraic product that yields a linear
combination is handled by the branching protocol (§3.3) before storage.

---

### 2.2 The Edge

An **Edge** E is a record:

```
E : {
  src : Nat      -- ID of the source node
  dst : Nat      -- ID of the destination node (dst > src, strict DAG order)
  op  : OctIdx   -- the gluon operator e_{op}
}
```

**The DAG invariant.** `dst > src` for every edge. The graph is acyclic by
construction.

**Physical meaning of the edge operator.** The operator `op = g` represents
the imaginary unit $e_g$ carried by the gluon. It is the color rotation
operator acting at the receiving node. For QCD color exchange, `g` is one of
the six imaginary units on the three Witt color planes. Photon (`U(1)`) edges
involve the complex unit $i$ and are specified in RFC-003.

---

### 2.3 The Graph State

The **graph state** $G$ is:

```
G : {
  nodes : List Node
  edges : List Edge
}
```

with the DAG invariant: for every edge in `G.edges`, both `src` and `dst` are
IDs of nodes in `G.nodes`, and the graph has no directed cycles.

---

## 3. The Interaction Rule

### 3.1 The 3-Body Product

A single **interaction event** is a triple $(N_{\mathrm{src}},\, g,\,
N_{\mathrm{dst}})$ where:

- $N_{\mathrm{src}}$: the **source node** (the quark emitting the gluon),
  with state $a \in \{1,\ldots,7\}$ (representing $e_a$).
- $g \in \{1,\ldots,7\}$: the **gluon operator** (carried by the edge).
- $N_{\mathrm{dst}}$: the **destination node** (the quark receiving the
  gluon), with state $b \in \{1,\ldots,7\}$ (representing $e_b$).

The **left-bracketed output state** is:

$$s_L = (e_a \cdot e_g) \cdot e_b$$

The **right-bracketed output state** is:

$$s_R = e_a \cdot (e_g \cdot e_b)$$

Both products are computed using the sign table from `CONVENTIONS.md §2`.

**Concretely** (using the table directly):

```
left_intermediate := fano_product(a, g)    -- = (sign_{ag}, k) where e_a * e_g = sign * e_k
s_L               := fano_product(left_intermediate.idx, b)

right_intermediate := fano_product(g, b)   -- = (sign_{gb}, m) where e_g * e_b = sign * e_m
s_R                := fano_product(a, right_intermediate.idx)
```

where `fano_product(i, j)` returns `(FANO_SIGN[(i,j)], FANO_THIRD[(i,j)])`
from `conftest.py`. Signs propagate multiplicatively.

---

### 3.2 The Associativity Test

**Definition.** The **Alternativity Trigger** condition for a triple $(a, g, b)$
with $a, g, b$ all distinct is:

```
triggers(a, g, b) :=  NOT  ({a, g, b} in FANO_CYCLES)
```

That is: the trigger fires when the three indices do NOT form one of the 7
directed Fano triples from `CONVENTIONS.md §2`.

**The 35/7/28 split.** There are $\binom{7}{3} = 35$ unordered triples of
distinct elements from $\{1,\ldots,7\}$. Exactly **7** are Fano triples.
The remaining **28** are non-associative. Therefore, for a randomly chosen
interaction triple, the Alternativity Trigger fires with probability
$28/35 = 4/5$.

**Theorem** (Alternativity, `CONVENTIONS.md §3`). For distinct imaginary
units $e_a, e_g, e_b$:

- `NOT triggers(a, g, b)` $\implies$ $s_L = s_R$ (single result).
- `triggers(a, g, b)` $\implies$ $s_L = -s_R$ (the two bracketings are
  negatives of each other; $s_L = \pm e_m$, $s_R = \mp e_m$ for some $m$).

Note: $s_L = -s_R$ means both branches have the **same** index $m$ but
**opposite signs**. The DAG must track both sign variants as distinct causal
futures.

---

### 3.3 The Branching Protocol (The Prime Directive of the Engine)

**Algorithm `update_step(N_src, g, N_dst, G)`:**

```
a := N_src.state
b := N_dst.state

s_L := left-bracketed product  (e_a · e_g) · e_b    [using CONVENTIONS §2]
s_R := right-bracketed product  e_a · (e_g · e_b)   [using CONVENTIONS §2]

if NOT triggers(a, g, b):

    ╔══════════════════════════════════════════════╗
    ║  ASSOCIATIVE CASE                            ║
    ║  s_L = s_R  (single unambiguous result)      ║
    ║  Cost: 1 tick (one product tree evaluated)   ║
    ╚══════════════════════════════════════════════╝

    N_new := Node {
        id        = nextId(G)
        state     = s_L
        tickCount = N_dst.tickCount + 1
    }
    append N_new to G.nodes
    append Edge { src=N_dst.id, dst=N_new.id, op=g } to G.edges
    return [N_new]

else:

    ╔══════════════════════════════════════════════════════════╗
    ║  NON-ASSOCIATIVE CASE — Alternativity Trigger fires      ║
    ║  s_L ≠ s_R  (two distinct results, neither preferred)   ║
    ║  Cost: 2 ticks (both product trees must be evaluated)    ║
    ║  Both futures are spawned as distinct DAG nodes.         ║
    ╚══════════════════════════════════════════════════════════╝

    N_left  := Node { id = nextId(G),     state = s_L, tickCount = N_dst.tickCount + 2 }
    N_right := Node { id = nextId(G) + 1, state = s_R, tickCount = N_dst.tickCount + 2 }
    append N_left, N_right to G.nodes
    append Edge { src=N_dst.id, dst=N_left.id,  op=g } to G.edges
    append Edge { src=N_dst.id, dst=N_right.id, op=g } to G.edges
    return [N_left, N_right]
```

**Why the cost is exactly 2 (not 1, not 3).** Each bracketing — $s_L$ and
$s_R$ — is one complete product-tree evaluation. These are the only two
possible bracketings of three elements (there are no others). Evaluating
both is the irreducible minimum for causal completeness. Neither is a
"penalty": they are the two physically distinct futures of the interaction.
The cost of 2 is forced by the algebra, not chosen by the model.

**Why both nodes are spawned.** The DAG encodes ALL causally consistent
futures. Discarding either branch would impose an evaluation order that
the algebra explicitly denies. Both branches are equally valid causal
continuations of the graph.

---

## 4. Tick Counting and Mass

### 4.1 Cumulative Tick Cost

The `tickCount` field of a node records the total number of product
evaluations consumed by the causal path that generated it. For a node $N$
reached via a sequence of $k$ interaction steps:

```
N.tickCount = sum of costs of all steps on the path from the root to N
            = (number of associative steps on the path) * 1
            + (number of non-associative steps on the path) * 2
```

### 4.2 The Electron Baseline

The **electron motif** consists of one node cycling within a single
associative quaternionic subalgebra $\mathbb{H}_L$ generated by one Fano
line (e.g., L1: $\{e_1, e_2, e_3\}$, `CONVENTIONS.md §3`).

Every interaction within this subalgebra satisfies `NOT triggers(a, g, b)`:
- All products of $\{e_1, e_2, e_3\}$ stay within the subalgebra.
- No Alternativity Trigger fires.
- Cost per hop: **1 tick**.

The electron baseline cycle length $C_e$ is the minimum number of hops to
return to the initial state. This must be computed from the update rule
(not assumed). It is likely 6 (the rotation order of the triangle under
the L1 quaternion action) or 8 (the full quaternion group order).

### 4.3 The Proton Motif

The **proton motif** initial color-singlet topology:

```
N_1: state = 5  (e_5, Color 2 lowering)
N_2: state = 1  (e_1, Color 1 raising)
N_3: state = 3  (e_3, Color 3 raising)
```

One element from each Witt pair; see `CONVENTIONS.md §5.2`.

A **routing step** applies three consecutive `update_step` calls:

```
Step A:  update_step(N_1, g_12, N_2)  -->  {N_2a, N_2b?, ...}
Step B:  update_step(N_2*, g_23, N_3) -->  {N_3a, N_3b?, ...}
Step C:  update_step(N_3*, g_31, N_1) -->  {N_1a, N_1b?, ...}
```

where the gluon operators $g_{12}, g_{23}, g_{31}$ are the SU(3) color-exchange
operators (locked in RFC-007 §3.2 — see §5.1 below).

The routing step may create a tree of branching states. The tree is evolved
until any branch reaches the **color-singlet recurrence condition**:

```
color_singlet_state(N_1', N_2', N_3') :=
    { N_1'.state ∈ {1, 6} }      -- Color 1 Witt pair
    AND { N_2'.state ∈ {2, 5} }  -- Color 2 Witt pair
    AND { N_3'.state ∈ {3, 4} }  -- Color 3 Witt pair
    AND the specific initial combination (5, 1, 3) is restored
```

The **cycle cost** $C_p$ is the `tickCount` of the first node (across all
branches) that satisfies this condition.

### 4.4 The Mass Ratio

```
mu_COG  :=  C_p / C_e
```

**Target:**  $\mu_{\mathrm{exp}} = 1836.15267343$ (CODATA 2022, MU-001).

The simulation must not be adjusted to approach this target. The rules in
§3.3 are fixed. If `mu_COG != 1836...`, document the exact computed value
in RFC-007 and `claims/proton_electron_ratio.yml` as a falsification datum.

---

## 5. Open Questions (Must Be Resolved Before Simulation)

### 5.1 Gluon Assignment Table (BLOCKING — highest priority)

**Question:** What imaginary unit $e_g$ is the gluon operator for each of
the three inter-color exchanges?

This is the critical missing piece. From the SU(3) Fano structure
(GAUGE-001, RFC-007), each color exchange corresponds to a rotation in
a Witt cross-plane. The candidates for each exchange are the imaginary
units that are NOT in either Witt pair being exchanged:

| Exchange | Witt pair 1 | Witt pair 2 | Candidate gluons (complement) |
|----------|-------------|-------------|-------------------------------|
| Color 1 ↔ 2 | $\{e_6, e_1\}$ | $\{e_2, e_5\}$ | $\{e_3, e_4, e_7\}$ |
| Color 1 ↔ 3 | $\{e_6, e_1\}$ | $\{e_3, e_4\}$ | $\{e_2, e_5, e_7\}$ |
| Color 2 ↔ 3 | $\{e_2, e_5\}$ | $\{e_3, e_4\}$ | $\{e_1, e_6, e_7\}$ |

**Pre-simulation action:** For each of the 9 candidate gluons (3 per
exchange), run the 3-body associativity check `triggers(s_src, g, s_dst)`
for all 4 possible (src state, dst state) combinations. The correct gluon
assignment is the one consistent with the SU(3) symmetry argument in
GAUGE-001. Record the result in RFC-007 §3.2.

### 5.2 Branch Merging Rule

When multiple branches simultaneously reach the singlet recurrence, which
tick count defines $C_p$? The proposed resolution is **(a) the minimum**,
on the grounds that the physical proton occupies the lowest-cost
configuration. Must be confirmed before reporting $\mu_{\mathrm{COG}}$.

### 5.3 Electron Cycle Length

Compute $C_e$ from the update rule (§4.2) before the mass ratio is
calculated. Do not assume $C_e = 1$.

---

## 6. Red Team Objections (Updated)

### Attack Vector 1: Lorentz covariance without a global clock

*How do macroscopic regions maintain synchronized Lorentz covariance?*

**Partial answer.** Lorentz covariance is expected to emerge as an
approximate symmetry of large node collections whose tick frequencies
synchronize through edge exchange. It is not an input axiom. The discrete
DAG distance metric (`CausalGraphTheory/Distance.lean`) provides the
discrete substitute for the Minkowski interval. Full derivation is a
future RFC.

### Attack Vector 2: Edge ordering at a node with multiple parents

*If nodes A and B both send edges to node C, what order does C use?*

**Answer.** There is no ordering to choose. The interaction $(s_A, g, s_B)$
is a single 3-body product. If it is non-associative, C branches — the
ordering ambiguity IS the branching. The graph engine spawns both orderings
as separate future nodes. This is fully deterministic; no tie-breaking rule
is needed.

### Attack Vector 3: Exponential branching blowup

*Each non-associative step doubles the tree. How does this terminate?*

**Answer.** Termination is guaranteed by the finite state space: there are
only $7^3 = 343$ possible three-quark color assignments, so the branching
tree must revisit a state within $343$ steps. The singlet recurrence
condition further restricts the state space to the subset where each quark
occupies one Witt pair. Whether the **minimum-cost** branch returns within
a tractable number of steps is the empirical question the simulation answers.

### Attack Vector 4: The factor of 2 cost for non-associative interactions
is still a "free parameter"

*You claim the non-associative cost is exactly 2, but why not 3 (spawning
and recording two nodes) or 4 (also recording the associator)?*

**Answer.** The cost is the number of complete product-tree evaluations
required to produce all valid outputs. There are exactly 2 binary bracketings
of 3 elements; evaluating them costs 2 units by the "1 evaluation = 1 tick"
Prime Directive. The spawning and recording of nodes are topological bookkeeping
(structural overhead), not algebraic evaluations. Algebraic evaluations are
the irreducible operations; the cost counts only those.

---

## 7. Implementation Checklist

**Before `calc/mass_drag.py` can produce a correct result, resolve:**

- [x] CONVENTIONS.md sign table and Fano triples (locked)
- [x] `is_fano_collinear` / `triggers` function (uses `FANO_CYCLES` from `conftest.py`)
- [x] Node and Edge data structures (defined in §2 above)
- [x] `update_step` algorithm (defined in §3.3 above)
- [ ] **Gluon assignment table** — lock $g_{12}, g_{23}, g_{31}$ in RFC-007 §3.2
- [ ] **Electron cycle length** $C_e$ — compute before calculating the ratio
- [ ] **Branch merging rule** — confirm minimum-cost rule (§5.2)

---

*Author scratchpad: The gluon assignment (§5.1) is the next concrete task.
It requires ~30 lines of Python to enumerate all candidate gluons and check
the 3-body associativity for each (src_state, g_candidate, dst_state)
combination. The result will determine whether the proton routing step
triggers non-associativity at all 3 hops, 2 of 3, 1 of 3, or 0 of 3.
This single calculation will either validate or immediately falsify the
COG mass mechanism.*
