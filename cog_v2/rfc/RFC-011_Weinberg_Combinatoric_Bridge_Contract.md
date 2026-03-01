# RFC-011: WEINBERG Combinatoric Bridge Contract (v2)

Status: Active  
Date: 2026-02-28  
Owner: COG Core  
Depends on:
- `cog_v2/rfc/RFC-001_Canonical_Axiom_Profile.md`
- `CausalGraphTheory/WeakMixingObservable.lean`
- `CausalGraphTheory/WeinbergCombinatoricBridge.lean`

## 1. Purpose

Lock a WEINBERG bridge lane with exact combinatoric constants and no tuned
numeric literals.

This RFC does not claim full first-principles IR closure by itself. It fixes
the bridge constants to finite-cardinality identities so the bridge cannot be
retrofitted numerically.

## 2. Locked Constants

Policy ID: `weinberg_ir_bridge_combinatoric_exact_v2`

1. UV anchor constant:
   - `uv_anchor = exclusive_u1_card / electroweak_card`
   - locked value: `1/4`.
2. Leakage coefficient:
   - `leakage_coeff = e000_sink_card / non_e000_card`
   - locked value: `1/7`.

## 3. Locked Bridge Form

The bridge form is fixed to:

`sin2_ir = uv_anchor - leakage_coeff * mean_e000_share_stationary`

with:
- `mean_e000_share_stationary` measured over a preregistered stationary window,
- deterministic kernel/event order per RFC-001.

## 4. Lean Targets

Required theorem targets:

1. `CausalGraph.uvAnchorCombinatoric_eq_one_four`
2. `CausalGraph.leakageCoeffCombinatoric_eq_one_seven`
3. `CausalGraph.sin2ThetaWBridgeCombinatoric_zero_share`
4. `CausalGraph.sin2ThetaWBridgeCombinatoric_antitone`

## 5. Required Artifacts

1. `cog_v2/sources/weinberg_ir_bridge_combinatoric_exact_v2.json`
2. `cog_v2/sources/weinberg_ir_bridge_combinatoric_exact_v2.md`
3. deterministic replay hash for the JSON payload.

## 6. Acceptance Gates

All must pass:

1. `combinatoric_constants_exact = true`.
2. `uv_anchor_exact_at_tick0 = true`.
3. `no_output_tuned_parameter = true`.
4. `stationary_period_detected = true`.

## 7. Non-Goals

This RFC does not:

1. by itself prove continuum EFT closure for `sin^2(theta_W)(M_Z)`,
2. replace needed bridge-assumption governance in the claim file,
3. allow coefficient search/tuning.
