# Master Implementation Plan: Literature → Lean + Python

**Status:** Draft
**Created:** 2026-02-21
**Prerequisite reading:** `rfc/RESEARCH_PLAN.md`, `sources/furey_and_related_literature.md`

---

## 0. Guiding Principles

1. **No continuum.** Every Lean file imports only discrete algebra from Mathlib (rings, finite groups, combinatorics, `CliffordAlgebra`). Importing `Real`, `Manifold`, `MeasureTheory`, or `Topology` is forbidden.
2. **One concept per file.** Each `.lean` file proves one tightly scoped algebraic fact. Each `.py` file implements one computational module with its own test.
3. **Claims drive work.** Every theorem or computation is tracked by a YAML file in `claims/`. Status flows: `stub → in_progress → proved | blocked`.
4. **Python mirrors Lean.** The Python simulator in `calc/` must produce numerically identical results to the Lean definitions. Discrepancies are bugs.
5. **Halt on confusion.** If a proof is stuck for more than ~30 minutes of tactic exploration, mark the claim `blocked` with a note explaining the obstacle. Do not brute-force.
6. **Convention lock is absolute.** `rfc/CONVENTIONS.md` is canonical for directed triples, sign tensor, Witt pairings, and vacuum axis. If any RFC text conflicts, `CONVENTIONS.md` wins.

---

## 1. Repository Layout (Target State)

```
CausalGraphTheory/
├── lakefile.toml                     # Lean build config
├── lean-toolchain                    # leanprover/lean4:v4.28.0
├── CausalGraphTheory.lean            # Root import file
├── CausalGraphTheory/
│   ├── Basic.lean                    # Common utilities, notation
│   │
│   │── # ── Phase 1: Algebraic Foundations ──
│   ├── Fano.lean                     # 1.1  Fano plane combinatorics
│   ├── FanoMul.lean                  # 1.1b Sign table for octonion mult
│   ├── Octonion.lean                 # 1.2  Octonion algebra (8-tuple)
│   ├── OctonionAlt.lean             # 1.2b Alternativity proofs
│   ├── OctonionNonAssoc.lean        # 1.2c Non-associativity witness
│   ├── ComplexOctonion.lean          # 1.3  C⊗O tensor product
│   ├── WittBasis.lean                # 1.3b Ladder operators in C⊗O
│   ├── SubalgebraDetect.lean         # 1.4  Associative subalgebra predicate
│   │
│   │── # ── Phase 2: Graph State & Dynamics ──
│   ├── State.lean                    # 2.1  CausalGraph, NodeLabel, Edge
│   ├── Distance.lean                 # 2.2  Topological distance (Nat)
│   ├── Tick.lean                     # 2.3  Batch vs Tick classifier
│   ├── Update.lean                   # 2.4  Single-step graph evolution
│   ├── DAGProof.lean                 # 2.4b Prove step preserves acyclicity
│   │
│   │── # ── Phase 4: Physics Content ──
│   ├── GaugeGroup.lean               # 4.1  SM gauge group from CO auts
│   ├── Triality.lean                 # 4.2  SO(8) triality automorphism
│   ├── ThreeGenerations.lean         # 4.2b V ↔ S+ ↔ S- permutation
│   ├── Mass.lean                     # 4.3  mass := tick_count / depth
│   │
│   │── # ── Phase 5: Red Team ──
│   ├── CausalOrder.lean              # 5.1  Partial order → light cones
│   ├── RaceCondition.lean            # 5.2  Confluence proof
│   │
│   │── # ── Infrastructure ──
│   └── ExportOracle.lean             # Writes computed values to JSON for Python oracle
│
├── calc/                             # Python computational layer
│   ├── __init__.py
│   ├── conftest.py                   # Shared pytest fixtures
│   │
│   │── # ── Phase 3: Computational Validation ──
│   ├── fano.py                       # 3.1  Fano plane + O multiplication
│   ├── octonion.py                   # 3.1b Octonion class with full algebra
│   ├── complex_octonion.py           # 3.1c C⊗O with Witt basis
│   ├── graph_sim.py                  # 3.2  NetworkX DAG simulator
│   ├── test_fano.py                  # 3.1  Tests for Fano/octonion
│   ├── test_tick.py                  # 3.3  Tick counter validation
│   ├── fano_penalty.py               # 3.4  Sign convention sweep
│   │
│   │── # ── Phase 4: Physics Numerics ──
│   ├── gauge_check.py                # 4.1  Numerical gauge group verify
│   ├── koide.py                      # 4.3  Koide formula from tick ratios
│   ├── mass_ratios.py                # 4.3  Mass ratio predictions
│   ├── hydrogen_sim.py               # 4.4  Hydrogen bound state motif
│   ├── deuterium_sim.py              # 4.5  Deuterium (p+n) bound state
│   ├── tritium_sim.py                # 4.6  Tritium (p+2n) + beta decay
│   └── test_physics.py               # 4.*  Tests for physics predictions
│
├── claims/                           # YAML knowledge graph
│   ├── fano_plane.yml
│   ├── octonion_alternativity.yml
│   ├── octonion_nonassoc.yml
│   ├── co_witt_basis.yml
│   ├── subalgebra_detection.yml
│   ├── dag_distance_triangle.yml
│   ├── tick_classification.yml
│   ├── step_preserves_dag.yml
│   ├── gauge_group_emergence.yml
│   ├── triality_three_gens.yml
│   ├── mass_tick_frequency.yml
│   └── ...
│
├── sources/                          # Literature surveys (read-only reference)
├── rfc/                              # Design documents
└── manuscript/                       # LaTeX textbook (future)
```

