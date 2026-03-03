# v3 Pair-Conservative Kernel Smoke (v1)

- date: `2026-03-03`
- kernel_profile: `cog_v3_s2880_pair_conservative_v1`
- module: `cog_v3/python/kernel_s2880_pair_conservative_v1.py`

## Protocol

Random S2880 worlds (`7x7x7`, uniform random sid in `[0, 2879]`), then `8` ticks with
`step_pair_conservative`, checking:

- `Gamma_total(t) = sum_i (phase_i mod 3) mod 3` is constant.

## Results

| stencil | boundary | edge-color rounds | gamma_exact_over_8_ticks |
|---|---|---:|---|
| `axial6` | `fixed_vacuum` | `6` | `true` |
| `axial6` | `periodic` | `7` | `true` |
| `cube26` | `fixed_vacuum` | `26` | `true` |
| `cube26` | `periodic` | `37` | `true` |

## Notes

- This confirms exact **global triality conservation** for the new pair-event lane.
- This does not yet include momentum/angular momentum/energy fields; those require an extended state model.
