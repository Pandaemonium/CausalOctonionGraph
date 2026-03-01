# ALPHA IR Bridge with Exact Combinatoric Constants (v1)

## Scope

- Claim: `ALPHA-001`
- Contract: `cog_v2/rfc/RFC-012_Alpha_Combinatoric_Bridge_Contract.md`
- Formula (locked): `alpha_bridge = 1 / (L^2 * P - D)`

## Exact Constants (No Tuning)

- `L` (Fano lines): `7`
- `P` (points per line): `3`
- `D` (degeneracy subtraction): `2`
- UV anchor: `1/49`
- Denominator: `145`

## Result

- Bridge alpha: `1/145` (`0.006896551724`)
- CODATA 2018 target: `0.007297352569`
- Relative error: `5.492414%`

## Checks

- combinatoric_constants_exact: `True`
- denominator_identity_exact: `True`
- bridge_formula_locked: `True`
- no_output_tuned_parameter: `True`
- value_within_6pct_target: `True`
- bridge_pass: `True`

## Replay

- replay_hash: `3653f2d59a05c5dbeccb6956d9ad29f78a41d32b960720756a73118f83ab7972`
