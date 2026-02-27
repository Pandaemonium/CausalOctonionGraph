# RFC-049: Benchmark and Falsification Battery v2

Status: Active Draft - Battery Closure Plan (2026-02-26)
Module:
- `COG.Governance.BatteryV2`
Depends on:
- `rfc/RFC-027_Foundational_Phenomena_Validation_Battery.md`
- `rfc/RFC-040_Particle_Motif_and_Interaction_Rule_Contract.md`
- `rfc/RFC-043_Motif_Catalog_v1.md`
- `rfc/RFC-044_Projection_Profile_Governance.md`
- `rfc/RFC-047_Confinement_Claim_Gates.md`
- `rfc/RFC-050_Proof_State_and_Claim_Status_Matrix.md`
- `rfc/RFC-054_Observable_Equivalence_and_Physical_Indistinguishability.md`
- `rfc/RFC-056_Spin_as_Missing_H_Factor.md`

---

## 1. Executive Summary

Battery v2 is the mandatory validation battery for claim promotion in COG.

It unifies:
1. deterministic replay checks,
2. motif signature checks,
3. projection-profile governance,
4. equivalence stability checks,
5. anti-retrofitting checks for constant-derivation tracks,
6. spin-mode governance for spin-sensitive claims.

No claim may be promoted to `supported` without passing required battery gates for its class.

---

## 2. Problem Statement

Current validation signals are scattered across:
1. Lean theorem lists,
2. Python tests,
3. ad hoc run logs.

This makes claim promotion inconsistent and prone to silent drift.
Battery v2 provides one canonical pass/fail contract.

---

## 3. Battery Scope (v2)

Battery v2 covers:
1. algebraic invariants,
2. update-rule determinism,
3. motif signatures from the catalog,
4. projection sensitivity and profile compliance,
5. observable-equivalence stability (static and finite-horizon where declared),
6. governance checks for no hidden fit/tuning,
7. mode-consistent spin claim validation.

Out of scope:
1. proving new physics claims,
2. replacing theorem proof obligations.

---

## 4. Gate Families

## B1. Core Determinism

1. Replay hash stability under fixed config.
2. No container-order dependence.
3. Rule-profile lock compliance (`rule_profile` declared and respected).

## B2. Motif Integrity

1. Motif IDs resolve to catalog entries.
2. Signature extraction matches catalog schema.
3. Evidence-level consistency with artifacts.

## B3. Interaction Baselines

1. Two-node polarity matrix regression checks.
2. Canonical baseline motifs (`vacuum`, `electron`, `dual`) remain stable.

## B4. Projection Governance

1. `pi_obs_profile` exists and is valid.
2. Required contrast runs exist for eligible claim classes.
3. `projection_sensitivity` labels are consistent with contrast outcomes.

## B5. Equivalence Governance

1. If `equivalence_mode != none`, required equivalence artifact exists.
2. Declared horizon equivalence is reproducible.
3. Profile-independent equivalence claims are cross-profile validated.

## B6. Anti-Retrofit Governance

1. Policy IDs and checksums are pinned.
2. No post-hoc parameter mutation in run artifacts.
3. No cherry-picked best-member reporting without declared ensemble protocol.

## B7. Confinement Claim Gates

1. Confinement-relevant claims must pass RFC-047 C1-C6 requirements.
2. Required artifacts must include dynamic non-escape report and negative controls.
3. Confinement promotion is blocked if projection or robustness disclosures are incomplete.

## B8. Spin Mode Governance

1. Spin-sensitive claims must declare `spin_mode` (`parity`, `label`, or `algebraic`).
2. Required spin artifacts must exist and be reproducible for the declared mode.
3. Claim language must match mode strength (no algebraic spin claims from `label` mode).

---

## 5. Gate-to-Claim-Class Matrix

Minimum required families by claim class:

1. `phase_clock`, `tick_ordering`:
   - B1, B2, B4
2. `two_node_polarity`, `distance_baseline`:
   - B1, B2, B3, B4
3. `proton/quark/strong-routing`:
   - B1, B2, B3, B4, B5, B7, B8
4. `constant_derivation`:
   - B1, B2, B4, B6
5. `equivalence-driven claims`:
   - B1, B4, B5
6. `confinement-derived claims`:
   - B1, B2, B4, B5, B6, B7
7. `spin-sensitive claims`:
   - B1, B2, B4, B8

If required families are not all passed, claim cannot advance to `supported`.

---

## 6. Output Contract

Each battery run must emit:
1. machine summary (`battery_v2_summary.json`),
2. human report (`battery_v2_report.md`),
3. run fingerprint (code hash + policy hash + seed/config hash),
4. gate-level pass/fail map,
5. declared `pi_obs_profile` and equivalence metadata snapshot.
6. confinement gate snapshot for confinement-relevant claim classes.
7. spin-mode snapshot for spin-sensitive claim classes.

Artifacts must be immutable and linkable from claim rows.

---

## 7. CI Integration

Required execution tiers:
1. pre-merge: reduced battery on changed claim classes.
2. nightly: full battery sweep.
3. release: full battery + reproducibility replay from clean environment.

CI must fail when:
1. required battery run missing for changed claims,
2. required gate family missing,
3. run artifacts not reproducible by hash.

---

## 8. Failure and Downgrade Policy

1. failed mandatory gate => promotion blocked,
2. repeated regression on previously passing gate => automatic status downgrade (`supported` -> `partial`),
3. missing provenance => run invalid,
4. governance violation (hidden fit/cherry-pick) => result rejected and claim flagged.
5. confinement-relevant claim with missing `B7` artifact => run invalid for promotion.
6. spin-sensitive claim with missing `B8` artifact => run invalid for promotion.

---

## 9. Deliverables

1. Battery v2 runner (`scripts/run_battery_v2.py` or equivalent).
2. Battery schema validator (`scripts/validate_battery_v2.py`).
3. CI workflow for pre-merge/nightly/release tiers.
4. Matrix sync hook to attach latest battery artifacts to claim rows.

---

## 10. Acceptance Criteria

This RFC is closed when:
1. battery v2 is executable in CI,
2. output artifacts are generated and persisted with stable schema,
3. at least three high-value active claims are re-evaluated through v2 end-to-end,
4. claim promotion flow in RFC-050 references battery v2 as mandatory gate source.

---

## 11. Relation to Adjacent RFCs

1. RFC-043 defines motif catalog entries consumed by B2.
2. RFC-044 defines projection profile policy consumed by B4.
3. RFC-054 defines equivalence policy consumed by B5.
4. RFC-050 defines status matrix fields where battery outputs are recorded.
5. RFC-047 defines confinement-specific pass/fail criteria consumed by B7.
6. RFC-056 defines spin-mode pass/fail constraints consumed by B8.
