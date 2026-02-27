# Python_code

For full worker onboarding and execution workflow, read:
1. `world_code/WORKER_ZERO_TO_EXPERT_SIMULATION_RUNBOOK.md`

`minimal_world_kernel.py` is the smallest executable kernel in this repo for:

1. loading a full predetermined lightcone microstate,
2. running deterministic `C x O` updates,
3. writing resulting microstate.

Experimental alternate profile:
1. `minimal_world_kernel_unity.py` runs the same update skeleton but projects coefficients to `{0,+1,-1,+i,-i}`.
2. It is exploratory and non-canonical for claim promotion.
3. `minimal_world_kernel_preregistered_unity.py` adds explicit preregistered event ordering via `eval_plan`:
   - `round_order` (node update order),
   - `parent_order` (message fold order per node),
   - `projection_policy` (projector checkpoint policy).

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

Preregistered unity run:

```bash
python world_code/Python_code/minimal_world_kernel_preregistered_unity.py \
  --input world_code/Python_code/lightcone_example_preregistered_unity.json \
  --steps 4 \
  --output world_code/Python_code/out_preregistered_unity.json
```

## Interactive Visualizer

Use the local GUI to:
1. inspect full node states (`e0_re, e0_im, ..., e7_re, e7_im`),
2. view the full graph (all nodes + parent edges),
3. hover a node to highlight its past/future lightcone,
4. view lightcone metrics across cached tick history,
5. step forward/backward one tick at a time.

```bash
python world_code/Python_code/lightcone_state_visualizer.py
```

With preloaded input:

```bash
python world_code/Python_code/lightcone_state_visualizer.py \
  --input world_code/Python_code/lightcone_microstate_examples/020_two_electrons_small_cone.json
```

Supports loading both:
1. simulation input JSONs (`init_state`),
2. saved output JSONs (`state` + `tick`).

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

## Fine-Structure Case Generator (Cold vs Warm Start)

`generate_fine_structure_20_cases.py` supports two initialization modes:
1. Cold start: electrons are seeded and measurement begins immediately.
2. Warm start: run deterministic preconditioning ticks first, then measure.

It also supports two kernel profiles:
1. `integer` (canonical),
2. `unity` (exploratory projection profile).

Dry-run safety is enabled by default; pass `--execute` to run.

Quick smoke run:

```bash
python world_code/Python_code/generate_fine_structure_20_cases.py \
  --execute \
  --case-limit 1 \
  --max-steps 2 \
  --preconditioning-ticks 1 \
  --include-cold-baseline \
  --output-dir world_code/Python_code/results/fine_structure_20_cases_smoke
```

Larger local run:

```bash
python world_code/Python_code/generate_fine_structure_20_cases.py \
  --execute \
  --kernel-profile unity \
  --preconditioning-ticks 12 \
  --include-cold-baseline \
  --output-dir world_code/Python_code/results/fine_structure_20_cases
```

Key output files:
1. `fine_structure_20_cases.json` (full per-case telemetry + summary deltas),
2. `fine_structure_20_cases.csv` (row-wise per-tick stage data).

## Preregistered Unity Pathway Validation

Front-to-back validation (schema + replay + unity closure):

```bash
python world_code/Python_code/validate_preregistered_unity_pathway.py \
  --input world_code/Python_code/lightcone_example_preregistered_unity.json \
  --steps 4
```
