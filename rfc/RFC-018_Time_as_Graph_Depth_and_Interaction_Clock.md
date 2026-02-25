# RFC-018: Time as Graph Depth and Interaction Clock

**Status:** Active - Architecture Draft (2026-02-25)  
**Module:** `COG.Core.Time` and `COG.Core.Scheduler`  
**Dependencies:** `rfc/RFC-001_Canonical_State_and_Rules.md`, `rfc/RFC-002_Deterministic_Tick_Ordering.md`, `rfc/RFC-016_Kernel_v1_Contract.md`  
**Literature basis:** `sources/time_as_graph_depth_lit_review.md`

---

## 1. Executive Summary

This RFC formalizes time in COG as two deterministic observables over a causal graph:

- `tau_topo`: topological causal depth (ordering clock)
- `tau_int`: interaction count tied to energy-exchange updates (process clock)

This split resolves a recurrent ambiguity: many ticks contain no state update.  
Depth still advances in the causal graph, but interaction-time does not.

The RFC also locks:

1. Candidate interactions are derived from the incoming causal lightcone.
2. Multiplicity `k` (number of incoming messages at a step) is an explicit observable.
3. `k > 4` is treated as a measurable tail, not a hard axiom.
4. Event-driven execution is allowed only if it is provably equivalent to fixed-step replay.

---

## 2. Motivation

The current program has deterministic update ordering (RFC-002) and a kernel/semantics
contract (RFC-016), but no unified definition of "time" when updates are sparse.

Observed behavior in the model:

- Most local evaluations have no effective incoming interaction (`k = 0`).
- Some evaluations have `k in {1,2,3,4}`.
- Higher multiplicities appear rare and likely low-impact, but this is not yet measured.

Without explicit clocks, the same run can be interpreted inconsistently:

- as many "ticks" (scheduler perspective), or
- as few "physical events" (interaction perspective).

This RFC removes that ambiguity.

---

## 3. Scope

This RFC defines:

- Canonical time observables for COG simulation state.
- Candidate interaction selection from causal neighborhoods.
- Null-step semantics and sparse-update instrumentation.
- Equivalence requirements for fixed-step vs event-driven execution.

This RFC does not define:

- The full quantitative map from `tau_int` to measured SI time.
- A final spectroscopy model.
- A specific mass observable (covered by separate RFC work).

---

## 4. Formal Definitions

### 4.1 Causal Graph and Depth

Let `G_t = (V_t, E_t)` be the DAG at simulation step `t`.  
For node `v`, let `Parents(v)` be incoming causal predecessors.

Define topological depth:

```
tau_topo(v) =
  0                                   if Parents(v) = empty
  1 + max_{p in Parents(v)} tau_topo(p)   otherwise
```

`tau_topo` is a graph-order observable. It exists even when no state update occurs.

### 4.2 Incoming Lightcone Message Multiset

At evaluation point `(t, v)`, define:

```
M_t(v) = multiset of active incoming messages to v
k_t(v) = |M_t(v)|
```

`M_t(v)` must be derived deterministically from:

- kernel state (`KernelState`, RFC-016),
- immutable evaluation plan (`ordered_edges_n`, `paren_tree_n`, RFC-002),
- active edge conditions.

No external entropy source is permitted.

### 4.3 Deterministic Update Function

Let `U(v, M_t(v), plan_v)` be the deterministic local update. Then:

- If `k_t(v) = 0`: no state mutation at `v` (null interaction step).
- If `k_t(v) > 0`: apply canonical update using RFC-002 ordering and parenthesization.

### 4.4 Interaction Clock

Define predicate:

```
is_energy_exchange(t, v) : Bool
```

This predicate is deterministic and computed from post-update state transition semantics
(module-specific details are allowed, but no randomness).

Define interaction clock:

```
tau_int(0) = 0
tau_int(t+1) = tau_int(t) + count_{v evaluated at t}( is_energy_exchange(t, v) )
```

`tau_int` is a process observable, not a replacement for `tau_topo`.

### 4.5 Canonical Time State

For analysis, each event/run state reports:

```
TimeState = {
  topo_depth : Nat,   -- tau_topo
  int_count  : Nat    -- tau_int
}
```

Any single-scalar time used in derived metrics must explicitly specify which component
or projection is being used.

---

## 5. Architecture Decisions (Locked)

### D1. Two-clock model is mandatory

