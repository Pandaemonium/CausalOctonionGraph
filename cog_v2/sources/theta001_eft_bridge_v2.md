# THETA-001 EFT Bridge Probe (v2)

- Claim: `THETA-001`
- Scope: `structure_first`
- Replay hash: `50e31b49986ddb2f42f57761c4316a6b48b38b0a631b77bae2fe80324d0f2639`

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

## Map Identification
- Policy ID: `theta_map_identification_linear_unit_v1`
- Eligible maps: `['linear_scale_1_v1']`
- Selected map: `linear_scale_1_v1`
- Selected unique: `True`

## Q_top Proxy Suite
- CP-odd all hold: `True`
- Max abs Q_top proxy: 29872

| Case | Q_top proxy | CP-dual Q_top | CP odd holds |
|---|---:|---:|---|
| eft_case_001 | 9144 | -9144 | True |
| eft_case_002 | -597 | 597 | True |
| eft_case_003 | 29872 | -29872 | True |

## Readiness
- cp_odd_proxy_consistent: `True`
- map_suite_has_cp_odd_candidate: `True`
- map_identification_locked: `True`
- full_value_closure_ready: `False`

## Notes
- This artifact is an EFT-bridge probe, not full continuum closure.
- Non-zero affine offsets are included intentionally to expose zero-anchor violations.
