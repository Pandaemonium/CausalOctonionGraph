# Photon-Candidate Directional Transport (v1)

## Params

- ticks: `36`
- size_xyz: `(121, 11, 11)`
- packet_width_x: `5`
- warmup_ticks: `8`

## Case Summaries

| case_id | left_front_speed_mean_abs | right_front_speed_mean_abs | directionality_index_mean_tail | one_sided_transport_detected |
|---|---:|---:|---:|---|
| `sym_control` | 1.000000 | 1.000000 | 0.000000 | False |
| `dir_grad_plusx` | 1.000000 | 1.000000 | 0.980815 | False |
| `dir_bias_plusx` | 1.000000 | 1.000000 | 0.198813 | False |

## Checks

- all_cases_causal_bound_ok: `True`
- all_cases_lightcone_saturated: `True`
- any_case_one_sided_transport: `False`
- directional_cases_shift_power_asymmetry_vs_control: `True`
