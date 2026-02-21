# COG (Causal Octonion Graph) Research Plan

**Status:** Active
**Created:** 2026-02-21
**Scope:** End-to-end roadmap from current stubs to a formally verified causal graph engine

---

## 0. Current State

The repository has build infrastructure (Lean 4.28.0, CI, lakefile) and conceptual documentation (CLAUDE.md, RFC-001) but no substantive implementation. The Lean library contains only a placeholder. No Python code, no YAML claims, and no manuscript content exist yet.

---

## Phase 1 — Algebraic Foundations (Lean)

Establish the discrete algebraic primitives that everything else depends on. No Mathlib continuous imports (`Real`, `Manifold`, `MeasureTheory`) are permitted.

| # | Deliverable | File | Description |
|---|-------------|------|-------------|
| 1.1 | Fano plane as `Fin 7` structure | `CausalGraphTheory/Fano.lean` | Define the 7 points and 7 lines. Prove each line has exactly 3 points, each point lies on exactly 3 lines. Encode the multiplication table. |
| 1.2 | Octonion algebra over a discrete base | `CausalGraphTheory/Octonion.lean` | Define `Octonion` as an 8-tuple with multiplication driven by the Fano signs. Prove alternativity: `x * (x * y) = (x * x) * y` and `(y * x) * x = y * (x * x)`. Prove non-associativity for a generic triple. |
| 1.3 | Complex-octonion tensor product | `CausalGraphTheory/ComplexOctonion.lean` | Define `CO := Complex × Octonion` with the tensor product algebra structure. Identify the Witt basis (ladder operators) as explicit elements. |
| 1.4 | Subalgebra detection | `CausalGraphTheory/Subalgebra.lean` | Given a set of octonion basis elements, decide whether they span an associative subalgebra (`ℂ` or `ℍ` inside `𝕆`). This is the predicate that separates "timeless" batching from "ticking." |

**Exit criterion:** `lake build` passes with all four files. Each file has at least one non-trivial `theorem` that type-checks.

---

## Phase 2 — Graph State & Dynamics (Lean)

Formalize the causal graph itself, as specified in RFC-001.

| # | Deliverable | File | Description |
|---|-------------|------|-------------|
| 2.1 | Graph state type | `CausalGraphTheory/State.lean` | `inductive NodeLabel` over the `CO` representations (`V`, `S_plus`, `S_minus`). `structure CausalGraph` as a DAG with typed nodes and directed, operator-labeled edges. |
| 2.2 | Topological distance | `CausalGraphTheory/Distance.lean` | `def dist (G : CausalGraph) (a b : NodeId) : Option Nat` — shortest directed path length via edge-counting. Prove triangle inequality. No `ℝ`. |
| 2.3 | Associativity classifier | `CausalGraphTheory/Tick.lean` | For a node receiving multiple incoming edges, collect the operator basis elements and call the subalgebra detector from 1.4. Classify the interaction as `Batch` (associative, no tick) or `Tick` (non-associative, forced sequential evaluation). |
| 2.4 | Single-step update | `CausalGraphTheory/Update.lean` | `def step (G : CausalGraph) : CausalGraph` — scan all nodes, apply `Batch` or `Tick` classification, produce the successor graph. Prove the output is still a DAG (no cycles introduced). |

**Exit criterion:** A unit test constructs a 5-node graph, runs `step`, and the local tick counter increments only at the non-associative node.

---

## Phase 3 — Computational Validation (Python)

Mirror the Lean definitions with a runnable simulator for rapid experimentation.

| # | Deliverable | File | Description |
|---|-------------|------|-------------|
| 3.1 | Fano arithmetic module | `calc/fano.py` | NumPy multiplication table for `𝕆`. Functions: `multiply(a, b)`, `is_associative_triple(i, j, k)`. |
| 3.2 | Graph simulator | `calc/graph_sim.py` | NetworkX DAG. Nodes carry `CO` state vectors; edges carry operator labels. `update_step()` implements the Batch/Tick logic from 2.3. |
| 3.3 | Tick counter validation | `calc/test_tick.py` | pytest suite. Construct the same 5-node scenario as the Lean unit test. Assert tick counts match. |
| 3.4 | Fano penalty explorer | `calc/fano_penalty.py` | Sweep over all 480 valid `𝕆` multiplication sign conventions. For each, compute the number of non-associative triples encountered in a fixed graph topology. Output a histogram. |

**Exit criterion:** `pytest calc/` passes. Tick counts from Python agree with Lean definitions.

---

## Phase 4 — Physics Content

Derive physical observables from the graph engine.

