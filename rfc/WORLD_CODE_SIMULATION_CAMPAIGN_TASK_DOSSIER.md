# WORLD_CODE Simulation Campaign Task Dossier

Status: Active
Owner: Research Director
Purpose: Drive autonomous workers to generate reusable raw-state artifacts from the minimal kernel.

---

## Task A - Baseline Campaign Sweep

### Goal
Run deterministic sweeps over the full `world_code` example set and save all outputs.

### Files to use
1. `world_code/Python_code/run_world_code_campaign.py`
2. `world_code/Python_code/campaign_configs/baseline_scan.json`
3. `world_code/Python_code/minimal_world_kernel.py`
4. `world_code/Python_code/lightcone_microstate_examples/*.json`

### Command
```bash
python world_code/Python_code/run_world_code_campaign.py \
  --config world_code/Python_code/campaign_configs/baseline_scan.json
```

### Success criteria
1. `world_code/Python_code/results/baseline_scan_v1/manifest.json` exists.
2. `world_code/Python_code/results/baseline_scan_v1/campaign_summary.json` exists.
3. Every example listed in config has a folder with `summary.json` and all `step_XXXX.json` files.

---

## Task B - Edge-Distance Scale Sweep (electron-electron)

### Goal
Generate multiple distance-initialization scenarios and run the same deterministic sweep.

### Files to use
1. `world_code/Python_code/lightcone_microstate_examples/020_two_electrons_small_cone.json`
2. `world_code/Python_code/lightcone_microstate_examples/060_distance_chain_electron_electron.json`
3. `world_code/Python_code/run_world_code_campaign.py`

### Required output
1. New campaign config under `world_code/Python_code/campaign_configs/`
2. New result folder under `world_code/Python_code/results/`
3. Short report file: `sources/world_code_distance_sweep_report.md`

### Success criteria
1. At least 3 distinct edge-separation setups are included.
2. Output metrics include `max_depth`, `edge_count`, and axis weights.

---

## Task C - Axis-Weight Scan (e0/e7 sensitivity)

### Goal
Produce controlled variants of selected examples to test sensitivity of:
1. `e0` axis weight,
2. `e7` axis weight,
3. `e0/e7` ratio trajectory.

### Files to use
1. `world_code/Python_code/lightcone_microstate_examples/050_photon_like_e7_pulse.json`
2. `world_code/Python_code/lightcone_microstate_examples/051_phase_shifted_electron.json`
3. `world_code/Python_code/run_world_code_campaign.py`

### Required output
1. New example files under `world_code/Python_code/lightcone_microstate_examples/`
2. New campaign config + result folder
3. Report: `sources/world_code_axis_weight_scan_report.md`

---

## Task D - Skeptic Review (claim-by-claim)

### Goal
Skeptic validates campaign artifacts and decides:
1. PASS
2. PASS_WITH_LIMITS
3. FAIL

### Required review artifact
`lab/orchestrator/data/context_packs/<task_id>/skeptic_claim_review.md`

### Required checks
1. Replay determinism (same config run twice -> identical manifest + output file hashes).
2. No hidden exogenous inputs.
3. Output completeness against config.
4. Salvage section with reusable valid sub-results.

---

## Why this matters

These artifacts are not final constants by themselves. They are the raw deterministic state traces needed to build representation layers for:
1. fine structure extraction,
2. strong coupling extraction,
3. muon/tau mass-drag extraction.

