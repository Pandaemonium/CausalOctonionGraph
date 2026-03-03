# v3 Bundle12 Seed vs Random Ablation (v1)

- kernel_profile: `cog_v3_octavian240_multiplicative_v1`
- convention_id: `v3_octavian240_perm_0-1-2-3-4-7-5-6_sign_all_plus`
- runs_per_strategy: `220`

| strategy | run_count | candidate_lock_yield | propagating_yield | median_period | median_drift | median_displacement |
|---|---:|---:|---:|---:|---:|---:|
| `random4` | 220 | 0.0000 | 0.0000 |  | 0.7496 | 0.2500 |
| `bundle4` | 220 | 0.0000 | 0.0000 |  | 0.6619 | 0.2393 |
| `bundle12` | 220 | 0.0000 | 0.0000 |  | 0.5680 | 0.1687 |
| `koide3` | 220 | 0.0000 | 0.0000 |  | 0.5152 | 0.0000 |

## Notes

- `bundle4`: phases `[p, p+3, p+6, p+9]` on one qid.
- `bundle12`: phases `[p..p+11]` on one qid.
- `koide3`: phases `[p, p+4, p+8]` on one qid.