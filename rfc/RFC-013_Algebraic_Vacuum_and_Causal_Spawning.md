# RFC-013: Algebraic Vacuum, State Representation, and Dynamic Causal Spawning

**Status:** Active — Architecture Blueprint (2026-02-23)
**Supersedes:** RFC-012 §3.1 (node type table), §3.3 (operator convention)
**Module:** `calc/qed_ee_sim.py` (new — Goal C: e⁻ + e⁻ dynamic graph)
**Dependencies:**
  - `rfc/CONVENTIONS.md` (locked Fano/Furey convention — do not modify)
  - `rfc/RFC-001_Canonical_State_and_Rules.md` (node/edge/tick rules)
  - `rfc/RFC-012_QED_Scattering_Graph_Simulation.md` (Goal A C_e=4 result)
**Claims addressed:**
  - `SPACE-001` (Emergent spatial dimensionality)
  - `LIGHT-001` (Derivation of c = 1 tick/node)

---

## 1. Executive Summary

This RFC establishes three interlocked architectural decisions for the COG simulation
engine: the algebraic definition of the vacuum state, the state representation format,
and the protocol for growing the causal graph lazily ("dynamic causal spawning").

**Three locked decisions (from Gemini architectural review, 2026-02-23):**

1. **Full ℂ⊗O state representation:** Node states are length-8 complex NumPy arrays.
   Basis element eₖ is represented as the unit vector with a 1 at index k.

2. **Left-multiplication universally:** The photon operator acts as
   State_next = e₇ · State_current (operator on the left). This is consistent with
   quantum-mechanical convention (operators act from the left on state vectors).

3. **Dynamic Causal Spawning with SPAWN sentinel:** The DAG grows on demand.
   Edges carry a target that is either an existing node ID or the sentinel `SPAWN`.
   A `SPAWN` edge, when processed, instantiates a new vacuum node and routes the
   operator there.

**Key algebraic result (verified 2026-02-23):**

$$e_7 \cdot \omega = -i\omega$$

The photon operator left-multiplying the vacuum produces a pure phase rotation.
The vacuum orbit under repeated e₇ hits has **period 4**, identical to the
electron orbit period. This is the algebraic grounding of c = 1 tick/hop.

---

## 2. The Vacuum State: ω as Absolute Identity

### 2.1 Definition

In the Furey ℂ⊗O framework, the vacuum is the idempotent:

$$\omega = \frac{1}{2}(1 + i e_7)$$

In the 8-component complex state vector (index 0 = e₀ = scalar identity,
index 7 = e₇ = vacuum axis):

```python
OMEGA = np.array([0.5, 0, 0, 0, 0, 0, 0, 0.5j], dtype=complex)
# index:           0   1  2  3  4  5  6   7
# physical:       e0  e1 e2 e3 e4 e5 e6  e7
```

### 2.2 Algebraic properties of ω

| Property | Expression | Value |
|----------|-----------|-------|
| Idempotent | ω² | ω |
| Conjugate | ω† = ½(1 − ie₇) | distinct from ω |
| Annihilation | αⱼ·ω = 0 for all j | ω is annihilated by all lowering operators |
| Vacuum product | ω·ω† | primitive idempotent (Witt decomposition basis) |

**Physical meaning:** ω is the algebraic vacuum — the state that is annihilated by all
matter creation operators. It is the *generator* from which the Witt decomposition is built.
Furey (arXiv:1603.04078 §2, arXiv:1611.09182 ch. 4) uses ω explicitly in this role.

### 2.3 The Axiom of Identity

> **A node is a vacuum node if and only if its algebraic state is in the orbit of ω
> under the photon operator e₇.**

The orbit (see §4) is {ω, −iω, −ω, iω}. A node is a *matter* node if its state
is outside this orbit. The engine branches on algebraic content, never on metadata.

**Correct:** `if state_is_vacuum_orbit(node.state):`
**Forbidden:** `if node.is_vacuum:` (where `is_vacuum` is stored alongside state)

The function `state_is_vacuum_orbit` checks `np.allclose(state, k * OMEGA)` for
k ∈ {1, −i, −1, +i} — a pure algebraic check, no metadata required.

---

## 3. State Representation: Full ℂ⊗O

### 3.1 Why integers are insufficient

The `SignedState(index: int, sign: ±1)` representation used in `qed_calibration.py`
cannot represent ω = ½e₀ + ½ie₇ (a complex linear combination of two basis elements).
As soon as the simulation must test whether a node is the vacuum, the index-level
representation breaks down.

