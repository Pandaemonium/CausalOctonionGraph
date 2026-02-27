# XOR Report Builder

Primary code: `calc/xor_report_builder.py`

## Purpose
1. Convert raw ensemble datasets into concise public-facing summaries.
2. Generate both machine-readable JSON and markdown narrative.

## Key functions
1. `build_ensemble_report(dataset)`
2. `render_markdown_report(report)`
3. `write_xor_report_artifacts(report, ...)`
4. `build_report_from_dataset_path(path)`

## Typical output
1. `calc/xor_ensemble_report.json`
2. `sources/xor_ensemble_report.md`
3. optional mirrored JSON under `website/data/`

