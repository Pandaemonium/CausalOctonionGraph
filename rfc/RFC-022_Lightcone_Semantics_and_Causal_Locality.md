# RFC-022: Lightcone Semantics and Causal Locality

**Status:** Active - Update Rule Partial Lock (2026-02-26)
**Module:** `COG.Core.Lightcone`, `COG.Core.CausalLocality`
**Depends on:** `rfc/RFC-001_Canonical_State_and_Rules.md`, `rfc/RFC-002_Deterministic_Tick_Ordering.md`, `rfc/RFC-018_Time_as_Graph_Depth_and_Interaction_Clock.md`, `rfc/RFC-020_Kernel_Representation_Reconciliation.md`, `rfc/RFC-023_Discrete_Phase_Clocks_and_Relative_Phase_Interactions.md`
**Lean claims:** `CAUS-001` (reachability partial order), `DAG-001` (step preserves acyclicity)
**Literature basis:** `sources/lightcone_lit_review.md`

---

## 1. Executive Summary

This RFC formalizes how light cones enter COG:

1. Light cones are graph-order objects (causal past/future), not coordinate objects.
2. Candidate update inputs at `(t, v)` are exactly the incoming boundary messages from the causal past of `v`.
3. Updates must satisfy causal locality: perturbations outside the past cone of `v` cannot affect `v` at that tick.
4. COG must explicitly distinguish strict-cone and effective-cone regimes.

This RFC keeps COG consistent with existing deterministic scheduling and Kernel v2 state semantics while making locality a first-class, testable contract.

---

## 2. Motivation

Current RFCs define deterministic ordering (RFC-002), two clocks (RFC-018), and CxO-native state representation (RFC-020), but light-cone semantics are not yet a locked kernel contract.

Without a formal light-cone contract:

- locality assumptions remain implicit,
- debugging cannot separate cone-local failures from scheduler failures,
- event-driven optimizations risk violating causal equivalence.

---

## 3. Literature-Constrained Claims

## 3.1 Claims adopted

1. Causal order is sufficient to define admissible influence structure in order-first frameworks.
2. Discrete causal dynamics can be constrained by bounded propagation speed on graphs.
3. Effective light cones with suppressed outside-cone influence are physically meaningful in local many-body systems.
4. The Fano-7 structure of COG octonion kernels provides a natural candidate upper bound on
   locality radius: each imaginary octonion axis participates in exactly 3 of the 7 directed
   Fano triples, suggesting `k_t(v) <= 3` as the expected Fano-sparse fan-in per interaction
   family. This is a COG-internal model hypothesis, not imported from external literature.

## 3.2 Claims not adopted

1. Literature does not prove that one specific octonion basis axis uniquely defines light cones.
2. Literature does not justify assuming exact zero outside-cone influence in every discrete kernel without proof.
3. Literature does not establish the specific `k_t(v) > 4` monitoring threshold used in §7;
   this is a COG-internal instrumentation choice calibrated to the Fano-7 degree structure.

These remain model hypotheses to be tested, not imported theorems.

---

## 4. Formal Definitions

Let `G_t = (V_t, E_t)` be the directed acyclic causal graph at global tick `t`.

For node `v in V_t`:

- `Past_t(v) := {u | u ->* v}` (transitive causal past)
- `Future_t(v) := {w | v ->* w}` (transitive causal future)

Define `IncomingBoundary_t(v)` as the multiset of active incoming messages delivered to `v` at tick `t` from edges in `E_t`.

Define multiplicity:

`k_t(v) := |IncomingBoundary_t(v)|`

Local state update:

`psi_{t+1}(v) = U(psi_t(v), IncomingBoundary_t(v), EvalPlan_v)`

where `U` is deterministic and `EvalPlan_v` uses immutable tie-break and parenthesization rules from RFC-002.

## 4.1 COG Type Grounding

The abstract types above are bound to concrete Lean definitions in the COG kernel:

