# Python_code

For full worker onboarding and execution workflow, read:
1. `world_code/WORKER_ZERO_TO_EXPERT_SIMULATION_RUNBOOK.md`

`minimal_world_kernel.py` is the smallest executable kernel in this repo for:

1. loading a full predetermined lightcone microstate,
2. running deterministic `C x O` updates,
3. writing resulting microstate.

## Input format

See `lightcone_example.json`. Required keys:

1. `node_ids`: list of node ids,
2. `parents`: map `node_id -> list[parent_node_id]`,
3. `init_state`: map `node_id -> 8 coefficients`, each coefficient `[re, im]`.

Canonical numeric rule:

1. `init_state` coefficients must be JSON integer literals (`1`, `0`, `-3`), not floats (`1.0`).
2. This keeps CxO microstates unambiguously integer-valued.

## Run

```bash
python world_code/Python_code/minimal_world_kernel.py \
  --input world_code/Python_code/lightcone_example.json \
  --steps 4 \
  --output world_code/Python_code/out.json
```

## Example Library

See:

1. `world_code/Python_code/lightcone_microstate_examples/README.md`
2. `world_code/Python_code/lightcone_microstate_examples/examples_index.json`

## Campaign Runner (for autonomous lab)

Run the baseline sweep:

```bash
python world_code/Python_code/run_world_code_campaign.py \
  --config world_code/Python_code/campaign_configs/baseline_scan.json
```

Outputs are saved under:
1. `world_code/Python_code/results/<campaign_id>/manifest.json`
2. `world_code/Python_code/results/<campaign_id>/campaign_summary.json`
3. `world_code/Python_code/results/<campaign_id>/<example>/step_XXXX.json`
