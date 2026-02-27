# RFC-052: Scale Calibration from Graph Units

Status: Active Draft - Contract Lock Candidate (2026-02-26)
Implements:
- `rfc/MASTER_IMPLEMENTATION_PLAN_V2.md` (WS-B, WS-D)
Companion:
- `rfc/RFC-046_Discrete_RG_Mechanism_No_Free_Params.md`
- `rfc/RFC-050_Proof_State_and_Claim_Status_Matrix.md`
Module:
- `COG.Theory.ScaleCalibration`
Depends on:
- `rfc/RFC-018_Time_as_Graph_Depth_and_Interaction_Clock.md`
- `rfc/RFC-035_Distance_as_Next_Interaction_Node_Gap.md`
- `rfc/RFC-036_Temperature_as_Coarse_Grained_Interaction_Intensity.md`
- `rfc/RFC-046_Discrete_RG_Mechanism_No_Free_Params.md`
- `rfc/RFC-051_Scheduler_Semantics_and_Update_Cadence.md`

---

## 1. Executive Summary

COG quantities are native graph observables (`tau_topo`, `tau_int`, `d_next`, interaction densities).  
Physical-language claims require a disciplined, versioned mapping from graph units to calibrated physical units.

This RFC locks:
1. one calibration profile schema (`scale_profile`),
2. one anti-fitting rule set,
3. one validation workflow with out-of-anchor checks.

Core rule:
1. anchor selection is predeclared and frozen before any derived-target evaluation.

---

## 2. Problem Statement

Current docs and claims mix:
1. graph-native quantities,
2. dimensionless ratios,
3. physical-unit interpretations (time/length/energy scale language).

Without a calibration contract:
1. two claims can use incompatible scale mappings,
2. constants can be back-fitted per claim,
3. falsification loses meaning.

---

## 3. Design Principles

1. **Graph-first:** graph units are primary; SI mapping is secondary.
2. **Profile versioning:** calibration is a named artifact, not informal prose.
3. **No target leakage:** a target observable cannot be both anchor and validation target.
4. **Regime explicitness:** if mapping is regime-specific, regime boundaries must be declared.
5. **Uncertainty propagation:** every derived physical estimate carries anchor-driven uncertainty.

---

## 4. Native Unit Basis

Canonical native quantities:
1. `tau_topo` (topological ticks, RFC-018),
2. `tau_int` (interaction-event count, RFC-018),
3. `d_next` (next-interaction node gap, RFC-035),
4. `T_proxy` / interaction-density summaries (RFC-036).

Calibration is a map from a subset of these observables to physical dimensions.

---

## 5. Calibration Profile Contract

Each promoted physical-unit claim must reference one frozen `scale_profile`.

```yaml
scale_profile_id: SCALE-PROFILE-v1
scale_profile_version: "1.0.0"
status: active
generated_at_utc: "2026-02-26T00:00:00Z"

scheduler_mode: snapshot_sync_v1
rule_profile: default_multiplicative_markov
pi_obs_profile: minimal

anchor_bundle:
  - anchor_id: A1
    native_observable: tau_int_rate_electron_motif
    physical_quantity: frequency_hz
    value: ...
    uncertainty: ...
    source_ref: ...
  - anchor_id: A2
    native_observable: d_next_motif_baseline
    physical_quantity: length_m
    value: ...
    uncertainty: ...
    source_ref: ...

mapping_family:
  time_map: "t = alpha_t * tau_int"
  length_map: "L = alpha_L * d_next"
  energy_map: "E = alpha_E * energy_proxy"

fit_policy:
  fitted_parameters:
    - alpha_t
    - alpha_L
    - alpha_E
  fitted_on_anchor_ids:
    - A1
    - A2
  forbidden_target_ids:
    - WEINBERG-001
    - STRONG-001

validation_targets:
  - target_id: V1
    native_observable: ...
    physical_quantity: ...
  - target_id: V2
    native_observable: ...
    physical_quantity: ...

checksums:
  profile_hash: "sha256:..."
  source_manifest_hash: "sha256:..."
```

---

## 6. Decisions Locked by This RFC

