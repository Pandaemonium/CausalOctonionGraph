# RFC-028: Canonical Update Rule Closure

Status: Active - Decision Draft (2026-02-26)
Module:
- `COG.Core.UpdateRule`
- `COG.Core.Trace`
- `COG.Core.Lightcone`
Depends on:
- `rfc/CONVENTIONS.md`
- `rfc/RFC-002_Deterministic_Tick_Ordering.md`
- `rfc/RFC-020_Kernel_Representation_Reconciliation.md`
- `rfc/RFC-022_Lightcone_Semantics_and_Causal_Locality.md`
- `rfc/RFC-023_Discrete_Phase_Clocks_and_Relative_Phase_Interactions.md`
Literature basis:
- `sources/update_rule_closure_lit_review.md`

---

## 1. Executive Summary

This RFC answers the current architecture question:

"Kernel state is `C x O`; does update depend on lightcone, trace, and superdetermined ordering?"

Answer:
1. Yes, lightcone-local boundary inputs are required.
2. Yes, deterministic ordering/parenthesization must be predeclared in the initial condition.
3. Trace is optional only if the kernel is strictly Markov; otherwise it must be explicit kernel state.
4. The final unresolved piece is the `combine` operator and its conservation contract.

This RFC defines what must be settled before promoting higher-level claims.

---

## 2. Problem Statement

COG has strong pieces already:
1. `C x O`-native node state (RFC-020),
2. deterministic ordering and parenthesization (RFC-002),
3. lightcone-local update framing (RFC-022),
4. phase clock semantics (RFC-023).

But the full transition law is still incomplete:
1. no locked `combine` law,
2. no locked trace-memory contract,
3. no locked mapping from transition class to `tau_int`,
4. no locked projection contract for observer-level uncertainty claims.

Without these, the model is not fully specified.

---

## 3. Canonical Update Skeleton

Let `psi_t(v) : C x O` be node `v` at tick `t`.

Define:
1. `B_t(v)`: incoming boundary messages from the causal past cone boundary.
2. `O_t(v)`: canonical order on `B_t(v)` (topoDepth, then nodeId), with immutable parenthesization.
3. `H_t(v)`: local trace slice (possibly empty for Markov kernels).
4. `T(x) := e7 * x`: temporal commit operator.

Required transition form:

`psi_{t+1}(v) = U( T(psi_t(v)), O_t(v), H_t(v) )`

where `U` is deterministic and free of external entropy.

---

## 4. Superdetermined Initial Condition Contract

To prevent runtime ambiguity, initial microstate must include immutable:

1. initial graph topology and node states,
2. edge operator assignment policy,
3. tie-break key order,
4. parenthesization tree per multi-input interaction family,
5. trace window policy (Markov or finite-memory),
6. scheduler mode contract (fixed-step reference semantics).

No runtime rule may consult wall-clock time, RNG, or nondeterministic container order.

---

## 5. Mandatory Decisions to Close the Update Rule

## D1. Choose one `combine` family

Exactly one must be primary:
1. additive: `U = base + interaction_term`,
2. multiplicative: `U = base * interaction_term`,
3. affine/projection form: `U = P(base, interaction, trace)`.

Closure requirement:
- chosen family must preserve declared invariants and be typed in `C x O`.

## D2. Lock trace semantics

Choose one:
1. Markov (`H_t(v) = empty`, memoryless),
2. finite-memory with explicit window `m`,
3. full-history (allowed only with a bounded representation plan).

## D3. Lock energy-exchange predicate

Define deterministic `isEnergyExchange(transition)` used for `tau_int`.
It must be computable from local transition data only.

## D4. Lock spawn semantics

Specify exact conditions under which a node/edge is spawned, and how spawned state is initialized.

## D5. Lock projection contract

Define observer map `Pi_obs : FullMicrostate -> ObservableState`.
Uncertainty claims must reference this map, not informal "hidden information" language.

