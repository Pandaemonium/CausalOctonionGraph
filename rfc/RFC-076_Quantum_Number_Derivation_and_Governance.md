# RFC-076: Quantum Number Derivation and Governance Contract

Status: Active Draft  
Date: 2026-02-27  
Owner: Research Director + Lab Manager  
Implements:
1. `rfc/RFC-050_Proof_State_and_Claim_Status_Matrix.md`
2. `rfc/RFC-075_Autonomous_Lab_Epistemic_Architecture.md`

Depends on:
1. `rfc/CONVENTIONS.md`
2. `calc/derive_sm_quantum_numbers.py`
3. `calc/test_derive_sm_quantum_numbers.py`
4. `sources/qn_claim_ledger.json`
5. `scripts/validate_qn_claim_ledger.py`

---

## 1. Executive Summary

This RFC defines the canonical quantum-number program in COG and its epistemic governance.

The current implementation derives a compact set of tier-1 quantum-number claims (`QN-001` to `QN-007`) using exact rational arithmetic and explicit assumption disclosure.  
The main policy lock is:
1. every QN claim must be labeled `core_derived` or `bridge_assumed`,
2. every QN claim must list assumptions and theorem/test references,
3. all QN results must be emitted as a machine-readable ledger and validated in CI.

---

## 2. Scope

In scope:
1. COG-side derivation rules for tier-1 quantum-number outputs.
2. Governance of QN claim status, assumptions, and falsification posture.
3. Artifact requirements and promotion gates.

Out of scope:
1. full derivation of running couplings across all scales,
2. replacing bridge assumptions with core proofs in this RFC,
3. observational extraction mechanics for all constants beyond QN tier.

---

## 3. Canonical Inputs

Locked preconditions (strict mode):
1. `N_c = len(WITT_PAIRS) = 3`
2. `N_gen = N_c = 3`
3. `N_w = 2`

Implementation reference:
1. `calc/derive_sm_quantum_numbers.py::validate_preconditions(strict=True)`

If strict preconditions fail, QN outputs are invalid for promotion.

---

## 4. QN Claim Set (v1)

## 4.1 QN-001 (core_derived)

Claim:
1. electric charge unit is quantized in multiples of `1/3`.

COG basis:
1. Witt occupation structure over locked `N_c=3`.

Artifact references:
1. `calc/derive_sm_quantum_numbers.py::derive_charge_quantization`
2. `calc/test_derive_sm_quantum_numbers.py::test_witt_charge_set`

## 4.2 QN-002 (core_derived)

Claim:
1. color channel count equals `N_c=3`.

COG basis:
1. direct cardinality of locked Witt pairs.

Artifact references:
1. `calc/test_derive_sm_quantum_numbers.py::test_N_c_equals_3`

## 4.3 QN-003 (bridge_assumed)

Claim:
1. generation count identified as `N_gen = N_c = 3`.

Bridge:
1. physical identification of generation count with color cardinality.

Artifact references:
1. `calc/test_derive_sm_quantum_numbers.py::test_N_gen_equals_N_c`

## 4.4 QN-004 (bridge_assumed)

Claim:
1. gauge boson count `8 + 3 + 1 = 12`.

Bridge:
1. SU(N) dimension bridge plus fixed SU(2) and U(1) channel assumptions.

Artifact references:
1. `calc/test_derive_sm_quantum_numbers.py::test_total_gauge_bosons`

## 4.5 QN-005 (bridge_assumed)

Claim:
1. anomaly checks vanish for reconstructed 15-LH-Weyl assignment (`Tr[Y]=0`, `Tr[Y^3]=0`).

Bridge:
1. imported SM hypercharge assignment.

Artifact references:
1. `calc/test_derive_sm_quantum_numbers.py::test_sm_hypercharge_linear_anomaly`
2. `calc/test_derive_sm_quantum_numbers.py::test_sm_hypercharge_cubic_anomaly`

## 4.6 QN-006 (bridge_assumed)

Claim:
1. GUT-normalized weak mixing prediction `sin^2(theta_W)=3/8`.

Bridge:
1. SU(5)-style normalization bridge.

Artifact references:
1. `calc/test_derive_sm_quantum_numbers.py::test_sin2_theta_W_exact`

## 4.7 QN-007 (bridge_assumed)

Claim:
1. one-loop UV beta-function coefficient from chosen flavor regime (`beta0=9` for `N_f=3`; reference `N_f=6` gives `7`).

Bridge:
1. standard one-loop QCD beta-function framework.

Artifact references:
1. `calc/test_derive_sm_quantum_numbers.py::test_beta0_uv`
2. `calc/test_derive_sm_quantum_numbers.py::test_beta0_nf6`

---

## 5. Governance Contract

For every QN row, required fields:
1. `claim_id`
2. `status` (`core_derived` or `bridge_assumed`)
3. `assumptions` (non-empty list)
4. `theorem_refs` (non-empty list)
5. `tests` (non-empty list)
6. `confidence`

Top-level required metadata:
1. `schema_version`
2. `generated_at_utc`
3. `generated_by`
4. `source_script`
5. `source_script_sha256`
6. `preconditions`

Validation reference:
1. `scripts/validate_qn_claim_ledger.py`

Policy:
1. `core_derived` rows must not use placeholder theorem refs.
2. `bridge_assumed` rows may carry placeholder refs until closure tasks complete.

---

## 6. Sensitivity and Falsification Requirements

Minimum sensitivity checks must run and be emitted:
1. perturb `N_gen = N_c` assumption and show impacted claims,
2. perturb weak-doublet bridge (`N_w`) and show impacted claims,
3. perturb hypercharge assignment and show impacted claims.

Reference:
1. `calc/derive_sm_quantum_numbers.py::run_sensitivity_checks`

Falsification policy:
1. any QN claim with failed sensitivity consistency or failed deterministic tests cannot be promoted.

---

## 7. Artifact and CI Requirements

Mandatory artifacts:
1. `sources/qn_claim_ledger.json`
2. passing tests in `calc/test_derive_sm_quantum_numbers.py`
3. passing ledger validation from `scripts/validate_qn_claim_ledger.py`

Pipeline integration:
1. `python -m calc.derive_sm_quantum_numbers`
2. `python scripts/validate_qn_claim_ledger.py --path sources/qn_claim_ledger.json --require-lean-backed-statuses core_derived`

---

## 8. Promotion Semantics for QN Claims

`bridge_assumed -> core_derived` is allowed only when:
1. bridge assumptions are removed or formally internalized as core derivations,
2. placeholder theorem refs are replaced with concrete Lean-backed references,
3. sensitivity checks pass without reliance on external bridge scaffolding.

Until then, claims remain `bridge_assumed` regardless of numerical agreement.

---

## 9. Implementation Plan

Phase A (now, locked):
1. maintain and validate QN ledger in CI,
2. keep explicit core/bridge split,
3. keep sensitivity report mandatory.

Phase B (next):
1. create closure tasklist for each bridge QN claim,
2. add falsifier-focused tasks for bridge assumptions,
3. add claim-by-claim oracle tracking for observable-facing QN outputs.

Phase C (promotion):
1. promote individual QN claims as assumptions are discharged,
2. preserve full audit trail in ledger history.

---

## 10. Acceptance Criteria

RFC-076 reaches `supported` when:
1. QN ledger validates in pipeline/CI,
2. all QN claims have explicit assumption and theorem/test metadata,
3. core vs bridge classification is enforced and stable,
4. sensitivity checks are present and passing in deterministic test runs.

