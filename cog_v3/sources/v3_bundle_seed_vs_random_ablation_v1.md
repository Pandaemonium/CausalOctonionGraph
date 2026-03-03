# v3 Bundle Seed vs Random Ablation (v1)

- panel_id: `P0_s960_bundle_ablation`
- convention_id: `v3_octavian240_perm_0-1-2-3-4-7-5-6_sign_all_plus`
- seed_budget: `40`

| strategy | seed_count | candidate_lock_yield | propagating_yield | score_mean | score_p90 |
|---|---:|---:|---:|---:|---:|
| `random4` | 10 | 0.0000 | 0.0000 | 0.3056 | 0.3468 |
| `bundle4` | 10 | 0.0000 | 0.0000 | 0.3334 | 0.3334 |
| `single_order12` | 10 | 0.0000 | 0.0000 | 0.2801 | 0.2801 |
| `single_order3` | 10 | 0.0000 | 0.0000 | 0.6000 | 0.6000 |

## Effect Size vs Control (`random4`)

- {"bundle4": {"delta_candidate_lock_yield": 0.0, "delta_propagating_yield": 0.0, "delta_score_mean": 0.027792103546489755}, "random4": {"delta_candidate_lock_yield": 0.0, "delta_propagating_yield": 0.0, "delta_score_mean": 0.0}, "single_order12": {"delta_candidate_lock_yield": 0.0, "delta_propagating_yield": 0.0, "delta_score_mean": -0.025576338127187015}, "single_order3": {"delta_candidate_lock_yield": 0.0, "delta_propagating_yield": 0.0, "delta_score_mean": 0.294365352834912}}

## Gate Results

- {"gate1_bundle_beats_random_lock": false, "gate2_bundle_beats_random_prop": false, "gate3_bundle_beats_random_score": true}