### D1. Profile-only calibration

All physical-scale claims must cite `scale_profile_id`; ad hoc conversion factors are invalid.

### D2. Anchor freeze before evaluation

Anchor bundle and mapping family are frozen before running validation targets.

### D3. No overlap between anchors and promoted targets

An observable used to fit calibration parameters cannot be promoted as independently derived.

### D4. Dual reporting is mandatory

Every calibrated result must report:
1. native graph value,
2. calibrated physical value plus uncertainty.

### D5. Regime policy is explicit

Default is one global profile.  
If regime-specific profiles are introduced, each claim must specify profile regime and switch criteria.

---

## 7. Anti-Retrofit Governance Rules

Forbidden:
1. changing anchor bundle after seeing validation misses,
2. adding a claim-specific correction factor not declared in profile,
3. redefining mapping family without profile version bump.

Required:
1. profile checksum in artifacts,
2. immutable source manifest for anchors,
3. explicit `forbidden_target_ids`.

---

## 8. Validation Workflow

1. Freeze `scale_profile`.
2. Fit mapping parameters using anchor bundle only.
3. Evaluate validation targets not present in anchor bundle.
4. Report residuals and uncertainty intervals.
5. Update claim status via matrix gates (RFC-050) only if profile checks pass.

Minimum validation set:
1. at least two non-anchor targets,
2. at least one from a different phenomenon family than the anchors.

---

## 9. Error and Uncertainty Contract

Each calibrated output must include:
1. parameter uncertainty from anchor fit,
2. propagated uncertainty on derived target,
3. residual (`derived - observed`) with sign,
4. normalized residual (`z` or equivalent).

If uncertainty propagation is absent, result is non-promotable.

---

## 10. CI Gates

### G1. Profile presence
Physical-unit claims without `scale_profile_id` fail.

### G2. Profile integrity
Profile checksum and source manifest hash must match.

### G3. Target leakage
If target is listed in `fitted_on_anchor_ids`, promotion fails.

### G4. Mapping mutation
If mapping family changed without profile version bump, fail.

### G5. Dual reporting
Missing native value alongside physical value fails.

---

## 11. Implementation Plan

### 11.1 Schemas and scripts

Add:
1. `schemas/scale_profile_v1.json`
2. `scripts/validate_scale_profile.py`
3. `scripts/run_scale_calibration.py`
4. `scripts/check_target_leakage.py`

### 11.2 Artifacts

Produce:
1. `sources/scale_profile_v1.json`
2. `sources/scale_validation_report_v1.md`
3. `sources/scale_validation_report_v1.json`

### 11.3 Matrix integration

Add fields to claim/matrix rows:
1. `scale_profile_id`
2. `scale_profile_hash`
3. `calibration_mode` (`native_only` or `calibrated`)

---

## 12. Failure Modes

1. **Anchor contamination:** validation target accidentally included in anchors.
2. **Profile drift:** recalibration done silently under same profile id.
3. **Overfitting by profile proliferation:** one profile per claim.
4. **Scheduler mismatch:** calibration built under one scheduler, applied under another.
5. **Unit illusion:** physical-unit confidence reported without native residual context.

---

## 13. Acceptance Criteria

This RFC is closed when:
1. `scale_profile_v1` schema and validator are implemented,
2. one canonical profile is frozen and checked in,
3. at least two non-anchor validation targets are reported with uncertainty propagation,
4. claim/matrix checks enforce profile metadata and leakage rules in CI.

---

## 14. Open Questions

1. Should calibration use `tau_topo`, `tau_int`, or both for time-like mapping in v1?
2. Is `d_next` sufficient for length-like mapping, or must motif-dependent corrections be explicit?
3. When should regime-specific profiles be allowed without undermining falsifiability?

---

## 15. Decision Register

Locked now:
1. profile-based calibration is mandatory for physical-unit claims,
2. anchor/target separation is mandatory,
3. dual native+physical reporting is mandatory.

Deferred:
1. exact anchor bundle composition for v1 canonical profile,
2. whether energy map should stay proxy-based or wait for RFC-045 closure.

