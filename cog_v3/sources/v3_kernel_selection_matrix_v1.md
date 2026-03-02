# v3 Kernel Selection Matrix (v1)

- kernel_profile: `cog_v3_octavian240_multiplicative_v1`
- convention_id: `v3_octavian240_perm_0-1-2-3-4-7-5-6_sign_all_plus`
- event_order_policy: `synchronous_parallel_v1`
- batches: `1`

## Ranked Candidates (Last Batch)

| rank | kernel_candidate_id | channel_policy_id | score_total | gate0 | gate1 | gate2 | gate3 | gate4 | det_excl | anisotropy |
|---:|---|---|---:|---|---|---|---|---|---:|---:|
| 1 | `K2_cube26_stochastic_v1` | `stochastic_gating_v1` | 0.497522 | True | True | False | True | True | 0.187500 | 1.0 |
| 2 | `K1_cube26_det_cycle_v1` | `deterministic_cycle_v1` | 0.453268 | True | True | False | True | False | 0.062500 | 1.0 |
| 3 | `K0_cube26_uniform_v1` | `uniform_all` | 0.439944 | True | True | False | True | False | 0.000000 | 1.0 |

## Notes

- This matrix is exploratory and should be rerun across seed sets before any promotion.