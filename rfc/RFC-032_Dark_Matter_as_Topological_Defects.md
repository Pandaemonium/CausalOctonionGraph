# RFC-032: Dark Matter as Topological Defects in the Vacuum Graph

**Status:** Active - Exploratory Draft (2026-02-25)  
**Module:** `COG.Theory.Cosmology`  
**Dependencies:** `rfc/RFC-013_Algebraic_Vacuum_and_Causal_Spawning.md`, `rfc/RFC-030_Gravity_as_Emergent_Graph_Density.md`

---

## 1. Executive Summary

This RFC explores a natural explanation for Dark Matter within Causal Graph Theory (COG). Standard cosmology assumes dark matter is a new, undiscovered, weakly interacting massive particle (WIMP) or axion. 

In COG, we propose that **Dark Matter is not a particle built from the standard vacuum state $\omega$. Instead, it is a localized "scar" or topological defect in the structure of the causal graph itself.** 

Because these defects require computational ticks to process as the graph updates, they generate "mass" (geodesic curvature, per RFC-030). However, because their local algebra is twisted or broken (e.g., a "knotted" Fano orientation), they are fundamentally orthogonal to the standard photon operator $e_7$ and the standard gauge symmetries, making them completely dark to electromagnetism and the nuclear forces.

---

## 2. Motivation

85% of the universe's mass is "dark," interacting only via gravity. Decades of searching for standard quantum particles have failed. COG's definition of mass as "computational friction" (RFC-018, RFC-030) provides a unique opportunity: anything that causes the graph to stall or loop will generate gravity, even if it has no standard algebraic particle identity.

---

## 3. Core Postulates

### P1. Particles are Structured Excitations
Standard matter (electrons, quarks) is created by applying specific Witt ladder operators ($\alpha^\dagger$) to the highly ordered vacuum idempotent $\omega = \frac{1}{2}(1 + ie_7)$. This structure mathematically guarantees their interaction with the photon $e_7$ and the SU(3)/SU(2) gauge edges.

### P2. Topological Defects are Algebraically Inert States

The dynamically spawned vacuum graph may contain nodes whose algebraic state is a valid element of $\mathbb{C} \otimes \mathbb{O}$ but is **not in the orbit of the vacuum idempotent $\omega$** under the standard Witt ladder operators. Such nodes are legal kernel states (they satisfy all DAG and type constraints) but dynamically inert: the standard particle creation/annihilation operators cannot act on them.

Examples of compliant defect types:

1. **Orbit-Isolated States:** A node whose $\mathbb{C} \otimes \mathbb{O}$ state cannot be reached from $\omega$ by any sequence of Witt ladder operators $\alpha^\dagger_i$. It is algebraically well-defined, acyclic, and causal — but invisible to the standard gauge operators.
2. **Orientation-Mismatched States:** A node carrying a valid octonion state that is consistent with a *different* Fano orientation (e.g., the opposite handedness convention). Under the global convention (locked in `rfc/CONVENTIONS.md`), such a node's $e_7$ phase response is orthogonal to the standard photon operator. *Note: any proposed Fano-orientation variant must be formally defined using the locked convention table — ad hoc local sign flips that break `rfc/CONVENTIONS.md` are not permitted.*
3. **Dead Ends:** A sub-graph that absorbs causal edges but has no algebraically valid outgoing $\mathbb{C} \otimes \mathbb{O}$ branches under the standard update rules, causing the graph engine to stall at that node.

**Removed from this RFC:** "Irreducible Loops" (cycles in the graph) are *not* a valid defect type. Local cycle violations are incompatible with the DAG axiom, which is foundational to the entire COG framework (causal ordering, time emergence, alternativity theorem). A mechanism that requires cycles cannot be a kernel candidate. Any future proposal for loop-like structure must be recast entirely within the DAG axiom before it can enter this RFC.

### P3. Defects Generate Friction (Gravity) but No Light
When the global wave of vacuum updates ($e_7$ phase rotations) hits a topological defect, the standard $e_7 \cdot \omega = -i\omega$ math fails. The defect cannot cleanly relay the photon edge. The graph must spend hundreds or thousands of interaction ticks (`tau_int`) attempting to resolve the broken algebra. 
This massive localized delay creates extreme geodesic curvature (Gravity, per RFC-030).
However, because the defect is not a standard Witt state, it cannot emit a valid $e_7$ photon edge. It is completely "dark" to standard model forces.

