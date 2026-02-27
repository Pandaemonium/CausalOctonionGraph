# S4 Character-Weight Weinberg Scan

Deterministic scan over predeclared irrep-weight combinations.
Target: `sin^2(theta_W) = 0.23122`

| Transform | U1 irrep | EW irrep | sin^2(theta_W)_obs | Gap |
|---|---|---|---:|---:|
| absolute | chi_2d | chi_sign | 0.66666667 | +0.43544667 |
| absolute | chi_2d | chi_trivial | 0.66666667 | +0.43544667 |
| absolute | chi_3d_std | chi_sign | 0.75000000 | +0.51878000 |
| absolute | chi_3d_std | chi_trivial | 0.75000000 | +0.51878000 |
| absolute | chi_3d_twist | chi_sign | 0.75000000 | +0.51878000 |
| absolute | chi_3d_twist | chi_trivial | 0.75000000 | +0.51878000 |
| absolute | chi_2d | chi_3d_std | 0.88888889 | +0.65766889 |
| absolute | chi_2d | chi_3d_twist | 0.88888889 | +0.65766889 |
| square | chi_2d | chi_2d | 1.00000000 | +0.76878000 |
| square | chi_2d | chi_3d_std | 1.00000000 | +0.76878000 |
| square | chi_2d | chi_3d_twist | 1.00000000 | +0.76878000 |
| square | chi_2d | chi_sign | 1.00000000 | +0.76878000 |
| square | chi_2d | chi_trivial | 1.00000000 | +0.76878000 |
| square | chi_3d_std | chi_2d | 1.00000000 | +0.76878000 |
| square | chi_3d_std | chi_3d_std | 1.00000000 | +0.76878000 |
| square | chi_3d_std | chi_3d_twist | 1.00000000 | +0.76878000 |
| square | chi_3d_std | chi_sign | 1.00000000 | +0.76878000 |
| square | chi_3d_std | chi_trivial | 1.00000000 | +0.76878000 |
| square | chi_3d_twist | chi_2d | 1.00000000 | +0.76878000 |
| square | chi_3d_twist | chi_3d_std | 1.00000000 | +0.76878000 |

## Notes
- This is an avenue probe, not a promoted observable contract.
- No policy was selected post-hoc for claim promotion.
- Use this to decide which irrep-based weighting families are worth formalizing in Lean.
