# v3 Neutrino Phase-Swap Probe (v1)

- kernel_profile: `cog_v3_octavian240_multiplicative_v1`
- convention_id: `v3_octavian240_perm_0-1-2-3-4-7-5-6_sign_all_plus`
- ticks: `20`
- size: `[15, 9, 9]`

| seed_label | case_id | odd_non3_rate_local | swap_to_seed_g_rate_local |
|---|---|---:|---:|
| `neutrino_like_identity` | `in_phase` | 0.316000 | 0.056054 |
| `neutrino_like_identity` | `same_gen_diff_subphase` | 0.316000 | 0.056054 |
| `neutrino_like_identity` | `off_phase_g0` | 0.534000 | 0.233668 |
| `neutrino_like_identity` | `off_phase_g2` | 0.500000 | 0.115566 |
| `control_e111` | `in_phase` | 0.316000 | 0.056054 |
| `control_e111` | `same_gen_diff_subphase` | 0.316000 | 0.056054 |
| `control_e111` | `off_phase_g0` | 0.534000 | 0.233668 |
| `control_e111` | `off_phase_g2` | 0.500000 | 0.115566 |

## Neutrino-vs-Control Deltas

| case_id | delta_odd_non3_rate_local | delta_swap_to_seed_g_rate_local |
|---|---:|---:|
| `in_phase` | 0.000000 | 0.000000 |
| `same_gen_diff_subphase` | 0.000000 | 0.000000 |
| `off_phase_g0` | 0.000000 | 0.000000 |
| `off_phase_g2` | 0.000000 | 0.000000 |

## Interpretation Hint

- If deltas are near zero across cases, behavior is phase-generic in current kernel (not neutrino-specific).
- If off-phase cases are high for both seed types, that indicates mismatch-driven dynamics rather than neutrino-unique swapping.