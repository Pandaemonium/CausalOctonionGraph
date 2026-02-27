# RFC-066: No Singularities — Cosmological Reframing of the Causal Octonion Graph

Status: Hypothesis — structural argument, not yet promoted to proved claim
Date: 2026-02-27
Author: Research Director
Depends on: RFC-028 (Update Rule Closure), RFC-040 (Particle Motif Contract),
            RFC-064 (Superdeterminism and Light-Cone Information Volume)
Cross-links: COG_GLOSSARY.md §§XIII–XV

---

## 1. Thesis

Every physical infinity predicted by classical general relativity — the Big
Bang singularity, the black hole singularity, runaway Hawking evaporation —
is an artifact of applying a continuous manifold model below its domain of
validity. In the Causal Octonion Graph (COG) framework, where reality is a
directed acyclic graph with integer-coefficient node states, infinities are
structurally forbidden. They cannot appear. This RFC formalises that
structural argument and derives the COG counterpart of each infinite quantity.

The key claim:

> A singularity in general relativity corresponds, in the COG model, to a
> maximally dense finite clique — a complete subgraph where every node is
> adjacent to every other. Density saturates at n(n−1)/2 edges for n nodes.
> It does not diverge. The continuum description's infinity is the graph's
> finite maximum.

---

## 2. Background: Where Infinities Come From in GR

General relativity is formulated on a smooth pseudo-Riemannian manifold M
with metric g_μν. Given a stress-energy source, the Einstein field equations
produce a metric. Singularities appear when this metric becomes non-
extendable — when curvature scalars like the Kretschner invariant
R_μνρσ R^μνρσ diverge.

The Penrose–Hawking singularity theorems prove that under plausible energy
conditions, singularities are inevitable: gravitational collapse always
terminates in a singularity; the universe began at one.

These theorems are correct within their domain: smooth manifolds with
continuous fields. They say nothing about what happens when the manifold
description is replaced by a discrete graph at the Planck scale.

---

## 3. The Structural Argument Against Infinities

### 3.1 Density is bounded in a finite graph

Let G = (V, E) be the causal graph at any tick. For any connected subgraph
H ⊆ G with |H| = n nodes, the number of edges |E(H)| satisfies:

    |E(H)| ≤ n(n−1)/2

This is the complete graph K_n. It is a finite number for any finite n.

The local energy density at a region is proportional to the message flux
(edge density × amplitude per edge). Since both edge count and node-state
amplitude are bounded (node states are integers, bounded by conservation of
total amplitude), the energy density is bounded.

**Conclusion: energy density cannot diverge. Singularities are forbidden.**

### 3.2 The Planck scale is the graph resolution

In the continuum description, volume can be taken to zero: you can always
zoom in further. In the graph, the minimum volume is one node. You cannot
zoom in further than one node.

The Planck length is not a lower bound imposed by quantum mechanics on top
of classical GR — it is the edge length, the fundamental granularity of
the graph. Below that scale, there is simply nothing to resolve. The
question "what happens at zero radius?" has no referent in the model.

### 3.3 Curvature saturates rather than diverges

In GR, curvature is a local differential property of the metric. As matter
density increases, curvature increases without bound.

In COG, the analogue of curvature is the deviation of the local hop metric
from flat space. Specifically:

    Curvature_local(v) ~ (actual edges at v) / (expected edges in flat 3D graph at v)

In a flat 3D graph, a node at hop-distance r has ~ 4πr² neighbours at that
shell. A massive region has more. As the region approaches K_n (complete
clique), the effective curvature approaches a maximum: every node is adjacent
to every other, so hop-distance within the region is 1 for all pairs.
Curvature = maximum. Not infinity. Maximum.

The "infinite curvature" of the GR singularity is the graph's curvature
maximum misread through a continuum lens.

---

## 4. The Big Bang as Root Node

### 4.1 Formal definition

Let T be the set of all nodes in the causal graph G, partially ordered by
causal depth d(v) = length of the longest directed path terminating at v.