- **`KernelState`** = `CausalGraph` (from `CausalGraphTheory.State`, RFC-001 §2).
  A DAG of `Node` (each carrying `state : ComplexOctonion ℤ` and `tickCount : Nat`) and
  `Edge` (each carrying `operator : ComplexOctonion ℤ` and an `EdgeLabel` gauge type).

- **`Message`** = an `Edge` with `edge.target = v.id` delivered to node `v` at tick `t`.
  The message payload is `edge.operator : ComplexOctonion ℤ`.

- **`Past_t(v)`** = `{u | CausalGraph.reachable G u v}` where `reachable` is the
  transitive closure of the edge relation, proved to be a strict partial order in
  **CAUS-001** (`CausalGraphTheory.CausalOrder`, theorems `reachable_irrefl`,
  `reachable_asymm`, `reachable_trans`). The key lemma `reachable_implies_lt` shows
  that `reachable G u v` implies `u < v` (in node ID order), guaranteeing that
  `Past_t(v)` is always finite and well-founded.

- **`IncomingBoundary_t(v)`** = `G.edges.filter (fun e => e.target == v.id)`, i.e.,
  the direct one-hop causal inputs at tick `t`. This is the strict-cone interpretation.

- The acyclicity invariant `forall e in G.edges, e.source < e.target` (proved in
  **DAG-001**, `CausalGraphTheory.DAGProof`, theorem `step_preserves_acyclic`) ensures
  `Past_t(v)` is strictly smaller than `v` in ID order and cannot loop back.

## 4.2 Update Rule Contract (Partially Settled 2026-02-26)

The abstract `U` in §4 is resolved into the following concrete structure.
Three components are locked as architecture decisions (D7–D9 in §5).
One component — the `combine` operator — remains open (see §10, Q5).

**Initial data extension.** `NodeStateV2` carries one additional field:

```
colorLabel : FanoPoint    -- 0-indexed Fano point (0..6), fixed at graph construction
```

This is the "superdetermined initial condition": color labels are assigned at
initialization and never change. Together with the DAG topology they fully determine
every edge operator for all future time.

**Settled update structure.** Let `v` be a node at tick `t` with incoming edges
`{u₁ → v, ..., uₖ → v}` sorted in increasing `topoDepth(uᵢ)` order, ties broken
by ascending node ID (RFC-002 deterministic ordering):

```
base_v(t)         := T(ψ_v(t))                          -- free temporal commit: e7 *_L ψ_v(t)
msg_i(t)          := L_{e_{colorLabel(uᵢ)}}(ψ_{uᵢ}(t)) -- color-charge message from uᵢ
interaction_v(t)  := fold_left(D8-order)(msg₁, ..., msgₖ)
ψ_v(t+1)          := combine(base_v(t), interaction_v(t))
```

**Zero-interaction case** (`k = 0`): `ψ_v(t+1) = T(ψ_v(t))`, matching the existing
`nextState` stub in `KernelV2.lean`. The `phi4` phase clock (RFC-023) holds exactly
in this case since `phi4_period4` is proved for the free-evolution path.

**Edge operator uniqueness.** For `colorLabel(u) ≠ colorLabel(v)`, the theorem
`two_points_determine_line` (`Fano.lean:57–61`) uniquely determines the Fano line
through `(colorLabel(u), colorLabel(v))`, giving an unambiguous cyclic rule
`e_{c_u} * e_{c_v} = e_{c_w}`. The operator `L_{e_{c_u}}` is thus fully determined
by the source label alone and consistent with the locked Fano convention
(`rfc/CONVENTIONS.md §2`).

---

## 5. Architecture Decisions (Locked)

### D1. Cone-local candidate set

At tick `t`, update inputs for node `v` are exactly `IncomingBoundary_t(v)`. No nonlocal heuristic injection is allowed.

### D2. Outside-cone non-influence

For fixed `EvalPlan` and initial microstate, if two runs differ only on nodes outside `Past_t(v)`, then `psi_{t+1}(v)` must be identical.

### D3. Strict vs effective regime must be explicit

