# XCALC-103 Task Prompt — Hydrogen XOR Binding Bridge

Status: Ready to Assign  
Roadmap ID: `XCALC-103`  
Roadmap Source: `rfc/XOR_PHYSICS_CALCULABLES_ROADMAP.md`  
Claim Link: `claims/HYDROGEN-001.yml`

---

## 1. Objective

Bridge existing structural hydrogen scaffold into the XOR motif stack:
1. preserve Gate 1 structural facts,
2. add XOR-cycle diagnostics for electron/proton-proto motifs,
3. emit deterministic artifacts suitable for dashboard and claim notes.

This is still structural; it is not spectroscopic closure.

---

## 2. Locked Inputs

Use existing scaffold constants from:
1. `calc/hydrogen_binding.py`
   - `ELECTRON_MOTIF = {1,2,3}`
   - `PROTON_PROTO_MOTIF = {1,2,4}`

Use canonical Fano cycles from:
1. `calc/conftest.py` / `rfc/CONVENTIONS.md`.

Use XOR update machinery from:
1. `calc/xor_update_rule.py`
2. `calc/xor_vector_spinor_phase_cycles.py` (if needed for shared sequence policy)

---

## 3. Required Deliverables

Create:
1. `calc/xor_hydrogen_binding_scan.py`
2. `calc/test_xor_hydrogen_binding_scan.py`
3. `sources/xor_hydrogen_binding_scan.md`

Generate artifacts:
1. `calc/xor_hydrogen_binding_scan.json`
2. `calc/xor_hydrogen_binding_scan.csv`
3. `website/data/xor_hydrogen_binding_scan.json`
4. `website/data/xor_hydrogen_binding_scan.csv`

Optional helper:
1. `scripts/build_xor_hydrogen_binding_scan.py`

---

## 4. Required Computations

## 4.1 Structural section

Compute and store:
1. motif overlap count,
2. shared pair,
3. unique line through shared pair,
4. binding proxy (`Fraction`) from shared-line count.

Expected baseline:
1. shared pair `{1,2}`,
2. line through pair `{1,2,3}`,
3. binding proxy positive.

## 4.2 XOR dynamic section

For electron motif and proton-proto motif, run same operator sequences:
1. `vacuum_pass_e7 = [7]`,
2. `interaction_pass_123 = [1,2,3]`.

For each motif and each hand (`left`, `right`), report:
1. cycle found or not,
2. cycle start,
3. period,
4. support trajectory summaries.

## 4.3 Coupled section (minimal)

Run one deterministic coupled two-motif round policy:
1. electron as node A,
2. proton-proto as node B.

Report:
1. detected pair period (within horizon),
2. whether period exceeds 4,
3. replay consistency hash.

---

## 5. Required API (`calc/xor_hydrogen_binding_scan.py`)

Implement:
1. `build_hydrogen_structural_summary() -> dict`
2. `build_hydrogen_xor_cycle_summary(max_steps=...) -> dict`
3. `build_hydrogen_coupled_summary(max_steps=...) -> dict`
4. `build_hydrogen_scan_dataset(max_steps=...) -> dict`
5. `write_hydrogen_scan_artifacts(dataset, ...)`
6. `main()`

---

## 6. Test Requirements

Add tests for:
1. structural summary fields and expected shared pair/line.
2. binding proxy type and positivity.
3. dynamic summary exists for both motifs and both hands.
4. coupled summary deterministic on repeated runs.
5. artifact writer produces valid JSON/CSV and required schema keys.

---

## 7. Claim File Touch Policy

`claims/HYDROGEN-001.yml` updates are limited to metadata notes/artifacts only.

Do not:
1. mark Gate 2 or Gate 3 as passed,
2. claim physical hydrogen spectrum closure,
3. claim calibrated binding energy.

Allowed:
1. append artifact references under notes or gate artifact list.

---

## 8. Not Claimed (Required in `sources/xor_hydrogen_binding_scan.md`)

State explicitly:
1. proton-proto motif remains provisional,
2. this scan is structural and discrete-dynamic only,
3. no SI calibration or spectroscopy claim is made.

---

## 9. Verification Commands

Run:
1. `python -m pytest calc/test_xor_hydrogen_binding_scan.py -v`
2. `python -m pytest calc/ -q`
3. `python -m calc.xor_hydrogen_binding_scan`

Success criteria:
1. tests pass,
2. artifacts generated in `calc/` and `website/data/`,
3. outputs are deterministic across re-runs.