### 3.2 The 8-component complex array

Every node state is a NumPy complex128 array of length 8:

```python
# state[k] = coefficient of eₖ (complex number) 
# Basis conventions (1-indexed):
#   e0 = scalar identity, index 0
#   e1..e6 = imaginary units, indices 1..6
#   e7 = vacuum axis (VACUUM_AXIS+1 from conftest.py), index 7

def basis_vector(k: int, sign: int = +1) -> np.ndarray:
    """Unit vector for basis element eₖ with given sign."""
    v = np.zeros(8, dtype=complex)
    v[k] = float(sign)
    return v

E0   = basis_vector(0)   # scalar identity
E1   = basis_vector(1)   # first L1 basis element
E7   = basis_vector(7)   # vacuum axis / photon operator
OMEGA = 0.5 * E0 + 0.5j * E7  # = ½(e0 + i·e7)
```

### 3.3 Left-multiplication function (full ℂ⊗O)

```python
def oct_mul_full(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Left-multiply a * b in ℂ⊗O.
    Uses the Furey Fano convention from calc/conftest.py.
    Both a and b are length-8 complex arrays.
    Returns a length-8 complex array.
    """
    result = np.zeros(8, dtype=complex)
    for i, ai in enumerate(a):
        if ai == 0:
            continue
        for j, bj in enumerate(b):
            if bj == 0:
                continue
            idx, sgn = oct_mul_basis(i, j)  # pure basis multiplication
            result[idx] += ai * bj * sgn
    return result
```

Where `oct_mul_basis(i, j)` returns `(k, s)` such that `eᵢ · eⱼ = s · eₖ`,
using `FANO_SIGN` and `FANO_THIRD` from `calc/conftest.py`.

---

## 4. Operator Convention: Left-Multiplication

### 4.1 The convention

All operator applications in the COG engine use **left-multiplication**:

$$\text{State}_{\text{next}} = \mathcal{O} \cdot \text{State}_{\text{current}}$$

**Literature grounding (confirmed 2026-02-23):** Furey (arXiv:1910.08395) builds the
entire Standard Model gauge structure from *left-multiplication* operators. All SU(3)_c
generators Λⱼ and the U(1)_EM charge Q = N/3 act by left-action on states. Right-
multiplication by e₇ is associated with *isospin* (SU(2)_L) effects, not electromagnetic:
Furey's eq. (5) expresses any right-multiplication as a chain of left-multiplications,
and the gauge algebra Cl(6) is generated solely by left-action maps (arXiv:1603.04078
eqs. 1–3). Consequently, the photon U(1)_EM operator must act by **L_{e₇}** (left-mult),
not R_{e₇}. This resolves the left/right ambiguity in favor of left-multiplication.

### 4.2 Orbit of e₁ under left-multiplication by e₇ (verified 2026-02-23)

From the Fano triple (e₁, e₇, e₆) with the Furey cyclic convention:
e₁ · e₇ = +e₆ (right-mult) implies e₇ · e₁ = −e₆ (left-mult, sign flip).

| Step | Operation | Result | In L1? |
|------|-----------|--------|--------|
| 0 | initial | +e₁ | yes |
| 1 | e₇ · (+e₁) | −e₆ | no |
| 2 | e₇ · (−e₆) | −e₁ | yes (phase flip) |
| 3 | e₇ · (−e₁) | +e₆ | no |
| 4 | e₇ · (+e₆) | +e₁ | yes ✓ |

**Period = 4.** Same as the right-multiplication orbit in `qed_calibration.py`.

### 4.3 Convention invariance of C_e = 4

The period-4 result is *convention-invariant*. It follows from:
- Under left-mult: $(L_{e_7})^4 = (-i)^4 \cdot \text{id} = +\text{id}$ (since $L_{e_7}^2 = -\text{id}$ for any octonion imaginary unit)
- Under right-mult: $(R_{e_7})^4 = +\text{id}$ by the same argument

The intermediate states differ (left: −e₆ at step 1; right: +e₆ at step 1), but both
yield exact return after 4 steps. **C_e = 4 is robust across both conventions.**

### 4.4 Emission and absorption are symmetric

Both emission and absorption apply the e₇ operator to the *emitting/absorbing* node's
state. There is no asymmetry between emission and absorption in the algebraic update:

```
Emission:   emitter_state_next = e₇ · emitter_state_current
Absorption: absorber_state_next = e₇ · absorber_state_current
```

