# v3 Active Hypothesis Board (v1)

Date: 2026-03-03  
Owner: COG Core  
Status: Active (single primary + multi-lane async execution)

## Operating rule

1. Exactly one **primary decision-driving hypothesis** at a time.
2. Up to 6+ **asynchronous supporting lanes** can run in parallel.
3. Promotion uses hard gates; no promotion from single quick runs.

## Primary Hypothesis (H-P1)

`H-P1`: In S2880, there exists a mesophase window (`D -> M`) where:
1. `R3 >= 2.0` (provisional) and target lane `R3 >= 4.0`,
2. Kuramoto `r_mean` enters mesophase band with nontrivial oscillation (`r_std > 0`),
3. spectral entropy decreases versus disordered baseline,
4. this unlocks downstream neutrino/photon/electron motif search.

Decision impact:
1. If true: prioritize motif discovery in Phase M.
2. If false: redesign kernel family before motif campaign.

Contract anchor:
1. `cog_v3/rfc/RFC-017_Phase_Boundary_and_Ordered_Phase_Detection_Contract.md`
2. `cog_v3/rfc/RFC-018_Gate2_Gate4_C12_Integration_Unlock_Contract.md`

## Primary lane tasks (must-complete)

1. Implement and run: `build_v3_phase_boundary_kernel_sweep_v1.py`
2. Measure `w3_crit` (or falsify in tested range).
3. Classify each sweep point as `D`, `M`, or `O`.
4. Emit canonical artifacts:
   - `cog_v3/sources/v3_phase_boundary_sweep_v1.json`
   - `cog_v3/sources/v3_phase_boundary_sweep_v1.csv`
   - `cog_v3/sources/v3_phase_boundary_sweep_v1.md`

Kill criteria:
1. No mesophase evidence (`R3 < 2`) for all tested `w3 <= 32` and control settings.
2. Metrics are unstable across seeds with no coherent trend.

## Asynchronous Supporting Lanes

### Lane S1 (Neutrino-first search prep)

Goal:
1. Define Phase-M-only neutrino candidate filters (`gate5b` oscillatory + low-drag transport).
2. Build ranking panel for Gen1/Gen2/Gen3 neutrino motifs.

Status:
1. Blocked until first Phase-M window is measured.

### Lane S2 (Photon directional unlock)

Goal:
1. Move `detector_exclusivity` above zero.
2. Compare sheet vs blob3 vs single-cell seeds under S2880 lanes.

Status:
1. Running precursor jobs; full promotion waits for Phase-M sweep.

### Lane S3 (Electron lane readiness)

Goal:
1. Define electron motif acceptance criteria after neutrino/photon candidate baselines are stable.
2. Freeze electron benchmark manifest (`stationary + excited` classes).

Status:
1. Planning stage.

### Lane S4 (Kernel robustness + ranking)

Goal:
1. Seed-sweep robustness on fixed-manifest gate stack.
2. Track ranking stability (`K0/K1/K2/...`) under seed variation.

Status:
1. Running (`build_v3_fixed_manifest_kernel_gate_stack_seed_sweep_v1.py`).

### Lane S5 (Algebraic structure probes)

Goal:
1. RFC-013 action-family refinement toward faithful 168-action.
2. RFC-012 associator field evidence tightening.

Status:
1. First-pass artifacts complete; refinement active.

### Lane S6 (Lit/RFC/manuscript prep)

Goal:
1. Keep contracts synchronized with evidence.
2. Build publication-ready chain:
   - kernel + phase diagram,
   - motif discovery evidence,
   - divergence predictions.

Status:
1. Active with Codex/Claude collaboration messages.

## Current running long jobs (snapshot)

1. `run_v3_overnight_autonomous_v1` (continuous background).
2. `build_v3_generation_aligned_equivalence_panel_v1 --global-seed 1337`.
3. `build_v3_bundle12_seed_vs_random_ablation_v1` (heavy).
4. `build_v3_bundle_seed_vs_random_ablation_v1 --seed-budget 5000`.
5. `build_v3_fixed_manifest_kernel_gate_stack_seed_sweep_v1 --seed-count 64 --quick`.

## Tactical policy

1. Use daytime for short diagnostics and contract updates.
2. Use background/overnight for heavy sweeps and ablations.
3. Do not pause all side lanes; keep throughput high.
4. Primary lane still has right-of-way for compute decisions.

