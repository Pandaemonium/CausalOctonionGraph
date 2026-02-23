# RFC-012: Two-Particle QED Vertex Simulation

**Status:** Draft — awaiting Python prototype in `calc/qed_scatter.py`
**Created:** 2026-02-22
**Module:** `calc/qed_scatter.py` (new), `CausalGraphTheory/Spinors.lean` (existing stubs)
**Dependencies:**
  - `rfc/CONVENTIONS.md` (locked Fano convention)
  - `rfc/RFC-001_Canonical_State_and_Rules.md` (node/edge/tick rules)
  - `rfc/RFC-009_Spinor_Representations_and_Triality_Overhead.md` (V vs S+ node types)
  - `rfc/RFC-011_XOR_Basis_Efficiency_and_Spinor_Cost.md` (N_tau = 14 derivation)
**Claims addressed:**
  - `LEPTON-001` (muon-to-electron mass ratio from orbit length)
  - `GEN-001` (three generations from triality)
**Upstream result:** `count_circuit_depth_greedy(H) = 14 = dim(G_2)` (2026-02-22)

---

## 1. Executive Summary

This RFC specifies two graph simulation systems that go beyond isolated
single-particle orbit counting. Both systems model a physical electromagnetic
scattering event — a photon emitted by one charged particle and absorbed by
another — inside a background vacuum lattice.

**System A — Møller scattering (e⁻ + e⁻):**
Both particles are Vector-rep (V) nodes. The incoming photon operator
$\mathcal{O}_\gamma = e_7$ is native to the V subalgebra. The interaction
vertex is evaluated by XOR hardware in **1 tick**.

**System B — Electron-muon scattering (e⁻ + μ⁻):**
The muon is a Spinor+ (S+) node. The incoming photon operator $e_7$
is V-rep machine code; the muon node is S+-rep hardware. The conflict
resolver must apply the McRae triality translation $H$ before the XOR
step, incurring $N_\tau = 14$ emulation ticks. Total cost: **15 ticks**.

**Key prediction:** the single-vertex cost ratio is $15 / 1 = 15$. The
full macroscopic mass ratio $m_\mu / m_e \approx 206.768$ is expected to
emerge from the orbit-return-time ratio $C_\mu / C_e$ when the vacuum
lattice propagation is included (see §6).

---

## 2. Physical Context

The two processes being modelled:

| Label | Process | QED name |
|-------|---------|----------|
| System A | $e^- + e^- \to e^- + e^-$ | Møller scattering |
| System B | $e^- + \mu^- \to e^- + \mu^-$ | Electron-muon elastic scattering |

In the Standard Model both are mediated by a single virtual photon at
leading order. In the COG graph:

- The photon is **not** a propagating node. It is a directed edge carrying
  the operator $\mathcal{O}_\gamma = e_7$ (the vacuum axis, the U(1)_EM
  generator in the Furey convention).
- Each particle is a node whose type (V or S+) determines the cost of
  absorbing the photon operator.
- The vacuum is a sea of nodes initialized to the idempotent state
  $\omega = \frac{1}{2}(1 + ie_7)$ which absorb and re-emit freely.

---

## 3. Graph Architecture

### 3.1 Node Types

| Symbol | Rep | Initial state | COG role |
|--------|-----|---------------|----------|
| `V`    | Vector | Witt nil-element $\alpha_j^\dagger \omega$ | Electron (generation 1) |
| `Sp`   | Spinor+ | Fano non-assoc state $\psi_\mu$ | Muon (generation 2) |
| `Vac`  | — | $\omega = \frac{1}{2}(1 + ie_7)$ | Vacuum lattice |

Each node carries:

```
Node : {
  id        : int        # strictly increasing (DAG topological order)
  rep       : str        # 'V', 'Sp', or 'Vac'
  state     : OctIdx     # octonion basis index {0..7}, 0 = scalar/vacuum
  tick_cost : int        # cumulative ticks consumed to reach this node
}
```

### 3.2 Edge Types (Boson Operators)

