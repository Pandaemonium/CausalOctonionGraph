# RFC-086: Projective Universe Axiom and Projective-Unity Kernel

Status: Active Draft (Exploratory, Non-Canonical)
Date: 2026-02-28
Owner: Research Director + Kernel Team
Depends on:
1. `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
2. `rfc/RFC-069_Canonical_Simulation_Artifact_Contract.md`
3. `rfc/RFC-077_CxO_Unity_Profile_and_Projection_Update_Rule.md`
4. `rfc/RFC-078_Superdeterministic_Preregistration_of_Event_Ordering.md`
5. `world_code/Python_code/minimal_world_kernel.py`
6. `world_code/Python_code/minimal_world_kernel_projective_unity.py`

---

## 1. Executive Summary

This RFC formalizes a compact exploratory kernel profile:
1. Universe model: directed acyclic graph (DAG),
2. node state space: `C x O` over a discrete unity alphabet,
3. local evolution: lightcone projection update.

The goal is to provide a bounded, deterministic phase-profile pathway for simulation experiments without replacing the canonical integer kernel.

Decision:
1. `minimal_world_kernel_projective_unity.py` is accepted as an exploratory profile implementation.
2. Canonical claim promotion remains on integer-kernel pathway unless explicit closure gates are passed in a future RFC.

---

## 2. Axiom Profile (Exploratory)

For this profile only:
1. world state is a DAG with fixed parent map,
2. each node carries an 8-slot `C x O` state,
3. each coefficient is constrained to `U5 = {0, +1, -1, +i, -i}`,
4. each tick computes a deterministic projected update from the node's past lightcone.

This RFC defines computational semantics, not a proved continuum equivalence.

---

## 3. State Contract

Coefficient type:
1. Gaussian integer pair `[re, im]` with integer literals.

Allowed alphabet for projective-unity profile:
1. `[0,0]`,
2. `[1,0]`,
3. `[-1,0]`,
4. `[0,1]`,
5. `[0,-1]`.

Input policy:
1. strict mode rejects non-unity initial coefficients,
2. optional compatibility mode projects initial coefficients to unity before run.

---

## 4. Projector Contract

Projector ID:
1. `pi_unity_axis_dominance_v1`

Definition `Pi_U : Z[i] -> U5`:
1. `Pi_U(0) = 0`,
2. if `|Re(z)| >= |Im(z)|`, map to real axis sign (`+1` or `-1`),
3. else map to imaginary axis sign (`+i` or `-i`),
4. tie breaks to real axis.

Lift to `C x O`:
1. apply `Pi_U` component-wise to all 8 coefficients.

Required invariant:
1. projector idempotence at coefficient and state level (`Pi_U(Pi_U(x)) = Pi_U(x)`).

---

## 5. Update Rule Contract

For node `v` at tick `t`:
1. collect parent messages in deterministic order,
2. compute raw fold by left-associative `C x O` multiplication from identity,
3. compute payload `p_t(v) = Pi_U(fold_raw(messages))`,
4. compute next state `psi_{t+1}(v) = Pi_U(p_t(v) * psi_t(v))`.

Interpretation:
1. fold summarizes incoming lightcone signal,
2. projection enforces bounded unity-state evolution,
3. second projection guarantees closure after local update.

---

## 6. Determinism and Replay Contract

Determinism requirements:
1. node iteration order is canonical and fixed,
2. parent message order per node is canonical and fixed,
3. no randomized branching,
4. tie-break rules are explicit and deterministic.

Replay requirement:
1. same input JSON + same step count -> byte-equivalent state payload after serialization.

---

## 7. Artifact Metadata Contract

Output artifacts for this profile must include:
1. `kernel_profile: "projective_unity_v1"`,
2. `projector_id: "pi_unity_axis_dominance_v1"`,
3. explicit unity alphabet declaration.

If used for physics-facing claims:
1. include canonical integer-baseline companion run,
2. include delta report against baseline observables.

---

## 8. Governance Boundary

Locked by this RFC:
1. projective-unity kernel is an approved exploratory pathway,
2. integer kernel remains canonical for promotion unless separately upgraded.

Explicit non-goals:
1. no claim here that projective-unity profile is physically complete,
2. no claim here that it is equivalent to continuum EFT,
3. no claim here that it supersedes integer-kernel derivations.

---

## 9. Validation Gates

Gate P1: projector idempotence
1. unit tests must prove coefficient/state idempotence.

Gate P2: unity closure
1. all coefficients remain in `U5` after any run horizon.

Gate P3: strict input contract
1. strict mode rejects non-unity input,
2. compatibility mode projects and runs deterministically.

Gate P4: replay determinism
1. repeated runs from same input and steps produce identical outputs.

Gate P5: profile disclosure
1. simulation outputs include `kernel_profile` and `projector_id`.

---

## 10. Immediate Next Steps

1. Add dedicated tests for `minimal_world_kernel_projective_unity.py`.
2. Add profile mention to `world_code/Python_code/README.md`.
3. Add profile validator hooks in promotion pipeline so exploratory outputs cannot be mislabeled as canonical.