All simulation and reporting interfaces must preserve both `tau_topo` and `tau_int`.

### D2. Lightcone-local candidate set

Candidate interactions at `(t, v)` are exactly `M_t(v)` from active incoming causal edges.
No nonlocal heuristic interaction injection is allowed.

### D3. Sparse updates are first-class

Null interaction steps (`k=0`) are legal and expected. They do not increment `tau_int`.

### D4. `k > 4` is empirical

The claim "higher-than-4 interactions are negligible" is not assumed in kernel logic.
It can be used only as an optimization after instrumentation demonstrates stability.

### D5. Event-driven mode requires equivalence proof

An event-driven scheduler that skips null steps is allowed only if replay-equivalent to
fixed-step execution under the same initial microstate and plan.

---

## 6. Required Invariants

1. `Determinism`: local update and scheduler behavior are pure functions of state + plan.
2. `No Exogenous Information`: no RNG, wall clock, external IO, nondeterministic iteration.
3. `Plan Immutability`: `ordered_edges_n` and `paren_tree_n` never mutate post-initialization.
4. `Clock Monotonicity`:
   - `tau_topo` nondecreasing along causal edges
   - `tau_int` nondecreasing over global steps
5. `Replay Invariance`: repeated runs from same initial microstate are bit-identical.
6. `Scheduler Equivalence`: fixed-step and event-driven produce identical state trajectories
   at all interaction boundaries.

---

## 7. Instrumentation Contract

Every run must emit:

- histogram `P(k)` for `k = 0,1,2,...`
- tail mass `P(k > 4)`
- update ratio `P(k > 0)`
- interaction density `delta(tau_int) / delta(step)`

For each tracked observable `O` (mass ratio, recurrence, spectrum proxy, etc.), report:

- baseline (`no truncation`)
- truncated (`k_max = 4`)
- relative error

`k_max=4` optimization is allowed only when error bounds are accepted in an RFC/claim note.

---

## 8. Lean and Python Implementation Targets

### 8.1 Lean

Add module(s):

- `CausalGraphTheory/Time.lean`
- optional: `CausalGraphTheory/SchedulerEquivalence.lean`

Define:

- `tauTopo : KernelState -> NodeId -> Nat`
- `incomingMessages : KernelState -> NodeId -> Multiset Message`
- `kMultiplicity : KernelState -> NodeId -> Nat`
- `tauInt : Trace -> Nat`

Prove:

- `tauTopo_monotone_on_edges`
- `tauInt_monotone`
- `deterministic_kMultiplicity`
- `fixed_vs_event_scheduler_equiv` (for kernels that satisfy D5 assumptions)

### 8.2 Python

Add/update:

- scheduler metrics in simulation logs
- deterministic event queue keyed only by kernel data
- replay test harness with hash equality across repeated runs

Required tests:

1. same input, repeated runs, identical hashes
2. `P(k)` generated and persisted
3. fixed-step vs event-driven equivalence on identical seeds/microstates
4. truncation sensitivity report for `k_max=4`

---

## 9. Validation Checklist

- [ ] `tau_topo` implemented and logged.
- [ ] `tau_int` implemented and logged.
- [ ] `k_t(v)` computed deterministically from kernel state.
- [ ] Null-step semantics validated (`k=0` causes no mutation).
- [ ] `P(k)` and `P(k>4)` reported per run.
- [ ] Fixed-step and event-driven equivalence test passes.
- [ ] No exogenous information paths in scheduling/update code.

---

## 10. Risks and Open Questions

1. **Energy predicate definition risk:** `is_energy_exchange` must be precise and shared
   across Lean and Python, or clock mismatch will appear.
2. **Depth convention risk:** if multiple depth definitions are used (rank vs longest-chain),
   derived claims become incomparable.
3. **Rare high-k events risk:** low frequency does not guarantee low impact.
4. **Projection risk:** any single scalar "time" derived from `(tau_topo, tau_int)` must be
   explicitly justified per claim.

---

## 11. Literature Alignment

This RFC adopts structure consistent with:

- causal-order-first time reconstruction (causal sets),
- local finite-speed interaction constraints (causal graph dynamics / Lieb-Robinson style),
- sparse event-driven simulation practice.

It does **not** claim that literature already proves COG's full energy-time mapping.
That mapping remains a project theorem to be derived.

See: `sources/time_as_graph_depth_lit_review.md`.

