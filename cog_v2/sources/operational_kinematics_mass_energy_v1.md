# Operational Kinematics / Mass / Kinetic Suite (v1)

## Params

- ticks: `56`
- burn_in_ticks: `20`
- measure_ticks: `24`
- kick_ops: `[1, 2, 3, 4]`
- profiles: `['elongated_1d_x41', 'elongated_3d_offaxis_x41_y11_z11']`
- fold_order_variants: `['canonical_xyz', 'reverse_xyz', 'axis_cycle_yzx', 'plus_first']`

## Profile Geometry

| profile_id | size_xyz | aspect_ratio_x_over_max_yz |
|---|---|---:|
| `elongated_1d_x41` | `[41, 1, 1]` | 41.0 |
| `elongated_3d_offaxis_x41_y11_z11` | `[41, 11, 11]` | 3.727272727272727 |

## Shape Robustness Summary

| particle_id | energy_id | relative_delta_velocity_gap | relative_mass_gap | shape_robust |
|---|---|---:|---:|---:|
| `left_spinor_electron_ideal` | `E1_center_kick` | 0.9613233772327304 | 0.9613233772327304 | False |
| `left_spinor_electron_ideal` | `E2_center_plus_shell1` | 0.49631211356267446 | 0.4963121135626745 | False |
| `left_spinor_electron_ideal` | `E3_center_plus_shell2` | 1.0 | None | False |
| `left_spinor_muon_motif` | `E1_center_kick` | 0.9613233772327304 | 0.9613233772327304 | False |
| `left_spinor_muon_motif` | `E2_center_plus_shell1` | 0.0 | 0.0 | True |
| `left_spinor_muon_motif` | `E3_center_plus_shell2` | 0.41428571428571426 | 0.4142857142857142 | False |
| `left_spinor_tau_motif` | `E1_center_kick` | 0.9613233772327304 | 0.9613233772327304 | False |
| `left_spinor_tau_motif` | `E2_center_plus_shell1` | 0.0 | 0.0 | True |
| `left_spinor_tau_motif` | `E3_center_plus_shell2` | 0.41428571428571426 | 0.4142857142857142 | False |
| `right_spinor_electron_ideal` | `E1_center_kick` | 0.9613233772327304 | 0.9613233772327304 | False |
| `right_spinor_electron_ideal` | `E2_center_plus_shell1` | 1.0 | None | False |
| `right_spinor_electron_ideal` | `E3_center_plus_shell2` | 1.0 | None | False |
| `vector_proton_proto_t124` | `E1_center_kick` | 1.9999999999998914 | 1.0861373528964831e-13 | False |
| `vector_proton_proto_t124` | `E2_center_plus_shell1` | 0.5733255382445287 | 0.3601351832336363 | False |
| `vector_proton_proto_t124` | `E3_center_plus_shell2` | 0.5695350191251999 | 0.4262143313813207 | False |

## Checks

- any_profile_elongated_x_over_10: `True`
- has_large_offaxis_profile_yz_ge_11: `True`
- any_shape_robust_case: `True`
- shape_comparison_count: `15`
- particle_count_processed: `5`
