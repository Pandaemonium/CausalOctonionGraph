# Triplet Coherence vs e000 Leakage Probe (v1)

- Hypothesis ID: `triplet_coherence_e000_leakage_v1`
- Replay hash: `434df3266483a696671b18ec5ad48d8988eaa759bf1c4200ba703b6d7d045ec7`
- Kernel profile: `cog_v2_projective_unity_v1`
- Projector ID: `pi_unity_axis_dominance_v1`
- Ticks: 120

## Scenario Summary
| Metric | coherent_triplet_v1 | broken_off_cycle_v1 |
|---|---:|---:|
| mean_C_t | 0.4495767195767196 | 0.3525793650793651 |
| mean_M_t | 6.666666666666667 | 5.633333333333334 |
| mean_E_t | 0.11994047619047618 | 0.13146825396825396 |
| mean_T_t | 0.495 | 0.47527777777777774 |
| positive_L_t_fraction | 0.11764705882352941 | 0.25210084033613445 |
| mean_positive_L_t | 1.0 | 1.0 |

## Discrete Distance Contract
- distance_axis_id: `graph_distance_tick_index_v1`
- domain: `nonnegative_integers`
- contiguous_from_zero: `True`
- tail_window_start_d: `20`
- abs_leakage_nonstrict_fraction_broken_ge_coherent: `0.8151260504201681`

## Discrete Transfer Shape (E_d)
- coherent near_field_first_order_fraction_E: `0.75`
- coherent far_field_high_order_fraction_E: `0.3793103448275862`
- coherent correction_onset_d_E: `16`
- broken correction_onset_d_E: `0`

## Hypothesis Checks
- `coherence_higher_in_coherent_triplet`: `True`
- `e000_share_higher_in_broken_state`: `True`
- `positive_leakage_frequency_higher_in_broken_state`: `True`
- `terminal_mass_lower_in_broken_state`: `True`
- `transport_lower_in_broken_state`: `True`
- `distance_axis_discrete_and_contiguous`: `True`
- `distance_tail_abs_leakage_higher_in_broken_state`: `True`
- `distancewise_abs_leakage_nonstrict_majority_broken`: `True`
- `coherent_nearfield_first_order_fraction_ge_0p6`: `True`
- `broken_correction_onset_not_later_than_coherent`: `True`
- `coherent_farfield_high_order_fraction_gt_nearfield`: `True`
- `all_checks_pass`: `True`

## Limits
- Toy 4-node DAG probe, not full physical closure.
- Observables are proxy metrics designed for falsifiable directionality tests.
- Does not by itself select a unique continuum bridge law.
