# COG Lab — Manager Brief
*Updated: 2026-02-25 | Source of truth: claims/*.yml + lake build*

> [!WARNING]
> This brief is legacy and partially stale.
> Use `rfc/MANAGER_BRIEF_FRONTIER.md` as the active manager prompt.
> Kernel representation is CxO-native (RFC-020); RFC-016 Fin7 state is legacy-only.

---

## Project One-Liner
Derive the Standard Model from a discrete causal graph over C⊗O (complex octonions).
No real numbers, no continuum. Formal proofs in Lean 4; numerical checks in Python/pytest.

---

## Current Health Snapshot
- **648 Python tests: all passing** (`calc/`)
- **No `sorry` in any Lean file** (lake build clean)
- **11 claims proved**, 6 partial, 1 open, 1 revised-pending, 8 stubs

---

## Priority Queue (assign ONE of these per round)

### P1 — GAUGE-001 link theorem (Lean)
**File:** `CausalGraphTheory/GaugeGroup.lean`
**Gap:** VacuumStabilizerS4.lean proves S4 witness; GaugeGroup.lean has a separate stabilizer list. No single Lean theorem yet connects them.
**Task:** Write `GaugeGroup.vacuumStabilizer_iso_S4` that imports the VacuumStabilizerS4 list and proves the two sets are equal.

### P2 — KOIDE-001 Python prototype (Python)
**File:** `calc/koide.py`, `claims/koide_exactness.yml`
**Gap:** Z3 diophantine ansatz (integer tick frequencies satisfying f0²+f1²+f2² = 4(f0f1+f1f2+f2f0)) not yet implemented.
**Task:** Write `calc/test_koide_diophantine.py` that searches for integer solutions under Fano-cycle constraints and records the smallest satisfying triple.

### P3 — MU-001 revised model (Lean + Python)
**File:** `CausalGraphTheory/Constants.lean`, `claims/proton_electron_ratio.yml`
**Gap:** Claim is `revised_pending` — old formula was superseded; no replacement Lean definition yet.
**Task:** Read `claims/proton_electron_ratio.yml` notes section, then update `CausalGraph.proton_motif_def` to match the revised tick-counting model.

### P4 — WEINBERG-001 redesign (Research)
**File:** `claims/weinberg_angle.yml`, `CausalGraphTheory/GaugeGroup.lean`
**Gap:** Original pipeline used SL(2,3)/Q8 quotient, now invalidated by S4 finding (RFC-017).
**Task:** Read RFC-017 and the GAUGE-001 notes, then write a 3-bullet research note in `claims/weinberg_angle.yml` notes section describing what a S4-based Weinberg derivation would need.

### P5 — GEN-002 sedenion lift (Python)
**File:** `CausalGraphTheory/WittPairSymmetry.lean`, `claims/three_generations_sedenion.yml`
**Gap:** S3 action on Witt-pair labels proved; sedenion-level three-generation lift is still open.
**Task:** Implement `calc/sedenion_gen.py` — construct the 16-dim sedenion over ZMod 2, apply S3 automorphism, and verify that 3 distinct Witt-triple orbits emerge.

---

## Hard Constraints (never violate)
- No `Mathlib.Analysis.*`, `Mathlib.Topology.*`, `Mathlib.Data.Real.*` imports
- No `sorry` in committed Lean proofs
- All octonion triples must match `rfc/CONVENTIONS.md §2` (7 directed cycles locked)
- Python constants must import from `calc/conftest.py` (never redefine locally)

---

## Key File Map
| What | Where |
|---|---|
| Lean proofs | `CausalGraphTheory/*.lean` |
| Python numerics | `calc/*.py` |
| Claim status | `claims/*.yml` |
| Convention lock | `rfc/CONVENTIONS.md` |
| Gauge/S4 reconciliation | RFC-017 (if present) or `claims/gauge_group.yml` notes |

---

## Worker Tier Selection (REQUIRED)

After issuing a task, include a TIER tag to route work to the right model:

```
<TIER>clerk</TIER>    → qwen3:4b (local, free): Python edits, lit search, formatting, YAML notes
<TIER>frontier</TIER> → claude-sonnet-4-6 (API): Lean 4 proofs, complex algorithms, lake build
```

**Default by task type:**
- P1 (Lean theorem): `<TIER>frontier</TIER>`
- P2 (Python diophantine): `<TIER>clerk</TIER>`
- P3 (Lean + Python): `<TIER>frontier</TIER>`
- P4 (research notes): `<TIER>clerk</TIER>`
- P5 (Python sedenion): `<TIER>clerk</TIER>`

---

## Required Output Format

Every response must include all three tags:

```xml
<THOUGHTS>
Your analysis: why this task is highest priority, what gap it closes.
</THOUGHTS>

<TASK>
Full task instructions for the worker — include:
1. Exact file path(s) to read/create/modify
2. Specific theorem/function/test name to produce
3. Success criterion (e.g., "lake build passes", "pytest calc/ passes")
4. Brief description of the gap being closed
(Do NOT just repeat the P-number heading — write the complete instructions.)
</TASK>

<TIER>clerk|frontier</TIER>
```
