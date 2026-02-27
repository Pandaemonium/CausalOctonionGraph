# RFC-064: Superdeterminism and Lightcone Information Volume

Status: Active Draft - Contract Lock Candidate (2026-02-27)
Module:
- `COG.Theory.Superdeterminism`
Depends on:
- `rfc/RFC-002_Deterministic_Tick_Ordering.md`
- `rfc/RFC-022_Lightcone_Semantics_and_Causal_Locality.md`
- `rfc/RFC-023_Discrete_Phase_Clocks_and_Relative_Phase_Interactions.md`
- `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
- `rfc/RFC-042_D4_D5_Implementation_Closure.md`

---

## 1. Executive Summary

This RFC formalizes the superdeterministic reading of COG:
1. if the exact initial microstate is known,
2. and the update rule/scheduler are fixed,
3. and no exogenous interaction is injected after initialization,
then the full microstate at arbitrary future tick is exactly determined.

For local prediction of node `v` at tick `t`, the required information is exactly the information content of `v`'s backward light cone (plus the globally fixed rulebook).

Core statement:
1. uncertainty is epistemic (missing cone data), not ontic (kernel randomness).

---

## 2. Problem Statement

COG already locks:
1. deterministic ordering and parenthesization (RFC-002),
2. cone-local admissible influence (RFC-022),
3. deterministic phase clock semantics (RFC-023),
4. deterministic update-rule core (RFC-028).

What is missing is one explicit contract saying:
1. what "perfect predictability" means in COG,
2. exactly what information must be known to predict a state,
3. how this requirement scales with light-cone volume.

---

## 3. Scope and Non-Scope

In scope:
1. deterministic predictability contract,
2. light-cone information requirement for exact local prediction,
3. phase reconstruction implications.

Out of scope:
1. claiming practical computability for large cones,
2. adding stochastic kernel terms,
3. claiming any Bell-test loophole result from this RFC alone.

---

## 4. Formal Contract

Let:
1. `m_t` be full microstate at discrete tick `t`,
2. `F` be the deterministic round update map (scheduler + update + spawn/projection policy),
3. `m_0` be initial microstate.

Closed-system assumption:
1. after `t = 0`, no exogenous writes occur to kernel state (`NoExogenousInput`).

Then:
1. `m_t = F^t(m_0)` for all `t >= 0`.

Uniqueness clause:
1. if two runs have identical `(m_0, F)`, they must have identical `m_t` at all `t`.

This is the replay form of superdeterminism in COG.

---

## 5. Lightcone Information Requirement

For node `v` at tick `t`, define required prediction set:
1. `Req(v,t)` = all initial microstate data and fixed edge/operator metadata in `Past_t(v)`,
2. plus globally fixed kernel metadata (`F`).

Strict-cone predictability law:
1. if two runs agree on `Req(v,t)`, then they must produce the same local state for `(v,t)`.

Interpretation:
1. to know `psi_t(v)` exactly, you must know the full causal past data of `v` (not the entire universe if the cone is bounded).

Define information volume (implementation-neutral):
1. `IV(v,t) := bits(encode(Req(v,t)))`.

Practical scaling expectation:
1. exact local prediction cost scales with backward light-cone size,
2. exact global-slice prediction cost scales with the union of all target cones at that slice.

---

## 6. Phase Predictability

Given RFC-023 phase clock:
1. `phi4(s) = s.tickCount mod 4`.

Under deterministic update:
1. phase at `(v,t)` is exactly predictable from initial phase and deterministic tick/spawn history in `Past_t(v)`.

So:
1. apparent phase uncertainty comes from incomplete cone knowledge,
2. not from intrinsic phase randomness.

---

## 7. Information-Completeness Statement

For any target set `T` of nodes at tick `t`:
1. exact prediction is possible iff observer information covers `Req(T,t) := union_{v in T} Req(v,t)` plus fixed `F`.

Equivalent operational statement:
1. missing information outside `Req(T,t)` is irrelevant,
2. missing information inside `Req(T,t)` creates epistemic uncertainty.

This is the precise COG meaning of:
1. "information volume needed for perfect prediction equals the target light-cone information volume."

---

## 8. Falsification Gates

Reject this RFC contract if any occur:
1. replay divergence: two runs with same `(m_0, F)` produce different traces,
2. cone violation: perturbation outside `Past_t(v)` changes `psi_t(v)` under strict-cone mode,
3. phase reconstruction failure: `phi4` computed from deterministic history disagrees with observed node state,
4. hidden exogenous dependency: runtime outcome depends on wall-clock, RNG, or nondeterministic iteration order.

---

## 9. Implementation Plan

### 9.1 Lean targets

Add module:
1. `CausalGraphTheory/Superdeterminism.lean`

Initial theorem targets:
1. `replay_unique` (same init + same rulebook -> same trace),
2. `local_state_cone_sufficient` (agreement on `Req(v,t)` -> equal local state),
3. `phi4_from_deterministic_history` (phase determined by deterministic history only).

### 9.2 Python targets

Add scripts:
1. `calc/superdeterministic_replay_audit.py`,
2. `calc/lightcone_information_volume_scan.py`.

Required outputs:
1. replay hash consistency report,
2. cone-perturbation invariance report,
3. `IV(v,t)` and `IV(T,t)` growth diagnostics over benchmark motifs.

---

## 10. Governance Impact

Any claim using words like "random", "uncertain", or "entropy" must now declare:
1. whether it is ontic (kernel-level) or epistemic (observer-level),
2. the target set `T`,
3. the declared information boundary used by the observer.

Promotion rule:
1. ontic-randomness claims are invalid unless they explicitly override this RFC and provide a new kernel contract.

---

## 11. Open Questions

1. Best canonical encoder for `bits(encode(Req(v,t)))` across Lean/Python pipelines.
2. How to report cone information volume for dynamic spawn-heavy regimes (D4-intensive runs).
3. Whether practical approximations (effective-cone truncations) preserve priority observables under bounded error.

---

## 12. References

1. `rfc/RFC-002_Deterministic_Tick_Ordering.md`
2. `rfc/RFC-022_Lightcone_Semantics_and_Causal_Locality.md`
3. `rfc/RFC-023_Discrete_Phase_Clocks_and_Relative_Phase_Interactions.md`
4. `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
5. `rfc/RFC-042_D4_D5_Implementation_Closure.md`
6. M. J. W. Hall (2010), *Relaxed Bell inequalities and Kochen-Specker theorems*. https://arxiv.org/abs/1007.5518
7. S. Hossenfelder, T. Palmer (2020), *Rethinking Superdeterminism*. https://arxiv.org/abs/1912.06462
