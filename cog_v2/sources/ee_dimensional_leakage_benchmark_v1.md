# EE Dimensional Leakage Benchmark (v1)

## Purpose

Compare 1D vs 2D strip vs 2D full vs 3D full lanes for off-axis leakage and distance-response scaling.

## Params

- ticks: `180`
- warmup_ticks: `90`
- width: `31`
- strip_height: `5`
- full_height: `15`
- full_depth: `7`
- separations: `[6, 10, 14, 18]`
- thin_output_step: `4`

## Lane Summary

### line_1d
- mean_leakage_across_separations: `0.0`
- fitted_exponent_n: `-0.0`
- fit_r2: `1.0`

### strip_2d
- mean_leakage_across_separations: `0.8`
- fitted_exponent_n: `-0.0`
- fit_r2: `1.0`

### full_2d
- mean_leakage_across_separations: `0.9333333333333333`
- fitted_exponent_n: `-0.0`
- fit_r2: `1.0`

### full_3d
- mean_leakage_across_separations: `0.9904761904761904`
- fitted_exponent_n: `-0.0`
- fit_r2: `1.0`

## Checks

- one_d_zero_leakage: `True`
- strip_has_nonzero_leakage: `True`
- full2_has_nonzero_leakage: `True`
- full3_has_nonzero_leakage: `True`
- full2_leakage_ge_strip: `True`
- full3_leakage_ge_full2: `True`

## 1D Validity Report

- decision: `FAIL`
- one_d_proxy_valid: `False`
- lane_leakage_means: `{'line_1d': 0.0, 'strip_2d': 0.8, 'full_2d': 0.9333333333333333, 'full_3d': 0.9904761904761904}`
- missing_lanes: `[]`

## Interpretation

- If 2D/3D leakage is nontrivial, strict 1D isolation is not physically generic.
- If 3D leakage >= 2D leakage, surrounding volume materially changes mediator transport.
