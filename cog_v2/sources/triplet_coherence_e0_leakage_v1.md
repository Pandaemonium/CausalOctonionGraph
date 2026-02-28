# Triplet Coherence vs e0 Leakage Probe (v1)

- Hypothesis ID: `triplet_coherence_e0_leakage_v1`
- Replay hash: `5a3a8b7251df6b741cdb2d909661eb2c135cd1f8b7072de671cd1889634cbea1`
- Kernel profile: `cog_v2_projective_unity_v1`
- Projector ID: `pi_unity_axis_dominance_v1`
- Ticks: 120

## Scenario Summary
| Metric | coherent_triplet_v1 | broken_off_cycle_v1 |
|---|---:|---:|
| mean_C_t | 0.4597222222222222 | 0.30694444444444446 |
| mean_M_t | 3.441666666666667 | 3.0 |
| mean_E_t | 0.0125 | 0.28541666666666665 |
| mean_T_t | 0.6125 | 0.375 |
| positive_L_t_fraction | 0.01680672268907563 | 0.24369747899159663 |
| mean_positive_L_t | 1.0 | 1.0 |

## Hypothesis Checks
- `coherence_higher_in_coherent_triplet`: `True`
- `e0_share_higher_in_broken_state`: `True`
- `positive_leakage_frequency_higher_in_broken_state`: `True`
- `terminal_mass_lower_in_broken_state`: `True`
- `transport_lower_in_broken_state`: `True`
- `all_checks_pass`: `True`

## Limits
- Toy 4-node DAG probe, not full physical closure.
- Observables are proxy metrics designed for falsifiable directionality tests.
- Does not by itself select a unique continuum bridge law.
