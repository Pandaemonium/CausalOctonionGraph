# XCALC-101 Task Prompt — XOR Charge-Sign Interaction Matrix

Status: Ready to Assign  
Roadmap ID: `XCALC-101`  
Roadmap Source: `rfc/XOR_PHYSICS_CALCULABLES_ROADMAP.md`

---

## 1. Objective

Implement a **pure XOR-basis** charge-sign interaction matrix for two-node interactions, aligned with current D1-D3 semantics:
1. repulsive,
2. attractive,
3. neutral.

This task is about deterministic classification and artifacts, not trajectory geometry.

---

## 2. Locked Semantics (Do Not Change)

Use existing policy contracts:
1. D1 combine: multiplicative.
2. D2 trace: Markov fold over current boundary messages.
3. D3 energy exchange: non-empty messages AND folded interaction is not identity.

Charge observable (current project contract):
1. `u1Charge(psi) = Re(psi_7)` (real part of `e7` coefficient).

---

## 3. Required Deliverables

Create:
1. `calc/xor_charge_sign_interaction_matrix.py`
2. `calc/test_xor_charge_sign_interaction_matrix.py`
3. `sources/xor_charge_sign_matrix.md`

Generate artifacts:
1. `calc/xor_charge_sign_interaction_matrix.json`
2. `calc/xor_charge_sign_interaction_matrix.csv`
3. `website/data/xor_charge_sign_interaction_matrix.json`
4. `website/data/xor_charge_sign_interaction_matrix.csv`

Optional helper:
1. `scripts/build_xor_charge_sign_interaction_matrix.py`

---

## 4. State Set (Required)

Use same-basis XOR states only:
1. `vector_electron_favored` from triad `(1,2,3)` integer-count seed.
2. `left_spinor_electron_ideal` from `furey_electron_doubled()`.
3. `right_spinor_electron_ideal` from `furey_dual_electron_doubled()`.
4. `vacuum_doubled` from `vacuum_doubled()`.

Do not import `oct_mul_full` from legacy QED path for this task.

---

## 5. Required API (`calc/xor_charge_sign_interaction_matrix.py`)

Implement these functions:
1. `u1_charge(state) -> int`
2. `temporal_commit(state) -> state` (left hit by `e7`)
3. `interaction_fold(msgs) -> state` (left fold with identity `e0`)
4. `next_state_v2_xor(state, msgs) -> state`
5. `two_node_round_xor(state1, state2) -> (state1_next, state2_next)`
6. `is_energy_exchange_locked_xor(msgs) -> bool`
7. `same_u1_charge_sign_xor(state1, state2) -> bool`
8. `opposite_u1_charge_sign_xor(state1, state2) -> bool`
9. `interaction_kind_xor(state1, state2) -> str` in `{repulsive, attractive, neutral}`
10. `build_charge_sign_matrix_xor() -> dict`
11. `summarize_xor() -> dict`

Matrix interpretation:
1. rows = source state,
2. cols = boundary payload state.

---

## 6. Test Requirements

Add tests for:
1. benchmark charge signs are deterministic.
2. same-sign non-zero pair classifies as `repulsive`.
3. opposite-sign non-zero pair classifies as `attractive`.
4. any pair involving vacuum classifies as `neutral`.
5. matrix contains all required labels and is deterministic on replay.
6. `two_node_round_xor` deterministic for repeated identical calls.
7. output JSON schema fields present.

Expected minimum assertions:
1. `left_spinor_electron_ideal` vs itself -> `repulsive`.
2. `left_spinor_electron_ideal` vs `right_spinor_electron_ideal` -> `attractive`.
3. `left_spinor_electron_ideal` vs `vacuum_doubled` -> `neutral`.

---

## 7. Artifact Contract

JSON summary must include:
1. `schema_version`
2. `generated_at_utc`
3. `charges`
4. `matrix`
5. `notes`

CSV must include:
1. `row_label`
2. `col_label`
3. `kind`
4. `row_charge`
5. `col_charge`

---

## 8. Not Claimed (Required in `sources/xor_charge_sign_matrix.md`)

State explicitly:
1. no spatial scattering trajectory is modeled,
2. no force magnitude calibration is claimed,
3. no SI-unit calibration is claimed.

---

## 9. Verification Commands

Run:
1. `python -m pytest calc/test_xor_charge_sign_interaction_matrix.py -v`
2. `python -m pytest calc/ -q`
3. `python -m calc.xor_charge_sign_interaction_matrix`

Success criteria:
1. tests pass,
2. artifacts generated in `calc/` and `website/data/`,
3. matrix values match expected sign-class rules.

