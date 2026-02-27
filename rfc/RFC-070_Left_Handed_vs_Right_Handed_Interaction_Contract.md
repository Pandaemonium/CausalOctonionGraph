# RFC-070: Left-Handed vs Right-Handed Interaction Contract

Status: Active Draft - Policy Lock Candidate (2026-02-27)
Module:
- `COG.Dynamics.Handedness`
- `COG.WorldKernel.HandSchedule`
Depends on:
- `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
- `rfc/RFC-063_XOR_Octonion_Gate_and_Signed_Handed_Dynamics.md`
- `rfc/RFC-065_XOR_Vector_Spinor_Operator_and_Ideal_Stabilization.md`
- `rfc/RFC-069_Canonical_Simulation_Artifact_Contract.md`
- `world_code/Lean_code/MinimalWorldKernel.lean`
- `world_code/Python_code/minimal_world_kernel.py`

---

## 1. Executive Summary

RFC-063 already locks the algebraic handedness fact:
1. distinct-imaginary products share output index under left/right action,
2. sign flips between left and right.

This RFC adds the simulation contract level:
1. how handedness is represented in a world run,
2. how a run selects left, right, or mixed interaction mode,
3. what must remain deterministic and replayable.

---

## 2. Problem Statement

Current kernels can evolve a full lightcone deterministically, but they do not yet
standardize a single runtime contract for:
1. left-only interaction mode,
2. right-only interaction mode,
3. mixed handed schedules.

Without this, two users can run the same initial lightcone and claim they used
"handed interactions" while actually using different implicit policies.

---

## 3. Handedness Interaction Contract

## 3.1 Primitive actions

For operator `op` and state `x`:
1. `LeftAct(op, x) := op * x`
2. `RightAct(op, x) := x * op`

Multiplication is exactly the canonical `C x O` product already locked by Fano orientation.

## 3.2 Distinct-imaginary law (inherited)

For distinct imaginary basis units:
1. output basis index matches under left and right,
2. sign flips under hand swap.

This is inherited from RFC-063 and not re-opened here.

## 3.3 Hand schedule (new runtime requirement)

Each simulation must declare one hand schedule:
1. `left_only`
2. `right_only`
3. `mixed_deterministic`

`mixed_deterministic` must be generated from declared state data only (no RNG, no wall clock).

---

## 4. World Artifact Requirements

Under RFC-069 artifact contract, add required field:
1. `hand_schedule_spec`

Minimum schema:
1. `mode`: `left_only | right_only | mixed_deterministic`
2. `rule_id`: stable identifier of schedule rule
3. `rule_source`: file path or embedded expression
4. `hash`: content hash

Interpretation:
1. handedness is part of dynamics, not an observable.
2. changing hand schedule means changing the physical simulation policy.

---

## 5. Determinism Requirements

A conforming implementation must satisfy:
1. same `initial_lightcone_state` + same `update_rule` + same `hand_schedule_spec` + same steps
   -> identical final state hash.
2. no hidden entropy source in schedule generation.
3. canonical parent/message ordering remains unchanged by hand mode.

---

## 6. Minimal Kernel Mapping

This RFC does not require adding observables or macrostate logic.

Minimal kernel changes are limited to:
1. expose two primitive actions (`left` and `right`),
2. select action via declared hand schedule,
3. keep everything else unchanged.

In `world_code/Python_code/minimal_world_kernel.py`, this is one switch at update time:
1. `payload * current` (left),
2. `current * payload` (right),
3. deterministic branch for mixed mode.

Lean kernel mirror:
1. add `Hand := left | right`,
2. add deterministic `handAt : World -> NodeId -> Hand`,
3. define update with `match handAt ...`.

---

## 7. Physics Interpretation Boundary

This RFC defines interaction semantics, not Standard Model chirality matching by itself.

Specifically:
1. It does not claim electroweak chirality is fully derived yet.
2. It locks a deterministic left/right interaction substrate required before those claims.

---

## 8. Verification Gates

Gate H1: Algebra gate
1. test left/right sign-flip property on distinct imaginary basis pairs.

Gate H2: Replay gate
1. run same config twice, assert identical output hash.

Gate H3: Mode separation gate
1. same initial state under `left_only` vs `right_only` should produce diverging traces
   on at least one nontrivial case.

Gate H4: Mixed schedule determinism gate
1. `mixed_deterministic` schedule reproduces exactly across runs.

---

## 9. Immediate Implementation Tasks

1. Add `hand_schedule_spec` to world simulation input schema.
2. Add hand-mode switch to minimal Python kernel.
3. Add Lean type/signature for handed update mode in minimal kernel file.
4. Add deterministic replay tests for all three hand modes.

---

## 10. Decision Record

Locked by this RFC:
1. left-handed vs right-handed interaction is a first-class part of update dynamics,
2. hand schedule must be explicitly declared in simulation artifacts,
3. no stochastic handedness policy is allowed in canonical runs.

