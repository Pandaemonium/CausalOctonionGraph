# RFC-043: Motif Catalog v1

Status: Active Draft - Catalog Closure Plan (2026-02-26)
Module:
- `COG.Core.MotifCatalog`
Depends on:
- `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
- `rfc/RFC-040_Particle_Motif_and_Interaction_Rule_Contract.md`
- `rfc/RFC-044_Projection_Profile_Governance.md`
- `rfc/RFC-047_Confinement_Claim_Gates.md`
- `rfc/RFC-050_Proof_State_and_Claim_Status_Matrix.md`
- `rfc/RFC-056_Spin_as_Missing_H_Factor.md`
- `CausalGraphTheory/FureyChain.lean`
- `CausalGraphTheory/Spinors.lean`
- `CausalGraphTheory/TwoNodeSystem.lean`

---

## 1. Executive Summary

COG needs one canonical motif registry so claims stop re-defining particles ad hoc.

This RFC defines:
1. the motif entry schema,
2. evidence and promotion rules,
3. the initial v1 motif set,
4. integration with claim metadata and CI.

Motif catalog entries are not claims by themselves; they are reusable typed inputs to claims.

---

## 2. Problem Statement

Current motif usage is fragmented across RFC prose, Lean theorem names, and Python scripts.
This causes:
1. duplicate names for the same motif,
2. hidden profile/rule dependence,
3. inconsistent evidence labels.

A machine-readable motif catalog is required to stabilize claim language.

---

## 3. Catalog Scope

v1 scope is intentionally narrow:
1. vacuum and lepton baseline motifs,
2. two-node polarity class motif,
3. placeholders for quark/proton motifs with explicit hypothesis status.

Non-goals for v1:
1. full proton internal structure,
2. confinement derivation,
3. many-body motif closure.
Confinement claim promotion is governed separately by RFC-047.

---

## 4. Canonical Schema (v1)

Each motif entry must include:
1. `motif_id` (stable identifier, snake case + version suffix).
2. `title` (human-readable name).
3. `seed_state_ref` (Lean constant and optional Python constructor).
4. `rule_profile` (update/scheduler profile ID).
5. `pi_obs_profile` (`minimal` or `with_sector`).
6. `observable_signature` (declared outputs: charge/phase/sector fields).
7. `stability_gate` (finite-horizon criteria and replay constraints).
8. `evidence_level` (`lean_proved`, `python_verified`, `hypothesis`).
9. `artifacts` (theorem refs, tests, files).
10. `owner_claims` (claim IDs using this motif).
11. `notes`.

Recommended optional fields:
1. `equivalence_mode` (if motif identity is profile/horizon qualified).
2. `sensitivity_flags` (projection/rule sensitivity results).
3. `spin_mode` (`none`, `parity`, `label`, `algebraic`).
4. `spin_signature` (mode-consistent spin outputs where applicable).

---

## 5. Naming and Versioning Rules

1. Motif IDs are immutable once published: e.g., `vacuum_v1`.
2. Breaking changes produce a new suffix (`_v2`), never silent mutation.
3. Deprecated motifs remain in catalog with status note; do not delete history.

---

## 6. Signature Contract

Minimum required signature keys:
1. `u1_charge_sign` (or explicit neutral).
2. `phase_class` (typically Z4 class behavior where applicable).
3. `topology_context` (single-node, pair, or many-body).
4. `periodicity` (if defined).

Extended signature keys (optional in v1):
1. `sector_support`.
2. `associator_load_profile`.
3. `interaction_sensitivity`.
4. `spin_class` or `spin_projection` (must match declared `spin_mode`).

---

## 7. Stability Gates

For motif promotion above `hypothesis`, all must hold:
1. finite-horizon persistence under declared `rule_profile`,
2. deterministic replay hash stability,
3. no undocumented projection-profile dependence.

Failure of any gate blocks promotion.

---

## 8. Evidence and Promotion Policy

1. `hypothesis` -> `python_verified` requires:
   - reproducible test artifact with pinned config.
2. `python_verified` -> `lean_proved` requires:
   - theorem-backed signature/stability statements or explicit theorem subset.
3. Demotion is mandatory if later contrast tests show profile/rule fragility not previously declared.

Evidence level governs motif usability:
1. claim may reference `hypothesis` motifs only as exploratory.
2. claim may reference `lean_proved` motifs for promotion-grade results.

---

## 9. Initial Motif Set (v1)

1. `vacuum_v1`
   - seed: `KernelV2.vacuumState` / `KernelV2.omega_vac`
   - profile: `minimal`
   - target evidence: `lean_proved`
2. `electron_furey_v1`
   - seed: `fureyElectronStateDoubled`
   - profile: `minimal`
   - target evidence: `lean_proved`
3. `positron_like_dual_v1`
   - seed: dual electron state constructor (Lean/Python references)
   - profile: `minimal`
   - target evidence: `python_verified` (upgrade path to Lean)
4. `two_node_pair_class_v1`
   - seed: `TwoNodeSystem.NodePair` class motif
   - profile: `minimal`
   - target evidence: `lean_proved` + `python_verified`
5. `quark_proto_v1`
   - profile: `with_sector`
   - target evidence: `hypothesis`
6. `proton_proto_v1`
   - profile: `with_sector`
   - target evidence: `hypothesis`

---

## 10. Artifact Layout

Required artifacts:
1. `calc/motif_catalog.json` (canonical machine-readable registry).
2. `calc/test_motif_catalog.py` (schema + integrity tests).
3. claim links to motif IDs.

Recommended:
1. `sources/motif_catalog_report.md` for human-readable export.

---

## 11. CI and Governance Integration

CI checks must enforce:
1. unique `motif_id` values,
2. required schema fields per entry,
3. valid `pi_obs_profile` values,
4. artifact paths exist,
5. owner claims reference existing motif IDs.
6. if `spin_mode != none`, spin signature fields are present.

Matrix sync rule:
1. any claim with `motif_id` must match an entry in `claims/CLAIM_STATUS_MATRIX.yml`.

---

## 12. Falsification Gates

1. Motif signature mismatch across deterministic reruns.
2. Hidden profile dependence discovered post hoc.
3. Missing or stale artifacts for non-hypothesis motifs.
4. Claim references deleted/unknown motif IDs.
5. Spin-sensitive motif reported without declared `spin_mode`.

---

## 13. Acceptance Criteria

This RFC is closed when:
1. `calc/motif_catalog.json` exists and validates in CI.
2. At least four motifs are populated with artifact-backed entries.
3. At least three active claims reference catalog motif IDs.
4. Motif evidence levels are synchronized with claim matrix entries.

---

## 14. Relation to Adjacent RFCs

1. RFC-040 defines motif semantics and rule contracts.
2. RFC-044 governs projection profile declarations used by motifs.
3. RFC-050 governs claim/motif status synchronization.
4. RFC-048 extends pair motifs into many-body contexts (future catalog expansion).
5. RFC-047 defines confinement gates for motifs used in strong/confinement claims.
6. RFC-056 defines spin-mode semantics for spin-sensitive motifs.
