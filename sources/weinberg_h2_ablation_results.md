# RFC-029 H2 Ablation Results

Target: sin^2(theta_W) = 0.23122000 at scale M_Z

| Policy ID | sin^2(theta_W)_obs | Gap from target | Policy checksum |
|---|---:|---:|---|
| h2_baseline_half | 0.50000000 | +0.26878000 | `e500f5ef295b908b` |
| h2_exclusive_u1_quarter | 0.25000000 | +0.01878000 | `a93571658bdfadef` |
| h2_weak_boost_third | 0.33333333 | +0.10211333 | `2f2ed8a360275fa4` |

## Governance
- Policies were loaded from `calc/weinberg_h2_policies.json`.
- No policy selection by output was performed.
- Structural S4 invariants are validated before evaluation.