---

## 2. Mathlib Strategy

### 2.1 What We Import

Lean 4.28.0 with mathlib4 provides substantial discrete algebra. We use:

| Mathlib module | Purpose | Import path |
|---|---|---|
| `Fin`, `ZMod` | Finite types, modular arithmetic | `Mathlib.Data.Fin.*`, `Mathlib.Data.ZMod.*` |
| `Matrix` | Finite matrices over rings | `Mathlib.Data.Matrix.*` |
| `CliffordAlgebra` | Universal Clifford algebra construction | `Mathlib.LinearAlgebra.CliffordAlgebra.*` |
| `QuadraticForm` | Quadratic forms (input to Clifford) | `Mathlib.LinearAlgebra.QuadraticForm.*` |
| `Finset`, `Fintype` | Finite sets, decidable membership | `Mathlib.Data.Finset.*` |
| `GroupTheory` | Finite groups, subgroups, actions | `Mathlib.GroupTheory.*` |
| `RingTheory` | Ring/algebra structure | `Mathlib.RingTheory.*` |
| `Combinatorics` | Incidence structures, designs | `Mathlib.Combinatorics.*` |
| `Graph` | Simple graphs (if available) | `Mathlib.Combinatorics.SimpleGraph.*` |
| `Order` | Partial orders, lattices | `Mathlib.Order.*` |

### 2.2 What We Never Import

Any module whose type signature mentions `ℝ`, smooth structures, or measure theory:

- `Mathlib.Analysis.*`
- `Mathlib.Topology.*` (except finite/discrete topology if needed)
- `Mathlib.MeasureTheory.*`
- `Mathlib.Geometry.Manifold.*`

### 2.3 Mathlib vs Hand-Rolled: Decision Points

| Structure | Mathlib? | Rationale |
|---|---|---|
| Fano plane (incidence) | **Hand-rolled** | 7 points, 7 lines — simpler as `Fin 7` with explicit `Decidable` proofs than fitting into a general design theory framework |
| Octonion multiplication | **Hand-rolled** | Mathlib has no octonion type. We define it as `Fin 8 → R` with Fano-driven multiplication |
| Clifford algebra $\mathbb{C}\ell(n)$ | **Mathlib** | `CliffordAlgebra` exists and is well-maintained (Wieser & Song, LF1). Use it for $\mathbb{C}\ell(6)$, $\mathbb{C}\ell(8)$ |
| Quadratic forms | **Mathlib** | Input to `CliffordAlgebra`. Use `QuadraticForm.ofBilinForm` |
| Complex numbers | **Hand-rolled** | Use `ZMod 2` or a simple `inductive Complex` to avoid pulling in `ℝ` via Mathlib's `Complex` type |
| DAG / directed graph | **Hand-rolled** | Mathlib's `SimpleGraph` is undirected. We need `structure CausalGraph` with directed edges and node labels |
| Finite groups ($S_3$, $G_2$ subgroups) | **Mathlib** | `MulAction`, `Subgroup`, `Equiv.Perm` are available |
| Partial orders | **Mathlib** | `PartialOrder`, `Finset.sup`, topological sort |

### 2.4 Mathlib Dependency (Active)

Mathlib is now a project dependency. The `lakefile.toml` includes:

```toml
[[require]]
name = "mathlib"
scope = "leanprover-community"
version = "git#master"
```

After updating, run `lake exe cache get` to download prebuilt oleans (avoids multi-hour local compilation).

**Guardrails against continuum contamination:**

