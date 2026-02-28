# THETA-001 Continuum Bridge Diagnostics (v2)

- Claim: `THETA-001`
- Scope: `structure_first`
- Replay hash: `ad02458a2f0a7094782654eb82dce2a366ed74a8f4b9f6ce83974e3e213995a9`

## Depth Sweep
- Depth schedule: [12, 16, 20, 24, 32, 40, 48, 56, 64, 72]

| Depth | Combined n | Max abs residual | RMS residual | Max abs residual / depth | All zero |
|---:|---:|---:|---:|---:|---|
| 12 | 1764 | 0.0 | 0.0 | 0.0 | True |
| 16 | 1764 | 0.0 | 0.0 | 0.0 | True |
| 20 | 1764 | 0.0 | 0.0 | 0.0 | True |
| 24 | 1764 | 0.0 | 0.0 | 0.0 | True |
| 32 | 1764 | 0.0 | 0.0 | 0.0 | True |
| 40 | 1764 | 0.0 | 0.0 | 0.0 | True |
| 48 | 1764 | 0.0 | 0.0 | 0.0 | True |
| 56 | 1764 | 0.0 | 0.0 | 0.0 | True |
| 64 | 1764 | 0.0 | 0.0 | 0.0 | True |
| 72 | 1764 | 0.0 | 0.0 | 0.0 | True |

## Convergence Diagnostics
- max_abs_nonincreasing: `True`
- rms_nonincreasing: `True`
- zero_plateau_depth: `12`
- finite_size_fit(mean_abs vs 1/depth): `{'slope': 0.0, 'intercept': 0.0, 'r2': 1.0}`

## Discrete Correction Envelope
- envelope_id: `theta_discrete_correction_envelope_v1`
- near_field_mode: `first_order_dominant`
- correction_mode: `higher_order_corrections_active`
- coherent_correction_onset_d_E: `16`
- broken_correction_onset_d_E: `0`
- correction_lane_ready: `True`

## Readiness
- finite_size_residual_stable_zero: `True`
- normalized_residual_stable_zero: `True`
- discrete_correction_lane_ready: `True`
- full_value_closure_ready: `False`

## Notes
- This artifact strengthens bridge diagnostics but does not establish proved_core by itself.