| Edge label | Operator | Carrier | Target rep |
|------------|----------|---------|------------|
| propagation | identity | free fermion | any |
| photon ($\gamma$) | $e_7$ | U(1)_EM boson | any |

An edge is a record `(src_id, dst_id, op: OctIdx)`.

### 3.3 Photon Operator Identity

The U(1)_EM generator in the Furey $\mathbb{C} \otimes \mathbb{O}$
decomposition is the **vacuum axis $e_7$**. Left-multiplication by $e_7$
on the octonion basis gives:

$$e_7 \cdot e_k = \epsilon_{7,k,m} \, e_m \quad (k \neq 0, 7)$$

where $\epsilon$ is the Furey sign tensor from `rfc/CONVENTIONS.md`. The
non-zero entries are determined by the three Fano lines through $e_7$:
$(e_7, e_1, e_6)$, $(e_7, e_2, e_5)$, $(e_7, e_3, e_4)$ — the three
Witt pairs. The XOR rule gives $e_7 \cdot e_k = \pm e_{7 \oplus k}$.

In hardware, this is a single XOR + sign lookup: **1 tick**.

### 3.4 Vacuum Lattice Initialization and Photon Routing

A 1D chain of $n$ vacuum nodes is inserted between the two particles:

```
t=0:  [E1] ─── [V_0] ─── [V_1] ─── ... ─── [V_{n-1}] ─── [E2]
```

All `V_i.state = 0` (scalar, representing $\omega = \frac{1}{2}(1+ie_7)$).
The vacuum nodes are **not** transparent to the photon. A photon emitted
by E1 traverses each vacuum node sequentially before reaching E2:

```
photon path:  E1 ──(e_7)──> V_0 ──(e_7)──> V_1 ──...──> V_{n-1} ──(e_7)──> E2
tick cost:          1           1          1         ...       1             1 or 15
```

Each vacuum-node hop costs **1 tick**. This is the definition of $c$:
the invariant speed of light equals one vacuum-node hop per graph tick.
See §4.3 for the algebraic justification and literature grounding.

---

## 4. The QED Vertex: Conflict Resolution

The physics of absorption happens at the **destination node** when it
receives two incoming edges simultaneously:

1. Its own free-propagation edge (from its previous self).
2. The incoming photon edge carrying $e_7$ from the emitter.

The Conflict Resolver (RFC-001 §4) sets a strict parenthesization: the
photon is absorbed first, then free propagation is applied. The cost
depends on the destination node's representation type.

### 4.1 System A — V-node absorbs photon (1 tick)

```
state_new = O_gamma * v_e    where O_gamma = e_7, v_e in V-rep
```

- $e_7$ and $v_e$ are both in (or computed from) the V subalgebra.
- The triple products required to evaluate the full update are
  associative relative to the V-rep vacuum axis.
- The Alternativity Trigger does **not** fire.
- **Cost: 1 tick** (single XOR + sign lookup).

### 4.2 System B — S+ node absorbs photon (15 ticks)

```
state_new = O'_gamma * s_mu    where s_mu in S+-rep
```

The incoming photon $\mathcal{O}_\gamma = e_7$ is written in V-rep machine
code. The muon node $s_\mu$ is S+-rep hardware. The COG graph engine cannot
evaluate $e_7 \times s_\mu$ natively: the representations are incompatible.

**The Emulation Protocol (Conflict Resolver, S+-branch):**

1. **Translate the operator:** apply the McRae triality translation
   $\mathcal{O}'_\gamma = \tau(e_7) = H \cdot e_7$ where $H$ is the
   $4 \times 4$ Euclidean triality quartet matrix (arXiv:2502.14016, eq. 8):

   $$H = \frac{1}{2}\begin{pmatrix} -1 & -1 & 1 & 1 \\ 1 & 1 & 1 & 1 \\ -1 & 1 & 1 & -1 \\ -1 & 1 & -1 & 1 \end{pmatrix}$$

   Cost: $N_\tau = 14$ ticks (proved by `count_circuit_depth_greedy(H)`,
   equal to $\dim(G_2) = 14$).

2. **Execute the translated interaction:** $\mathcal{O}'_\gamma \times s_\mu$
   is now a native S+-rep multiplication. Cost: 1 tick (XOR).