1. **CI Import Linter (hard gate):** `.github/workflows/lean_action_ci.yml` scans all `.lean` files for forbidden import patterns (`Mathlib.Analysis.*`, `Mathlib.Topology.*`, `Mathlib.MeasureTheory.*`, `Mathlib.Geometry.Manifold.*`, `Mathlib.Data.Real.*`, `Mathlib.Data.Complex.Basic`) and fails the build if any are found.
2. **Surgical imports only:** Always import the deepest leaf module needed (e.g., `import Mathlib.Tactic.Ring`), never a broad subtree.
3. **Dependency audit:** After adding any new Mathlib import, run `lake exe graph` and verify that no forbidden module appears in the transitive closure.
4. **Use `FormalComplex` not `Mathlib.Data.Complex.Basic`:** Mathlib's `Complex` type transitively depends on `ℝ`. Our `FormalComplex R` is parameterized over any `CommRing R` and stays purely discrete.

See CLAUDE.md §3 and GEMINI.md §3 for the full allowed/forbidden import lists.

---

## 3. Phase 1 — Algebraic Foundations: Detailed Specs

### 3.1 Fano Plane (`Fano.lean`, `FanoMul.lean`)

**Literature source:** All papers (universal); Baez BH2 §4 for definitions.

**Lean definitions:**
```
-- Points and lines as Fin 7
abbrev FanoPoint := Fin 7
abbrev FanoLine  := Fin 7

-- The 7 lines, each a triple of points
-- Canonical directed triples from rfc/CONVENTIONS.md §2 (1-indexed):
-- (1,2,3), (1,4,5), (1,7,6), (2,4,6), (2,5,7), (3,4,7), (3,6,5)
def fanoLines : Fin 7 → Finset (Fin 7)

-- Incidence predicate
def incident (p : FanoPoint) (l : FanoLine) : Prop := p ∈ fanoLines l
```

**Theorems to prove:**
1. `each_line_has_three_points`: `∀ l, (fanoLines l).card = 3`
2. `each_point_on_three_lines`: `∀ p, (Finset.filter (incident p) Finset.univ).card = 3`
3. `two_points_determine_line`: `∀ p q, p ≠ q → ∃! l, incident p l ∧ incident q l`
4. `two_lines_meet_in_one_point`: `∀ l₁ l₂, l₁ ≠ l₂ → ∃! p, incident p l₁ ∧ incident p l₂`

**`FanoMul.lean` — Sign table:**

**Important:** The cyclic orientation of the 7 lines is notoriously easy to get wrong, which silently breaks alternativity proofs downstream. Define a single source-of-truth list of 7 **directed cyclic triples** (e.g., `(1,2,3)` means $e_1 e_2 = +e_3$, $e_2 e_3 = +e_1$, $e_3 e_1 = +e_2$, and reversals negate). Both Lean and Python must generate their full 7×7 sign/multiplication tables programmatically from this same list — never hardcode the 49 outcomes independently.

```
-- The 7 directed cyclic triples (source of truth)
def fanoCycles : Fin 7 → Fin 3 → Fin 7

-- Generated from fanoCycles, not hardcoded
-- ε(i,j) = +1 if (i,j) follows the arrow on line, -1 if against
def fanoSign : Fin 7 → Fin 7 → Int

-- Octonion multiplication of basis elements: eᵢ * eⱼ = ε(i,j) * eₖ
-- where k is the third point on the line through i and j
def fanoBasisMul : Fin 7 → Fin 7 → Fin 7 × Int
```

**Claim file:** `claims/fano_plane.yml`

---

### 3.2 Octonion Algebra (`Octonion.lean`, `OctonionAlt.lean`, `OctonionNonAssoc.lean`)

**Literature source:** Baez BH2 §3–4; Furey F1 §2.

**Lean definitions:**
```
-- Octonion over a commutative ring R (initially R = ℤ or ℚ)
structure Octonion (R : Type*) [CommRing R] where
  re : R           -- real part (e₀ coefficient)
  im : Fin 7 → R   -- imaginary parts (e₁..e₇ coefficients)

-- Multiplication using Fano signs
instance [CommRing R] : Mul (Octonion R)

-- Conjugation: conj(a₀ + Σ aᵢeᵢ) = a₀ - Σ aᵢeᵢ
def Octonion.conj : Octonion R → Octonion R

-- Norm: N(x) = x * conj(x) (lands in R, the real part)
def Octonion.norm : Octonion R → R
```