The asymmetry is purely in *timing*: the absorber receives the edge D ticks after the
emitter emits (where D is the topological distance).

---

## 5. Vacuum Relay: e₇ · ω = −iω

### 5.1 Derivation (exact)

$$e_7 \cdot \omega = e_7 \cdot \tfrac{1}{2}(e_0 + i e_7)
= \tfrac{1}{2}(e_7 \cdot e_0 + i \cdot e_7 \cdot e_7)
= \tfrac{1}{2}(e_7 + i(-1))
= \tfrac{1}{2}e_7 - \tfrac{1}{2}i$$

$$-i\omega = -i \cdot \tfrac{1}{2}(e_0 + ie_7)
= \tfrac{1}{2}(-ie_0 + (-i)(ie_7))
= \tfrac{1}{2}(-ie_0 + e_7)
= \tfrac{1}{2}e_7 - \tfrac{1}{2}i \quad \checkmark$$

**Verified numerically** in `calc/` (2026-02-23): `np.allclose(e7 @ omega, -1j * omega) == True`.

### 5.2 The vacuum orbit (period 4)

Under repeated left-multiplication by e₇:

| Step | State | Phase | In orbit? |
|------|-------|-------|-----------|
| 0 | ω | ×1 | yes |
| 1 | −iω | ×(−i) | yes |
| 2 | −ω | ×(−1) | yes |
| 3 | +iω | ×(+i) | yes |
| 4 | ω | ×1 | yes ✓ |

The vacuum orbit {ω, −iω, −ω, iω} is **closed** under the photon operator, with
**period 4** — identical to the electron orbit period. This means:

> **The photon and the vacuum are in algebraic resonance.** The electron returns
> to its initial state in exactly the same number of photon interactions as the
> vacuum lattice returns to its ground state. This is the COG algebraic grounding
> of the invariant speed of light: neither the electron nor the vacuum accumulates
> an unresolvable phase asymmetry over one full electromagnetic cycle.

### 5.3 Vacuum relay protocol

When the photon edge (e₇ operator) arrives at a vacuum node at state S ∈ {ω, −iω, −ω, iω}:

1. **Update state:** S_next = e₇ · S (= phase_factor × S, one tick)
2. **Re-emit immediately:** spawn a new outgoing e₇ edge from this node to the next
   node in the chain (a `SPAWN` target if no node exists there yet)
3. **Total cost:** 1 tick for steps 1 and 2 combined

The relay is *transparent* in timing: the photon advances by one hop per tick
regardless of what phase state the vacuum node is in. The phase accumulation
{1, −i, −1, +i} is tracked in the node state but does not affect propagation cost.

### 5.4 Why vacuum propagation costs exactly 1 tick

The update `S_next = e₇ · S` requires only the operations for elements in
Span_ℂ{e₀, e₇}. This is a **commutative, associative** subalgebra of ℂ⊗O
(isomorphic to ℂ itself: e₇² = −1 makes it a copy of the complex numbers).
The Alternativity Trigger evaluates to *False* — no non-associative penalty.
Cost: 1 tick (native multiplication, no additional evaluation steps).

### 5.5 Relationship to causal set vacuum propagation

**Standard causal set theory** (Dowker, Henson, Sorkin 2010, arXiv:1009.3058;
Sorkin 2009, arXiv:0910.0673) treats the vacuum as *transparent*: a massless
scalar field propagates along causal links without changing the internal state of
intermediate vacuum nodes. The Dowker-Henson-Sorkin mean signal exactly matches
the continuum retarded Green's function (their eq. 31); vacuum nodes pass the
signal through with no disturbance.

**COG departure:** The vacuum relay protocol in §5.3 differs from this standard
picture: COG vacuum nodes undergo a phase shift (ω → −iω) on each photon pass.
This is a COG-original proposal. The two approaches agree on:
- Propagation cost: 1 tick per hop (both models)
- Signal amplitude: undistorted (relay is lossless)
- Speed of light: 1 hop/tick (both models)

They differ on whether intermediate vacuum nodes accumulate phase. The physical
consequence is the (−i)^D phase factor after D hops (see §10, open question 3).
No existing causal set paper discusses this internal algebraic phase; it is
**COG-original with no literature precedent or contradiction**.

---

## 6. Dynamic Causal Spawning

### 6.1 The SPAWN sentinel

An edge carries either:
- A concrete **destination node ID** (an already-instantiated node), or
- The sentinel **`SPAWN`** — meaning "instantiate a new vacuum node to receive this edge"