Each kernel/operator pair must declare one regime:

1. `strict_cone`: outside-cone effect exactly zero by construction, or
2. `effective_cone`: outside-cone effect bounded by a declared tail estimator.

### D4. Clock compatibility

This RFC does not replace RFC-018:

- `tau_topo` tracks causal ordering progress.
- `tau_int` tracks energy-exchange process count.

Cone-locality constraints apply to both clocks.

### D5. Event-driven equivalence

Skipping null steps is allowed only if the resulting trajectory matches fixed-step replay at all interaction boundaries.

### D6. Fano-7 locality radius (conjectured structural bound)

In the COG octonion kernel, each imaginary axis `e_i` (i = 1..7) participates in exactly
3 of the 7 directed Fano triples. Under strict Fano-triple-only coupling, each node
receives at most one incoming message per triple it participates in, giving `k_t(v) <= 3`
as the expected Fano-sparse fan-in.

The instrumentation threshold `k > 4` (§7) reflects this structure conservatively:

- `k <= 3`: nominal Fano-triple regime.
- `k = 4`: possible quaternionic sub-interaction (two nested Fano triples sharing an
  edge); must be explicitly classified.
- `k > 4`: anomalous degree — requires either an `effective_cone` tail declaration or an
  explicit physical mechanism justifying the extra inputs.

This bound is a **model hypothesis** until a formal upper-bound proof is certified in
Lean. The Fano structure and directed-triple convention are locked in `rfc/CONVENTIONS.md`.

### D7. Edge operator assignment: static, color-label-derived

The operator on directed edge `u → v` is determined entirely by the source node's
color label, fixed at graph construction:

```
edgeOp(u → v) := L_{e_{colorLabel(u)}}
```

`colorLabel(u) : FanoPoint` is immutable initial data on `NodeStateV2`. The
`edge.operator` field in the `Edge` type stores the precomputed octonion basis
element `e_{colorLabel(source)}` at construction time.

Rationale: in a causal DAG, edges record past events. Allowing operators to vary
with current node states would permit the present to rewrite the past, violating
causal integrity (D2). Static assignment also enables `edgeOp` to be a pure function
in Lean, making invariance proofs tractable.

### D8. Multi-edge composition order: depth-first left fold

When `k_t(v) > 1`, message contributions are composed in strictly increasing
`topoDepth` order of their source nodes (left-to-right fold). Ties in `topoDepth`
are broken by ascending node ID, consistent with RFC-002 deterministic tick ordering.

This decision resolves all non-associative ordering ambiguities: the causal graph
topology (fixed at initialization) imposes a total order on every set of causal
ancestors. No additional runtime disambiguation is needed.

### D9. Temporal-first composition

The free temporal tick `T(ψ) := e7 *_L ψ` is applied to `ψ_v(t)` **before**
interaction contributions are folded in (see §4.2 update structure).

Rationale: this keeps the `phi4` phase clock (RFC-023, `PhaseClock.lean`) invariant
under interaction — the phase advances by exactly +1 mod 4 per tick regardless of
how many incoming edges fire. The theorems `phi4_period4` and `phase_uncertainty_not_energy`
in `PhaseClock.lean` are proved for the free-evolution case and remain valid because
temporal commit is separated from interaction.

---

## 6. Required Invariants

1. `ConeDeterminism`: `Past_t(v)` and `IncomingBoundary_t(v)` are pure functions of kernel state and immutable plan.
2. `NoConeLeak`: local update output at `(t, v)` is invariant under any outside-`Past_t(v)` perturbation.
3. `FinitePropagation`: causal influence per tick obeys declared locality radius.
4. `ReplayInvariance`: same initial microstate and plan produce bit-identical traces.
5. `SchedulerEquivalence`: fixed-step and event-driven traces agree at interaction boundaries.

---

## 7. Instrumentation Contract

Each run must log:

