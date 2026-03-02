# Photon Chirality-Direction Probe (v1)

## Params

- ticks: `96`
- width: `257`
- packet_width: `9`
- warmup_ticks: `24`

## Case Summaries

| case_id | mean_centroid_velocity_x_tail | mean_directionality_index_tail | left_front_speed_mean_abs | right_front_speed_mean_abs |
|---|---:|---:|---:|---:|
| `flat_su` | 0.000000 | 0.000000 | 1.000000 | 1.000000 |
| `ramp_plus_su` | 0.000000 | 0.000000 | 1.000000 | 1.000000 |
| `ramp_minus_su` | 0.000000 | 0.000000 | 1.000000 | 1.000000 |
| `ramp_plus_sd` | 0.000000 | 0.000000 | 1.000000 | 1.000000 |
| `ramp_minus_sd` | 0.000000 | 0.000000 | 1.000000 | 1.000000 |

## Checks

- all_cases_lightcone_saturated_fronts: `True`
- su_ramp_has_signed_opposite_drift: `False`
- sd_ramp_has_signed_opposite_drift: `False`
- any_nonzero_group_drift: `False`