**Definition (Root Node):** A node r ∈ T is the root node if d(r) = 0 —
i.e., r has no incoming edges.

The Big Bang is the root node. It is not a singularity. It has a definite
state vector psi_r ∈ ℂ⊗𝕆 (16 integers). It is the unique node with no
causal ancestors.

### 4.2 "Before the Big Bang" is not well-formed

The question "what existed before the Big Bang?" asks for a node v with
d(v) < 0, or for a node v with an edge v → r. Neither exists in the DAG.
The question is not unanswerable — it is ill-formed. Time (tick depth) is
defined only within the graph.

This is not mysticism. It is the same logic as asking for a real number less
than zero on the non-negative integers: the structure simply doesn't contain
such an object.

### 4.3 The CMB flatness and horizon problems dissolve

The horizon problem: how did regions of the early universe come to have the
same temperature if they were never in causal contact?

In COG: at early causal depths (small d), the graph is small. Any two nodes
v, w with d(v), d(w) < D_horizon are separated by a small hop distance —
they are in causal contact. The CMB uniformity is a statement that the early
graph had small diameter, meaning all early nodes could exchange messages.

The flatness problem: why is the spatial curvature so close to zero?

In COG: the graph begins with a single root node (or a small cluster) and
grows via D4 spawn rules. The initial graph is necessarily "flat" in the
sense of having no pre-existing curvature — there is no prior metric to curve.
Flatness is the initial condition, not a fine-tuned miracle.

---

## 5. Black Holes as Topological Sinks

### 5.1 Formal definition

**Definition (Black hole region):** A connected subgraph B ⊆ G is a black
hole region if for every node v ∈ B and every directed edge (v, w) ∈ E,
we have w ∈ B. That is, no directed edge exits B.

**Definition (Event horizon):** The horizon ∂B is the set of nodes v ∈ B
such that there exists at least one directed edge (u, v) with u ∉ B.
The horizon is the "interface" between interior and exterior.

No directed path from B reaches any node outside B. B is causally isolated
from the exterior. This is the topological definition of a black hole.

### 5.2 Interior dynamics are ordinary

Inside B, nodes continue to:
- Apply T(psi) = e7 * psi each tick.
- Exchange messages along internal edges.
- Follow the standard update rule D1/D2/D3.

Physics is not "broken" inside. The interior is a densely connected subgraph
running the same local dynamics as anywhere else — just isolated from the
outside.

The "singularity at the center" of a GR black hole corresponds to the
maximum-density clique at the core of B. Density is finite. The local update
rule still executes. The Planck scale discreteness prevents further collapse.

### 5.3 Event horizon as information valve

The horizon ∂B has a definite topological structure:
- Inward edges: (u, v) with u ∉ B, v ∈ B. Information enters B.
- No outward edges: no (v, w) with v ∈ B, w ∉ B in the classical limit.

This is a one-way valve. Information can enter but not exit classically.
This is the origin of the black hole information paradox in GR.

In COG, there is no paradox: the information is preserved in the interior
node states, which are fully determined by the deterministic update rule
(RFC-064). It is causally inaccessible to external observers but not
destroyed. The DAG is the complete record.

### 5.4 Hawking radiation as boundary edge fluctuation

Boundary nodes v ∈ ∂B are adjacent to both interior and exterior nodes.
At each tick, the vacuum drive T acts on v. Because v participates in the
exterior vacuum orbit (it receives exterior messages), there is a nonzero
amplitude for v to spawn a new directed edge to an exterior node w ∉ B —
an outward edge that carries a vacuum phase pulse (photon).

This is Hawking radiation: a slow, tick-by-tick leakage of vacuum phase
pulses from the boundary of the topological sink.

Qualitative features:
1. Rate is proportional to boundary area (number of ∂B nodes): more boundary
   = more potential outward spawns. This gives S_BH ~ Area, matching the
   Bekenstein-Hawking entropy formula.
2. Spectrum is thermal because interior states are scrambled by the dense-
   clique dynamics: the outgoing message amplitude is determined by a complex
   average over many interior states, producing a Planck spectrum.