**Theorems to prove:**
1. `left_alternative`: `∀ x y, x * (x * y) = (x * x) * y`
2. `right_alternative`: `∀ x y, (y * x) * x = y * (x * x)`
3. `flexible`: `∀ x y, x * (y * x) = (x * y) * x`  (follows from alternativity)
4. `moufang_identity`: any one of the three Moufang identities
5. `non_associative_witness`: `∃ a b c, a * (b * c) ≠ (a * b) * c`
6. `norm_multiplicative`: `∀ x y, norm (x * y) = norm x * norm y`
7. `conj_involution`: `∀ x, conj (conj x) = x`

**Proof strategy for alternativity:**
- Over `Fin 7` basis elements, alternativity reduces to checking a finite number of cases (7 × 7 = 49 pairs for left-alt, 49 for right-alt).
- Use `Decidable` instance + `decide` tactic, or enumerate via `Fin.cases`.
- For general elements, extend by bilinearity: if `L(x,y) := x*(x*y) - (x*x)*y` is zero on basis elements, and `L` is linear in `y` and satisfies `L(x+z, y) = L(x,y) + L(z,y) + ...`, then it's zero everywhere.
- **Fallback:** If the bilinearity argument is too complex, prove it for `Octonion ℤ` by explicit computation (each of the 8³ = 512 basis triples), then lift.

**Claim files:** `claims/octonion_alternativity.yml`, `claims/octonion_nonassoc.yml`

---

### 3.3 Complex Octonions & Witt Basis (`ComplexOctonion.lean`, `WittBasis.lean`)

**Literature source:** Furey F1, F2; Todorov T4.

**Key decision: How to represent ℂ without importing ℝ.**

Option A (recommended): Define a **formal complex ring** as pairs over ℤ (or any base ring):
```
structure FormalComplex (R : Type*) [CommRing R] where
  re : R
  im : R
-- with i² = -1 enforced in the ring structure
```

Option B: Use `ZMod` or `GaussianInt` from Mathlib if available without `ℝ` dependency.

**Lean definitions:**
```
-- Complex-Octonion algebra: (FormalComplex R) ⊗ (Octonion R)
-- Concretely: 16 real components = 8 complex components
structure ComplexOctonion (R : Type*) [CommRing R] where
  z : Fin 8 → FormalComplex R
  -- z[0] = real-octonion part, z[1..7] = imaginary-octonion parts

-- Witt basis: the 6 ladder operators aⱼ, aⱼ† (j = 1,2,3)
-- a_j = 1/2(e_a + i·e_b), a_j† = 1/2(e_a - i·e_b)
-- with canonical pairs (e6,e1), (e2,e5), (e3,e4); vacuum axis is e7.
def wittBasis (j : Fin 3) : ComplexOctonion R × ComplexOctonion R
```

**Theorems to prove:**
1. `witt_anticommute`: `aⱼ * aₖ + aₖ * aⱼ = 0` for `j ≠ k`
2. `witt_create_annihilate`: `aⱼ† * aⱼ + aⱼ * aⱼ† = 1` (Clifford relation)
3. `witt_generates_cl6`: The 6 generators produce all 64 basis elements of $\mathbb{C}\ell(6)$

**When to add Mathlib dependency:** This is the point where `CliffordAlgebra` from Mathlib becomes useful. We can verify that our hand-built $\mathbb{C}\ell(6)$ is isomorphic to `CliffordAlgebra Q` for the appropriate quadratic form `Q` on `(Fin 6 → R)`.

---

### 3.4 Subalgebra Detection (`SubalgebraDetect.lean`)

**Literature source:** RFC-001 §3.1–3.2; Furey F2 (ladder operator structure).

**Lean definitions:**
```
-- Given a set of octonion basis indices, are they associative?
def isAssociativeSubset (S : Finset (Fin 7)) : Bool :=
  S.card ≤ 2  -- Any two imaginary units generate ℍ (associative)
  -- More precisely: check all triples in S for associativity

-- The key predicate for the Tick mechanism
def batchable (ops : List (Fin 7)) : Prop :=
  ∀ i j k ∈ ops, (eᵢ * eⱼ) * eₖ = eᵢ * (eⱼ * eₖ)
```

**Theorems to prove:**
1. `complex_subalgebra_assoc`: Any single basis element spans an associative (ℂ-like) subalgebra
2. `quaternion_subalgebra_assoc`: Any Fano line triple generates an associative (ℍ-like) subalgebra
3. `cross_line_nonassoc`: Two basis elements from different, non-adjacent Fano lines are non-associative
4. `batchable_decidable`: `DecidablePred batchable` — the classifier is computable

---

## 4. Phase 2 — Graph State & Dynamics: Detailed Specs

### 4.1 Graph State (`State.lean`)

**Literature source:** RFC-001 §2; Causal set theory CS1, CS2.