---

## 4. Falsifiability & Cosmological Predictions

### 1. No Annihilation Signals
If dark matter is a WIMP particle, colliding dark matter should occasionally annihilate and produce gamma rays (which observatories like Fermi-LAT look for). If dark matter is a graph defect, two defects colliding might "untangle" each other, but they would not produce standard model photons. The lack of a gamma-ray signature in galactic centers strongly supports the defect model.

### 2. Halo Formation
Because defects do not interact via electromagnetism, they cannot easily shed kinetic energy by radiating light (unlike normal gas, which cools and collapses into disks). Therefore, defects will naturally remain in vast, diffuse, spherical "halos" around galaxies—exactly matching the observed distribution of dark matter.

### 3. "Self-Interacting" Dark Matter
If two topological defects collide, the graph must resolve the clash of two broken algebras. This could lead to defects merging (forming larger knots) or fragmenting, providing a natural mechanism for Self-Interacting Dark Matter (SIDM), which helps solve the "core-cusp" problem in galactic density profiles.

---

## 5. Implementation Targets for the Lab

### 5.1 Python Simulation (`calc/defect_sim.py`)
1. Construct a lattice of standard $\omega$ vacuum nodes (compliant with `calc/conftest.py` convention constants — `FANO_CYCLES`, `FANO_SIGN`, `WITT_PAIRS`).
2. Inject a defect node using a **compliant defect definition**: a node whose state is a valid $\mathbb{C} \otimes \mathbb{O}$ element but is not reachable from $\omega$ by any Witt operator sequence. *Do not artificially invert a Fano sign — that would violate `rfc/CONVENTIONS.md`. Instead, construct the defect as an orbit-isolated state using the existing algebra.*
3. Propagate a photon edge ($e_7$) through the lattice.
4. **Measurement:** Verify that (a) the defect generates tick-delay (mass/gravity per RFC-030 $S(v) > 1$) and (b) the photon cannot be absorbed and re-emitted as a standard interaction — the $e_7$ operator has zero inner product with the defect state. Report both measurements independently.

### 5.2 Lean Formalization (`CausalGraphTheory/Topology.lean`)

This is the most tractable formalization target in this RFC — it requires only existing Lean infrastructure.

1. **Define orbit-isolated defect:** `def isDefect (s : KCO) : Prop := ¬ ∃ ops : List WittOp, applyOps ops omega = s` — a state not reachable from $\omega$ by any Witt operator sequence.
2. **Prove U(1) disconnection:** Prove that for any `s` satisfying `isDefect s`, the $U(1)$ gauge group action (projection onto `u1Mask`) yields zero inner product. This is the formal "dark to electromagnetism" lemma.
3. **Prove $e_7$ orthogonality:** Prove that the photon operator $e_7$ cannot map a defect state back into the $\omega$-orbit. This is what makes the defect electromagnetically invisible.

These three lemmas can be assigned immediately — they use only finite algebra over `Fin 8` and do not depend on RFC-028 or RFC-030 being locked.

---

## 6. Compatibility Requirements

| Check | Status | Blocking? |
|-------|--------|-----------|
| DAG acyclicity preserved | **Yes** — defects are legal node states, no cycles introduced (irreducible loops removed) | No |
| `rfc/CONVENTIONS.md` respected | **Yes** — defects are orbit-isolated states, not ad hoc sign flips | No |
| RFC-028 determinism policy compatible | Yes — defects undergo deterministic update rules, just with no valid outgoing branches | No |
| RFC-030 gravity mechanism available | **No** — defect mass-generation claim depends on RFC-030 tick-density mechanism, which is exploratory | Yes (for §4) |
| "Statistically inevitable" formation explained | **No** — cosmological formation mechanism unspecified; COG has no expansion model yet | Yes (for §3 P2 narrative) |

**Minimum viable path:** Assign the three Lean lemmas in §5.2 — they are fully self-contained. Defer the Python simulation until a compliant orbit-isolated state is constructed. Defer all cosmological claims (§3 P2 formation argument) until COG has a graph-expansion model.