3. Evaporation is finite: as n decreases (boundary nodes lost), the boundary
   shrinks, radiation slows. Complete evaporation takes finite time (finite
   node count) — no firewall, no remnant paradox.

### 5.5 The Schwarzschild radius in COG

In GR: r_s = 2GM/c². Below r_s, all geodesics point inward.

In COG: the Schwarzschild radius is the hop distance at which the edge
density is high enough that all forward-directed paths point inward. It is
not a smooth surface but a topological property of the graph — the boundary
of the set {v : all paths from v terminate inside the mass concentration}.

The emergence of r_s ~ M from graph dynamics is an open derivation (not
yet completed; requires quantitative calibration of the edge-density-to-mass
ratio, pending RFC-052 scale calibration).

---

## 6. Dark Energy as Spawn Rate

### 6.1 Hubble expansion without a background

Standard cosmology: the universe expands, but there is no centre of expansion
and no exterior to expand into. Space itself grows.

COG counterpart: the D4 spawn rule generates new nodes at a baseline rate
even in the vacuum. These new nodes are inserted into the adjacency web with
edges to their local neighbourhood. The hop-distance between any two motifs
that are not gravitationally bound increases over time as new nodes are
inserted between them.

There is no centre because the spawning is distributed uniformly across all
vacuum nodes. There is no exterior because new nodes are graph-interior (they
connect to existing nodes, not to some outside).

### 6.2 The cosmological constant as a spawn rate

Let Lambda_spawn = (mean new nodes generated per existing vacuum node per tick).

This is a dimensionless parameter of the D4 rule. It is the COG counterpart
of the cosmological constant Lambda.

Observed value: Lambda ~ 10^{-122} in Planck units. This is a tiny but
nonzero spawn rate — the graph grows, but slowly compared to Planck time.

### 6.3 Why Lambda is not a coincidence problem in COG

The "cosmological constant problem" in QFT asks why the observed vacuum energy
is 120 orders of magnitude smaller than the naive quantum field theory
prediction.

In COG there is no QFT vacuum energy. The vacuum is the background tick —
it has no zero-point fluctuation energy in the QFT sense. The spawn rate
Lambda_spawn is a simple property of the D4 rule, not the sum of zero-point
energies of infinitely many field modes. The problem is dissolved, not solved.

---

## 7. Dark Matter as Sterile Motifs

### 7.1 The EM coupling condition

For a motif M to couple to an e7 vacuum phase pulse (photon), it must have
an internal Fano structure that can absorb the phase kick. Specifically, the
motif must have a nonzero Witt-pair component in its state — one of the six
imaginary directions e1..e6 — because the photon interaction is a sign flip
on a Witt-pair direction.

**Definition (EM-sterile motif):** A motif M is EM-sterile if its internal
state lives entirely in the e0 ⊕ e7 subspace of ℂ⊗𝕆. Such a motif:
- Accumulates e0 via self-collision (mass, gravity): yes.
- Couples to e7 vacuum pulses (photon absorption/emission): no.
- Appears as mass-bearing but electromagnetically invisible: yes.

This is the algebraic definition of dark matter.

### 7.2 Stability of EM-sterile motifs

An e0 ⊕ e7 state under the temporal commit T(psi) = e7 * psi:

    T(a*e0 + b*e7) = e7*(a*e0 + b*e7) = a*(e7*e0) + b*(e7*e7)
                   = a*e7 + b*(-e0)
                   = -b*e0 + a*e7

This is a rotation in the e0-e7 plane with period 4 (same as the vacuum
orbit). Such a motif is stable under T and does not generate Witt-pair
components from self-interaction alone. It remains EM-sterile indefinitely.

### 7.3 Gravitational coupling without EM coupling

The e0 accumulation (self-collision rate, mass) drives graph curvature
independently of Witt-pair content. So a pure-e0⊕e7 motif:
- Has mass: yes (e0 accumulates via e7*e7 = -e0 products in the orbit).
- Curves the causal graph: yes (high e0 density → high edge density).
- Emits/absorbs photons: no (no Witt-pair content to flip).

