# Triplet Coherence e000 Robustness Sweep (v1)

- Replay hash: `ff79a7972459b6654c05d22317049ba23a2b609faa36c035d79a8cf5202187ea`
- Kernel profile: `cog_v2_projective_unity_v1`
- Pair count: `4`
- Topology families: `['alt_branch_v1', 'baseline_v1']`
- Robustness lane ready: `True`

## Envelope
- envelope_id: `theta_discrete_correction_envelope_robustness_v1`
- coherent_near_first_order_fraction_mean_E: `0.6625`
- coherent_far_high_order_fraction_mean_E: `0.5344827586206896`
- coherent_near_high_order_fraction_mean_E: `0.3375`
- critical_all_pairs_hold: `True`
- supporting_majority_hold: `True`

## Pair Summary
| Pair | Topology | all_checks_pass | coherent mean_C_t | broken mean_E_t | broken mean_M_t |
|---|---|---|---:|---:|---:|
| pair_1 | baseline_v1 | True | 0.4495767195767196 | 0.13146825396825396 | 5.633333333333334 |
| pair_2 | baseline_v1 | True | 0.4495767195767196 | 0.13146825396825396 | 5.633333333333334 |
| pair_3 | baseline_v1 | False | 0.47138888888888886 | 0.5041666666666667 | 0.9916666666666667 |
| pair_4 | alt_branch_v1 | True | 0.4697751322751323 | 0.14027777777777778 | 5.208333333333333 |

## Check Pass Rates
| Check | Pass rate |
|---|---:|
| broken_correction_onset_not_later_than_coherent | 0.75 |
| coherence_higher_in_coherent_triplet | 1.0 |
| coherent_farfield_high_order_fraction_gt_nearfield | 1.0 |
| coherent_nearfield_first_order_fraction_ge_0p6 | 0.75 |
| distance_axis_discrete_and_contiguous | 1.0 |
| distance_tail_abs_leakage_higher_in_broken_state | 0.75 |
| distancewise_abs_leakage_nonstrict_majority_broken | 1.0 |
| e000_share_higher_in_broken_state | 1.0 |
| positive_leakage_frequency_higher_in_broken_state | 0.75 |
| terminal_mass_lower_in_broken_state | 1.0 |
| transport_lower_in_broken_state | 1.0 |

## Limits
- Deterministic scenario family sweep, not full physical closure.
- This artifact stress-tests directional stability of the structure-first proxy checks.
- Pair-family coverage can be extended without changing acceptance semantics.
