# Constant Factory Playbook

Status: Active Draft  
Owner: Research Director  
Audience: Research Director, Lab Manager, Skeptic, Worker agents  
Depends on:
- `rfc/RFC-069_Canonical_Simulation_Artifact_Contract.md`
- `rfc/RFC-050_Proof_State_and_Claim_Status_Matrix.md`
- `rfc/RFC-067_Objective_Time_as_Graph_Depth.md`
- `rfc/RFC-070_Left_Handed_vs_Right_Handed_Interaction_Contract.md`
- `world_code/Lean_code/MinimalWorldKernel.lean`
- `world_code/Python_code/minimal_world_kernel.py`

---

## 1. Purpose

This playbook defines how to derive as many fundamental constants as possible while preserving scientific credibility and priority.

Priority is earned by:
1. reproducible artifacts,
2. timestamped preregistered protocols,
3. independent skeptical review,
4. fast publication of bounded claims.

---

## 2. Operating Rule

For every constant, execute the same pipeline:
1. define observable,
2. preregister protocol,
3. run canonical simulations,
4. perform skeptic claim-by-claim dissection,
5. publish artifact bundle and claim status.

No constant claim is promotable without all five stages.

---

## 3. Constant Portfolio Order

Run constants in this order:
1. Algebra-first constants (small cones, structural ratios, minimal runtime risk).
2. Running constants with medium cones (requires scale sweep).
3. Many-body constants (large cones, high compute).

Initial queue recommendation:
1. Weinberg angle UV + running protocol closure.
2. Fine-structure constant running protocol.
3. Strong coupling running protocol.
4. Lepton generation mass ratios.

---

## 4. Freeze Policy

Use sprint-level freezes to prevent moving targets:
1. Freeze kernel semantics for one sprint (no update-rule changes).
2. Freeze conventions for one sprint (`rfc/CONVENTIONS.md`).
3. Freeze observable definition per constant before execution.

Allowed during freeze:
1. bug fixes that do not change semantics,
2. test harness improvements,
3. performance optimization preserving bit-for-bit outputs.

---

## 5. Artifact Contract (Per Constant)

Create one folder per constant campaign:
`artifacts/constants/<CONST-ID>/<YYYYMMDD_run_id>/`

Required files:
1. `constant_definition.md`  
Exact mathematical definition of the measured quantity and units.
2. `preregistered_protocol.md`  
Inputs, schedule, horizons, steps, decision thresholds, falsification criteria.
3. `input_manifest.json`  
All input microstate files and SHA256 hashes.
4. `run_commands.sh` (or `.ps1`)  
Exact commands used to run.
5. `run_log.json`  
Machine info, commit hash, start/end UTC, command exit codes.
6. `raw_outputs/`  
Unmodified simulation outputs.
7. `reduction_script.py`  
Deterministic reducer from raw outputs to candidate constant.
8. `reduction_output.json`  
Reduced result with confidence envelope and diagnostics.
9. `skeptic_full_report.md`  
Mandatory claim-by-claim skeptic report.
10. `claim_update_patch.diff`  
Patch showing claim YAML transition proposal.

No file, no promotion.

---

## 6. Promotion Gate

A constant result can move to `proved` only if:
1. preregistered protocol exists and is timestamped before run,
2. all required artifacts exist and validate,
3. rerun by a second model or operator reproduces result,
4. skeptic decision is `PASS` or `PASS_WITH_LIMITS` with explicit limits,
5. limits are reflected in claim YAML notes.

`FAIL` or `MIXED` always creates follow-up tasks and blocks promotion.

---

## 7. Skeptic Standard (Non-Optional)

Skeptic must provide:
1. claim restatement,
2. formalization,
3. model-fit comparison against truth anchors,
4. claim verdict matrix,
5. salvage list,
6. defects with minimal reproducer,
7. follow-up tasks.

Use canonical anchors:
1. `rfc/CONVENTIONS.md`
2. `rfc/RFC-028_Canonical_Update_Rule_Closure.md`
3. `rfc/RFC-067_Objective_Time_as_Graph_Depth.md`
4. `rfc/RFC-070_Left_Handed_vs_Right_Handed_Interaction_Contract.md`
5. `world_code/Lean_code/MinimalWorldKernel.lean`
6. `world_code/Python_code/minimal_world_kernel.py`

---

## 8. Daily Cadence (Throughput Mode)

Daily cycle:
1. 00:00-00:30 UTC: queue grooming and protocol preregistration.
2. 00:30-08:00 UTC: simulation execution and artifact capture.
3. 08:00-10:00 UTC: skeptic analysis and follow-up creation.
4. 10:00-11:00 UTC: claim-gate review and publication packaging.

Daily outputs:
1. at least one completed constant bundle,
2. one skeptic-approved or skeptic-limited claim decision,
3. one public ledger update.

---

## 9. Anti-Scoop Priority Protocol

To secure priority without overclaiming:
1. tag releases daily (`constant-factory-YYYYMMDD`),
2. publish hash-signed bundles to immutable storage,
3. submit concise technical notes for each major milestone,
4. separate proven claims from conjectures in all public text.

Priority comes from timestamped reproducibility, not marketing velocity.

---

## 10. Reusable Task Template

Use this when assigning workers:

1. Objective:
- Derive `<CONST-ID>` using preregistered protocol `<path>`.

2. Must-read files:
- protocol file
- kernel files
- reduction script
- claim YAML

3. Required commands:
- build command
- simulation command set
- reduction command
- verification command

4. Done condition:
- artifact contract complete,
- skeptic report generated,
- claim update patch prepared,
- no semantic kernel drift.

---

## 11. Minimum Viable Automation

Automate these checks first:
1. artifact completeness checker,
2. hash integrity checker,
3. protocol timestamp check (`protocol_time < run_start_time`),
4. rerun reproducibility checker,
5. skeptic report schema checker.

These five checks should block claim promotion on failure.

---

## 12. First 7-Day Sprint Plan

Day 1:
1. freeze kernel semantics,
2. finalize constant queue and owners.

Day 2-3:
1. run first two constants end-to-end with full artifact bundles.

Day 4:
1. skeptic deep review and repair pass.

Day 5:
1. rerun reproducibility pass and claim proposals.

Day 6:
1. public evidence ledger update with bounded claims.

Day 7:
1. retrospective,
2. update queue,
3. start next sprint.

---

## 13. Bottom Line

This playbook is optimized for:
1. speed with discipline,
2. priority with rigor,
3. maximum value to humanity through reproducible science.