1. `k_t(v)` distribution and `P(k > 4)`.
2. Cone width/depth metrics for updated nodes.
3. `no_cone_leak` test outcomes.
4. If `effective_cone`: measured tail magnitude outside cone.
5. Replay hash and fixed-vs-event equivalence verdict.

---

## 8. Lean and Python Targets

## 8.1 Lean targets

### 8.1.1 `CausalGraphTheory/KernelV2.lean` — `colorLabel` extension

Add `colorLabel : FanoPoint` to `NodeStateV2` (D7 initial data).
Update `vacuumState` to supply a default label (e.g. `colorLabel := ⟨6, by omega⟩`
for the e7 vacuum axis).

### 8.1.2 `CausalGraphTheory/UpdateRule.lean` (new)

Imports: `CausalGraphTheory.KernelV2`, `CausalGraphTheory.Fano`, `Mathlib.Tactic`.

Definitions:

```lean
-- Edge operator: left-multiplication by the source's color-labeled basis element.
def edgeOp (label : FanoPoint) : ComplexOctonion ℤ → ComplexOctonion ℤ :=
  fun psi => ComplexOctonion.basisMul (label.val) psi  -- e_{label} *_L psi

-- Sort incoming edges by source topoDepth, breaking ties by source nodeId.
def depthOrdered (edges : List (NodeStateV2 × NodeStateV2)) :
    List (NodeStateV2 × NodeStateV2) :=
  edges.mergeSort (fun a b =>
    a.1.topoDepth < b.1.topoDepth ∨
    (a.1.topoDepth = b.1.topoDepth ∧ a.1.nodeId < b.1.nodeId))

-- Free temporal commit (alias for nextState restricted to base tick).
def temporalCommit (s : NodeStateV2) : NodeStateV2 := nextState s
```

Theorem targets:

1. `edgeOp_unique` — for `c₁ ≠ c₂ : FanoPoint`, `edgeOp c₁ ≠ edgeOp c₂`
   (follows from distinctness of Fano basis elements; connects to D7 uniqueness).
2. `depthOrdered_totalOrder` — `depthOrdered` produces a unique canonical ordering
   (connects to `ConeDeterminism` and D8).
3. `temporalCommit_advances_phi4` — `phi4 (temporalCommit s) = phi4 s + 1`
   (already proved as `phi4_advances` in `PhaseClock.lean`; re-export or alias here).
4. `temporal_first_preserves_period4` — applying D9 order (temporal commit before fold)
   keeps the free-evolution period-4 property.

### 8.1.3 `CausalGraphTheory/Lightcone.lean` (original target, unchanged)

Add module importing from `CausalGraphTheory.State` and `CausalGraphTheory.CausalOrder`.

```lean
def pastCone (G : CausalGraph) (v : Nat) : Finset Nat := ...

def incomingBoundary (G : CausalGraph) (v : Nat) : List Edge :=
  G.edges.filter (fun e => e.target == v)

def noConeLeak (G : CausalGraph) (v : Nat) : Prop := ...
```

Theorem targets:

1. `incomingBoundary_deterministic` — pure function of `G` and `v`.
2. `pastCone_subset_lt` — corollary of CAUS-001 `reachable_implies_lt`.
3. `outside_pastCone_perturbation_invariant` — formalizes `NoConeLeak` (D2).
4. `fixed_event_equiv_at_boundaries` — under RFC-018 assumptions.

## 8.2 Python targets

Add/update:

- cone-extraction utility for each tick/node
- deterministic outside-cone perturbation test harness
- fixed-step vs event-driven equivalence harness
- dashboard metrics for cone occupancy and leak flags

Required tests:

1. perturbing outside past cone does not change local update result
2. perturbing inside past cone can change local update result (sanity check)
3. fixed-step/event-driven equivalence
4. determinism replay hash

---

## 9. Falsification and Decision Tests

1. **Leak test:** if outside-cone perturbations affect local update under `strict_cone`, kernel is invalid.
2. **Tail test:** if `effective_cone` tails are large enough to alter priority observables, strict-cone approximation is invalid.
3. **Clock test:** if cone-locality holds for `tau_topo` but fails for `tau_int`, energy predicate implementation is inconsistent.
4. **Scheduler test:** if event-driven diverges from fixed-step at interaction boundaries, event mode is not admissible.