**Total cost: $14 + 1 = 15$ ticks per photon absorption at a muon node.**

### 4.3 Vacuum Hop — Algebraic Justification and the Speed of Light

When the photon edge ($\mathcal{O}_\gamma = e_7$) arrives at a vacuum node
with state $\omega = \frac{1}{2}(1 + ie_7)$, the interaction is:

$$e_7 \cdot \omega = e_7 \cdot \tfrac{1}{2}(1 + ie_7) = \tfrac{1}{2}(e_7 + i \cdot e_7^2) = \tfrac{1}{2}(e_7 - i)$$

**Associativity check:** Both $e_7$ and $\omega$ live in
$\mathrm{Span}_\mathbb{C}\{1, e_7\}$ — the complex plane defined by the
vacuum axis. This is a commutative, associative sub-algebra of
$\mathbb{C} \otimes \mathbb{O}$: no triple product involving only these
elements can be non-associative. The Alternativity Trigger does **not**
fire. Cost: **1 tick**.

**The speed of light as a kinematic bound:** In the COG DAG, 1 tick is the
minimum possible cost of any causal interaction. A photon that incurs
exactly 1 tick per vacuum hop propagates at the maximum possible rate —
this is $c$. Any massive excitation incurs overhead ticks (the electron
incurs 1 extra tick per scattering vertex; the muon incurs 14 extra ticks
per vertex), which is why their effective propagation rate is less than $c$.

**Literature grounding:**
- Sorkin (2009) arXiv:0910.0673 "Light, Links and Causal Sets": photon
  propagation = link traversal; $c$ is the link-traversal rate (1 link per
  fundamental growth step of the causal set).
- Dowker, Henson, Sorkin (2003) arXiv:gr-qc/0311055: massless excitations
  saturate the maximum causal-link rate; this is a consequence of the causal
  partial order, not an additional postulate.
- Gorard (2020) arXiv:2004.14810: causal invariance of a discrete rewriting
  system → discrete Lorentz covariance; mass = reduced hop rate
  (computational drag below $c$).

**COG-original claim:** The specific identification of the photon with
$e_7 \in \mathbb{C} \otimes \mathbb{O}$ (the vacuum axis) and the proof that
$e_7 \cdot \omega$ is associative has no direct arXiv precedent. The closest
published work is Furey (2016) arXiv:1603.04078 (U(1)_EM from octonion
number operator) and Furey (2019) arXiv:1910.08395 (3 generations +
SU(3)×U(1) from $\mathbb{C}\otimes\mathbb{O}$), neither of which explicitly
identifies the photon propagation rule with the vacuum-associativity property.

---

## 5. Topological Mass Drag and Orbit Return Times

In the COG DAG, physical time is topological depth. Mass is tick-cost
density. Two distinct tick-cost contributions must be tracked:

1. **The vertex entry cost** — the cost of absorbing the photon (1 or 15
   ticks depending on rep type).
2. **The orbit recovery cost** — the cost for the particle to return to its
   exact initial state after the photon has altered it.

### 5.1 Orbit Return Time Definition ($C_\mu$ and $C_e$)

**Definition:** The orbit return time $C_p$ of particle $p$ is the total
number of ticks accumulated from the moment $p$ emits or absorbs a photon
until $p$'s state vector returns to its exact initial baseline:

$$C_p = \text{(vertex entry ticks)} + \text{(recovery propagation ticks)}$$

**Electron ($C_e$):**
1. Absorbs photon $e_7 \cdot v_e$: state changes to $v_e' \neq v_e$ (1 tick).
2. Propagates through vacuum nodes: each 1-tick XOR returns a new state.
3. The electron lives in the associative L1 subalgebra $\{e_1, e_2, e_3\}$.
   Products stay within L1, and the orbit is short (period = 3 from the
   associative group structure of L1).
4. $C_e$ is small — dominated by the 3-element associative orbit.

