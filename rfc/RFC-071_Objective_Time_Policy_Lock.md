# RFC-071: Objective Time Policy Lock

Status: Active Draft - Lock Candidate (2026-02-27)
Module:
- `COG.Core.ObjectiveTime`
- `COG.Core.LightconeClock`
Depends on:
- `rfc/RFC-018_Time_as_Graph_Depth_and_Interaction_Clock.md`
- `rfc/RFC-022_Lightcone_Semantics_and_Causal_Locality.md`
- `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
- `rfc/RFC-064_Superdeterminism_and_Lightcone_Information_Volume.md`
- `rfc/RFC-067_Objective_Time_as_Graph_Depth.md`
- `rfc/RFC-069_Canonical_Simulation_Artifact_Contract.md`

---

## 1. Executive Summary

This RFC locks one core COG claim:
1. time is objective,
2. objective time is graph depth (`topoDepth`),
3. it is not observer-dependent.

`tickCount` remains a local process counter (proper-time analogue), but it does not replace global objective time.

---

## 2. Policy Statement (Locked)

In canonical COG:
1. physical event order is determined by causal DAG structure,
2. event time is `topoDepth`,
3. simultaneity is equality of `topoDepth`,
4. no frame-dependent redefinition of event order is allowed.

Equivalent statement:
1. there is one global causal clock in the model,
2. local clocks are derived process observables, not fundamental time.

---

## 3. Formal Contract

Let `G = (V, E)` be the causal DAG.

Define:
1. `topoDepth(v) = 0` for roots,
2. `topoDepth(v) = 1 + max { topoDepth(u) | (u, v) in E }` otherwise.

Required properties:
1. well-defined (acyclic graph),
2. unique per node,
3. integer-valued,
4. strictly increasing along edges:
   - if `(u, v) in E` then `topoDepth(u) < topoDepth(v)`.

Objective-time definition:
1. `time(v) := topoDepth(v)`.

---

## 4. Two-Clock Clarification

To prevent category errors:

1. `topoDepth`:
   - global, structural, objective time.
2. `tickCount`:
   - local update count for a node/state,
   - can vary across nodes with different histories,
   - source of clock-rate differences in effective/observer descriptions.

Lock:
1. `tickCount` is never used to reorder causal event precedence.

---

## 5. Simulation Requirements

All canonical simulation artifacts must:
1. include enough topology to compute `topoDepth` exactly,
2. preserve deterministic ordering semantics from RFC-028,
3. report depth explicitly when reporting event traces.

Under RFC-069:
1. objective time must come from the shared base simulation contract,
2. observables may project/aggregate it, but may not redefine it.

---

## 6. What This Excludes

This lock excludes:
1. hidden wall-clock dependence as physical time,
2. observer-frame-dependent event order in canonical kernel semantics,
3. stochastic time advancement in canonical runs.

This lock does not exclude:
1. emergent relativistic behavior at coarse-grained observational layers,
2. local clock-rate differences (`tickCount` effects).

---

## 7. Verification Gates

Gate T1: DAG monotonicity
1. assert every edge respects strict depth increase.

Gate T2: replay invariance
1. same initial lightcone + same update rule -> same depth-labeled trace.

Gate T3: simultaneity consistency
1. nodes with equal depth are in same canonical slice,
2. no algorithm path may assign conflicting slice labels.

Gate T4: no exogenous time
1. runtime behavior is independent of wall-clock or nondeterministic sources.

---

## 8. Implementation Checklist

1. Lean:
   - theorem(s) for depth uniqueness and edge monotonicity in canonical kernel modules.
2. Python:
   - deterministic depth computation utility for artifact validation and trace output.
3. Artifact schema:
   - require depth fields in recorded event traces.

---

## 9. Decision Record

Locked by this RFC:
1. objective time in COG is graph depth,
2. `tickCount` is local process time, not global causal time,
3. canonical simulations must preserve and expose depth-based time ordering.

