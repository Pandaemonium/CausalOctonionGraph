# Particle Excited Propagation Cycle Library (v2)

## Params

- ticks: `48`
- size_xyz: `7`
- burn_in_ticks: `0`
- period range: `2..20`
- kick_ops: `[1, 2, 3, 4, 5, 6, 7]`
- fold_order_variants: `['canonical_xyz', 'reverse_xyz', 'axis_cycle_yzx', 'plus_first']`

## Particle Summary

| particle_id | selected_case_count | has_two_cases | has_two_energy_cases |
|---|---:|---:|---:|
| `left_spinor_electron_ideal` | 0 | False | False |
| `left_spinor_muon_motif` | 2 | True | False |
| `left_spinor_tau_motif` | 1 | False | False |
| `right_spinor_electron_ideal` | 2 | True | True |
| `vector_proton_proto_t124` | 2 | True | False |

## Selected Cases

### left_spinor_electron_ideal
- no robust nontrivial RPO case found

### left_spinor_muon_motif
- `E1_center_kick` op=`3` N=`14` dx=`0` speed=`0.0` lock=`9` confirm=`23` min_nonvac_nz=`343`
- `E1_center_kick` op=`4` N=`7` dx=`0` speed=`0.0` lock=`9` confirm=`16` min_nonvac_nz=`343`

### left_spinor_tau_motif
- `E1_center_kick` op=`1` N=`14` dx=`0` speed=`0.0` lock=`9` confirm=`23` min_nonvac_nz=`343`

### right_spinor_electron_ideal
- `E2_center_plus_shell1` op=`7` N=`14` dx=`0` speed=`0.0` lock=`9` confirm=`23` min_nonvac_nz=`343`
- `E3_center_plus_shell2` op=`7` N=`14` dx=`0` speed=`0.0` lock=`8` confirm=`22` min_nonvac_nz=`343`

### vector_proton_proto_t124
- `E1_center_kick` op=`3` N=`14` dx=`0` speed=`0.0` lock=`1` confirm=`15` min_nonvac_nz=`21`
- `E1_center_kick` op=`5` N=`14` dx=`0` speed=`0.0` lock=`1` confirm=`15` min_nonvac_nz=`21`

## Checks

- all_particles_have_at_least_two_cases: `False`
- all_particles_have_at_least_two_energy_cases: `False`
- particle_count_processed: `5`
