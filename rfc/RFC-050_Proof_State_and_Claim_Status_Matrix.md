# RFC-050: Proof-State and Claim-Status Matrix

Status: Active Draft - Governance Sync Plan (2026-02-26)
Module:
- `COG.Governance.ClaimMatrix`
Depends on:
- `claims/*.yml`
- `rfc/RFC-040_Particle_Motif_and_Interaction_Rule_Contract.md`
- `rfc/RFC-043_Motif_Catalog_v1.md`
- `rfc/RFC-044_Projection_Profile_Governance.md`
- `rfc/RFC-047_Confinement_Claim_Gates.md`
- `rfc/RFC-049_Benchmark_and_Falsification_Battery_v2.md`
- `rfc/RFC-054_Observable_Equivalence_and_Physical_Indistinguishability.md`
- `rfc/RFC-056_Spin_as_Missing_H_Factor.md`

---

## 1. Executive Summary

This RFC defines one canonical machine-readable claim matrix used by CI, dashboards, and release reviews. It synchronizes:
1. theorem state (Lean),
2. simulation state (Python),
3. governance state (projection/equivalence/battery),
4. status semantics (`stub -> ... -> supported/falsified/superseded`).

---

## 2. Problem Statement

Claim readiness is currently distributed across:
1. claim YAML files,
2. RFC prose,
3. ad hoc test artifacts.

This causes drift. A single matrix is required to enforce consistency and prevent silent status inflation.

---

## 3. Matrix Artifact

Canonical file:
1. `claims/CLAIM_STATUS_MATRIX.yml`

Optional derived outputs:
1. `claims/CLAIM_STATUS_MATRIX.json`
2. dashboard snapshot export.

Matrix rows are keyed by `claim_id`.

---

## 4. Matrix Schema (v2, synchronized)

Required fields per claim row:
1. `claim_id`
2. `status` (`stub`, `active_hypothesis`, `partial`, `supported`, `falsified`, `superseded`)
3. `lean_artifacts`
4. `python_artifacts`
5. `battery_artifacts`
6. `motif_id`
7. `rule_profile`
8. `pi_obs_profile`
9. `projection_sensitivity` (`unknown`, `insensitive`, `sensitive`)
10. `equivalence_mode` (`none`, `static`, `one_step`, `horizon`)
11. `equivalence_artifact` (optional unless `equivalence_mode != none`)
12. `evidence_level` (`lean_proved`, `python_verified`, `hypothesis`, or mixed descriptor)
13. `last_verified_at` (ISO-8601 UTC)
14. `owner_rfc` (primary RFC driving this claim)
15. `notes`
16. `confinement_gate_status` (`not_applicable`, `open`, `pass`, `fail`)
17. `confinement_artifact` (required when confinement-relevant)
18. `ensemble_policy_id` (required when confinement-relevant)
19. `spin_mode` (`none`, `parity`, `label`, `algebraic`)
20. `spin_artifact` (required when spin-sensitive)
21. `spin_sensitivity` (`unknown`, `insensitive`, `sensitive`)

Migration alias (temporary):
1. accept legacy `projection_profile` only during migration.
2. canonical key remains `pi_obs_profile`.

---

## 5. Status Semantics

1. `supported` requires:
   - all mandatory gates for the claim class passed,
   - artifact-complete evidence linked,
   - no unresolved contradiction at equal or stronger evidence level.
2. confinement-relevant claims require `confinement_gate_status: pass` before `supported`.
3. spin-precision claims require `spin_mode: algebraic` before `supported`.
4. `partial` requires:
   - nontrivial evidence present,
   - at least one mandatory gate still open.
5. `active_hypothesis` requires:
   - coherent proposed mechanism,
   - no decisive contradictory evidence,
   - proof/validation stack incomplete.
6. `falsified` requires:
   - explicit failed gate or contradiction artifact.
7. `superseded` requires:
   - explicit replacement claim/RFC link.

---

## 6. CI Validation Rules

CI must fail when:
1. active claim lacks matrix row,
2. matrix row lacks required field,
3. `pi_obs_profile` is invalid or missing,
4. `equivalence_mode != none` and `equivalence_artifact` missing,
5. `status: supported` but mandatory artifacts/gates are missing,
6. stale `last_verified_at` exceeds declared recency window for volatile claim classes.
7. confinement-relevant row lacks any of:
   - `confinement_gate_status`,
   - `confinement_artifact`,
   - `ensemble_policy_id`.
8. spin-sensitive row lacks any of:
   - `spin_mode`,
   - `spin_artifact`,
   - `spin_sensitivity`.

Recommended validator:
1. `scripts/validate_claim_status_matrix.py`

---

## 7. Sync Workflow

1. Update claim YAML and matrix row in the same change set.
2. Run matrix validator and battery checks.
3. If status changes, add short status-change note in corresponding RFC or run report.
4. Never merge claim status changes without artifact links.

---

## 8. Falsification and Supersession Workflow

1. Do not delete failed branches; retain rows with `status: falsified`.
2. `superseded` rows must include replacement pointer in `notes` (claim ID + RFC link).
3. Failed branch artifacts remain immutable references.

---

## 9. Deliverables

1. matrix file(s) and schema documentation.
2. generator/sync script for artifact extraction.
3. CI validator for schema + semantic constraints.
4. dashboard integration consuming matrix only (no side-channel status logic).

---

## 10. Acceptance Criteria

1. matrix exists and is CI-validated.
2. all non-archived claims have rows.
3. projection/equivalence metadata are synchronized with RFC-044 and RFC-054.
4. dashboards and summary docs use matrix as the single status source.
