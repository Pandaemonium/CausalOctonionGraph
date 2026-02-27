# RFC-029 Weighted Weinberg Estimate

Target scale: `M_Z`

## Governance
- H2 policy file: `calc/weinberg_h2_policies.json`
- H2 policy file sha256: `d0368add1b19757d9fcb85323b182f4631b8914d03bcd48b027e43722e71b9ab`
- H1 bridge file: `calc/weinberg_h1_bridge_policies.json`
- H1 bridge file sha256: `0c585e70a8bf0c83356d4491bbe34d5222118a8f784a97618cf3508d29667409`

## H2 Results

| H2 policy | sin^2(theta_W)_obs | Gap from target | Policy checksum |
|---|---:|---:|---|
| h2_baseline_half | 0.50000000 | +0.26878000 | `e500f5ef295b908b` |
| h2_exclusive_u1_quarter | 0.25000000 | +0.01878000 | `a93571658bdfadef` |
| h2_weak_boost_third | 0.33333333 | +0.10211333 | `2f2ed8a360275fa4` |

Best H2 (abs gap): `h2_exclusive_u1_quarter` with gap `+0.01878000`

## H1 Bridge Results

| H2 policy | H1 bridge policy | Bridged sin^2(theta_W) | Gap from target | Steps | Attenuation | Bridge checksum |
|---|---|---:|---:|---:|---:|---|
| h2_baseline_half | h1_no_running | 0.50000000 | +0.26878000 | 0 | 1.000000 | `243595c42ddb8688` |
| h2_baseline_half | h1_mild_running_4x0p95 | 0.40725312 | +0.17603312 | 4 | 0.950000 | `af5f81b9691d986f` |
| h2_baseline_half | h1_strong_running_8x0p90 | 0.21523361 | -0.01598639 | 8 | 0.900000 | `3100abb8cda0f958` |
| h2_exclusive_u1_quarter | h1_no_running | 0.25000000 | +0.01878000 | 0 | 1.000000 | `243595c42ddb8688` |
| h2_exclusive_u1_quarter | h1_mild_running_4x0p95 | 0.20362656 | -0.02759344 | 4 | 0.950000 | `af5f81b9691d986f` |
| h2_exclusive_u1_quarter | h1_strong_running_8x0p90 | 0.10761680 | -0.12360320 | 8 | 0.900000 | `3100abb8cda0f958` |
| h2_weak_boost_third | h1_no_running | 0.33333333 | +0.10211333 | 0 | 1.000000 | `243595c42ddb8688` |
| h2_weak_boost_third | h1_mild_running_4x0p95 | 0.27150208 | +0.04028208 | 4 | 0.950000 | `af5f81b9691d986f` |
| h2_weak_boost_third | h1_strong_running_8x0p90 | 0.14348907 | -0.08773093 | 8 | 0.900000 | `3100abb8cda0f958` |

Best H1+H2 (abs gap): `h2_baseline_half + h1_strong_running_8x0p90` with gap `-0.01598639`

## Notes
- This report is descriptive, not a proof of mechanism.
- Policies are predeclared; no output-driven tuning was applied.
- Promotion of WEINBERG-001 requires RFC-029 acceptance gates.