**Muon ($C_\mu$):**
1. Absorbs photon via H-matrix translation: state changes to
   $\mathcal{O}'_\gamma \cdot s_\mu$ (15 ticks). This rotation is in the
   **S+-representation space** — the muon's state now lies in the image of
   the triality automorphism $\tau$.
2. Propagates through vacuum nodes: each 1-tick XOR applies a further
   octonion rotation from the vacuum.
3. The muon lives outside the associative sector. Its recovery must traverse
   the $G_2$ automorphism orbit — the 14-dimensional group that stabilizes
   $\tau$. The state wanders through $G_2$ state space before returning.
4. $C_\mu$ is large — the $G_2$ orbit period, weighted by the 14-tick
   entry cost, is expected to give $C_\mu \approx 207 \cdot C_e$.

**The hypothesis (LEPTON-001):**

$$\frac{C_\mu}{C_e} \approx 206.768$$

**Literature grounding for the orbit method:**
- Dixon (1994) arXiv:hep-th/9410202 "Octonion X-product orbits":
  explicitly counts return times (orbit periods) of octonion states under
  repeated application of a modified octonion product. Methodological
  ancestor of the $C_\mu / C_e$ calculation, though applied to abstract
  octonion orbits rather than particle masses.
- Singh (2025) arXiv:2508.10131 "Fermion mass ratios from the exceptional
  Jordan algebra": derives fermion mass ratios from a parameter-free discrete
  algebraic eigenvalue ladder in $J_3(\mathbb{O}_\mathbb{C})$, with mass
  ratios set by the ladder rung-spacing ($\delta^2 = 3/8$, CG factors
  $(2,1,1)$). Structurally analogous — mass from discrete algebra, not
  continuous fields — but uses eigenvalue ladders, not orbit periods.
- Both the Dixon and Singh approaches remain distinct from the COG orbit
  return-time mechanism. No arXiv paper has computed 206.768 from a $G_2$
  orbit length or a Fano-plane cycle count. This claim is **COG-original**.

**Topological drag as emergent gravity:**
After each photon absorption the muon node lags 14 ticks behind the ambient
vacuum lattice. The vacuum edges, propagating at $c = 1$ tick/hop, must wait
at the muon's causal future. This localized tick-density excess **bends the
surrounding vacuum edges toward the muon** — the COG mechanism for inertial
mass and, in aggregate, for gravitational attraction.

The single-vertex ratio $\Delta t_\mu / \Delta t_e = 15 / 1 = 15$ is only
the *entry* cost. The full orbit ratio $C_\mu / C_e$ includes the recovery
traversal through $G_2$ state space and is the target observable.

---

## 6. Python Implementation Spec

### 6.1 File

`calc/qed_scatter.py`

### 6.2 Data Structures

```python
from dataclasses import dataclass, field
from typing import Literal, Optional

RepType = Literal['V', 'Sp', 'Vac']

@dataclass
class Node:
    id: int
    rep: RepType
    state: int           # octonion basis index 0..7
    tick_cost: int = 0

@dataclass
class Edge:
    src: int             # Node.id
    dst: int             # Node.id
    op: Optional[int]    # octonion basis index of carried operator, None = propagation
```

### 6.3 Core Function: `update_step`

