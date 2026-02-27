# XOR Ensemble Runner

Primary code: `calc/xor_ensemble_runner.py`

## Purpose
1. Run many scenario specs as one batch.
2. Attach observables per run.
3. Emit aggregate ensemble metrics and CSV summaries.

## Key functions
1. `run_spec_to_result(spec)`
2. `run_ensemble_specs(specs)`
3. `run_ensemble_from_yaml(path)`
4. `write_xor_ensemble_artifacts(dataset, ...)`

## Typical output
1. `calc/xor_ensemble_results.json`
2. `calc/xor_ensemble_results.csv`
3. mirrored files under `website/data/`

