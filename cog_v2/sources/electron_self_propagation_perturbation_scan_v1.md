# Electron Self-Propagation Perturbation Scan (v1)

## Goal

Determine which one-shot perturbations of a stable electron motif produce coherent self-propagation in 3D vacuum background.

## Params

- ticks: `24`
- size_xyz: `15`
- warmup_ticks: `2`
- directionality_threshold: `0.6`
- net_displacement_threshold: `1.0`
- min_speed_threshold: `0.08`

## Ranked Cases (Top 12)

| rank | case_id | coherence_score | directionality | net_displacement | mean_speed | coherent |
|---:|---|---:|---:|---:|---:|---:|
| 1 | `center_left_e001` | 12.124356 | 1.000000 | 12.124356 | 0.527146 | True |
| 2 | `center_left_e010` | 12.124356 | 1.000000 | 12.124356 | 0.527146 | True |
| 3 | `center_left_e011` | 12.124356 | 1.000000 | 12.124356 | 0.527146 | True |
| 4 | `center_left_e100` | 12.124356 | 1.000000 | 12.124356 | 0.527146 | True |
| 5 | `center_left_e101` | 12.124356 | 1.000000 | 12.124356 | 0.527146 | True |
| 6 | `center_left_e110` | 12.124356 | 1.000000 | 12.124356 | 0.527146 | True |
| 7 | `center_neighbor_px_left_e001` | 9.019137 | 0.733471 | 12.296510 | 0.728905 | True |
| 8 | `center_neighbor_px_left_e010` | 9.019137 | 0.733471 | 12.296510 | 0.728905 | True |
| 9 | `center_neighbor_px_left_e011` | 9.019137 | 0.733471 | 12.296510 | 0.728905 | True |
| 10 | `center_neighbor_px_left_e100` | 9.019137 | 0.733471 | 12.296510 | 0.728905 | True |
| 11 | `center_neighbor_px_left_e101` | 9.019137 | 0.733471 | 12.296510 | 0.728905 | True |
| 12 | `center_neighbor_px_left_e110` | 9.019137 | 0.733471 | 12.296510 | 0.728905 | True |

## Coherent Cases

- `center_left_e001`
- `center_left_e010`
- `center_left_e011`
- `center_left_e100`
- `center_left_e101`
- `center_left_e110`
- `center_neighbor_px_left_e001`
- `center_neighbor_px_left_e010`
- `center_neighbor_px_left_e011`
- `center_neighbor_px_left_e100`
- `center_neighbor_px_left_e101`
- `center_neighbor_px_left_e110`

## Checks

- has_control_case: `True`
- best_case_beats_control_coherence: `True`
- rows_match_ticks_all_cases: `True`
- likely_fold_order_anisotropy: `True`

## Diagnostics

- core_directional_score_span: `0.0`
- core_directional_all_end_at_origin: `True`
- interpretation: If true, coherent drift may be dominated by non-commutative parent-fold order bias instead of physically distinct perturbation content.