```python
def update_step(
    node: Node,
    incoming_edges: list[Edge],
    oct_mul,             # from calc/conftest.py or equiv.
    N_tau: int = 14,
) -> Node:
    """
    Compute the successor node after all incoming edges are resolved.

    Resolution order (Conflict Resolver, RFC-001 §4):
      1. Photon edges processed first (highest priority).
      2. Propagation edge applied last.

    Tick cost:
      - V node absorbing a photon edge: +1 tick (native XOR)
      - Sp node absorbing a photon edge: +N_tau + 1 ticks (triality emulation)
      - Vac node absorbing a photon edge: +1 tick (e_7 and omega share the
        vacuum complex plane — associative, no triality penalty fires)
        NOTE: Vac nodes are NOT transparent. The photon routes THROUGH them.
        Each vacuum hop costs 1 tick and defines c = 1 hop/tick.
      - Any node absorbing a propagation edge: +1 tick
    """
    total_ticks = node.tick_cost
    state = node.state

    # Sort: photon edges first, propagation edges last
    photon_edges = [e for e in incoming_edges if e.op is not None]
    prop_edges   = [e for e in incoming_edges if e.op is None]

    for edge in photon_edges:
        if node.rep == 'Sp':
            # S+ node: must emulate triality translation before XOR.
            # The incoming V-rep operator (e_7) is incompatible with S+-rep.
            # Cost = N_tau (H-matrix emulation) + 1 (native XOR)
            translated_op = apply_triality_h(edge.op)   # tau(e_7)
            state = oct_mul(translated_op, state)
            total_ticks += N_tau + 1
        else:
            # V or Vac node: native XOR, 1 tick.
            # For Vac: e_7 * omega = (1/2)(e_7 - i) — stays in the vacuum
            # complex plane Span_C{1, e_7}, associative, no penalty.
            state = oct_mul(edge.op, state)
            total_ticks += 1
            # If this is a Vac node, it must re-emit the photon to the next
            # node in the chain (see propagate_photon() in run_scattering).

    for edge in prop_edges:
        # Free propagation: identity operator, 1 tick
        total_ticks += 1

    return Node(
        id=node.id + 1,   # successor in DAG (simplified; real sim uses global counter)
        rep=node.rep,
        state=state,
        tick_cost=total_ticks,
    )
```

### 6.4 Simulation Runner

```python
def run_scattering(
    system: Literal['ee', 'emu'],
    n_vacuum: int = 4,
    n_interactions: int = 1,
) -> dict:
    """
    Simulate one photon emission/absorption cycle in a vacuum lattice.

    Returns:
        {
          'system': 'ee' | 'emu',
          'particle1_rep': 'V',
          'particle2_rep': 'V' | 'Sp',
          'vertex_tick_cost': int,       # ticks at the absorption vertex
          'n_tau': 14,
          'vacuum_tick_cost': int,       # ticks across n_vacuum nodes
          'total_tick_cost': int,
        }
    """
    ...
```

### 6.5 Expected Outputs

| System | `vertex_tick_cost` | Interpretation |
|--------|--------------------|----------------|
| `'ee'` | 1 | Native V-rep XOR |
| `'emu'` | 15 | 14 (triality emulation) + 1 (XOR) |

The ratio $15 / 1 = 15$ is a lower bound on $m_\mu / m_e$ from a single
vertex. The full $C_\mu / C_e$ ratio from orbit simulation (LEPTON-001)
is the target observable.

---

## 7. Open Questions

| Question | Status |
|----------|--------|
| Does the orbit return-time ratio $C_\mu / C_e$ converge to 206.768? | **Open** (LEPTON-001) |
| What is the correct orbit definition for the muon motif? | **Resolved** — §5.1: total ticks from absorption until state returns to exact initial baseline |
| Does the vacuum lattice size $n$ affect the ratio? | **Open** — expect $C_\mu / C_e$ to be independent of $n$ (vacuum hops cancel in ratio) |
| Should the photon propagate through vacuum nodes (incurring per-node costs)? | **Resolved** — Yes: 1 tick/hop, defining $c$; see §3.4 and §4.3 |
| How does the conflict resolver handle simultaneous photon + propagation? | Specified (photon first) |
| Does the triality translation $\tau(e_7)$ preserve the U(1)_EM charge? | **Open** (needs Lean proof in Spinors.lean) |
| Does $n$ cancel in $C_\mu / C_e$? | **Open** — hypothesis: vacuum hops $n$ add equally to both $C_\mu$ and $C_e$, so ratio converges |

---

## 8. Claims Addressed

| Claim ID | Title | RFC contribution |
|----------|-------|-----------------|
| LEPTON-001 | Muon-to-electron mass ratio | Provides the simulation architecture |
| GEN-001 | Three generations from triality | V vs S+ cost distinction models generation gap |
| GAUGE-001 | U(1)_EM from e₇ | Photon operator $= e_7$ is the U(1) generator |

---

## 9. References

### COG-internal

