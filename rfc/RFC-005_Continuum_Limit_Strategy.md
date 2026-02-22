# RFC-005: Continuum Limit Strategy

**Status:** Conceptual
**Created:** 2026-02-22
**Purpose:** Define the mathematical bridge between discrete graph updates and continuous field equations.

---

## 1. The Target: Causal Fermion Systems (CFS)

*   **Theory:** Finster (2016), arXiv:1605.04742.
*   **Space:** A measure space $(M, \mu)$ derived from a causal set.
*   **Dynamics:** Minimization of the **Causal Action**:
    $$S = \iint_{M \times M} \mathcal{L}(x, y) \, d\mu(x) \, d\mu(y)$$
*   **Lagrangian:** $\mathcal{L}(x, y) = |\xi(x, y)|^2$, where $\xi$ is the spectral projector.
*   **Continuum Limit Theorem:** As the number of points $N \to \infty$, the critical points of $S$ satisfy the classical Einstein-Maxwell-Dirac equations.

---

## 2. The COG Approach: Discrete Action Principle

We do not derive the continuum directly. Instead, we show that our discrete update rule **minimizes the discrete version of the Causal Action**.

### 2.1 The Discrete Action

Let $G = (V, E)$ be the causal graph. The action is sum over pairs:
$$S_G = \sum_{x, y \in V} \mathcal{L}_{disc}(x, y)$$

*   $\mathcal{L}_{disc}(x, y)$: A function of the algebraic "distance" or "overlap" between nodes $x$ and $y$.
*   **Hypothesis:** The "overlap" is the commutator/associator of their octonionic states. Nodes that commute/associate have low $\mathcal{L}$, nodes that don't have high $\mathcal{L}$.
*   **Minimization:** The update rule `step(G)` adds a new node $z$ such that it minimizes the action relative to its causal past $J^-(z)$.

### 2.2 Convergence Argument

1.  **Microscopic:** `step(G)` adds nodes locally to minimize algebraic conflict (non-associativity).
2.  **Macroscopic:** Over large regions, this local minimization approximates the global minimization of $\int \mathcal{L}$.
3.  **Result:** The large-scale graph looks like a manifold satisfying the vacuum Einstein equations $R_{\mu\nu} = 0$ (or with matter sources).

---

## 3. Implementation in Code

*   **Lean:** Define `causalAction (G : CausalGraph) : ℕ × ℕ` as a discrete proxy (a rational approximant `p/q`). **Do not use `Real` — it violates the Prime Directive.**
*   **Theorem:** `step_minimizes_action`: `step G` produces a graph with minimal action growth among all valid extensions.
*   **Validation:** Use `calc/fano_penalty.py` to numerically check if the generated graphs have lower "algebraic tension" than random graphs.

---

## 4. Key Literature Support

*   **Finster & Gresnigt (2024):** Explicitly connects octonionic vacuum symmetries to the CFS action.
*   **Wolfram (2020):** Shows that causal invariance in rewriting systems is equivalent to the Einstein equations in the continuum limit.

---

## 5. Next Steps

1.  Read Finster §4 in detail.
2.  Define `Lagrangian` in `CausalGraphTheory/Action.lean`.
3.  Prove `step_minimizes_action` in Phase 5.