---

## 10. Open Questions

1. What is the minimal effective locality radius for each operator family, given the D7 color-label
   scheme? (D6 bounds `k_t(v) ≤ 3` for Fano-sparse coupling; does D7 tighten this?)
2. Does measured cone-tail behavior stay negligible for target observables under high-depth runs?
3. Which observables are most sensitive to rare high-`k` cone intersections?
4. How should cone-locality be represented in claims metadata (`strict_cone` vs `effective_cone`)?
5. **What is the `combine` operator?** Options: (a) additive — `ψ_v(t+1) = base + interaction`
   (natural for a ℤ-module); (b) multiplicative — `ψ_v(t+1) = base * interaction` (octonion
   product); (c) a projection onto a specific sector. The choice must be constrained by
   conservation laws (color charge, energy accounting from RFC-015/RFC-018) and must yield
   a well-typed `ComplexOctonion ℤ`. This is the single remaining open element in the
   update rule contract. Settle before writing the `combine` step in `UpdateRule.lean`.

---

## 11. Governance Impact

1. Any claim that assumes locality must specify whether it depends on `strict_cone` or `effective_cone`.
2. Any optimization that truncates cone inputs must report an empirical error bound.
3. No claim may treat nonlocal behavior as "debug noise"; it must be classified as model failure, approximation, or explicit operator design.

---

## 12. References

1. S. W. Hawking, A. R. King, P. J. McCarthy (1976), *A new topology for curved space-time which incorporates the causal, differential, and conformal structures*. https://doi.org/10.1063/1.522874  
2. L. Bombelli, J. Lee, D. Meyer, R. D. Sorkin (1987), *Space-Time as a Causal Set*. https://doi.org/10.1103/PhysRevLett.59.521  
3. D. P. Rideout, R. D. Sorkin (1999), *A Classical Sequential Growth Dynamics for Causal Sets*. https://arxiv.org/abs/gr-qc/9904062  
4. S. Surya (2019), *The causal set approach to quantum gravity*. https://arxiv.org/abs/1903.11544  
5. P. Arrighi, G. Dowek (2012), *Causal graph dynamics*. https://arxiv.org/abs/1202.1098  
6. P. Arrighi, S. Martiel (2016), *Quantum Causal Graph Dynamics*. https://arxiv.org/abs/1607.06700  
7. E. H. Lieb, D. W. Robinson (1972), *The finite group velocity of quantum spin systems*. https://doi.org/10.1007/BF01645779  
8. Z. Wang, K. R. A. Hazzard (2019), *Tightening the Lieb-Robinson Bound in Locally-Interacting Systems*. https://arxiv.org/abs/1908.03997  
9. M. Cheneau et al. (2011), *Light-cone-like spreading of correlations in a quantum many-body system*. https://arxiv.org/abs/1111.0776  
10. S. Johnston (2008), *Particle propagators on discrete spacetime*. https://arxiv.org/abs/0806.3083
11. Nomaan X, F. Dowker, S. Surya (2017), *Scalar Field Green Functions on Causal Sets*. https://arxiv.org/abs/1701.07212
    *(Note: "X" is the author's surname, not an initial.)*
12. F. Finster, N. G. Gresnigt, J. M. Isidro, A. Marciano, C. F. Paganini, T. P. Singh (2024), *Causal Fermion Systems and Octonions*. https://arxiv.org/abs/2403.00360
    *(Connects causal fermion system vacuum structure to octonion symmetries — directly relevant to D6.)*
13. L. Maignan, A. Spicher (2024), *Causal Graph Dynamics and Kan Extensions*. https://arxiv.org/abs/2403.13393
    *(Category-theoretic proof that any local, synchronous, deterministic graph transformation is a Kan extension; provides the most general formal basis for §5 architecture decisions.)*

