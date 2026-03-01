# Particle Excited Propagation Cycle Library (v1)

## Params

- ticks: `48`
- size_xyz: `7`
- burn_in_ticks: `8`
- period range: `2..20`
- kick_ops: `[1, 2, 3, 4, 5, 6, 7]`
- fold_order_variants: `['canonical_xyz', 'reverse_xyz', 'axis_cycle_yzx', 'plus_first']`

## Particle Summary

| particle_id | selected_case_count | has_two_energy_cases |
|---|---:|---:|
| `left_spinor_electron_ideal` | 2 | True |
| `left_spinor_muon_motif` | 2 | True |
| `left_spinor_tau_motif` | 2 | True |
| `right_spinor_electron_ideal` | 2 | True |
| `vector_proton_proto_t124` | 2 | True |

## Selected Cases

### left_spinor_electron_ideal
- `E1_center_kick` op=`1` N=`2` dx=`1` speed=`0.5` lock=`9` confirm=`11`
- `E2_center_plus_shell1` op=`1` N=`2` dx=`1` speed=`0.5` lock=`9` confirm=`11`

### left_spinor_muon_motif
- `E1_center_kick` op=`1` N=`2` dx=`1` speed=`0.5` lock=`9` confirm=`11`
- `E2_center_plus_shell1` op=`1` N=`2` dx=`1` speed=`0.5` lock=`9` confirm=`11`

### left_spinor_tau_motif
- `E1_center_kick` op=`2` N=`2` dx=`1` speed=`0.5` lock=`9` confirm=`11`
- `E2_center_plus_shell1` op=`1` N=`2` dx=`1` speed=`0.5` lock=`9` confirm=`11`

### right_spinor_electron_ideal
- `E1_center_kick` op=`1` N=`2` dx=`1` speed=`0.5` lock=`9` confirm=`11`
- `E2_center_plus_shell1` op=`1` N=`2` dx=`1` speed=`0.5` lock=`9` confirm=`11`

### vector_proton_proto_t124
- `E2_center_plus_shell1` op=`1` N=`2` dx=`1` speed=`0.5` lock=`9` confirm=`11`
- `E3_center_plus_shell2` op=`1` N=`2` dx=`1` speed=`0.5` lock=`9` confirm=`11`

## Checks

- all_particles_have_at_least_two_energy_cases: `True`
- particle_count_processed: `5`