This is precisely the observed behavior of dark matter.

---

## 8. Matter-Antimatter Asymmetry

### 8.1 The asymmetry is an initial condition

The standard model introduces CP violation to explain why the universe contains
more matter than antimatter. In COG, the explanation is simpler:

The root node state vector psi_r was not symmetric under Fano orientation
reversal (the 2-cocycle flip). This is an initial condition, not a derived
mechanism.

The universe has more matter than antimatter because the root node started
in a state with slightly more of one cocycle orientation than the other.
All subsequent causal structure inherits this asymmetry.

### 8.2 CP violation from cocycle asymmetry

The observed CP violation in weak interactions maps onto the asymmetry
between the two possible cocycle orientations for the W boson message.
The W boson message couples to one orientation (left-handed fermions)
because the root node's cocycle bias selected that orientation globally.

This is a structural claim, not a derivation. Quantitative connection to
the CKM matrix requires closing the Witt-pair overlap integrals.

---

## 9. Predictions and Falsifiability

### 9.1 The density cap prediction

**Prediction:** No region of spacetime can have energy density above the
Planck density (one Planck mass per Planck volume = one unit e0 amplitude
per node). Current probes cannot reach Planck density, so this is not
directly testable today but is a hard constraint on any COG-derived
cosmological model.

**Falsification:** If future observations or theory require energy density
to diverge (not just grow large) for a consistent cosmological history,
COG is falsified.

### 9.2 The event horizon structure prediction

**Prediction:** The event horizon of a black hole is not a smooth 2-sphere
but a discrete graph boundary ∂B. At Planck-scale resolution, it has
granular structure with area quantised in units of the Planck area
(one node per Planck area).

This is consistent with the Bekenstein-Hawking entropy S = A/(4*l_P²) if
each boundary node carries exactly one bit of entropy. COG predicts this
naturally.

### 9.3 Hawking radiation must be exactly thermal

**Prediction:** Hawking radiation has a perfect Planck spectrum with
temperature T_H = hbar*c³/(8*pi*G*M*k_B). Deviations from exact
thermality would indicate information leakage through the boundary,
which COG allows only at the quantum level (tiny Planck-scale corrections).

### 9.4 No pre-Big-Bang signature

**Prediction:** There are no observational signatures of a "pre-Big-Bang"
state because there is no pre-Big-Bang state. Any cosmological model
requiring a bouncing universe (cyclic cosmology, string gas cosmology)
is incompatible with the DAG structure, which is strictly acyclic.

**Falsification:** A confirmed cosmological observation that requires a
prior causal structure before the CMB epoch would require either extending
the DAG or replacing it.

---

## 10. Open Questions

1. **Quantitative Schwarzschild radius derivation.** The condition under which
   a subgraph B becomes a topological sink needs to be derived from the D4
   spawn rate, the edge-density-to-mass relation, and the spatial dimension.
   Currently blocked on RFC-052 scale calibration.

2. **Dark matter candidate identification.** The EM-sterile motif class is
   defined but no concrete candidate motif (specific state vector and orbit)
   has been proposed. This is the next step: exhibit an explicit stable e0⊕e7
   motif in the event engine.

3. **Lambda_spawn derivation.** The cosmological constant is currently a free
   parameter (spawn rate of D4). A derivation from the octonion structure
   would require understanding why the root node selected its specific initial
   state vector, which is currently treated as a free initial condition.

4. **Inflation mechanism.** The early high-spawn-rate epoch is postulated but
   not derived. What property of the initial state vector drives the high
   early spawn rate, and why does it decay to the present low value?

5. **Black hole information retrieval.** While COG asserts information is
   preserved (the DAG is the complete record), it does not yet specify how
   an external observer could in principle reconstruct the interior state
   from the Hawking radiation sequence. This is the COG version of the
   Page curve problem.

---