```
-- Node labels: which CO representation
inductive NodeLabel where
  | V       : NodeLabel   -- vector representation
  | S_plus  : NodeLabel   -- positive spinor
  | S_minus : NodeLabel   -- negative spinor
  | vacuum  : NodeLabel   -- sterile vacuum v

-- Edge labels: gauge operator type
inductive EdgeLabel where
  | U1    : EdgeLabel     -- U(1) phase / photon
  | SU2   : Fin 3 → EdgeLabel  -- SU(2) weak / W,Z
  | SU3   : Fin 8 → EdgeLabel  -- SU(3) color / gluon

-- Node with its state data
structure Node where
  id       : Nat
  label    : NodeLabel
  state    : ComplexOctonion ℤ    -- the CO state vector
  tickCount : Nat                  -- local time counter

-- Directed edge
structure Edge where
  source : Nat
  target : Nat
  label  : EdgeLabel
  operator : ComplexOctonion ℤ    -- the algebraic operator carried

-- The full causal graph
structure CausalGraph where
  nodes : List Node
  edges : List Edge
  acyclic : <proof that the edge relation has no cycles>
```

**Design choice — acyclicity encoding:**
Option A (chosen): Carry a topological sort witness `topo : nodes → Fin n` with `∀ e ∈ edges, topo e.source < topo e.target`.
Option B (rejected): Use `Finset`-based reachability and prove `¬ reachable G n n` for all `n`.

**Option A is strongly preferred.** By baking the topological index into the `Node` structure and enforcing that edges only point from lower to higher indices, acyclicity is guaranteed by construction. This makes `step_preserves_acyclic` a trivial proof (new nodes get indices beyond all existing ones, new edges respect the ordering) rather than a deep topological theorem. The index is also reused by `Distance.lean` for BFS bounds.

---

### 4.2 Distance (`Distance.lean`)

```
-- Shortest directed path length (edge-counting)
def dist (G : CausalGraph) (a b : Nat) : Option Nat

-- Triangle inequality (when paths exist)
theorem dist_triangle (G : CausalGraph) (a b c : Nat) :
  ∀ dab dbc dac,
    dist G a b = some dab →
    dist G b c = some dbc →
    dist G a c = some dac →
    dac ≤ dab + dbc
```

**Proof strategy:** BFS on the DAG. Since the graph is finite and acyclic, `dist` terminates. Triangle inequality follows from path concatenation: any path a→b→c has length ≥ shortest path a→c.

---

### 4.3 Tick Classification (`Tick.lean`)

```
-- Collect all incoming operator basis elements at a node
def incomingBasis (G : CausalGraph) (n : Nat) : List (Fin 7)

-- Classify: Batch (associative) or Tick (non-associative)
inductive TickClass where
  | Batch : TickClass
  | Tick  : TickClass

def classify (G : CausalGraph) (n : Nat) : TickClass :=
  if batchable (incomingBasis G n) then .Batch else .Tick
```

---

### 4.4 Graph Update (`Update.lean`, `DAGProof.lean`)

```
-- Single-step evolution
def step (G : CausalGraph) : CausalGraph

-- Key invariant
theorem step_preserves_acyclic (G : CausalGraph) :
  G.acyclic → (step G).acyclic
```

**Proof strategy for acyclicity preservation:**
- `step` only adds nodes/edges with topological index strictly greater than all existing nodes.
- New edges only point from existing nodes to new nodes, or between new nodes in index order.
- Therefore no backward edges are introduced, preserving the DAG property.

**Determinism and information-conservation rule (canonical):**
- Parenthesization/evaluation order for each non-associative update is fixed by metadata already present in the initial microstate.
- `step` is deterministic and may only reveal or rearrange pre-encoded information; it does not introduce exogenous information.
- Detailed normative rules are specified in `rfc/RFC-002_Deterministic_Tick_Ordering.md`.

---

## 5. Phase 3 — Python Computational Layer: Detailed Specs

### 5.1 Technology Stack

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Runtime |
| NumPy | latest | Array operations, linear algebra |
| NetworkX | latest | DAG construction and traversal |
| pytest | latest | Test framework |
| matplotlib | latest | Visualization (histograms, graph plots) |

**`calc/requirements.txt`:**
```
numpy>=1.24
networkx>=3.0
pytest>=7.0
matplotlib>=3.7
```

### 5.2 Module Specifications

#### `calc/fano.py` — Fano Arithmetic

