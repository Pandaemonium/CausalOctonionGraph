# RFC-041: Charge Operator Reconciliation

Status: Active - Analysis Draft (2026-02-26)
Module:
- `COG.Core.ChargeOperator`
- `CausalGraphTheory/ChargeOperator.lean` (planned)
Depends on:
- `rfc/CONVENTIONS.md`
- `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
- `rfc/RFC-040_Particle_Motif_and_Interaction_Rule_Contract.md`
- `CausalGraphTheory/WeakMixingObservable.lean`
- `CausalGraphTheory/FureyChain.lean`
- `CausalGraphTheory/TwoNodeSystem.lean`
Literature basis:
- Furey (2014, 2016, 2018, 2019, 2022) and octonion algebra references (links in Section 12).

---

## 1. Executive Summary

COG currently uses:

`u1Charge(psi) = Re(psi_7)`

as the operational U(1) charge readout (`WeakMixingObservable.lean`).
This is local, simple, and already wired into interaction logic.

In parallel, division-algebra literature derives electric charge via number operators built from Witt-style ladder operators in `C x O`.

This RFC reconciles these two paths by introducing a two-layer contract:

1. **Operational charge** for kernel/runtime claims (`Q_proj`).
2. **Structural charge** for algebraic interpretation/calibration (`Q_num`).

The immediate objective is not to force a global proof of equality, but to make the relationship explicit, testable, and governance-safe.

---

## 2. Problem Statement

Current risk:

1. Runtime claims use `Q_proj = Re(psi_7)`.
2. Narrative/theory claims often cite number-operator charge quantization.
3. No formal bridge currently states when these are equivalent, proportional, or distinct.

Without a reconciliation contract, claim language can overstate what the code currently proves.

---

## 3. Evidence State (Current)

## 3.1 Lean-proved / implemented

1. `u1Charge` is defined in `CausalGraphTheory/WeakMixingObservable.lean`.
2. Electron benchmark sign is fixed:
   - `TwoNodeSystem.u1Charge_electron_neg8` proved.
3. Two-node polarity classification uses `u1Charge` sign and locked D3 gate.

## 3.2 Python-verified

1. Charge-sign interaction matrix behavior is stable under replay (`calc/charge_sign_interaction_matrix.py`).
2. Electron/dual/vacuum polarity behavior aligns with current kernel operator stack.

## 3.3 Not yet proved

1. A formal number-operator implementation over current `ComplexOctonion Int` state.
2. A theorem relating `Q_proj` to a structural `Q_num`.
3. A canonical charge-conjugation law that is simultaneously:
   - algebraically sound,
   - consistent with current runtime charge readout.

---

## 4. Literature Synthesis

## 4.1 Strongly relevant primary results

1. **Furey (2016)** argues electric-charge quantization via a number operator in the octonionic framework and identifies `Q = N/3` structure in that representation.
2. **Furey (2016 thesis)** develops the ladder/operator construction in full detail, including minimal-ideal machinery.
3. **Furey (2019)** extends algebraic state construction to three generations using the same `C x O` structural setting.
4. **Furey and Hughes (2022)** emphasize conjugation-invariant subalgebras and representation structure relevant to surviving gauge symmetries.
5. **Furey (2014)** gives a direct particle/antiparticle algebraic map through conjugation in the Clifford/octonionic encoding.

## 4.2 Supporting algebra references

1. **Baez (The Octonions)** provides baseline facts about octonion automorphisms and structure (`G2`), useful for avoiding representation-level mistakes.

## 4.3 Inference from literature

Inference (not yet proved in COG): number-operator charge is the physically richer structural definition, while projection-style charge is a local observable surrogate.

This RFC treats that inference as a hypothesis to be tested, not assumed.

---

## 5. Candidate Operator Families

1. `Q_proj(psi) := Re(psi_7)` (deployed baseline).
2. `Q_num(psi)` from Witt-ladder occupancy/operator algebra (structural target).
3. Optional conversion map `Q_phys = s * Q_proj` on a declared motif domain, where `s` is fixed by unit convention (not tuned per result).

Hard rule:
1. No affine fitting (`a*Q + b` with free `a,b`) to match targets post hoc.

---

## 6. Recommended Reconciliation Model

## 6.1 Two-layer charge contract

1. **Layer A (runtime canonical):** `Q_runtime := Q_proj`.
   - Used by update, polarity, and near-term simulations.
2. **Layer B (structural canonical):** `Q_struct := Q_num`.
   - Used for deep algebraic interpretation and long-horizon unification.

## 6.2 Bridge policy

Bridge obligations:
1. Define an explicit state-domain `D` (motif subspace).
2. Prove or measure a fixed relation on `D`:
   - equality, sign-equivalence, or constant-scale proportionality.
3. Declare mismatch set outside `D` if present.

This prevents false universal-equivalence claims while still enabling practical use now.

---

## 7. Decisions To Lock

1. **D1: Operator roles**
   - Accept two-layer contract (`Q_runtime`, `Q_struct`) vs single-operator doctrine.
2. **D2: Domain of bridge validity**
   - all states vs motif-restricted domain.
3. **D3: Unit normalization**
   - doubled integer units vs normalized physical units.
4. **D4: Conjugation contract**
   - define the canonical conjugation map and expected sign behavior per operator.
5. **D5: Claim policy**
   - which operator is mandatory for which claim classes.

Recommendation:
1. Lock D1 to two-layer now.
2. Lock D2 to motif domain first (vacuum/electron/dual states), then widen.
3. Keep D3 explicit in every artifact (`unit_mode` field).

---

## 8. Implementation Plan

## 8.1 Lean (Phase 1: operational hardening)

Planned file:
- `CausalGraphTheory/ChargeOperator.lean`

Phase-1 targets:
1. `def qProj : ComplexOctonion Int -> Int := u1Charge`
2. Bench theorems:
   - vacuum charge baseline,
   - electron charge sign/value,
   - dual-state charge sign/value.
3. Add explicit theorem refs used by claim metadata.

## 8.2 Lean (Phase 2: structural operator)

1. Define number-operator scaffolding over existing Witt objects.
2. Establish integer-spectrum theorem on benchmark motif domain.
3. Add bridge theorem candidates:
   - sign-equivalence,
   - scale-equivalence on domain `D`.

## 8.3 Python

Planned files:
1. `calc/charge_operator_reconciliation.py`
2. `calc/test_charge_operator_reconciliation.py`

Required reports:
1. operator comparison table on registered motifs,
2. bridge diagnostics (exact/sign/scale relation),
3. replay-hash stability.

---

## 9. Governance and Claim Impact

Until bridge closure:

1. Runtime claims may use `Q_runtime` only.
2. Structural claims citing quantization from number operators must be tagged `hypothesis` or `partial` unless backed by implemented `Q_num` artifacts.
3. Claims must declare:
   - `charge_operator_profile: runtime | structural | bridged`
   - `unit_mode: doubled | normalized`

---

## 10. Falsification Gates

1. If `Q_runtime` fails benchmark sign consistency under locked motifs, reject.
2. If `Q_struct` cannot reproduce integer-spectrum behavior on motif domain, reject structural promotion.
3. If bridge relation requires free fitted parameters, reject bridge claim.
4. If operator choice changes claim conclusion without declaration, downgrade claim.

---

## 11. Acceptance Criteria

1. `Q_runtime` path is fully documented and theorem-linked.
2. `Q_struct` scaffold exists with at least motif-domain tests.
3. At least one explicit bridge result is published on domain `D`:
   - exact or sign/scale relation.
4. Claim schema includes charge operator profile and unit mode.

---

## 12. Sources

Primary sources used in this draft:

1. Furey (2014), *Generations: three prints, in colour*  
   https://arxiv.org/abs/1405.4601
2. Furey (2016), *Charge quantization from a number operator*  
   https://arxiv.org/abs/1603.04078
3. Furey (2016), *Standard model physics from an algebra?* (thesis)  
   https://arxiv.org/abs/1611.09182
4. Furey (2018), *Three generations, two unbroken gauge symmetries...*  
   https://arxiv.org/abs/1806.00612
5. Furey (2019), *Three generations in the 64-dimensional Clifford algebra*  
   https://arxiv.org/abs/1910.08395
6. Furey and Hughes (2022), *One generation of Standard Model Weyl representations from complexified octonions*  
   https://arxiv.org/abs/2209.13016
7. Baez (2001), *The Octonions*  
   https://arxiv.org/abs/math/0105155

