# RFC-003: THETA Continuum Identification Contract (v2)

Status: Active  
Date: 2026-02-28  
Owner: COG Core  
Depends on:
- `cog_v2/rfc/RFC-001_Canonical_Axiom_Profile.md`
- `cog_v2/rfc/RFC-002_Event_Resolution_Modes_and_Interpretation_Layer.md`

## 1. Purpose

Lock the continuum-identification contract used by THETA-001 so bridge semantics
are explicit and replayable.

This RFC does not declare `proved_core` value closure. It defines the v2
structure-first identification contract.

## 2. Locked Contract

Policy ID: `theta_continuum_linear_identification_v1`

1. Discrete CP-odd observable:
   - `discreteTopologicalCharge_v1 := discreteCpResidual`
2. Continuum theta proxy coefficient:
   - `thetaContinuumCoeff_linear_v1 := discreteTopologicalCharge_v1`
3. `F \tilde F` coefficient proxy:
   - `fTildeFCoeff_proxy_linear_v1 := thetaContinuumCoeff_linear_v1`
4. Coarse-grain operator:
   - `depth_normalized_residual_mean_v1`
5. Operational map-identification policy:
   - `theta_map_identification_linear_unit_v1`
   - constraints:
     - mode is `linear`,
     - CP-odd and zero-anchor checks pass,
     - unit normalization (`theta(+1)=+1`, `theta(-1)=-1`).
   - selected map id must be `linear_scale_1_v1`.
6. Discrete leakage compatibility:
   - leakage/isolation diagnostics are treated as depth-binned observables over integer distance `d`.
   - bridge acceptance consumes coarse-grained summaries from the discrete ladder, not continuous interpolation.
7. Discrete correction envelope id:
   - `theta_discrete_correction_envelope_v1`.

## 3. Lean Targets

Required theorem targets:

1. `CausalGraphV2.discreteTopologicalCharge_v1_zero`
2. `CausalGraphV2.thetaContinuumCoeff_linear_v1_zero`
3. `CausalGraphV2.fTildeFCoeff_proxy_linear_v1_zero`
4. `CausalGraphV2.theta_qcd_zero_under_locked_identification_v1`

## 4. Required Artifacts

1. `cog_v2/sources/theta001_bridge_closure_v2.json`
2. `cog_v2/sources/theta001_eft_bridge_v2.json`
3. `cog_v2/sources/theta001_continuum_bridge_v2.json`

## 5. Promotion Semantics

1. This contract is sufficient for `supported_bridge` in THETA-001 when all
   gate checks pass.
2. `proved_core` remains blocked until a stronger continuum EFT derivation
   discharges remaining hypothesis-level bridge assumptions.

## 6. Non-Goals

This RFC does not:

1. derive full QCD continuum EFT from external first principles,
2. claim hadronic phenomenology closure,
3. relax deterministic replay requirements.
4. imply that leakage dynamics are continuous in distance.
