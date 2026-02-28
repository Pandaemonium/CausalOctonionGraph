# THETA-001 UV Exhaustive Microstate/Event Witness (v1)

- Claim: `THETA-001`
- Scope: `structure_first`
- Replay hash: `c95c81d96001b72e768788fb6855e086cbea718bdbe08d342be56f9e1b56184f`
- states_are_events: `True`
- enumeration_mode: `full_exhaustive`
- microstates_total: `390625`

## Global Checks
- all_lanes_all_ticks_hold: `True`
- all_lanes_full_exhaustive: `True`

## Lane `uv_lane_a`
- op_sequence: `[1, 2, 3, 4]`
- ticks: `4`
- enumerated_microstates: `390625`
- full_exhaustive: `True`
- lane_all_ticks_hold: `True`

| Tick | Events | cp==dual | cp==-dual | parity holds all | expected mode | expected mode holds all | strong_cp_delta_sum | strong_dual_delta_sum |
|---:|---:|---:|---:|---|---|---|---:|---:|
| 0 | 390625 | 390625 | 1 | True | cp_equals_dual | True | 0 | 0 |
| 1 | 390625 | 1 | 390625 | True | cp_equals_neg_dual | True | 0 | 0 |
| 2 | 390625 | 390625 | 1 | True | cp_equals_dual | True | 0 | 0 |
| 3 | 390625 | 1 | 390625 | True | cp_equals_neg_dual | True | 0 | 0 |
| 4 | 390625 | 390625 | 1 | True | cp_equals_dual | True | 0 | 0 |

## Lane `uv_lane_b`
- op_sequence: `[7, 1, 7, 2]`
- ticks: `4`
- enumerated_microstates: `390625`
- full_exhaustive: `True`
- lane_all_ticks_hold: `True`

| Tick | Events | cp==dual | cp==-dual | parity holds all | expected mode | expected mode holds all | strong_cp_delta_sum | strong_dual_delta_sum |
|---:|---:|---:|---:|---|---|---|---:|---:|
| 0 | 390625 | 390625 | 1 | True | cp_equals_dual | True | 0 | 0 |
| 1 | 390625 | 1 | 390625 | True | cp_equals_neg_dual | True | 0 | 0 |
| 2 | 390625 | 390625 | 1 | True | cp_equals_dual | True | 0 | 0 |
| 3 | 390625 | 1 | 390625 | True | cp_equals_neg_dual | True | 0 | 0 |
| 4 | 390625 | 390625 | 1 | True | cp_equals_dual | True | 0 | 0 |

## Limits
- UV witness is exact and exhaustive over a finite microstate lattice for short tick horizons.
- This extends structure-first evidence; it does not alone discharge full continuum EFT identification.