- McRae (2025): Triality and the Standard Model, arXiv:2502.14016, eq. (8) — source of $H$ matrix
- Furey (2019): arXiv:1910.08395 — electron/muon state vectors in $\mathbb{C}\otimes\mathbb{O}$
- `rfc/CONVENTIONS.md` §2 — locked Fano triples; §8 — Witt pairs and vacuum axis $e_7$
- `calc/triality_map.py` — `count_circuit_depth_greedy(H) = 14` (the $N_\tau = \dim(G_2)$ result)
- `claims/muon_mass.yml` — LEPTON-001 status and next_steps
- `CausalGraphTheory/Koide.lean:brannen_b_squared` — $B^2=2$ algebraic proof (2026-02-22)

### Speed of light from discrete causal structure (§4.3 grounding)

- Sorkin (2009) arXiv:0910.0673 — "Light, Links and Causal Sets": photon = link traversal;
  $c$ = link-traversal rate (1 link per fundamental growth step). **Primary reference for §4.3.**
- Dowker, Henson, Sorkin (2003) arXiv:gr-qc/0311055 — masslessness saturates the maximum
  causal-link rate; Lorentz invariance emerges from the causal partial order.
- Gorard (2020) arXiv:2004.14810 — causal invariance → discrete Lorentz covariance;
  mass = reduced hop rate (computational drag below $c$). **Primary reference for §5.**
- Kastrati & Hinrichsen (2025) arXiv:2504.12919 — 1 hop/tick rule is curvature-stable
  across AdS spacetime; not an artifact of flat-space approximation.

### Discrete QED / causal set field theory (§4.2 grounding)

- Johnston (2009) arXiv:0909.0944 — Feynman propagator for scalar field on causal set;
  foundational reference for quantized vertex amplitudes on discrete edges.
- Johnston (2010) arXiv:1010.5514 — Full QFT + non-perturbative S-matrix on causal set;
  formalizes "amplitude per causal hop." U(1) gauge field vertex is an open problem (§4).
- Cortes & Smolin (2014) arXiv:1407.0032 — spin foam = energetic causal set; quantized
  energy-momentum flows along causal edges. Validates discrete vertex events.

### Octonion photon / U(1)_EM (§4.3 COG-original claim)

- Furey (2016) arXiv:1603.04078 — charge quantization from octonion number operator;
  U(1)_EM arises from ladder operators anchored at the Witt vacuum. Closest published
  grounding for COG's $\mathcal{O}_\gamma = e_7$ identification.
- Furey & Hughes (2022) arXiv:2210.10126 — U(1)_EM survives as the last unbroken abelian
  factor in the Spin(10) → SM breaking cascade through octonion complex structures.

### Orbit period / mass ratio methods (§5.1 grounding)

- Dixon (1994) arXiv:hep-th/9410202 — "Octonion X-product orbits": explicit return-time
  counting for states under repeated application of a modified octonion product.
  **Methodological ancestor of the $C_\mu / C_e$ computation.** No mass interpretation.
- Singh (2025) arXiv:2508.10131 — "Fermion mass ratios from the exceptional Jordan algebra":
  parameter-free mass ratios from discrete eigenvalue ladder in $J_3(\mathbb{O}_\mathbb{C})$
  ($\delta^2 = 3/8$, CG factors $(2,1,1)$). Closest published result structurally.
  Uses eigenvalue ladder, not orbit periods; 206.768 not computed directly.
- Gillard & Gresnigt (2019) arXiv:1906.05102 — triality orbit of length 3 in Cl(8)
  explains three generations; orbit length 3 ≠ 206.

### Open gap: COG-original claims with no arXiv precedent

1. Photon propagation rule: $e_7 \cdot \omega$ is associative (1 tick) because both live
   in $\mathrm{Span}_\mathbb{C}\{1, e_7\}$. Not stated in any published paper.
2. Photon = $e_7$ (vacuum axis): consistent with Furey (1603.04078, 1910.08395) but not
   stated explicitly in those terms.
3. $m_\mu / m_e$ from $G_2$ orbit return time: no paper derives 206.768 from a
   Fano-cycle count or $G_2$-orbit period. **Genuinely novel prediction.**
