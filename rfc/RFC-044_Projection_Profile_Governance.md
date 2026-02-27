# RFC-044: Projection Profile Governance

Status: Active Draft - Governance Closure Plan (2026-02-26)
Module:
- `COG.Governance.ProjectionProfiles`
Depends on:
- `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
- `rfc/RFC-040_Particle_Motif_and_Interaction_Rule_Contract.md`
- `rfc/RFC-056_Spin_as_Missing_H_Factor.md`
- `rfc/RFC-042_D4_D5_Implementation_Closure.md`
- `CausalGraphTheory/D4D5Contracts.lean`

---

## 1. Executive Summary

COG claims are observer-profile dependent. The same microstate can produce different claim outcomes under different `piObs` maps. This RFC locks the governance contract for projection usage, reporting, and claim-grade validation.

Core rules:
1. every claim must declare a projection profile,
2. baseline claims use `piObsCanonical := piObsMinimal`,
3. profile-sensitive outcomes must be explicitly marked and downgraded from universal interpretation,
4. CI must fail on missing or inconsistent projection metadata.
5. projection profile does not substitute for `spin_mode`; spin-sensitive claims must declare both.

---

## 2. Problem Statement

Without profile governance:
1. claims can silently depend on hidden observer choices,
2. contradictory outcomes can appear without being recognized as projection effects,
3. "model-derived" status can be over-assigned to profile-fragile claims.

Projection governance is therefore a correctness requirement, not a formatting preference.

---

## 3. Canonical Profile Set

## 3.1 `minimal` profile (canonical baseline)

Map: `piObsMinimal`.
Per-node fields:
1. `nodeId`
2. `u1Charge`
3. `phase4`
4. `topoDepth`
5. `u1Sector := none`

Use for:
1. phase clock claims,
2. charge-sign interaction classification,
3. scheduler/update determinism claims,
4. distance-gap baseline claims that do not require color routing details.

## 3.2 `with_sector` profile (extended)

Map: `piObsWithSector`.
Adds sector vector visibility (`u1Sector := some piObs(psi)`).

Use for:
1. proton and quark internal-structure claims,
2. color routing and strong-sector channel claims,
3. any claim where motif distinction depends on sector support.

## 3.3 Canonical baseline lock

For broad/base claim promotion:
1. `piObsCanonical := piObsMinimal` remains mandatory until explicit promotion criteria are met in RFC-028.

---

## 4. Required Claim Metadata

All claim documents (`claims/*.yml`) must include:
1. `pi_obs_profile`: `minimal` or `with_sector`
2. `pi_obs_profile_version`: semantic version string (for future profile evolution)
3. `projection_sensitivity`: `unknown`, `insensitive`, or `sensitive`
4. `profile_contrast_run`: artifact ID/hash for profile-contrast test when meaningful

Backward-compatibility:
1. `projection_profile` is accepted temporarily as an alias for migration only.
2. canonical key is `pi_obs_profile`.

---

## 5. Policy Matrix by Claim Class

1. `phase_clock`, `tick_ordering`, `determinism` -> required `minimal`
2. `u1_charge_sign`, `two_node_polarity` -> required `minimal`
3. `proton_internal`, `quark_sector`, `color_routing` -> required `with_sector`
4. `strong_coupling_proxy` -> starts with `with_sector`; must state if any derived value remains valid under `minimal`
5. `projection-theory claims` -> must run and report both profiles

If claim class and profile mismatch, claim is invalid until corrected.

Spin governance interaction:
1. projection and spin are orthogonal metadata dimensions,
2. spin-sensitive claims must pass both profile policy (this RFC) and mode policy (RFC-056).

---

## 6. Projection-Sensitivity Protocol

For every claim where alternate profile is meaningful:

1. run primary claim under declared profile,
2. run contrast evaluation under alternate profile,
3. classify outcome:
   - `insensitive`: conclusion unchanged,
   - `sensitive`: conclusion changes materially,
   - `unknown`: contrast not yet executed.

Material change criteria (any true):
1. pass/fail status flips,
2. sign of key observable flips,
3. rank/order of compared motifs flips,
4. numeric shift crosses claim tolerance gate.

Governance consequence:
1. `sensitive` claims cannot be labeled model-universal.

---

## 7. CI and Lint Enforcement

CI checks must enforce:
1. every active claim has `pi_obs_profile`,
2. profile value is in allowed set,
3. claims requiring contrast have `profile_contrast_run`,
4. if `projection_sensitivity: sensitive`, claim status cannot be upgraded to universal/support labels without qualifier.

Recommended check script:
1. `scripts/validate_projection_profiles.py`

---

## 8. Failure Modes

1. **Hidden profile dependence:** Claim appears stable until profile changes.
2. **Profile drift:** New profile behavior introduced without version bump.
3. **Cross-profile overreach:** Result from `with_sector` reported as if profile-independent.
4. **Metadata omission:** claim cannot be audited.

---

## 9. Migration Plan

Phase A (immediate):
1. add metadata fields to all active claims,
2. map existing `projection_profile` to `pi_obs_profile`.

Phase B (short-term):
1. run contrast checks for high-impact active claims,
2. set `projection_sensitivity` statuses.

Phase C (cleanup):
1. remove alias support for `projection_profile`,
2. fail CI on legacy key usage.

---

## 10. Deliverables

1. projection metadata schema in claim template.
2. CI validator for projection fields and policy matrix compliance.
3. contrast-run report artifact format.
4. dashboard facet showing profile and sensitivity status per claim.

---

## 11. Falsification Gates

1. Missing or invalid `pi_obs_profile` -> claim invalid.
2. Undisclosed profile-sensitive reversal -> status downgrade.
3. Cross-profile contradiction ignored in summary docs -> governance failure.
4. Profile version drift without migration note -> claim blocked.

---

## 12. Acceptance Criteria

1. projection policy is documented and CI-enforced.
2. all active claims include canonical projection metadata.
3. at least one nontrivial claim has published contrast report.
4. projection-sensitive claims are correctly labeled and not overpromoted.

---

## 13. References

1. Lamport, L. (1978), *Time, Clocks, and the Ordering of Events in a Distributed System*  
   https://www.microsoft.com/en-us/research/publication/time-clocks-ordering-events-distributed-system/
2. Chandy, K. M., Lamport, L. (1985), *Distributed Snapshots*  
   https://www.microsoft.com/en-us/research/publication/distributed-snapshots-determining-global-states-distributed-system/
3. Arrighi, P., Dowek, G. (2012), *Causal graph dynamics*  
   https://arxiv.org/abs/1202.1098