```python
SPAWN = -1  # sentinel: destination does not yet exist

@dataclass
class Edge:
    src_id: int        # source node ID
    dst_id: int        # destination node ID, or SPAWN
    op: np.ndarray     # operator carried (e.g., E7 for photon, E0 for propagation)
    tick_emitted: int  # tick at which this edge was created
```

### 6.2 The update protocol (depth t → t+1)

```
1. Collect the frontier F = {all leaf nodes at the current tick with unresolved edges}
2. For each edge e in F:
   a. If e.dst_id is SPAWN:
      - Instantiate new node N with state = OMEGA (vacuum)
      - Assign N a fresh node ID
      - Route edge to N
   b. Apply the Conflict Resolver (RFC-001 §4) to all edges arriving at each node:
      - Photon edges first (higher priority)
      - Propagation edges last
   c. Compute each receiving node's new state:
      - state_next = e.op · state_current  (left-multiplication)
   d. Assign tick costs (1 tick for vacuum/V nodes, 15 ticks for S+ nodes)
3. For each updated node:
   a. If the node is in the vacuum orbit and carries a photon edge: re-emit (relay)
   b. If the node is a matter node: it may emit a new photon edge (see §7)
```

### 6.3 Topology without coordinates

The causal graph has no coordinates. Two nodes are "adjacent" if and only if there
is a direct edge between them. The concept of "distance" reduces to the topological
(graph-theoretic) path length. The engine never computes `sqrt(x² + y² + z²)`.

---

## 7. Seed Topology: Encoding Separation as D Vacuum Nodes

Two electrons E₁ and E₂ separated by a physical distance are represented by
initializing a *seed topology*: a directed chain of D vacuum nodes between them.

```
t=0 seed:  E1 ──► V_0 ──► V_1 ──► ... ──► V_{D-1} ──► E2
```

- D is the topological distance (number of vacuum hops = number of ticks for a
  photon to travel from E₁ to E₂).
- D is an **initial condition** of the simulation, not a free parameter of the theory.
  It encodes the specific experimental geometry being modelled.
- Nodes V₀ through V_{D-1} all initialize with state OMEGA.
- The graph grows beyond D as photons are emitted and relayed.

### 7.1 E₁ emits a photon at tick 0

When E₁ is initialized and begins evolving:
- E₁ emits a photon: an e₇ edge is added from E₁ to V₀.
- E₁'s own state updates: E₁_state_next = e₇ · E₁_state_current.
- V₀ receives the edge at tick 1 (1 hop), relays to V₁.
- E₂ receives the edge at tick D (D hops), updates its state.

### 7.2 E₂ emits a return photon

