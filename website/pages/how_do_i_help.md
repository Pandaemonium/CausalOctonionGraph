# How Do I Help?

You can directly help COG by running deterministic world-code simulations and sharing outputs.

This page gives the shortest path to:
1. download `Python_code` and/or `Lean_code`,
2. generate canonical full-lightcone microstates,
3. run the simulation kernel,
4. keep outputs in a reusable format.

---

## Quick Start

Repository:
- `https://github.com/Pandaemonium/CausalOctonionGraph`

Clone:

```bash
git clone https://github.com/Pandaemonium/CausalOctonionGraph.git
cd CausalOctonionGraph
```

---

## Option A: Run Python World Code

Primary executable:
- `world_code/Python_code/minimal_world_kernel.py`

Run a known example:

```bash
python world_code/Python_code/minimal_world_kernel.py \
  --input world_code/Python_code/lightcone_example.json \
  --steps 4 \
  --output world_code/Python_code/out.json
```

Run a library example:

```bash
python world_code/Python_code/minimal_world_kernel.py \
  --input world_code/Python_code/lightcone_microstate_examples/020_two_electrons_small_cone.json \
  --steps 8 \
  --output world_code/Python_code/results/manual_two_electrons_step8.json
```

---

## Option B: Use the Lean World Code Contract

Formal kernel contract:
- `world_code/Lean_code/MinimalWorldKernel.lean`

Build:

```bash
lake build
```

Lean world code is the formal reference for deterministic evolution semantics.
Python world code is the executable runner for concrete campaigns.

---

## Generate Canonical Full-Lightcone Microstates

Canonical policy for simulation input:
1. include all nodes in the chosen lightcone horizon,
2. include all parent links for every included node,
3. include `init_state` for every node id listed,
4. use integer Gaussian coefficients `[re, im]` in all 8 CxO basis slots.

Input format:

```json
{
  "node_ids": ["n0", "n1"],
  "parents": {
    "n0": [],
    "n1": ["n0"]
  },
  "init_state": {
    "n0": [[0, 0],[0, 0],[0, 0],[0, 0],[0, 0],[0, 0],[0, 0],[1, 0]],
    "n1": [[1, 0],[0, 0],[0, 0],[0, 0],[0, 0],[0, 0],[0, 0],[0, 0]]
  }
}
```

Practical workflow:
1. start from `world_code/Python_code/lightcone_microstate_examples/`,
2. duplicate the closest example,
3. modify `node_ids`, `parents`, and `init_state`,
4. run with `--steps 0` first to validate structure,
5. run your full step schedule.

Validation run:

```bash
python world_code/Python_code/minimal_world_kernel.py \
  --input world_code/Python_code/lightcone_microstate_examples/000_vacuum_single_node.json \
  --steps 0 \
  --output world_code/Python_code/results/validation_step0.json
```

---

## Run Multi-Example Campaigns

Campaign runner:
- `world_code/Python_code/run_world_code_campaign.py`

Baseline campaign:

```bash
python world_code/Python_code/run_world_code_campaign.py \
  --config world_code/Python_code/campaign_configs/baseline_scan.json
```

Outputs are written under:
- `world_code/Python_code/results/<campaign_id>/manifest.json`
- `world_code/Python_code/results/<campaign_id>/campaign_summary.json`
- `world_code/Python_code/results/<campaign_id>/<example>/step_XXXX.json`

---

## What To Save

For every run, keep:
1. input microstate JSON,
2. command used (`input`, `steps`, `output`),
3. output JSON,
4. any derived analysis script and summary.

This makes your run reproducible and useful for later extraction of constants and observables.

---

## Reporting Results

Open a GitHub issue in the repository with the label **`results`**:

```
https://github.com/Pandaemonium/CausalOctonionGraph/issues/new?labels=results
```

Attach or paste:
1. your input microstate JSON,
2. the command you ran (input path, steps, output path),
3. your output JSON (or a link to it),
4. any derived analysis or summary you produced.

We review all `results`-labelled issues. Interesting or unexpected outputs are prioritised for integration into the formal claim pipeline.
