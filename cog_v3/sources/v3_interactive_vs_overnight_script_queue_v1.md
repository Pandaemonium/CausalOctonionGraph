# v3 Interactive vs Overnight Script Queue (v1)

Date: 2026-03-03
Owner: COG Core
Status: Active execution queue

## 1) Immediate Feedback Queue (write/run now)

Use this lane for:
1. quick scripts,
2. quick confirmation runs,
3. blockers that affect next design choices.

## 1.1 Run now (already implemented)

1. `python -m cog_v3.calc.build_v3_fixed_manifest_kernel_gate_stack_v1 --quick --backend numba_cpu --global-seed 1337`
- Purpose: fast gate-stack sanity after any kernel or metric change.
- Expected runtime: 2-8 minutes.
- Decision unlocked: whether `K1` or `K2` remains best near-term kernel lane.

2. `python -m cog_v3.calc.build_v3_c12_phase_sector_metrics_v1 --quick --global-seed 1337`
- Purpose: quick check of RFC-010 metrics after phase/channel edits.
- Expected runtime: 1-4 minutes.
- Decision unlocked: whether `R3/C3/A1/A2` move in the right direction.

3. `python -m cog_v3.calc.build_v3_generation_aligned_equivalence_panel_v1 --quick --global-seed 1337`
- Purpose: quick check for large `Delta_max` regressions/improvements in RFC-011.
- Expected runtime: 5-20 minutes.
- Decision unlocked: whether equivalence lane is improving before heavy run.

## 1.2 Write now (small, high-value diagnostics)

1. `cog_v3/calc/build_v3_omega_hat_diagnostic_v1.py`
- Purpose: isolate why `Omega_hat` dominates RFC-011 mismatch.
- Runtime target: <5 minutes.
- Output target: `cog_v3/sources/v3_omega_hat_diagnostic_v1.{json,md}`.
- Status: done (`2026-03-03`).

2. `cog_v3/calc/build_v3_gate5_clock_repeat_probe_v1.py`
- Purpose: explain why gate-5 fails despite good gates 0-4.
- Runtime target: <10 minutes.
- Output target: `cog_v3/sources/v3_gate5_clock_repeat_probe_v1.{json,md}`.
- Status: done (`2026-03-03`).

3. `cog_v3/calc/build_v3_r3_zero_breakdown_v1.py`
- Purpose: break down RFC-010 `R3=0` by trial family, panel, and support mask.
- Runtime target: <10 minutes.
- Output target: `cog_v3/sources/v3_r3_zero_breakdown_v1.{csv,md}`.
- Status: done (`2026-03-03`).

## 2) Overnight Write Queue

Use this lane for:
1. scripts that are straightforward but not urgent,
2. scripts required for next-day heavy runs.

1. `cog_v3/calc/build_v3_associator_field_probe_v1.py` (RFC-012)
2. `cog_v3/calc/test_v3_associator_field_probe_v1.py`
3. `cog_v3/calc/build_v3_order6_psl27_action_probe_v1.py` (RFC-013)
4. `cog_v3/calc/test_v3_order6_psl27_action_probe_v1.py`
5. `cog_v3/calc/build_v3_order3_order12_bundle_seed_bank_v1.py` (RFC-014)
6. `cog_v3/calc/build_v3_bundle_seed_vs_random_ablation_v1.py`
7. `cog_v3/calc/test_v3_bundle_seed_vs_random_ablation_v1.py`
8. `cog_v3/calc/build_v3_fixed_manifest_kernel_gate_stack_seed_sweep_v1.py`

## 3) Overnight Run Queue

Use this lane for:
1. long sweeps,
2. seed panels,
3. multi-scale runs.

## 3.1 High priority overnight runs

1. Full RFC-011 run:
- `python -m cog_v3.calc.build_v3_generation_aligned_equivalence_panel_v1 --global-seed 1337`
- Purpose: canonical equivalence panel (non-quick).
- Expected runtime: long (10+ minutes to hours depending on machine load).

2. Gate-stack seed sweep (after script exists):
- `python -m cog_v3.calc.build_v3_fixed_manifest_kernel_gate_stack_seed_sweep_v1 --backend numba_cpu --seed-count 64`
- Purpose: robustness of `K1` vs `K2` ranking and gate pass rates.

3. Associator field scan (after script exists):
- `python -m cog_v3.calc.build_v3_associator_field_probe_v1 --backend numba_cpu --seed-count 32 --ticks 256`
- Purpose: RFC-012 Gate 1/2 evidence.

4. Bundle-vs-random ablation (after script exists):
- `python -m cog_v3.calc.build_v3_bundle_seed_vs_random_ablation_v1 --backend numba_cpu --seed-budget 5000`
- Purpose: RFC-014 effectiveness test.

## 3.2 Medium priority overnight runs

1. RFC-010 panel rerun across more seeds:
- `python -m cog_v3.calc.build_v3_c12_phase_sector_metrics_v1 --global-seed <seed>`
- Multiple seeds orchestrated by wrapper script.

2. RFC-013 action probe:
- `python -m cog_v3.calc.build_v3_order6_psl27_action_probe_v1`
- Purpose: test if `168` is structural or only cardinality coincidence.

## 4) Day/Night split policy

1. Daytime interactive:
- only run scripts that finish fast enough to inform immediate decisions.

2. Overnight:
- run seed sweeps and heavy panels with fixed manifests.

3. Promotion discipline:
- no promotion from single-seed or quick-mode results.

## 5) Next recommended sequence

1. Run the 3 immediate quick scripts in section 1.1.
2. Write `v3_omega_hat_diagnostic_v1.py`.
3. If diagnostics are clear, queue full RFC-011 and gate-stack seed sweep overnight.