| # | Deliverable | Depends on | Description |
|---|-------------|------------|-------------|
| 4.1 | Gauge group emergence | 1.3, 2.1 | Show that the automorphism group of the `CO` node algebra, restricted to the sterile vacuum stabilizer, is exactly `SU(3) × SU(2) × U(1)`. (Following Todorov 2022.) |
| 4.2 | Generation structure from triality | 1.2, 2.1 | The `V ↔ S_+ ↔ S_-` triality permutation maps one fermion generation to another. Formalize the triality automorphism and show it permutes three copies of the SM fermion content. |
| 4.3 | Mass as tick frequency | 2.3, 2.4 | Define `mass(n) := tick_count(n) / graph_depth` for a node `n` over a fixed evolution window. Compute the ratio for different node types and compare to Koide-formula predictions. |
| 4.4 | Hydrogen bound state | 4.1, 4.3 | Model a proton node (3 color-entangled quarks) and an electron node coupled by `U(1)` edges. Show the graph settles into a stable repeating motif — the discrete analogue of a bound state. |
| 4.5 | Deuterium bound state | 4.4 | Extend the hydrogen model with a neutron node (3 quarks, no net color/charge) bound to the proton via residual `SU(3)` (strong nuclear) edges. Verify the motif is stable and the neutron's tick frequency matches the expected mass ratio $m_n / m_p \approx 1.0014$. |
| 4.6 | Tritium bound state | 4.5 | Add a second neutron to deuterium. Test whether the graph reproduces tritium's known instability — the motif should exhibit a slow drift or eventual topology change corresponding to beta decay ($n \to p + e^- + \bar{\nu}_e$). |

**Exit criterion:** Each result is recorded as a YAML claim in `claims/` with status `proved` or `blocked`, and the blocking reason documented.

---

## Phase 5 — Red Team & Robustness

Stress-test the framework against known objections.

| # | Attack vector | Source | Resolution strategy |
|---|---------------|--------|---------------------|
| 5.1 | Lorentz covariance without a global clock | RFC-001 §4.3 | Show that the causal partial order on the DAG reproduces the light-cone structure. Two nodes are spacelike-separated iff neither is an ancestor of the other. |
| 5.2 | DAG race conditions | RFC-001 §4.3 | If two spacelike paths converge at node C, the result must be independent of evaluation order. This holds exactly when the incoming operators lie in an associative subalgebra — which is precisely the Batch case. If they don't, the Tick mechanism forces a unique binary tree. Prove no ambiguity remains. |
| 5.3 | Continuum limit | General | As graph density grows, do macroscopic observables converge to known continuum QFT predictions? Or does discreteness produce observable artifacts? |
| 5.4 | Anomaly cancellation | Todorov 2022 | Verify that the algebraic constraints from `CO` automatically cancel gauge anomalies (matching the 16-dim particle subspace structure). |

**Exit criterion:** Each attack has a dedicated `rfc/RFC-001_Objections.md` entry with status `resolved`, `open`, or `fatal`.

---

## Dependency Graph

```
Phase 1 (Algebra)
  ├── 1.1 Fano
  ├── 1.2 Octonion ← 1.1
  ├── 1.3 ComplexOctonion ← 1.2
  └── 1.4 Subalgebra ← 1.1

Phase 2 (Graph) ← Phase 1
  ├── 2.1 State ← 1.3
  ├── 2.2 Distance ← 2.1
  ├── 2.3 Tick ← 2.1, 1.4
  └── 2.4 Update ← 2.1, 2.2, 2.3

Phase 3 (Python) ← Phase 1 (conceptually)
  ├── 3.1 fano.py ← 1.1
  ├── 3.2 graph_sim.py ← 3.1
  ├── 3.3 test_tick.py ← 3.2
  └── 3.4 fano_penalty.py ← 3.1

Phase 4 (Physics) ← Phase 2
  ├── 4.1 Gauge groups ← 1.3, 2.1
  ├── 4.2 Generations ← 1.2, 2.1
  ├── 4.3 Mass ← 2.3, 2.4
  ├── 4.4 Hydrogen ← 4.1, 4.3
  ├── 4.5 Deuterium ← 4.4
  └── 4.6 Tritium ← 4.5

Phase 5 (Red Team) ← Phase 2, Phase 4
```

---

## Immediate Next Actions

1. **Start with 1.1** — formalize the Fano plane in Lean. This is the irreducible combinatorial kernel that everything else references.
2. **In parallel, start 3.1** — the Python Fano module can be built independently and used for rapid experimentation while Lean proofs are in progress.
3. **Create the first YAML claim** in `claims/` for the Fano plane properties (7 points, 7 lines, 3-per-line, 3-lines-per-point) so the workflow loop has something to track.
