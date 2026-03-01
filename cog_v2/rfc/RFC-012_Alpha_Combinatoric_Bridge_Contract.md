# RFC-012: ALPHA Combinatoric Bridge Contract (v1)

Status: Active  
Date: 2026-03-01  
Owner: COG Core  
Depends on:
- `cog_v2/rfc/RFC-001_Canonical_Axiom_Profile.md`
- `cog_v2/rfc/RFC-006_Bridge_Construction_from_CxO_Combinatorics.md`
- `CausalGraphTheory/AlphaCombinatoricBridge.lean`

## 1. Purpose

Lock an exact, no-fit combinatoric bridge lane for `ALPHA-001`.

This contract fixes the bridge map family and constants so bridge artifacts are
auditable and cannot be numerically retrofitted after target inspection.

## 2. Locked Constants

Policy ID: `alpha_ir_bridge_combinatoric_exact_v1`

1. Fano line cardinality:
   - `L = 7`
2. Points per Fano line:
   - `P = 3`
3. Degeneracy subtraction cardinality:
   - `D = 2`

## 3. Locked Bridge Form

The map family is fixed to:

`alpha_bridge = 1 / (L^2 * P - D)`

with UV anchor:

`alpha_uv = 1 / L^2`

No additional free parameters are permitted in this lane.

## 4. Lean Targets

Required theorem targets:

1. `CausalGraph.fanoLineCard_eq_seven`
2. `CausalGraph.alphaDenominatorCombinatoric_eq_145`
3. `CausalGraph.alphaUvAnchorCombinatoric_eq_one_div_49`
4. `CausalGraph.alphaBridgeCombinatoric_eq_one_div_145`

## 5. Required Artifacts

1. `cog_v2/sources/alpha_ir_bridge_combinatoric_exact_v1.json`
2. `cog_v2/sources/alpha_ir_bridge_combinatoric_exact_v1.md`
3. deterministic replay hash for the JSON payload.

## 6. Acceptance Gates

All must pass:

1. `combinatoric_constants_exact = true`
2. `denominator_identity_exact = true`
3. `no_output_tuned_parameter = true`
4. `bridge_formula_locked = true`

## 7. Epistemic Scope

This lane is `supported_bridge` scope only:

1. it locks exact combinatoric constants and map form,
2. it does not, by itself, prove continuum EFT identification,
3. it separates `structure_match` from `value_match`.

## 8. Non-Goals

This RFC does not:

1. claim full first-principles closure of the physical fine-structure constant,
2. allow coefficient search/tuning against target values,
3. replace independent skeptic review requirements for promotion.

