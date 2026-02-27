# RFC-056: Spin Observable Contract on CxO Kernel

Status: Active Draft - Corrected Framing (2026-02-26)
Module:
- `COG.Core.SpinObservable`
- `COG.Governance.SpinMode`
Depends on:
- `rfc/CONVENTIONS.md`
- `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
- `rfc/RFC-039_Charge_as_Discrete_Z4_Cycle.md`
- `rfc/RFC-040_Particle_Motif_and_Interaction_Rule_Contract.md`
- `rfc/RFC-043_Motif_Catalog_v1.md`
- `rfc/RFC-044_Projection_Profile_Governance.md`
- `rfc/RFC-049_Benchmark_and_Falsification_Battery_v2.md`
- `rfc/RFC-050_Proof_State_and_Claim_Status_Matrix.md`
- `CausalGraphTheory/KernelV2.lean`
- `CausalGraphTheory/SubalgebraDetect.lean`

---

## 1. Executive Summary

This RFC corrects the prior framing that spin requires adding an external `H` factor because "`H` is missing from `C x O`."

That statement is incorrect in this codebase. `H` is already present as quaternionic subalgebras of `O` (one per Fano line). The real gap is different:
1. the kernel has no explicit spin observable field or operator contract,
2. claims do not yet carry consistent `spin_mode` metadata,
3. spin-sensitive gates are not yet part of battery and claim promotion workflow.

This RFC defines a practical spin contract without forcing immediate kernel replacement.

---

## 2. Erratum to Prior Draft

Withdrawn statement:
1. "H is not there in C x O."

Corrected statement:
1. `H` is structurally present as associative subalgebras `H subset O` defined by Fano lines.
2. What is missing is an explicit, project-governed spin observable semantics.

Source anchors:
1. `rfc/CONVENTIONS.md` section "Quaternionic Subalgebras."
2. `CausalGraphTheory/SubalgebraDetect.lean` (batchable equals one-line quaternionic closure).

---

## 3. Established Facts We Keep

1. Kernel state remains `NodeStateV2` with `psi : ComplexOctonion Z` in `CausalGraphTheory/KernelV2.lean`.
2. Quaternionic closure is already used operationally for associativity and batching.
3. Electroweak quaternionic sector claims remain valid as currently scoped in RFC-039.

This RFC does not invalidate those results.

---

## 4. Actual Open Problem

The current model lacks a canonical spin contract at three levels:
1. Node-level representation: no standard spin field/operator in kernel semantics.
2. Claim-level governance: no mandatory `spin_mode` declaration for spin-sensitive claims.
3. Validation-level gates: no spin invariants in battery and matrix criteria.

So the problem is governance plus observable formalization, not algebra absence.

---

## 5. Spin Modes (Operational to Algebraic)

This RFC defines three explicit modes.

## 5.1 `spin_mode: parity`

Meaning:
1. use Grassmann parity style classification (fermionic or bosonic class),
2. no claim about signed projection `S_z`.

Allowed claims:
1. fermion/boson class distinctions only.

Disallowed claims:
1. hyperfine splitting,
2. detailed two-spin projection outcomes.

## 5.2 `spin_mode: label`

Meaning:
1. attach `spin_z in {+1, -1}` (doubled units) to motifs or simulation records,
2. treat as operational metadata with strict disclosure.

Allowed claims:
1. Pauli-style exclusion checks,
2. two-node spin bookkeeping invariants,
3. spin-conditioned interaction classification in declared toy regimes.

Requirement:
1. every result must state this is a label-mode claim, not a derived algebraic theorem.

## 5.3 `spin_mode: algebraic`

Meaning:
1. spin projection is derived from explicit algebraic operators and proved invariants.

Current status:
1. not yet closed,
2. promotion target for future work.

---

## 6. Contract to Lock Now

## 6.1 Kernel decision

1. Keep kernel representation as `C x O` for current roadmap.
2. Do not require immediate migration to `C x H x O`.

## 6.2 Claim metadata additions

For any spin-sensitive claim, require:
1. `spin_mode: parity | label | algebraic`,
2. `spin_artifact` reference,
3. `spin_sensitivity: unknown | insensitive | sensitive`.

## 6.3 Promotion guard

1. No claim may present spin-precision physics as model-derived unless `spin_mode: algebraic`.
2. `spin_mode: label` and `spin_mode: parity` remain exploratory or partial.

---

## 7. Minimal Physics Rules for `spin_mode: label`

These are operational rules, not deep derivations.

1. Label convention:
   - `+1` means spin-up,
   - `-1` means spin-down.
2. Pauli gate in declared two-node toy settings:
   - two identical fermion motifs with identical `spin_z` cannot occupy the same declared motif slot.
3. Closed-system round invariant:
   - in a declared closed two-node exchange without external injection, total labeled spin is conserved by design of the simulator update wrapper.

If any run violates these declared rules, the run fails the spin gate.

---

## 8. Implementation Plan

## 8.1 Phase A (governance and schema)

1. Update claim template with `spin_mode`, `spin_artifact`, `spin_sensitivity`.
2. Add matrix fields in RFC-050 sync plan.
3. Add battery gate family entry for spin-sensitive claim classes in RFC-049.

## 8.2 Phase B (Python operational harness)

1. Add `calc/spin_observable.py`.
2. Add `calc/test_spin_observable.py` with:
   - label conservation checks in closed toy rounds,
   - Pauli gate checks,
   - replay determinism.

## 8.3 Phase C (Lean bridge, scoped)

1. Add a Lean file for spin-mode contracts and theorem placeholders.
2. Prove mode-level consistency lemmas where possible.
3. Keep full algebraic spin-operator derivation as an open milestone, not a blocked prerequisite for all ongoing work.

---

## 9. Decisions Locked by This RFC

1. D1: `C x O` kernel stays canonical for now.
2. D2: Prior "missing-H" wording is deprecated.
3. D3: `spin_mode: label` is accepted for near-term operational studies with explicit disclosure.
4. D4: `spin_mode: parity` is classification-only.
5. D5: `spin_mode: algebraic` is the only path for promotion-grade precision spin claims.
6. D6: `C x H x O` can be explored as a future branch but is not required for immediate program continuity.

---

## 10. Falsification and Failure Gates

1. A claim uses spin-sensitive language without declaring `spin_mode`.
2. A label-mode claim is reported as if algebraic mode were proved.
3. Pauli gate behavior is asserted but fails deterministic replay tests.
4. Spin-sensitive result changes materially across declared profiles without disclosure.
5. Governance metadata is missing for active spin claims.

Any of the above blocks promotion.

---

## 11. Acceptance Criteria

This RFC closes when:
1. this corrected framing is adopted in related docs,
2. spin metadata is enforced for spin-sensitive claims,
3. one reproducible label-mode harness exists with deterministic tests,
4. at least one claim is reclassified using explicit `spin_mode`.

---

## 12. Notes on Future Algebraic Extension

A full algebraic spin reconstruction remains valuable, but it should be staged:
1. first prove what can be done within present `C x O` governance and observables,
2. then evaluate whether a true `C x H x O` kernel extension is required for unresolved spin phenomena.

This prevents premature architecture churn.

---

## 13. References

1. Furey and Hughes (2022), arXiv:2209.13016.
2. Furey (2016), arXiv:1603.04078.
3. Baez (2002), arXiv:math/0105155.
4. Existing COG conventions and Lean contracts listed in Depends on.
