# EE 1D Validity Report (v1)

- from_schema: `ee_dimensional_leakage_benchmark_v1`
- from_replay_hash: `7236d61991cbb4c5d2b98de969965f591218d81192fd39433970928b44056725`
- decision: `FAIL`
- one_d_proxy_valid: `False`
- missing_lanes: `[]`

## Leakage Means

- line_1d: `0.0`
- strip_2d: `0.8`
- full_2d: `0.9333333333333333`
- full_3d: `0.9904761904761904`

## Thresholds

- one_d_zero_leakage_eps: `1e-12`
- max_strip_leak_for_1d_valid: `0.05`
- max_full2_leak_for_1d_valid: `0.05`
- max_full3_leak_for_1d_valid: `0.05`

## Notes

- 1D proxy is valid only if higher-dimensional lanes remain near-zero leakage.
- If 2D/3D leakage is nontrivial, 1D over-constrains mediator transport.