```python
# Canonical constants must be imported from calc/conftest.py
# (which is pinned to rfc/CONVENTIONS.md §2 and §5).
from calc.conftest import FANO_CYCLES, FANO_SIGN, FANO_THIRD

# Basis multiplication: e_i * e_j = sign * e_k
def basis_mul(i: int, j: int) -> tuple[int, int]:
    """Returns (k, sign) where e_i * e_j = sign * e_k."""

# Full octonion multiplication
def multiply(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Multiply two octonions (8-vectors). a[0] is real part."""

# Associator
def associator(a, b, c) -> np.ndarray:
    """[a,b,c] = (a*b)*c - a*(b*c)"""

# Test if a triple of basis indices is associative
def is_associative_triple(i: int, j: int, k: int) -> bool:
    """True iff (e_i * e_j) * e_k == e_i * (e_j * e_k)."""
```

#### `calc/octonion.py` — Octonion Class

```python
class Octonion:
    """Octonion with rational or float coefficients."""
    def __init__(self, coeffs: np.ndarray):  # length-8 vector
    def __mul__(self, other): ...
    def conjugate(self) -> 'Octonion': ...
    def norm(self) -> float: ...
    def is_alternative(self) -> bool:
        """Verify x*(x*y) == (x*x)*y for random y."""
```

#### `calc/complex_octonion.py` — C⊗O and Witt Basis

```python
class ComplexOctonion:
    """Element of C⊗O (16 real = 8 complex components)."""
    def __init__(self, z: np.ndarray):  # shape (8,) complex
    def witt_basis() -> list[tuple['ComplexOctonion', 'ComplexOctonion']]:
        """Return the 3 pairs (a_j, a_j†) of ladder operators."""
```

#### `calc/graph_sim.py` — DAG Simulator

```python
import networkx as nx

class CausalGraphSim:
    def __init__(self):
        self.G = nx.DiGraph()

    def add_node(self, node_id, label, state): ...
    def add_edge(self, src, tgt, operator): ...

    def incoming_basis(self, node_id) -> list[int]:
        """Collect Fano indices of incoming operators."""

    def classify(self, node_id) -> str:
        """Return 'Batch' or 'Tick'."""

    def update_step(self):
        """Scan all nodes, classify, increment tick counters."""

    def tick_count(self, node_id) -> int: ...
    def graph_depth(self) -> int: ...
```

#### `calc/fano_penalty.py` — Sign Convention Sweep

```python
def enumerate_sign_conventions() -> list[np.ndarray]:
    """Generate all 480 valid O multiplication sign tables."""

def penalty_score(signs: np.ndarray, topology: nx.DiGraph) -> int:
    """Count non-associative triples encountered in one update."""

def sweep(topology: nx.DiGraph) -> dict[int, int]:
    """Return histogram: penalty_score → count."""
```

---

## 6. Phase 4 — Physics Content: Translation Map

This section maps specific literature results to concrete Lean theorems and Python computations.

### 6.1 Gauge Group Emergence

**Source:** Todorov T4, Furey F2, Furey-Hughes FH1.

| Literature claim | Lean theorem | Python validation |
|---|---|---|
| Left-multiplication by $e_i$ generates $\mathfrak{g}_2 \subset \mathfrak{so}(7)$ | `g2_from_left_mul` | `calc/gauge_check.py`: verify dim = 14 |
| Sterile vacuum stabilizer in $G_{PS}$ = $G_{SM}$ | `sm_gauge_from_stabilizer` | Compute stabilizer subgroup numerically |
| $SU(3)_C$ from Witt basis ladder operators | `su3_from_witt` | Check 8 Gell-Mann matrices span the algebra |
| $\mathbb{Z}_6$ quotient in $G_{SM}$ | `z6_quotient` | Verify center of the representation |

### 6.2 Three Generations

**Source:** Furey F1, F3, FH3; Gresnigt G4; Boyle B5.

| Literature claim | Lean theorem | Python validation |
|---|---|---|
| $SO(8)$ triality permutes $V \leftrightarrow S_+ \leftrightarrow S_-$ | `triality_permutation` | Construct $3 \times 3$ permutation matrix on reps |
| Each image carries one SM generation | `triality_generation` | Decompose 48 states into 3 × 16 |
| Triality is outer automorphism of $Spin(8)$ | `triality_outer` | Verify it's not inner |

### 6.3 Mass as Tick Frequency

**Source:** RFC-001 §3.2; Koide K1, K2.

| Quantity | Lean definition | Python computation |
|---|---|---|
| `mass(n) := tick_count(n) / graph_depth` | `def mass` in `Mass.lean` | `CausalGraphSim.mass()` |
| Koide ratio $Q = (\sum m_i) / (\sum \sqrt{m_i})^2$ | `def koide_ratio` | `calc/koide.py` |
| Electron / muon / tau mass ratios | — | Run simulation, extract ratios |

