# THETA-001 EFT Bridge Probe (v2)

- Claim: `THETA-001`
- Scope: `structure_first`
- Replay hash: `fe5b9274ad56277eafe07814ca1b4ebc9a87c535113cf46b393994cb919f1439`

## Map Suite
- Map count: 10
- CP-odd all-hold (all maps): `False`
- Zero-anchor all-hold (all maps): `False`

| Map ID | Mode | CP odd all hold | Zero anchor all hold | Max CP odd violation |
|---|---|---|---|---:|
| direct_v1 | direct | True | True | 0.0 |
| linear_scale_-2_v1 | linear | True | True | 0.0 |
| linear_scale_-1_v1 | linear | True | True | 0.0 |
| linear_scale_1_v1 | linear | True | True | 0.0 |
| linear_scale_2_v1 | linear | True | True | 0.0 |
| affine_scale_1_offset_0_v1 | affine | True | True | 0.0 |
| affine_scale_1_offset_0.25_v1 | affine | False | False | 0.5 |
| zero_anchored_poly_scale_1_cubic_0_v1 | zero_anchored_poly | True | True | 0.0 |
| zero_anchored_poly_scale_1_cubic_0.01_v1 | zero_anchored_poly | True | True | 0.0 |
| zero_anchored_poly_scale_1_cubic_0.05_v1 | zero_anchored_poly | True | True | 0.0 |

## Q_top Proxy Suite
- CP-odd all hold: `True`
- Max abs Q_top proxy: 6852

| Case | Q_top proxy | CP-dual Q_top | CP odd holds |
|---|---:|---:|---|
| eft_case_001 | 5346 | -5346 | True |
| eft_case_002 | -1929 | 1929 | True |
| eft_case_003 | 6852 | -6852 | True |

## Readiness
- cp_odd_proxy_consistent: `True`
- map_suite_has_cp_odd_candidate: `True`
- full_value_closure_ready: `False`

## Notes
- This artifact is an EFT-bridge probe, not full continuum closure.
- Non-zero affine offsets are included intentionally to expose zero-anchor violations.
