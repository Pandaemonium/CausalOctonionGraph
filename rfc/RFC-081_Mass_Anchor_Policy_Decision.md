# RFC-081: Mass Anchor Policy Decision (Single-Anchor Calibration)

Status: Active Draft  
Date: 2026-02-28  
Owner: Mass + Calibration Team  
Depends on:
1. `rfc/RFC-045_Energy_Mass_Observable_Unification.md`
2. `rfc/RFC-052_Scale_Calibration_from_Graph_Units.md`
3. `rfc/RFC-074_Proof_First_Generation_Motif_Lock.md`
4. `rfc/RFC-079_Typical_Starting_Conditions_and_Cold_Start_Control.md`

## 1. Purpose

Lock exactly one global dimensionful anchor to convert COG-native mass observables
to physical units and prevent circular multi-anchor calibration.

## 2. Problem

Absolute masses cannot be claimed rigorously while anchor choice remains fluid.
Using multiple anchors enables hidden refitting.

## 3. Policy (Normative)

1. Exactly one anchor policy is active per claim family.
2. Anchor policy must be preregistered before runs.
3. No claim-grade mass result may change anchor post hoc.
4. All derived masses must use the same frozen mass observable contract.

## 4. Candidate Anchors (Decision Set)

1. `anchor_top_mass_v1` (top quark mass).
2. `anchor_vev_v1` (electroweak VEV).
3. `anchor_electron_v1` (electron mass; lowest-energy anchor).

Each candidate must be evaluated with:
1. calibration stability across seeds/depths,
2. propagated uncertainty,
3. leakage risk (how easily downstream fit can hide in anchor choice).

## 5. Mass Observable Prerequisites

Before anchor lock:
1. freeze control subtraction rule,
2. freeze normalization rule,
3. freeze plateau-window rule,
4. prove representative/gauge invariance for motif classes used.

## 6. Promotion Gates

For any mass claim (`m_e`, `m_mu`, `m_tau`, quark/neutrino masses):
1. anchor policy ID must be declared in artifact metadata,
2. observable contract ID must be declared and immutable,
3. uncertainty propagation must include anchor uncertainty,
4. skeptic review must check anti-refit constraints.

## 7. Immediate Tasks

1. Run anchor comparison battery under one frozen observable contract.
2. Publish decision memo selecting one anchor policy.
3. Update mass claims to reference chosen anchor policy ID.

## 8. Non-Goals

1. This RFC does not define CKM/PMNS extraction.
2. This RFC does not resolve generation/triality representation closure.

## 9. Acceptance Criteria

RFC-081 reaches `supported` when:
1. a single anchor policy is selected and documented,
2. all promoted mass claims reference that anchor policy,
3. promotion pipeline rejects mass claims without anchor metadata.

## 10. Anti-Circularity Constraints

1. Anchor selection cannot use downstream multi-parameter fit quality as evidence.
2. Once anchor is locked, downstream masses may not update anchor metadata.
3. Any recalibration requires a new anchor policy ID and claim downgrades to `active_hypothesis`.
4. Relative-mass claims (`m_mu/m_e`, `m_tau/m_e`) must still declare the same observable contract ID even if absolute unit conversion is deferred.

## 11. Recommended Decision Path

1. Freeze one mass observable contract first (subtraction, normalization, plateau window).
2. Run anchor battery on `anchor_top_mass_v1` and `anchor_vev_v1` as top-down candidates.
3. Choose one anchor via preregistered scorecard:
   - stability across seeds/depths,
   - uncertainty compactness,
   - minimal leakage risk.
4. Defer quark/neutrino absolute-mass promotion until this lock is complete.

## 12. Jumping-the-Gun Risks

1. Pushing muon/tau absolute masses before anchor lock.
2. Changing plateau-window definitions per particle family.
3. Using one anchor for leptons and a different anchor for quarks.

## 13. Closure Discipline Addendum

1. Until anchor lock, all absolute-mass outputs must be labeled
   `non_promotable_calibration_pending`.
2. Relative-mass claims may proceed only if they use one frozen observable
   contract ID across all compared particles.
3. Anchor decision memo must include one rejected-anchor section with explicit
   failure reasons (stability, leakage risk, or uncertainty expansion).
4. Any anchor change requires:
   - new `anchor_policy_id`,
   - downgrade of dependent promoted claims,
   - full replay under new anchor before re-promotion.
