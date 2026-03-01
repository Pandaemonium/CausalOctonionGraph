# Electron Excited RPO Scan (v1)

Searches exact relative periodic orbits under x-shift translation on a 3D torus.

## Params

- ticks: `40`
- size_xyz: `7`
- burn_in_ticks: `8`
- min_period..max_period: `2..16`
- kick_ops: `[1, 2, 3, 4, 5, 6, 7]`
- max_shift_x: `3`
- fold_order_variants: `['canonical_xyz', 'reverse_xyz', 'axis_cycle_yzx', 'plus_first']`

## Cases

| case_id | variants_with_rpo | all_variants_found_rpo | all_variants_same_period_shift | representative_period_shift | representative_speed |
|---|---:|---:|---:|---|---:|
| `control_none` | 4 | True | True | `[14, 0]` | `0.0` |
| `center_left_e001` | 4 | True | True | `[2, 1]` | `0.5` |
| `center_left_e010` | 4 | True | True | `[2, 1]` | `0.5` |
| `center_left_e011` | 4 | True | True | `[2, 1]` | `0.5` |
| `center_left_e100` | 4 | True | True | `[2, 1]` | `0.5` |
| `center_left_e101` | 4 | True | True | `[2, 1]` | `0.5` |
| `center_left_e110` | 4 | True | True | `[2, 1]` | `0.5` |
| `center_left_e111` | 4 | True | True | `[2, 1]` | `0.5` |
| `center_neighbor_px_left_e001` | 4 | True | True | `[2, 1]` | `0.5` |
| `center_neighbor_px_left_e010` | 4 | True | True | `[2, 1]` | `0.5` |
| `center_neighbor_px_left_e011` | 4 | True | True | `[2, 1]` | `0.5` |
| `center_neighbor_px_left_e100` | 4 | True | True | `[2, 1]` | `0.5` |
| `center_neighbor_px_left_e101` | 4 | True | True | `[2, 1]` | `0.5` |
| `center_neighbor_px_left_e110` | 4 | True | True | `[2, 1]` | `0.5` |
| `center_neighbor_px_left_e111` | 4 | True | True | `[14, 0]` | `0.0` |
| `neighbor_px_only_e001` | 4 | True | True | `[2, 1]` | `0.5` |
| `neighbor_px_only_e010` | 4 | True | True | `[2, 1]` | `0.5` |
| `neighbor_px_only_e011` | 4 | True | True | `[2, 1]` | `0.5` |
| `neighbor_px_only_e100` | 4 | True | True | `[2, 1]` | `0.5` |
| `neighbor_px_only_e101` | 4 | True | True | `[2, 1]` | `0.5` |
| `neighbor_px_only_e110` | 4 | True | True | `[2, 1]` | `0.5` |
| `neighbor_px_only_e111` | 4 | True | True | `[14, 0]` | `0.0` |

## Robust RPO Cases

- `control_none`
- `center_left_e001`
- `center_left_e010`
- `center_left_e011`
- `center_left_e100`
- `center_left_e101`
- `center_left_e110`
- `center_left_e111`
- `center_neighbor_px_left_e001`
- `center_neighbor_px_left_e010`
- `center_neighbor_px_left_e011`
- `center_neighbor_px_left_e100`
- `center_neighbor_px_left_e101`
- `center_neighbor_px_left_e110`
- `center_neighbor_px_left_e111`
- `neighbor_px_only_e001`
- `neighbor_px_only_e010`
- `neighbor_px_only_e011`
- `neighbor_px_only_e100`
- `neighbor_px_only_e101`
- `neighbor_px_only_e110`
- `neighbor_px_only_e111`

## Robust Nonzero-Shift RPO Cases

- `center_left_e001`
- `center_left_e010`
- `center_left_e011`
- `center_left_e100`
- `center_left_e101`
- `center_left_e110`
- `center_left_e111`
- `center_neighbor_px_left_e001`
- `center_neighbor_px_left_e010`
- `center_neighbor_px_left_e011`
- `center_neighbor_px_left_e100`
- `center_neighbor_px_left_e101`
- `center_neighbor_px_left_e110`
- `neighbor_px_only_e001`
- `neighbor_px_only_e010`
- `neighbor_px_only_e011`
- `neighbor_px_only_e100`
- `neighbor_px_only_e101`
- `neighbor_px_only_e110`

## Checks

- has_any_rpo: `True`
- has_robust_rpo: `True`
- has_robust_nonzero_shift_rpo: `True`
- rpo_requires_order_robustness_gate: `True`