## 11. Relation to Existing RFCs

| RFC | Connection |
|-----|-----------|
| RFC-028 | Update rule D1/D2/D3 — the local dynamics that governs black hole interiors |
| RFC-040 | Particle motif contract — what a stable motif is (applies to dark matter) |
| RFC-052 | Scale calibration — required to derive Schwarzschild radius quantitatively |
| RFC-064 | Superdeterminism — confirms information is preserved in the DAG; no paradox |
| RFC-030 | Gravity proxy — precursor to the full COG gravity derivation |
| RFC-032 | Defect dynamics — dark matter motifs may be a class of stable defects |

---

## 12. Summary

| GR Concept | COG Counterpart | Key Difference |
|---|---|---|
| Singularity (infinite density) | Maximum-density clique (finite) | Density caps at n(n-1)/2 edges |
| Big Bang singularity | Root node (tick depth 0) | No infinite density; just a first node |
| Black hole singularity | Dense interior clique | Physics continues; just causally isolated |
| Event horizon (smooth surface) | Topological boundary ∂B | Discrete, Planck-granular |
| Hawking radiation | Boundary edge fluctuation | Same formula; different mechanism |
| Dark energy (vacuum energy) | D4 spawn rate Lambda_spawn | No QFT zero-point divergence |
| Dark matter (unknown substance) | EM-sterile e0⊕e7 motif | Algebraically defined, not ad hoc |
| Matter-antimatter asymmetry | Root node cocycle bias | Initial condition, not mechanism |

The central message: **the infinities of classical gravity are precision artifacts
of taking the continuum model outside its domain of validity. The discrete graph
has no room for infinity. Every "singularity" is a saturation point. Every
"divergence" is a maximum. The physics continues, finite and deterministic,
all the way down.**

---

## Appendix A: Why Complete Cliques Are Not Singularities

Suppose a region collapses to a complete clique K_n on n nodes.

Properties of K_n in the COG model:
1. Every node has degree n-1 (maximum for n nodes).
2. Every pair of nodes is at hop-distance 1.
3. The effective dimension within K_n is 0 (all nodes are equidistant).
4. The curvature is maximum and finite.
5. The update rule still applies at each node each tick.
6. The total e0 amplitude is the sum over all node e0 components — finite.

Nothing is infinite. Nothing is undefined. The nodes tick. The algebra runs.

The region is maximally dense, maximally curved, and maximally self-
interacting. It is a black hole core. It is not a singularity. It is a
valid, finite configuration of the causal graph.

---

## Appendix B: Discrete Analogue of the Penrose Singularity Theorem

The Penrose theorem proves that if:
1. The null energy condition holds,
2. A trapped surface exists (all null geodesics converge),
3. The spacetime is globally hyperbolic,

then a singularity must exist.

In COG:
1. Null energy condition → all message amplitudes are non-negative. Satisfied.
2. Trapped surface → a subgraph B where all directed paths point inward. This
   is the black hole definition. It can exist.
3. Global hyperbolicity → the DAG has no closed timelike curves (it is acyclic
   by definition).

The conclusion of the Penrose theorem: "a singularity exists" maps onto:
"there exists a causal path that cannot be extended indefinitely forward."

In COG, a path inside B cannot reach outside B. It can be extended inside B
indefinitely (nodes continue to exist and tick). The path is "trapped" but
not terminated. It reaches the dense-clique core and bounces around inside
the clique forever.

This is not a singularity — it is a trapped path in a finite region.
The Penrose conclusion is correct within GR. The COG resolution is that the
conclusion needs to be translated: "inextendible" in the smooth manifold
sense becomes "trapped in a finite clique" in the graph sense.

---

*RFC-066 is a structural argument document. It does not contain Lean proofs or
Python simulations — those are planned work items under the Open Questions
section. The core argument (infinity is forbidden in a finite discrete graph)
is a mathematical tautology; the physical claims (black holes, dark matter, dark
energy as described) are falsifiable hypotheses awaiting quantitative derivation.*
