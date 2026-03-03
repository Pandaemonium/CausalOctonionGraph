# v3 Gate-5 Clock Repeat Probe (v1)

- kernel_profile: `cog_v3_octavian240_multiplicative_v1`
- convention_id: `v3_octavian240_perm_0-1-2-3-4-7-5-6_sign_all_plus`
- backend: `numba_cpu`
- candidate_count: `3`

## Candidate Status

| kernel_candidate_id | channel_policy_id | manifest_gate5 | scan_recurrence_ok | drift_ok | collapse_ok | noise_ok | likely_bottlenecks |
|---|---|---|---|---|---|---|---|
| `K0_cube26_uniform_v1` | `uniform_all` | False | False | False | True | True | primary:manifest_recurrence_absent_seed_sensitive, primary:clock_signature_drift_high |
| `K2_cube26_stochastic_v1` | `stochastic_gating_v1` | False | False | True | True | True | primary:scan_recurrence_absent, secondary:no_world_state_repeat_within_horizon |
| `K1_cube26_det_cycle_v1` | `deterministic_cycle_v1` | False | False | True | True | True | primary:scan_recurrence_absent, secondary:no_world_state_repeat_within_horizon |

## Summary

- manifest_gate5_pass_count: `0`
- candidates_with_scan_recurrence_rate_lt_0p2: `2`

## Notes

- Gate-5 requires both recurrence from fast scan and clock-structure quality checks.
- Repeat-horizon probe is diagnostic only; it does not modify the fixed-manifest gate contract.