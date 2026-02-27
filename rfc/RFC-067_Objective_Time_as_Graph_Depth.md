# RFC-067: Objective Time as Graph Depth

Status: Active Draft (2026-02-27)
Module:
- `COG.Core.ObjectiveTime`
Depends on:
- `rfc/RFC-002_Deterministic_Tick_Ordering.md`
- `rfc/RFC-022_Lightcone_Semantics_and_Causal_Locality.md`
- `rfc/RFC-023_Discrete_Phase_Clocks_and_Relative_Phase_Interactions.md`
- `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
- `rfc/RFC-064_Superdeterminism_and_Lightcone_Information_Volume.md`
Related:
- `rfc/RFC-060_Lorentz_Symmetry_Recovery_from_Causal_DAG.md`
- `rfc/COG_GLOSSARY.md` §§ II, III

---

## 1. Executive Summary

In COG, time is not a coordinate, not a dimension, and not an observer-relative
measurement. Time **is** the `topoDepth` function: the integer-valued graph depth
of a node in the causal DAG.

This makes time:
1. **Objective** — it is a structural property of the graph, not an artifact of
   any measurement frame.
2. **Absolute** — every node has exactly one depth; there is no ambiguity.
3. **Discrete** — depths are natural numbers; there is no "between" two consecutive
   ticks.
4. **Directed** — edges only go forward; the arrow of time requires no additional
   postulate.
5. **Universal** — the depth function is defined globally over the entire DAG.

This RFC states the formal claim, distinguishes the two COG clocks
(`topoDepth` vs `tickCount`), explains how relativistic time dilation reappears
without sacrificing objectivity, and lists the open questions that follow.

---

## 2. The Problem with Conventional Accounts of Time

### 2.1 The Newtonian picture

In Newtonian mechanics, time is a universal background parameter `t in R`.
It ticks at the same rate for every object everywhere. Simultaneity is absolute:
two events either happen at the same `t` or they do not.

This is observationally wrong. Two clocks at different altitudes or velocities
diverge measurably. Newtonian time is an approximation.

### 2.2 The relativistic picture

Special and general relativity replace the single `t` with a spacetime manifold.
Time becomes one coordinate among four. Simultaneity becomes frame-dependent:
whether two events are "at the same time" depends on which inertial frame you use.
Proper time (the time a specific clock measures along its worldline) is real, but
it is path-dependent — two clocks that separate and reunite will disagree.

This solves the observational problem but introduces a philosophical one: **time
has no observer-independent meaning.** The "present moment" has no global
definition. The universe does not have a well-defined "now."

This is the twin paradox, the relativity of simultaneity, the block universe — and
it has been the source of confusion in foundations of physics for a century.

### 2.3 The quantum mechanical non-answer

Quantum mechanics makes the situation worse. The Schrodinger equation evolves the
wavefunction forward in a background time parameter identical to Newton's. The
wavefunction "collapses" at measurement — but when exactly? The measurement is not
a local event. The time at which collapse occurs is not well-defined. Time in QM
is an external classical scaffolding bolted onto a theory that does not explain it.

### 2.4 The COG claim

COG dissolves all three problems simultaneously:
1. There is a global, observer-independent notion of time: `topoDepth`.
2. Proper time (what a clock measures) is `tickCount`, which can vary — restoring
   relativistic effects without sacrificing objectivity.
3. The wavefunction does not collapse; there is only the deterministic microstate,
   and `topoDepth` timestamps every event exactly.

---

## 3. Formal Definition: Time as topoDepth

### 3.1 The causal DAG

Let `G = (V, E)` be the COG causal directed acyclic graph.

- `V` is the set of nodes (each carrying a state in `C x O over Z`).
- `E` is the set of directed edges, where `(u, v) in E` means "u causally
  precedes v."
- Acyclicity is a hard structural requirement: there are no directed cycles.
  This is enforced by the COG update rule, which only allows a node at depth `d`
  to influence nodes at depth `d+1` or greater (RFC-002).

### 3.2 The depth function

**Definition (topoDepth).** For a DAG `G = (V, E)` with a unique root set
`R subset V` (nodes with no incoming edges), define:

```
topoDepth : V -> N