**Key experiment:** Construct a graph with three nodes of different `NodeLabel` types (`V`, `S_+`, `S_-`), run the simulator for $N$ steps, measure their tick-count ratios, and compare to $m_e : m_\mu : m_\tau$.

### 6.4 Hydrogen Bound State

**Source:** RFC-001 §4.4.

| Component | Model |
|---|---|
| Proton | 3 nodes (quarks), color-entangled via $SU(3)$ edges |
| Electron | 1 node, coupled to proton via $U(1)$ edge |
| Bound state | Graph reaches a periodic motif (cycle in the state sequence) |

This is primarily a Python simulation task (`calc/hydrogen_sim.py`). The Lean side provides correctness guarantees on the update rule; the simulation explores whether stable motifs emerge.

### 6.5 Deuterium Bound State

**Source:** Extension of 6.4.

| Component | Model |
|---|---|
| Proton | Same as hydrogen (3 quarks, color-entangled) |
| Neutron | 3 quark nodes (udd), color-confined, net charge 0 |
| Nuclear binding | Residual $SU(3)$ edges between proton and neutron (the strong nuclear force as color-leakage at short topological distance) |
| Bound state | Graph motif must be stable; neutron tick frequency should give $m_n/m_p \approx 1.0014$ |

### 6.6 Tritium and Beta Decay

**Source:** Extension of 6.5.

| Component | Model |
|---|---|
| Tritium | Proton + 2 neutrons, bound by residual $SU(3)$ edges |
| Beta decay | Tritium is unstable ($t_{1/2} \approx 12.3$ yr). The graph motif should exhibit a topology change: one neutron's quark content rearranges ($d \to u + W^- \to u + e^- + \bar{\nu}_e$), converting the neutron node into a proton + electron + antineutrino emission. This is the first test of **dynamical topology change** in the graph engine. |
| Success criterion | The tritium motif is metastable (persists for many steps then decays), while deuterium is stable (no decay observed). |

---

## 7. Claims Workflow

### 7.1 YAML Schema

```yaml
# claims/fano_plane.yml
id: FANO-001
title: "Fano plane has 7 points and 7 lines"
statement: |
  The Fano plane PG(2,2) is the unique (7,7,3,3,1)-design:
  7 points, 7 lines, 3 points per line, 3 lines per point,
  any 2 points on exactly 1 line.
status: stub          # stub | in_progress | proved | blocked
lean_file: CausalGraphTheory/Fano.lean
lean_theorems:
  - each_line_has_three_points
  - each_point_on_three_lines
  - two_points_determine_line
python_test: calc/test_fano.py::test_fano_incidence
depends_on: []
literature:
  - "Baez BH2 §4"
  - "Furey F1 §2"
notes: ""
blocked_reason: ""
```

### 7.2 Status Transitions

```
stub ──→ in_progress ──→ proved
                    └──→ blocked ──→ in_progress (after unblock)
```

- `stub`: Claim defined, no code written.
- `in_progress`: Lean file and/or Python file created, work underway.
- `proved`: `lake build` passes, `python -m pytest -q` passes, all listed theorems type-check.
- `blocked`: A specific obstacle documented in `blocked_reason`.

---

## 8. Execution Order & Parallelism

### 8.1 Critical Path

```
1.1 Fano ──→ 1.2 Octonion ──→ 1.3 ComplexOctonion ──→ 2.1 State ──→ 2.3 Tick ──→ 2.4 Update
                                                                └──→ 2.2 Distance ─┘
```

Everything downstream depends on the Fano plane being correct. This is the single highest-priority deliverable.

### 8.2 Parallel Tracks

These can proceed simultaneously:

| Track | Items | Notes |
|---|---|---|
| **Lean algebra** | 1.1 → 1.2 → 1.3 → 1.4 | Sequential (each imports the previous) |
| **Python algebra** | 3.1 → 3.1b → 3.1c | Can start immediately, no Lean dependency |
| **Python graph** | 3.2 → 3.3 | Starts once 3.1 is done |
| **Claims setup** | YAML stubs for all Phase 1–2 claims | Can be created immediately |
| **Literature deep-read** | Download & annotate key papers (F1, F2, T4, BH2) | Ongoing reference |

### 8.3 Milestones

