# Particle Motifs Exact Patterns (v1)

- motif_count: `29`
- op_bitswitch_label: `e111`
- replay_hash: `c711777f21581cb3ae583e42c40db9e7e62806555af7deba49f5fcfc8afa4413`
- all_steps_match_bitswitch_rule_left: `True`
- all_steps_match_bitswitch_rule_right: `True`
- all_periods_equal_4: `True`

## Particle-Candidate IDs
- `left_spinor_electron_ideal`
- `left_spinor_muon_motif`
- `left_spinor_tau_motif`
- `right_spinor_electron_ideal`
- `sd_triple_dual_electron`
- `sd_vacuum_omega_dag`
- `su_triple_electron`
- `su_vacuum_omega`
- `vector_electron_favored`
- `vector_proton_proto_t124`

## Motif Summary
| Motif ID | Family | Left Period | Right Period | Support |
|---|---:|---:|---:|---|
| `left_spinor_electron_ideal` | `particle_alias_left` | `4` | `4` | `['e000', 'e111']` |
| `left_spinor_muon_motif` | `particle_alias_left` | `4` | `4` | `['e011', 'e100']` |
| `left_spinor_tau_motif` | `particle_alias_left` | `4` | `4` | `['e001', 'e110']` |
| `right_spinor_electron_ideal` | `particle_alias_right` | `4` | `4` | `['e000', 'e111']` |
| `sd_double_12` | `spinor_Sd` | `4` | `4` | `['e011', 'e100']` |
| `sd_double_13` | `spinor_Sd` | `4` | `4` | `['e010', 'e101']` |
| `sd_double_23` | `spinor_Sd` | `4` | `4` | `['e001', 'e110']` |
| `sd_single_1` | `spinor_Sd` | `4` | `4` | `['e001', 'e110']` |
| `sd_single_2` | `spinor_Sd` | `4` | `4` | `['e010', 'e101']` |
| `sd_single_3` | `spinor_Sd` | `4` | `4` | `['e011', 'e100']` |
| `sd_triple_dual_electron` | `spinor_Sd` | `4` | `4` | `['e000', 'e111']` |
| `sd_vacuum_omega_dag` | `spinor_Sd` | `4` | `4` | `['e000', 'e111']` |
| `su_double_12` | `spinor_Su` | `4` | `4` | `['e011', 'e100']` |
| `su_double_13` | `spinor_Su` | `4` | `4` | `['e010', 'e101']` |
| `su_double_23` | `spinor_Su` | `4` | `4` | `['e001', 'e110']` |
| `su_single_1` | `spinor_Su` | `4` | `4` | `['e001', 'e110']` |
| `su_single_2` | `spinor_Su` | `4` | `4` | `['e010', 'e101']` |
| `su_single_3` | `spinor_Su` | `4` | `4` | `['e011', 'e100']` |
| `su_triple_electron` | `spinor_Su` | `4` | `4` | `['e000', 'e111']` |
| `su_vacuum_omega` | `spinor_Su` | `4` | `4` | `['e000', 'e111']` |
| `vector_electron_favored` | `vector` | `4` | `4` | `['e001', 'e010', 'e011']` |
| `vector_fano_line_l1` | `vector` | `4` | `4` | `['e001', 'e010', 'e011']` |
| `vector_fano_line_l2` | `vector` | `4` | `4` | `['e001', 'e100', 'e101']` |
| `vector_fano_line_l3` | `vector` | `4` | `4` | `['e001', 'e110', 'e111']` |
| `vector_fano_line_l4` | `vector` | `4` | `4` | `['e010', 'e100', 'e110']` |
| `vector_fano_line_l5` | `vector` | `4` | `4` | `['e010', 'e101', 'e111']` |
| `vector_fano_line_l6` | `vector` | `4` | `4` | `['e011', 'e100', 'e111']` |
| `vector_fano_line_l7` | `vector` | `4` | `4` | `['e011', 'e101', 'e110']` |
| `vector_proton_proto_t124` | `vector` | `4` | `4` | `['e001', 'e010', 'e100']` |

Full exact cycle states and per-step XOR/sign bit-switch decomposition are in JSON under:
1. `motifs[*].left_cycle.tick_rows` / `step_rows`
2. `motifs[*].right_cycle.tick_rows` / `step_rows`
