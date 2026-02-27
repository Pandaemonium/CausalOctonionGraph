# Worker Zero-to-Expert Simulation Runbook

Status: Active  
Audience: Worker models and human contributors running world_code simulations  
Scope: Operational execution, not final physical interpretation

---

## 1. Why This Exists

This document is the one-stop orientation for workers with zero context.
If you follow this exactly, you can:
1. understand the model at an operational level,
2. prepare canonical lightcone microstates,
3. run deterministic simulations,
4. save reproducible artifacts for downstream constant analysis.

---

## 2. Core Mental Model (Fast, Accurate)

The simulation is intentionally minimal:
1. input a full predetermined lightcone microstate,
2. apply one deterministic local update rule repeatedly,
3. save resulting microstates.

What this means in practice:
1. The kernel does not contain observables.
2. The kernel does not contain fitting knobs.
3. Interpretation happens later in separate analysis layers.

Think of the kernel as:
1. a pure state transition engine over `C x O` states,
2. with fixed algebraic multiplication rules,
3. and strict replay determinism.

---

## 3. What Is Actually Represented

Each node stores a `C x O` state with 8 octonion basis slots.
Each slot is a Gaussian integer pair `[re, im]`.

So each node state is:
1. 8 basis coefficients,
2. each coefficient is two integers,
3. total 16 integer scalars per node.

Canonical numeric rule:
1. use integer literals only (`1`, `0`, `-3`),
2. do not use float literals (`1.0`) in `init_state`.

This is enforced by:
1. `world_code/Python_code/minimal_world_kernel.py`

---

## 4. Model Anchors You Must Treat as Locked

Before running anything, internalize these anchors:
1. `rfc/CONVENTIONS.md`
2. `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
3. `rfc/RFC-067_Objective_Time_as_Graph_Depth.md`
4. `rfc/RFC-070_Left_Handed_vs_Right_Handed_Interaction_Contract.md`
5. `world_code/Lean_code/MinimalWorldKernel.lean`
6. `world_code/Python_code/minimal_world_kernel.py`

Do not silently replace conventions, Fano orientation, or update semantics.

---

## 5. Time, Depth, and Tick (Operationally)

Use these terms correctly:
1. `topoDepth`: graph depth from causal ancestry (objective ordering).
2. `tick`: number of kernel step applications performed in a run.

In kernel output:
1. `tick` is explicit in output JSON,
2. `topoDepth` is derivable from parent links.

---

## 6. Lightcone Input Contract (Non-Negotiable)

Simulation input JSON must include:
1. `node_ids`: list of all included nodes in the chosen horizon,
2. `parents`: parent list for every included node,
3. `init_state`: initial `C x O` state for every node id.

Minimal shape:

```json
{
  "node_ids": ["n0", "n1"],
  "parents": {
    "n0": [],
    "n1": ["n0"]
  },
  "init_state": {
    "n0": [[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[1,0]],
    "n1": [[1,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
  }
}
```

Validation checklist:
1. every `node_id` appears in `parents`,
2. every `node_id` appears in `init_state`,
3. each state has exactly 8 pairs,
4. each pair is exactly 2 integer literals,
5. parent node ids exist in `node_ids`.

---

## 7. Worker Workflow: From Idea to Saved Results

## 7.1 Step A - Choose or prepare input

Option 1 (recommended first):
1. pick an existing example from:
   - `world_code/Python_code/lightcone_microstate_examples/`

Option 2:
1. copy `world_code/Python_code/lightcone_example.json`,
2. edit into a new file under:
   - `world_code/Python_code/lightcone_microstate_examples/<your_name>.json`

## 7.2 Step B - Preflight parse check

Run with `--steps 0` to validate schema and integer coefficients:

```bash
python world_code/Python_code/minimal_world_kernel.py \
  --input world_code/Python_code/lightcone_microstate_examples/<file>.json \
  --steps 0 \
  --output world_code/Python_code/results/_tmp_validate.json
```

If parse fails, fix input first. Do not continue with invalid input.

## 7.3 Step C - Run deterministic evolution

```bash
python world_code/Python_code/minimal_world_kernel.py \
  --input world_code/Python_code/lightcone_microstate_examples/<file>.json \
  --steps <N> \
  --output world_code/Python_code/results/<run_id>/step_<N>.json
```

Recommended first step grid:
1. `N = 0, 1, 2, 4, 8`

## 7.4 Step D - Save a reproducible run package

Create:
1. `world_code/Python_code/results/manual_runs/<run_id>/`

Required files in that folder:
1. `input.json` (exact input used),
2. `step_0000.json`, `step_0001.json`, ... (selected checkpoints),
3. `run_manifest.json`,
4. `run_notes.md`.

`run_manifest.json` minimum fields:
1. `run_id`
2. `timestamp_utc`
3. `kernel_path`
4. `kernel_commit`
5. `input_file`
6. `steps`
7. `commands`
8. `output_files`

---

## 8. Standard Commands Workers Should Use

## 8.1 Single run

```bash
python world_code/Python_code/minimal_world_kernel.py \
  --input world_code/Python_code/lightcone_microstate_examples/020_two_electrons_small_cone.json \
  --steps 8 \
  --output world_code/Python_code/results/manual_runs/e2e2_demo/step_0008.json
```

## 8.2 Campaign run (batch over many examples)

```bash
python world_code/Python_code/run_world_code_campaign.py \
  --config world_code/Python_code/campaign_configs/baseline_scan.json
```

Campaign outputs are stored under:
1. `world_code/Python_code/results/<campaign_id>/manifest.json`
2. `world_code/Python_code/results/<campaign_id>/campaign_summary.json`
3. per-example step files and summary.

---

## 9. Quality Bar for Worker Deliverables

A worker output is acceptable only if it includes:
1. exact input file path,
2. exact commands run,
3. exit status for each command,
4. exact output file paths,
5. short note on what changed vs baseline.

Not acceptable:
1. claims without output files,
2. summaries without commands,
3. interpretation without reproducible artifacts.

---

## 10. Common Failure Modes and Fixes

1. Float coefficients in `init_state`:
- Symptom: parse error for integer literal requirement.
- Fix: replace `1.0` with `1` everywhere in `init_state`.

2. Missing node in `init_state`:
- Symptom: kernel raises missing entry error.
- Fix: ensure every `node_id` has an 8-slot state.

3. Invalid coefficient shape:
- Symptom: "Each coefficient must be [re, im]".
- Fix: use exactly two integers per basis slot.

4. Non-reproducible run folder:
- Symptom: cannot replay later.
- Fix: always include `run_manifest.json` + command list + input copy.

---

## 11. What Workers Should Not Do

1. Do not edit locked conventions to force a desired result.
2. Do not add observables inside the minimal kernel.
3. Do not reinterpret failed runs as success.
4. Do not promote claim status directly from single-run intuition.

Workers produce reproducible state artifacts.
Research Director and skeptic layers decide constant claims.

---

## 12. Hand-off Contract (Worker -> Director/Skeptic)

When complete, provide this block in your final message:
1. `RUN_ID`
2. `INPUT_FILE`
3. `STEPS`
4. `COMMANDS_EXECUTED`
5. `OUTPUT_FILES`
6. `EXIT_CODES`
7. `KNOWN_LIMITS`

If any item is missing, the run is incomplete.

---

## 13. Immediate Starter Task (for new workers)

Do this exact exercise first:
1. run `020_two_electrons_small_cone.json` at steps `0,1,2,4,8`,
2. save all outputs under one manual run folder,
3. write a clean `run_manifest.json`,
4. hand off artifacts without interpretation.

This proves you can operate the pipeline correctly before larger campaigns.
