# RFC-004: Particle Motifs (Microstates)

**Status:** Draft
**Created:** 2026-02-22
**Purpose:** Define the graph-theoretic representation of Standard Model particles for Python simulation.

---

## 1. Core Principles

1.  **Motif = Subgraph:** A particle is not a single node. It is a **stable, repeating subgraph** (motif) embedded in the larger causal graph.
2.  **Stability:** A motif is "stable" if the update rule `step(G)` produces a successor motif that is isomorphic (up to translation in the DAG).
3.  **Interaction:** Motifs interact by exchanging edges (force carriers).

---

## 2. Fundamental Motifs

### 2.1 The Sterile Vacuum ($\nu_R$)

*   **Node Count:** 1
*   **Node Label:** `vacuum` (represents the idempotent $\omega = \frac{1}{2}(1 + i e_7)$).
*   **Internal Edges:** None.
*   **External Edges:** None (sterile).
*   **Function:** Background "spacetime points" that can be excited into matter.

### 2.2 The Electron ($e^-$)

*   **Node Count:** 1 (fundamental lepton).
*   **Node Label:** `S_minus` (represents the algebraic state $\Psi_e = \alpha_1^\dagger \alpha_2^\dagger \alpha_3^\dagger \omega$).
*   **Charge:** -1 (electric).
*   **Color:** Neutral (singlet).
*   **Internal Edges:** None.
*   **External Edges:** Emits/absorbs `U1` (photon) edges to other charged nodes.

### 2.3 The Quark ($u, d$)

*   **Node Count:** 1.
*   **Node Label:** `S_plus` (represents algebraic states like $\Psi_u = \alpha_1^\dagger \omega$, $\Psi_d = \alpha_2^\dagger \alpha_3^\dagger \omega$).
*   **Charge:** +2/3 or -1/3.
*   **Color:** Red, Green, or Blue (triplet).
*   **Constraint:** Quarks cannot exist in isolation (confinement). They must be part of a color-neutral composite motif (meson or baryon).

---

## 3. Composite Motifs (Hadrons)

### 3.1 The Proton ($p^+$)

*   **Composition:** 3 Quark Nodes ($u, u, d$).
*   **Binding:** Strong force (Gluon edges).
*   **Structure:**
    *   Nodes: $N_1(u), N_2(u), N_3(d)$.
    *   Edges: A cycle of `SU3` exchange edges $N_1 \to N_2 \to N_3 \to N_1$.
    *   Algebra: The octonionic multiplication of the three color states must yield a real (associative) scalar, ensuring stability.
*   **Stability Condition:** The update rule must preserve this 3-cycle. If a gluon edge breaks, the motif decays.

### 3.2 The Neutron ($n^0$)

*   **Composition:** 3 Quark Nodes ($u, d, d$).
*   **Binding:** Strong force (Gluon edges).
*   **Structure:** Similar to proton but with different quark flavors.
*   **Instability:** The neutron motif is **metastable**.
    *   Topology Change: One $d$-quark node ($N_3$) can emit a `W_minus` edge to a vacuum node.
    *   Decay Product: $N_3 \to N_3'(u) + N_e(e^-) + N_{\bar{\nu}}(\bar{\nu}_e)$.
    *   Result: $n^0 \to p^+ + e^- + \bar{\nu}_e$.

---

## 4. Atomic Motifs

### 4.1 Hydrogen ($^1H$)

*   **Composition:** 1 Proton Motif + 1 Electron Motif.
*   **Binding:** Electromagnetic (`U1`) edges.
*   **Structure:**
    *   Proton subgraph (3 nodes).
    *   Electron node (1 node).
    *   Photon exchange: Bi-directional `U1` edges between the electron and the proton's quark nodes.
*   **Tick Synchronization:** The electron's tick frequency relative to the proton's must match the mass ratio $m_e / m_p \approx 1/1836$ for the bound state to be stable.

---

## 5. Implementation Strategy

1.  **Python Class:** `calc/tritium_microstate.py` will define these motifs as `NetworkX` graph generators.
    *   `def create_proton(start_id: int) -> nx.DiGraph`
    *   `def create_electron(start_id: int) -> nx.DiGraph`
2.  **Simulation:** `calc/graph_sim.py` will load these subgraphs into the main `CausalGraph` and run the `update_step`.
3.  **Analysis:** Detect if the subgraph topology persists or breaks apart.
