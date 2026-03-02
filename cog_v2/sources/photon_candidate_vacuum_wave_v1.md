# Photon-Candidate Vacuum Wave (v1)

## Scope

- Model: coherent vacuum-phase packet in 1D canonical kernel lane
- Not a full electrodynamic closure claim

## Params

- ticks: `64`
- width: `257`
- packet_width: `5`
- thin_output_step: `1`
- motif_ids: `['su_vacuum_omega', 'sd_vacuum_omega_dag']`

## Lane Summaries

| motif_id | left_front_speed_mean_abs | right_front_speed_mean_abs | max_front_step_speed_abs | causal_bound_front_speed_le_1 | lightcone_saturated_front_speed_eq_1 | final_dominant_e111 | final_dominant_e111_share |
|---|---:|---:|---:|---|---|---|---:|
| `su_vacuum_omega` | 1.000000 | 1.000000 | 1.000000 | True | True | `[0, 1]` | 1.000000 |
| `sd_vacuum_omega_dag` | 1.000000 | 1.000000 | 1.000000 | True | True | `[0, -1]` | 1.000000 |

## Checks

- all_lanes_causal_bound_ok: `True`
- all_lanes_lightcone_saturated: `True`
- all_lanes_high_phase_alignment: `True`
