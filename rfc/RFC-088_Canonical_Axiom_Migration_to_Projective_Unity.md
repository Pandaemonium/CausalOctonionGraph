# RFC-088: Canonical Axiom Migration to Projective Unity

Status: Active (Policy Lock, Migration In Progress)
Date: 2026-02-28
Owner: Research Director + Kernel Team
Depends on:
1. `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
2. `rfc/RFC-069_Canonical_Simulation_Artifact_Contract.md`
3. `rfc/RFC-077_CxO_Unity_Profile_and_Projection_Update_Rule.md`
4. `rfc/RFC-078_Superdeterministic_Preregistration_of_Event_Ordering.md`
5. `rfc/RFC-086_Projective_Universe_Axiom_and_Projective_Unity_Kernel.md`
6. `world_code/Python_code/minimal_world_kernel_projective_unity.py`

---

## 1. Decision

From this RFC onward, the canonical axiom profile is:
1. universe as DAG,
2. node states in `C x O` over unity alphabet,
3. deterministic lightcone projection update rule.

Canonical runtime profile ID:
1. `projective_unity_v1`

Projector ID:
1. `pi_unity_axis_dominance_v1`

---

## 2. What Changes

1. `projective_unity_v1` is now canonical for new claim-grade simulation lanes.
2. Integer-kernel profile is reclassified as legacy/sensitivity profile.
3. Legacy results remain valid historical artifacts but are not the default evidence lane for new promotions.

---

## 3. Override/Supersession Notes

1. RFC-077 is superseded for canonical-profile governance (retained as historical comparison context).
2. RFC-086 remains the operational contract for projector semantics and determinism.
3. Any documentation stating "`integer` is canonical" must be updated or tagged as legacy.

---

## 4. Migration Rules (Normative)

1. New simulation artifacts must declare:
   - `kernel_profile: projective_unity_v1`,
   - `projector_id: pi_unity_axis_dominance_v1`.
2. Mixed-profile closure bundles are forbidden.
3. Legacy integer runs may be attached only as:
   - `legacy_sensitivity_comparison`,
   - with explicit non-canonical label.
4. Claims in active closure must freeze one profile per lane.

---

## 5. Promotion Policy During Migration

For claims already in-flight:
1. If a claim has promoted status from legacy profile, keep status but mark profile provenance explicitly.
2. Any new gate advancement after this RFC requires either:
   - migration rerun under `projective_unity_v1`, or
   - explicit waiver with rationale and reviewer sign-off.

For new claims:
1. projective-unity canonical lane is mandatory by default.

---

## 6. Required Tooling/Doc Updates

1. Default `--kernel-profile` in campaign generators must switch to `projective_unity`.
2. Worker/help docs must point first to `minimal_world_kernel_projective_unity.py`.
3. Public pages must state projective-unity as canonical.
4. Validators should reject profile mixing in one closure lane.

---

## 7. Risks and Mitigations

Risk:
1. Historical comparability break due to profile shift.

Mitigation:
1. retain legacy profile runs as declared sensitivity references.

Risk:
1. Apparent regressions caused by projection semantics, not physics.

Mitigation:
1. require side-by-side legacy deltas for high-impact claims until migration stabilizes.

---

## 8. Acceptance Criteria

RFC-088 reaches `supported` when:
1. default generators use `projective_unity`,
2. key docs/help pages reflect the new canonical profile,
3. at least one active constant lane is rerun under `projective_unity_v1`,
4. promotion pipeline has profile-provenance checks enabled for migrated claims.

