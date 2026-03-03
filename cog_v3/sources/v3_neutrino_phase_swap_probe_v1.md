# v3 Neutrino Phase-Swap Probe (v1)

- kernel_profile: `cog_v3_s2880_pair_conservative_v1`
- convention_id: `v3_octavian240_perm_0-1-2-3-4-7-5-6_sign_all_plus`
- ticks: `48`
- size: `[9, 9, 9]`

| seed_label | case_id | odd_non3_rate_local | swap_to_seed_g_rate_local |
|---|---|---:|---:|
| `neutrino_like_identity` | `in_phase` | 0.645000 | 0.318414 |
| `neutrino_like_identity` | `same_gen_diff_subphase` | 0.645000 | 0.318414 |
| `neutrino_like_identity` | `off_phase_g0` | 0.645000 | 0.322304 |
| `neutrino_like_identity` | `off_phase_g2` | 0.645000 | 0.350699 |
| `control_e111` | `in_phase` | 0.658333 | 0.291310 |
| `control_e111` | `same_gen_diff_subphase` | 0.658333 | 0.291310 |
| `control_e111` | `off_phase_g0` | 0.658333 | 0.340373 |
| `control_e111` | `off_phase_g2` | 0.658333 | 0.361183 |

## Triality Audit

| seed_label | case_id | gamma_global_nonzero_tick_rate | gamma_local_nonzero_tick_rate |
|---|---|---:|---:|
| `neutrino_like_identity` | `in_phase` | 0.000000 | 0.687500 |
| `neutrino_like_identity` | `same_gen_diff_subphase` | 0.000000 | 0.687500 |
| `neutrino_like_identity` | `off_phase_g0` | 0.000000 | 0.687500 |
| `neutrino_like_identity` | `off_phase_g2` | 0.000000 | 0.687500 |
| `control_e111` | `in_phase` | 0.000000 | 0.750000 |
| `control_e111` | `same_gen_diff_subphase` | 0.000000 | 0.750000 |
| `control_e111` | `off_phase_g0` | 0.000000 | 0.750000 |
| `control_e111` | `off_phase_g2` | 0.000000 | 0.750000 |

## Neutrino-vs-Control Deltas

| case_id | delta_odd_non3_rate_local | delta_swap_to_seed_g_rate_local |
|---|---:|---:|
| `in_phase` | -0.013333 | 0.027105 |
| `same_gen_diff_subphase` | -0.013333 | 0.027105 |
| `off_phase_g0` | -0.013333 | -0.018069 |
| `off_phase_g2` | -0.013333 | -0.010484 |

## Interpretation Hint

- If deltas are near zero across cases, behavior is phase-generic in current kernel (not neutrino-specific).
- If off-phase cases are high for both seed types, that indicates mismatch-driven dynamics rather than neutrino-unique swapping.