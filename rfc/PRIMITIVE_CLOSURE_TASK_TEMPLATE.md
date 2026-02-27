# Primitive Closure Task Template (H7 Mode)

Status: Active Template  
Owner: Lab Manager  
Scope: Worker assignment format for primitive-closure packets

---

## 1. Purpose

Use this template when assigning foundational research tasks in H7 primitive mode.
Each task closes exactly one primitive gate and emits one deterministic artifact.

Core object:
`H7 = {e1..e7 with locked Fano incidence + orientation/sign table, e0 identity}`

---

## 2. Allowed Primitive Gate IDs

1. `P-XOR-INDEX`
   - prove/test `out_idx = i xor j` for distinct imaginaries.
2. `P-SIGN-ORIENT`
   - prove/test sign from locked orientation table.
3. `P-HANDED-FLIP`
   - prove/test left/right sign inversion at fixed output index.
4. `P-CYCLE-DETECT`
   - deterministic cycle extraction and period contract.
5. `P-SUPPORT-CLOSURE`
   - support-stability criterion and counterexample reporting.
6. `P-ARTIFACT-REPLAY`
   - deterministic replay hash or equivalent reproducibility check.

---

## 3. Single-Task Dossier Skeleton

Use this exact structure in manager-issued tasks:

1. `primitive_gate_id`: one of Section 2 (required).
2. `files_in_scope`: exact file paths, no wildcards.
3. `inputs_locked`:
   - `rfc/CONVENTIONS.md`
   - `calc/conftest.py` (`FANO_CYCLES`, `FANO_SIGN`, `FANO_THIRD`)
4. `deliverable`:
   - theorem/test/script/artifact, exactly one primary output.
5. `verifier_command`:
   - one deterministic command (`pytest ...` or `lake build ...`).
6. `artifact_path`:
   - one output path (`calc/...json`, `website/data/...csv`, etc.).
7. `forbidden_scope`:
   - no new physics claims,
   - no convention edits,
   - no unrelated file rewrites.

---

## 4. Packeting Policy (3-5 Tasks)

For each packet:
1. choose 3-5 different primitive gate IDs,
2. assign at least one independent audit task,
3. avoid duplicate `(claim_id, gate_id, artifact_target)` keys.
If only one task can be dispatched per manager response, run packets over 3-5 consecutive rounds.

Minimal packet recipe:
1. one author task (implementation),
2. one audit task (different model provider),
3. one integration task (artifact/claim-doc sync).

---

## 5. Pass/Fail Rule

Task is done only if all hold:
1. verifier command exits 0,
2. artifact exists at declared path,
3. artifact is deterministic on rerun,
4. no convention drift from `rfc/CONVENTIONS.md`.

If any fail:
1. mark task failed,
2. create one repair task for the same primitive gate,
3. do not promote claim status from that task.

---

## 6. Example (Filled)

1. `primitive_gate_id`: `P-HANDED-FLIP`
2. `files_in_scope`: `calc/xor_octonion_gate.py`, `calc/test_xor_octonion_gate.py`
3. `deliverable`: add exhaustive handedness sign-flip test on all distinct imaginary pairs
4. `verifier_command`: `pytest calc/test_xor_octonion_gate.py -q`
5. `artifact_path`: `calc/xor_handed_flip_report.json`
6. `forbidden_scope`: no edits outside listed files; no claim status updates
