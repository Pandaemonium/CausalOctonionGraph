# COG v3 Stable Motif Scan (v1)

## Params

- ticks: `24`
- size: `15 x 7 x 7`
- boundary_mode: `fixed_vacuum`
- stencil_id: `cube26` (size `26`)
- period range: `2..8`
- max_shift_x: `2`
- repeat_checks: `2`

## Trial Summary

| trial_id | seed_family | seeded_cells | candidate_count | best_class | best_period | best_dx | best_support_ratio |
|---|---|---:|---:|---|---:|---:|---:|
| `photon_sheet_e111_kick_e001` | `photon_sheet_x` | 9 | 0 | - | - | - | - |
| `photon_sheet_e111_kick_e010` | `photon_sheet_x` | 9 | 0 | - | - | - | - |
| `single_e111_kick_e001` | `single_unit` | 1 | 6 | `candidate_lock/stationary` | 8 | 0 | 0.941176 |

## Checks

- trial_count: `3`
- any_strict_lock: `False`
- any_candidate_lock: `True`
- any_stationary_candidate: `True`
- any_propagating_candidate: `False`
