# RFC-082: Flavor Unitary Extraction Contract (CKM/PMNS as Matrix-First Claims)

Status: Active Draft  
Date: 2026-02-28  
Owner: Flavor + Representation Team  
Depends on:
1. `rfc/RFC-041_Charge_Operator_Reconciliation.md`
2. `rfc/RFC-054_Observable_Equivalence_and_Physical_Indistinguishability.md`
3. `rfc/RFC-074_Proof_First_Generation_Motif_Lock.md`
4. `rfc/RFC-081_Mass_Anchor_Policy_Decision.md`

## 1. Purpose

Prevent angle-by-angle curve fitting by requiring CKM and PMNS extraction
from one full unitary map per sector.

## 2. Problem

Extracting `theta12/theta13/theta23/delta` independently is underconstrained
and sensitive to basis/gauge conventions.

## 3. Contract (Normative)

1. Derive one `3x3` unitary matrix for CKM from frozen up/down transport maps.
2. Derive one `3x3` unitary matrix for PMNS from frozen neutrino/lepton maps.
3. Only after matrix lock, extract PDG parameters from that matrix.
4. All reported parameters must be reproducible from the same matrix artifact.

## 4. Required Convention Locks

1. phase-gauge convention,
2. basis ordering convention,
3. projector/representation convention,
4. equivalence-class handling for gauge-related motifs.

## 5. Required Outputs

1. matrix artifact (`U_ckm`, `U_pmns`) with checksum,
2. unitarity residual metrics,
3. extracted PDG angles/phases with convention metadata,
4. sensitivity report under allowed relabelings.

## 6. Promotion Gates

For CKM/PMNS claims:
1. matrix-level derivation exists and passes unitarity checks,
2. no per-angle tuning parameters are present,
3. gauge/basis invariance checks pass,
4. skeptic review confirms matrix-first discipline.

## 7. Immediate Tasks

1. Draft matrix extraction theorem skeletons in Lean.
2. Build deterministic Python matrix extraction harness.
3. Add CI checks to forbid per-angle-only claim promotion.

## 8. Non-Goals

1. This RFC does not pick neutrino branch (Dirac vs Majorana).
2. This RFC does not solve absolute mass calibration.

## 9. Acceptance Criteria

RFC-082 reaches `supported` when:
1. CKM/PMNS claims are matrix-first in pipeline and docs,
2. promotions fail if only angle-level artifacts are provided,
3. at least one matrix artifact passes full extraction and invariance battery.

## 10. Preconditions and Execution Order

1. Lock quark/lepton generation basis ordering before matrix extraction.
2. Lock phase-gauge equivalence class handling (not sign-only).
3. Complete `CHARGE-DERIVATION-001` to reduce hidden SM injection risk in flavor claims.
4. Extract full matrix first, then derive all angles/phases in one pass.

## 11. Anti-Fit Controls

1. Ban per-angle optimization objectives in promotion tasks.
2. Require one matrix checksum to back all four CKM parameters (and all PMNS parameters).
3. Require sensitivity report over allowed relabelings; reject unstable matrices.
4. Separate `structure_match` and `value_match` in reports to avoid overclaiming early closures.

## 12. Jumping-the-Gun Risks

1. Claiming Cabibbo closure before full CKM matrix closure.
2. Claiming PMNS phase results before neutrino branch lock (Dirac vs Majorana).
3. Mixing basis conventions between extraction runs.

## 13. Closure Discipline Addendum

1. Angle-level claim IDs (`theta12_*`, `theta13_*`, `theta23_*`, `delta_*`)
   are non-promotable unless a matrix artifact (`U_ckm` or `U_pmns`) is linked.
2. Every flavor promotion candidate must include:
   - matrix checksum,
   - convention IDs (phase gauge + basis ordering),
   - unitarity residual report,
   - relabeling sensitivity report.
3. If convention IDs change, all angle/phase outputs derived from prior matrix
   artifacts are automatically invalidated for promotion.
4. `CHARGE-DERIVATION-001` unresolved status must be treated as a bridge
   assumption in all flavor claims.
