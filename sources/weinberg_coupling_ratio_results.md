# RFC-037 Avenue 7 Coupling-Ratio Results

Target: sin^2(theta_W) = 0.23122000 at scale M_Z

| Policy ID | g'^2 source | g^2 source | sin^2(theta_W)_obs | Gap from target | Policy checksum |
|---|---|---|---:|---:|---|
| a7_baseline_half | u1_card | ew_minus_u1_card | 0.50000000 | +0.26878000 | `084c6c5d88521e6c` |
| a7_exclusive_u1_quarter | exclusive_u1_card | weak_card | 0.25000000 | +0.01878000 | `ad4078d33886e2fa` |
| a7_overlap_shift_third | u1_card | ew_card | 0.33333333 | +0.10211333 | `a2f3bcb132ba727c` |

Best Avenue-7 row by absolute gap:
- `a7_exclusive_u1_quarter` with sin^2(theta_W)=0.25000000, gap=+0.01878000

## Governance
- Policies are predeclared in `calc/weinberg_coupling_policies.json`.
- Coupling proxies are fixed to locked weak-mixing observables before evaluation.
- No output-driven policy selection is applied.
