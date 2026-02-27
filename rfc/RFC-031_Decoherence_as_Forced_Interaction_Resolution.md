# RFC-031: Decoherence as Forced Interaction Resolution in the Causal Graph

**Status:** Active - Exploratory Draft (2026-02-25)  
**Module:** `COG.Theory.QuantumMeasurement`  
**Dependencies:** `rfc/RFC-001_Canonical_State_and_Rules.md`

---

## 1. Executive Summary

This RFC provides a structural definition of the "Measurement Problem" and "Wavefunction Collapse" using Causal Graph Theory (COG). In standard quantum mechanics, collapse is an unexplained, instantaneous, non-local event triggered by an "observer." 

In COG, we propose that **decoherence and collapse are the direct result of the graph's deterministic Conflict Resolver (RFC-001) being overwhelmed by a high density of incoming causal edges from a macroscopic environment.**

A quantum "superposition" is simply a sub-graph where multiple potential update branches are pending, and no local information has forced a definite non-associative resolution. "Measurement" occurs when the target node receives a massive influx of interaction edges (from a detector/environment). The COG update rules mathematically *force* the node to resolve its state deterministically to process the sheer volume of incoming information, snapping the pending branches into a single, definite history.

---

## 2. Motivation

The Copenhagen Interpretation relies on a magical "observer" to collapse the wavefunction. Many-Worlds creates infinite, unobservable universes. Objective Collapse theories (like GRW) add arbitrary mathematical parameters to force collapse.

COG is strictly deterministic and causal. It cannot use any of these standard interpretations. If the state updates are deterministic functions of the algebra $\mathbb{C} \otimes \mathbb{O}$, we must explain how the illusion of probabilistic "superposition" and sudden "collapse" emerges purely from graph topology.

---

## 3. Core Postulates

### P1. Superposition is "Pending Evaluation"
In COG, when an electron travels through the vacuum graph, it does not exist as a smeared-out cloud of probability. However, because the graph is dynamically spawned, the exact topological path the electron takes may be under-constrained by the immediate local algebra. If there are multiple valid graph pathways that perfectly preserve the algebraic invariants (no interaction), the state is effectively "unresolved" relative to the rest of the universe. It is a set of pending branches in the evaluation tree.

**Kernel gap:** "Pending branches" is not yet a formal type in the kernel (RFC-001 or RFC-028). The current NodeState only represents resolved states. Formalizing a `pending` state — a node with under-constrained outgoing edges — is a prerequisite for this RFC. This must be added to RFC-028 or RFC-001 before any Lean formalization here can proceed.

### P2. The Environment is a Dense Graph Component
A macroscopic measurement device (a screen, a camera, a human eye) is not special because it is "conscious." It is special because it is incredibly dense. It contains trillions of massive particles, each generating massive numbers of interaction ticks (`tau_int`), and constantly emitting thermal and electromagnetic edges into the surrounding causal graph.

### P3. Measurement is Forced Resolution via Conflict Resolver
When the "pending" electron sub-graph intersects with the extremely dense "detector" sub-graph, the electron node suddenly receives millions of incoming causal edges.
According to the Conflict Resolver (RFC-001), when a node receives multiple concurrent edges, it must apply a deterministic ordering (e.g., based on topological index or operator priority) and compute the resulting non-associative product. 

This massive influx of information **forces the evaluation** of the pending branches. The node must pick a single, definite algebraic outcome to satisfy the incoming operators. The "superposition" is destroyed not by magic, but by the computational necessity of resolving a highly connected local graph neighborhood.

---

## 4. The Mechanism of "Apparent Randomness"

If COG is deterministic, why do quantum measurements look perfectly random (obeying the Born Rule)?

Imagine the target node at the moment of measurement. It is receiving thousands of incoming causal edges from the detector. The exact non-associative outcome depends entirely on the **exact arrival order and algebraic phase** of those thousands of edges. 

The exact micro-state of those incoming edges is determined by the internal states of the detector's constituent nodes — fully deterministic in principle, but practically unpredictable because the detector's internal state is inaccessible. No exogenous randomness is introduced. The apparent randomness is entirely epistemic: it reflects the observer's ignorance of the detector's microstate at the moment of measurement, not any non-determinism in the update rules.

Therefore, the outcome (e.g., spin-up or spin-down) is deterministic in principle, and unpredictable in practice solely due to the complexity of the detector subgraph.

