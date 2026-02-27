# XOR Perturbation-to-Attractor Matrix

Status: active scaffold artifact  
Primary code: `calc/xor_perturbation_attractor_matrix.py`  
Build script: `scripts/build_xor_perturbation_attractor_matrix.py`

## Scope
1. Start from canonical vector/spinor motif seeds.
2. Apply one-step perturbations (`left_hit_e1..e7`, `right_hit_e1..e7`).
3. Evolve under fixed policy (`vacuum_pass_e7_left`).
4. Detect cycle attractors and build source->attractor transition matrix.
5. Compute retention statistics (fraction that return to source attractor class).

## Artifacts
1. `calc/xor_perturbation_attractor_matrix.json`
2. `calc/xor_perturbation_attractor_matrix.csv`
3. `website/data/xor_perturbation_attractor_matrix.json`
4. `website/data/xor_perturbation_attractor_matrix.csv`

## Not Claimed
1. This matrix is a structural dynamical map, not direct scattering cross-sections.
2. No continuum force law or SI calibration is included.
3. Attractor IDs are model-internal canonical representatives.

## Extension Clues
1. Add perturbation amplitude families (not only single basis hits).
2. Add alternative evolution policies and compare matrices.
3. Add basin-size estimation from random perturbation ensembles.
4. Add public visualization by motif family and retention fraction.