---

## 6. Invariants and Gates

All must pass before promoting derived-constant claims:

1. Determinism: identical init state and plan gives identical trace hash.
2. No exogenous information: no randomness, no nondeterministic iteration dependence.
3. Cone locality: outside-past-cone perturbations do not change local update under strict-cone mode.
4. Scheduler equivalence: event-driven and fixed-step agree at interaction boundaries.
5. Clock consistency: `tau_topo` monotonic on causal edges, `tau_int` increments only on declared energy exchanges.
6. Trace policy consistency: if `m=0`, transition is provably history-independent.

---

## 7. Lean and Python Deliverables

## 7.1 Lean deliverables

Add module(s):
1. `CausalGraphTheory/UpdateRule.lean`
2. `CausalGraphTheory/TraceSemantics.lean`

Minimum theorem targets:
1. `incomingBoundary_deterministic`
2. `orderedBoundary_unique`
3. `update_deterministic`
4. `no_exogenous_information`
5. `outsideConeInvariant_strict`
6. `markov_if_m0`

## 7.2 Python deliverables

Add script(s):
1. `calc/update_rule_ablation.py`
2. `calc/no_cone_leak_tests.py`
3. `calc/fixed_vs_event_equivalence.py`

Required outputs:
1. trace hashes across replay runs,
2. leak score under outside-cone perturbations,
3. divergence report for scheduler comparison,
4. sensitivity table for `m` and `k_max` choices.

---

## 8. Literature-Constrained Policy

Adopted:
1. local bounded-speed update constraints,
2. explicit memory semantics for non-Markov dynamics,
3. operational no-signaling audits for correlation claims.

Not adopted as theorem:
1. any specific `combine` law,
2. blanket assumption that `k > 4` is negligible,
3. "superdeterminism implies no-signaling" (must still be tested).

---

## 9. Claim Governance Impact

Until this RFC is closed:
1. no claim can be upgraded to "model-derived" if it depends on unspecified `combine` behavior,
2. uncertainty/entropy claims remain provisional unless tied to `Pi_obs`,
3. scheduler-dependent results must be labeled unstable.

---

## 10. Recommended Execution Order

1. Lock D1 (`combine`) with one-page decision note and counterexample checks.
2. Lock D2 (`trace`) and implement `m=0` and one `m>0` baseline.
3. Lock D3 (`isEnergyExchange`) and wire to `tau_int`.
4. Implement invariants and replay/leak/equivalence harnesses.
5. Only then resume deeper constant-derivation pushes.

---

## 11. References

1. P. Arrighi, G. Dowek (2012), Causal graph dynamics, https://arxiv.org/abs/1202.1098
2. P. Arrighi, S. Martiel (2016), Quantum Causal Graph Dynamics, https://arxiv.org/abs/1607.06700
3. L. Maignan, A. Spicher (2024), Causal Graph Dynamics and Kan Extensions, https://arxiv.org/abs/2403.13393
4. D. P. Rideout, R. D. Sorkin (1999), Classical Sequential Growth Dynamics for Causal Sets, https://arxiv.org/abs/gr-qc/9904062
5. S. Surya (2019), The causal set approach to quantum gravity, https://arxiv.org/abs/1903.11544
6. F. A. Pollock et al. (2018), Operational Markov Condition for Quantum Processes, https://arxiv.org/abs/1801.09811
7. G. Chiribella, G. M. D'Ariano, P. Perinotti (2008), Quantum Circuit Architecture, https://arxiv.org/abs/0803.3231
8. M. J. W. Hall (2010), Relaxing measurement independence, https://arxiv.org/abs/1007.5518
9. A. S. Friedman et al. (2019), Measurement dependence in Bell tests, https://arxiv.org/abs/1901.04521
10. S. Hossenfelder, T. Palmer (2020), Rethinking Superdeterminism, https://arxiv.org/abs/1912.06462
