# v3 Omega Hat Diagnostic (v1)

- kernel_profile: `cog_v3_octavian240_multiplicative_v1`
- convention_id: `v3_octavian240_perm_0-1-2-3-4-7-5-6_sign_all_plus`
- pair_rows_analyzed: `4`

## Core Findings

- omega_dominant_rate: `1.0000`
- median_omega_share_of_total_delta: `0.7527`
- median_omega_relative_delta: `0.402227`
- median_omega_abs_diff: `0.073404`
- sign_flip_rate: `0.0000`

## Denominator Stress

- denom_lt_1e-3_rate: `0.0000`
- denom_lt_1e-2_rate: `0.0000`
- denom_lt_5e-2_rate: `0.0000`

## Interpretation Flags

- omega_is_primary_driver: `True`
- small_denominator_primary_cause: `False`
- frequent_sign_inversion: `False`

## Pair Breakdown

| pair_id | count | omega_dominant_rate | median_omega_delta | median_omega_abs_diff | sign_flip_rate |
|---|---:|---:|---:|---:|---:|
| `P_baseline_e_uud_vs_mu_ccs` | 2 | 1.0000 | 0.719934 | 0.131342 | 0.0000 |
| `P_desync_mu_uud_vs_tau_ccs` | 2 | 1.0000 | 0.084521 | 0.015466 | 0.0000 |

## Top Cases (Omega Relative Delta)

| pair_id | seed | size | boundary | orientation | omega_lhs | omega_rhs | omega_delta_rel | omega_abs_diff | max_metric |
|---|---:|---|---|---|---:|---:|---:|---:|---|
| `P_baseline_e_uud_vs_mu_ccs` | 0 | `15x7x7` | `fixed_vacuum` | `x` | 0.051094 | 0.182436 | 0.719934 | 0.131342 | `Omega_hat` |
| `P_baseline_e_uud_vs_mu_ccs` | 1 | `15x7x7` | `fixed_vacuum` | `x` | 0.051094 | 0.182436 | 0.719934 | 0.131342 | `Omega_hat` |
| `P_desync_mu_uud_vs_tau_ccs` | 0 | `15x7x7` | `fixed_vacuum` | `x` | 0.182980 | 0.167515 | 0.084521 | 0.015466 | `Omega_hat` |
| `P_desync_mu_uud_vs_tau_ccs` | 1 | `15x7x7` | `fixed_vacuum` | `x` | 0.182980 | 0.167515 | 0.084521 | 0.015466 | `Omega_hat` |

## Notes

- Diagnostic is post-hoc over RFC-011 rows (no new physics claim).
- If `small_denominator_primary_cause=false`, Omega dominance is not mainly a near-zero denominator artifact.