| Milestone | Definition of Done | Unlocks |
|---|---|---|
| **M1: Fano Done** | `Fano.lean` type-checks, `calc/test_fano.py` passes | All of Phase 1 |
| **M2: Octonions Done** | Alternativity + non-associativity proved in Lean, tested in Python | Phase 1.3, 1.4, 3.4 |
| **M3: Graph Engine** | `step` function works, DAG preservation proved | All of Phase 4 |
| **M4: One Generation** | $SU(3) \times SU(2) \times U(1)$ emerges from CO automorphisms | Phase 4.2, 4.4 |
| **M5: Three Generations** | Triality maps between generations formalized | Phase 4.3, 4.4 |
| **M6: Mass Predictions** | Tick ratios computed, Koide formula compared | Phase 5 |

---

## 9. Testing Strategy

### 9.1 Lean Testing

- **Type-checking is the test.** Every `theorem` in a `.lean` file is automatically verified by the Lean kernel.
- **`#eval` smoke tests:** Use `#eval` blocks to run small computations (e.g., multiply two specific octonions and print the result).
- **`example` blocks:** Quick sanity checks that specific values satisfy properties.
- **CI:** `lake build` on every push via `.github/workflows/lean_action_ci.yml`.

### 9.2 Python Testing

- **`python -m pytest -q`** runs all tests.
- **Property-based tests** (via `hypothesis` if useful): random octonion pairs satisfy alternativity.
- **Cross-validation:** For every Lean `#eval` that computes a specific value, there is a matching Python `assert`.
- **CI:** Python tests run in `.github/workflows/lean_action_ci.yml` via `python -m pytest -q`.

### 9.3 Lean ↔ Python Consistency (Automated Oracle)

Rather than manually maintaining hardcoded expected values (which silently drifts), automate the oracle:

1. **`ExportOracle.lean`** — A Lean script that `#eval`s key computed values (Fano multiplication table, sign array, alternativity witnesses, triality permutations, Koide ratios) and writes them to `calc/lean_outputs.json` via `IO.FS.writeFile`.
2. **`lake build` produces the JSON** — Add `ExportOracle` as a build target so `lake build` regenerates the oracle whenever Lean definitions change.
3. **`calc/conftest.py` loads the JSON** — A pytest fixture reads `lean_outputs.json` and makes the data available to all Python tests.
4. **Python tests assert against the oracle** — If the Lean math changes, the Python tests automatically fail until the Python logic is updated to match.

This closes the loop: a change to `Fano.lean` triggers a new JSON export, which triggers Python test failures if `calc/fano.py` is out of sync.

---

## 10. Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| **Alternativity proof too large** for `decide` tactic (512 cases) | Blocks M2 | Split into lemmas per basis pair; use `native_decide`; or prove by bilinearity argument |
| **Mathlib `CliffordAlgebra` pulls in `ℝ`** transitively | Violates Prime Directive | Run `lake exe graph` after adding Mathlib to visualize the full dependency tree. If `Mathlib.Topology` or `Mathlib.Analysis` appears transitively, hand-roll a minimal $\mathbb{C}\ell(6)$ from the already-proven `ComplexOctonion` base instead. |
| **Lean 4.28.0 ↔ Mathlib version mismatch** | Build failures | Pin Mathlib to a known-compatible commit |
| **Non-associativity witness too weak** | Claim is trivially true (just one triple) — not physically meaningful | Prove the count of non-associative unordered triples is exactly 28 out of C(7,3)=35 (the other 7 are the Fano lines), matching `rfc/CONVENTIONS.md` §3. |
| **Graph update `step` not well-defined** | Ambiguity in evaluation order | Require a canonical parenthesization schedule encoded in the initial microstate; Batch remains order-independent, Tick follows this predeclared schedule deterministically. |
| **Koide formula doesn't emerge from tick ratios** | Core physics prediction fails | Document as `blocked` with quantitative discrepancy. This is a legitimate falsification of the theory, not a code bug. |
| **DAG simulator too slow** for interesting graph sizes | Can't reach continuum-like behavior | Use sparse representations, limit to O(1000) nodes for Phase 3–4, note scaling limitations |

---

## 11. Immediate Action Items

**Start now (parallel):**

1. **Create `claims/fano_plane.yml`** — First YAML claim file, status `stub`.
2. **Create `CausalGraphTheory/Fano.lean`** — Define `fanoLines`, prove `each_line_has_three_points`.
3. **Create `calc/fano.py` + `calc/test_fano.py`** — Python Fano module with multiplication table and tests.

**Start after M1:**

4. **Create `CausalGraphTheory/Octonion.lean`** — 8-tuple definition with Fano-driven multiplication.
5. **Create `calc/octonion.py`** — Python octonion class.

**Infrastructure (anytime):**

6. **Add Python CI job** to `.github/workflows/`.
7. **Create `calc/requirements.txt`** and `calc/conftest.py`.