After absorbing the photon at tick D, E₂ may emit a photon back toward E₁.
This photon must traverse D vacuum nodes again (but now in the reverse direction —
new nodes are spawned if the reverse chain doesn't exist yet).

---

## 8. Strict Prohibitions

The following patterns are banned from any module that claims to implement COG physics:

| Pattern | Why banned |
|---------|-----------|
| Pre-allocated N×N×N array for "empty space" | Assumes a background manifold; forbidden by the Prime Directive |
| Software type tag alongside state: `node.is_vacuum = True` | Violates the Axiom of Identity; type is determined by `node.state` alone |
| Free-aiming: `target_id = find_nearest_node(x, y, z)` | Assumes coordinates; all interaction must follow explicit graph edges |
| ω stored as integer index 0 | Cannot distinguish ω from −iω from −ω from iω (all map to "e₀") |
| Reusing SignedState(index, sign) for vacuum | SignedState can only represent pure basis elements; ω is a complex superposition |

---

## 9. Consistency with Existing Results

### 9.1 C_e = 4 is preserved under the left-multiplication convention

`qed_calibration.py` uses right-multiplication and obtains C_e = 4.
This RFC adopts left-multiplication. Both give period 4 (§4.3 above).
The new `qed_ee_sim.py` will use left-multiplication and should independently
reproduce C_e = 4 as a calibration check.

### 9.2 Vacuum hop cost = 1 tick is preserved

The vacuum relay (§5.3) still costs exactly 1 tick. The e₇·ω calculation is
associative (both factors in Span_ℂ{e₀, e₇}), so no Alternativity penalty.
This is consistent with RFC-012 §4.3.

### 9.3 The ELECTRON_STATE correction is preserved

The electron still initializes at e₁ (basis vector E1), not at e₆ or ω.
In full ℂ⊗O notation: `E1 = basis_vector(1)` = [0, 1, 0, 0, 0, 0, 0, 0].

---

## 10. Open Questions

| Question | Status | Literature |
|----------|--------|-----------|
| Does the vacuum return to ω after 4 photon hits, or does phase accumulate? | **Resolve in simulation** — mathematically returns; physically TBD | No precedent |
| Is the "vacuum orbit = electron orbit" period-4 coincidence meaningful? | **Open** — COG-original; both are a consequence of L_{e₇}⁴ = id acting on all of Cl(6)s | Furey (implicit); **novel** |
| What observable closes the e-e scattering experiment? | **Pending decision** — both electrons return to initial state simultaneously? | RFC-012 §5.1 |
| Does the vacuum relay preserve the photon phase? | **Open** — phase factor (−i)^D after D hops | No precedent |
| Do (−i)^D vacuum factors cancel in C_μ/C_e? | **Open** — likely yes, both particles traverse same D hops | No precedent |
| Is the COG vacuum relay (phase shift) consistent with transparent vacuum in causal sets? | **Open** — both give 1 tick/hop; phase shift is extra COG structure | Dowker-Henson-Sorkin 1009.3058 (transparent vacuum) |
| Does [Q, s] = 0 imply the vacuum orbit is charge-invariant? | **Yes** — Furey: Q·s = 0 (vacuum Q=0), [Q, s] = 0; orbit is electrically neutral | Furey 1603.04078 |

---

## 11. References

### Vacuum idempotent ω
- Furey (2016) arXiv:1603.04078 §2: ω = ½(1+ie₇) as the Witt vacuum; αⱼω = 0.
  Equation (3) defines the ladder operators from the six imaginary Witt elements.
- Furey (2016 thesis) arXiv:1611.09182 ch. 4: Full Fock space from ω; the neutrino
  is ωω†, the electron is α₁α₂α₃ω†ω (maximal occupation, eq. 6.29–6.31).
- Furey (2019) arXiv:1910.08395 §II: e₇ is held fixed by SU(3)_c;
  U(1)_EM from number operator N/3.

### Causal set photon propagation
- Sorkin (2009) arXiv:0910.0673: photon = link traversal; c = 1 link/fundamental step.
- Johnston (2009) arXiv:0909.0944: Feynman propagator on causal set; vacuum propagator
  = sum over causal paths.
- Johnston (2010) arXiv:1010.5514: Full QFT on causal sets; U(1) gauge field open §4.

### COG-internal
- `rfc/CONVENTIONS.md` §2–8: locked Fano triples, FANO_SIGN, WITT_PAIRS, VACUUM_AXIS
- `calc/conftest.py`: FANO_CYCLES, FANO_SIGN, FANO_THIRD constants
- `rfc/RFC-012_QED_Scattering_Graph_Simulation.md`: Goal A C_e=4 result
- `calc/qed_calibration.py`: right-multiplication calibration (C_e=4 verified, 50 tests)

---

## 12. COG-Original Claims in This RFC

Claims in this RFC that have **no direct arXiv precedent** (searched 2026-02-23):

1. **Vacuum orbit period = 4**: e₇·ω = −iω → orbit {ω, −iω, −ω, iω} has period 4.
   The result e₇·ω = −iω is implicit in Furey's algebra but the 4-cycle orbit and its
   physical interpretation are not stated in any paper reviewed.

2. **Vacuum orbit period = electron orbit period**: Both ω and e₁ (and all elements of
   Cl(6)s) have period 4 under L_{e₇}. This follows from the fact that L_{e₇} multiplies
   every element of Cl(6)s by the phase −i (since e₇ commutes with SU(3)_c). Not stated
   in Furey or any other paper reviewed.

3. **Vacuum phase accumulation per relay hop**: Standard causal set theory (Dowker-
   Henson-Sorkin) treats the vacuum as transparent — no internal state change. COG adds
   the phase factor (−i) per hop. This is an extension beyond standard causal set theory.

4. **SPAWN sentinel for lazy DAG growth**: The specific algorithm of using a sentinel
   value to trigger on-demand vacuum node instantiation is a COG implementation choice
   with no direct literature precedent.

**Claims that ARE supported by literature:**
- ω = ½(1+ie₇) is an idempotent: s² = s (Furey 1910.08395)
- U(1)_EM acts by left-multiplication (Furey 1603.04078, 1910.08395)
- Massless field propagates at 1 link/tick recovering continuum c (Sorkin 0910.0673)
- Vacuum transparent in standard causal set propagation (Dowker-Henson-Sorkin 1009.3058)
