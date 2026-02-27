# RFC-037 Avenue 13 Associator-Running Results

Traffic source: deterministic rollout payloads (not handcrafted triple schedules).
Target: sin^2(theta_W) = 0.23122000 at scale M_Z
Initial state mode: `uniform_ew_unit`
Ticks: `24`

| Policy | Seq initial | Seq final | Seq delta | Seq nonincreasing | Empirical final |
|---|---:|---:|---:|---|---:|
| a13_associative_control_rollout | 0.25000000 | 0.25000000 | +0.00000000 | True | 0.25000000 |
| a13_mixed_nonassoc_rollout | 0.25000000 | 0.04166667 | -0.20833333 | True | 0.04166667 |

## Interpretation
- `series_seq` uses per-tick observed rollout triples.
- `series_empirical_avg` reconstructs running from empirical triple frequencies (mean tick loads).
- This branch is still a mechanism probe, not a promoted derivation.
