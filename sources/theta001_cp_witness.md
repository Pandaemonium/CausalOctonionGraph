# THETA-001 CP-Invariance Witness

- Claim: `THETA-001`
- Policy: `theta001_cp_invariance_v1`
- Replay hash: `0482e9f6c058108b5be7f4726e72fd8fcbe364b37d8fe9176930a0b5c8fd76d6`
- Source script: `calc/build_theta001_witness.py`
- Witness module: `calc/theta001_cp_invariant.py`

## Scope And Scale
- Closure scope: `structure_first`
- Continuum value derivation: `False`
- Validation scale: `reduced_scale`
- Trace case count: `3`

## Replay Verification
Run `python -m calc.build_theta001_witness --write-sources` and verify the replay hash in the JSON output is unchanged.

## Fano Sign Balance
- Positive count: 21
- Negative count: 21
- Signed sum: 0

## Orientation Witness
- Orientation reversal closed on Fano lines: `True`
- Canonical triple count: 7

## Trace Suite

| Case | CP-dual relation | Weighted trace delta |
|---|---|---:|
| theta_case_001 | True | 0 |
| theta_case_002 | True | 0 |
| theta_case_003 | True | 0 |

## Residual Summary
- CP-dual all hold: `True`
- Weighted trace all zero: `True`
- Weak-leakage strong residual zero: `True`
- Weak-leakage strong residual value: `0`
- Max abs weighted trace delta: 0
- Fano signed sum zero: `True`
- `discrete_fano_cp_residual_zero`: `True`
- Legacy alias `theta_cp_odd_residual_forced_zero`: `True`

## Governance Notes
- Witness cases and weights are predeclared constants in this script.
- No output-driven tuning is allowed for claim-grade promotion.