topoDepth(v)  =  0                              if v in R
topoDepth(v)  =  1 + max{ topoDepth(u) : (u,v) in E }   otherwise
```

This is the standard longest-path depth in a DAG. It is:
- **Well-defined** because `G` is acyclic (no infinite recursion, no cycles to
  create ambiguity).
- **Integer-valued** by induction.
- **Unique** — each node has exactly one depth (not a range or interval).
- **Computable** in `O(|V| + |E|)` time (topological sort order).

### 3.3 Time is this function

**Claim (Objective Time).** The physical time of a node `v` is `topoDepth(v)`.
This is not a coordinate assigned by convention. It is a structural property of
the graph, determined entirely by the causal ancestry of `v`.

No observer, no reference frame, and no measurement apparatus is required to
define it. The depth exists whether or not it is read.

---

## 4. The Two Clocks: topoDepth and tickCount

The RESEARCH_DIRECTOR_PRIMER (§5.2) introduces a critical distinction. There
are two clocks in COG and they must not be conflated.

### 4.1 topoDepth — the cosmic clock

`topoDepth` is the global causal clock. It answers: "how far from the initial
conditions is this node in the causal ordering?"

Properties:
- Global: defined for every node in the entire DAG.
- Monotone: if `(u, v) in E` then `topoDepth(u) < topoDepth(v)`.
- Observer-independent: does not depend on which nodes you visit or what path
  you take.
- The discrete analogue of **coordinate time** in GR — but unlike coordinate
  time, it is not a gauge choice. It is fixed by the graph structure.

### 4.2 tickCount — the local clock

`tickCount(v)` is the number of times the update rule has fired at node `v`.
It counts how many D1-D3 cycles a specific node has undergone.

Properties:
- Local: each node has its own count.
- Can differ between nodes at the same topoDepth: a node that was spawned late
  (D4 spawn at depth d) may have fewer accumulated ticks than a node that has
  existed since depth 0.
- The discrete analogue of **proper time** in GR — and, like proper time,
  it can differ between nodes.

### 4.3 The distinction matters

The relativistic twin paradox is about `tickCount`, not `topoDepth`.

If two nodes both start at `topoDepth = 0` but one takes a "longer path" through
the graph (connecting through more intermediate hops, each requiring a tick), it
will accumulate a higher `tickCount` by the time both reach `topoDepth = T`.

This is the COG analogue of time dilation: **tickCount rate per topoDepth unit
varies with path length through the causal graph.** But the underlying ordering
— which event happened before which — is determined by `topoDepth`, which is
invariant.

**Summary:**
- `topoDepth`: the objective, global, absolute time. Never ambiguous.
- `tickCount`: the experienced, path-dependent, local clock. Can differ between
  observers. Gives rise to time-dilation-like effects.

---

## 5. Simultaneity is Absolute in COG

### 5.1 The simultaneity equivalence class

**Definition.** Two nodes `u, v in V` are **simultaneous** if and only if:

```
topoDepth(u)  =  topoDepth(v)
```

This is an equivalence relation. The equivalence classes are the **depth slices**
of the DAG:

```
S(d)  =  { v in V  |  topoDepth(v) = d }
```

These slices are well-defined, non-overlapping, and cover all of `V`. They
provide a canonical foliation of the causal structure into "nows."

### 5.2 Contrast with special relativity

In special relativity, whether two events are simultaneous depends on the
observer's velocity. Two events that are simultaneous in one inertial frame are
not in another. There is no preferred foliation; "now" is a gauge choice.

In COG, the foliation is not a gauge choice. It is determined by the graph. The
depth slices are physically real in the sense that they are fixed by the causal
structure, which is fixed by the initial conditions and the update rule.

### 5.3 How Lorentz-like effects survive

This does not contradict the recovery of approximate Lorentz symmetry at large
scales (which RFC-060 addresses separately). The mechanism is:

1. At the microscopic level: `topoDepth` provides an absolute global time and
   genuine simultaneity classes.
2. At the macroscopic level: coarse-grained observers cannot directly measure
   `topoDepth` of arbitrary nodes. What they measure is their own `tickCount`
   and the arrival times of signals (messages through the graph).
3. Signal travel takes at least as many ticks as the graph distance between
   nodes (the speed-of-light constraint: dx <= dt in the lightcone test).
4. The *apparent* relativity of simultaneity — what observers disagree about
   when comparing signal arrival times — emerges from the impossibility of
   measuring the absolute depth ordering without visiting every intermediate node.

Observers cannot **access** the absolute `topoDepth` of distant events in real
time. They can only infer it retrospectively from the causal structure of messages
they have received. This produces all the operational predictions of special
relativity while preserving the underlying objectivity of `topoDepth`.

The key word is **operational**: SR is a statement about what observers can
measure, not about what is real. COG separates these levels.

---

## 6. The Arrow of Time Requires No Additional Postulate

### 6.1 The standard problem

In classical and quantum mechanics, the dynamical laws are time-symmetric. Nothing
in the equations of motion forbids running them backward. The arrow of time —
the fact that the past differs qualitatively from the future — has to be inserted
by hand, typically via thermodynamics (entropy increases because of low-entropy
initial conditions).

This is unsatisfying. Why should a fundamental theory require an initial
condition as a separate input just to explain why time has a direction?

### 6.2 The COG resolution

In COG, the arrow of time is **structural**, not thermodynamic. It follows
directly from the definition of a DAG:

- A DAG has a partial order: `u < v` if there is a directed path from `u` to `v`.
- This partial order is asymmetric: if `u < v` then not `v < u`.
- `topoDepth` is a monotone function on this order: `u < v` implies
  `topoDepth(u) < topoDepth(v)`.

There is no time-reverse of a DAG that is itself the same DAG with edges
reversed, because the edge structure is part of the physical state of the
universe. Reversing the edges would produce a different causal structure — a
different universe — not the same universe running backward.

**The arrow of time is not a thermodynamic fact about entropy. It is a
topological fact about the graph: directed edges are not bidirectional.**

This dissolves the puzzle entirely. There is nothing to explain. Time has a
direction because causality has a direction, and causality has a direction because
the COG update rule writes edges that go one way only.

---

## 7. The Present Moment is Real

### 7.1 The block universe objection

The block universe view (common in GR and SR) holds that past, present, and
future all equally "exist." The present is not special — it is just the location
of an observer's worldline on the spacetime block. There is no becoming; there
is only being.

Many physicists find this unsatisfying because it seems to contradict the
phenomenological reality of the present moment. If past and future are equally
real, why do we experience exactly one moment as "now"?

### 7.2 The COG answer

In COG, the present is the current frontier of the DAG: the set of nodes at the
highest populated `topoDepth`. It is not just a label on a pre-existing structure;
it is the leading edge of construction.

More precisely:

- Depths `0, 1, ..., T-1` are "computed" — their node states are fixed by the
  deterministic update rule and the initial conditions.
- Depth `T` is being computed now — the update rule is currently firing for
  nodes at this depth.
- Depths `T+1, T+2, ...` do not yet exist — they have no nodes because those
  nodes have not been spawned or updated yet.

The present is not a location in an already-complete block. It is the tip of
an ever-growing structure. Past depths are frozen; future depths are empty.
This gives the present a privileged ontological status that the block universe
denies it.

**The present is real in COG because the graph is being built, not merely read.**

---

## 8. Implications

### 8.1 For measurement and observation

Every observation is an interaction between two nodes. That interaction is a
directed edge from the observed node to the observing node. The observation
therefore carries a definite `topoDepth` — the depth of the observing node.

There is no ambiguity about when a measurement happened. There is no
wavefunction collapse event with an unclear timestamp. The update rule fires
at a specific depth and the result is fixed. The "measurement problem" in
quantum mechanics does not arise in COG because there is no classical/quantum
boundary, no collapse postulate, and no ambiguous timing.

### 8.2 For causality and locality

A node at depth `d` can only be influenced by nodes at depth `d-1` or earlier
(within its lightcone). There is no retrocausality, no action at a distance,
and no information traveling faster than the lightcone speed limit. This is
structurally enforced by the DAG — not a postulate layered on top of the physics.

### 8.3 For thermodynamics

The second law of thermodynamics is typically explained as: the universe started
in a low-entropy state and entropy can only increase. COG does not change this
for the macroscopic case. But it adds a deeper layer: **monotone depth increase
is more fundamental than entropy increase.** Entropy is a macroscopic, coarse-
grained concept. `topoDepth` is a microscopic, structural one. The thermodynamic
arrow of time is a consequence of the structural one, not an independent fact.

### 8.4 For cosmology

The "beginning of time" in COG is depth `0`: the root set `R` of the DAG.
This is a precise concept. There is no ambiguity about what "before the Big Bang"
means: there is no graph below depth `0`. The question is not unanswerable; it
is empty. There are no nodes at depth `-1`.

This is compatible with RFC-066's treatment of the Big Bang as Root Node.

### 8.5 For superdeterminism

RFC-064 establishes that the full future microstate is determined by the initial
microstate and the update rule. RFC-067 adds: and every event in that future
microstate has a definite, objective timestamp (`topoDepth`) which is part of
its structural identity, not a label added afterward.

---

## 9. Distinction from Causal Set Theory

Causal set theory (Bombelli, Lee, Meyer, Sorkin 1987) is the closest existing
framework. It also treats spacetime as a partial order. The key differences in COG:

| Property | Causal Sets | COG |
|---|---|---|
| Node content | Bare events (no algebraic state) | `C x O` state per node |
| Growth law | Random Poisson sprinkling | Deterministic update rule |
| Depth function | Not generally used; set is a partial order | `topoDepth` is explicit and primary |
| Time | Emerges from partial order | IS the topoDepth function |
| Dynamics | Stochastic (CSG model) | Deterministic (RFC-028) |
| Simultaneity | Not defined (no global preferred foliation) | Defined: same `topoDepth` |

The COG claim is stronger than the causal set claim. Causal sets identify
spacetime with a partial order but do not provide a preferred global clock.
COG provides the preferred clock: `topoDepth`. The price is the loss of
manifest Lorentz covariance at the microscopic level (recovered approximately
at macroscopic scales, per RFC-060).

---

## 10. Formal Contract

**Contract OT-1 (topoDepth well-definedness).**
For any finite DAG `G` generated by the COG update rule with root set `R`,
the function `topoDepth : V -> N` is well-defined, integer-valued, and unique.

*Proof:* By induction on graph construction. Root nodes get depth `0`. Each
subsequent node spawned by D4 receives depth `1 + max(parent depths)`. Acyclicity
(enforced by the update rule) prevents circular dependency. [ ]

**Contract OT-2 (monotonicity).**
For all `(u, v) in E`: `topoDepth(u) < topoDepth(v)`.

*Proof:* Follows from D4 spawn semantics: a node is only spawned at depth
`> max(parent depths)`. Edges always go from lower to higher depth. [ ]

**Contract OT-3 (simultaneity is an equivalence relation).**
The relation `u ~ v iff topoDepth(u) = topoDepth(v)` is an equivalence relation
on `V`.

*Proof:* Reflexivity, symmetry, and transitivity all follow trivially from
integer equality. [ ]

**Contract OT-4 (arrow of time is structural).**
The COG causal DAG has no automorphism that reverses all edges while preserving
the graph structure.

*Proof:* Such an automorphism would map every directed path `u -> v` to `v -> u`.
But `topoDepth(u) < topoDepth(v)` and the automorphism would require
`topoDepth(v) < topoDepth(u)` simultaneously. Contradiction. [ ]

---

## 11. Open Questions

1. **topoDepth recovery by macroscopic observers.** Can a macroscopic observer
   reconstruct the absolute `topoDepth` ordering from local signal exchanges?
   The answer is likely: yes, in principle, but requiring information from the
   full backward lightcone. This connects to RFC-064 (lightcone information volume).

2. **topoDepth and energy.** If `topoDepth` is time, is there a discrete
   analogue of the Hamiltonian (the generator of time translation)? The update
   rule `T(psi) = e7 * psi` acts as the temporal commit, but it is not obviously
   Hermitian in the usual sense. What is the conserved charge of depth-translation
   invariance?

3. **Multi-root universes.** If the root set `R` contains multiple disconnected
   components, the `topoDepth` function is still well-defined on each component
   but there is no canonical way to synchronize depths across components. Does
   this correspond to disconnected universes, or is causal connection always
   established eventually?

4. **Depth and the Planck scale.** Is there a physical unit for one topoDepth
   increment? The candidate is the Planck time `t_P = 5.39 x 10^-44 s`. This
   connects to the scale calibration program of RFC-052.

5. **tickCount as a physical observable.** Is `tickCount` directly measurable,
   or is it always inferred from state comparisons? The answer has implications
   for whether "clock" objects in COG (nodes with high accumulated tickCount)
   are meaningfully different from "young" nodes at the same topoDepth.

6. **Compatibility with the lightcone engine.** The `xor_full_lightcone_engine.py`
   simulation already uses `depth` as the loop variable and enforces the light-cone
   condition `dx <= dt`. This is consistent with the `topoDepth` framework. The
   open question is whether the simulation's `depth` variable is the best
   approximation to `topoDepth` in a fixed-grid setting, or whether a more
   general depth-tracking mechanism is needed for non-uniform graphs.

---

## 12. Relationship to Existing RFCs

| RFC | Relationship |
|---|---|
| RFC-002 | Establishes deterministic tick ordering — the ground for topoDepth being well-defined |
| RFC-022 | Lightcone semantics — defines which nodes can influence which; topoDepth determines the depth coordinate in the lightcone test |
| RFC-023 | Phase clocks — tickCount is the phase clock; this RFC clarifies it is NOT topoDepth |
| RFC-028 | Update rule — the rule that creates the edges; those edges define topoDepth |
| RFC-060 | Lorentz recovery — explains how approximate SR emerges from a graph with absolute topoDepth ordering |
| RFC-064 | Superdeterminism — topoDepth gives the timestamp for every event in the deterministic trajectory |
| RFC-066 | No singularities — Big Bang as Root Node (topoDepth = 0); this RFC formalizes what that means |

---

## 13. Summary

Time in COG is `topoDepth`: the integer depth of a node in the causal DAG.

This single identification resolves:
- The arrow of time (structural, not thermodynamic)
- The objectivity of simultaneity (same depth = genuinely simultaneous)
- The reality of the present moment (the current frontier of graph construction)
- The absence of time-travel (acyclicity is a hard graph constraint)
- The measurement problem's timestamp ambiguity (every interaction has a definite depth)

The experience of varying clock rates (relativistic time dilation, gravitational
redshift) is recovered through `tickCount`, which can differ between nodes at the
same `topoDepth`. This preserves all observational predictions of relativity
while keeping the underlying time ordering absolute and observer-independent.

The most important sentence in this document:

> **Time is not something that happens to the graph. Time is the graph counting itself.**

---

*End of RFC-067*
