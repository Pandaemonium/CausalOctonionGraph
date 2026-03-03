# v3 Two-Region Seed R3 Probe (v1)

- kernel_profile: `cog_v3_octavian240_multiplicative_v1`
- convention_id: `v3_octavian240_perm_0-1-2-3-4-7-5-6_sign_all_plus`

| panel_id | stencil | any_d3_global | any_d3_boundary | any_odd_global | any_odd_boundary |
|---|---|---|---|---|---|
| `P0_axial6_two_region_0_vs_3` | `axial6` | True | True | True | True |
| `P1_cube26_two_region_0_vs_3` | `cube26` | True | True | True | True |

## Notes

- Seed is a sharp boundary: left half `phase=0`, right half `phase=3`, same Q240 element.
- Probe reports both global and boundary-only hop activity.
- Snapshots include phase histograms at ticks 1, 10, 50.