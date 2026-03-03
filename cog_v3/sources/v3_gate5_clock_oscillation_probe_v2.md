# v3 Gate-5 Clock Oscillation Probe (v2)

- kernel_profile: `cog_v3_octavian240_multiplicative_v1`
- convention_id: `v3_octavian240_perm_0-1-2-3-4-7-5-6_sign_all_plus`
- backend: `numba_cpu`

| kernel_candidate_id | channel_policy_id | stable_count | oscillatory_count | diffusive_count | median_peak_ratio | median_period |
|---|---|---:|---:|---:|---:|---:|
| `K0_cube26_uniform_v1` | `uniform_all` | 0 | 0 | 4 | 0.2670 | 4.05 |
| `K2_cube26_stochastic_v1` | `stochastic_gating_v1` | 0 | 0 | 4 | 0.0957 | 4.82 |
| `K1_cube26_det_cycle_v1` | `deterministic_cycle_v1` | 0 | 0 | 4 | 0.1980 | 11.57 |

## Notes

- `coherent_oscillatory` requires spectral peak evidence, not just gate-5 failure.
- This is a diagnostic classifier, not a particle identification claim.