# Algebraic and Sign Conventions

**Status:** Locked
**Scope:** Universal — applies to ALL Lean and Python code in this repository.
**Convention family:** Furey (literature-matched)

**WARNING: Do not modify the directed triples, sign tensor, Witt basis pairings, or vacuum axis defined in this file without explicit human approval. All Lean definitions and Python constants must agree with these values exactly. Changing a single sign will silently break alternativity proofs, gauge group derivations, and fermion state assignments downstream.**

---

## 1. Octonionic Basis

The octonion algebra $\mathbb{O}$ has basis $\{e_0, e_1, e_2, e_3, e_4, e_5, e_6, e_7\}$ where $e_0 = 1$ is the real identity.

Properties of the identity:
- $e_0 \cdot e_i = e_i \cdot e_0 = e_i$ for all $i$
- $e_i \cdot e_i = -e_0$ for $i = 1, \dots, 7$

---

## 2. The Seven Directed Lines (Source of Truth)

The multiplication of imaginary units is defined by $e_i \cdot e_j = \varepsilon_{ijk}\, e_k$. The totally antisymmetric structure constant $\varepsilon_{ijk} = +1$ for exactly the following seven directed cyclic triples:

| Line # | Directed triple $(i, j, k)$ | Meaning |
|--------|----------------------------|---------|
| L1 | $(1, 2, 3)$ | $e_1 e_2 = +e_3$ |
| L2 | $(1, 4, 5)$ | $e_1 e_4 = +e_5$ |
| L3 | $(1, 7, 6)$ | $e_1 e_7 = +e_6$ |
| L4 | $(2, 4, 6)$ | $e_2 e_4 = +e_6$ |
| L5 | $(2, 5, 7)$ | $e_2 e_5 = +e_7$ |
| L6 | $(3, 4, 7)$ | $e_3 e_4 = +e_7$ |
| L7 | $(3, 6, 5)$ | $e_3 e_6 = +e_5$ |

### Cyclic and anti-cyclic rules

If $(i, j, k)$ is a directed triple with $\varepsilon_{ijk} = +1$, then:
- **Cyclic:** $e_i e_j = +e_k$, $\quad e_j e_k = +e_i$, $\quad e_k e_i = +e_j$
- **Anti-cyclic:** $e_j e_i = -e_k$, $\quad e_k e_j = -e_i$, $\quad e_i e_k = -e_j$

### The full 7x7 sign table (generated from the triples above)

For $i, j \in \{1, \dots, 7\}$, $i \neq j$: find the unique line containing both $i$ and $j$, read the cyclic order, and apply the sign rule.

```
       e1    e2    e3    e4    e5    e6    e7
e1 |  -1   +e3   -e2   +e5   -e4   -e7   +e6
e2 | -e3    -1   +e1   +e6   +e7   -e4   -e5
e3 | +e2   -e1    -1   +e7   -e6   +e5   -e4
e4 | -e5   -e6   -e7    -1   +e1   +e2   +e3
e5 | +e4   -e7   +e6   -e1    -1   -e3   +e2
e6 | +e7   +e4   -e5   -e2   +e3    -1   -e1
e7 | -e6   +e5   +e4   -e3   -e2   +e1    -1
```

The diagonal entries represent $e_i^2 = -1$ (i.e., the result is $-e_0$).

---

## 3. Quaternionic Subalgebras

Each directed line generates an associative quaternionic subalgebra $\mathbb{H} \subset \mathbb{O}$. For example, line L1 gives $\{e_0, e_1, e_2, e_3\} \cong \{1, i, j, k\}$.

**Key fact for HACG:** Any two imaginary units on the *same* line associate: $(e_i e_j) e_k = e_i (e_j e_k)$. Any two imaginary units on *different* lines that do not share a common third line are non-associative. Since every triple of distinct imaginary units from $\{e_1, \dots, e_7\}$ either lies on a single Fano line (associative) or does not (non-associative), and there are $\binom{7}{3} = 35$ triples of which exactly 7 are collinear, exactly **28 out of 35 unordered triples are non-associative**.

---

## 4. The Complex Octonions ($\mathbb{C} \otimes \mathbb{O}$)

Introduce a commuting complex imaginary unit $i$ satisfying $i^2 = -1$.

**Commutation rule:** The complex unit $i$ commutes with all octonionic units:
$$i \cdot e_j = e_j \cdot i \quad \text{for all } j = 0, 1, \dots, 7$$

The algebra $\mathbb{C} \otimes \mathbb{O}$ has complex dimension 8 (real dimension 16). An element is:
$$z = \sum_{j=0}^{7} (a_j + i\, b_j)\, e_j, \quad a_j, b_j \in \mathbb{Z} \text{ (or } \mathbb{Q}\text{)}$$

---

## 5. The Witt Basis (Ladder Operators)

### 5.1 Symmetry-breaking axis

We designate $e_7$ as the symmetry-breaking axis (the sterile vacuum direction). This choice aligns with Furey's convention and isolates $e_7$ from the three color planes.

### 5.2 Color plane pairings

The six remaining imaginary units pair into three complex color planes, determined by the three Fano lines through the vacuum axis $e_7$. The annihilation condition $\alpha_j \omega = 0$ requires $e_a \cdot e_7 = -e_b$ and $e_b \cdot e_7 = +e_a$:

| Color index $j$ | Pair $(e_a, e_b)$ | Fano line through $e_7$ | Verification |
|-----------------|-------------------|------------------------|--------------|
| 1 | $(e_6, e_1)$ | L3: $(1, 7, 6)$ | $e_6 e_7 = -e_1$, $e_1 e_7 = +e_6$ |
| 2 | $(e_2, e_5)$ | L5: $(2, 5, 7)$ | $e_2 e_7 = -e_5$, $e_5 e_7 = +e_2$ |
| 3 | $(e_3, e_4)$ | L6: $(3, 4, 7)$ | $e_3 e_7 = -e_4$, $e_4 e_7 = +e_3$ |

### 5.3 Lowering (annihilation) operators

$$\alpha_1 = \tfrac{1}{2}(e_6 + i\, e_1)$$
$$\alpha_2 = \tfrac{1}{2}(e_2 + i\, e_5)$$
$$\alpha_3 = \tfrac{1}{2}(e_3 + i\, e_4)$$

### 5.4 Raising (creation) operators

$$\alpha_j^\dagger = -\frac{1}{2}(e_a - i\, e_b) = \frac{1}{2}(-e_a + i\, e_b)$$

*Correction (2026-02-21): The original definition $\frac{1}{2}(e_a - i e_b)$ was just the complex conjugate. The Hermitian adjoint in the octonion algebra includes octonion conjugation ($e_a^\dagger = -e_a$), yielding the negative sign required to satisfy $\{\alpha_j, \alpha_j^\dagger\} = +1$.*

### 5.5 Clifford relations

These six operators satisfy the $\mathbb{C}\ell(6)$ anticommutation relations:
$$\{\alpha_j,\, \alpha_k^\dagger\} = \delta_{jk}, \qquad \{\alpha_j,\, \alpha_k\} = 0, \qquad \{\alpha_j^\dagger,\, \alpha_k^\dagger\} = 0$$

---

## 6. The Algebraic Vacuum State

The sterile vacuum (Fock vacuum) is defined using the symmetry-breaking axis $e_7$:

$$\omega = \tfrac{1}{2}(1 + i\, e_7)$$

### Properties:
1. **Idempotent:** $\omega^2 = \omega$ *(proved in Lean: `vacuum_idempotent_doubled`)*
2. **Annihilated by all lowering operators:** $\alpha_j\, \omega = 0$ for $j = 1, 2, 3$ *(proved in Lean: `wittLower_annihilates_vacuum`)*
3. **The sterile neutrino** is identified with $\omega$ itself

### Fermion state construction

One-particle states are built by applying raising operators to the vacuum:
- $\alpha_j^\dagger\, \omega$ — a quark of color $j$
- $\alpha_j^\dagger \alpha_k^\dagger\, \omega$ — an anti-quark (two creation operators)
- $\alpha_1^\dagger \alpha_2^\dagger \alpha_3^\dagger\, \omega$ — the charged lepton (all three colors)

---

## 7. Identifier Mapping (Literature → Code)

| Physics notation | Lean identifier | Python identifier | Notes |
|-----------------|----------------|------------------|-------|
| $e_0, \dots, e_7$ | `Octonion.basis i` | `Octonion.basis(i)` | $i$ : `Fin 8` (Lean) / `int` (Python) |
| Directed triples | `fanoCycles` | `FANO_CYCLES` | `List (Fin 7 × Fin 7 × Fin 7)` / `list[tuple[int,int,int]]` |
| $\varepsilon_{ijk}$ | `fanoSign i j` | `fano_sign(i, j)` | Returns `Int` / `int` in $\{-1, 0, +1\}$ |
| $e_i \cdot e_j \to (\text{sign}, k)$ | `fanoBasisMul i j` | `basis_mul(i, j)` | Returns `(Fin 7 × Int)` / `tuple[int, int]` |
| $\alpha_j$ | `wittLower j` | `witt_lower(j)` | $j$ : `Fin 3` / `int` in $\{0,1,2\}$ |
| $\alpha_j^\dagger$ | `wittRaise j` | `witt_raise(j)` | $j$ : `Fin 3` / `int` in $\{0,1,2\}$ |
| $\omega$ | `vacuum` | `VACUUM` | The idempotent $\frac{1}{2}(1 + i e_7)$ |
| $i$ (complex unit) | `FormalComplex.I` | `1j` (Python native) | Commutes with all $e_j$ |

---

## 8. Bitwise XOR Optimization (Deferred)

For future high-performance computations, the Furey basis can be converted to a Cayley-Dickson (bitwise XOR) basis via a permutation matrix $P$. This is **not used in any current code** but is documented here for future reference.

### Translation contract (to be proved in Lean when needed):
```
theorem furey_xor_equiv (x y : Octonion R) :
  fureyMul x y = P⁻¹ (xorMul (P x) (P y))
```

The permutation $P$ maps Furey indices to XOR indices. Its exact values will be determined and locked when the optimization is implemented. Until then, all code uses the Furey basis directly.

---

## 9. Verification Checklist

Before any Lean file or Python module touching octonion multiplication is merged, verify:

- [ ] The 7 directed triples match Section 2 exactly
- [ ] The sign table matches Section 2 exactly
- [ ] Witt basis pairings match Section 5.2: $(e_6, e_1)$, $(e_2, e_5)$, $(e_3, e_4)$
- [ ] Vacuum uses $e_7$: $\omega = \frac{1}{2}(1 + i\, e_7)$
- [ ] Lean identifiers match Section 7
- [ ] Python identifiers match Section 7
- [ ] `alpha_j * vacuum = 0` passes for $j = 1, 2, 3$
- [ ] `vacuum * vacuum = vacuum` passes
- [ ] No forbidden Mathlib imports (CI linter passes: no `Analysis`, `Topology`, `MeasureTheory`, `Manifold`, `Data.Real`, or `Data.Complex.Basic`)
