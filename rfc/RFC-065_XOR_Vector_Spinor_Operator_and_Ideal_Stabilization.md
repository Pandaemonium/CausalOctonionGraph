# RFC-065: XOR Vector/Spinor Unified Operator and Ideal Stabilization

Status: Active Draft - Contract Proposal (2026-02-27)
Module:
- `COG.Algebra.XORUnified`
- `COG.Spinor.IdealStabilizer`
Depends on:
- `rfc/CONVENTIONS.md` (Furey convention lock)
- `rfc/RFC-063_XOR_Octonion_Gate_and_Signed_Handed_Dynamics.md` (XOR gate contract)
- `rfc/RFC-056_Spin_as_Missing_H_Factor.md` (spin observable governance)
- `CausalGraphTheory/WittBasis.lean`
- `CausalGraphTheory/FureyChain.lean`
- `CausalGraphTheory/Spinors.lean`

---

## 1. Executive Summary

This RFC proposes one operator family for both:
1. vector motifs (basis-sparse octonion states), and
2. spinor motifs (Furey minimal-left-ideal states),

using the same XOR multiplication kernel:
1. index channel: `k = i xor j` (distinct imaginaries),
2. sign channel: locked Fano orientation,
3. handedness channel: left vs right action.

Key extension:
1. spinor motifs require an extra stabilization stage around the XOR update to remain in a stable ideal class.
2. vector motifs do not require this stage.

---

## 2. Problem Statement

Current XOR runtime is strong for vector-style motifs:
1. deterministic,
2. replayable,
3. stable-cycle extraction already implemented.

But spinor/ideal motifs introduce a second constraint:
1. we care not only about state evolution,
2. we also care whether the state remains inside a chosen ideal sector (`S^u` or `S^d` style construction).

Without an explicit ideal stabilizer:
1. repeated XOR updates can drift out of the intended ideal manifold (or into equivalent but non-canonical representatives),
2. motif identity becomes unstable even if raw dynamics remain deterministic.

---

## 3. Unified Operator Contract

Let `X` be any state encoded as Gaussian-integer octonion coefficients over basis `e0..e7`.

Define one primitive operator:
1. `U(op, X, hand) := oct_mul_xor(op, X)` for left hand,
2. `U(op, X, hand) := oct_mul_xor(X, op)` for right hand.

Same `U` is used for both vectors and spinors.

No separate "spinor operator algebra" is introduced at the kernel level.

---

## 4. State Classes

## 4.1 Vector class

Definition:
1. sparse support on selected basis channels,
2. no ideal-membership constraint.

Update:
1. `X_{t+1} = U(op_t, X_t, hand_t)`.

## 4.2 Spinor-ideal class

Definition:
1. state built from ladder chains on idempotent vacuum projectors,
2. must remain in declared ideal family (`S^u` or `S^d`) under evolution policy.

Update (proposed):
1. `X_{t+1} = StabilizeIdeal( U(op_t, PreconditionIdeal(X_t), hand_t), ideal_spec )`.

---

## 5. Why Spinors Need Extra Computation

For vectors, closure target is simple support/cycle behavior.

For spinors, stability means:
1. preserve ideal family constraints,
2. preserve canonical representative class,
3. avoid coefficient-gauge ambiguity from equivalent scaled/phased forms.

Therefore spinors need extra computation that vectors do not:
1. ideal projection/repair,
2. canonical normalization,
3. consistency checks against ideal constraints.

---

## 6. Spinor Stabilization Pipeline (Proposed)

Given `ideal_spec in {Su, Sd}`:

1. **PreconditionIdeal**
   - map state into declared ideal frame using fixed projector sandwich:
     - `Su`: relative to `omega`,
     - `Sd`: relative to `omega^dagger`.
   - enforce fixed parenthesization order.

2. **Apply Unified XOR Operator**
   - apply `U(op, X, hand)` exactly as for vectors.

3. **Project/Re-anchor**
   - apply ideal re-anchor transform to remove out-of-ideal leakage components.

4. **Canonical Normalize**
   - divide by coefficient gcd where defined,
   - fix discrete phase/sign convention (deterministic pivot coefficient rule).

5. **ValidateIdeal**
   - verify declared ideal predicates hold.
   - if not, mark transition invalid for ideal-stability runs.

This yields deterministic ideal-preserving trajectories.

---

## 7. Minimal Formal Contracts

## C1. Operator identity
1. Same `U` implementation is used for vector and spinor classes.

## C2. Determinism
1. Stabilization pipeline has no randomness or order ambiguity.

## C3. Idempotent canonicalization
1. `Canonicalize(Canonicalize(X)) = Canonicalize(X)`.

## C4. Ideal closure under stabilized update
1. If `InIdeal(X_t, spec)`, then `InIdeal(X_{t+1}, spec)` for stabilized runs.

## C5. Replay invariance
1. same `(X0, ops, hands, spec)` gives same trace hash.

---

## 8. Implementation Plan

## 8.1 Python

Add:
1. `calc/xor_spinor_stabilizer.py`
2. `calc/test_xor_spinor_stabilizer.py`
3. `calc/xor_vector_spinor_unified_cycles.py`
4. `calc/test_xor_vector_spinor_unified_cycles.py`

Core functions:
1. `precondition_ideal(state, spec)`
2. `stabilize_ideal(state, spec)`
3. `canonicalize_spinor(state)`
4. `update_unified(state, op_idx, hand, state_class, spec=None)`

Artifacts:
1. `calc/xor_vector_spinor_unified_cycles.json`
2. `website/data/xor_vector_spinor_unified_cycles.json`

## 8.2 Lean (scaffold-first)

Add:
1. `CausalGraphTheory/XorSpinorStabilizer.lean`

Initial theorem targets:
1. canonicalization idempotence,
2. deterministic stabilization,
3. closure lemma skeleton for declared ideal spec.

---

## 9. Falsification Gates

Reject this RFC direction if:
1. vector and spinor paths require different core XOR operator semantics,
2. stabilization introduces nondeterministic branch behavior,
3. canonicalization is not idempotent,
4. stabilized spinor runs still leak from declared ideal at nonzero rate,
5. replay hashes diverge under fixed inputs.

---

## 10. Acceptance Criteria

RFC-065 is `partial` when:
1. unified operator is codified in one runtime path,
2. spinor stabilizer exists and passes deterministic tests,
3. unified-cycle artifacts compare vector vs spinor behavior side-by-side.

RFC-065 is `supported` when:
1. ideal-closure gates pass across benchmark motif suites,
2. Lean scaffold theorems for canonicalization/closure are proven or clearly bounded.

---

## 11. Decision Notes

1. This RFC does **not** replace Furey basis conventions.
2. XOR is an execution notation for multiplication, not a new physical basis claim.
3. Spinor stabilization is a governance and representation contract to keep ideal identity stable under shared operators.

---

## 12. References

1. `rfc/CONVENTIONS.md`
2. `rfc/RFC-063_XOR_Octonion_Gate_and_Signed_Handed_Dynamics.md`
3. `rfc/RFC-056_Spin_as_Missing_H_Factor.md`
4. `CausalGraphTheory/WittBasis.lean`
5. `CausalGraphTheory/FureyChain.lean`
6. `CausalGraphTheory/Spinors.lean`