The **Born Rule** (probabilities being the square of the amplitude) must emerge as a statistical law of combinatorics: it represents the ratio of valid graph topologies that result in state $A$ versus state $B$ under massive random edge bombardment.

---

## 5. Falsifiability & Differences from Standard QM

### 1. No Faster-Than-Light Spooky Action
In COG, Bell-test entanglement is not instantaneous communication across continuous space. Two entangled particles are simply two branches of a recent graph ancestor. Because the graph updates are deterministic, the invariants between the two branches are mathematically locked at the shared ancestor. When one branch is hit by a dense detector (measured), its state resolves, and the global invariants of that sub-graph constrain the *other* branch. Distance is topological, so this does not violate causality; the invariant was established at the shared ancestor node.

**⚠ Bell's theorem audit required (not addressed by narrative):** Bell's theorem rules out local hidden-variable theories. COG is a deterministic theory with correlations set at a shared ancestor — precisely the structure Bell's analysis targets. A formal no-signaling audit is mandatory before this claim can stand:

- Given shared ancestor $A$ and two successor branches $B$ and $C$ at topological depth $d$:
  - Prove that resolving $B$'s state at time $t$ does not propagate any information to $C$ faster than the causal graph depth allows.
  - Identify which of Bell's assumptions (locality, realism, statistical independence) is being modified or denied by the COG structure.
  - Show whether the resulting correlations can reproduce the full range of quantum correlations measured in loophole-free Bell tests (Hensen et al. 2015, etc.).

This is a prerequisite for §2 of this section, not a downstream corollary.

### 2. The Heisenberg Cut is Computable
Standard physics cannot define exactly where the quantum world ends and the classical world begins (the Heisenberg Cut). In COG, this cut is a precise, computable topological metric: the critical edge density at which the Conflict Resolver forces a non-associative branch resolution. We can mathematically define exactly how large a system must be before it "collapses" itself.

---

## 6. Implementation Targets for the Lab

### 6.1 Python Simulation (`calc/decoherence_sim.py`)
1. Create a "pending" quantum state (a graph node with two potential, un-evaluated outgoing edges).
2. Simulate a "measurement": connect 1,000 deterministically-ordered incoming edges representing the detector microstate. **The edge ordering must be derived from a seeded internal state of the "detector" subgraph — not from an external random number generator.** Two different detector seeds produce two different orderings; the distribution over seeds represents epistemic uncertainty about the detector microstate.
3. Run the deterministic Conflict Resolver.
4. **Measurement:** Verify that the node is forced to snap to a single classical state. Show that repeated runs with different detector seeds produce a statistical distribution of outcomes. Report the Born-rule consistency check: does the frequency of spin-up vs. spin-down match the amplitude-squared ratio?

### 6.2 Lean Formalization (`CausalGraphTheory/Measurement.lean`)

The following must be proved in this order before any higher-level decoherence claim:

1. **`pending` state type:** Define `PendingState` as a node with a set of algebraically valid but not-yet-selected outgoing edges. Add this to the kernel type hierarchy (coordinate with RFC-028 / RFC-001 update).
2. **Forced resolution:** Prove that increasing in-degree strictly reduces the number of valid pending branches. This is the formal decoherence lemma.
3. **Observable map $\Pi_{\text{obs}}$:** Define the projection from a resolved `NodeState` to a classical observable outcome. Without this, there is no connection between graph states and measurement results.
4. **No-signaling benchmark:** Prove the causal propagation theorem — information cannot travel faster than the DAG's topological depth ordering. This is the minimal Bell-compliance check required before the claim in §5.1 can be asserted.

---

## 7. Compatibility Requirements

| Check | Status | Blocking? |
|-------|--------|-----------|
| DAG acyclicity preserved | Yes — measurement adds edges, does not create cycles | No |
| Determinism — no exogenous randomness | Fixed in §4 (see above) — randomness is epistemic, from detector microstate | No |
| `pending` state type defined in kernel | **No** — must be added to RFC-001/RFC-028 | **Yes for §6.2** |
| Bell/no-signaling formally audited | **No** — narrative only; formal proof required | **Yes for §5.1** |
| Observable map $\Pi_{\text{obs}}$ defined | **No** — prerequisite for Born-rule claim | **Yes for §6.2 step 3** |
| RFC-028 determinism policy compatible | Unverified — forced resolution must be consistent with RFC-028 Conflict Resolver | Yes |

**Minimum viable path:** Implement the Python sim (§6.1) with deterministic detector seeds. Do not write Lean until the `pending` state type is added to the kernel specification.