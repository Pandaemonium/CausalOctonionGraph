# v3 e-neutrino Volume Probe (v1)

- kernel_profile: `cog_v3_s2880_pair_conservative_v1`
- convention_id: `v3_octavian240_perm_0-1-2-3-4-7-5-6_sign_all_plus`
- grid: `[15, 15, 15]`
- ticks: `16`
- radius: `3`
- sweep_c4: `False`

## Requested Seed Components

- g (Z3): `1`
- q coeffs: `[1, 0, 0, 0, 0, 0, 0, 0]`
- E (Z): `4` (recorded; non-dynamical in this lane)
- a (Z4): `1`

## Case Summary

| a (Z4) | phase_idx (Z12) | sid | sid_label | max_com_displacement | final_com_displacement | final_active_count |
|---:|---:|---:|---|---:|---:|---:|
| 1 | 7 | 1919 | `zeta12^7*(1*e000)` | 0.623693 | 0.132225 | 2969.0 |

## Interpretation

- Nonzero COM displacement means net propagation/drift of the seeded volume.
- If displacement is ~0 at final tick, the seeded volume is approximately stationary overall.
- To test true E-driven kinetics, E must be upgraded to a dynamical kernel field.